"""Chief Marketing Officer (CMO) Agent.

Reports to the CEO Agent. Owns ZYNTH's full marketing strategy: content
calendar, campaign pipeline, channel mix, brand positioning, and KPI
tracking. Briefs the creative and research agents with specific tasks.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class CMOAgent(BaseAgent):
    agent_key = "cmo"
    display_name = "CMO — Chief Marketing Officer"
    role_description = (
        "You are ZYNTH's Chief Marketing Officer. You are responsible for the overall "
        "marketing strategy, content calendar, campaign planning, and brand positioning. "
        "You receive the CEO's daily agenda and translate it into specific tasks for the "
        "Creative, Research, and Social Media teams. You are data-driven, brand-obsessed, "
        "and relentlessly focused on measurable growth outcomes."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["marketing_priorities", "content_calendar", "campaign_ideas", "team_assignments", "kpis"],
        "properties": {
            "marketing_priorities": {"type": "array", "items": {"type": "string"}},
            "content_calendar": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["day", "content_type", "topic", "channel"],
                    "properties": {
                        "day": {"type": "string"},
                        "content_type": {"type": "string"},
                        "topic": {"type": "string"},
                        "channel": {"type": "string"},
                    },
                },
            },
            "campaign_ideas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "objective", "channels", "est_budget_usd"],
                    "properties": {
                        "name": {"type": "string"},
                        "objective": {"type": "string"},
                        "channels": {"type": "array", "items": {"type": "string"}},
                        "est_budget_usd": {"type": "number"},
                    },
                },
            },
            "team_assignments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["team", "task", "priority"],
                    "properties": {
                        "team": {"type": "string"},
                        "task": {"type": "string"},
                        "priority": {"type": "string"},
                    },
                },
            },
            "kpis": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        ceo_agenda = await memory.get("ceo_agenda", {})
        client_brief = await memory.get("client_brief", {})
        qa_feedback = kwargs.get("qa_feedback", "")

        prompt = (
            "CEO Daily Agenda:\n"
            f"{ceo_agenda}\n\n"
            "Agency context / active clients:\n"
            f"{client_brief}\n\n"
            "As CMO, produce: (1) your top 3-5 marketing priorities for today, "
            "(2) a content calendar covering the next 5 days across key channels, "
            "(3) 2-3 new campaign ideas with name, objective, channel mix and rough budget, "
            "(4) specific task assignments for your teams (Creative, Research, Social), "
            "(5) the KPIs you will track this week."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt
