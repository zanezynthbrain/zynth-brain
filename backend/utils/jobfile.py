"""Job file — one JSON object per brief that travels the agent chain.

Each agent reads the job file, appends its section, and passes it on. Input-
contract gates read it to check that upstream sections exist before starting;
a missing dependency becomes a blocking question the MD sees. The Critic writes
qc_scores. Persisted to outputs/jobs/ (pool pattern — survives redeploys).

Schema (sections filled as the chain runs):
  id, created_at, brief, market, budget, constraints,
  research, concept, design, ops, pricing,
  qc_scores[], status, history[], blocking_questions[]
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

_DIR = Path("outputs/jobs")
_FMT = "%Y-%m-%d %H:%M"

SECTIONS = ("research", "concept", "design", "ops", "pricing")
STATUSES = ("open", "in_progress", "qc", "approved", "blocked", "rejected")


def _path(job_id: str) -> Path:
    return _DIR / f"{job_id}.json"


def create(brief: str, market: str = "", budget: str = "", constraints: str = "") -> dict:
    _DIR.mkdir(parents=True, exist_ok=True)
    job = {
        "id": f"J{uuid.uuid4().hex[:8]}",
        "created_at": datetime.now().strftime(_FMT),
        "brief": brief,
        "market": market,
        "budget": budget,
        "constraints": constraints,
        "research": None, "concept": None, "design": None, "ops": None, "pricing": None,
        "qc_scores": [],
        "status": "open",
        "history": [{"at": datetime.now().strftime(_FMT), "event": "created"}],
        "blocking_questions": [],
    }
    _save(job)
    return job


def _save(job: dict) -> None:
    _DIR.mkdir(parents=True, exist_ok=True)
    _path(job["id"]).write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")


def get(job_id: str) -> dict | None:
    p = _path(job_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def append_section(job_id: str, section: str, data: Any) -> dict | None:
    """Write an agent's section into the job file."""
    job = get(job_id)
    if not job or section not in SECTIONS:
        return None
    job[section] = data
    job["history"].append({"at": datetime.now().strftime(_FMT), "event": f"section:{section}"})
    if job["status"] == "open":
        job["status"] = "in_progress"
    _save(job)
    return job


def has_sections(job_id: str, required: list[str]) -> tuple[bool, list[str]]:
    """Input-contract check: are all required upstream sections present?
    Returns (ok, missing[])."""
    job = get(job_id)
    if not job:
        return False, required
    missing = [s for s in required if not job.get(s)]
    return (not missing), missing


def add_blocking_question(job_id: str, agent: str, question: str) -> dict | None:
    """An agent that can't proceed on thin input records a blocking question."""
    job = get(job_id)
    if not job:
        return None
    job["blocking_questions"].append(
        {"at": datetime.now().strftime(_FMT), "agent": agent, "question": question}
    )
    job["status"] = "blocked"
    job["history"].append({"at": datetime.now().strftime(_FMT), "event": f"blocked:{agent}"})
    _save(job)
    return job


def record_qc(job_id: str, score: float, verdict: str, reasons: list[str]) -> dict | None:
    job = get(job_id)
    if not job:
        return None
    job["qc_scores"].append({
        "at": datetime.now().strftime(_FMT),
        "score": score, "verdict": verdict, "reasons": reasons,
    })
    job["status"] = "approved" if verdict == "pass" else "qc"
    _save(job)
    return job


def set_status(job_id: str, status: str) -> dict | None:
    job = get(job_id)
    if not job or status not in STATUSES:
        return None
    job["status"] = status
    job["history"].append({"at": datetime.now().strftime(_FMT), "event": f"status:{status}"})
    _save(job)
    return job
