"""Master Proposal Agent — turns a brief (or a pool idea) into a full,
client-grade proposal document.

Unlike ProposalFactoryAgent (cheap, high-volume idea drafts on the
fallback model), this agent makes ONE high-quality call on the primary
model and produces the eight master-proposal sections per the ZYNTH
document standard. The result is rendered to .docx by utils/docgen.py.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory

SECTION_NAMES = [
    "Executive Summary",
    "Situation & Market Analysis",
    "Strategy & Big Idea",
    "Campaign / Event Plan & Key Activities",
    "Timeline & Milestones",
    "Budget & Investment",
    "KPIs & Measurement",
    "Why ZYNTH & Next Steps",
]

_PROPOSAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "client", "market", "sections"],
    "properties": {
        "title": {"type": "string", "description": "Proposal title, client-facing"},
        "client": {"type": "string", "description": "Client or prospect name (or 'Prospective Client')"},
        "market": {"type": "string", "description": "Myanmar or Singapore"},
        "estimated_value": {"type": "string", "description": "e.g. 'MMK 45,000,000' or 'S$18,000'"},
        "sections": {
            "type": "array",
            "minItems": 8,
            "maxItems": 8,
            "items": {
                "type": "object",
                "required": ["heading", "body"],
                "properties": {
                    "heading": {"type": "string"},
                    "body": {
                        "type": "string",
                        "description": (
                            "Full client-grade prose for this section, 150-400 words. "
                            "Use \\n\\n between paragraphs and '- ' bullet lines for lists. "
                            "NO emoji. Concrete numbers, activities, and deliverables."
                        ),
                    },
                },
            },
        },
    },
}


class MasterProposalAgent(BaseAgent):
    """Writes the full eight-section master proposal document."""

    agent_key = "master_proposal"
    display_name = "Master Proposal Writer"
    role_description = (
        "You are ZYNTH's senior proposal writer producing complete, client-ready "
        "proposal documents. You write to the ZYNTH document standard: numbered "
        "sections, no emoji, client-grade prose, concrete deliverables and numbers. "
        "You always respect financial governance: pricing protects a 35% gross "
        "margin and every proposal carries the 50% deposit-before-work clause. "
        "Vendor rates from the knowledge base are estimates pending RFQ."
    )
    output_schema: dict[str, Any] = _PROPOSAL_SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return self._build_prompt(kwargs.get("brief", ""))

    @staticmethod
    def _build_prompt(brief: str) -> str:
        section_list = "\n".join(f"{i}. {name}" for i, name in enumerate(SECTION_NAMES, 1))
        return (
            f"Write a COMPLETE client-ready proposal for this brief:\n\n"
            f"BRIEF: {brief}\n\n"
            f"Produce exactly these eight sections:\n{section_list}\n\n"
            "Rules:\n"
            "- Infer the market (Myanmar or Singapore) and industry from the brief; "
            "if ambiguous, choose the most likely and note the assumption in the summary\n"
            "- Budget & Investment: itemised categories with realistic amounts in the "
            "local currency, drawn from the vendor benchmarks where relevant, plus the "
            "50% deposit clause\n"
            "- Timeline: week-by-week milestones\n"
            "- KPIs: measurable targets with numbers\n"
            "- Key activities and deliverables must be concrete and countable\n"
            "- This document goes directly to a client — polish accordingly"
        )

    async def write_proposal(self, brief: str, memory: SharedMemory) -> dict[str, Any]:
        """Generate the full proposal structure (single high-quality LLM call)."""
        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=self._build_prompt(brief),
            schema=_PROPOSAL_SCHEMA,
            max_tokens=8000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        return data
