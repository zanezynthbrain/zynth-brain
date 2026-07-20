"""Video Production pipeline — a working implementation of the multi-specialist
video system (Creative Director → Storyboard → Pre-Production → Post-Production)
as ONE cost-controlled, schema-validated production package.

Built on ZYNTH's real BaseAgent/LLMClient (unlike a stub): a single high-quality
call on the primary model, with the real Myanmar production knowledge base and
live market FX injected, producing a bilingual (EN + Myanmar) client-ready
package that renders to a premium .docx.

Deep interactive craft + storyboard image rendering stays in the
`zynth-creative-video-director` Claude skill; this is the bot's productised
"give me a full production package" path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory

_KB_PATH = Path(__file__).resolve().parent.parent / "data" / "video_production_mm.md"
_kb_cache: str | None = None


def _kb() -> str:
    global _kb_cache
    if _kb_cache is None:
        try:
            _kb_cache = _KB_PATH.read_text(encoding="utf-8")
        except Exception:
            _kb_cache = ""
    return _kb_cache


_SHOT = {
    "type": "object",
    "required": ["shot", "framing", "action"],
    "properties": {
        "shot": {"type": "integer"},
        "framing": {"type": "string", "description": "shot size + angle, e.g. 'CU, low angle'"},
        "movement": {"type": "string"},
        "action": {"type": "string"},
        "specs": {"type": "string", "description": "lens / aspect / lighting note"},
        "audio": {"type": "string"},
        "duration": {"type": "string"},
    },
}

_BUDGET_ROW = {
    "type": "object",
    "required": ["item", "total_mmk"],
    "properties": {
        "item": {"type": "string"},
        "qty": {"type": "string"},
        "unit_mmk": {"type": "string"},
        "total_mmk": {"type": "string"},
        "note": {"type": "string"},
    },
}

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["title", "scale", "creative", "storyboard", "preproduction", "postproduction"],
    "properties": {
        "title": {"type": "string"},
        "client": {"type": "string"},
        "market": {"type": "string"},
        "scale": {"type": "string", "description": "tiktok / commercial / brand film"},
        "one_line_ask": {"type": "string"},
        "estimated_value": {"type": "string", "description": "total production budget, e.g. 'MMK 42,000,000'"},
        "creative": {
            "type": "object",
            "required": ["concept_name", "hook", "narrative", "script_en", "script_mm"],
            "properties": {
                "concept_name": {"type": "string"},
                "target_audience": {"type": "string"},
                "hook": {"type": "string", "description": "the first-1.5s / first-3s hook"},
                "narrative": {"type": "string"},
                "emotional_arc": {"type": "string"},
                "script_en": {"type": "string", "description": "full AV script in English (visual + VO/dialogue)"},
                "script_mm": {"type": "string", "description": "the script in Myanmar Unicode (Pyidaungsu), transcreated not translated"},
                "audio_direction": {"type": "string"},
            },
        },
        "storyboard": {
            "type": "object",
            "required": ["shots"],
            "properties": {
                "shots": {"type": "array", "minItems": 3, "items": _SHOT},
                "visual_style": {"type": "string"},
                "color_palette": {"type": "string"},
                "lighting": {"type": "string"},
                "transitions": {"type": "string"},
            },
        },
        "preproduction": {
            "type": "object",
            "required": ["budget_mmk"],
            "properties": {
                "schedule": {"type": "string"},
                "locations": {"type": "string"},
                "equipment": {"type": "string"},
                "casting": {"type": "string"},
                "budget_mmk": {"type": "array", "minItems": 3, "items": _BUDGET_ROW},
                "budget_total_mmk": {"type": "string"},
            },
        },
        "postproduction": {
            "type": "object",
            "required": ["edit_direction"],
            "properties": {
                "edit_direction": {"type": "string"},
                "davinci_resolve": {"type": "string"},
                "premiere_pro": {"type": "string"},
                "after_effects": {"type": "string"},
                "capcut": {"type": "string"},
                "color_workflow": {"type": "string"},
                "sound_design": {"type": "string"},
                "vfx": {"type": "string"},
                "delivery": {"type": "string"},
            },
        },
    },
}


class MasterVideoAgent(BaseAgent):
    """Produces a complete, bilingual video production package."""

    agent_key = "video_master"
    display_name = "Video Production Lead"
    role_description = (
        "You are ZYNTH's video production lead — creative director, storyboard artist, "
        "line producer and post supervisor in one. You turn a brief into a complete, "
        "executable production package for the Myanmar/Singapore market: concept + "
        "bilingual script, a shot-by-shot storyboard, a real MMK pre-production budget, "
        "and a professional post-production guide (DaVinci Resolve, Premiere, After "
        "Effects, CapCut). You price on real local rates, respect the 35% margin floor "
        "and the 10% contingency, and never present an unverified vendor rate as fact."
    )
    output_schema: dict[str, Any] = _SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return self._prompt(kwargs.get("brief", ""), kwargs.get("scale", "commercial"))

    @staticmethod
    def _prompt(brief: str, scale: str) -> str:
        from utils.fx import rates_block
        return (
            f"Produce a COMPLETE video production package for this brief:\n\n"
            f"BRIEF: {brief}\nSCALE: {scale} (tiktok = 9:16 social hook-first; commercial = "
            f"15/30/60s TVC; brand film = 60-120s)\n"
            f"{rates_block()}\n\n"
            "===== MYANMAR PRODUCTION KNOWLEDGE (use for budget & logistics) =====\n"
            f"{_kb()}\n===== END KNOWLEDGE =====\n\n"
            "Deliver ALL of: \n"
            "1. CREATIVE — concept, target audience, the hook (first 1.5-3s), narrative, "
            "emotional arc, a FULL AV script in English (visual + VO/dialogue), the SAME "
            "script transcreated into Myanmar Unicode (Pyidaungsu — natural, not literal), "
            "and audio direction.\n"
            "2. STORYBOARD — a shot-by-shot list (framing/angle, movement, action, lens/"
            "aspect spec, audio, duration), visual style, colour palette, lighting, transitions.\n"
            "3. PRE-PRODUCTION — schedule, locations (+ permit/censorship notes), equipment, "
            "casting, and an itemised budget table in MMK at the MARKET rate using the crew/"
            "equipment rates above (tag rates 'indicative — RFQ'), with a 10% contingency and "
            "a total. Give the total as estimated_value.\n"
            "4. POST-PRODUCTION — edit direction, plus specific guidance for DaVinci Resolve "
            "(node order), Premiere Pro, After Effects and CapCut; colour workflow; sound "
            "design; VFX; and delivery specs per platform (aspect/res/fps/LUFS).\n"
            "Also write one_line_ask: who + what + budget + the one result. Client-grade, "
            "no emoji, no coding jargon. Respect Myanmar cultural etiquette."
        )

    async def run(self, brief: str, scale: str, memory: SharedMemory) -> dict[str, Any]:
        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=self._prompt(brief, scale),
            schema=_SCHEMA,
            max_tokens=14000,
        )
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        return data


async def run_video_pipeline(brief: str, memory: SharedMemory, scale: str = "commercial") -> dict[str, Any]:
    from utils.llm_client import LLMClient
    agent = MasterVideoAgent(llm_client=LLMClient())
    return await agent.run(brief, scale, memory)


def package_to_sections(pkg: dict[str, Any]) -> list[dict[str, Any]]:
    """Map the production package into docgen sections (premium .docx)."""
    c = pkg.get("creative", {})
    sb = pkg.get("storyboard", {})
    pre = pkg.get("preproduction", {})
    post = pkg.get("postproduction", {})

    def _p(*parts: str) -> str:
        return "\n\n".join(p for p in parts if p)

    # 1. Creative & script
    creative_body = _p(
        f"Concept: {c.get('concept_name', '')}",
        f"Audience: {c.get('target_audience', '')}" if c.get("target_audience") else "",
        f"Hook: {c.get('hook', '')}" if c.get("hook") else "",
        f"Narrative: {c.get('narrative', '')}" if c.get("narrative") else "",
        f"Emotional arc: {c.get('emotional_arc', '')}" if c.get("emotional_arc") else "",
        f"Audio direction: {c.get('audio_direction', '')}" if c.get("audio_direction") else "",
        "— SCRIPT (English) —", c.get("script_en", ""),
        "— SCRIPT (Myanmar) —", c.get("script_mm", ""),
    )

    # 2. Storyboard shot table
    shots = sb.get("shots", []) or []
    shot_rows = [[
        str(s.get("shot", i + 1)), s.get("framing", ""), s.get("movement", ""),
        s.get("action", ""), s.get("specs", ""), s.get("audio", ""), s.get("duration", ""),
    ] for i, s in enumerate(shots)]
    sb_body = _p(
        f"Visual style: {sb.get('visual_style', '')}" if sb.get("visual_style") else "",
        f"Colour palette: {sb.get('color_palette', '')}" if sb.get("color_palette") else "",
        f"Lighting: {sb.get('lighting', '')}" if sb.get("lighting") else "",
        f"Transitions: {sb.get('transitions', '')}" if sb.get("transitions") else "",
    )
    sb_tables = [{
        "title": "Shot list",
        "headers": ["#", "Framing", "Movement", "Action", "Spec", "Audio", "Time"],
        "rows": shot_rows,
    }] if shot_rows else []

    # 3. Pre-production + budget
    budget = pre.get("budget_mmk", []) or []
    budget_rows = [[b.get("item", ""), b.get("qty", ""), b.get("unit_mmk", ""),
                    b.get("total_mmk", ""), b.get("note", "")] for b in budget]
    pre_body = _p(
        f"Schedule: {pre.get('schedule', '')}" if pre.get("schedule") else "",
        f"Locations: {pre.get('locations', '')}" if pre.get("locations") else "",
        f"Equipment: {pre.get('equipment', '')}" if pre.get("equipment") else "",
        f"Casting: {pre.get('casting', '')}" if pre.get("casting") else "",
        f"Total (MMK): {pre.get('budget_total_mmk', '')}" if pre.get("budget_total_mmk") else "",
    )
    pre_tables = [{
        "title": "Production budget (MMK, indicative — confirm by RFQ)",
        "headers": ["Item", "Qty", "Unit (MMK)", "Total (MMK)", "Note"],
        "rows": budget_rows,
    }] if budget_rows else []

    # 4. Post-production
    post_body = _p(
        f"Edit direction: {post.get('edit_direction', '')}" if post.get("edit_direction") else "",
        f"DaVinci Resolve: {post.get('davinci_resolve', '')}" if post.get("davinci_resolve") else "",
        f"Premiere Pro: {post.get('premiere_pro', '')}" if post.get("premiere_pro") else "",
        f"After Effects: {post.get('after_effects', '')}" if post.get("after_effects") else "",
        f"CapCut: {post.get('capcut', '')}" if post.get("capcut") else "",
        f"Colour workflow: {post.get('color_workflow', '')}" if post.get("color_workflow") else "",
        f"Sound design: {post.get('sound_design', '')}" if post.get("sound_design") else "",
        f"VFX: {post.get('vfx', '')}" if post.get("vfx") else "",
        f"Delivery: {post.get('delivery', '')}" if post.get("delivery") else "",
    )

    return [
        {"heading": "Creative Concept & Script (EN + Myanmar)", "body": creative_body, "tables": []},
        {"heading": "Storyboard & Shot List", "body": sb_body, "tables": sb_tables},
        {"heading": "Pre-Production & Budget (MMK)", "body": pre_body, "tables": pre_tables},
        {"heading": "Post-Production Guide", "body": post_body, "tables": []},
    ]
