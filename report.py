"""out/report.html from the held-out results and the public-page run (python report.py)."""
import html
import json
from pathlib import Path

OUT = Path(__file__).parent / "out"
H = json.loads((OUT / "heldout.json").read_text())["summary"]
F = json.loads((OUT / "heldout_first_run.json").read_text())["summary"]
R = json.loads((OUT / "real_pages.json").read_text(encoding="utf-8")) if (OUT / "real_pages.json").exists() else {}
KINDS = [("STALE_RESTATEMENT", "stale restatements"), ("DATE_MATH", "date-math slips"), ("PAST_FUTURE", "future wording, past date"),
         ("ASOF_LAG", "old as-of claims")]
# my own reading of each live finding (sentence start -> verdict); everything else is "worth a look"
VERDICT = {"Food chemical": "real slip", "The submission period": "false alarm", "Stat. §": "false alarm"}


def cells(s):
    return "".join(f"<td>{s.get(k + '_caught', 0)}/{s.get(k + '_planted', 0)}</td>" for k, _ in KINDS) + f"<td>{s.get('false_flags', 0)}</td>"


rows = (f"<tr><td>Status pill + at-a-glance check</td>{cells(F['glance_only'])}</tr>"
        f"<tr><td>Grep for the old value</td>{cells(F['grep_old'])}</tr>"
        f"<tr><td>trackcheck, first run</td>{cells(F['trackcheck'])}</tr>"
        f"<tr style='font-weight:700;color:#1d6b3c'><td>trackcheck, after vocabulary fix</td>{cells(H['trackcheck'])}</tr>")
live = ""
for slug, r in R.items():
    for f in r["findings"]:
        v = next((v for k, v in VERDICT.items() if f["quote"].startswith(k)), "worth a look")
        col = {"real slip": "#c0392b", "false alarm": "#888"}.get(v, "#c98a12")
        live += (f"<div class='f'><b style='color:{col}'>{v}</b> · {f['kind']} · regbase.com/{slug} · {html.escape(f['heading'][:50])}<br>"
                 f"<span class='m'>{html.escape(f['why'][:170])}</span></div>")
page = f"""<!doctype html><meta charset="utf-8"><title>Tracker update check</title>
<style>body{{font-family:Segoe UI,sans-serif;margin:28px;color:#1b1f24;width:1180px}}td,th{{padding:7px 12px;border-bottom:1px solid #ddd;text-align:right}}
td:first-child,th:first-child{{text-align:left}}.f{{border-left:4px solid #ddd;padding:5px 10px;margin:6px 0;font-size:14px}}.m{{color:#555}}</style>
<h2>Tracker pages after an update pass → what still says the old thing</h2>
<p class="m">Held-out: 500 synthetic tracker pages, new wording frozen in git before the first run; 14,070 sentences. Each cell is caught/planted.</p>
<table><tr><th>Check</th>{''.join(f'<th>{n}</th>' for _, n in KINDS)}<th>false flags</th></tr>{rows}</table>
<h3>Read-only run on Regbase's 6 public tracker pages</h3>{live}"""
(OUT / "report.html").write_text(page, encoding="utf-8")
print("wrote out/report.html")
