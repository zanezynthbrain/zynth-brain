"""Content & Design Studio — the team that writes and designs a brand's month.

Four specialists, one pipeline (``run_content_studio``):

  1. BrandStrategistAgent  — brand strategy + owned-channel strategy: the
     positioning, the messaging house, the audience insight, the content
     pillars with weightings, and what each channel is FOR. Runs first,
     on the primary model, because everything downstream inherits it.
  2. ContentCreatorAgent   — the month's calendar: every post with hook,
     caption (English + Myanmar), hashtags, CTA and a design handoff note.
     Volume and content-type mix come from the package, not from the model.
  3. DesignDirectorAgent   — the visual system: art direction, palette, type,
     templates, layout rules, per-format specs. Runs in PARALLEL with the
     content creator (both take the strategy as input).
  4. DesignerAgent         — per-asset design specs and render prompts for the
     posts the package says get original design work.

Collaboration with the rest of the agency happens through SharedMemory, the
same as every other ZYNTH pipeline: this studio READS ``cmo`` (campaign plan),
``research_seo`` (keywords, competitor intel) and ``paid_ads`` (what's being
boosted) when they're present, and WRITES its own namespaces so the campaign
planner, paid-ads and portfolio agents can build on the calendar. See
``orchestrator.WORKFLOWS['content_studio' | 'brand_content_month']``.

Cost shape per month-plan: 1 primary-model call (strategy) + 3 cheap-model
calls (content, design system, design specs). The calendar is the expensive
part by token count, so it runs on the fallback model with a hard structure.
"""

from __future__ import annotations

import asyncio
from typing import Any

from agents.base import BaseAgent
from config import get_settings
from config.content_packages import CONTENT_TYPES, ContentPackage, resolve_package
from utils.brands import brand_block
from utils.state import SharedMemory


def _feedback_note(feedback: str) -> str:
    if not feedback:
        return ""
    return (
        f"\n\nMD REVISION FEEDBACK (address this directly, keep what wasn't "
        f"criticised): {feedback}"
    )


async def _agency_context(memory: SharedMemory, max_chars: int = 2200) -> str:
    """Pull whatever the rest of the agency has already produced this run.

    The studio is not an island: if the campaign planner (CMO), the research
    agent, or paid ads have run, their output steers the month. Missing
    upstream agents are simply absent — never faked.
    """
    parts: list[str] = []
    for key, label in (
        ("campaign_plan", "CAMPAIGN PLAN (from the campaign planner — the content must serve it)"),
        ("cmo", "CMO / CAMPAIGN DIRECTION"),
        ("research_seo", "MARKET RESEARCH & SEO (keywords, competitors, angles)"),
        ("paid_ads", "PAID MEDIA PLAN (what gets boosted)"),
        ("event_concept", "LINKED EVENT CONCEPT (content should build toward it)"),
    ):
        data = await memory.get(key, None)
        if data:
            parts.append(f"--- {label} ---\n{data}")
    if not parts:
        return ""
    block = "\n\n".join(parts)
    if len(block) > max_chars:
        block = block[:max_chars] + "\n…(agency context truncated)"
    return (
        "\n===== WHAT THE REST OF THE AGENCY HAS ALREADY DECIDED =====\n"
        f"{block}\n"
        "Align to this. Where you disagree, say so in open_questions rather than "
        "silently contradicting it.\n"
        "===== END AGENCY CONTEXT =====\n"
    )


# ---------------------------------------------------------------------------
# 1. Brand + owned-channel strategist
# ---------------------------------------------------------------------------

