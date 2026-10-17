"""Checks a tracker page against a dated event ledger.

facts:  [{"key", "cues": [regex], "type": "date"|"stage",
          "stage_phrases": {stage: regex}}]           # stage facts: how each stage is said in the present tense
ledger: [{"fact", "date": when it happened, "value": date | stage name, "source"}]

Finding kinds: STALE_RESTATEMENT, DATE_MATH, PAST_FUTURE, ASOF_LAG, CONFLICT.
"""
import re

from .dates import NUM, add, find_dates, fmt, number
from .page import FUTURE_CUES

ASOF_DAYS = 14


def F(kind, s, why, fix=""):
    q = s.text if len(s.text) <= 220 else s.text[:217] + "..."
    return {"kind": kind, "sid": s.sid, "text": s.text, "section": s.section, "heading": s.heading, "quote": q, "why": why, "fix": fix}


def linked(s, fact):
    return any(re.search(c, s.text, re.I) for c in fact["cues"])


def state(ledger, fact, asof):
    ev = sorted((e for e in ledger if e["fact"] == fact["key"] and (asof is None or e["date"] <= asof)), key=lambda e: e["date"])
    if not ev:
        return None, []
    cur = ev[-1]["value"]
    old = [e["value"] for e in ev[:-1] if e["value"] != cur]
    return ev[-1], old


# ---------------- stale restatements ----------------
def stale(page, facts, ledger):
    out = []
    for fact in facts:
        last, old = state(ledger, fact, page.verified)
        if not last or not old:
            continue
        cur = last["value"]
        for s in page.sentences:
            if s.tense == "history" or not linked(s, fact):
                continue
            if fact["type"] == "date":
                ds = {d for _, _, d in s.dates}
                hit = [o for o in old if o in ds]
                if hit and cur not in ds:
                    out.append(F("STALE_RESTATEMENT", s, f'{fact["key"]} is {fmt(cur)} since {fmt(last["date"])} ({last.get("source", "ledger")}); '
                                                       f'this sentence still says {fmt(hit[0])}', f"change {fmt(hit[0])} -> {fmt(cur)}"))
            else:
                ph = fact["stage_phrases"]
                hit = [o for o in old if o in ph and re.search(ph[o], s.text, re.I)]
                if hit and not (cur in ph and re.search(ph[cur], s.text, re.I)):
                    out.append(F("STALE_RESTATEMENT", s, f'{fact["key"]} is "{cur}" since {fmt(last["date"])} ({last.get("source", "ledger")}); '
                                                       f'this sentence still says "{hit[0]}"', f'restate as "{cur}"'))
    return out


# ---------------- date math ----------------
REL = re.compile(rf"\b{NUM}[- ](calendar[- ]|business[- ])?(days?|weeks?|months?)\s+(?:after|from|following|later than)\b", re.I)
PERIOD = re.compile(rf"\b{NUM}[- ](calendar[- ]|business[- ])?(day|week|month)\s+(?:comment |public |review |consultation |objection )?(?:period|window)\b", re.I)
BY = re.compile(rf"\b(?:deferred|moved|pushed(?: back| out)?|extended|delayed|postponed)\b[^.;]{{0,60}}?\bby\s+{NUM}\s+(days?|weeks?|months?)\b", re.I)
DUE = re.compile(r"\b(?:due|deadline|closes?|close on|ends?|runs? through|open (?:until|through))\b", re.I)
RULE_TEXT = re.compile(r"\bwhichever is (?:later|earlier|sooner)\b|\b(?:the )?(?:earlier|later) of\b|\beach year\b|\bevery year\b|\bannually\b", re.I)
TOL = {"day": 0, "week": 1, "month": 3}
SOURCE_WORDS = re.compile(r"\b(?:page|list|lists|listed|docket|site|website|register|mirror|record|shows?|still|status|no decision|not yet|portal|database)\b", re.I)
REPORTED = re.compile(r"\b(?:states?|stated|continues to state|says|said|reads|lists|shows|confirms|represents) that\b|\bcontinues to (?:state|list|show)\b", re.I)
DEADLINE_SUBJ = re.compile(r"\b(?:deadline|due date|comments?|period|window|filing date)\b", re.I)


def plus(d, n, unit, kind):
    if kind and kind.lower().startswith("business"):
        import datetime as dt
        k, x = 0, d
        while k < n:
            x += dt.timedelta(days=1)
            if x.weekday() < 5:
                k += 1
        return x
    return add(d, n, unit)


def due_date(s, after=0):
    for m in DUE.finditer(s.text, after):
        for a, _, d in s.dates:
            if 0 <= a - m.end() <= 25:
                return d
    return None


