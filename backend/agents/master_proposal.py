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

# IGNITE-standard structure: 11 sections, table-heavy, executable — not a
# narrative pitch. Benchmarked against the ZYNTH IGNITE Master Proposal.
SECTION_NAMES = [
    "Executive Overview & Strategic Rationale",
    "Market Analysis & Audience Intelligence",
    "Concept, Programme & Creative Direction",
    "Financial Model (multi-currency)",
    "Marketing & Campaign Plan",
    "Operations Plan & Phase Gates",
    "Vendor & Talent Register",
    "KPI Dashboard & Measurement Framework",
    "Risk Register & Contingency Protocols",
    "Post-Event/Campaign Report Framework & Roadmap",
    "Investment Summary & Next Steps",
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
        "sections": {
            "type": "array",
            "minItems": 11,
            "maxItems": 11,
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
        from utils.venues import venues_block
        section_list = "\n".join(f"{i}. {name}" for i, name in enumerate(SECTION_NAMES, 1))
        return (
            f"Write a COMPLETE, EXECUTABLE client-ready proposal for this brief:\n\n"
            f"BRIEF: {brief}\n"
            f"{venues_block()}\n\n"
            f"Produce exactly these eleven sections:\n{section_list}\n\n"
            "TABLE REQUIREMENTS (a document without these is a pitch, not a plan):\n"
            "- Sec 2: audience segment table (segment, demographics, channel behaviour) "
            "and/or competitor table\n"
            "- Sec 3: programme/run-of-show table (time, duration, segment, owner) for "
            "events; content calendar table for campaigns\n"
            "- Sec 4: itemised cost table with USD/SGD/MMK columns at the MARKET rate, "
            "10% contingency line, quoted total; if the project generates revenue "
            "(tickets/sponsorship), add a revenue table AND a Lean/Standard/Premium "
            "scenario P&L table\n"
            "- Sec 5: week-by-week plan table (week, phase, activities, channels, budget)\n"
            "- Sec 6: phase-gate table (phase, timeline, gates, owner, risk if skipped)\n"
            "- Sec 7: vendor/talent table (category, recommendation, est cost, lead time, "
            "backup plan) — unverified rates tagged 'TBC'\n"
            "- Sec 8: KPI table (metric, formula, target, benchmark)\n"
            "- Sec 9: risk table (risk, likelihood, impact, mitigation, owner)\n"
            "Other rules: infer market/industry from the brief and state assumptions; "
            "50% deposit clause in Sec 11; every number realistic for the market; "
            "prose carries strategy, tables carry the detail; client-grade, no emoji."
        )

    async def write_proposal(self, brief: str, memory: SharedMemory) -> dict[str, Any]:
        """Generate the full proposal structure (single high-quality LLM call)."""
        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=self._build_prompt(brief),
            schema=_PROPOSAL_SCHEMA,
            max_tokens=16000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        return data
