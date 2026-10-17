"""Tracker page -> sections -> sentences tagged with tense, dates and their own as-of date.

Canonical text format (the generator writes it; real_pages.py converts live pages into it):

    # <title>
    Last verified: October 13, 2026
    ## <section heading>
    <prose or one glance row per line>
"""
import re
from dataclasses import dataclass, field

from .dates import DATE_RE, find_dates

KIND_BY_HEADING = [("pill", r"\bpill|status bar"), ("glance", r"at a glance|key facts|summary table"),
                   ("history", r"history|why it moved|how we got here|background"), ("changelog", r"changelog|change log|update log|what changed"),
                   ("faq", r"\bfaq|questions"), ("timeline", r"timeline|key dates|calendar|what.s next"), ("overview", r"overview|in brief|tl;?dr")]
HISTORY_SECTIONS = {"history", "changelog"}

HISTORY_CUES = re.compile("|".join([
    r"\bmoved (?:it |the date )?from\b", r"\bshift(?:s|ed)? from\b", r"\bpushed (?:back |out )?from\b", r"\bextended from\b",
    r"\binitially\b", r"\boriginally\b", r"\bpreviously\b", r"\bhad (?:been|set|proposed|said|listed|shown|planned)\b",
    r"\bwas (?:set|scheduled|proposed|due|moved|pushed|extended|planned|expected|slated)\b", r"\bwere (?:due|scheduled|expected)\b",
    r"\bfloated\b", r"→", r"\bfrom [A-Z][a-z]+\.? \d{1,2}(?:, \d{4})? to\b", r"\breplac(?:ed|es|ing)\b", r"\bsuperseded\b",
    r"\bno longer\b", r"\bbefore (?:the )?(?:approval|change|extension|move)\b", r"\bin place of\b", r"\binstead of\b",
    r"\bthe (?:earlier|prior|old|former) (?:date|deadline|schedule)\b", r"\bpre-(?:extension|approval)\b"]), re.I)
PAST_CUES = re.compile(r"\b(?:fell due|was due|were due|closed|has passed|have passed|took effect|took place|expired|ended|lapsed|"
                       r"was held|were held|published|issued|announced|approved|enacted|signed|filed|posted|became)\b", re.I)
FUTURE_CUES = re.compile(r"\b(?:will|scheduled|upcoming|expected|due|pending|awaits?|awaited|is set to|are set to|slated|"
                         r"opens|closes|comes into force|takes effect|kicks in|remains? open|still open|not yet)\b", re.I)
ASOF_RE = re.compile(r"\b(?:as of|checked (?:on|again on)|re-?read on|confirmed on|verified on|last checked)\s+(?:the\s+)?"
                     + DATE_RE.pattern, re.I)
VERIFIED_RE = re.compile(r"last verified:?\s*(.+)", re.I)


@dataclass
class Sentence:
    sid: str
    section: str     # section kind
    heading: str
    text: str
    tense: str = "current"   # current | history
    future: bool = False
    dates: list = field(default_factory=list)   # [(start, end, date)]
    asof: object = None


@dataclass
class Page:
    title: str
    verified: object
    sentences: list

    def by_section(self, kind):
        return [s for s in self.sentences if s.section == kind]


def kind_of(heading):
    h = heading.lower()
    for kind, pat in KIND_BY_HEADING:
        if re.search(pat, h):
            return kind
    return "body"


def split_sentences(block, kind):
    if kind in ("glance", "pill", "timeline", "changelog"):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        out = []
        for l in lines:
            out += [p for p in re.split(r"(?<=[.;!?])\s+(?=[A-Z“\"(])", l) if p.strip()] if kind == "changelog" else [l]
        return out
    text = re.sub(r"\s*\n\s*", " ", block).strip()
    parts = [p.strip() for p in re.split(r"(?<=[.;!?])\s+(?=[A-Z“\"(])", text) if p.strip()]
    if kind == "faq":   # keep a question with its answer: "When is it due? On May 1." is one claim
        merged = []
        for p in parts:
            if merged and merged[-1].endswith("?"):
                merged[-1] += " " + p
            else:
                merged.append(p)
        parts = merged
    return parts


def tag(s, year):
    s.dates = find_dates(s.text, year)
    m = ASOF_RE.search(s.text)
    if m:
        ds = find_dates(m.group(0), year)
        s.asof = ds[0][2] if ds else None
    if s.section in HISTORY_SECTIONS or HISTORY_CUES.search(s.text):
        s.tense = "history"
    s.future = bool(FUTURE_CUES.search(s.text)) and not PAST_CUES.search(s.text)
    return s


def parse(text):
    title, verified, cur, heading, blocks = "", None, None, "", []
    lines = text.split("\n")
    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif VERIFIED_RE.match(line.strip()) and verified is None:
            ds = find_dates(line, 2000)
            verified = ds[0][2] if ds else None
        elif line.startswith("## "):
            if cur is not None:
                blocks.append((heading, "\n".join(cur)))
            heading, cur = line[3:].strip(), []
        elif cur is not None:
            cur.append(line)
    if cur is not None:
        blocks.append((heading, "\n".join(cur)))
    year = verified.year if verified else 2026
    sents, counts = [], {}
    for heading, block in blocks:
        kind = kind_of(heading)
        for txt in split_sentences(block, kind):
            counts[kind] = counts.get(kind, 0) + 1
            sents.append(tag(Sentence(f"{kind}#{counts[kind]}", kind, heading, txt), year))
    return Page(title, verified, sents)
