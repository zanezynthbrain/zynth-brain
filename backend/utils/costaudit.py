"""Cost audit + telemetry — 'stop burning cash in the air'.

Two jobs:
  1. Make every scheduled job accountable: a registry with purpose + NAMED
     CONSUMER + cadence. The standing rule (Phase 7) is: nothing runs on a
     schedule unless its output has a named consumer. Anything here without a
     real consumer is a candidate for removal.
  2. Surface spend: read the daily cost-tracker files and report cost this
     week + the metric that matters — cost per APPROVED artifact, not per call.

Retroactive Critic scoring of past artifacts costs API credit and needs the
brain online, so it is opt-in (audit_text(retro=True) / `/costaudit deep`).
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

# ── The accountable schedule: every job needs a NAMED CONSUMER ────────────────
SCHEDULED_JOBS = [
    {"id": "market_research", "cadence": "daily 06:30", "purpose": "grow prospect DB",
     "consumer": "MD (/prospects), BD Sheet", "keep": True},
    {"id": "bd_autopilot", "cadence": "daily 07:00", "purpose": "enrich + draft outreach",
     "consumer": "MD (/queue) — outreach pipeline", "keep": True},
    {"id": "fx_refresh", "cadence": "daily 07:00", "purpose": "market FX rates",
     "consumer": "every proposal/pricing prompt", "keep": True},
    {"id": "morning_brief", "cadence": "daily 08:00", "purpose": "CEO day plan",
     "consumer": "MD (Telegram)", "keep": True},
    {"id": "daily_proposals", "cadence": "daily 09:00", "purpose": "grow proposal library",
     "consumer": "proposal pool — REVIEW: does MD read these?", "keep": None},
    {"id": "outreach_sender", "cadence": "hourly 09-18", "purpose": "send released outreach",
     "consumer": "prospects (external) — MD-gated", "keep": True},
    {"id": "eod_report", "cadence": "daily 18:00", "purpose": "end-of-day summary",
     "consumer": "MD (Telegram)", "keep": True},
    {"id": "nightly_consolidation", "cadence": "daily 21:00", "purpose": "gap digest",
     "consumer": "MD (Telegram/email)", "keep": True},
    {"id": "weekly_bridge_export", "cadence": "Mon 08:00", "purpose": "lead DB → Drive",
     "consumer": "MD / consultant (bridge/)", "keep": True},
    {"id": "monday_priorities", "cadence": "Mon 08:45", "purpose": "weekly cadence",
     "consumer": "MD (Telegram)", "keep": True},
    {"id": "friday_review", "cadence": "Fri 15:30", "purpose": "weekly review",
     "consumer": "MD (Telegram)", "keep": True},
    {"id": "self_improve", "cadence": "Sun 20:00", "purpose": "learn from own mistakes → lessons",
     "consumer": "every agent (knowledge inject) + MD", "keep": True},
]


def _cost_dir() -> Path:
    return Path("outputs/cost_tracker")


def _spend_last_days(days: int = 7) -> tuple[float, int]:
    """Return (total SGD, total calls) over the last N daily cost files."""
    total_sgd = 0.0
    calls = 0
    today = datetime.now()
    for i in range(days):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        f = _cost_dir() / f"{d}.json"
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                total_sgd += float(data.get("sgd", 0) or 0)
                calls += int(data.get("calls", 0) or 0)
            except Exception:
                continue
    return round(total_sgd, 2), calls


def _approved_artifacts() -> int:
    """Count approved proposals (job files with a passing QC verdict)."""
    n = 0
    jobs = Path("outputs/jobs")
    if jobs.is_dir():
        for f in jobs.glob("*.json"):
            try:
                job = json.loads(f.read_text(encoding="utf-8"))
                if any(q.get("verdict") == "pass" for q in job.get("qc_scores", [])):
                    n += 1
            except Exception:
                continue
    return n


def jobs_table() -> str:
    lines = ["<b>Scheduled jobs — named-consumer audit</b>"]
    for j in SCHEDULED_JOBS:
        mark = "✅" if j["keep"] is True else ("⚠️ REVIEW" if j["keep"] is None else "❌")
        lines.append(f"{mark} <code>{j['id']}</code> ({j['cadence']}) — {j['purpose']} → {j['consumer']}")
    return "\n".join(lines)


def audit_text(retro: bool = False) -> str:
    sgd7, calls7 = _spend_last_days(7)
    approved = _approved_artifacts()
    per = f"S${sgd7/approved:.2f}" if approved else "n/a (0 approved yet)"
    review = [j["id"] for j in SCHEDULED_JOBS if j["keep"] is None]
    out = [
        "💸 <b>Cost Audit</b>",
        f"Spend last 7 days: <b>S${sgd7:.2f}</b> over {calls7} calls",
        f"Approved artifacts: {approved} · <b>cost per approved artifact: {per}</b>",
        "",
        jobs_table(),
    ]
    if review:
        out += ["", f"⚠️ <b>Review these</b> (no confirmed consumer): {', '.join(review)} — "
                "keep only if you actually open the output; kill the rest (Phase 7 rule)."]
    out += ["", "<i>Deep retro-scoring of past artifacts costs credit — run "
            "<code>/costaudit deep</code> when the brain is online.</i>"]
    return "\n".join(out)
