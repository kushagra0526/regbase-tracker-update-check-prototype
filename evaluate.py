"""Score the checker and two baselines on synthetic tracker pages after an update pass.

python evaluate.py --dev      # dev phrase bank, 300 pages
python evaluate.py            # held-out phrase bank (eval/bank_heldout.py, frozen in git first), 500 pages
"""
import collections
import json
import re
import sys
from pathlib import Path

from trackcheck.check import check, state
from trackcheck.facts import DEFAULT_FACTS
from trackcheck.page import parse
from trackcheck.synth import case

KINDS = ["STALE_RESTATEMENT", "DATE_MATH", "PAST_FUTURE", "ASOF_LAG"]


def same(a, b):
    return a == b or (len(a) >= 10 and a in b) or (len(b) >= 10 and b in a)


def old_values(page, facts, ledger):
    out = []
    for fact in facts:
        _, old = state(ledger, fact, page.verified)
        out += [(fact, o) for o in old]
    return out


def grep_old(page, facts, ledger):
    """Flag every sentence that contains a superseded value, wherever it is."""
    F = []
    for s in page.sentences:
        ds = {d for _, _, d in s.dates}
        for fact, o in old_values(page, facts, ledger):
            hit = (o in ds) if fact["type"] == "date" else bool(re.search(fact["stage_phrases"][o], s.text, re.I))
            if hit:
                F.append({"kind": "STALE_RESTATEMENT", "text": s.text})
                break
    return F


def glance_only(page, facts, ledger):
    """What a status-pill / at-a-glance check against the ledger sees."""
    return [f for f in grep_old(page, facts, ledger)
            if any(s.text == f["text"] and s.section in ("pill", "glance") for s in page.sentences)]


POLICIES = {"glance_only": glance_only, "grep_old": grep_old, "trackcheck": lambda p, f, l: check(p, f, l)}


def run(bank, seeds):
    S = {p: collections.Counter() for p in POLICIES}
    misses, falses = collections.Counter(), []
    for seed in seeds:
        text, ledger, truth = case(seed, bank)
        page = parse(text)
        for name, pol in POLICIES.items():
            found = pol(page, DEFAULT_FACTS, ledger)
            for t, kind in truth.items():
                S[name][f"{kind}_planted"] += 1
                if any(f["kind"] == kind and same(f["text"], t) for f in found):
                    S[name][f"{kind}_caught"] += 1
                elif name == "trackcheck":
                    misses[kind] += 1
            for f in found:
                if not any(f["kind"] == k and same(f["text"], t) for t, k in truth.items()):
                    S[name]["false_flags"] += 1
                    S[name][f"false_{f['kind']}"] += 1
                    if name == "trackcheck" and len(falses) < 40:
                        falses.append((seed, f["kind"], f["text"][:160], f["why"][:160]))
            S[name]["pages"] += 1
            S[name]["sentences"] += len(page.sentences)
    return {p: dict(c) for p, c in S.items()}, falses


def main():
    dev = "--dev" in sys.argv
    if dev:
        from trackcheck import bank_dev as bank
        seeds = range(0, 300)
    else:
        from eval import bank_heldout as bank
        seeds = range(100_000, 100_500)
    S, falses = run(bank, seeds)
    print(f"{'dev' if dev else 'held-out'}: {len(seeds)} pages")
    for p, c in S.items():
        row = "  ".join(f"{k[:5]} {c.get(k + '_caught', 0)}/{c.get(k + '_planted', 0)}" for k in KINDS)
        print(f"  {p:12s} {row}  false flags {c.get('false_flags', 0)} (of {c['sentences']} sentences)")
    print("\ntrackcheck false flags (first 40):")
    for x in falses:
        print("  ", x)
    Path("out").mkdir(exist_ok=True)
    Path(f"out/{'dev' if dev else 'heldout'}.json").write_text(json.dumps({"summary": S, "false_examples": falses}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
