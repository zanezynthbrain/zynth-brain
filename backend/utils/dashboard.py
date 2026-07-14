"""ZYNTH Command Center — a live HTML dashboard of everything.

render_dashboard() reads all data sources fresh and returns a
self-contained HTML page (no external requests). Served live by the bot's
web server on Railway's $PORT, and sendable to Telegram via /dashboard.

Sections: system health · scorecard · BD pipeline · proposals · suppliers ·
venues · knowledge/notes · cost. Everything the MD has, in one scan.
"""

from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

_POOL = Path("outputs/proposal_pool")


def _read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _gather() -> dict[str, Any]:
    from config import get_settings
    data: dict[str, Any] = {"generated": datetime.now().strftime("%a %d %b %Y, %H:%M")}
    s = get_settings()

    # System
    from utils.llm_client import LLMClient
    data["sys"] = {
        "ai": not LLMClient().is_mocked,
        "voice": bool(s.gemini_api_key),
        "email": bool(s.smtp_user and s.smtp_password),
    }

    # Leads
    try:
        from utils.leads import all_leads, STAGES
        leads = all_leads()
        by_stage = {st: [l for l in leads if l.get("stage") == st] for st in STAGES}
        open_val = sum(float(l.get("value_sgd") or 0) for l in leads if l.get("stage") not in ("won", "lost"))
        data["leads"] = {"all": leads, "by_stage": by_stage, "stages": STAGES, "open_value": open_val}
    except Exception:
        data["leads"] = {"all": [], "by_stage": {}, "stages": [], "open_value": 0}

    # Vendors
    try:
        from utils.suppliers import all_suppliers
        vend = all_suppliers()
        cats: dict[str, int] = {}
        for v in vend:
            cats[v.get("category", "?")] = cats.get(v.get("category", "?"), 0) + 1
        data["vendors"] = {"count": len(vend), "verified": sum(1 for v in vend if v.get("verified")), "by_cat": cats}
    except Exception:
        data["vendors"] = {"count": 0, "verified": 0, "by_cat": {}}

    # Venues
    try:
        from utils.venues import all_venues
        ven = all_venues()
        data["venues"] = {"count": len(ven), "verified": sum(1 for v in ven if v.get("verified")),
                          "list": [(v.get("name"), v.get("type")) for v in ven]}
    except Exception:
        data["venues"] = {"count": 0, "verified": 0, "list": []}

    # Scorecard
    try:
        from utils.business import SCORECARD, _load as _bload, _status
        state = _bload().get("scorecard", {})
        rows = []
        for spec in SCORECARD:
            e = state.get(spec["key"])
            if e is None:
                rows.append((spec["label"], None, "none", spec["target"]))
            else:
                rows.append((spec["label"], e["value"], _status(spec, e["value"]), spec["target"]))
        data["scorecard"] = rows
        data["audit_done"] = bool(_bload().get("audit", {}).get("completed_at"))
    except Exception:
        data["scorecard"] = []
        data["audit_done"] = False

    # Proposals
    idx = _read_json(_POOL / "index.json", [])
    data["proposals"] = {"count": len(idx), "recent": list(reversed(idx))[:8]}

    # Knowledge + notes
    try:
        from utils.knowledge import list_knowledge_files
        kb = list_knowledge_files()
        data["knowledge"] = sum(1 for _, _, a in kb if a)
    except Exception:
        data["knowledge"] = 0
    data["notes"] = len(list((_POOL / "vault").rglob("*.md"))) if (_POOL / "vault").is_dir() else 0

    # FX
    try:
        from utils.fx import get_rates
        data["fx"] = get_rates().get("rates", {})
    except Exception:
        data["fx"] = {}
    return data


_STAGE_TONE = {"new": "muted", "contacted": "accent", "meeting": "accent",
               "proposal": "warn", "won": "good", "lost": "bad"}