class BrandStrategistAgent(BaseAgent):
    """Sets the brand platform and the owned-channel strategy the month runs on."""

    agent_key = "brand_strategist"
    display_name = "Brand & Owned-Channel Strategist"
    role_description = (
        "You are ZYNTH's Brand Strategist. You decide what a brand stands for and how "
        "it shows up on the channels it owns. You produce a brand platform (positioning, "
        "promise, personality, tone), a messaging house, a sharp audience insight, and "
        "the owned-channel strategy: content pillars with percentage weightings, the job "
        "each platform does, posting cadence, and the growth thesis for the next 90 days. "
        "You are specific to THIS brand and THIS market — a strategy that could be pasted "
        "onto a competitor is a failed strategy."
    )
    #: Strategy is the one call that stays on the primary model — everything
    #: downstream inherits it, so it is the wrong place to save money.
    max_output_tokens = 8000
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": [
            "brand_platform", "audience", "content_pillars",
            "channel_strategy", "owned_strategy", "kpis",
        ],
        "properties": {
            "brand_platform": {
                "type": "object",
                "required": ["positioning", "promise", "personality", "tone_of_voice"],
                "properties": {
                    "positioning": {"type": "string", "description": "one sentence: for whom, what, unlike whom"},
                    "promise": {"type": "string"},
                    "personality": {"type": "array", "items": {"type": "string"}, "minItems": 3},
                    "tone_of_voice": {"type": "string"},
                    "tagline_options": {"type": "array", "items": {"type": "string"}},
                    "do_not": {"type": "array", "items": {"type": "string"}},
                },
            },
            "audience": {
                "type": "object",
                "required": ["primary", "insight"],
                "properties": {
                    "primary": {"type": "string"},
                    "segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "profile", "trigger"],
                            "properties": {
                                "name": {"type": "string"},
                                "profile": {"type": "string", "description": "age, role, platform habits, income signal"},
                                "trigger": {"type": "string", "description": "what makes them act now"},
                                "objection": {"type": "string"},
                            },
                        },
                    },
                    "insight": {"type": "string", "description": "the tension the brand resolves — not a demographic"},
                },
            },
            "messaging_house": {
                "type": "object",
                "properties": {
                    "core_message": {"type": "string"},
                    "pillars": {"type": "array", "items": {"type": "string"}},
                    "proof_points": {"type": "array", "items": {"type": "string"}},
                },
            },
            "content_pillars": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["name", "purpose", "share_pct", "example_topics"],
                    "properties": {
                        "name": {"type": "string"},
                        "purpose": {"type": "string", "description": "what this pillar is for commercially"},
                        "share_pct": {"type": "integer", "description": "share of the month's posts; all pillars sum to 100"},
                        "example_topics": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                        "success_signal": {"type": "string"},
                    },
                },
            },
            "channel_strategy": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["platform", "role", "format_focus", "cadence"],
                    "properties": {
                        "platform": {"type": "string"},
                        "role": {"type": "string", "description": "the job this channel does in the funnel"},
                        "format_focus": {"type": "string"},
                        "cadence": {"type": "string"},
                        "best_times": {"type": "string"},
                    },
                },
            },
            "owned_strategy": {
                "type": "object",
                "required": ["thesis", "ninety_day_arc"],
                "properties": {
                    "thesis": {"type": "string", "description": "how owned channels compound into growth"},
                    "ninety_day_arc": {"type": "array", "items": {"type": "string"}, "minItems": 3,
                                        "description": "month 1, 2, 3 — what each month is for"},
                    "community_plan": {"type": "string", "description": "comments, DMs, response SLA"},
                    "organic_paid_handshake": {"type": "string", "description": "which organic winners get boosted and on what trigger"},
                },
            },
            "kpis": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["metric", "target", "why"],
                    "properties": {
                        "metric": {"type": "string"},
                        "target": {"type": "string"},
                        "why": {"type": "string"},
                    },
                },
            },
            "open_questions": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        brand_name = kwargs.get("brand", "")
        brief = kwargs.get("brief", "")
        package: ContentPackage = kwargs.get("package") or resolve_package(None)
        context = await _agency_context(memory)
        return (
            f"BRAND: {brand_name or 'see brief'}\n"
            f"BRIEF: {brief}\n"
            f"{brand_block(brand_name)}"
            f"{context}\n"
            f"{package.as_prompt_block()}\n\n"
            "Produce the strategy this month's content will be built on:\n"
            "1. BRAND PLATFORM — positioning (for whom / what / unlike whom), promise, "
            "3-5 personality traits, tone of voice, tagline options, and what this brand "
            "must never say or look like.\n"
            "2. AUDIENCE — the primary audience in plain language, 2-3 segments with real "
            "platform habits and buying triggers, and ONE sharp insight: the tension the "
            "brand resolves. Demographics alone are not an insight.\n"
            "3. MESSAGING HOUSE — core message, supporting pillars, proof points.\n"
            "4. CONTENT PILLARS — 3-5 pillars with a commercial purpose each and a "
            "share_pct that sums to exactly 100 across all pillars.\n"
            "5. CHANNEL STRATEGY — for each platform in the package: the job it does in "
            "the funnel, format focus, cadence, best posting times for this market.\n"
            "6. OWNED STRATEGY — the thesis for how owned channels compound, a 90-day arc "
            "(what months 1/2/3 are each for), the community/response plan, and the "
            "organic→paid handshake (which winners get boosted, on what trigger).\n"
            "7. KPIS — 3-5 metrics with targets that are realistic for this volume and market.\n"
            "Ground every choice in the brand profile and the market. Flag anything you had "
            "to assume under open_questions."
            + _feedback_note(kwargs.get("feedback", ""))
            + (f"\n\nQA feedback to address: {kwargs['qa_feedback']}" if kwargs.get("qa_feedback") else "")
        )


# ---------------------------------------------------------------------------
# 2. Content creator — the month's calendar
# ---------------------------------------------------------------------------

_POST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["ref", "week", "platform", "content_type", "pillar", "hook", "caption_en", "cta"],
    "properties": {
        "ref": {"type": "string", "description": "stable id like P01 — the design spec references this"},
        "week": {"type": "integer", "description": "1-4"},
        "day": {"type": "string", "description": "e.g. 'Mon' or 'Week 2, Tue'"},
        "platform": {"type": "string"},
        "content_type": {"type": "string", "enum": CONTENT_TYPES},
        "pillar": {"type": "string"},
        "objective": {"type": "string", "description": "awareness / consideration / conversion / community"},
        "hook": {"type": "string", "description": "the first line or first 1.5s — must stop the scroll"},
        "caption_en": {"type": "string"},
        "caption_mm": {"type": "string", "description": "Myanmar Unicode (Pyidaungsu), transcreated not translated"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "cta": {"type": "string"},
        "needs_design": {"type": "boolean", "description": "true if this post needs an original designed asset"},
        "design_note": {"type": "string", "description": "the handoff to the designer: what the visual must do"},
        "asset_source": {"type": "string", "description": "designed / client photo / shoot / UGC / stock"},
        "boost": {"type": "boolean", "description": "flagged for paid amplification"},
    },
}

_CONTENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["month_theme", "posts", "story_plan"],
    "properties": {
        "month_theme": {"type": "string", "description": "the single idea holding the month together"},
        "posts": {"type": "array", "minItems": 1, "items": _POST_SCHEMA},
        "story_plan": {"type": "array", "items": {"type": "string"},
                        "description": "one line per story set: what it covers and when"},
        "series_ideas": {"type": "array", "items": {"type": "string"},
                          "description": "repeatable formats worth running every month"},
        "community_prompts": {"type": "array", "items": {"type": "string"},
                               "description": "reply/DM angles for the community manager"},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
}


class ContentCreatorAgent(BaseAgent):
    """Writes the month: every post, in both languages, ready to schedule."""

    agent_key = "content_creator"
    display_name = "Content Creator"
    role_description = (
        "You are ZYNTH's Content Creator. You write a full month of social content that "
        "a scheduler can publish without rewriting: scroll-stopping hooks, captions in "
        "English and natural Myanmar, the right hashtags, and one clear CTA per post. "
        "You write to the strategy you are given — the pillars, the audience insight and "
        "the brand's tone are constraints, not suggestions. You never pad the month with "
        "filler: if a post has no job, it does not exist."
    )
    #: A 30-post month with bilingual captions is the longest output the
    #: agency produces; the default 4k budget truncates it mid-JSON.
    max_output_tokens = 16000
    use_fallback_model = True
    output_schema: dict[str, Any] = _CONTENT_SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        brand_name = kwargs.get("brand", "")
        brief = kwargs.get("brief", "")
        package: ContentPackage = kwargs.get("package") or resolve_package(None)
        strategy = kwargs.get("strategy") or await memory.get("brand_strategist", {})
        month = kwargs.get("month", "next month")
        context = await _agency_context(memory, max_chars=1500)
        mix = "\n".join(f"  - {count}× {name}" for name, count in package.type_mix.items() if count)
        return (
            f"BRAND: {brand_name or 'see brief'}\nMONTH: {month}\nBRIEF: {brief}\n"
            f"{brand_block(brand_name, max_chars=1800)}"
            f"{context}\n"
            "===== APPROVED STRATEGY (obey the pillars and their weightings) =====\n"
            f"{strategy}\n===== END STRATEGY =====\n\n"
            f"{package.as_prompt_block()}\n\n"
            f"Write EXACTLY {package.posts_per_month} posts — no more, no fewer — matching "
            f"this content-type mix exactly:\n{mix}\n\n"
            f"Set needs_design=true on EXACTLY {package.designed_assets} of them (the ones "
            f"where an original designed asset does the work); the remaining "
            f"{package.copy_only_posts} are photo/UGC/copy-led with light treatment only. "
            f"Flag exactly {package.boosted_posts} posts with boost=true — pick the ones "
            "most likely to earn paid amplification.\n\n"
            "For every post give: ref (P01, P02, …), week (1-4), day, platform, "
            "content_type, pillar, objective, hook, caption_en, caption_mm (Myanmar "
            "Unicode — transcreated so it reads like a Myanmar person wrote it, never a "
            "literal translation), hashtags, cta, needs_design, design_note (what the "
            "visual must DO, written for the designer), asset_source, boost.\n\n"
            "Spread pillars across the month in the strategy's weightings, spread posts "
            "evenly across weeks 1-4, and vary the hooks — if two hooks share a formula, "
            "rewrite one. Also give: a month_theme, the story plan "
            f"({package.story_sets} sets), repeatable series ideas, and community prompts."
            + _feedback_note(kwargs.get("feedback", ""))
            + (f"\n\nQA feedback to address: {kwargs['qa_feedback']}" if kwargs.get("qa_feedback") else "")
        )


# ---------------------------------------------------------------------------
# 3. Design director — the visual system
# ---------------------------------------------------------------------------

