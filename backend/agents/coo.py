"""Chief Operations Officer (COO) Agent.

Reports to the CEO Agent. Owns ZYNTH's operational efficiency, vendor
management, process development, and ensures every department has the
resources to execute. Oversees Event Management and Operations teams.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class COOAgent(BaseAgent):
    agent_key = "coo"
    display_name = "COO — Chief Operations Officer"
    role_description = (
        "You are ZYNTH's Chief Operations Officer. You own process, efficiency, and "
        "execution. You develop SOPs, manage vendor relationships, oversee event "
        "operations, and make sure the agency can deliver flawlessly when client "
        "projects come in. You think in systems: workflows, checklists, vendor contracts, "
        "project timelines. You are calm, thorough, and relentlessly organized."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["operations_priorities", "process_improvements", "vendor_tasks", "resource_requirements", "risk_flags"],
        "properties": {
            "operations_priorities": {"type": "array", "items": {"type": "string"}},
            "process_improvements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["area", "current_gap", "proposed_action"],
                    "properties": {
                        "area": {"type": "string"},
                        "current_gap": {"type": "string"},
                        "proposed_action": {"type": "string"},
                    },
                },
            },
            "vendor_tasks": {"type": "array", "items": {"type": "string"}},
            "resource_requirements": {"type": "array", "items": {"type": "string"}},
            "risk_flags": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        ceo_agenda = await memory.get("ceo_agenda", {})
        cmo_output = await memory.get("cmo", {})
        qa_feedback = kwargs.get("qa_feedback", "")

        prompt = (
            "CEO Daily Agenda:\n"
            f"{ceo_agenda}\n\n"
            "CMO's marketing plan (your operations must support this):\n"
            f"{cmo_output}\n\n"
            "As COO, produce: (1) your operational priorities today, (2) process improvements "
            "to close gaps in how ZYNTH delivers projects, (3) vendor tasks to assign to the "
            "Operations team today (research, outreach, quotes), (4) resource requirements "
            "(tools, headcount, budget) flagged to CEO, (5) any operational risks or blockers."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt
