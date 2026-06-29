"""Content & Creative Copywriter Agent.

Turns the Research & SEO Agent's findings directly into high-converting,
on-brand creative: ad copy, a LinkedIn thought-leadership article, an SEO
blog outline, and an email nurture sequence.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class ContentCopywriterAgent(BaseAgent):
    """Generates ZYNTH-voiced creative across paid, organic, and email channels."""

    agent_key = "copywriter"
    display_name = "Content & Creative Copywriter Agent"
    role_description = (
        "You are ZYNTH's Senior Copywriter. You write premium, high-converting "
        "copy across paid ads, LinkedIn thought leadership, SEO blogs, and email "
        "nurture sequences. Every piece is grounded in the research findings you "
        "are given -- you never write generic copy."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["ad_copy", "linkedin_article", "seo_blog", "email_sequence"],
        "properties": {
            "ad_copy": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["platform", "headline", "body", "cta"],
                    "properties": {
                        "platform": {"type": "string"},
                        "headline": {"type": "string"},
                        "body": {"type": "string"},
                        "cta": {"type": "string"},
                    },
                },
            },
            "linkedin_article": {
                "type": "object",
                "required": ["title", "body"],
                "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
            },
            "seo_blog": {
                "type": "object",
                "required": ["title", "outline", "meta_description"],
                "properties": {
                    "title": {"type": "string"},
                    "outline": {"type": "array", "items": {"type": "string"}},
                    "meta_description": {"type": "string"},
                },
            },
            "email_sequence": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["subject", "body", "send_day"],
                    "properties": {
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "send_day": {"type": "integer"},
                    },
                },
            },
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        client_brief = await memory.get("client_brief", {})
        research = await memory.get("research_seo", {})
        qa_feedback = kwargs.get("qa_feedback")

        prompt = (
            "Client brief:\n"
            f"{client_brief}\n\n"
            "Research & SEO findings to build directly on (use the keywords and focus "
            "areas, don't ignore them):\n"
            f"{research}\n\n"
            "Produce: (1) ad copy for at least 2 platforms (e.g. Meta and Google), "
            "(2) one LinkedIn thought-leadership article, (3) one SEO blog with title, "
            "outline, and meta description targeting the high-intent keywords, and "
            "(4) a 3-5 email nurture sequence with send-day cadence."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback on your previous attempt -- address this directly: {qa_feedback}"
        return prompt
