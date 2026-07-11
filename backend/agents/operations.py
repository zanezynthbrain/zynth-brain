"""Operations & Vendor Research Agent.

Reports to COO. Researches and maintains ZYNTH's vendor database,
develops SOPs for every project type, sources pricing from the Yangon
market, and builds the operational playbooks that ensure flawless
delivery when real client projects come in.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from config.yangon_data import YANGON_SUPPLIERS, YANGON_MARKET_CONTEXT
from utils.state import SharedMemory
from utils.storage import save_document


class OperationsAgent(BaseAgent):
    agent_key = "operations"
    display_name = "Operations & Vendor Research"
    role_description = (
        "You are ZYNTH's Operations Specialist. You research vendors, build the agency's "
        "supplier database, develop pricing benchmarks for the Yangon/Myanmar market, "
        "write standard operating procedures (SOPs) for every type of project ZYNTH "
        "delivers, and create the checklists and workflows that the team uses on every "
        "job. You are meticulous, thorough, and think in systems. When you research a "
        "vendor, you document: name, category, services, price range, contact approach, "
        "negotiation notes, and lead time requirements."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["vendor_research", "sop_produced", "pricing_benchmarks", "market_research_findings", "negotiation_strategies"],
        "properties": {
            "vendor_research": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["category", "vendor_name", "services", "est_price_range", "notes"],
                    "properties": {
                        "category": {"type": "string"},
                        "vendor_name": {"type": "string"},
                        "services": {"type": "array", "items": {"type": "string"}},
                        "est_price_range": {"type": "string"},
                        "contact_approach": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                },
            },
            "sop_produced": {
                "type": "object",
                "required": ["title", "project_type", "steps", "estimated_duration"],
                "properties": {
                    "title": {"type": "string"},
                    "project_type": {"type": "string"},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "estimated_duration": {"type": "string"},
                    "checklist": {"type": "array", "items": {"type": "string"}},
                },
            },
            "pricing_benchmarks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["service", "market_low_mmk", "market_high_mmk", "zynth_target_margin_pct"],
                    "properties": {
                        "service": {"type": "string"},
                        "market_low_mmk": {"type": "string"},
                        "market_high_mmk": {"type": "string"},
                        "zynth_target_margin_pct": {"type": "number"},
                    },
                },
            },
            "market_research_findings": {"type": "array", "items": {"type": "string"}},
            "negotiation_strategies": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        coo_output = await memory.get("coo", {})
        event_output = await memory.get("event_manager", {})
        today_focus = kwargs.get("focus_category", "av_sound")
        qa_feedback = kwargs.get("qa_feedback", "")

        supplier_summary = [
            f"- {s.category}: {s.est_price_range} | services: {', '.join(s.services[:3])}"
            for s in YANGON_SUPPLIERS
        ]
        market_notes = YANGON_MARKET_CONTEXT

        prompt = (
            "COO Priorities:\n"
            f"{coo_output.get('vendor_tasks', [])}\n\n"
            "Event vendor requirements from Event Manager:\n"
            f"{event_output.get('vendor_requirements', [])}\n\n"
            "Existing Yangon supplier categories in our database:\n"
            + "\n".join(supplier_summary)
            + f"\n\nYangon market context:\n{market_notes}\n\n"
            f"Today's deep-dive vendor focus category: {today_focus}\n\n"
            "Produce: (1) expanded vendor research for today's focus category — imagine "
            "you have called around and gotten 3-5 real vendor options with realistic MMK "
            "pricing, (2) one complete SOP for a common ZYNTH project type (product launch, "
            "event, campaign), (3) pricing benchmarks for 3-5 ZYNTH services with market "
            "low/high and our target margin, (4) market research findings about current "
            "Yangon supplier landscape, (5) negotiation strategies specific to Myanmar "
            "vendor culture."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt

    async def run(self, memory: SharedMemory, **kwargs: Any):
        result = await super().run(memory, **kwargs)
        if result.success and result.data:
            save_document("vendor_research_latest.json", result.data, department="operations")
            sop = result.data.get("sop_produced", {})
            if sop.get("title"):
                save_document(
                    f"sop_{sop['project_type'].replace(' ', '_').lower()}.json",
                    sop,
                    department="operations/sops",
                )
        return result
