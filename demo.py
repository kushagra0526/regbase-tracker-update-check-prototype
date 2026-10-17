"""One fictional tracker page, one incoming event, the edit list and the checks.

python demo.py
"""
import datetime as dt

from trackcheck.check import check, impact
from trackcheck.facts import DEADLINE, DEFAULT_FACTS, STAGE
from trackcheck.page import parse

D = dt.date
PAGE = """# Example Packaging EPR Rule Tracker (fictional)
Last verified: October 14, 2026
## Status pill
Rule in effect
Reports due Nov 30, 2026
## At a glance
Stage | The rule is now final
First report due | September 30, 2026
Comment period | closed August 11, 2026
## General overview
The rule is now final. Covered producers must file by November 30, 2026. The deadline was moved from September 30 to November 30 when the board approved the rule.
## Details
The filing deadline set by the Recycling Board is September 30, 2026. A producer workshop is scheduled for October 2, 2026.
As of September 12, the Board's rulemaking page still lists the rule as under review.
The Board published the final text on October 6, 2026, fourteen days after approval on September 18, 2026.
## FAQ
When is the first report due? Reports are due September 30, 2026.
## Key dates
November 30, 2026 | First reports due
## Changelog
October 6, 2026: deadline changed from September 30, 2026 to November 30, 2026; rule approved.
"""
LEDGER = [{"fact": "deadline", "date": D(2026, 3, 2), "value": D(2026, 9, 30), "source": "proposed rule"},
          {"fact": "deadline", "date": D(2026, 10, 6), "value": D(2026, 11, 30), "source": "final rule text, Oct 6"},
          {"fact": "stage", "date": D(2026, 3, 2), "value": "proposed", "source": "proposed rule"},
          {"fact": "stage", "date": D(2026, 9, 18), "value": "final", "source": "Board approval"}]


def main():
    page = parse(PAGE)
    print(f"{page.title}: {len(page.sentences)} sentences, last verified {page.verified}\n")
    print("EVENT  deadline September 30, 2026 -> November 30, 2026 (final rule text, Oct 6). Sentences that must change:")
    for sid, heading, text, change in impact(page, DEADLINE, D(2026, 9, 30), D(2026, 11, 30)):
        print(f"  {sid:12s} [{heading}] {text}   ({change})")
    print("\nCHECKS after the update pass")
    for f in check(page, DEFAULT_FACTS, LEDGER):
        print(f"  {f['kind']:18s} [{f['heading']}] {f['why']}\n  {'':18s} \"{f['quote']}\"")
    left = [s.text for s in page.sentences if s.tense == "history"]
    print(f"\nleft alone as history ({len(left)}): " + " | ".join(t[:70] for t in left))


if __name__ == "__main__":
    main()