def render_dashboard() -> str:
    d = _gather()
    sysd = d["sys"]

    def pill(ok, label):
        tone = "good" if ok else "warn"
        return f'<span class="pill {tone}">{"●" if ok else "○"} {escape(label)}</span>'

    # KPI strip from scorecard reds/greens
    reds = sum(1 for _, _, st, _ in d["scorecard"] if st == "🔴")
    set_n = sum(1 for _, v, _, _ in d["scorecard"] if v is not None)

    # Pipeline funnel
    stages_html = ""
    for st in d["leads"]["stages"]:
        n = len(d["leads"]["by_stage"].get(st, []))
        tone = _STAGE_TONE.get(st, "muted")
        stages_html += f'<div class="funnel-step"><span class="dot {tone}"></span><b>{n}</b><small>{escape(st)}</small></div>'

    lead_rows = ""
    for l in d["leads"]["all"][:10]:
        val = f'S${int(l["value_sgd"]):,}' if l.get("value_sgd") else "—"
        lead_rows += (
            f'<tr><td><b>{escape(str(l.get("company","?")))}</b><br><small>{escape(str(l.get("industry") or ""))}</small></td>'
            f'<td><span class="tag {_STAGE_TONE.get(l.get("stage","new"),"muted")}">{escape(str(l.get("stage","new")))}</span></td>'
            f'<td class="num">{val}</td><td><small>{escape(str(l.get("next_step") or ""))}</small></td></tr>'
        )
    if not lead_rows:
        lead_rows = '<tr><td colspan="4" class="empty">No leads yet — add with <code>/lead add</code></td></tr>'

    # Scorecard grid
    sc_html = ""
    tone_map = {"🟢": "good", "🔴": "bad", "none": "muted", "⚪": "muted"}
    for label, val, st, target in d["scorecard"]:
        tone = tone_map.get(st, "muted")
        shown = f"{val:g}" if val is not None else "—"
        sc_html += (
            f'<div class="metric"><div class="metric-top"><span class="dot {tone}"></span>'
            f'<span class="metric-val">{shown}</span></div>'
            f'<div class="metric-label">{escape(label)}</div>'
            f'<div class="metric-target">{escape(target)}</div></div>'
        )

    # Vendors by category
    vend_html = "".join(
        f'<div class="chip"><b>{n}</b> {escape(c)}</div>' for c, n in sorted(d["vendors"]["by_cat"].items(), key=lambda x: -x[1])
    ) or '<div class="empty">—</div>'

    # Proposals recent
    prop_html = ""
    for p in d["proposals"]["recent"]:
        prop_html += f'<li><b>{escape(str(p.get("title","?"))[:60])}</b><small>{escape(str(p.get("industry") or ""))} · {escape(str(p.get("month") or ""))} · {escape(str(p.get("market") or ""))}</small></li>'
    if not prop_html:
        prop_html = '<li class="empty">Pool building daily…</li>'

    # FX
    fx_html = " · ".join(f'{escape(k)} {int(v.get("sell",0)):,}' for k, v in d["fx"].items()) or "—"

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZYNTH Command Center</title>
<style>
:root{{
  --bg:#0d0e13; --surface:#161821; --surface2:#1d2029; --border:#272b37;
  --text:#e8e9ef; --muted:#8b8fa3; --accent:#6d6df0; --accent-soft:rgba(109,109,240,.15);
  --good:#34d399; --warn:#fbbf24; --bad:#f87171;
}}
@media (prefers-color-scheme: light){{
  :root{{ --bg:#f6f7fb; --surface:#fff; --surface2:#eef0f6; --border:#e3e5ee;
    --text:#191b23; --muted:#6a6e80; --accent:#5a5ae6; --accent-soft:rgba(90,90,230,.1);
    --good:#059669; --warn:#b45309; --bad:#dc2626; }}
}}
:root[data-theme="dark"]{{ --bg:#0d0e13; --surface:#161821; --surface2:#1d2029; --border:#272b37; --text:#e8e9ef; --muted:#8b8fa3; --good:#34d399; --warn:#fbbf24; --bad:#f87171; }}
:root[data-theme="light"]{{ --bg:#f6f7fb; --surface:#fff; --surface2:#eef0f6; --border:#e3e5ee; --text:#191b23; --muted:#6a6e80; --good:#059669; --warn:#b45309; --bad:#dc2626; }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.5;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:28px 20px 60px}}
header{{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;margin-bottom:8px}}
.brand{{display:flex;align-items:center;gap:12px}}
.logo{{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,var(--accent),#a78bfa);
  display:grid;place-items:center;font-weight:800;color:#fff;font-size:19px}}
h1{{font-size:20px;margin:0;letter-spacing:-.02em}}
.sub{{color:var(--muted);font-size:12.5px}}
.pills{{display:flex;gap:7px;flex-wrap:wrap}}
.pill{{font-size:11.5px;padding:4px 10px;border-radius:20px;background:var(--surface2);border:1px solid var(--border);font-weight:600}}
.pill.good{{color:var(--good)}} .pill.warn{{color:var(--warn)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:20px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:18px 18px 16px}}
.card.wide{{grid-column:1/-1}}
.card h2{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 14px;font-weight:700}}
.big{{font-size:34px;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums}}
.big small{{font-size:14px;color:var(--muted);font-weight:600}}
.funnel{{display:flex;gap:6px;justify-content:space-between}}
.funnel-step{{flex:1;text-align:center;background:var(--surface2);border-radius:10px;padding:12px 4px}}
.funnel-step b{{display:block;font-size:22px;font-variant-numeric:tabular-nums}}
.funnel-step small{{color:var(--muted);font-size:10.5px;text-transform:capitalize}}
.dot{{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--muted)}}
.dot.good{{background:var(--good)}} .dot.warn{{background:var(--warn)}} .dot.bad{{background:var(--bad)}} .dot.accent{{background:var(--accent)}} .dot.muted{{background:var(--muted)}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
td{{padding:9px 8px;border-top:1px solid var(--border);vertical-align:top}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
small{{color:var(--muted)}}
.tag{{font-size:11px;padding:2px 9px;border-radius:12px;background:var(--surface2);font-weight:600;text-transform:capitalize}}
.tag.good{{color:var(--good)}} .tag.warn{{color:var(--warn)}} .tag.bad{{color:var(--bad)}} .tag.accent{{color:var(--accent)}} .tag.muted{{color:var(--muted)}}
.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}}
.metric{{background:var(--surface2);border-radius:11px;padding:12px}}
.metric-top{{display:flex;align-items:center;gap:7px}}
.metric-val{{font-size:20px;font-weight:800;font-variant-numeric:tabular-nums}}
.metric-label{{font-size:11.5px;margin-top:3px}} .metric-target{{font-size:10.5px;color:var(--muted)}}
.chips{{display:flex;flex-wrap:wrap;gap:7px}}
.chip{{background:var(--surface2);border:1px solid var(--border);border-radius:9px;padding:6px 11px;font-size:12.5px}}
.chip b{{color:var(--accent)}}
ul.clean{{list-style:none;margin:0;padding:0}}
ul.clean li{{padding:8px 0;border-top:1px solid var(--border);font-size:13px}}
ul.clean li:first-child{{border-top:0}}
ul.clean small{{display:block}}
.empty{{color:var(--muted);font-style:italic;font-size:12.5px;padding:10px 0}}
.banner{{background:var(--accent-soft);border:1px solid var(--accent);border-radius:12px;padding:12px 14px;margin-top:16px;font-size:13px}}
code{{background:var(--surface2);padding:1px 6px;border-radius:5px;font-size:12px}}
footer{{margin-top:26px;color:var(--muted);font-size:12px;text-align:center}}
</style></head><body><div class="wrap">
<header>
  <div class="brand"><div class="logo">Z</div>
    <div><h1>ZYNTH Command Center</h1><div class="sub">The Intelligence of Creativity · {escape(d["generated"])}</div></div>
  </div>
  <div class="pills">{pill(sysd["ai"],"AI brain")}{pill(sysd["voice"],"Voice")}{pill(sysd["email"],"Email")}</div>
</header>

{"" if d["audit_done"] else '<div class="banner">🩺 <b>Week 0 Audit not done yet.</b> Run <code>/audit</code> in Telegram — it sets your starting line and activates the scorecard.</div>'}

<div class="grid">
  <div class="card">
    <h2>BD Pipeline</h2>
    <div class="big">{len(d["leads"]["all"])}<small> leads · S${int(d["leads"]["open_value"]):,} open</small></div>
    <div class="funnel" style="margin-top:14px">{stages_html or '<div class="empty">No leads yet</div>'}</div>
  </div>
  <div class="card">
    <h2>Proposals generated</h2>
    <div class="big">{d["proposals"]["count"]}</div>
    <div class="sub" style="margin-top:6px">Auto-built daily · IGNITE-standard on demand</div>
  </div>
  <div class="card">
    <h2>Resources</h2>
    <div class="chips">
      <div class="chip"><b>{d["vendors"]["count"]}</b> suppliers</div>
      <div class="chip"><b>{d["venues"]["count"]}</b> venues</div>
      <div class="chip"><b>{d["knowledge"]}</b> knowledge</div>
      <div class="chip"><b>{d["notes"]}</b> notes</div>
    </div>
    <div class="sub" style="margin-top:10px">FX: {fx_html}</div>
  </div>

  <div class="card wide">
    <h2>Leads — latest</h2>
    <table><tbody>{lead_rows}</tbody></table>
  </div>

  <div class="card wide">
    <h2>Master Scorecard {f'· <span style="color:var(--bad)">{reds} red</span>' if reds else ''} · {set_n}/12 set</h2>
    <div class="metrics">{sc_html or '<div class="empty">Run /scorecard set … to populate</div>'}</div>
  </div>

  <div class="card">
    <h2>Suppliers by category</h2>
    <div class="chips">{vend_html}</div>
  </div>
  <div class="card">
    <h2>Recent proposals</h2>
    <ul class="clean">{prop_html}</ul>
  </div>
</div>
<footer>ZYNTH · live data · refresh to update · built by your AI agency</footer>
</div>
<script>
// honour a saved theme toggle if the host stamps data-theme; default = OS
</script>
</body></html>"""