def date_math(page):
    out = []
    for i, s in enumerate(page.sentences):
        if RULE_TEXT.search(s.text):
            continue
        for m in REL.finditer(s.text):
            n, kind, unit = number(m.group(1)), m.group(2), m.group(3)
            ref = next((d for a, _, d in s.dates if 0 <= a - m.end() <= 70), None)
            if ref is None or n == 0:
                continue
            want = plus(ref, n, unit, kind)
            subj = s.text[max(0, m.start() - 60):m.start()]
            if DEADLINE_SUBJ.search(subj) and due_date(s):
                got = due_date(s)
                if got != want:
                    out.append(F("DATE_MATH", s, f'"{m.group(0)} {fmt(ref)}" is {fmt(want)}, but the deadline in this sentence is {fmt(got)} '
                                                 f'({(got - ref).days} days after)', "fix the interval or the date"))
                continue
            # "X happened on D2 - N days after D1": D2 must sit just before the phrase
            before = [d for a, _, d in s.dates if 0 <= m.start() - a <= 90 and d != ref]
            if before:
                got = before[-1]
                tol = TOL[unit.lower().rstrip("s")]
                if got > ref and abs((got - want).days) > tol:
                    out.append(F("DATE_MATH", s, f'"{m.group(0)} {fmt(ref)}" is {fmt(want)}; the date it describes is {fmt(got)} '
                                                 f'({(got - ref).days} days after)', "fix the interval or the date"))
        for m in PERIOD.finditer(s.text):
            n, kind, unit = number(m.group(1)), m.group(2), m.group(3)
            window = s.dates + (page.sentences[i - 1].dates if i and page.sentences[i - 1].section == s.section else [])
            got = due_date(s, m.end())
            if not got:
                continue
            starts = [d for _, _, d in window if d < got]
            if starts and all(plus(d, n, unit, kind) != got for d in starts):
                d0 = max(starts)
                out.append(F("DATE_MATH", s, f"a {n}-{unit} period ending {fmt(got)} would start {(got - d0).days} days after {fmt(d0)}, "
                                             f"not {n} {unit}s", "fix the period length or the due date"))
        for m in BY.finditer(s.text):
            n, unit = number(m.group(1)), m.group(2)
            ft = re.search(r"\bfrom ([A-Z][a-z]+\.? \d{1,2}(?:, \d{4})?) to ([A-Z][a-z]+\.? \d{1,2}(?:, \d{4})?)", s.text)
            ds = [d for _, _, d in find_dates(ft.group(0), page.verified.year if page.verified else 2026)] if ft else []
            if len(ds) == 2 and n:
                a, b = ds
                if plus(a, n, unit, None) != b and abs((plus(a, n, unit, None) - b).days) > 3:
                    out.append(F("DATE_MATH", s, f"{fmt(a)} moved by {n} {unit} is {fmt(plus(a, n, unit, None))}, not {fmt(b)}", "fix the interval"))
    return out


# ---------------- tense vs the page date ----------------
def past_future(page):
    out = []
    if not page.verified:
        return out
    for s in page.sentences:
        if s.tense == "history" or not s.future or s.asof or RULE_TEXT.search(s.text):
            continue
        for a, b, d in s.dates:
            if d >= page.verified:
                continue
            cue = None
            for c in FUTURE_CUES.finditer(s.text, max(0, a - 40), a):
                gap = s.text[c.end():a]
                if not re.search(r"[;()]", gap) and not find_dates(gap, d.year):
                    cue = c
            if cue and not REPORTED.search(s.text[max(0, cue.start() - 80):cue.start()]):
                out.append(F("PAST_FUTURE", s, f"says {cue.group(0)!r} about {fmt(d)}, which is "
                                               f"{(page.verified - d).days} days before the page's last-verified date {fmt(page.verified)}",
                             "say what happened, or mark it unconfirmed with an as-of date"))
                break
    return out


def asof_lag(page, days=ASOF_DAYS):
    out = []
    if not page.verified:
        return out
    for s in page.sentences:
        if s.tense == "history" or not s.asof or not SOURCE_WORDS.search(s.text):
            continue
        lag = (page.verified - s.asof).days
        if lag > days:
            out.append(F("ASOF_LAG", s, f"claim is as of {fmt(s.asof)}, {lag} days before the page's last-verified {fmt(page.verified)}",
                         "re-check this source or show its own date next to the claim"))
    return out


# ---------------- restatements of one fact disagree ----------------
def conflict(page, facts):
    out = []
    for fact in facts:
        if fact["type"] != "date":
            continue
        vals = {}
        for s in page.sentences:
            if s.tense == "history" or not linked(s, fact):
                continue
            m = next((re.search(c, s.text, re.I) for c in fact["cues"] if re.search(c, s.text, re.I)), None)
            d = next((d for a, _, d in s.dates if 0 <= a - m.end() <= 25), None)
            if d:
                vals.setdefault(d, []).append(s)
        if len(vals) > 1:
            major = max(vals, key=lambda d: len(vals[d]))
            for d, ss in vals.items():
                if d != major:
                    for s in ss:
                        out.append(F("CONFLICT", s, f'{fact["key"]}: this sentence says {fmt(d)}; {len(vals[major])} other restatements say {fmt(major)}',
                                     "make the restatements agree"))
    return out


def check(page, facts=(), ledger=()):
    found = stale(page, facts, ledger) + date_math(page) + past_future(page) + asof_lag(page)
    if not ledger:
        found += conflict(page, facts)
    seen, out = set(), []
    for f in found:
        k = (f["kind"], f["sid"])
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def impact(page, fact, old, new):
    """Every non-history sentence about `fact` that still states `old`: the edit list for one incoming event."""
    rows = []
    for s in page.sentences:
        if s.tense == "history" or not linked(s, fact):
            continue
        if fact["type"] == "date" and old in {d for _, _, d in s.dates}:
            rows.append((s.sid, s.heading, s.text, f"{fmt(old)} -> {fmt(new)}"))
        elif fact["type"] == "stage" and re.search(fact["stage_phrases"].get(old, "$^"), s.text, re.I):
            rows.append((s.sid, s.heading, s.text, f"{old} -> {new}"))
    return rows
