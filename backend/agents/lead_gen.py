"""Lead Generation & Outreach Agent.

Automates prospecting: maps client personas, builds a prospect shortlist,
drafts personalized cold emails, and scores inbound leads.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class LeadGenOutreachAgent(BaseAgent):
    """Persona mapping, prospecting, cold outreach, and inbound lead scoring."""

    agent_key = "lead_gen"
    display_name = "Lead Generation & Outreach Agent"
    role_description = (
        "You are ZYNTH's Lead Generation Strategist. You map buyer personas, "
        "build realistic prospect shortlists, write outreach that gets replies "
        "(not deleted), and score inbound leads against ICP fit."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["personas", "prospect_list", "cold_emails", "inbound_lead_evaluation"],
        "properties": {
            "personas": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "role", "pain_points", "channels"],
                    "properties": {
                        "name": {"type": "string"},
                        "role": {"type": "string"},
                        "pain_points": {"type": "array", "items": {"type": "string"}},
                        "channels": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "prospect_list": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["company", "contact_title", "fit_score"],
                    "properties": {
                        "company": {"type": "string"},
                        "contact_title": {"type": "string"},
                        "fit_score": {"type": "number"},
                    },
                },
            },
            "cold_emails": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["to_persona", "subject", "body"],
                    "properties": {
                        "to_persona": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                },
            },
            "inbound_lead_evaluation": {
                "type": "object",
                "required": ["score", "qualification_notes"],
                "properties": {
                    "score": {"type": "number"},
                    "qualification_notes": {"type": "string"},
                },
            },
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        client_brief = await memory.get("client_brief", {})
        research = await memory.get("research_seo", {})
        inbound_lead = kwargs.get("inbound_lead", {})
        qa_feedback = kwargs.get("qa_feedback")

        prompt = (
            "Client brief:\n"
            f"{client_brief}\n\n"
            "Research & SEO findings (use to inform persona pain points and channels):\n"
            f"{research}\n\n"
            "Inbound lead to evaluate (may be empty if none submitted yet):\n"
            f"{inbound_lead}\n\n"
            "Produce: (1) 2-3 buyer personas, (2) a prospect shortlist of realistic-sounding "
            "target companies with contact titles and a 0-1 fit score, (3) one personalized "
            "cold email per persona, and (4) an evaluation of the inbound lead (or a "
            "placeholder evaluation noting none was submitted)."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback on your previous attempt -- address this directly: {qa_feedback}"
        return prompt
