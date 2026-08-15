"""Master Proposal Agent — turns a brief (or a pool idea) into a full,
client-grade proposal document.

Unlike ProposalFactoryAgent (cheap, high-volume idea drafts on the
fallback model), this agent makes ONE high-quality call on the primary
model and produces the eight master-proposal sections per the ZYNTH
document standard. The result is rendered to .docx by utils/docgen.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory

_EXEMPLAR_PATH = Path(__file__).resolve().parent.parent / "data" / "proposal_exemplar.md"
_exemplar_cache: str | None = None


def load_exemplar() -> str:
    """The IGNITE gold-standard skeleton — few-shot target for every proposal."""
    global _exemplar_cache
    if _exemplar_cache is None:
        try:
            _exemplar_cache = _EXEMPLAR_PATH.read_text(encoding="utf-8")
        except Exception:
            _exemplar_cache = ""
    return _exemplar_cache

# ZYNTH client-grade proposal structure. It is a minimum completeness standard,
# not a ceiling on creative or specialist thinking. Add relevant specialist detail
# inside the sections when a brief needs event, 3D, video, creator, sponsorship,
# regulated-sector, retail, or dual-market treatment.
SECTION_NAMES = [
    "Proposal Control Sheet & Executive Decision Summary",
    "Client Challenge, Stakes & Strategic Objective",
    "Market, Audience & Category Intelligence",
    "Human Insight, Opportunity & Competitive Opening",
    "Creative Territories Considered & Recommended Route",
    "Campaign/Event Title, Big Idea & Full Concept Explanation",
    "Audience Journey, Channel Architecture & Signature Moment",
    "Deliverables, Content, Experience & Production Specification",
    "Workstreams, Timeline, RACI & Approval Rhythm",
    "Supplier, Technology, Compliance & Operational Plan",
    "Itemised Investment, Funding Model & Scenario Logic",
    "Commercial Terms, Rights, Scope Control & Payment Plan",
    "Results, Measurement, Attribution & Learning Plan",
    "Risk Register, Contingency & Governance",
    "Why ZYNTH, Client Inputs & Next Mobilisation Decision",
]

_TABLE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "headers", "rows"],
    "properties": {
        "title": {"type": "string"},
        "headers": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 7},
        "rows": {
            "type": "array",
            "minItems": 2,
            "items": {"type": "array", "items": {"type": "string"}},
        },
    },
}

_PROPOSAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "client", "market", "sections"],
    "properties": {
        "title": {"type": "string", "description": "Proposal title, client-facing"},
        "client": {"type": "string", "description": "Client or prospect name (or 'Prospective Client')"},
        "market": {"type": "string", "description": "Myanmar or Singapore"},
        "estimated_value": {"type": "string", "description": "e.g. 'MMK 45,000,000' or 'S$18,000'"},
        "one_line_ask": {
            "type": "string",
            "description": (
                "ONE sentence the client reads first: who engages ZYNTH to do what, "
                "for what turnkey investment, targeting which single headline result. "
                "e.g. 'WavePay engages ZYNTH to deliver a 250-guest premium launch for "
                "~129M MMK, targeting 250 premium sign-ups in 30 days.'"
            ),
        },
        "sections": {
            "type": "array",
            "minItems": 15,
            "maxItems": 15,
            "items": {
                "type": "object",
                "required": ["heading", "body", "tables"],
                "properties": {
                    "heading": {"type": "string"},
                    "body": {
                        "type": "string",
                        "description": (
                            "Client-grade prose, 100-250 words: the strategic narrative. "
                            "Detail lives in the tables, not the prose. \\n\\n paragraphs, "
                            "'- ' bullets. NO emoji."
                        ),
                    },
                    "tables": {
                        "type": "array",
                        "items": _TABLE_SCHEMA,
                        "maxItems": 3,
                        "description": "Structured data tables — the executable core of the section",
                    },
                },
            },
        },
    },
}


class MasterProposalAgent(BaseAgent):
    """Writes a full fifteen-section client-grade proposal document."""

    agent_key = "master_proposal"
    display_name = "Master Proposal Writer"
    role_description = (
        "You are ZYNTH's senior proposal writer producing complete, client-ready "
        "decision documents. You write to the full ZYNTH document standard: clear "
        "sections, concept depth, concrete deliverables, bottom-up costs, measurement, "
        "risk and approvals. You protect commercial discipline with founder-approved "
        "margin targets, deposits and written change control. Vendor rates are verified "
        "or explicitly indicative pending RFQ."
    )
    output_schema: dict[str, Any] = _PROPOSAL_SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return self._build_prompt(kwargs.get("brief", ""))

    @staticmethod
    def _build_prompt(brief: str) -> str:
        from utils.venues import venues_block
        section_list = "\n".join(f"{i}. {name}" for i, name in enumerate(SECTION_NAMES, 1))
        # Rotating best-of pool (top-3 Critic-scored proposals); falls back to the
        # seed exemplar until real approved proposals exist.
        from utils.bestof import best_of_block
        exemplar_block = best_of_block()
        return (
            f"Write a COMPLETE, EXECUTABLE, CLIENT-GRADE ZYNTH proposal for this brief:\n\n"
            f"BRIEF: {brief}\n"
            f"{venues_block()}"
            f"{exemplar_block}"
            "FIRST, write `one_line_ask`: who engages ZYNTH to do what, over what period, "
            "for what stated investment basis, targeting which headline decision or result. "
            "Make it approvable in one sentence.\n\n"
            f"Then produce exactly these fifteen sections:\n{section_list}\n\n"
            "This is a completeness FLOOR, not a creative ceiling. Generate bold, original, "
            "market-relevant work and add specialist tables/logic for events, 3D, video, "
            "creator, sponsorship, retail, regulated work or dual markets whenever relevant.\n\n"
            "NON-NEGOTIABLE CONTENT:\n"
            "- Sec 1: release status, version, decision required, one-line ask and executive summary.\n"
            "- Sec 3–4: distinguish verified facts, client-provided inputs and assumptions. Include "
            "audience, category/competitor and cultural/market table as appropriate.\n"
            "- Sec 5: compare at least THREE named creative territories and defend the recommended route.\n"
            "- Sec 6: give the campaign/event title, big idea, full concept explanation, brand role, "
            "signature moment, visual/tonal world, key message and cultural/claims boundaries.\n"
            "- Sec 7: include a full audience journey plus phase/channel/experience architecture.\n"
            "- Sec 8: specify deliverable, quantity, format, owner, revisions, approval gate and acceptance criteria.\n"
            "- Sec 9: include a week-by-week timeline and RACI/approval table.\n"
            "- Sec 10: include supplier/technology/rights/compliance table. Tag every supplier/rate "
            "Verified, Indicative or To Source. Never invent contacts or present a guess as fact.\n"
            "- Sec 11: itemise every budget line in the local market currency; separate ZYNTH fee, paid media, "
            "production, talent, venue, technology, travel, taxes and third-party costs. State FX/date only "
            "when supplied by evidence. Include a 10% contingency on confirmed third-party cost and show any "
            "lean/standard/premium scenario when scope uncertainty is material.\n"
            "- Sec 12: state payment milestones, deposits, revision/change-order policy, exclusions, IP/usage, "
            "account ownership and currency review rule. Do not claim a fixed margin or payment term unless "
            "the brief or ZYNTH policy gives one; label proposed terms clearly.\n"
            "- Sec 13: table with objective, KPI, definition, target/baseline status, source/tool, cadence, "
            "attribution method, owner and action if underperforming. Never guarantee ROI, sales or reach.\n"
            "- Sec 14: risk table covering creative, cultural, claims, platform, data, commercial, production, "
            "safety and market-specific risks as relevant, with likelihood, impact, mitigation, owner and fallback.\n"
            "- Sec 15: explain why ZYNTH without fabricated proof, list exact client inputs and named approval gates, "
            "then close with one practical mobilisation decision.\n\n"
            "Write rich, specific client-grade prose and useful tables. Every number must be marked verified, "
            "indicative or assumption. Explain the concept so a client can feel it and explain the setup so a "
            "delivery team can run it. No emoji, no AI/system jargon, no empty generic statements."
        )

    async def write_proposal(self, brief: str, memory: SharedMemory) -> dict[str, Any]:
        """Generate the full proposal structure (single high-quality LLM call).

        Best-effort live web research is prepended to the brief so the
        proposal reflects current market signals — but a failed/blocked
        fetch never delays or breaks generation.
        """
        live_context = ""
        try:
            from utils.webresearch import research_block
            live_context = await research_block(brief)
        except Exception:
            live_context = ""

        prompt = self._build_prompt(brief)
        if live_context:
            prompt = prompt + live_context

        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=prompt,
            schema=_PROPOSAL_SCHEMA,
            max_tokens=24000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        return data
