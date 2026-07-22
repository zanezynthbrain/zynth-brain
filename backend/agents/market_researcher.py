"""Myanmar Market Researcher agent — finds potential business clients.

Given a target sector, it produces a batch of REAL, currently-operating
Myanmar businesses that fit ZYNTH (marketing/events), each fit-scored with a
reason — the raw material of BD. It uses best-effort live web research for
current signals and is told which companies already exist so it doesn't repeat.

Hard rules (match the rest of ZYNTH):
  * Only real, plausible, currently-operating Myanmar businesses.
  * NEVER fabricate a phone/email. Leave unknown contacts blank; a website or
    Facebook page is fine if it's genuinely known.
  * Quality over volume — a fit-scored, non-duplicate target beats noise.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory

_PROSPECT_ITEM = {
    "type": "object",
    "required": ["company", "industry", "why_fit", "fit_score", "service_fit"],
    "properties": {
        "company": {"type": "string", "description": "Real Myanmar business name"},
        "industry": {"type": "string"},
        "sub_sector": {"type": "string"},
        "location": {"type": "string", "description": "e.g. Yangon, Mandalay, Nay Pyi Taw, Nationwide"},
        "size": {"type": "string", "description": "SME / Enterprise / Large enterprise"},
        "why_fit": {"type": "string", "description": "One line: why they need ZYNTH (marketing/event budget, brand ambition, launch cadence)"},
        "fit_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "service_fit": {"type": "string", "description": "Which ZYNTH service fits: events / brand video / social / campaigns / activations"},
        # Deep BD intelligence — the analytical fields (inference is fine here).
        "company_analysis": {"type": "string", "description": "2-3 sentences: what the company is, its brand posture and marketing budget/behaviour"},
        "online_activities": {"type": "string", "description": "Their known digital/social presence: Facebook, app campaigns, content, influencer/creator work"},
        "onground_activities": {"type": "string", "description": "Their known on-ground work: events, sponsorships, activations, roadshows, store openings"},
        "marketing_gap": {"type": "string", "description": "The gap/opportunity ZYNTH can exploit — where their current marketing is weak"},
        "zynth_approach": {"type": "string", "description": "Concrete play: how ZYNTH should pitch them (which concept/service, angle, proof point)"},
        "target_role": {"type": "string", "description": "The decision-maker ROLE(S) to reach (e.g. Head of Marketing, Brand Manager) — a role, never an invented person"},
        # Contact fields: leave BLANK unless genuinely, publicly known. Never fabricate.
        "website": {"type": "string"},
        "facebook": {"type": "string"},
        "contact_name": {"type": "string", "description": "Leave blank unless publicly, verifiably known — never guess a name"},
        "contact_title": {"type": "string"},
        "email": {"type": "string", "description": "Leave blank — never invent an email"},
        "phone": {"type": "string", "description": "Leave blank — never invent a phone number"},
        "linkedin": {"type": "string", "description": "Leave blank unless a real, known profile URL"},
        "source": {"type": "string"},
    },
}

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["prospects"],
    "properties": {
        "prospects": {"type": "array", "minItems": 1, "maxItems": 40, "items": _PROSPECT_ITEM},
    },
}


class MarketResearcherAgent(BaseAgent):
    """Researches Myanmar businesses as ZYNTH client prospects."""

    agent_key = "market_researcher"
    display_name = "Myanmar Market Researcher"
    role_description = (
        "You are ZYNTH's Myanmar market research analyst. You find real, currently-"
        "operating Myanmar businesses that are strong potential CLIENTS for a marketing "
        "& events agency, and you score each for fit. You know the Myanmar business "
        "landscape: the banks, telcos, FMCG groups, retail chains, property developers, "
        "hospitals, universities, auto distributors, hotels and conglomerates. You never "
        "invent contact numbers or emails — verification is human work. You value quality "
        "over volume: every prospect is a real company with a genuine reason to need ZYNTH."
    )
    output_schema: dict[str, Any] = _SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return self._prompt(kwargs.get("sector", ""), kwargs.get("known", []), kwargs.get("count", 25), "")

    @staticmethod
    def _prompt(sector: str, known: list[str], count: int, live: str) -> str:
        known_block = ""
        if known:
            sample = ", ".join(known[:120])
            known_block = (
                "\n\nALREADY IN THE DATABASE (do NOT return any of these — find NEW ones):\n"
                f"{sample}\n"
            )
        return (
            f"Find {count} real, currently-operating Myanmar businesses in this sector "
            f"that are strong potential clients for ZYNTH (marketing & events):\n\n"
            f"SECTOR: {sector or 'any high-value sector'}\n"
            f"{live}{known_block}\n"
            "For each business give the FULL BD intelligence profile:\n"
            "- company, industry, sub_sector, location, size (SME/Enterprise/Large enterprise)\n"
            "- why_fit (one sharp line) and fit_score 1-5 (5 = big brand + high marketing/event spend)\n"
            "- service_fit (events / brand video / social / campaigns / activations)\n"
            "- company_analysis: 2-3 sentences on the company, brand posture and marketing behaviour\n"
            "- online_activities: their known digital/social presence and campaigns\n"
            "- onground_activities: their known events, sponsorships, activations, roadshows\n"
            "- marketing_gap: where their current marketing is weak = ZYNTH's opening\n"
            "- zynth_approach: a concrete play — which ZYNTH concept/service to pitch and the angle\n"
            "- target_role: the decision-maker ROLE(S) to reach (e.g. Head of Marketing, Brand Manager)\n"
            "- website / facebook ONLY if genuinely known.\n"
            "CONTACTS: leave contact_name, contact_title, email, phone, linkedin BLANK unless "
            "genuinely and publicly verifiable. NEVER invent a person, email, phone or profile — "
            "fabricated contacts are worse than none. Verification is human work.\n"
            "Prioritise businesses that actually spend on marketing or events. Real "
            "companies only — no placeholders, no duplicates of the list above."
        )

    async def research_segment(
        self, sector: str, memory: SharedMemory, known: list[str] | None = None, count: int = 25
    ) -> list[dict[str, Any]]:
        """Return a batch of prospect dicts for a sector (best-effort live research)."""
        live = ""
        try:
            from utils.webresearch import research_block
            live = await research_block(f"{sector} companies Myanmar Yangon business")
        except Exception:
            live = ""

        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=self._prompt(sector, known or [], count, live),
            schema=_SCHEMA,
            max_tokens=16000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        rows = data.get("prospects", []) if isinstance(data, dict) else []
        for r in rows:
            r.setdefault("source", f"researcher:{sector}")
        return rows
