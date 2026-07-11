"""Lead Generation & Outreach Agent — NOVA persona.

NOVA is ZYNTH's BD Agent covering Singapore and Myanmar.
Sharp, specific, no fluff. Picks 3 real prospects per run,
writes copy-paste ready outreach in the exact ZYNTH BD Brief format.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class LeadGenOutreachAgent(BaseAgent):
    """NOVA — ZYNTH's BD Agent. Prospects, qualifies, drafts outreach."""

    agent_key = "lead_gen"
    display_name = "NOVA — BD Agent"
    role_description = (
        "You are NOVA, ZYNTH's BD Agent based in Singapore.\n\n"
        "ZYNTH is an AI-powered 360° marketing agency serving Singapore and Myanmar.\n"
        "Services: social media management, paid ads (Meta/Google/TikTok), creative production, "
        "brand strategy, events, KOL campaigns, video production.\n\n"
        "Target clients:\n"
        "SG — F&B brands, aesthetic/wellness clinics, fintech startups, property developers, "
        "lifestyle brands, SMEs spending S$2,000–10,000/month on marketing.\n"
        "MM — KBZ Bank, AYA Bank, CB Bank, major FMCG brands (City Mart, Super Seven Stars), "
        "private hospitals (Pun Hlaing, Victoria, Parami), real estate (Shwe Taung, "
        "Myanmar Thilawa SEZ), F&B chains, telecom (MPT, Ooredoo, Mytel).\n\n"
        "You write like a sharp, confident agency insider. Short sentences. Direct. Punchy. "
        "Every prospect must be a real, specific company — not a generic placeholder. "
        "Every cold message must be copy-paste ready — natural, not salesy."
    )

    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["prospects", "inbound_lead_evaluation"],
        "properties": {
            "prospects": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "required": [
                        "company", "market", "what_they_do", "contact_title",
                        "fit_score", "why_now", "angle", "outreach_message",
                        "expected_move", "suggested_services", "budget_estimate",
                    ],
                    "properties": {
                        "company": {"type": "string"},
                        "market": {"type": "string", "enum": ["Singapore", "Myanmar"]},
                        "what_they_do": {"type": "string"},
                        "contact_title": {"type": "string"},
                        "fit_score": {"type": "number", "minimum": 0, "maximum": 1},
                        "why_now": {
                            "type": "string",
                            "description": "Specific reason to reach out today — recent news, growth signal, gap spotted",
                        },
                        "angle": {
                            "type": "string",
                            "description": "2-3 sentences. Why them. Why ZYNTH specifically. What pain we solve.",
                        },
                        "outreach_message": {
                            "type": "string",
                            "description": "Exact first message — ready to copy-paste into LinkedIn DM or email. Natural, not salesy.",
                        },
                        "expected_move": {
                            "type": "string",
                            "description": "What happens next if they respond positively.",
                        },
                        "suggested_services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "description": "Specific ZYNTH services to pitch this prospect",
                        },
                        "budget_estimate": {
                            "type": "string",
                            "description": "Estimated monthly budget range e.g. S$3,000–6,000/month or MMK 5M–10M/month",
                        },
                    },
                },
            },
            "inbound_lead_evaluation": {
                "type": "object",
                "required": ["score", "qualification_notes"],
                "properties": {
                    "score": {"type": "number", "minimum": 0, "maximum": 1},
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

        market_focus = client_brief.get("market", "both Singapore and Myanmar")

        prompt = (
            f"Market focus today: {market_focus}\n\n"
            "Pick exactly 3 real, specific prospects — mix markets and sectors for variety. "
            "Do NOT invent companies. Name real brands you have knowledge of.\n\n"
            "SG options: Tolido's Espresso, Atlas Bar, The Providore, Angie's Oyster Bar, "
              "OG Department Store, Watsons Singapore, Courts Singapore, Razer, Carousell, "
              "PropertyGuru, Hegen, Charles & Keith, BreadTalk, Toast Box, Ya Kun Kaya Toast, "
              "Skin Inc, TLC Surgery, The Aesthetic Medical Partners, Raffles Medical.\n"
            "MM options: KBZ Bank, AYA Bank, CB Bank, AGD Bank, MPT, Ooredoo Myanmar, Mytel, "
              "City Mart, Ocean Supercenter, Super Seven Stars, Pun Hlaing Hospital, "
              "Victoria Hospital, Grand Royal Group, Myanmar Brewery, Shwe Taung Group, "
              "HAGL Myanmar, FMI Centre, Junction City.\n\n"
        )

        if research:
            keywords = research.get("high_intent_keywords", [])
            if keywords:
                top_kw = [k.get("keyword", k) if isinstance(k, dict) else k for k in keywords[:5]]
                prompt += f"Market research — trending keywords: {', '.join(top_kw)}\n"
            gaps = research.get("competitor_analysis", {})
            if isinstance(gaps, dict) and gaps.get("content_gap_opportunity"):
                prompt += f"Content gap opportunity: {gaps['content_gap_opportunity']}\n"
            prompt += "\n"

        if client_brief and client_brief != {"market": market_focus}:
            prompt += f"Additional brief context:\n{client_brief}\n\n"

        if inbound_lead:
            prompt += f"Inbound lead to evaluate:\n{inbound_lead}\n\n"
        else:
            prompt += "No inbound lead submitted today — use placeholder evaluation.\n\n"

        prompt += (
            "For each prospect produce:\n"
            "- company: real company name\n"
            "- market: Singapore or Myanmar\n"
            "- what_they_do: one sentence describing their business\n"
            "- contact_title: best person to reach (e.g. Marketing Director, CMO, Founder)\n"
            "- fit_score: 0.0 to 1.0\n"
            "- why_now: specific trigger — recent expansion, weak digital presence, "
            "seasonal opportunity, competitor move, etc.\n"
            "- angle: 2-3 punchy sentences. Why them. Why ZYNTH. What gap we fill.\n"
            "- outreach_message: exact copy-paste ready DM or email opening — "
            "references something specific, never generic\n"
            "- expected_move: what we propose as next step\n"
            "- suggested_services: list of specific ZYNTH services to pitch\n"
            "- budget_estimate: realistic monthly spend range for their size\n"
        )

        if qa_feedback:
            prompt += f"\n\nQA feedback — address this directly: {qa_feedback}"

        return prompt
