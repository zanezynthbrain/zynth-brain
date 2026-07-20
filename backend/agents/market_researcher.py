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
        "website": {"type": "string"},
        "facebook": {"type": "string"},
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
            "For each business give: company, industry, sub_sector, location, size "
            "(SME/Enterprise/Large enterprise), why_fit (one sharp line on why they need "
            "a marketing/events agency — brand ambition, launch cadence, ad/event budget), "
            "fit_score 1-5 (5 = big brand + high marketing/event spend), service_fit "
            "(events / brand video / social / campaigns / activations), and website or "
            "facebook ONLY if genuinely known. Leave phone/email out — never invent them.\n"
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
            max_tokens=8000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        rows = data.get("prospects", []) if isinstance(data, dict) else []
        for r in rows:
            r.setdefault("source", f"researcher:{sector}")
        return rows
