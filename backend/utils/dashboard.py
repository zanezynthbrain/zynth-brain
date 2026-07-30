"""ZYNTH Command Center — interactive, responsive productivity dashboard.

- build_state(): full JSON state (departments, works, actions, tasks, activity,
  data, scorecard) served at /api/state and embedded in the page for first paint.
- render_spa(): a self-contained single-page app — a LIVING neural brain (Canvas)
  whose nodes are the agency's real works (prospects, proposals, venues, notes,
  tasks…). Light pulses run core→department→work, and fire brightly along a
  department's path whenever its data actually changes. Every department is
  workable from a slide-in drawer: run its actions, add/move/assign tasks.

No external requests: Canvas graph, vanilla JS, inline CSS. Works on phone,
tablet and desktop.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_POOL = Path("outputs/proposal_pool")

DEPT_META = {
    "BD":         {"color": "#1FB4D8", "label": "BD & Sales",   "icon": "🎯"},
    "Events":     {"color": "#E0A83D", "label": "Events",       "icon": "🎪"},
    "Creative":   {"color": "#E5675F", "label": "Creative",     "icon": "🎨"},
    "Marketing":  {"color": "#3FB27F", "label": "Marketing",    "icon": "📣"},
    "Operations": {"color": "#59C1F0", "label": "Operations",   "icon": "⚙️"},
    "Finance":    {"color": "#9B8CFF", "label": "Finance",      "icon": "💰"},
    "Content":    {"color": "#E0883D", "label": "Content",      "icon": "🗂️"},
}


def _read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def build_state() -> dict[str, Any]:
    from config import get_settings
    from utils.tasks import all_tasks, tasks_by_department, recent_activity, DEPARTMENTS
    s = get_settings()

    # data sources
    leads = _read_json(_POOL / "leads.json", [])
    open_leads = [l for l in leads if l.get("stage") not in ("won", "lost")]
    open_value = sum(float(l.get("value_sgd") or 0) for l in open_leads)
    proposals = _read_json(_POOL / "index.json", [])

    try:
        from utils.suppliers import all_suppliers
        suppliers = all_suppliers()
    except Exception:
        suppliers = []
    try:
        from utils.venues import all_venues
        venues = all_venues()
    except Exception:
        venues = []
    try:
        from utils.events import all_events as _all_events, stage_counts as _ev_counts
        events = _all_events()
        ev_counts = _ev_counts()
        ev_active = sum(v for k, v in ev_counts.items() if k not in ("closed", "lost"))
    except Exception:
        events, ev_counts, ev_active = [], {}, 0
    try:
        from utils.knowledge import list_knowledge_files
        knowledge = sum(1 for _, _, a in list_knowledge_files() if a)
    except Exception:
        knowledge = 0
    notes = len(list((_POOL / "vault").rglob("*.md"))) if (_POOL / "vault").is_dir() else 0
    try:
        from utils.prospects import stats as _pstats, seed_if_empty as _pseed
        _pseed()  # load the starter set on first view so it's never a false 0
        pstats = _pstats()
    except Exception:
        pstats = {"total": 0, "hot": 0, "added_week": 0}

    # scorecard
    scorecard = []
    reds = 0
    try:
        from utils.business import SCORECARD, _load as _bload, _status
        state = _bload().get("scorecard", {})
        for spec in SCORECARD:
            e = state.get(spec["key"])
            if e is None:
                scorecard.append({"label": spec["label"], "value": None, "status": "none", "target": spec["target"]})
            else:
                st = _status(spec, e["value"])
                if st == "🔴":
                    reds += 1
                scorecard.append({"label": spec["label"], "value": e["value"],
                                  "status": {"🟢": "good", "🔴": "bad"}.get(st, "muted"), "target": spec["target"]})
        audit_done = bool(_bload().get("audit", {}).get("completed_at"))
    except Exception:
        audit_done = False

    tbd = tasks_by_department()
    sc_filled = sum(1 for x in scorecard if x["value"] is not None)

    # per-department data headline
    dept_data = {
        "BD": f"{pstats['total']} prospects · {len(leads)} leads · S${int(open_value):,} open",
        "Events": f"{ev_active} live events · {len(venues)} venues · {len(suppliers)} suppliers",
        "Creative": "portfolio & concepts",
        "Marketing": f"{len(proposals)} proposals",
        "Operations": "rhythm · consolidation",
        "Finance": f"scorecard {sc_filled}/12" + (f" · {reds} red" if reds else ""),
        "Content": f"{notes} notes · {knowledge} knowledge",
    }

    # per-department "works" — the real things you have, the neural-brain leaf nodes.
    # Each work node lights up when its count grows between refreshes.
    dept_works = {
        "BD": [{"label": "prospects", "value": pstats["total"]},
               {"label": "hot", "value": pstats["hot"]},
               {"label": "leads", "value": len(leads)}],
        "Events": [{"label": "events", "value": ev_active},
                   {"label": "confirmed", "value": ev_counts.get("confirmed", 0) + ev_counts.get("preproduction", 0)},
                   {"label": "venues", "value": len(venues)},
                   {"label": "suppliers", "value": len(suppliers)}],
        "Creative": [{"label": "concepts", "value": len(recent_activity(40, department="Creative"))}],
        "Marketing": [{"label": "proposals", "value": len(proposals)}],
        "Operations": [{"label": "actions", "value": len(recent_activity(40, department="Operations"))}],
        "Finance": [{"label": "KPIs", "value": sc_filled},
                    {"label": "reds", "value": reds}],
        "Content": [{"label": "notes", "value": notes},
                    {"label": "knowledge", "value": knowledge}],
    }

    # per-department runnable actions (whitelisted commands the dashboard can queue)
    dept_actions = {
        "BD": [{"cmd": "research", "label": "Scout Prospects"},
               {"cmd": "autopilot", "label": "Run BD Autopilot"}],
        "Marketing": [{"cmd": "proposals", "label": "Generate Proposals"},
                      {"cmd": "research", "label": "Market Intel"}],
        "Operations": [{"cmd": "brief", "label": "Daily CEO Brief"},
                       {"cmd": "consolidation", "label": "Consolidate"},
                       {"cmd": "improve", "label": "Self-Improve"},
                       {"cmd": "push", "label": "Sync → Obsidian"}],
        "Finance": [{"cmd": "costaudit", "label": "Cost Audit"}],
        "Content": [{"cmd": "push", "label": "Sync → Obsidian"}],
        "Events": [],
        "Creative": [],
    }

    departments = []
    for d in DEPARTMENTS:
        items = tbd.get(d, [])
        counts = {st: sum(1 for t in items if t.get("status") == st) for st in ("todo", "doing", "done")}
        departments.append({
            "name": d,
            "label": DEPT_META[d]["label"],
            "color": DEPT_META[d]["color"],
            "icon": DEPT_META[d]["icon"],
            "data": dept_data.get(d, ""),
            "works": dept_works.get(d, []),
            "actions": dept_actions.get(d, []),
            "tasks": {"counts": counts, "items": items[-25:]},
            "activity": recent_activity(8, department=d),
            "load": counts["todo"] + counts["doing"] + len(recent_activity(20, department=d)),
        })

    all_t = all_tasks()

    # ── cost vitals ──
    cap = float(getattr(s, "daily_budget_sgd", 5.0) or 5.0)
    try:
        from utils.costaudit import _spend_last_days
        today_sgd, today_calls = _spend_last_days(1)
        week_sgd, week_calls = _spend_last_days(7)
    except Exception:
        today_sgd = week_sgd = 0.0
        today_calls = week_calls = 0
    cost = {"today": round(today_sgd, 2), "cap": cap, "week": round(week_sgd, 2),
            "calls_today": today_calls, "calls_week": week_calls,
            "pct": min(100, round((today_sgd / cap * 100) if cap else 0))}

    # ── pipeline by stage ──
    STAGE_ORDER = ["new", "contacted", "meeting", "proposal", "won", "lost"]
    pipeline = []
    for st in STAGE_ORDER:
        in_st = [l for l in leads if l.get("stage") == st]
        pipeline.append({"stage": st, "count": len(in_st),
                         "value": int(sum(float(l.get("value_sgd") or 0) for l in in_st))})

    # ── deliverables index (proposals + queued outreach) ──
    deliverables = []
    for p in (proposals or [])[-30:]:
        if isinstance(p, dict):
            deliverables.append({
                "title": p.get("title") or p.get("name") or p.get("concept") or "Proposal",
                "meta": " · ".join(str(p.get(k, "")) for k in ("industry", "market") if p.get(k)),
                "date": p.get("created_at") or p.get("date") or "",
                "type": "proposal",
            })
    deliverables.reverse()

    # ── today's directives (top 3, heuristic) ──
    directives = []
    if not audit_done:
        directives.append("Run /audit — set your starting line")
    if pstats.get("hot"):
        directives.append(f"Work {pstats['hot']} hot prospects (/prospects)")
    try:
        from utils.outreach import pending as _oq
        q = len(_oq())
        if q:
            directives.append(f"Review {q} outreach drafts (/queue)")
    except Exception:
        pass
    if reds:
        directives.append(f"Fix {reds} red KPI{'s' if reds > 1 else ''} (/scorecard)")
    if not leads:
        directives.append("Land the first real client — leverage on 0 clients is 0")
    directives = directives[:3]

    # ── sync + brain status ──
    try:
        from utils import gitsync
        sync_on = gitsync.is_configured()
    except Exception:
        sync_on = False

    try:
        from utils import switches as _sw
        switch_list = _sw.all_switches()
        md_only = _sw.md_only()
    except Exception:
        switch_list, md_only = [], False

    return {
        "generated": datetime.now().strftime("%a %d %b %Y, %H:%M"),
        "model": getattr(s, "model_name", ""),
        "cost": cost,
        "pipeline": pipeline,
        "deliverables": deliverables,
        "directives": directives,
        "sync_on": sync_on,
        "switches": switch_list,
        "md_only": md_only,
        "sys": {"ai": bool(s.anthropic_api_key), "voice": bool(s.gemini_api_key),
                "email": bool(s.smtp_user and s.smtp_password), "sync": sync_on},
        "totals": {
            "leads": len(leads), "open_value": int(open_value), "proposals": len(proposals),
            "prospects": pstats["total"], "prospects_hot": pstats["hot"], "prospects_week": pstats.get("added_week", 0),
            "suppliers": len(suppliers), "venues": len(venues), "notes": notes,
            "tasks_open": sum(1 for t in all_t if t.get("status") != "done"), "reds": reds,
        },
        "scorecard": scorecard,
        "audit_done": audit_done,
        "departments": departments,
        "activity": recent_activity(30),
    }


def render_dashboard() -> str:
    """Alias kept for the /health snapshot path."""
    return render_spa()


def render_spa() -> str:
    state_json = json.dumps(build_state())
    return _HUD.replace("__STATE__", state_json)


_HUD = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>ZYNTH Command</title>
<style>
:root{
  --bg:#0A0E12; --panel:#0F141A; --panel2:#131B23; --border:#1E2A35;
  --cyan:#1FB4D8; --teal:#0D7C99; --ink:#FFFFFF; --mut:#7C8B9A;
  --good:#3FB27F; --warn:#E0A83D; --bad:#E5675F;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:
  radial-gradient(1200px 600px at 82% -12%, rgba(31,180,216,.07), transparent),
  radial-gradient(900px 500px at 8% 108%, rgba(155,140,255,.05), transparent),
  var(--bg); color:var(--ink);
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  -webkit-font-smoothing:antialiased; overscroll-behavior:none}
a{color:var(--cyan);text-decoration:none}
.top{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;
  padding:12px 16px;background:rgba(10,14,18,.82);backdrop-filter:blur(8px);border-bottom:1px solid var(--border)}
.brand{display:flex;align-items:center;gap:11px}
.hex{width:30px;height:30px;filter:drop-shadow(0 0 6px rgba(31,180,216,.5))}
.title{font-weight:700;letter-spacing:.16em;font-size:14px}
.title small{display:block;color:var(--mut);font-size:9.5px;letter-spacing:.24em;font-weight:400}
.clock{color:var(--cyan);font-size:12.5px;font-variant-numeric:tabular-nums}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
.chip{font-size:10.5px;padding:3px 9px;border-radius:4px;border:1px solid var(--border);background:var(--panel);letter-spacing:.05em}
.chip .d{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle}
.on{background:var(--good)} .off{background:var(--bad)}
.ticker{width:100%;font-size:11px;color:var(--mut);letter-spacing:.04em;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.ticker b{color:var(--cyan)}
/* neural brain hero */
.brainwrap{position:relative;margin:14px 16px 0;max-width:1500px;margin-left:auto;margin-right:auto;
  background:radial-gradient(700px 380px at 50% 42%, rgba(31,180,216,.05), transparent), var(--panel);
  border:1px solid var(--border);border-radius:14px;overflow:hidden}
#brain{display:block;width:100%;height:46vh;min-height:340px;max-height:560px;touch-action:manipulation;cursor:pointer}
.brainhead{position:absolute;top:12px;left:14px;pointer-events:none}
.brainhead .h{margin:0}
.brainhead .fx{font-size:11px;color:var(--mut);margin-top:3px;min-height:14px}
.brainhead .fx b{color:var(--cyan)}
.legend{position:absolute;top:12px;right:14px;display:flex;flex-wrap:wrap;gap:5px 8px;justify-content:flex-end;max-width:55%;pointer-events:none}
.legend span{font-size:10px;color:var(--mut);display:flex;align-items:center;gap:4px}
.legend i{width:8px;height:8px;border-radius:50%;display:inline-block}
.brainhint{position:absolute;bottom:10px;left:14px;font-size:10.5px;color:var(--mut);pointer-events:none}
.h{font-size:10.5px;letter-spacing:.18em;color:var(--cyan);text-transform:uppercase;margin:0 0 12px;
  display:flex;align-items:center;gap:8px}
.h::before{content:"";width:6px;height:6px;background:var(--cyan);box-shadow:0 0 8px var(--cyan)}
.grid{display:grid;grid-template-columns:1fr 1.15fr 1fr;gap:14px;padding:14px 16px 96px;max-width:1500px;margin:0 auto}
@media(max-width:980px){.grid{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px}
.mut{color:var(--mut)}
.gauge{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.gauge b{font-size:26px;font-variant-numeric:tabular-nums}
.bar{height:8px;border-radius:6px;background:var(--panel2);overflow:hidden;border:1px solid var(--border)}
.bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--teal),var(--cyan))}
.sub{font-size:11px;color:var(--mut);margin-top:6px;display:flex;justify-content:space-between}
.pipe{margin:7px 0}
.pipe .lab{display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px}
.pipe .lab span:last-child{color:var(--mut)}
.pipe .track{height:6px;background:var(--panel2);border-radius:5px;overflow:hidden}
.pipe .track>i{display:block;height:100%;background:var(--cyan);opacity:.85}
.score{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.sc{background:var(--panel2);border:1px solid var(--border);border-radius:7px;padding:8px 9px;font-size:11px}
.sc .t{display:flex;align-items:center;gap:6px;color:var(--mut)}
.dot{width:7px;height:7px;border-radius:50%;flex:none}
.sc b{font-size:14px;font-variant-numeric:tabular-nums;display:block;margin-top:3px}
.ev{display:flex;gap:9px;padding:9px 0;border-top:1px solid var(--border);font-size:12.5px;line-height:1.4}
.ev:first-child{border-top:0}
.ev .ed{width:8px;height:8px;border-radius:50%;margin-top:5px;flex:none}
.ev small{color:var(--mut);font-size:10.5px}
.deliv{display:flex;gap:9px;padding:9px 0;border-top:1px solid var(--border);font-size:12.5px}
.deliv:first-child{border-top:0}
.deliv .ic{color:var(--teal)}
.deliv small{color:var(--mut);display:block;font-size:10.5px}
.empty{color:var(--mut);font-size:12px;padding:8px 0}
/* department rail */
.rail{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px}
.dcard{background:var(--panel2);border:1px solid var(--border);border-radius:9px;padding:11px;cursor:pointer;
  transition:.12s;border-left:3px solid var(--cyan)}
.dcard:hover{transform:translateY(-2px);border-color:var(--cyan)}
.dcard .n{font-size:12.5px;display:flex;align-items:center;gap:7px}
.dcard .m{font-size:10px;color:var(--mut);margin-top:5px}
.dcard .b{display:flex;gap:5px;margin-top:8px}
.dcard .b span{font-size:9px;color:var(--mut);background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:1px 6px}
.deck{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.cmd{background:var(--panel2);border:1px solid var(--border);color:var(--ink);border-radius:8px;
  padding:12px 10px;font:inherit;font-size:12px;cursor:pointer;text-align:left;transition:.12s;letter-spacing:.03em}
.cmd:hover{border-color:var(--cyan);color:var(--cyan)}
.cmd .k{display:block;color:var(--mut);font-size:9.5px;letter-spacing:.14em;margin-bottom:3px}
.add{display:flex;gap:7px;margin-top:10px}
.add select,.add input{background:var(--panel2);border:1px solid var(--border);color:var(--ink);
  border-radius:7px;padding:9px;font:inherit;font-size:12px;min-width:0}
.add input{flex:1}
.add button{background:var(--cyan);color:#04222b;border:0;border-radius:7px;padding:9px 13px;font:inherit;font-weight:700;cursor:pointer}
.tk{display:flex;align-items:center;gap:8px;font-size:12px;padding:7px 0;border-top:1px solid var(--border)}
.tk:first-child{border-top:0}
.tk .s{font-size:9px;color:var(--mut);border:1px solid var(--border);border-radius:4px;padding:1px 5px;letter-spacing:.08em}
.tk .c{color:var(--mut);flex:none}
/* drawer */
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.55);opacity:0;pointer-events:none;transition:.2s;z-index:40}
.scrim.open{opacity:1;pointer-events:auto}
.drawer{position:fixed;z-index:50;background:var(--panel);border:1px solid var(--border);
  transition:transform .24s cubic-bezier(.4,0,.2,1)}
@media(max-width:640px){.drawer{left:0;right:0;bottom:0;border-radius:16px 16px 0 0;max-height:88vh;transform:translateY(103%)}.drawer.open{transform:translateY(0)}}
@media(min-width:641px){.drawer{top:0;bottom:0;right:0;width:min(460px,94vw);border-radius:14px 0 0 14px;transform:translateX(103%)}.drawer.open{transform:translateX(0)}}
.din{padding:18px 18px calc(22px + env(safe-area-inset-bottom));overflow:auto;height:100%}
.din h2{font-size:16px;margin:0 0 3px;display:flex;align-items:center;gap:9px;letter-spacing:.02em}
.close{position:absolute;top:13px;right:15px;background:var(--panel2);border:1px solid var(--border);
  color:var(--ink);width:32px;height:32px;border-radius:8px;font-size:15px;cursor:pointer}
.wchip{display:inline-flex;gap:6px;align-items:baseline;font-size:11px;background:var(--panel2);
  border:1px solid var(--border);border-radius:6px;padding:5px 9px;margin:0 6px 6px 0}
.wchip b{font-size:14px;font-variant-numeric:tabular-nums}
.act{display:block;width:100%;text-align:left;background:var(--panel2);border:1px solid var(--border);
  color:var(--ink);border-radius:8px;padding:11px 12px;font:inherit;font-size:12.5px;cursor:pointer;margin-top:7px;transition:.12s}
.act:hover{border-color:var(--cyan);color:var(--cyan)}
.act .k{color:var(--mut);font-size:9.5px;letter-spacing:.14em;margin-right:8px}
.task{background:var(--panel2);border:1px solid var(--border);border-radius:9px;padding:10px 11px;margin-top:8px;font-size:12.5px}
.task.done .ttl{text-decoration:line-through;color:var(--mut)}
.task .row{display:flex;align-items:center;gap:8px}
.task .ttl{flex:1}
.cb{border:1px solid var(--border);background:var(--panel);color:var(--mut);border-radius:6px;font:inherit;font-size:10.5px;padding:3px 8px;cursor:pointer}
.cb.on{color:#04222b;border-color:transparent}
.asg{display:flex;gap:6px;margin-top:8px;align-items:center}
.asg input{flex:1;background:var(--panel);border:1px solid var(--border);color:var(--ink);border-radius:6px;padding:6px 9px;font:inherit;font-size:11.5px;min-width:0}
.sect{font-size:10px;letter-spacing:.16em;color:var(--mut);text-transform:uppercase;margin:18px 2px 4px}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(20px);opacity:0;
  background:var(--cyan);color:#04222b;padding:10px 16px;border-radius:8px;font-size:12.5px;font-weight:700;
  transition:.25s;z-index:60;pointer-events:none}
.toast.on{opacity:1;transform:translateX(-50%) translateY(0)}
.live{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--good);margin-right:5px;animation:bl 2s infinite}
@keyframes bl{50%{opacity:.3}}
.modebtn{width:100%;text-align:center;border:1px solid var(--border);border-radius:8px;padding:11px;font:inherit;
  font-size:12px;cursor:pointer;background:var(--panel2);color:var(--ink);margin-bottom:10px;letter-spacing:.03em}
.sw{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:11px;padding:6px 0;border-top:1px solid var(--border)}
.sw:first-child{border-top:0}
.sw span{color:var(--mut)}
.tgl{border:1px solid var(--border);background:var(--panel);color:var(--mut);border-radius:6px;font:inherit;
  font-size:9.5px;padding:3px 11px;cursor:pointer;letter-spacing:.1em;flex:none}
.tgl.on{background:var(--good);color:#04222b;border-color:transparent}
</style></head><body>
<div class="top">
  <div class="brand">
    <svg class="hex" viewBox="0 0 100 100"><polygon points="50,3 93,26 93,74 50,97 7,74 7,26" fill="none" stroke="#1FB4D8" stroke-width="5"/><text x="50" y="63" text-anchor="middle" font-size="42" fill="#1FB4D8" font-family="monospace" font-weight="700">Z</text></svg>
    <div class="title">ZYNTH COMMAND<small>THE INTELLIGENCE OF CREATIVITY</small></div>
  </div>
  <div class="clock" id="clock">--:--:--</div>
  <div class="chips" id="chips"></div>
  <div class="ticker" id="ticker"></div>
</div>

<div class="brainwrap">
  <canvas id="brain"></canvas>
  <div class="brainhead">
    <div class="h">Agency Brain</div>
    <div class="fx" id="brainfx">initialising neural map…</div>
  </div>
  <div class="legend" id="legend"></div>
  <div class="brainhint">tap a node to open its department · light fires when something updates</div>
</div>

<div class="grid">
  <div>
    <div class="panel">
      <div class="h">System Vitals</div>
      <div class="gauge"><b id="costToday">S$0.00</b><span class="mut" id="costCap">/ S$5 cap</span></div>
      <div class="bar"><i id="costBar" style="width:0%"></i></div>
      <div class="sub"><span id="costWeek">7-day: S$0</span><span id="model">—</span></div>
    </div>
    <div class="panel" style="margin-top:14px">
      <div class="h">Pipeline</div>
      <div id="pipeline"></div>
    </div>
    <div class="panel" style="margin-top:14px">
      <div class="h">Scorecard · 12 KPIs</div>
      <div class="score" id="score"></div>
    </div>
  </div>
  <div>
    <div class="panel">
      <div class="h">Departments · tap to work</div>
      <div class="rail" id="rail"></div>
    </div>
    <div class="panel" style="margin-top:14px">
      <div class="h"><span class="live"></span>Activity Feed</div>
      <div id="feed"></div>
    </div>
    <div class="panel" style="margin-top:14px">
      <div class="h">Deliverables Index</div>
      <div id="deliv"></div>
    </div>
  </div>
  <div>
    <div class="panel">
      <div class="h">Command Deck</div>
      <div class="deck" id="deck"></div>
      <div class="add">
        <select id="dept"></select>
        <input id="tin" placeholder="add task…" onkeydown="if(event.key==='Enter')addTask()">
        <button onclick="addTask()">+</button>
      </div>
    </div>
    <div class="panel" style="margin-top:14px">
      <div class="h">Mode &amp; Switches</div>
      <div id="mode"></div>
      <div id="switches"></div>
    </div>
    <div class="panel" style="margin-top:14px">
      <div class="h">Open Work</div>
      <div id="tasks"></div>
    </div>
  </div>
</div>

<div class="scrim" id="scrim" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer"><button class="close" onclick="closeDrawer()">✕</button><div class="din" id="din"></div></div>
<div class="toast" id="toast"></div>

<script>
let S = __STATE__;
let CURRENT = null;
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const DC={BD:'#1FB4D8',Events:'#E0A83D',Creative:'#E5675F',Marketing:'#3FB27F',Operations:'#59C1F0',Finance:'#9B8CFF',Content:'#E0883D'};
const CMDS=[['brief','CEO','Daily Brief'],['research','BD','Scout Prospects'],['autopilot','BD','Run Autopilot'],['proposals','WORK','Gen Proposals'],['improve','SELF','Self-Improve'],['consolidation','OPS','Consolidate'],['costaudit','FIN','Cost Audit'],['push','SYNC','Push→Obsidian']];

function clock(){const d=new Date(new Date().toLocaleString('en-US',{timeZone:'Asia/Yangon'}));$('#clock').textContent=d.toTimeString().slice(0,8)+' YGN';}
setInterval(clock,1000);clock();
function toast(m){const t=$('#toast');t.textContent=m;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),2400);}

/* ============ panels ============ */
function render(){
  const sys=S.sys||{}, c=S.cost||{today:0,cap:5,week:0,pct:0};
  $('#chips').innerHTML=[['BRAIN',sys.ai],['SYNC',sys.sync],['EMAIL',sys.email],['VOICE',sys.voice]]
    .map(([n,ok])=>`<span class="chip"><span class="d ${ok?'on':'off'}"></span>${n}</span>`).join('');
  const dir=(S.directives||[]);
  $('#ticker').innerHTML=dir.length?('▸ '+dir.map(esc).join('  ·  ')):'▸ <b>All clear.</b> Feed the machine a brief.';
  $('#costToday').textContent='S$'+(c.today||0).toFixed(2);
  $('#costCap').textContent='/ S$'+c.cap+' cap';
  const bar=$('#costBar');bar.style.width=Math.min(100,c.pct||0)+'%';
  bar.style.background=(c.pct>=100)?'var(--bad)':(c.pct>=80?'linear-gradient(90deg,var(--warn),var(--bad))':'linear-gradient(90deg,var(--teal),var(--cyan))');
  $('#costWeek').textContent='7-day: S$'+(c.week||0).toFixed(2)+' · '+(c.calls_week||0)+' calls';
  $('#model').textContent=S.model||'';
  const pipe=S.pipeline||[];const mx=Math.max(1,...pipe.map(p=>p.count));
  $('#pipeline').innerHTML=pipe.map(p=>`<div class="pipe"><div class="lab"><span>${esc(p.stage)}</span><span>${p.count}${p.value?(' · S$'+p.value.toLocaleString()):''}</span></div><div class="track"><i style="width:${Math.round(p.count/mx*100)}%"></i></div></div>`).join('')||'<div class="empty">No leads yet — /enrich a company.</div>';
  const tone={good:'var(--good)',bad:'var(--bad)',muted:'var(--warn)',none:'var(--border)'};
  $('#score').innerHTML=(S.scorecard||[]).map(x=>`<div class="sc"><div class="t"><span class="dot" style="background:${tone[x.status]||'var(--border)'}"></span>${esc(x.label)}</div><b>${x.value==null?'—':esc(x.value)}</b></div>`).join('')||'<div class="empty">Run /audit to activate.</div>';
  // department rail
  $('#rail').innerHTML=(S.departments||[]).map(d=>{const c2=d.tasks.counts;
    return `<div class="dcard" style="border-left-color:${d.color}" onclick="openDept('${d.name}')">
      <div class="n"><span>${d.icon}</span>${esc(d.label)}</div>
      <div class="m">${esc(d.data)}</div>
      <div class="b"><span>${c2.todo} todo</span><span>${c2.doing} doing</span></div></div>`;}).join('');
  const feed=(S.activity||[]);
  $('#feed').innerHTML=feed.length?feed.slice(0,20).map(a=>`<div class="ev"><span class="ed" style="background:${DC[a.department]||'var(--mut)'}"></span><div>${esc(a.text)}<br><small>${esc(a.department||'')} · ${esc(a.at||'')}</small></div></div>`).join(''):'<div class="empty">No activity yet — it streams here as the agency works.</div>';
  const dv=(S.deliverables||[]);
  $('#deliv').innerHTML=dv.length?dv.slice(0,18).map(d=>`<div class="deliv"><span class="ic">▤</span><div>${esc(d.title)}<small>${esc(d.meta||'')}${d.date?(' · '+esc(d.date)):''}</small></div></div>`).join(''):'<div class="empty">No deliverables yet — /proposal or /event to create.</div>';
  $('#deck').innerHTML=CMDS.map(([k,tag,label])=>`<button class="cmd" onclick="cmd('${k}')"><span class="k">${tag}</span>${label}</button>`).join('');
  const depts=(S.departments||[]).map(d=>d.name);
  if($('#dept').options.length===0)$('#dept').innerHTML=depts.map(n=>`<option>${n}</option>`).join('');
  let open=[];(S.departments||[]).forEach(d=>(d.tasks.items||[]).forEach(t=>{if(t.status!=='done')open.push({...t,dept:d.name});}));
  $('#tasks').innerHTML=open.length?open.slice(0,14).map(t=>`<div class="tk"><span class="s">${esc(t.status)}</span><span style="flex:1">${esc(t.title)}</span><span class="c" style="color:${DC[t.dept]||'var(--mut)'}">${esc(t.dept)}</span></div>`).join(''):'<div class="empty">No open tasks.</div>';
  // legend
  $('#legend').innerHTML=(S.departments||[]).map(d=>`<span><i style="background:${d.color}"></i>${esc(d.label)}</span>`).join('');
  // mode + switches
  const autoOn=!S.md_only;
  const mb=$('#mode');
  if(mb){mb.innerHTML=`<button class="modebtn" style="border-color:${autoOn?'var(--good)':'var(--warn)'};color:${autoOn?'var(--good)':'var(--warn)'}" onclick="toggleSwitch('autonomy',${autoOn?1:0})">${autoOn?'🟢 AUTONOMOUS ON — tap for MD-ONLY (save cost)':'🌙 MD-ONLY — tap to WAKE autonomous work'}</button>`;}
  const sws=$('#switches');
  if(sws){sws.innerHTML=(S.switches||[]).filter(s=>!s.master).map(s=>`<div class="sw"><span>${esc(s.name)}</span><button class="tgl ${s.effective?'on':''}" onclick="toggleSwitch('${s.name}',${s.on?1:0})">${s.on?'ON':'OFF'}</button></div>`).join('');}
}
async function toggleSwitch(name,cur){await api('/api/switch',{name,on:!cur});toast(name+' → '+(!cur?'ON':'OFF'));refresh();}

/* ============ neural brain ============ */
const cv=$('#brain'), cx=cv.getContext('2d');
let DPR=Math.min(2,window.devicePixelRatio||1), W=0, H=0;
let B={core:null, depts:[]};        // laid-out nodes
let SIG=[];                          // active signal pulses
let PREV=null, LASTACT='';          // change detection
let HOVER=null;

function sizeCanvas(){W=cv.clientWidth;H=cv.clientHeight;cv.width=W*DPR;cv.height=H*DPR;cx.setTransform(DPR,0,0,DPR,0,0);}
function layoutBrain(){
  sizeCanvas();
  const cxp=W/2, cyp=H/2, R1=Math.min(W,H)*0.30, R2=R1+Math.min(W,H)*0.20;
  B.core={x:cxp,y:cyp};
  const ds=(S.departments||[]);
  B.depts=ds.map((d,i)=>{
    const a=-Math.PI/2 + i*2*Math.PI/Math.max(1,ds.length);
    const works=(d.works||[]).filter(w=>w.value>0);
    const node={name:d.name,label:d.label,color:d.color,icon:d.icon,load:d.load||0,a,
      x:cxp+Math.cos(a)*R1, y:cyp+Math.sin(a)*R1, ph:Math.random()*6.28, flash:0, works:[]};
    const spread=0.42;
    works.forEach((w,j)=>{
      const wa=a + (works.length>1? (j/(works.length-1)-0.5)*spread : 0);
      node.works.push({label:w.label,value:w.value,color:d.color,dept:d.name,
        x:cxp+Math.cos(wa)*R2, y:cyp+Math.sin(wa)*R2, ph:Math.random()*6.28, flash:0});
    });
    return node;
  });
}
function worksMap(){const m={};(S.departments||[]).forEach(d=>(d.works||[]).forEach(w=>m[d.name+'|'+w.label]=w.value));return m;}
function findDept(n){return B.depts.find(d=>d.name===n);}
function fire(deptName, workLabel, kind){
  const d=findDept(deptName); if(!d) return;
  const path=[B.core,{x:d.x,y:d.y,node:d}];
  if(workLabel){const w=(d.works||[]).find(x=>x.label===workLabel); if(w) path.push({x:w.x,y:w.y,node:w});}
  SIG.push({path, color:d.color, t0:performance.now(), dur:kind==='idle'?1500:1050, kind:kind||'event'});
  if(SIG.length>26) SIG.shift();
  d.flash=performance.now()+900;
}
function ptAlong(path,u){
  if(path.length<2) return path[0];
  const seg=1/(path.length-1); let i=Math.min(path.length-2,Math.floor(u/seg)); let f=(u-i*seg)/seg;
  const a=path[i], b=path[i+1]; return {x:a.x+(b.x-a.x)*f, y:a.y+(b.y-a.y)*f};
}
function drawLink(a,b,col,w,al){cx.strokeStyle=col;cx.globalAlpha=al;cx.lineWidth=w;cx.beginPath();cx.moveTo(a.x,a.y);cx.lineTo(b.x,b.y);cx.stroke();cx.globalAlpha=1;}
function nodeAt(mx,my){
  for(const d of B.depts){ for(const w of d.works){ if(Math.hypot(mx-w.x,my-w.y)<15) return {dept:d.name}; }
    if(Math.hypot(mx-d.x,my-d.y)< (16+Math.min(10,d.load)) +6) return {dept:d.name}; }
  return null;
}
function draw(t){
  cx.clearRect(0,0,W,H);
  const C=B.core; if(!C){requestAnimationFrame(draw);return;}
  // gentle float
  B.depts.forEach(d=>{d.dx=Math.sin(t/1400+d.ph)*3;d.dy=Math.cos(t/1600+d.ph)*3;
    d.works.forEach(w=>{w.dx=Math.sin(t/1300+w.ph)*2.4;w.dy=Math.cos(t/1500+w.ph)*2.4;});});
  const P=n=>({x:n.x+(n.dx||0),y:n.y+(n.dy||0)});
  // links + ambient pulses
  B.depts.forEach((d,i)=>{
    const dp=P(d);
    drawLink(C,dp,d.color,1+Math.min(3,d.load*0.25),0.16);
    let u=((t/2600)+(i*0.13))%1; let ap=ptAlong([C,dp],u);
    cx.fillStyle=d.color;cx.globalAlpha=0.35;cx.beginPath();cx.arc(ap.x,ap.y,1.7,0,7);cx.fill();cx.globalAlpha=1;
    d.works.forEach((w,j)=>{const wp=P(w);
      drawLink(dp,wp,d.color,1,0.12);
      let u2=((t/2200)+(j*0.2)+(i*0.05))%1; let bp=ptAlong([dp,wp],u2);
      cx.fillStyle=d.color;cx.globalAlpha=0.25;cx.beginPath();cx.arc(bp.x,bp.y,1.4,0,7);cx.fill();cx.globalAlpha=1;
    });
  });
  // signal pulses (the meaningful ones)
  SIG=SIG.filter(s=>t-s.t0 < s.dur);
  SIG.forEach(s=>{
    const u=Math.min(1,(t-s.t0)/s.dur); const p=ptAlong(s.path,u);
    const bright=s.kind==='idle'?0.5:1;
    // trail
    for(let k=1;k<=6;k++){const uk=Math.max(0,u-k*0.035);const pk=ptAlong(s.path,uk);
      cx.fillStyle=s.color;cx.globalAlpha=bright*(0.16-k*0.02);cx.beginPath();cx.arc(pk.x,pk.y,3.2,0,7);cx.fill();}
    cx.globalAlpha=1;
    const g=cx.createRadialGradient(p.x,p.y,0,p.x,p.y,9);g.addColorStop(0,s.color);g.addColorStop(1,'transparent');
    cx.fillStyle=g;cx.globalAlpha=bright;cx.beginPath();cx.arc(p.x,p.y,9,0,7);cx.fill();
    cx.fillStyle='#fff';cx.globalAlpha=bright;cx.beginPath();cx.arc(p.x,p.y,2.2,0,7);cx.fill();cx.globalAlpha=1;
  });
  // core
  const puls=(Math.sin(t/650)+1)/2;
  for(let k=3;k>=1;k--){cx.fillStyle='rgba(31,180,216,'+(0.05*k)+')';cx.beginPath();cx.arc(C.x,C.y,20+k*7+puls*4,0,7);cx.fill();}
  cx.fillStyle='#1FB4D8';cx.beginPath();cx.arc(C.x,C.y,15,0,7);cx.fill();
  cx.fillStyle='#04222b';cx.font='700 14px ui-monospace,monospace';cx.textAlign='center';cx.textBaseline='middle';cx.fillText('Z',C.x,C.y);
  // department + work nodes
  B.depts.forEach(d=>{
    const dp=P(d); const r=16+Math.min(10,d.load); const hot=HOVER&&HOVER.dept===d.name;
    d.works.forEach(w=>{const wp=P(w); const wr=6+Math.min(9,Math.log2(w.value+1)*2.6);
      cx.fillStyle=w.color;cx.globalAlpha=0.13;cx.beginPath();cx.arc(wp.x,wp.y,wr+6,0,7);cx.fill();cx.globalAlpha=1;
      cx.fillStyle=w.color;cx.globalAlpha=0.85;cx.beginPath();cx.arc(wp.x,wp.y,wr,0,7);cx.fill();cx.globalAlpha=1;
      cx.fillStyle='#04121a';cx.font='700 9px ui-monospace,monospace';cx.fillText(String(w.value),wp.x,wp.y);
      cx.fillStyle='var(--mut)';cx.fillStyle='#7C8B9A';cx.font='9px ui-monospace,monospace';cx.fillText(w.label,wp.x,wp.y+wr+9);
    });
    // glow + flash
    if(d.flash>t){const fu=(d.flash-t)/900;cx.strokeStyle=d.color;cx.globalAlpha=fu*0.9;cx.lineWidth=2;cx.beginPath();cx.arc(dp.x,dp.y,r+8+(1-fu)*10,0,7);cx.stroke();cx.globalAlpha=1;}
    cx.fillStyle=d.color;cx.globalAlpha=hot?0.28:0.16;cx.beginPath();cx.arc(dp.x,dp.y,r+7,0,7);cx.fill();cx.globalAlpha=1;
    cx.fillStyle=d.color;cx.beginPath();cx.arc(dp.x,dp.y,r,0,7);cx.fill();
    cx.font='700 13px ui-monospace,monospace';cx.fillText(d.icon,dp.x,dp.y);
    cx.fillStyle=hot?'#fff':'#9fb0bf';cx.font='700 10px ui-monospace,monospace';cx.fillText(d.label,dp.x,dp.y+r+13);
    const open=(S.departments.find(x=>x.name===d.name)||{tasks:{counts:{}}}).tasks.counts;
    const badge=(open.todo||0)+(open.doing||0);
    if(badge){cx.fillStyle='#04222b';cx.beginPath();cx.arc(dp.x+r*0.72,dp.y-r*0.72,7,0,7);cx.fill();
      cx.fillStyle=d.color;cx.beginPath();cx.arc(dp.x+r*0.72,dp.y-r*0.72,7,0,7);cx.fill();
      cx.fillStyle='#04222b';cx.font='700 9px ui-monospace,monospace';cx.fillText(String(badge),dp.x+r*0.72,dp.y-r*0.72);}
  });
  requestAnimationFrame(draw);
}
// pointer
cv.addEventListener('pointermove',e=>{const r=cv.getBoundingClientRect();HOVER=nodeAt(e.clientX-r.left,e.clientY-r.top);
  const fx=$('#brainfx');
  if(HOVER){const d=S.departments.find(x=>x.name===HOVER.dept);fx.innerHTML='▸ <b>'+esc(d.label)+'</b> — '+esc(d.data)+' · tap to open';cv.style.cursor='pointer';}
  else{cv.style.cursor='default';fx.innerHTML=idleFx();}});
cv.addEventListener('click',e=>{const r=cv.getBoundingClientRect();const n=nodeAt(e.clientX-r.left,e.clientY-r.top);if(n)openDept(n.dept);});
function idleFx(){const a=(S.activity||[])[0];return a?('▸ last: <b>'+esc(a.text).slice(0,54)+'</b>'):'▸ <b>'+(S.departments||[]).length+'</b> departments online · brain nominal';}

/* boot + change detection */
function bootSweep(){let i=0;const ds=(S.departments||[]);(function step(){if(i>=ds.length)return;fire(ds[i].name,null,'idle');i++;setTimeout(step,120);})();}
function detectChanges(){
  const now=worksMap();
  if(PREV){for(const k in now){if(now[k]>(PREV[k]??now[k])){const[dep,lab]=k.split('|');fire(dep,lab,'event');}}}
  PREV=now;
  const a=(S.activity||[])[0]; const sig=a?(a.text+'|'+a.at):'';
  if(sig && LASTACT && sig!==LASTACT && a.department){fire(a.department,null,'event');}
  LASTACT=sig;
}
// ambient "thought" so it always feels alive
setInterval(()=>{const ds=(S.departments||[]).filter(d=>(d.works||[]).some(w=>w.value>0));if(!ds.length)return;
  const d=ds[Math.floor(Math.random()*ds.length)];fire(d.name,null,'idle');},3800);

/* ============ actions ============ */
async function api(path,body){try{const r=await fetch(path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});return await r.json();}catch(e){return{ok:false}}}
async function cmd(k,dept){toast('Queued: '+k+' — watch Telegram');if(dept)fire(dept,null,'event');await api('/api/cmd',{cmd:k});}
async function addTask(){const el=$('#tin');const v=(el.value||'').trim();if(!v)return;const dp=$('#dept').value;el.value='';fire(dp,null,'event');await api('/api/task',{action:'add',title:v,department:dp});toast('Task added → '+dp);refresh();}
async function refresh(){const s=await api('/api/state');if(s&&s.departments){const nOld=(S.departments||[]).length;S=s;render();detectChanges();if((S.departments||[]).length!==nOld||!B.core)layoutBrain();else syncLayout();if(CURRENT)fillDrawer(CURRENT);}}
function syncLayout(){ // keep positions, refresh values/works
  (S.departments||[]).forEach(d=>{const n=findDept(d.name);if(!n)return;n.load=d.load||0;
    const works=(d.works||[]).filter(w=>w.value>0);
    // update existing, add new near dept angle
    const cxp=W/2,cyp=H/2,R2=Math.min(W,H)*0.30+Math.min(W,H)*0.20,spread=0.42;
    n.works=works.map((w,j)=>{const ex=(findDept(d.name).works||[]).find(o=>o.label===w.label);
      const wa=n.a+(works.length>1?(j/(works.length-1)-0.5)*spread:0);
      return ex?{...ex,value:w.value}:{label:w.label,value:w.value,color:d.color,dept:d.name,x:cxp+Math.cos(wa)*R2,y:cyp+Math.sin(wa)*R2,ph:Math.random()*6.28,flash:0};});});
}

/* ============ department drawer ============ */
function openDept(name){CURRENT=name;fillDrawer(name);$('#scrim').classList.add('open');$('#drawer').classList.add('open');}
function closeDrawer(){CURRENT=null;$('#scrim').classList.remove('open');$('#drawer').classList.remove('open');}
function fillDrawer(name){
  const d=(S.departments||[]).find(x=>x.name===name);if(!d)return;
  const works=(d.works||[]).map(w=>`<span class="wchip"><b style="color:${d.color}">${w.value}</b>${esc(w.label)}</span>`).join('')||'<span class="mut" style="font-size:11px">no works yet</span>';
  const acts=(d.actions||[]).map(a=>`<button class="act" onclick="cmd('${a.cmd}','${name}')"><span class="k">RUN</span>${esc(a.label)}</button>`).join('')
    || `<div class="empty">No one-tap command here yet. Plan ${esc(d.label).toLowerCase()} via Telegram (/event, /video) or add a task below.</div>`;
  const items=(d.tasks.items||[]).slice().reverse();
  const tasks=items.length?items.map(tk=>`
    <div class="task ${tk.status}"><div class="row"><span class="ttl">${esc(tk.title)} <small class="mut">[${esc(tk.id)}]</small></span></div>
      <div class="row" style="margin-top:7px">${['todo','doing','done'].map(st=>`<button class="cb ${tk.status===st?'on':''}" style="${tk.status===st?'background:'+d.color:''}" onclick="move('${esc(tk.id)}','${st}')">${st}</button>`).join('')}</div>
      <div class="asg"><span class="mut">👤</span><input id="as_${esc(tk.id)}" placeholder="assignee" value="${esc(tk.assignee||'')}"><button class="cb" onclick="assign('${esc(tk.id)}')">save</button></div>
    </div>`).join(''):'<div class="empty">No tasks yet — add the first below.</div>';
  const act=(d.activity||[]).map(a=>`<div class="ev"><span class="ed" style="background:${d.color}"></span><div>${esc(a.text)}<br><small>${esc(a.at||'')}</small></div></div>`).join('')||'<div class="empty">No recent activity.</div>';
  $('#din').innerHTML=`
    <h2><span class="dot" style="background:${d.color};width:11px;height:11px"></span>${d.icon} ${esc(d.label)}</h2>
    <div class="mut" style="font-size:11.5px;margin-bottom:12px">${esc(d.data)}</div>
    <div>${works}</div>
    <div class="sect">Run</div>${acts}
    <div class="sect">Add task</div>
    <div class="add"><input id="dtin" placeholder="task for ${esc(d.label)}…" onkeydown="if(event.key==='Enter')addDeptTask('${name}')"><button onclick="addDeptTask('${name}')">+</button></div>
    <div class="sect">Tasks</div>${tasks}
    <div class="sect">Activity</div><div>${act}</div>`;
}
async function addDeptTask(name){const el=$('#dtin');const v=(el.value||'').trim();if(!v)return;el.value='';fire(name,null,'event');await api('/api/task',{action:'add',title:v,department:name});toast('Task added');await refresh();}
async function move(id,st){await api('/api/task',{action:'status',id,status:st});await refresh();}
async function assign(id){const v=($('#as_'+id).value||'').trim();await api('/api/task',{action:'assign',id,assignee:v});await refresh();toast('Assigned');}

/* ============ boot ============ */
window.addEventListener('resize',()=>{layoutBrain();});
render();layoutBrain();PREV=worksMap();LASTACT=((S.activity||[])[0]||{}).text||'';
$('#brainfx').innerHTML=idleFx();
requestAnimationFrame(draw);
setTimeout(bootSweep,300);
setInterval(refresh,12000);
</script></body></html>"""
