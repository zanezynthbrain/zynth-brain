"""HR & People Agent.

Reports to CEO. Manages all people operations: hiring plans, job
descriptions, onboarding SOPs, team structure (AI team + future human
team), performance frameworks, and back-office HR documentation.
When human staff are hired, this agent helps manage their onboarding,
culture, and day-to-day HR needs.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class HRAgent(BaseAgent):
    agent_key = "hr"
    display_name = "HR — People & Culture"
    role_description = (
        "You are ZYNTH's HR and People Lead. You own everything related to the team: "
        "organizational structure, hiring plans, job descriptions, onboarding, culture, "
        "and back-office HR documentation. Right now ZYNTH runs as an AI-first team; "
        "you help plan for future human hires, develop the documentation and SOPs they "
        "will need from day one, and ensure the AI agents have clear role definitions "
        "and performance criteria. Think of it as building the company handbook before "
        "we need it — so when the first human employee joins, everything is ready."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["hr_priorities", "org_chart_update", "hiring_plan", "documents_produced", "culture_initiatives"],
        "properties": {
            "hr_priorities": {"type": "array", "items": {"type": "string"}},
            "org_chart_update": {
                "type": "object",
                "required": ["current_ai_team", "next_human_hire", "rationale"],
                "properties": {
                    "current_ai_team": {"type": "array", "items": {"type": "string"}},
                    "next_human_hire": {"type": "string"},
                    "rationale": {"type": "string"},
                },
            },
            "hiring_plan": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["role", "priority", "key_skills", "target_salary_range"],
                    "properties": {
                        "role": {"type": "string"},
                        "priority": {"type": "string"},
                        "key_skills": {"type": "array", "items": {"type": "string"}},
                        "target_salary_range": {"type": "string"},
                    },
                },
            },
            "documents_produced": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["document_name", "status", "description"],
                    "properties": {
                        "document_name": {"type": "string"},
                        "status": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            },
            "culture_initiatives": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        ceo_agenda = await memory.get("ceo_agenda", {})
        coo_output = await memory.get("coo", {})
        qa_feedback = kwargs.get("qa_feedback", "")

        prompt = (
            "CEO Agenda:\n"
            f"{ceo_agenda}\n\n"
            "COO's resource requirements (may trigger hiring needs):\n"
            f"{coo_output.get('resource_requirements', [])}\n\n"
            "You ARE HR — you do the work, you do not assign it (see Operating "
            "Principles). Zane has zero HR experience beyond payroll, so never hand him "
            "a task; hand him finished, ready-to-use documents.\n\n"
            "Produce: (1) today's HR priorities, (2) an org chart update showing the "
            "current AI team and who the next human hire should be (and why), (3) a "
            "hiring plan with roles, required skills, and Myanmar/Singapore market salary "
            "ranges. Then (4) in documents_produced, ACTUALLY WRITE the single most "
            "important HR document that is still missing — the FULL, adopt-today text "
            "(e.g. the complete offer-letter template, the leave policy in full, the "
            "onboarding checklist step by step) inside the 'description' field, and set "
            "status to 'ready to use'. One finished document beats five named ones. "
            "(5) culture initiatives that keep ZYNTH a great place to work as humans join. "
            "The canonical, full HR system lives in docs/departments/HR_operating_system.md "
            "— build on it, don't contradict it."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt
