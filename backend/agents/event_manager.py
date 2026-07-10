"""Event Management Agent.

Reports to COO. Specializes in planning and proposing marketing events,
brand activations, product launches, galas, trade shows, and corporate
functions — with a focus on the Yangon market. Produces full event
proposals ready to present to clients or the CEO for approval.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from agents.base import BaseAgent
from config.yangon_data import YANGON_VENUES, YANGON_MARKET_CONTEXT, get_venues_by_capacity
from utils.state import SharedMemory
from utils.storage import save_document


class EventManagerAgent(BaseAgent):
    agent_key = "event_manager"
    display_name = "Event Manager"
    role_description = (
        "You are ZYNTH's Event Manager. You design and plan outstanding marketing events "
        "in Yangon and across Myanmar. You know every major venue, understand local "
        "logistics, build realistic budgets, and create event proposals that clients say "
        "yes to. For every event you plan, you consider: objective, audience, venue fit, "
        "budget, timeline, vendors needed, risk mitigation, and how the event feeds into "
        "the larger marketing campaign."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["event_proposals", "active_event_pipeline", "vendor_requirements", "upcoming_milestones"],
        "properties": {
            "event_proposals": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "event_type", "objective", "proposed_venue", "est_budget_mmk", "timeline_weeks", "key_deliverables"],
                    "properties": {
                        "name": {"type": "string"},
                        "event_type": {"type": "string"},
                        "objective": {"type": "string"},
                        "proposed_venue": {"type": "string"},
                        "est_budget_mmk": {"type": "string"},
                        "timeline_weeks": {"type": "integer"},
                        "key_deliverables": {"type": "array", "items": {"type": "string"}},
                        "target_audience": {"type": "string"},
                        "success_metrics": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "active_event_pipeline": {"type": "array", "items": {"type": "string"}},
            "vendor_requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["category", "requirement"],
                    "properties": {
                        "category": {"type": "string"},
                        "requirement": {"type": "string"},
                    },
                },
            },
            "upcoming_milestones": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        ceo_agenda = await memory.get("ceo_agenda", {})
        cmo_output = await memory.get("cmo", {})
        coo_output = await memory.get("coo", {})
        client_brief = await memory.get("client_brief", {})
        qa_feedback = kwargs.get("qa_feedback", "")

        # Feed the actual Yangon venue database into the prompt
        venue_summary = [
            f"- {v.name} ({v.area}): seats {v.capacity_seated}, est {v.est_price_range}"
            for v in YANGON_VENUES[:8]
        ]
        market_notes = YANGON_MARKET_CONTEXT

        prompt = (
            "CEO Agenda:\n"
            f"{ceo_agenda}\n\n"
            "CMO campaign ideas requiring events:\n"
            f"{cmo_output.get('campaign_ideas', [])}\n\n"
            "COO operational context:\n"
            f"{coo_output.get('operations_priorities', [])}\n\n"
            "Client / agency context:\n"
            f"{client_brief}\n\n"
            "YANGON VENUE DATABASE (use these real venues in proposals):\n"
            + "\n".join(venue_summary)
            + f"\n\nYangon market context: {market_notes}\n\n"
            "Produce: (1) 2-3 concrete event proposals with realistic Yangon venues and "
            "MMK budgets, covering at least one product launch/activation AND one corporate "
            "dinner/gala format, (2) the current event pipeline with status, (3) vendor "
            "categories needed this week, (4) key milestones and deadlines."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt

    async def run(self, memory: SharedMemory, **kwargs: Any):
        result = await super().run(memory, **kwargs)
        if result.success and result.data:
            save_document("event_proposals_latest.json", result.data, department="event_management")
        return result
