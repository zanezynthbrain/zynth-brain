"""Apollo.io contact enrichment — the REAL data source for BD contacts.

This is the piece that makes contact-finding autonomous: given a company and a
target decision-maker role, it asks Apollo for a real person (name, title,
LinkedIn, and — if the plan unlocks it — email/phone). The AI never invents
these; Apollo returns them or the fields stay blank.

Gracefully inert until configured. Set in Railway → Variables:
  APOLLO_API_KEY = your Apollo API key (Settings → Integrations → API in Apollo)

Apollo free/basic plans return name + title + LinkedIn freely; email/phone often
come back locked ("email_not_unlocked@domain.com") until you spend a credit to
reveal. We store only genuine values and flag locked ones — never a fake email.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from utils.logging_config import get_logger

logger = get_logger("apollo")

_SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/search"

# Map a free-text target_role into Apollo person_titles filters. We keep it
# broad so we still match if the exact title differs.
_ROLE_TITLES = [
    "Chief Marketing Officer", "Head of Marketing", "Marketing Director",
    "Head of Brand", "Brand Manager", "Marketing Manager",
    "Head of Corporate Communications", "Head of Communications",
    "Head of Digital Marketing", "Events Manager", "Marketing Communications Manager",
]


def is_configured() -> bool:
    return bool(os.getenv("APOLLO_API_KEY"))


def _titles_for(role_hint: str) -> list[str]:
    """Pick sensible Apollo title filters from the researcher's target_role text."""
    hint = (role_hint or "").lower()
    picked = [t for t in _ROLE_TITLES if any(w in hint for w in t.lower().split())]
    return picked or _ROLE_TITLES[:6]


def _looks_locked(email: str) -> bool:
    e = (email or "").lower()
    return (not e) or ("not_unlocked" in e) or ("email_not" in e) or e.endswith("domain.com")


async def find_contact(company: str, role_hint: str = "") -> dict[str, str] | None:
    """Return a real decision-maker dict for a company, or None.

    Keys: contact_name, contact_title, email, phone, linkedin. Locked/placeholder
    emails from Apollo are dropped (left blank) — we never store a fake address.
    """
    key = os.getenv("APOLLO_API_KEY", "")
    if not key or not company:
        return None
    payload: dict[str, Any] = {
        "q_organization_names": [company],
        "person_titles": _titles_for(role_hint),
        "page": 1,
        "per_page": 5,
    }
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": key,
    }
    try:
        async with httpx.AsyncClient(timeout=30, headers=headers, trust_env=True) as c:
            r = await c.post(_SEARCH_URL, json=payload)
            if r.status_code >= 300:
                logger.info("apollo %s: %s", r.status_code, r.text[:120])
                return None
            people = (r.json() or {}).get("people", [])
    except Exception as exc:
        logger.info("apollo error: %s", type(exc).__name__)
        return None
    if not people:
        return None

    p = people[0]
    name = (p.get("name") or f"{p.get('first_name','')} {p.get('last_name','')}").strip()
    email = p.get("email") or ""
    if _looks_locked(email):
        email = ""  # never store a locked placeholder as if it were real
    phone = ""
    for num in (p.get("phone_numbers") or []):
        if num.get("sanitized_number") or num.get("raw_number"):
            phone = num.get("sanitized_number") or num.get("raw_number")
            break
    return {
        "contact_name": name,
        "contact_title": p.get("title") or "",
        "email": email,
        "phone": phone,
        "linkedin": p.get("linkedin_url") or "",
    }


async def enrich_prospect(prospect: dict[str, Any]) -> bool:
    """Fill a prospect's contact fields from Apollo in-place. Returns True if any
    real field was added. Never overwrites an existing value with a blank."""
    found = await find_contact(prospect.get("company", ""), prospect.get("target_role", ""))
    if not found:
        return False
    changed = False
    for k, v in found.items():
        if v and not (prospect.get(k) or "").strip():
            prospect[k] = v
            changed = True
    return changed
