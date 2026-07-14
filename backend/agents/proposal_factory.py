"""Proposal Factory Agent — generates Event & Campaign proposals at scale.

Produces 4-5 distinct proposals per (industry × month × market) combination
and persists them to the local proposal pool (utils/proposal_pool.py).

Supported call patterns:
  agent.generate_batch(industry, month, market, memory, pool)  ← one combo
  agent.run_month_sweep(month, market, memory, pool)           ← all industries × one month

Industries rotate through ALL sectors in Myanmar and Singapore so the pool
becomes a comprehensive library of ready-to-pitch proposals over time.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from agents.base import BaseAgent
from utils.proposal_pool import ProposalPool
from utils.state import SharedMemory

# ── Industry lists ────────────────────────────────────────────────────────────

INDUSTRIES_MM = [
    "Banking & Finance",
    "Real Estate & Property",
    "F&B & Restaurant",
    "Retail & Fashion",
    "Healthcare & Wellness",
    "Education & Training",
    "Manufacturing & Industrial",
    "Tourism & Hospitality",
    "Technology & Startup",
    "Beauty & Personal Care",
    "Media & Entertainment",
    "Automotive",
    "Logistics & Trade",
    "NGO & Non-profit",
    "Government & Public Sector",
]

INDUSTRIES_SG = [
    "Banking & Fintech",
    "Real Estate & PropTech",
    "F&B & Restaurant",
    "Retail & E-commerce",
    "Healthcare & MedTech",
    "Education & EdTech",
    "Manufacturing & Industry 4.0",
    "Tourism & MICE",
    "Technology & SaaS",
    "Beauty & Wellness",
    "Media & Content",
    "Automotive & Mobility",
    "Logistics & Supply Chain",
    "Government & Public Sector",
    "Finance & Wealth Management",
]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

SEASONAL_CONTEXT: dict[str, str] = {
    "January": "New Year momentum, Q1 goal-setting, resolution themes, fresh-start energy",
    "February": "Valentine's Day, Chinese New Year (some years), love & loyalty themes",
    "March": "International Women's Day, spring energy, Q1 close, brand storytelling",
    "April": "Thingyan Water Festival (MM), Easter, financial year-end (SG), renewal themes",
    "May": "Labour Day, Mother's Day, mid-year countdown, gratitude campaigns",
    "June": "Mid-year review, school holidays SG, digital-first, monsoon season MM",
    "July": "School holidays SG, influencer season, youth campaigns, brand refresh",
    "August": "National Day SG, independence & heritage themes MM, local pride campaigns",
    "September": "Back-to-school, mid-autumn festival, Q3 closing push, B2B focus",
    "October": "Diwali, Halloween, year-end pipeline, Thadingyut MM, festive planning",
    "November": "Year-end push, Black Friday, pre-Christmas, corporate events season",
    "December": "Christmas, year-end celebration, new year countdown, client appreciation",
}

# ── Output schema ─────────────────────────────────────────────────────────────

_BATCH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["proposals"],
    "properties": {
        "proposals": {
            "type": "array",
            "minItems": 3,
            "maxItems": 5,
            "items": {
                "type": "object",
                "required": [
                    "title", "type", "objective", "target_audience",
                    "key_activities", "budget_range", "timeline_weeks",
                    "kpis", "zynth_services", "why_now", "deliverables",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "type": {
                        "type": "string",
                        "description": (
                            "Proposal category: Seasonal Campaign, Product Launch Event, "
                            "Corporate Conference, Awards Ceremony, Brand Activation, "
                            "Digital Campaign, Influencer Campaign, CSR Campaign, "
                            "Trade Show / Exhibition, Rebranding Campaign, "
                            "Lead Generation Campaign, Anniversary Campaign"
                        ),
                    },
                    "objective": {"type": "string"},
                    "target_audience": {"type": "string"},
                    "key_activities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                    },
                    "budget_range": {
                        "type": "object",
                        "required": ["min", "max", "currency"],
                        "properties": {
                            "min": {"type": "number"},
                            "max": {"type": "number"},
                            "currency": {"type": "string"},
                        },
                    },
                    "timeline_weeks": {"type": "integer"},
                    "kpis": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                    },
                    "zynth_services": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "ZYNTH services used: Social Media Management, Content Creation, "
                            "Paid Ads, Event Management, Branding, PR & Media, "
                            "Influencer Marketing, SEO, Email Marketing, Photography & Video"
                        ),
                    },
                    "why_now": {"type": "string"},
                    "deliverables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                    },
                    "estimated_value_sgd": {
                        "type": "number",
                        "description": "Estimated project value in SGD (use 1 SGD ≈ 3600 MMK for MM proposals)",
                    },
                },
            },
        }
    },
}


# ── Agent ─────────────────────────────────────────────────────────────────────

class ProposalFactoryAgent(BaseAgent):
    """Proposal Factory — generates Event & Campaign proposals for the data pool."""

    agent_key = "proposal_factory"
    display_name = "Proposal Factory"
    role_description = (
        "You are ZYNTH's senior strategist and proposal writer. You create compelling, "
        "commercially realistic Event and Marketing Campaign proposals for businesses across "
        "industries in Myanmar and Singapore. Each proposal showcases ZYNTH's services "
        "(social media, content creation, paid ads, event management, branding, PR, "
        "influencer marketing, SEO) and is designed to win the client's business. "
        "Your proposals are specific, seasonal, and actionable — not generic templates."
    )
    output_schema: dict[str, Any] = _BATCH_SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        industry = kwargs.get("industry", INDUSTRIES_MM[0])
        month = kwargs.get("month", datetime.now().strftime("%B"))
        market = kwargs.get("market", "MM")
        return self._build_prompt(industry, month, market)

    @staticmethod
    def _build_prompt(industry: str, month: str, market: str) -> str:
        market_name = "Myanmar" if market.upper() == "MM" else "Singapore"
        currency = "MMK" if market.upper() == "MM" else "SGD"
        seasonal = SEASONAL_CONTEXT.get(month, "")
        return (
            f"Generate 4-5 DISTINCT Event & Marketing Campaign proposals for the "
            f"<b>{industry}</b> industry in <b>{market_name}</b> for <b>{month}</b>.\n\n"
            f"Seasonal context: {seasonal}\n\n"
            f"Rules:\n"
            f"- Each proposal must be a DIFFERENT type (one seasonal campaign, one event, "
            f"  one activation, one digital campaign, etc.)\n"
            f"- Budget in {currency} — realistic for {market_name} SMEs and mid-market brands\n"
            f"- KPIs must be measurable (e.g. '500 new followers', '20 qualified leads', "
            f"  '300 event attendees', '15% CTR')\n"
            f"- Deliverables must be concrete ('8 social posts', '3 influencer videos', "
            f"  'venue for 150 pax', '1 brand film')\n"
            f"- why_now must tie directly to the {month} seasonal moment\n"
            f"- ZYNTH services: list the specific services this proposal sells\n"
            f"- estimated_value_sgd: realistic project value a client would pay ZYNTH\n"
            f"- Make every proposal commercially attractive — a real client should WANT to buy it"
        )

    # ── Parameterized generation (main entry point) ───────────────────────────

    async def generate_batch(
        self,
        industry: str,
        month: str,
        market: str,
        memory: SharedMemory,
        pool: ProposalPool | None = None,
    ) -> list[dict[str, Any]]:
        """Generate proposals for one industry × month × market combo.

        Writes to pool if provided. Returns the list of proposal dicts.
        """
        system = self.build_system_prompt()
        prompt = self._build_prompt(industry, month, market)
        # Idea drafts are high-volume — route to the cheap fallback model.
        # The client-grade document comes from MasterProposalAgent instead.
        # 4-5 full proposals need generous max_tokens or the JSON truncates
        # mid-string (seen in proposal-pool run #6).
        from config import get_settings
        data, response = await self.llm.complete_json(
            system=system, user_prompt=prompt, schema=_BATCH_SCHEMA,
            model=get_settings().fallback_model_name,
            max_tokens=8000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)

        proposals = data.get("proposals", [])
        if pool and proposals:
            pool.add_batch(industry, month, market, proposals)

        return proposals

    async def run_month_sweep(
        self,
        month: str,
        market: str,
        memory: SharedMemory,
        pool: ProposalPool | None = None,
        max_industries: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Generate proposals for all (or first N) industries for one month.

        Useful for filling a whole month's library in one command.
        Returns {industry: [proposals]} dict.
        """
        industries = INDUSTRIES_MM if market.upper() == "MM" else INDUSTRIES_SG
        if max_industries:
            industries = industries[:max_industries]

        results: dict[str, list[dict]] = {}
        for industry in industries:
            try:
                proposals = await self.generate_batch(industry, month, market, memory, pool)
                results[industry] = proposals
            except Exception as exc:
                await memory.log(
                    self.agent_key, "batch_failed",
                    industry=industry, month=month, error=str(exc)
                )
                results[industry] = []
        return results

    def next_uncovered(
        self,
        market: str,
        pool: ProposalPool,
    ) -> tuple[str, str] | None:
        """Return the next (industry, month) not yet in the pool for this market.

        Cycles industries faster than months so each month builds up across
        all industries before moving to the next month.
        """
        covered = {(ind, mo) for ind, mo, mk in pool.covered_combos() if mk.upper() == market.upper()}
        industries = INDUSTRIES_MM if market.upper() == "MM" else INDUSTRIES_SG
        current_month = datetime.now().strftime("%B")
        # prioritise current month first, then rotate through all months
        ordered_months = [current_month] + [m for m in MONTHS if m != current_month]
        for month in ordered_months:
            for industry in industries:
                if (industry, month) not in covered:
                    return industry, month
        return None
