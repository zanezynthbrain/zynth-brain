"""Market Research & SEO Agent.

Analyzes the competitive landscape, surfaces high-intent keywords, and
grounds every downstream agent in ZYNTH's own site context. In production
this agent would call Serper/SEMrush/Jina AI; here it uses the shared
``http_get`` tool mockup (toggle ``ZYNTH_ALLOW_NETWORK=true`` plus real API
keys to go live) so the rest of the pipeline is fully exercised offline.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory
from utils.tools import http_get


class MarketResearchSEOAgent(BaseAgent):
    """Competitor analysis + keyword research feeding the rest of the pipeline."""

    agent_key = "research_seo"
    display_name = "Market Research & SEO Agent"
    role_description = (
        "You are ZYNTH's Market Research & SEO Lead. You analyze competitor "
        "landscapes, surface high-intent keywords with commercial value, and "
        "ground recommendations in real market context. You are precise, "
        "evidence-based, and call out what's actually winning vs. what's noise."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": [
            "site_context_summary",
            "competitor_landscape",
            "high_intent_keywords",
            "recommended_focus_areas",
        ],
        "properties": {
            "site_context_summary": {"type": "string"},
            "competitor_landscape": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "strengths", "weaknesses"],
                    "properties": {
                        "name": {"type": "string"},
                        "url": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "weaknesses": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "high_intent_keywords": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["keyword", "intent", "est_monthly_volume"],
                    "properties": {
                        "keyword": {"type": "string"},
                        "intent": {"type": "string"},
                        "est_monthly_volume": {"type": "integer"},
                    },
                },
            },
            "recommended_focus_areas": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        client_brief = await memory.get("client_brief", {})
        qa_feedback = kwargs.get("qa_feedback")

        # Tool integration: pull lightweight context signals before reasoning.
        # In production, swap the URLs below for real Serper/SEMrush/Jina calls.
        site_signal = await http_get("https://www.zynth.asia", params={"source": "context-scan"})
        competitor_signal = await http_get(
            "https://serper.dev/search",
            params={"q": f"{client_brief.get('industry', 'digital marketing')} competitors"},
        )

        prompt = (
            "Client brief:\n"
            f"{client_brief}\n\n"
            "Tool signal -- ZYNTH site scan (mocked unless ZYNTH_ALLOW_NETWORK=true):\n"
            f"{site_signal.data}\n\n"
            "Tool signal -- competitor search (mocked unless ZYNTH_ALLOW_NETWORK=true):\n"
            f"{competitor_signal.data}\n\n"
            "Produce: (1) a summary of how www.zynth.asia should position itself for this "
            "client's industry, (2) a competitor landscape with named strengths/weaknesses, "
            "(3) a high-intent keyword list with commercial intent and estimated monthly "
            "volume, and (4) recommended strategic focus areas for the campaign."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback on your previous attempt -- address this directly: {qa_feedback}"
        return prompt
