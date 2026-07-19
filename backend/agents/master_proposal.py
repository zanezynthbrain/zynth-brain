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
        exemplar = load_exemplar()
        exemplar_block = (
            f"\n\n===== GOLD-STANDARD REFERENCE (match this bar) =====\n{exemplar}\n"
            "===== END REFERENCE =====\n\n"
            if exemplar else ""
        )
        return (
            f"Write a COMPLETE, EXECUTABLE client-ready proposal for this brief:\n\n"
            f"BRIEF: {brief}\n"
            f"{venues_block()}"
            f"{exemplar_block}"
            "FIRST, write `one_line_ask`: ONE sentence — who engages ZYNTH to do what, "
            "for what turnkey investment, targeting which single headline result. This is "
            "the line the client reads before anything else.\n\n"
            f"Then produce exactly these eleven sections:\n{section_list}\n\n"
            "OPEN Section 1 by restating the one-line ask and the strategic read — WHY this, "
            "WHY now, and the single audience insight the whole plan is built on (not just "
            "an overview).\n\n"
            "TABLE REQUIREMENTS (a document without these is a pitch, not a plan):\n"
            "- Sec 2: audience segment table (segment, demographics, channel behaviour) "
            "and/or competitor table\n"
            "- Sec 3: programme/run-of-show table (time, duration, segment, owner) for "
            "events; content calendar table for campaigns\n"
            "- Sec 4: itemised cost table with USD/SGD/MMK columns at the MARKET rate, "
            "10% contingency line, quoted total; THEN a transparent commercial table "
            "(delivered cost + ZYNTH management fee with its tier %, e.g. Premium 20-25% + "
            "total client investment) and 50/30/20 payment terms; if the project generates "
            "revenue (tickets/sponsorship), add a revenue table AND a Lean/Standard/Premium "
            "scenario P&L table\n"
            "- Sec 5: week-by-week plan table (week, phase, activities, channels, budget)\n"
            "- Sec 6: phase-gate table (phase, timeline, gates, owner, risk if skipped)\n"
            "- Sec 7: vendor/talent table (category, recommendation, est cost, lead time, "
            "backup). DATA HONESTY: tag each row 'Verified' (confirmed in ZYNTH's supplier "
            "DB) or 'Indicative' (market placeholder, confirmed at contracting) — never "
            "present a guessed number as fact.\n"
            "- Sec 8: KPI + ATTRIBUTION table (metric, target, HOW measured). State how each "
            "result is attributed to the work — e.g. a unique QR/tracking link per guest or "
            "lead — so success is measured, not claimed. Lead with the money/reach metrics.\n"
            "- Sec 9: risk table (risk, likelihood, impact, mitigation, owner)\n"
            "- Sec 11: investment summary + 50% deposit clause + a 'What we need from you' "
            "client-input checklist (approvals, assets, spokespeople, disclaimers) so the "
            "client can act immediately.\n"
            "Other rules: infer market/industry from the brief and state assumptions; "
            "every number realistic for the market; prose carries strategy, tables carry "
            "the detail; client-grade, no emoji, no coding/system jargon."
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
            max_tokens=16000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        return data