class DesignDirectorAgent(BaseAgent):
    """Sets the visual system every asset in the month is built from."""

    agent_key = "design_director"
    display_name = "Design Director"
    role_description = (
        "You are ZYNTH's Design Director. You define the visual system a month of content "
        "is built from: art direction, colour with real hex values, type hierarchy with "
        "sizes, grid and safe areas, template set, photography/illustration direction, and "
        "the rules that keep 30 posts looking like one brand. You respect an existing brand "
        "kit when there is one and say clearly when you are proposing an evolution. You "
        "specify like a professional — a freelancer should be able to build from your spec "
        "without asking you a question."
    )
    max_output_tokens = 6000
    use_fallback_model = True
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["art_direction", "palette", "typography", "templates", "layout_rules"],
        "properties": {
            "art_direction": {"type": "string", "description": "the visual world in 3-5 sentences"},
            "mood_keywords": {"type": "array", "items": {"type": "string"}, "minItems": 3},
            "palette": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["name", "hex", "use"],
                    "properties": {
                        "name": {"type": "string"},
                        "hex": {"type": "string", "description": "#RRGGBB"},
                        "use": {"type": "string", "description": "where it may and may not be used"},
                    },
                },
            },
            "typography": {
                "type": "object",
                "required": ["headline", "body"],
                "properties": {
                    "headline": {"type": "string", "description": "typeface + weight + size range + case"},
                    "body": {"type": "string"},
                    "myanmar": {"type": "string", "description": "Myanmar typeface + line-height note (Pyidaungsu safe)"},
                    "hierarchy_rules": {"type": "string"},
                },
            },
            "templates": {
                "type": "array",
                "minItems": 3,
                "items": {
                    "type": "object",
                    "required": ["name", "use_for", "layout"],
                    "properties": {
                        "name": {"type": "string"},
                        "use_for": {"type": "string", "description": "which content types use this template"},
                        "layout": {"type": "string", "description": "grid, image/text split, logo placement, safe areas"},
                        "dimensions": {"type": "string", "description": "e.g. 1080×1350 (4:5)"},
                    },
                },
            },
            "layout_rules": {"type": "array", "items": {"type": "string"}, "minItems": 3,
                              "description": "the non-negotiables that hold the system together"},
            "photography_direction": {"type": "string"},
            "graphic_devices": {"type": "array", "items": {"type": "string"},
                                 "description": "recurring shapes, frames, textures, motion signatures"},
            "accessibility": {"type": "string", "description": "contrast ratios, min text size, caption/subtitle rules"},
            "asset_checklist": {"type": "array", "items": {"type": "string"},
                                 "description": "what the client must supply (logo files, product shots, fonts)"},
            "open_questions": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        brand_name = kwargs.get("brand", "")
        brief = kwargs.get("brief", "")
        package: ContentPackage = kwargs.get("package") or resolve_package(None)
        strategy = kwargs.get("strategy") or await memory.get("brand_strategist", {})
        return (
            f"BRAND: {brand_name or 'see brief'}\nBRIEF: {brief}\n"
            f"{brand_block(brand_name, max_chars=1800)}\n"
            "===== APPROVED STRATEGY (the visuals must express this) =====\n"
            f"{strategy}\n===== END STRATEGY =====\n\n"
            f"{package.as_prompt_block()}\n\n"
            "Define the visual system for the month:\n"
            "1. ART DIRECTION — the visual world, and mood keywords.\n"
            "2. PALETTE — 3-6 colours with real hex values and rules for where each may "
            "and may not be used. If the brand profile has colours, build on them; if you "
            "propose an evolution, say so explicitly.\n"
            "3. TYPOGRAPHY — headline and body typefaces with weights, size ranges and "
            "case rules, a Myanmar typeface note (Pyidaungsu-safe, line-height for stacked "
            "diacritics), and the hierarchy rules.\n"
            "4. TEMPLATES — at least 3, each with what it's used for, its layout (grid, "
            "image/text split, logo placement, safe areas) and exact dimensions per "
            "platform format.\n"
            "5. LAYOUT RULES — the non-negotiables that make 8-30 posts read as one brand.\n"
            "6. PHOTOGRAPHY DIRECTION, graphic devices, accessibility (contrast ratios, "
            "minimum text size, subtitle rules for video), and the asset checklist the "
            "client must supply.\n"
            "Specific over pretty. No unnamed 'modern, clean, minimal' — say what it "
            "actually looks like."
            + _feedback_note(kwargs.get("feedback", ""))
            + (f"\n\nQA feedback to address: {kwargs['qa_feedback']}" if kwargs.get("qa_feedback") else "")
        )


# ---------------------------------------------------------------------------
# 4. Designer — per-asset specs + render prompts
# ---------------------------------------------------------------------------

_DESIGN_SPEC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["ref", "format", "template", "composition", "on_asset_text", "render_prompt"],
    "properties": {
        "ref": {"type": "string", "description": "matches the post ref, e.g. P01"},
        "format": {"type": "string", "description": "square / portrait / story / carousel / landscape + pixel size"},
        "template": {"type": "string", "description": "which template from the system"},
        "composition": {"type": "string", "description": "what is where: subject, hierarchy, focal point, negative space"},
        "on_asset_text": {
            "type": "object",
            "required": ["headline"],
            "properties": {
                "headline": {"type": "string", "description": "the words ON the artwork — short"},
                "subline": {"type": "string"},
                "myanmar": {"type": "string"},
                "cta_chip": {"type": "string"},
            },
        },
        "colour_use": {"type": "string"},
        "imagery": {"type": "string", "description": "photo/illustration/product — and where it comes from"},
        "frames": {"type": "array", "items": {"type": "string"},
                    "description": "for carousels: one line per frame, in order"},
        "motion_note": {"type": "string", "description": "for video: pacing, text animation, subtitle style"},
        "render_prompt": {
            "type": "string",
            "description": (
                "A complete image-generation prompt for this asset: subject, style, "
                "composition, palette by hex, lighting, mood, aspect. Describe the "
                "background/scene only — no logo, no long text baked in (text and logo "
                "are laid over in Canva/Figma)."
            ),
        },
        "production_note": {"type": "string", "description": "what a designer must do by hand after rendering"},
    },
}

_DESIGNER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["design_specs"],
    "properties": {
        "design_specs": {"type": "array", "minItems": 1, "items": _DESIGN_SPEC_SCHEMA},
        "hero_asset_ref": {"type": "string", "description": "the one asset that defines the month"},
        "production_order": {"type": "array", "items": {"type": "string"},
                              "description": "efficient build order — batch by template"},
        "estimated_design_hours": {"type": "string"},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
}


