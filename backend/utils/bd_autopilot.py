"""BD Autopilot — the closed-loop engine that runs BD without you in each step.

Daily flow (all autonomous; you supervise on Telegram):
  research a sector → enrich the top new prospects with REAL contacts (Apollo)
  → draft + queue personalised outreach → notify you. A separate sender job
  releases/sends what's due (1-tap or auto-release). You are ON the loop:
  /bd pause · /bd resume · /queue · /release · /reject at any time.

Switches (Railway → Variables):
  BD_AUTOPILOT_ENABLED = true         turn the loop on (default off = safe)
  APOLLO_API_KEY       = ...          real contacts (else contacts stay blank)
  OUTREACH_* (see utils/outreach)     send cadence + daily cap

Pause state persists to outputs/proposal_pool/bd_state.json so it survives
restarts and is visible to every part of the system.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from utils.logging_config import get_logger

logger = get_logger("bd_autopilot")

_POOL = Path("outputs/proposal_pool")
_STATE = _POOL / "bd_state.json"

# How many of the day's new prospects to enrich + draft outreach for per run.
# Small on purpose — quality over spray, and it protects the domain reputation.
ENRICH_PER_RUN = 8


def is_enabled() -> bool:
    return os.getenv("BD_AUTOPILOT_ENABLED", "").lower() in ("1", "true", "yes", "on")


def _read() -> dict:
    if _STATE.exists():
        try:
            return json.loads(_STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write(d: dict) -> None:
    _POOL.mkdir(parents=True, exist_ok=True)
    _STATE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def is_paused() -> bool:
    return bool(_read().get("paused"))


def pause() -> None:
    d = _read(); d["paused"] = True; _write(d)


def resume() -> None:
    d = _read(); d["paused"] = False; _write(d)


async def enrich_and_queue(prospects: list[dict]) -> dict:
    """For each prospect: pull a real contact via Apollo, persist it, and if we
    got a real email, draft + queue an outreach. Returns counts. Never fabricates."""
    from utils import apollo_enrich, outreach
    from utils.prospects import update_fields

    enriched = queued = 0
    have_apollo = apollo_enrich.is_configured()

    for p in prospects[:ENRICH_PER_RUN]:
        if have_apollo and not (p.get("email") or "").strip():
            try:
                if await apollo_enrich.enrich_prospect(p):
                    update_fields(p.get("id", ""), {
                        "contact_name": p.get("contact_name", ""),
                        "contact_title": p.get("contact_title", ""),
                        "email": p.get("email", ""),
                        "phone": p.get("phone", ""),
                        "linkedin": p.get("linkedin", ""),
                        "apollo_enriched": True,
                    })
                    enriched += 1
            except Exception as exc:
                logger.info("enrich failed for %s: %s", p.get("company"), type(exc).__name__)

        if (p.get("email") or "").strip():
            try:
                if outreach.enqueue(p):
                    queued += 1
            except Exception as exc:
                logger.info("enqueue failed for %s: %s", p.get("company"), type(exc).__name__)

    return {"enriched": enriched, "queued": queued, "apollo": have_apollo}
