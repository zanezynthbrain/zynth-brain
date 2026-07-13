"""Event Specialist Team — ConceptPlanner + Designer + Ops/Vendor + merger.

Pipeline (run_event_pipeline):
  1. Three specialists run IN PARALLEL on the cheap model (drafts):
       - EventConceptPlannerAgent  → theme, big idea, programme
       - EventDesignerAgent        → spatial/staging design + Blender MCP block
       - EventOpsVendorAgent       → run-of-show, vendors, budget lines, risks
  2. One merge call on the primary model produces the client-grade
     8-section proposal (docgen-compatible), priced at MARKET FX.

HITL: the bot presents the document with Approve / Revise buttons; on
revise, MD feedback is passed back into every specialist for the next
cycle (max 3 cycles, enforced by the bot).
"""

from __future__ import annotations

import asyncio
from typing import Any

from agents.base import BaseAgent
from agents.master_proposal import SECTION_NAMES
from config import get_settings
from utils.state import SharedMemory
from utils.venues import venues_block


def _feedback_note(feedback: str) -> str:
    if not feedback:
        return ""
    return (
        f"\n\nMD REVISION FEEDBACK (cycle revision — address this directly, "
        f"keep what wasn't criticised): {feedback}"
    )


class EventConceptPlannerAgent(BaseAgent):
    agent_key = "event_concept"
    display_name = "Event Concept Planner"
    role_description = (
        "You are ZYNTH's Event Concept Planner. You turn a brief into a theme, "
        "a big idea, an audience journey, and a programme outline that a client "
        "instantly understands and wants. Concrete over clever; every wow moment "
        "must be producible in Yangon or Singapore at realistic cost."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["theme", "big_idea", "programme_outline", "wow_moments"],
        "properties": {
            "theme": {"type": "string"},
            "big_idea": {"type": "string", "description": "2-3 sentences"},
            "audience_journey": {"type": "array", "items": {"type": "string"}, "minItems": 3},
            "programme_outline": {"type": "array", "items": {"type": "string"}, "minItems": 4},
            "wow_moments": {"type": "array", "items": {"type": "string"}, "minItems": 2},
            "format_notes": {"type": "string"},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return (
            f"EVENT BRIEF: {kwargs.get('brief', '')}\n\n"
            "Develop the concept: theme, big idea, audience journey (arrival to exit), "
            "programme outline with rough timings, 2-3 producible wow moments, format notes."
            + _feedback_note(kwargs.get("feedback", ""))
        )


class EventDesignerAgent(BaseAgent):
    agent_key = "event_designer"
    display_name = "Event Designer"
    role_description = (
        "You are ZYNTH's Event Designer. You direct the spatial and visual "
        "experience: zones, staging, LED, lighting, materials. You specify like "
        "a professional (LED pixel pitch, stage dimensions, rigging vs ground "
        "support) and design within the venue's real constraints. You also "
        "write a Blender MCP block so the MD can render the stage in 3D."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["spatial_concept", "zones", "staging_spec", "blender_block"],
        "properties": {
            "spatial_concept": {"type": "string"},
            "zones": {"type": "array", "items": {"type": "string"}, "minItems": 3},
            "staging_spec": {
                "type": "object",
                "properties": {
                    "stage": {"type": "string", "description": "dimensions + build method"},
                    "led": {"type": "string", "description": "size + pixel pitch"},
                    "sound": {"type": "string"},
                    "lighting": {"type": "string"},
                },
            },
            "materials": {"type": "array", "items": {"type": "string"}},
            "mood_keywords": {"type": "array", "items": {"type": "string"}},
            "blender_block": {
                "type": "string",
                "description": (
                    "Ready-to-paste instructions for Claude Desktop with Blender MCP: "
                    "scene setup, stage geometry with dimensions in metres, LED wall "
                    "placement, camera angle, simple materials/colors. Imperative, step-by-step."
                ),
            },
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return (
            f"EVENT BRIEF: {kwargs.get('brief', '')}\n"
            f"{venues_block(1500)}\n\n"
            "Design the space: zones, staging spec (stage size, LED with pixel pitch, "
            "sound, lighting), materials (note sustainable options), mood keywords, and "
            "the Blender MCP block for a 3D preview of the main stage."
            + _feedback_note(kwargs.get("feedback", ""))
        )


class EventOpsVendorAgent(BaseAgent):
    agent_key = "event_ops"
    display_name = "Event Operations & Vendor Manager"
    role_description = (
        "You are ZYNTH's Event Operations & Vendor Manager. You produce the "
        "run-of-show, staffing plan, vendor shortlist from the vendor database, "
        "itemised budget at MARKET FX (sell side), permits and risk register. "
        "Every unverified rate is tagged 'to be confirmed'. Contingency 10% "
        "always. 50% deposit clause always."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["run_of_show", "vendor_shortlist", "budget_lines", "risks"],
        "properties": {
            "run_of_show": {"type": "array", "items": {"type": "string"}, "minItems": 5},
            "staffing": {"type": "array", "items": {"type": "string"}},
            "vendor_shortlist": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["category", "recommendation"],
                    "properties": {
                        "category": {"type": "string"},
                        "recommendation": {"type": "string"},
                        "est_cost": {"type": "string"},
                    },
                },
            },
            "budget_lines": {
                "type": "array",
                "minItems": 6,
                "items": {
                    "type": "object",
                    "required": ["item", "amount"],
                    "properties": {
                        "item": {"type": "string"},
                        "amount": {"type": "string", "description": "with currency, e.g. 'MMK 12,000,000'"},
                    },
                },
            },
            "risks": {"type": "array", "items": {"type": "string"}, "minItems": 3},
            "timeline_weeks": {"type": "integer"},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return (
            f"EVENT BRIEF: {kwargs.get('brief', '')}\n"
            f"{venues_block(1500)}\n\n"
            "Produce operations: run-of-show (load-in to strike, with times), staffing, "
            "vendor shortlist by category from the vendor database, itemised budget lines "
            "(local currency at market FX, include 10% contingency line), permits/risks, "
            "timeline in weeks."
            + _feedback_note(kwargs.get("feedback", ""))
        )


_MERGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "client", "market", "estimated_value", "sections"],
    "properties": {
        "title": {"type": "string"},
        "client": {"type": "string"},
        "market": {"type": "string"},
        "estimated_value": {"type": "string"},
        "sections": {
            "type": "array",
            "minItems": 8,
            "maxItems": 8,
            "items": {
                "type": "object",
                "required": ["heading", "body"],
                "properties": {
                    "heading": {"type": "string"},
                    "body": {"type": "string", "description": "client-grade prose, 150-400 words, \\n\\n paragraphs, '- ' bullets, NO emoji"},
                },
            },
        },
    },
}


async def run_event_pipeline(
    brief: str,
    memory: SharedMemory,
    feedback: str = "",
    cycle: int = 1,
) -> dict[str, Any]:
    """Full event-team cycle: 3 parallel specialists (cheap) + 1 merge (primary).

    Returns {title, client, market, estimated_value, sections, blender_block,
    specialist_outputs, cycle}.
    """
    settings = get_settings()
    concept = EventConceptPlannerAgent()
    designer = EventDesignerAgent()
    ops = EventOpsVendorAgent()

    async def _run(agent: BaseAgent) -> dict:
        prompt = await agent.build_user_prompt(memory, brief=brief, feedback=feedback)
        data, response = await agent.llm.complete_json(
            system=agent.build_system_prompt(),
            user_prompt=prompt,
            schema=agent.output_schema,
            model=settings.fallback_model_name,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        await memory.set(agent.agent_key, data)
        return data

    concept_out, design_out, ops_out = await asyncio.gather(
        _run(concept), _run(designer), _run(ops)
    )

    # Merge on the primary model — this is the client-facing artifact
    section_list = "\n".join(f"{i}. {n}" for i, n in enumerate(SECTION_NAMES, 1))
    merge_prompt = (
        f"EVENT BRIEF: {brief}\n\n"
        f"CONCEPT TEAM OUTPUT:\n{concept_out}\n\n"
        f"DESIGN TEAM OUTPUT (exclude the blender_block from the client doc):\n"
        f"{ {k: v for k, v in design_out.items() if k != 'blender_block'} }\n\n"
        f"OPERATIONS TEAM OUTPUT:\n{ops_out}\n\n"
        f"Merge into ONE cohesive client-ready event proposal with exactly these "
        f"eight sections:\n{section_list}\n\n"
        "Rules: resolve any contradictions between teams in favour of feasibility; "
        "budget section itemised at MARKET FX with 10% contingency and the 50% "
        "deposit clause; unverified vendor/venue figures tagged 'to be confirmed'; "
        "client-grade prose, no emoji."
        + _feedback_note(feedback)
    )
    merger = EventConceptPlannerAgent()  # reuse brand+knowledge system prompt shell
    merger.role_description = (
        "You are ZYNTH's senior event proposal writer assembling specialist team "
        "outputs into one flawless client document to the ZYNTH standard."
    )
    data, response = await merger.llm.complete_json(
        system=merger.build_system_prompt(),
        user_prompt=merge_prompt,
        schema=_MERGE_SCHEMA,
        max_tokens=8000,
    )
    await memory.record_tokens(response.input_tokens, response.output_tokens)

    data["blender_block"] = design_out.get("blender_block", "")
    data["specialist_outputs"] = {
        "concept": concept_out,
        "design": design_out,
        "ops": ops_out,
    }
    data["cycle"] = cycle
    return data
