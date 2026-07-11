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
            "As HR Lead, produce: (1) today's HR priorities, (2) an org chart update "
            "showing the current AI team and who the next human hire should be (and why), "
            "(3) a hiring plan with roles, required skills, and Myanmar market salary ranges, "
            "(4) list of HR documents to produce today (job descriptions, offer letter templates, "
            "onboarding checklists, employee handbook sections, leave policies, etc.), "
            "(5) culture and team initiatives to keep ZYNTH as a great place to work when "
            "humans join. Note: current team is AI-first but document everything as if "
            "humans are joining next month."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt
