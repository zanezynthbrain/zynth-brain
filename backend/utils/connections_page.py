"""Render the connection report as a standalone HTML control surface.

This is the MD's "is everything wired?" page. It is generated *from* a live
:func:`utils.connections.summary` run, so it can never show a stale green light:
if the page says a link is up, the check said so at the timestamp printed on it.

Usage:
    python -m utils.connections_page > page.html
    python -m utils.connections_page --out ../deliverables/ops/connections.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

from utils import connections

_ICON = {"ok": "●", "warn": "▲", "down": "■"}
_WORD = {"ok": "connected", "warn": "degraded", "down": "not connected"}

_CSS = """
:root{
  --bg:#F5F3EE; --card:#FFF; --ink:#15181D; --ink2:#535B68; --ink3:#858D9A;
  --line:#DFDACE; --ok:#1F6F43; --warn:#9A6608; --down:#9E2C2C;
  --accent:#8A6F1E; --shadow:0 1px 2px rgba(20,24,31,.06);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0A0E15; --card:#121926; --ink:#ECEAE4; --ink2:#A7AFBD; --ink3:#6B7484;
  --line:#1F2937; --ok:#4FBE85; --warn:#DDA83F; --down:#E2726A;
  --accent:#C9A227; --shadow:none;
}}
:root[data-theme="dark"]{
  --bg:#0A0E15; --card:#121926; --ink:#ECEAE4; --ink2:#A7AFBD; --ink3:#6B7484;
  --line:#1F2937; --ok:#4FBE85; --warn:#DDA83F; --down:#E2726A;
  --accent:#C9A227; --shadow:none;
}
:root[data-theme="light"]{
  --bg:#F5F3EE; --card:#FFF; --ink:#15181D; --ink2:#535B68; --ink3:#858D9A;
  --line:#DFDACE; --ok:#1F6F43; --warn:#9A6608; --down:#9E2C2C;
  --accent:#8A6F1E; --shadow:0 1px 2px rgba(20,24,31,.06);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:860px;margin:0 auto;padding:44px 22px 70px}
h1{font-family:Georgia,"Times New Roman",serif;font-weight:400;
  font-size:clamp(28px,4.4vw,40px);letter-spacing:-.02em;margin:0 0 6px}
.sub{color:var(--ink2);margin:0 0 4px}
.stamp{color:var(--ink3);font-size:13px;font-variant-numeric:tabular-nums;margin:0 0 30px}
.tally{display:flex;gap:1px;background:var(--line);border:1px solid var(--line);
  border-radius:3px;overflow:hidden;margin-bottom:32px}
.t{flex:1;background:var(--card);padding:16px 18px}
.t .n{font-family:Georgia,serif;font-size:30px;line-height:1.1;font-variant-numeric:tabular-nums}
.t .l{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3);
  font-weight:600;margin-top:5px}
.t.ok .n{color:var(--ok)} .t.warn .n{color:var(--warn)} .t.down .n{color:var(--down)}
.link{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
  border-radius:3px;padding:18px 20px;margin-bottom:12px;box-shadow:var(--shadow)}
.link.ok{border-left-color:var(--ok)}
.link.warn{border-left-color:var(--warn)}
.link.down{border-left-color:var(--down)}
.hd{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.dot{font-size:13px;line-height:1}
.link.ok .dot{color:var(--ok)} .link.warn .dot{color:var(--warn)} .link.down .dot{color:var(--down)}
.nm{font-weight:600;font-size:17px}
.st{margin-left:auto;font-size:11px;letter-spacing:.12em;text-transform:uppercase;font-weight:600}
.link.ok .st{color:var(--ok)} .link.warn .st{color:var(--warn)} .link.down .st{color:var(--down)}
.dt{color:var(--ink2);margin:8px 0 0}
.fx{margin-top:12px;padding:10px 12px;background:var(--bg);border:1px solid var(--line);
  border-radius:3px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:13px;color:var(--ink);overflow-x:auto;white-space:pre}
.fx b{display:block;font-family:ui-sans-serif,system-ui,sans-serif;font-size:10px;
  letter-spacing:.13em;text-transform:uppercase;color:var(--ink3);margin-bottom:5px;font-weight:600}
details{margin-top:10px}
summary{cursor:pointer;font-size:13px;color:var(--ink3);user-select:none}
summary:hover{color:var(--accent)}
pre.facts{margin:8px 0 0;padding:10px 12px;background:var(--bg);border:1px solid var(--line);
  border-radius:3px;font-size:12.5px;overflow-x:auto;color:var(--ink2)}
.note{border-left:2px solid var(--accent);padding:2px 0 2px 16px;margin:30px 0 0;
  color:var(--ink2);font-size:14.5px;max-width:64ch}
footer{margin-top:38px;padding-top:20px;border-top:1px solid var(--line);
  color:var(--ink3);font-size:13px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""


def render(summary: dict | None = None) -> str:
    s = summary or connections.summary()
    e = html.escape
    tally, overall = s["tally"], s["overall"]

    head = {
        "ok": "Everything is connected.",
        "warn": "Connected, with things that need attention.",
        "down": "Something is not connected.",
    }[overall]

    parts = [
        "<title>ZYNTH — Connections</title>",
        f"<style>{_CSS}</style>",
        '<div class="wrap">',
        "<h1>Connections</h1>",
        f'<p class="sub">{e(head)}</p>',
        f'<p class="stamp">Checked {e(s["checked_at"])} · every light below was '
        "verified at that moment, not remembered.</p>",
        '<div class="tally">',
        f'<div class="t ok"><div class="n">{tally["ok"]}</div><div class="l">Connected</div></div>',
        f'<div class="t warn"><div class="n">{tally["warn"]}</div><div class="l">Needs attention</div></div>',
        f'<div class="t down"><div class="n">{tally["down"]}</div><div class="l">Not connected</div></div>',
        "</div>",
    ]

    order = {"down": 0, "warn": 1, "ok": 2}
    for l in sorted(s["links"], key=lambda x: order.get(x["status"], 9)):
        st = l["status"]
        parts.append(f'<div class="link {st}">')
        parts.append(
            f'<div class="hd"><span class="dot">{_ICON[st]}</span>'
            f'<span class="nm">{e(l["name"])}</span>'
            f'<span class="st">{_WORD[st]}</span></div>'
        )
        parts.append(f'<p class="dt">{e(l["detail"])}</p>')
        if l.get("fix"):
            parts.append(f'<div class="fx"><b>To fix</b>{e(l["fix"])}</div>')
        if l.get("facts"):
            parts.append(
                "<details><summary>What was checked</summary>"
                f'<pre class="facts">{e(json.dumps(l["facts"], indent=2))}</pre></details>'
            )
        parts.append("</div>")

    parts += [
        '<p class="note">This page is generated from a live check. Re-run it any time with '
        "<code>/connections</code> in Telegram, or regenerate the page with "
        "<code>python -m utils.connections_page</code> from <code>backend/</code>. "
        "A green light here means the check passed when the timestamp says — it is never a "
        "stored assumption.</p>",
        "<footer>ZYNTH Asia — operations control surface. "
        "Secrets are never read or printed by these checks; only whether they are set.</footer>",
        "</div>",
    ]
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render the ZYNTH connections page.")
    ap.add_argument("--out", help="write to this path instead of stdout")
    args = ap.parse_args(argv)
    page = render()
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(page, encoding="utf-8")
        print(f"wrote {p} ({len(page)/1024:.1f} KB)", file=sys.stderr)
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
