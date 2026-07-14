"""Business operating state — the playbook's rhythm, carried by the bot.

Stores the Week 0 audit answers and the 12-metric master scorecard in
outputs/proposal_pool/business_state.json (committed back to the repo by
the daily pool workflow, so it survives Railway redeploys).

This is the layer that turns the bot from a content generator into an
operating system: /audit, /scorecard, and the weekly rhythm nudges all
read and write here.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_PATH = Path("outputs/proposal_pool/business_state.json")

# The Agency Master Scorecard (from docs/playbook/03_KPI_System.md).
# direction: "up" = higher is better, "down" = lower is better,
# "band" = stay inside [red_low, red_high]. Values are MD-entered.
SCORECARD = [
    {"key": "mrr", "label": "Monthly Recurring Revenue (SGD)", "unit": "S$", "direction": "up", "target": "+8-12% MoM", "red_below": None},
    {"key": "revenue", "label": "Total Revenue vs plan (%)", "unit": "%", "direction": "up", "target": "≥100% of plan", "red_below": 85},
    {"key": "gross_margin", "label": "Gross Margin (%)", "unit": "%", "direction": "up", "target": ">50%", "red_below": 40},
    {"key": "net_profit", "label": "Net Profit (%)", "unit": "%", "direction": "up", "target": "15-25%", "red_below": 10},
    {"key": "utilization", "label": "Utilization (%)", "unit": "%", "direction": "band", "target": "65-75%", "red_low": 55, "red_high": 85},
    {"key": "pipeline_cov", "label": "Pipeline Coverage (x quarterly target)", "unit": "x", "direction": "up", "target": ">3x", "red_below": 2},
    {"key": "retention", "label": "Client Retention (%)", "unit": "%", "direction": "up", "target": ">85%", "red_below": 75},
    {"key": "nps", "label": "NPS", "unit": "", "direction": "up", "target": ">50", "red_below": 30},
    {"key": "rev_per_head", "label": "Revenue per Head (SGD/yr, k)", "unit": "k", "direction": "up", "target": ">100k", "red_below": 70},
    {"key": "runway", "label": "Cash Runway (months)", "unit": "mo", "direction": "up", "target": ">3 months", "red_below": 1.5},
    {"key": "concentration", "label": "Top-client Concentration (%)", "unit": "%", "direction": "down", "target": "<25%", "red_above": 35},
    {"key": "on_time", "label": "On-Time Delivery (%)", "unit": "%", "direction": "up", "target": ">92%", "red_below": 85},
]

AUDIT_QUESTIONS = [
    "FINANCE — last 3 projects' gross margin %? cash in bank? monthly burn? runway (months)?",
    "FINANCE — which invoices are overdue and total amount? What % of revenue is your single biggest client?",
    "CLIENTS — how many clients on retainer vs project? Any client you'd secretly like to fire? Last referral received?",
    "OPERATIONS — how many SOPs are written? How long could the agency run without you? Hours/week you personally do client work?",
    "PIPELINE — how many deals in the pipeline right now? New leads added in the last 30 days?",
]


def _load() -> dict[str, Any]:
    try:
        if _PATH.exists():
            return json.loads(_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"audit": {}, "scorecard": {}, "updated": None}


def _save(state: dict[str, Any]) -> None:
    state["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Audit ─────────────────────────────────────────────────────────────────────

def save_audit(answers: dict[str, Any]) -> None:
    state = _load()
    state["audit"] = {"answers": answers, "completed_at": datetime.now().strftime("%Y-%m-%d")}
    _save(state)


def get_audit() -> dict[str, Any]:
    return _load().get("audit", {})


# ── Scorecard ─────────────────────────────────────────────────────────────────

def set_metric(key: str, value: float) -> dict | None:
    spec = next((m for m in SCORECARD if m["key"] == key), None)
    if not spec:
        return None
    state = _load()
    state.setdefault("scorecard", {})[key] = {
        "value": value,
        "at": datetime.now().strftime("%Y-%m-%d"),
    }
    _save(state)
    return spec


def _status(spec: dict, value: float) -> str:
    d = spec["direction"]
    if d == "band":
        if value < spec["red_low"] or value > spec["red_high"]:
            return "🔴"
        return "🟢"
    if d == "up":
        rb = spec.get("red_below")
        if rb is not None and value < rb:
            return "🔴"
        return "🟢"
    if d == "down":
        ra = spec.get("red_above")
        if ra is not None and value > ra:
            return "🔴"
        return "🟢"
    return "⚪"


def scorecard_view() -> str:
    state = _load()
    scores = state.get("scorecard", {})
    lines = ["📊 <b>ZYNTH Master Scorecard</b>\n"]
    reds = 0
    for spec in SCORECARD:
        entry = scores.get(spec["key"])
        if entry is None:
            lines.append(f"⚪ <b>{spec['label']}</b> — not set · target {spec['target']}")
            continue
        st = _status(spec, entry["value"])
        if st == "🔴":
            reds += 1
        lines.append(
            f"{st} <b>{spec['label']}</b> — {spec['unit']}{entry['value']:g} "
            f"· target {spec['target']}"
        )
    lines.append(f"\nUpdate: <code>/scorecard set gross_margin 48</code>")
    lines.append(f"Keys: {', '.join(m['key'] for m in SCORECARD)}")
    if reds:
        lines.insert(1, f"🚨 <b>{reds} metric(s) in the red — address these first.</b>\n")
    return "\n".join(lines)