class DesignerAgent(BaseAgent):
    """Turns each post that needs design into a buildable spec + render prompt."""

    agent_key = "designer"
    display_name = "Designer"
    role_description = (
        "You are ZYNTH's Designer. You take the visual system and the month's posts and "
        "produce a buildable spec for every asset that needs original design: format and "
        "pixel size, which template, the composition, the exact words that sit ON the "
        "artwork, colour use, imagery source, carousel frames, motion notes — plus a "
        "complete image-generation prompt for the background/scene. You design for the "
        "platform's safe areas and for a thumb on a mid-range Android in bright daylight."
    )
    max_output_tokens = 14000
    use_fallback_model = True
    output_schema: dict[str, Any] = _DESIGNER_SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        brand_name = kwargs.get("brand", "")
        package: ContentPackage = kwargs.get("package") or resolve_package(None)
        design_system = kwargs.get("design_system") or await memory.get("design_director", {})
        content = kwargs.get("content") or await memory.get("content_creator", {})
        posts = content.get("posts", []) if isinstance(content, dict) else []
        needing = [p for p in posts if p.get("needs_design")] or posts
        brief_rows = "\n".join(
            f"- {p.get('ref', '?')} · {p.get('content_type', '?')} · {p.get('platform', '?')} · "
            f"pillar: {p.get('pillar', '?')} · hook: {p.get('hook', '')[:80]} · "
            f"design note: {p.get('design_note', '')[:120]}"
            for p in needing
        )
        return (
            f"BRAND: {brand_name or 'see brief'}\n"
            f"{brand_block(brand_name, max_chars=1200)}\n"
            "===== VISUAL SYSTEM (build inside it — do not invent new colours or type) =====\n"
            f"{design_system}\n===== END VISUAL SYSTEM =====\n\n"
            f"POSTS NEEDING ORIGINAL DESIGN ({len(needing)} of {package.posts_per_month}, "
            f"ratio {package.design_ratio}):\n{brief_rows}\n\n"
            "Produce one design spec per post above, keyed by the SAME ref. Each spec: "
            "format + exact pixel size for that platform, which template, composition "
            "(subject, hierarchy, focal point, negative space), the on-asset text "
            "(headline — short enough to read at thumbnail size — subline, Myanmar text, "
            "CTA chip), colour use by hex, imagery and where it comes from, carousel "
            "frames in order where relevant, motion notes for video (pacing, text "
            "animation, subtitle style), and a complete render_prompt for the "
            "background/scene.\n\n"
            "render_prompt rules: describe scene, style, composition, palette by hex, "
            "lighting, mood and aspect ratio. Never ask the generator for logos, long "
            "text, or brand marks — those are laid over by hand. Keep people generic "
            "unless the brand supplies talent.\n\n"
            "Also give the hero asset ref, an efficient production order (batch by "
            "template), and estimated design hours."
            + _feedback_note(kwargs.get("feedback", ""))
            + (f"\n\nQA feedback to address: {kwargs['qa_feedback']}" if kwargs.get("qa_feedback") else "")
        )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def _reconcile(content: dict[str, Any], package: ContentPackage) -> dict[str, Any]:
    """Make the calendar obey the package contract, whatever the model returned.

    The package — not the model — is the source of truth for volume, the
    content:design ratio and the boost count, because that's what the client
    is invoiced for. This trims/pads deterministically and records what it
    had to change so the MD sees it.
    """
    posts = list(content.get("posts") or [])
    adjustments: list[str] = []

    if len(posts) > package.posts_per_month:
        adjustments.append(f"Trimmed {len(posts) - package.posts_per_month} extra post(s) beyond the package.")
        posts = posts[: package.posts_per_month]
    elif len(posts) < package.posts_per_month:
        adjustments.append(
            f"Model returned {len(posts)} of {package.posts_per_month} posts — "
            f"{package.posts_per_month - len(posts)} slot(s) left open for the next cycle."
        )

    # Stable refs so design specs can key off them.
    for i, post in enumerate(posts, 1):
        post.setdefault("ref", f"P{i:02d}")
        post.setdefault("week", min(4, (i - 1) // max(1, round(package.posts_per_month / 4)) + 1))

    designed = [p for p in posts if p.get("needs_design")]
    if len(designed) > package.designed_assets:
        for post in designed[package.designed_assets:]:
            post["needs_design"] = False
            post.setdefault("asset_source", "client photo / UGC")
        adjustments.append(
            f"Reset {len(designed) - package.designed_assets} post(s) to copy-led to hold the "
            f"{package.design_ratio} content:design ratio."
        )
    elif len(designed) < package.designed_assets:
        shortfall = package.designed_assets - len(designed)
        promoted = 0
        for post in posts:
            if promoted >= shortfall:
                break
            if not post.get("needs_design"):
                post["needs_design"] = True
                post.setdefault("asset_source", "designed")
                promoted += 1
        if promoted:
            adjustments.append(
                f"Promoted {promoted} post(s) to designed to reach the "
                f"{package.design_ratio} content:design ratio."
            )

    boosted = [p for p in posts if p.get("boost")]
    if len(boosted) > package.boosted_posts:
        for post in boosted[package.boosted_posts:]:
            post["boost"] = False
        adjustments.append(f"Capped boost flags at the package's {package.boosted_posts}.")

    content["posts"] = posts
    if adjustments:
        content["package_adjustments"] = adjustments
    return content


def ratio_report(content: dict[str, Any], package: ContentPackage) -> dict[str, Any]:
    """The month's actual numbers — what the MD and the client both check."""
    posts = content.get("posts") or []
    designed = sum(1 for p in posts if p.get("needs_design"))
    by_type: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    by_pillar: dict[str, int] = {}
    for post in posts:
        by_type[post.get("content_type", "?")] = by_type.get(post.get("content_type", "?"), 0) + 1
        by_platform[post.get("platform", "?")] = by_platform.get(post.get("platform", "?"), 0) + 1
        by_pillar[post.get("pillar", "?")] = by_pillar.get(post.get("pillar", "?"), 0) + 1
    total = len(posts)
    return {
        "package": package.name,
        "posts_planned": total,
        "posts_contracted": package.posts_per_month,
        "designed_assets": designed,
        "copy_led": total - designed,
        "design_ratio": f"{designed}:{total}" if total else "0:0",
        "design_ratio_pct": round(100 * designed / total) if total else 0,
        "contracted_ratio": package.design_ratio,
        "story_sets": package.story_sets,
        "short_videos": sum(1 for p in posts if p.get("content_type") == "short_video"),
        "boosted": sum(1 for p in posts if p.get("boost")),
        "by_type": by_type,
        "by_platform": by_platform,
        "by_pillar": by_pillar,
        "on_contract": total == package.posts_per_month and designed == package.designed_assets,
    }


def parse_studio_request(text: str) -> tuple[str, str, str]:
    """Split a free-text ask into (brand, package_key, brief).

    '/content Golden Duck 16' → ('Golden Duck', 'growth_16', 'Golden Duck')
    A bare number or tier word anywhere is the package; a stored brand name
    appearing in the text is the brand. Everything stays in the brief so no
    detail is lost to parsing.
    """
    from utils.brands import find, names

    tokens = (text or "").split()
    package_spec = ""
    rest: list[str] = []
    for token in tokens:
        candidate = token.strip().lower().strip(",.")
        if not package_spec and (candidate.isdigit() or candidate in
                                 ("starter", "core", "growth", "dominate", "daily")):
            package_spec = candidate
        else:
            rest.append(token)
    brief = " ".join(rest).strip()

    brand = ""
    lowered = brief.lower()
    for name in names():
        if name and name.lower() in lowered:
            brand = name
            break
    if not brand:
        match = find(brief)
        if match:
            brand = match.get("brand", "")
    return brand, resolve_package(package_spec).key, brief


async def run_content_studio(
    brief: str,
    memory: SharedMemory,
    brand: str = "",
    package: str | int | None = None,
    month: str = "next month",
    feedback: str = "",
    cycle: int = 1,
) -> dict[str, Any]:
    """Full studio cycle: strategy (primary) → content + design system (parallel,
    cheap) → design specs (cheap).

    Returns {brand, month, package, strategy, content, design_system, designs,
    ratio, render_specs, cycle}.
    """
    settings = get_settings()
    pkg = resolve_package(package)
    brand_name = brand or ""

    # 1. Strategy first — everything downstream inherits it. Primary model.
    strategist = BrandStrategistAgent()
    strategy_prompt = await strategist.build_user_prompt(
        memory, brand=brand_name, brief=brief, package=pkg, feedback=feedback
    )
    strategy, response = await strategist.llm.complete_json(
        system=strategist.build_system_prompt(),
        user_prompt=strategy_prompt,
        schema=strategist.output_schema,
        max_tokens=8000,
    )
    await memory.record_tokens(response.input_tokens, response.output_tokens)
    await memory.set(strategist.agent_key, strategy)

    # 2 + 3. The month's copy and the visual system, in parallel on the cheap model.
    creator = ContentCreatorAgent()
    director = DesignDirectorAgent()

    async def _run(agent: BaseAgent, max_tokens: int, **kwargs: Any) -> dict[str, Any]:
        prompt = await agent.build_user_prompt(
            memory, brand=brand_name, brief=brief, package=pkg,
            strategy=strategy, feedback=feedback, **kwargs
        )
        data, resp = await agent.llm.complete_json(
            system=agent.build_system_prompt(),
            user_prompt=prompt,
            schema=agent.output_schema,
            model=settings.fallback_model_name,
            max_tokens=max_tokens,
        )
        await memory.record_tokens(resp.input_tokens, resp.output_tokens)
        await memory.set(agent.agent_key, data)
        return data

    # A 30-post month needs real output room; an 8-post month doesn't.
    content_tokens = min(16000, 4000 + pkg.posts_per_month * 420)
    content, design_system = await asyncio.gather(
        _run(creator, content_tokens, month=month),
        _run(director, 6000),
    )

    content = _reconcile(content, pkg)
    await memory.set(creator.agent_key, content)

    # 4. Per-asset design specs, keyed to the reconciled calendar.
    designer = DesignerAgent()
    designs = await _run(
        designer,
        min(14000, 3000 + pkg.designed_assets * 500),
        design_system=design_system,
        content=content,
    )

    ratio = ratio_report(content, pkg)
    package_dict = pkg.as_dict()
    result = {
        "brand": brand_name or (strategy.get("brand_platform", {}) or {}).get("positioning", "")[:60],
        "month": month,
        "brief": brief,
        "package": package_dict,
        "strategy": strategy,
        "content": content,
        "design_system": design_system,
        "designs": designs,
        "ratio": ratio,
        "render_specs": render_specs(designs),
        "cycle": cycle,
    }
    await memory.set("content_studio", {
        "brand": result["brand"], "month": month, "package": pkg.key, "ratio": ratio,
    })
    return result


def render_specs(designs: dict[str, Any]) -> list[dict[str, str]]:
    """Extract render-ready specs from the designer output, for utils.imagegen."""
    specs = []
    for spec in designs.get("design_specs", []) or []:
        prompt = (spec.get("render_prompt") or "").strip()
        if not prompt:
            continue
        specs.append({
            "prompt": prompt,
            "label": spec.get("ref", "design"),
            "format": spec.get("format", "square"),
        })
    return specs


# ---------------------------------------------------------------------------
# Document export
# ---------------------------------------------------------------------------

def _bullets(items: Any, prefix: str = "• ") -> str:
    if not items:
        return ""
    if isinstance(items, str):
        return items
    return "\n".join(f"{prefix}{i}" for i in items)


def plan_to_sections(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Map a studio result into docgen sections (branded .docx)."""
    strategy = plan.get("strategy", {}) or {}
    content = plan.get("content", {}) or {}
    system = plan.get("design_system", {}) or {}
    designs = plan.get("designs", {}) or {}
    ratio = plan.get("ratio", {}) or {}
    pkg = plan.get("package", {}) or {}

    platform = strategy.get("brand_platform", {}) or {}
    audience = strategy.get("audience", {}) or {}
    house = strategy.get("messaging_house", {}) or {}
    owned = strategy.get("owned_strategy", {}) or {}

    def _p(*parts: str) -> str:
        return "\n\n".join(p for p in parts if p)

    # 1. Brand strategy
    strategy_body = _p(
        f"Positioning: {platform.get('positioning', '')}",
        f"Promise: {platform.get('promise', '')}" if platform.get("promise") else "",
        f"Personality: {_bullets(platform.get('personality'), '')}".replace("\n", ", ")
        if platform.get("personality") else "",
        f"Tone of voice: {platform.get('tone_of_voice', '')}" if platform.get("tone_of_voice") else "",
        f"Core message: {house.get('core_message', '')}" if house.get("core_message") else "",
        "Proof points:\n" + _bullets(house.get("proof_points")) if house.get("proof_points") else "",
        "Never:\n" + _bullets(platform.get("do_not")) if platform.get("do_not") else "",
    )

    # 2. Audience
    segments = audience.get("segments", []) or []
    audience_body = _p(
        f"Primary audience: {audience.get('primary', '')}",
        f"The insight: {audience.get('insight', '')}" if audience.get("insight") else "",
    )
    audience_tables = [{
        "title": "Audience segments",
        "headers": ["Segment", "Profile", "What makes them act", "Objection"],
        "rows": [[s.get("name", ""), s.get("profile", ""), s.get("trigger", ""), s.get("objection", "")]
                 for s in segments],
    }] if segments else []

    # 3. Owned-channel strategy
    pillars = strategy.get("content_pillars", []) or []
    channels = strategy.get("channel_strategy", []) or []
    owned_body = _p(
        f"Thesis: {owned.get('thesis', '')}" if owned.get("thesis") else "",
        "90-day arc:\n" + _bullets(owned.get("ninety_day_arc")) if owned.get("ninety_day_arc") else "",
        f"Community & response: {owned.get('community_plan', '')}" if owned.get("community_plan") else "",
        f"Organic → paid: {owned.get('organic_paid_handshake', '')}"
        if owned.get("organic_paid_handshake") else "",
    )
    owned_tables = []
    if pillars:
        owned_tables.append({
            "title": "Content pillars",
            "headers": ["Pillar", "Purpose", "Share of month", "Example topics"],
            "rows": [[p.get("name", ""), p.get("purpose", ""), f"{p.get('share_pct', '')}%",
                      ", ".join(p.get("example_topics", []) or [])] for p in pillars],
        })
    if channels:
        owned_tables.append({
            "title": "Channel strategy",
            "headers": ["Platform", "Role in the funnel", "Format focus", "Cadence", "Best times"],
            "rows": [[c.get("platform", ""), c.get("role", ""), c.get("format_focus", ""),
                      c.get("cadence", ""), c.get("best_times", "")] for c in channels],
        })

    # 4. The month's calendar
    posts = content.get("posts", []) or []
    calendar_body = _p(
        f"Month theme: {content.get('month_theme', '')}" if content.get("month_theme") else "",
        f"Volume: {ratio.get('posts_planned', 0)} posts · content:design ratio "
        f"{ratio.get('design_ratio', '')} ({ratio.get('design_ratio_pct', 0)}% designed) · "
        f"{ratio.get('short_videos', 0)} videos · {ratio.get('story_sets', 0)} story sets · "
        f"{ratio.get('boosted', 0)} flagged to boost",
        "Story plan:\n" + _bullets(content.get("story_plan")) if content.get("story_plan") else "",
        "Repeatable series:\n" + _bullets(content.get("series_ideas")) if content.get("series_ideas") else "",
    )
    calendar_tables = [{
        "title": "Monthly content calendar",
        "headers": ["Ref", "Wk", "Platform", "Type", "Pillar", "Hook", "CTA", "Design?"],
        "rows": [[p.get("ref", ""), str(p.get("week", "")), p.get("platform", ""),
                  p.get("content_type", ""), p.get("pillar", ""), p.get("hook", ""),
                  p.get("cta", ""), "Yes" if p.get("needs_design") else "—"] for p in posts],
    }] if posts else []

    # 5. Captions (the copy deck itself)
    caption_rows = [[
        p.get("ref", ""),
        p.get("caption_en", ""),
        p.get("caption_mm", ""),
        " ".join(p.get("hashtags", []) or []),
    ] for p in posts]
    caption_tables = [{
        "title": "Copy deck — captions (English / Myanmar)",
        "headers": ["Ref", "Caption (EN)", "Caption (MM)", "Hashtags"],
        "rows": caption_rows,
    }] if caption_rows else []

    # 6. Visual system
    palette = system.get("palette", []) or []
    templates = system.get("templates", []) or []
    typography = system.get("typography", {}) or {}
    system_body = _p(
        system.get("art_direction", ""),
        f"Mood: {', '.join(system.get('mood_keywords', []) or [])}" if system.get("mood_keywords") else "",
        f"Headline type: {typography.get('headline', '')}" if typography.get("headline") else "",
        f"Body type: {typography.get('body', '')}" if typography.get("body") else "",
        f"Myanmar type: {typography.get('myanmar', '')}" if typography.get("myanmar") else "",
        f"Photography: {system.get('photography_direction', '')}"
        if system.get("photography_direction") else "",
        "Layout rules:\n" + _bullets(system.get("layout_rules")) if system.get("layout_rules") else "",
        f"Accessibility: {system.get('accessibility', '')}" if system.get("accessibility") else "",
        "Client to supply:\n" + _bullets(system.get("asset_checklist"))
        if system.get("asset_checklist") else "",
    )
    system_tables = []
    if palette:
        system_tables.append({
            "title": "Palette",
            "headers": ["Colour", "Hex", "Where it's used"],
            "rows": [[c.get("name", ""), c.get("hex", ""), c.get("use", "")] for c in palette],
        })
    if templates:
        system_tables.append({
            "title": "Template set",
            "headers": ["Template", "Used for", "Layout", "Dimensions"],
            "rows": [[t.get("name", ""), t.get("use_for", ""), t.get("layout", ""),
                      t.get("dimensions", "")] for t in templates],
        })

    # 7. Design specs
    specs = designs.get("design_specs", []) or []
    design_body = _p(
        f"Hero asset: {designs.get('hero_asset_ref', '')}" if designs.get("hero_asset_ref") else "",
        f"Estimated design time: {designs.get('estimated_design_hours', '')}"
        if designs.get("estimated_design_hours") else "",
        "Production order:\n" + _bullets(designs.get("production_order"))
        if designs.get("production_order") else "",
    )
    design_tables = [{
        "title": "Design specifications",
        "headers": ["Ref", "Format", "Template", "Composition", "On-asset headline", "Imagery"],
        "rows": [[s.get("ref", ""), s.get("format", ""), s.get("template", ""),
                  s.get("composition", ""), (s.get("on_asset_text", {}) or {}).get("headline", ""),
                  s.get("imagery", "")] for s in specs],
    }] if specs else []

    # 8. Measurement, scope and investment
    kpis = strategy.get("kpis", []) or []
    scope_body = _p(
        f"Package: {pkg.get('name', '')} — {pkg.get('posts_per_month', '')} posts/month, "
        f"content:design ratio {pkg.get('design_ratio', '')} "
        f"({pkg.get('design_ratio_pct', '')}% designed), {pkg.get('short_videos', '')} short "
        f"videos, {pkg.get('story_sets', '')} story sets, "
        f"{pkg.get('revision_rounds', '')} revision round(s).",
        f"Platforms: {', '.join(pkg.get('platforms', []) or [])}",
        f"Reporting: {pkg.get('reporting', '')}",
        f"Investment: {pkg.get('price_mmk', '')} / {pkg.get('price_sgd', '')} per month. "
        "50% deposit before work starts. Rates at market FX, sell side.",
        "Not included: paid media spend, talent fees, production shoots and printing — "
        "quoted separately per campaign.",
    )
    scope_tables = [{
        "title": "KPIs",
        "headers": ["Metric", "Target", "Why it matters"],
        "rows": [[k.get("metric", ""), k.get("target", ""), k.get("why", "")] for k in kpis],
    }] if kpis else []

    sections = [
        {"heading": "Brand Strategy", "body": strategy_body, "tables": []},
        {"heading": "Audience & Insight", "body": audience_body, "tables": audience_tables},
        {"heading": "Owned-Channel Strategy", "body": owned_body, "tables": owned_tables},
        {"heading": "The Month — Content Calendar", "body": calendar_body, "tables": calendar_tables},
        {"heading": "Copy Deck", "body": "", "tables": caption_tables},
        {"heading": "Visual System", "body": system_body, "tables": system_tables},
        {"heading": "Design Specifications", "body": design_body, "tables": design_tables},
        {"heading": "Scope, Measurement & Investment", "body": scope_body, "tables": scope_tables},
    ]

    # Anything the team had to assume travels with the document, never silently.
    questions: list[str] = []
    for block in (strategy, content, system, designs):
        questions.extend(block.get("open_questions", []) or [])
    adjustments = content.get("package_adjustments", []) or []
    if questions or adjustments:
        sections.append({
            "heading": "Open Questions & Delivery Notes",
            "body": _p(
                "To confirm with the client:\n" + _bullets(questions) if questions else "",
                "Plan adjustments made to hold the package contract:\n" + _bullets(adjustments)
                if adjustments else "",
            ),
            "tables": [],
        })
    return sections


__all__ = [
    "BrandStrategistAgent", "ContentCreatorAgent", "DesignDirectorAgent", "DesignerAgent",
    "run_content_studio", "parse_studio_request", "plan_to_sections",
    "ratio_report", "render_specs",
]
