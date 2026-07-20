"""ZYNTH Command Center — interactive, responsive productivity dashboard.

- build_state(): full JSON state (departments, tasks, activity, data, scorecard)
  served at /api/state and embedded in the page for first paint.
- render_spa(): a self-contained single-page app — a neural-network graph of
  the agency's departments (clickable), per-department tasks & activity, add/
  assign tasks, live polling so anything that hits Telegram shows up here.

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
    "BD":         {"color": "#6d6df0", "label": "BD & Sales",   "icon": "🎯"},
    "Events":     {"color": "#f59e0b", "label": "Events",       "icon": "🎪"},
    "Creative":   {"color": "#ec4899", "label": "Creative",     "icon": "🎨"},
    "Marketing":  {"color": "#34d399", "label": "Marketing",    "icon": "📣"},
    "Operations": {"color": "#38bdf8", "label": "Operations",   "icon": "⚙️"},
    "Finance":    {"color": "#a78bfa", "label": "Finance",      "icon": "💰"},
    "Content":    {"color": "#fb923c", "label": "Content",      "icon": "🗂️"},
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

    # per-department data headline
    dept_data = {
        "BD": f"{pstats['total']} prospects · {len(leads)} leads · S${int(open_value):,} open",
        "Events": f"{len(venues)} venues · {len(suppliers)} suppliers",
        "Creative": "portfolio & concepts",
        "Marketing": f"{len(proposals)} proposals",
        "Operations": "rhythm · consolidation",
        "Finance": f"scorecard {sum(1 for x in scorecard if x['value'] is not None)}/12" + (f" · {reds} red" if reds else ""),
        "Content": f"{notes} notes · {knowledge} knowledge",
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
            "tasks": {"counts": counts, "items": items[-25:]},
            "activity": recent_activity(6, department=d),
            "load": counts["todo"] + counts["doing"] + len(recent_activity(20, department=d)),
        })

    all_t = all_tasks()
    return {
        "generated": datetime.now().strftime("%a %d %b %Y, %H:%M"),
        "sys": {"ai": bool(s.anthropic_api_key), "voice": bool(s.gemini_api_key), "email": bool(s.smtp_user and s.smtp_password)},
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
    return _HTML.replace("__STATE__", state_json)


_HTML = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>ZYNTH Command Center</title>
<style>
:root{
  --bg:#0b0c11; --surface:#14161f; --surface2:#1b1e29; --border:#262a37;
  --text:#e9eaf1; --muted:#8a8ea3; --accent:#6d6df0;
  --good:#34d399; --warn:#fbbf24; --bad:#f87171;
}
@media (prefers-color-scheme: light){
  :root{ --bg:#f5f6fb; --surface:#fff; --surface2:#eef0f7; --border:#e2e4ee;
    --text:#181a22; --muted:#666a7d; --accent:#5a5ae6; --good:#059669; --warn:#b45309; --bad:#dc2626; }
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--text);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;overscroll-behavior:none}
.wrap{max-width:1240px;margin:0 auto;padding:16px 14px calc(80px + env(safe-area-inset-bottom))}
header{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:10px}
.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--accent),#a78bfa);
  display:grid;place-items:center;font-weight:800;color:#fff}
h1{font-size:17px;margin:0;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:11.5px}
.pills{display:flex;gap:6px;flex-wrap:wrap}
.pill{font-size:11px;padding:3px 9px;border-radius:20px;background:var(--surface2);border:1px solid var(--border);font-weight:600}
.pill.good{color:var(--good)} .pill.warn{color:var(--warn)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:14px 0}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:13px;padding:12px 13px}
.kpi b{font-size:22px;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.kpi span{display:block;font-size:11px;color:var(--muted);margin-top:1px}
.graphwrap{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:16px;
  overflow:hidden;margin-bottom:14px}
#graph{display:block;width:100%;height:340px;touch-action:manipulation}
.hint{position:absolute;left:12px;bottom:10px;font-size:11px;color:var(--muted);pointer-events:none}
.banner{background:color-mix(in srgb,var(--accent) 14%,transparent);border:1px solid var(--accent);
  border-radius:12px;padding:11px 13px;margin-bottom:14px;font-size:12.5px}
.section-title{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);
  font-weight:700;margin:18px 4px 10px}
.deptgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.dept{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px;cursor:pointer;
  transition:transform .12s,border-color .12s}
.dept:hover{transform:translateY(-2px)}
.dept-top{display:flex;align-items:center;gap:9px}
.dept-dot{width:11px;height:11px;border-radius:50%}
.dept h3{font-size:14px;margin:0;flex:1}
.dept .data{font-size:11.5px;color:var(--muted);margin:8px 0 10px}
.tbar{display:flex;gap:5px}
.tcount{flex:1;text-align:center;background:var(--surface2);border-radius:8px;padding:6px 2px}
.tcount b{display:block;font-size:15px;font-variant-numeric:tabular-nums}
.tcount span{font-size:9.5px;color:var(--muted);text-transform:uppercase}
.feed{margin-top:6px}
.feed .ev{display:flex;gap:8px;padding:7px 0;border-top:1px solid var(--border);font-size:12.5px}
.feed .ev:first-child{border-top:0}
.feed .evd{width:9px;height:9px;border-radius:50%;margin-top:4px;flex:none}
.feed small{color:var(--muted)}
/* drawer */
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.5);opacity:0;pointer-events:none;transition:.2s;z-index:40}
.scrim.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;z-index:50;background:var(--surface);border:1px solid var(--border);
  transition:transform .24s cubic-bezier(.4,0,.2,1)}
@media (max-width:640px){
  .drawer{left:0;right:0;bottom:0;border-radius:18px 18px 0 0;max-height:86vh;transform:translateY(102%)}
  .drawer.on{transform:translateY(0)}
}
@media (min-width:641px){
  .drawer{top:0;bottom:0;right:0;width:min(440px,92vw);border-radius:16px 0 0 16px;transform:translateX(103%)}
  .drawer.on{transform:translateX(0)}
}
.drawer-in{padding:18px 18px calc(20px + env(safe-area-inset-bottom));overflow:auto;height:100%}
.drawer h2{font-size:18px;margin:0 0 2px;display:flex;align-items:center;gap:9px}
.close{position:absolute;top:14px;right:16px;background:var(--surface2);border:1px solid var(--border);
  color:var(--text);width:32px;height:32px;border-radius:9px;font-size:16px;cursor:pointer}
.task{background:var(--surface2);border-radius:10px;padding:10px 11px;margin-top:8px;font-size:13px}
.task .row{display:flex;align-items:center;gap:8px}
.task .ttl{flex:1}
.task.done .ttl{text-decoration:line-through;color:var(--muted)}
.chipbtn{border:1px solid var(--border);background:var(--bg);color:var(--muted);border-radius:7px;
  font-size:11px;padding:3px 8px;cursor:pointer}
.chipbtn.active{color:#fff;border-color:transparent}
.addbox{display:flex;gap:8px;margin-top:14px}
.addbox input{flex:1;background:var(--surface2);border:1px solid var(--border);color:var(--text);
  border-radius:10px;padding:11px 12px;font-size:14px;min-width:0}
.addbox button,.mini{background:var(--accent);color:#fff;border:0;border-radius:10px;padding:11px 15px;
  font-weight:700;cursor:pointer;font-size:14px}
.assignrow{display:flex;gap:6px;margin-top:8px;align-items:center;font-size:12px;color:var(--muted)}
.assignrow input{flex:1;background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:6px 9px;font-size:12.5px;min-width:0}
footer{margin-top:22px;color:var(--muted);font-size:11.5px;text-align:center}
.live{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--good);margin-right:5px;animation:blink 2s infinite}
@keyframes blink{50%{opacity:.35}}
</style></head><body>
<div class="wrap">
  <header>
    <div class="brand"><div class="logo">Z</div>
      <div><h1>ZYNTH Command Center</h1><div class="sub" id="gen"><span class="live"></span>live</div></div>
    </div>
    <div class="pills" id="pills"></div>
  </header>
  <div id="banner"></div>
  <div class="kpis" id="kpis"></div>
  <div class="graphwrap"><canvas id="graph"></canvas><div class="hint">tap a department node to open it</div></div>
  <div class="section-title">Departments</div>
  <div class="deptgrid" id="depts"></div>
  <div class="section-title">Recent activity</div>
  <div class="feed" id="activity"></div>
  <footer>ZYNTH · The Intelligence of Creativity · auto-refreshing</footer>
</div>
<div class="scrim" id="scrim" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer"><button class="close" onclick="closeDrawer()">✕</button><div class="drawer-in" id="drawerIn"></div></div>

<script>
let STATE = __STATE__;
let CURRENT = null;
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const toneVar={good:'var(--good)',bad:'var(--bad)',warn:'var(--warn)',muted:'var(--muted)'};

function render(){
  const t=STATE.totals, sys=STATE.sys;
  $('#gen').innerHTML='<span class="live"></span>'+esc(STATE.generated);
  $('#pills').innerHTML=[['AI brain',sys.ai],['Voice',sys.voice],['Email',sys.email]]
    .map(([n,ok])=>`<span class="pill ${ok?'good':'warn'}">${ok?'●':'○'} ${n}</span>`).join('');
  $('#banner').innerHTML = STATE.audit_done? '' :
    '<div class="banner">🩺 <b>Week 0 Audit not done.</b> Send <b>/audit</b> in Telegram to set your starting line & activate the scorecard.</div>';
  const kpi=[['Prospects',(t.prospects||0)+(t.prospects_hot?' · '+t.prospects_hot+'★':''),''],
    ['Open leads',t.leads,''],['Pipeline','S$'+t.open_value.toLocaleString(),''],
    ['Open tasks',t.tasks_open,''],['Proposals',t.proposals,''],
    ['Suppliers',t.suppliers,''],['Scorecard reds',t.reds,t.reds?'bad':'']];
  $('#kpis').innerHTML=kpi.map(([l,v,tone])=>`<div class="kpi"><b style="color:${tone==='bad'?'var(--bad)':'inherit'}">${v}</b><span>${l}</span></div>`).join('');
  $('#depts').innerHTML=STATE.departments.map(d=>{
    const c=d.tasks.counts;
    return `<div class="dept" style="border-left:3px solid ${d.color}" onclick="openDept('${d.name}')">
      <div class="dept-top"><span class="dept-dot" style="background:${d.color}"></span><h3>${d.icon} ${esc(d.label)}</h3></div>
      <div class="data">${esc(d.data)}</div>
      <div class="tbar">
        <div class="tcount"><b>${c.todo}</b><span>todo</span></div>
        <div class="tcount"><b>${c.doing}</b><span>doing</span></div>
        <div class="tcount"><b>${c.done}</b><span>done</span></div>
      </div></div>`;
  }).join('');
  $('#activity').innerHTML = (STATE.activity.length?STATE.activity:[{text:'No activity yet — it appears as you use the bot',department:'Operations',at:''}])
    .slice(0,20).map(a=>{const col=(STATE.departments.find(d=>d.name===a.department)||{}).color||'var(--muted)';
      return `<div class="ev"><span class="evd" style="background:${col}"></span><div>${esc(a.text)}<br><small>${esc(a.department)} · ${esc(a.at)}</small></div></div>`;}).join('');
}

/* ---- neural graph ---- */
const cv=$('#graph'), cx=cv.getContext('2d');
let nodes=[], t0=performance.now(), DPR=Math.min(2,window.devicePixelRatio||1);
function layout(){
  const w=cv.clientWidth,h=cv.clientHeight;cv.width=w*DPR;cv.height=h*DPR;cx.setTransform(DPR,0,0,DPR,0,0);
  const cxp=w/2,cyp=h/2,R=Math.min(w,h)*0.36;
  nodes=STATE.departments.map((d,i)=>{
    const a=-Math.PI/2 + i*2*Math.PI/STATE.departments.length;
    return {...d, x:cxp+Math.cos(a)*R, y:cyp+Math.sin(a)*R, r:12+Math.min(10,d.load*1.4), a};
  });
  nodes.center={x:cxp,y:cyp};
}
function draw(t){
  const w=cv.clientWidth,h=cv.clientHeight;cx.clearRect(0,0,w,h);
  const C=nodes.center; const pulse=(Math.sin(t/700)+1)/2;
  // links
  nodes.forEach(n=>{
    const grad=cx.createLinearGradient(C.x,C.y,n.x,n.y);
    grad.addColorStop(0,'rgba(120,120,160,0.05)');grad.addColorStop(1,n.color+'55');
    cx.strokeStyle=grad;cx.lineWidth=1+ n.load*0.12;cx.beginPath();cx.moveTo(C.x,C.y);cx.lineTo(n.x,n.y);cx.stroke();
    // travelling pulse
    const p=((t/2200)+(n.a))%1; const px=C.x+(n.x-C.x)*p, py=C.y+(n.y-C.y)*p;
    cx.fillStyle=n.color;cx.globalAlpha=.7;cx.beginPath();cx.arc(px,py,2,0,7);cx.fill();cx.globalAlpha=1;
  });
  // center
  cx.fillStyle='rgba(140,140,180,'+(0.10+pulse*0.06)+')';cx.beginPath();cx.arc(C.x,C.y,26+pulse*4,0,7);cx.fill();
  cx.fillStyle=getComputedStyle(document.body).getPropertyValue('--accent');
  cx.beginPath();cx.arc(C.x,C.y,13,0,7);cx.fill();
  cx.fillStyle='#fff';cx.font='700 12px system-ui';cx.textAlign='center';cx.textBaseline='middle';cx.fillText('Z',C.x,C.y);
  // dept nodes
  nodes.forEach(n=>{
    cx.fillStyle=n.color+'22';cx.beginPath();cx.arc(n.x,n.y,n.r+6,0,7);cx.fill();
    cx.fillStyle=n.color;cx.beginPath();cx.arc(n.x,n.y,n.r,0,7);cx.fill();
    cx.fillStyle='#fff';cx.font='600 12px system-ui';cx.fillText(n.icon,n.x,n.y);
    cx.fillStyle=getComputedStyle(document.body).getPropertyValue('--muted');
    cx.font='600 10px system-ui';cx.fillText(n.label,n.x,n.y+n.r+12);
    const open=n.tasks.counts.todo+n.tasks.counts.doing;
    if(open){cx.fillStyle=n.color;cx.beginPath();cx.arc(n.x+n.r*0.8,n.y-n.r*0.8,7,0,7);cx.fill();
      cx.fillStyle='#fff';cx.font='700 9px system-ui';cx.fillText(open,n.x+n.r*0.8,n.y-n.r*0.8);}
  });
  requestAnimationFrame(draw);
}
cv.addEventListener('click',e=>{
  const rect=cv.getBoundingClientRect();const mx=e.clientX-rect.left,my=e.clientY-rect.top;
  for(const n of nodes){if(Math.hypot(mx-n.x,my-n.y)<n.r+8){openDept(n.name);return;}}
});

/* ---- drawer ---- */
function openDept(name){
  CURRENT=name;const d=STATE.departments.find(x=>x.name===name);if(!d)return;
  const items=d.tasks.items.slice().reverse();
  const taskHtml=items.length?items.map(tk=>`
    <div class="task ${tk.status}">
      <div class="row"><span class="ttl">${esc(tk.title)} <small>[${tk.id}]</small></span></div>
      <div class="row" style="margin-top:7px">
        ${['todo','doing','done'].map(s=>`<button class="chipbtn ${tk.status===s?'active':''}" style="${tk.status===s?'background:'+d.color:''}" onclick="move('${tk.id}','${s}')">${s}</button>`).join('')}
      </div>
      <div class="assignrow"><span>👤</span><input id="as_${tk.id}" placeholder="assignee" value="${esc(tk.assignee||'')}"><button class="chipbtn" onclick="assign('${tk.id}')">save</button></div>
    </div>`).join(''):'<p style="color:var(--muted);font-size:13px">No tasks yet. Add the first below.</p>';
  const actHtml=(d.activity||[]).map(a=>`<div class="ev"><span class="evd" style="background:${d.color}"></span><div>${esc(a.text)}<br><small>${esc(a.at)}</small></div></div>`).join('')||'<small style="color:var(--muted)">No recent activity</small>';
  $('#drawerIn').innerHTML=`
    <h2><span class="dept-dot" style="background:${d.color}"></span>${d.icon} ${esc(d.label)}</h2>
    <div class="sub" style="margin-bottom:10px">${esc(d.data)}</div>
    <div class="addbox"><input id="newtask" placeholder="Add a task for ${esc(d.label)}…" onkeydown="if(event.key==='Enter')addTask()"><button onclick="addTask()">Add</button></div>
    <div class="section-title" style="margin:16px 4px 6px">Tasks</div>${taskHtml}
    <div class="section-title" style="margin:18px 4px 6px">Activity</div><div class="feed">${actHtml}</div>`;
  $('#scrim').classList.add('on');$('#drawer').classList.add('on');
}
function closeDrawer(){$('#scrim').classList.remove('on');$('#drawer').classList.remove('on');}
async function api(path,body){
  try{const r=await fetch(path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});return await r.json();}
  catch(e){return {ok:false,error:String(e)};}
}
async function addTask(){const el=$('#newtask');const v=(el.value||'').trim();if(!v)return;el.value='';
  await api('/api/task',{action:'add',title:v,department:CURRENT});await refresh();openDept(CURRENT);}
async function move(id,s){await api('/api/task',{action:'status',id,status:s});await refresh();openDept(CURRENT);}
async function assign(id){const v=($('#as_'+id).value||'').trim();await api('/api/task',{action:'assign',id,assignee:v});await refresh();openDept(CURRENT);}
async function refresh(){const s=await api('/api/state');if(s&&s.departments){STATE=s;render();layout();}}
window.addEventListener('resize',layout);
render();layout();requestAnimationFrame(draw);
setInterval(refresh,15000);
</script></body></html>"""
