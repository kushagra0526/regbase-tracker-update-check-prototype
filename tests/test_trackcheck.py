import datetime as dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from trackcheck.check import check, impact
from trackcheck.dates import find_dates, number
from trackcheck.facts import DEADLINE, DEFAULT_FACTS, STAGE
from trackcheck.page import parse

D = dt.date
PAGE = """# Test Rule Tracker
Last verified: October 13, 2026
## Status pill
First deadline Nov 10, 2026
## At a glance
Deadline | August 10, 2026
## General overview
The first deadline is November 10, 2026. The deadline was moved from August 10 to November 10. The rule remains proposed.
## Details
A public hearing is scheduled for September 9, 2026. As of September 15, the agency page still lists the rule as under review.
The record closed July 30, 2026, twenty days after the hearing on July 10, 2026.
## Changelog
October 12, 2026: deadline changed from August 10, 2026 to November 10, 2026.
"""
LEDGER = [{"fact": "deadline", "date": D(2026, 2, 1), "value": D(2026, 8, 10), "source": "notice"},
          {"fact": "deadline", "date": D(2026, 6, 24), "value": D(2026, 11, 10), "source": "bulletin"},
          {"fact": "stage", "date": D(2026, 1, 1), "value": "proposed"},
          {"fact": "stage", "date": D(2026, 10, 12), "value": "final", "source": "approval"}]


def kinds(found):
    return {(f["kind"], f["section"]) for f in found}


def test_dates_and_number_words():
    assert [d for _, _, d in find_dates("due Sept. 15 and Dec 26, 2025", 2026)] == [D(2026, 9, 15), D(2025, 12, 26)]
    assert number("twenty-one") == 21 and number("120") == 120


def test_stale_restatement_skips_history_and_changelog():
    found = check(parse(PAGE), DEFAULT_FACTS, LEDGER)
    stale = [f for f in found if f["kind"] == "STALE_RESTATEMENT"]
    assert {f["section"] for f in stale} == {"glance", "overview"}      # glance date + "remains proposed"
    assert not any("moved from" in f["text"] for f in stale)


def test_date_math_exact_and_wrong():
    page = parse(PAGE)
    assert not [f for f in check(page) if f["kind"] == "DATE_MATH"]       # July 10 + 20 days = July 30
    bad = parse(PAGE.replace("July 30, 2026, twenty days", "August 4, 2026, twenty days"))
    assert [f for f in check(bad) if f["kind"] == "DATE_MATH"]


def test_deadline_subject_math_uses_the_due_date():
    page = parse("# t\nLast verified: September 1, 2026\n## Feed\nComments now due August 31, 2026 — the deadline arrives twenty days after the July 10 announcement.")
    f = [x for x in check(page) if x["kind"] == "DATE_MATH"]
    assert f and "52 days" in f[0]["why"]


def test_rule_text_is_not_a_claim():
    page = parse("# t\nLast verified: September 23, 2026\n## Body\nThose denied report 30 days after the notice or by September 15, whichever is later.")
    assert not check(page)


def test_past_future_and_asof_lag():
    k = kinds(check(parse(PAGE)))
    assert ("PAST_FUTURE", "body") in k and ("ASOF_LAG", "body") in k
    ok = parse(PAGE.replace("is scheduled for September 9", "was held on September 9").replace("As of September 15", "As of October 10"))
    assert not {x for x in kinds(check(ok)) if x[0] in ("PAST_FUTURE", "ASOF_LAG")}


def test_impact_list_for_an_incoming_event():
    rows = impact(parse(PAGE), DEADLINE, D(2026, 8, 10), D(2026, 11, 10))
    assert [r[0].split("#")[0] for r in rows] == ["glance"]
    assert impact(parse(PAGE), STAGE, "proposed", "final")[0][0].startswith("overview")
