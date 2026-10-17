"""Synthetic tracker pages after an update pass, with the truth of what the update missed.

A program has facts (deadline, comment close, stage). One or two events arrive (deadline moved, comments extended,
rule final). The page restates every fact across sections; the simulated editor updates each restatement with
probability P_UPDATE, so the rest still state the superseded value (planted STALE_RESTATEMENT). History lines quote the
old values on purpose (look-alikes). Also planted, each with a clean twin: date-math slips, future wording on past dates,
claims with an old as-of date.
"""
import datetime as dt
import random

from .dates import fmt

P_UPDATE = 0.7
SECTIONS = ["pill", "glance", "overview", "body", "faq", "timeline"]
HEADINGS = {"pill": "Status pill", "glance": "At a glance", "overview": "General overview", "body": "Details", "faq": "FAQ",
            "timeline": "Key dates", "history": "Deadline history", "changelog": "Changelog"}


def dstr(rng, d, asof):
    styles = [lambda: fmt(d), lambda: f"{d:%b}. {d.day}, {d.year}" if d.month != 5 else fmt(d), lambda: f"{d:%b} {d.day}, {d.year}"]
    if d.year == asof.year:
        styles.append(lambda: f"{d:%B} {d.day}")
    return rng.choice(styles)()


def case(seed, bank):
    rng = random.Random(seed)
    prog, agency = rng.choice(bank.PROGRAMS)
    asof = dt.date(2026, rng.randint(2, 11), rng.randint(1, 28))
    ev_date = asof - dt.timedelta(days=rng.randint(0, 6))
    dl_old = asof + dt.timedelta(days=rng.randint(25, 220))
    dl_new = dl_old + dt.timedelta(days=rng.choice([30, 45, 60, 90, 92, 120]))
    c_open = asof - dt.timedelta(days=rng.randint(15, 60))
    c_n = rng.choice([30, 45, 60, 90])
    c_old = c_open + dt.timedelta(days=c_n)
    if c_old <= asof:
        c_old = asof + dt.timedelta(days=rng.randint(5, 40))
    c_new = c_old + dt.timedelta(days=rng.choice([14, 30, 45]))
    events = rng.sample(["deadline", "comment_close", "stage"], rng.choice([1, 1, 2]))
    vals = {"deadline": (dl_old, dl_new), "comment_close": (c_old, c_new), "stage": ("proposed", "final")}
    ledger = []
    for k, (old, new) in vals.items():
        ledger.append({"fact": k, "date": asof - dt.timedelta(days=rng.randint(60, 200)), "value": old, "source": f"{agency} notice"})
        if k in events:
            ledger.append({"fact": k, "date": ev_date, "value": new, "source": f"{agency} notice of {fmt(ev_date)}"})
    truth, sections = {}, {s: [] for s in SECTIONS + ["history", "changelog"]}

    def say(sec, text, kind=None):
        text = text[0].upper() + text[1:]
        sections[sec].append(text)
        if kind:
            truth[text] = kind

    ctx = {"prog": prog, "agency": agency}
    for fact, (old, new) in vals.items():
        changed = fact in events
        for sec in SECTIONS:
            tpl = rng.choice(bank.RESTATE[fact][sec]) if fact != "stage" else None
            updated = (not changed) or rng.random() < P_UPDATE
            v = new if (changed and updated) else old
            vs = v if fact == "stage" else dstr(rng, v, asof)
            if fact == "stage":
                tpl = rng.choice(bank.STAGE[v][sec])
            text = tpl.format(v=vs, **ctx)
            say(sec, text, "STALE_RESTATEMENT" if changed and not updated else None)
        if changed:   # history look-alikes quote the superseded value
            o = old if fact == "stage" else dstr(rng, old, asof)
            n = new if fact == "stage" else dstr(rng, new, asof)
            say("history", rng.choice(bank.HISTORY[fact]).format(old=o, new=n, **ctx))
            say("body", rng.choice(bank.HISTORY_IN_BODY[fact]).format(old=o, new=n, **ctx))
            say("changelog", rng.choice(bank.CHANGELOG[fact]).format(old=o, new=n, ev=dstr(rng, ev_date, asof), **ctx))

    # ---- date math: a stated interval between two dates (planted wrong, or right) ----
    d1 = asof - dt.timedelta(days=rng.randint(40, 120))
    n, unit = rng.choice([(10, "days"), (14, "days"), (21, "days"), (30, "days"), (45, "days"), (60, "days"), (3, "months"), (2, "weeks")])
    from .dates import add
    d2 = add(d1, n, unit)
    wrong = rng.random() < 0.5
    if wrong:
        d2 += dt.timedelta(days=rng.choice([-9, -6, 5, 8, 12, 19]) * (7 if unit == "months" else 1))
    nw = bank.NUMWORD.get(n, str(n)) if rng.random() < 0.5 else str(n)
    say("body", rng.choice(bank.MATH).format(d1=dstr(rng, d1, asof), d2=dstr(rng, d2, asof), n=nw, unit=unit, **ctx),
        "DATE_MATH" if wrong else None)

    # ---- future wording about a past date (planted) vs a future date / past tense (clean) ----
    if rng.random() < 0.5:
        d = asof - dt.timedelta(days=rng.randint(3, 60))
        say(rng.choice(["overview", "body", "faq"]), rng.choice(bank.FUTURE).format(d=dstr(rng, d, asof), **ctx), "PAST_FUTURE")
    else:
        if rng.random() < 0.5:
            d = asof + dt.timedelta(days=rng.randint(3, 60))
            say(rng.choice(["overview", "body", "faq"]), rng.choice(bank.FUTURE).format(d=dstr(rng, d, asof), **ctx))
        else:
            d = asof - dt.timedelta(days=rng.randint(3, 60))
            say(rng.choice(["overview", "body", "faq"]), rng.choice(bank.PAST).format(d=dstr(rng, d, asof), **ctx))

    # ---- a claim checked against a source on an old date (planted) vs recently (clean) ----
    lagging = rng.random() < 0.5
    d = asof - dt.timedelta(days=rng.randint(20, 70) if lagging else rng.randint(0, 10))
    say(rng.choice(["body", "glance", "overview"]), rng.choice(bank.ASOF).format(d=dstr(rng, d, asof), **ctx), "ASOF_LAG" if lagging else None)

    # ---- filler: neutral sentences with unrelated dates ----
    for sec in ("body", "overview", "faq"):
        f = asof + dt.timedelta(days=rng.randint(-300, 300))
        say(sec, rng.choice(bank.FILLER).format(d=dstr(rng, f, asof), **ctx))

    lines = [f"# {prog} Tracker", f"Last verified: {fmt(asof)}"]
    for sec in SECTIONS + ["history", "changelog"]:
        items = sections[sec][:]
        if sec not in ("pill", "glance", "timeline", "changelog"):
            rng.shuffle(items)
        lines.append(f"## {HEADINGS[sec]}")
        lines += items if sec in ("pill", "glance", "timeline", "changelog") else [" ".join(items)]
    return "\n".join(lines), ledger, truth
