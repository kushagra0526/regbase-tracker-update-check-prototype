"""Run the checks on Regbase's public tracker pages (read-only: one GET per page, nothing else).

python real_pages.py             # fetch live pages, print findings, write out/real_pages.json
python real_pages.py --cache D   # use HTML files saved in directory D instead of fetching

Page text is not stored in this repo; findings quote at most one sentence each.
"""
import html as H
import json
import re
import sys
import urllib.request
from pathlib import Path

from trackcheck.check import check
from trackcheck.page import parse

PAGES = ["trackers", "sb-253", "gras-rule", "pfas-reporting-rule", "state-pfas-tracker", "state-food-additive-tracker"]
# restatement-conflict check needs to know which sentences talk about which fact
FACTS = {
    "sb-253": [{"key": "first_deadline", "type": "date", "cues": [r"first (?:SB 253 )?(?:annual )?(?:report(?:ing)? )?deadline", r"deadline is (?=[A-Z])", r"due on"]},
               {"key": "fee_notice", "type": "date", "cues": [r"fee (?:determination )?notice"]}],
    "gras-rule": [{"key": "gras_comments", "type": "date", "cues": [r"comments (?:on the proposed rule )?(?:are )?due"]}],
    "state-pfas-tracker": [{"key": "mn_extended", "type": "date", "cues": [r"extended (?:Amara.s Law )?reports"]}],
}


def text_of(fragment):
    t = re.sub(r"<br\s*/?>", "\n", fragment)
    t = re.sub(r"</(?:p|li|tr|div|h\d)>", "\n", t)
    t = re.sub(r"</t[dh]>", " | ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = H.unescape(t)
    return "\n".join(re.sub(r"[ \t]+", " ", l).strip(" |") for l in t.split("\n") if l.strip(" |\t"))


def to_canonical(raw):
    raw = re.sub(r"<(script|style|nav|footer|header)\b.*?</\1>", "", raw, flags=re.S | re.I)
    title = text_of(re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S).group(1))
    h1_end = raw.find("</h1>")
    first_h2 = raw.find("<h2", h1_end)
    head = raw[h1_end + 5:first_h2]
    verified = re.search(r"Last verified\s*(?:<[^>]+>\s*)*([A-Z][a-z]+ \d{1,2}, \d{4})", head)
    lead, _, pill = head.partition("Last verified")
    parts = re.split(r"<div[^>]*>", lead)
    pill_html = parts[-1] if len(parts) > 1 else ""
    lead_html = "".join(parts[:-1])
    pill_items = [x for x in (text_of(p) for p in re.split(r"<span[^>]*>\s*·\s*</span>", pill_html)) if x and x != "·"]
    out = [f"# {title}", f"Last verified: {verified.group(1) if verified else ''}", "## Update note", text_of(lead_html),
           "## Status pill", *pill_items]
    for m in re.finditer(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|\Z)", raw[first_h2:], re.S):
        heading = text_of(m.group(1))
        if heading.lower() in ("regbase",):
            continue
        out += [f"## {heading}", text_of(m.group(2))]
    return "\n".join(out)


def fetch(slug):
    req = urllib.request.Request(f"https://regbase.com/{slug}", headers={"User-Agent": "trackcheck-prototype (read-only, 1 request/page)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    cache = Path(sys.argv[sys.argv.index("--cache") + 1]) if "--cache" in sys.argv else None
    report = {}
    for slug in PAGES:
        raw = (cache / f"{slug}.html").read_text(encoding="utf-8") if cache else fetch(slug)
        page = parse(to_canonical(raw))
        found = check(page, FACTS.get(slug, []))
        report[slug] = {"title": page.title, "verified": str(page.verified), "sentences": len(page.sentences), "findings": found}
        print(f"\n== {page.title} (last verified {page.verified}; {len(page.sentences)} sentences) -> {len(found)} findings")
        for f in found:
            print(f"  [{f['kind']}] {f['heading'][:40]}: {f['why']}\n      \"{f['quote'][:200]}\"")
    Path("out").mkdir(exist_ok=True)
    Path("out/real_pages.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
