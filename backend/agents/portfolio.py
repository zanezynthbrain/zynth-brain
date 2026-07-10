"""Creative Portfolio Agent.

Picks a real brand or industry category each day and produces a complete
creative work package — as if ZYNTH had been hired by that brand. The
output builds ZYNTH's portfolio so the team has real creative examples
to show potential clients, even before any paying projects exist.

CEO assigns the brand/industry. Creative team (Copywriter + this agent)
executes. Results are saved to outputs/portfolio/ as showcase pieces.
"""

from __future__ import annotations

import random
from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory
from utils.storage import save_document

# Rotating list of brand archetypes ZYNTH might work with in Myanmar/SEA
PORTFOLIO_BRANDS = [
    {"brand": "BrewHouse Myanmar", "industry": "craft_beverage", "tier": "local_sme"},
    {"brand": "AeroPulse Fitness", "industry": "health_wellness", "tier": "startup"},
    {"brand": "CityNest Property", "industry": "real_estate", "tier": "local_enterprise"},
    {"brand": "TechNova Solutions", "industry": "b2b_saas", "tier": "tech_startup"},
    {"brand": "LuxeThreads Myanmar", "industry": "fashion_retail", "tier": "local_sme"},
    {"brand": "SolarEdge Myanmar", "industry": "cleantech", "tier": "startup"},
    {"brand": "Pagoda Capital", "industry": "fintech_investment", "tier": "financial_services"},
    {"brand": "FreshMarket App", "industry": "grocery_delivery", "tier": "startup"},
    {"brand": "AceLearn Academy", "industry": "edtech", "tier": "startup"},
    {"brand": "GoldenGrain Rice", "industry": "fmcg_food", "tier": "local_enterprise"},
    {"brand": "MedConnect Myanmar", "industry": "healthtech", "tier": "startup"},
    {"brand": "TravelMM", "industry": "travel_tourism", "tier": "local_sme"},
    {"brand": "AutoRoute Myanmar", "industry": "automotive", "tier": "local_enterprise"},
    {"brand": "BuildSmart Construction", "industry": "construction", "tier": "b2b"},
    {"brand": "LittleStars Kindergarten", "industry": "education", "tier": "local_sme"},
]


class PortfolioAgent(BaseAgent):
    agent_key = "portfolio"
    display_name = "Creative Portfolio — Daily Brand Work"
    role_description = (
        "You are ZYNTH's Creative Team producing portfolio work. Each day you are given "
        "a brand to work on — as if ZYNTH has just been hired by them. You produce "
        "publication-ready creative direction, a content plan, ad copy concepts, and "
        "social media ideas. The goal is to build a portfolio ZYNTH can show to real "
        "clients to demonstrate the quality and range of the agency's work. Treat every "
        "portfolio brand as a real paying client. The work must be genuinely impressive."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["brand", "industry", "creative_direction", "content_plan", "ad_concepts", "social_media_plan", "brand_voice"],
        "properties": {
            "brand": {"type": "string"},
            "industry": {"type": "string"},
            "creative_direction": {
                "type": "object",
                "required": ["tagline", "visual_concept", "tone", "key_messages"],
                "properties": {
                    "tagline": {"type": "string"},
                    "visual_concept": {"type": "string"},
                    "tone": {"type": "string"},
                    "key_messages": {"type": "array", "items": {"type": "string"}},
                },
            },
            "brand_voice": {"type": "string"},
            "content_plan": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["content_type", "title", "description", "channel"],
                    "properties": {
                        "content_type": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "channel": {"type": "string"},
                    },
                },
            },
            "ad_concepts": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "required": ["platform", "headline", "body", "cta", "visual_note"],
                    "properties": {
                        "platform": {"type": "string"},
                        "headline": {"type": "string"},
                        "body": {"type": "string"},
                        "cta": {"type": "string"},
                        "visual_note": {"type": "string"},
                    },
                },
            },
            "social_media_plan": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["platform", "post_idea", "caption"],
                    "properties": {
                        "platform": {"type": "string"},
                        "post_idea": {"type": "string"},
                        "caption": {"type": "string"},
                    },
                },
            },
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        cmo_output = await memory.get("cmo", {})
        brand_override = kwargs.get("brand_override")
        qa_feedback = kwargs.get("qa_feedback", "")

        # CEO or CMO can assign a specific brand; otherwise rotate from list
        brand_info = brand_override or await memory.get("portfolio_brand_today")
        if not brand_info:
            brand_info = random.choice(PORTFOLIO_BRANDS)
            await memory.set("portfolio_brand_today", brand_info)

        prompt = (
            f"Today's portfolio brand: {brand_info['brand']}\n"
            f"Industry: {brand_info['industry']}\n"
            f"Brand tier/size: {brand_info['tier']}\n\n"
            "CMO content direction for context:\n"
            f"{cmo_output.get('marketing_priorities', [])}\n\n"
            "Imagine ZYNTH has just won this client. Produce a FULL creative package:\n"
            "(1) Creative direction: tagline, visual concept, tone, key messages\n"
            "(2) Brand voice definition (2-3 sentences)\n"
            "(3) Content plan: 5+ content pieces across formats and channels\n"
            "(4) Ad concepts: 2-3 ads with headline, body, CTA, and visual direction\n"
            "(5) Social media plan: 3-5 posts with platform and caption\n\n"
            "Make this genuinely impressive — something ZYNTH would be proud to show "
            "in a client pitch deck. Reference the Myanmar/SEA market where relevant."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt

    async def run(self, memory: SharedMemory, **kwargs: Any):
        result = await super().run(memory, **kwargs)
        if result.success and result.data:
            brand_slug = result.data.get("brand", "brand").replace(" ", "_").lower()
            save_document(f"{brand_slug}_creative_package.json", result.data, department="portfolio")
        return result
