"""HubSpot sync for prospects (one-way: JSON → HubSpot Companies).

Gracefully inert until configured. Set in Railway:

  HUBSPOT_TOKEN = a HubSpot Private App access token (starts with 'pat-')

Create it: HubSpot → Settings → Integrations → Private Apps → create app with
CRM 'crm.objects.companies.write/read' scopes → copy the token.

Only pushes prospects not already sent (tracked with a per-record hs_synced
flag), so re-running never duplicates. Companies are created with name +
industry + website + a note on why they fit. HubSpot de-dupes by domain when a
website is present.
"""

from __future__ import annotations

import os

import httpx

from utils.logging_config import get_logger

logger = get_logger("hubspot")

_API = "https://api.hubapi.com/crm/v3/objects/companies/batch/create"


def _token() -> str:
    return os.getenv("HUBSPOT_TOKEN", "")


def is_configured() -> bool:
    return bool(_token())


def _domain(website: str) -> str:
    w = (website or "").strip().lower()
    for p in ("https://", "http://", "www."):
        if w.startswith(p):
            w = w[len(p):]
    return w.split("/")[0].strip()


async def push_prospects(limit: int = 100) -> tuple[bool, str]:
    """Push un-synced prospects to HubSpot as Companies. Returns (ok, message)."""
    tok = _token()
    if not tok:
        return False, "not configured (set HUBSPOT_TOKEN)"

    from utils.prospects import all_prospects, seed_if_empty, mark_synced
    seed_if_empty()
    pending = [r for r in all_prospects() if not r.get("hs_synced")][:limit]
    if not pending:
        return True, "HubSpot already up to date (nothing new to push)"

    inputs = []
    for r in pending:
        props = {
            "name": r.get("company", ""),
            "industry_note": r.get("industry", ""),
            "description": f"[ZYNTH prospect · fit {r.get('fit_score', '')}/5] {r.get('why_fit', '')}".strip(),
        }
        dom = _domain(r.get("website", ""))
        if dom:
            props["domain"] = dom
        # 'industry_note' isn't a default HubSpot property; keep to safe defaults:
        props.pop("industry_note", None)
        inputs.append({"properties": props})

    try:
        async with httpx.AsyncClient(timeout=30, trust_env=True) as client:
            resp = await client.post(
                _API,
                headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                json={"inputs": inputs},
            )
        if resp.status_code >= 300:
            return False, f"hubspot {resp.status_code}: {resp.text[:160]}"
    except Exception as exc:
        logger.info("HubSpot sync failed: %s", type(exc).__name__)
        return False, f"hubspot error: {str(exc)[:160]}"

    mark_synced({r["id"] for r in pending}, field="hs_synced")
    logger.info("HubSpot sync: %d companies created", len(pending))
    return True, f"pushed {len(pending)} companies to HubSpot"
