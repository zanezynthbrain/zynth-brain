"""Daily Agency Workforce — founder-controlled proactive proposal production.

This module turns Zynth Brain from a request-response tool into a practical
agency workforce. Every run creates exactly three *internal* Concept Packages
across rotating industries, markets and work types. A package is a proposal and
creative brief: it is useful to review, improve and pitch, but it is never an
authorisation to contact a client, spend money, publish, or begin production.

The generator is intentionally separate from the creative queue. Daily ideas
may be produced autonomously; image, 3D, video and client release are routed
only after a named founder approves a real project.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from agents.proposal_factory import INDUSTRIES_MM, INDUSTRIES_SG, SEASONAL_CONTEXT
from utils.llm_client import LLMClient

_ROOT = Path("outputs/proposal_pool/daily_workforce")
MARKETS = ("MM", "SG")

# These lanes represent the agency work the founder explicitly wants prepared
# proactively. The rotation guarantees that a day covers different media and
# commercial situations instead of returning three social-post ideas.
WORK_LANES: tuple[dict[str, str], ...] = (
    {
        "key": "integrated_campaign",
        "label": "Integrated Campaign",
        "brief": "an insight-led integrated marketing campaign with channel roles, activation and measurable growth objective",
        "production_lane": "mixed",
    },
    {
        "key": "sponsorship_program",
        "label": "Sponsorship Programme",
        "brief": "a commercially credible sponsorship platform with tier logic, brand value and audience experience",
        "production_lane": "scene3d",
    },
    {
        "key": "digital_omnichannel",
        "label": "Digital / Omnichannel Campaign",
        "brief": "a digital-first campaign connecting paid, owned, social, CRM and experience touchpoints",
        "production_lane": "image",
    },
    {
        "key": "social_challenge",
        "label": "Social / TikTok Challenge",
        "brief": "a participation-led social challenge designed for safe creator adoption, clear mechanics and repeatable short-form content",
        "production_lane": "storyboard",
    },
    {
        "key": "corporate_event",
        "label": "Corporate Event",
        "brief": "a corporate conference, awards, launch or internal event concept with a meaningful guest journey and operating feasibility",
        "production_lane": "scene3d",
    },
    {
        "key": "stage_experience",
        "label": "Stage / Spatial Experience",
        "brief": "a stage, exhibition or event-environment concept with spatial storytelling, technical assumptions and controlled 3D-preview potential",
        "production_lane": "scene3d",
    },
    {
        "key": "video_storyboard",
        "label": "Video Storyboard",
        "brief": "a film or social-video platform with an insight, narrative structure, shot direction and sample-frame plan",
        "production_lane": "storyboard",
    },
    {
        "key": "seasonal_activation",
        "label": "Seasonal / Cultural Activation",
        "brief": "a culturally respectful seasonal, festival or special-day activation that avoids generic greetings and earns relevance for the named brand category",
        "production_lane": "image",
    },
)

_PACKAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["packages"],
    "properties": {
        "packages": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "required": [
                    "title", "opportunity", "business_objective", "audience",
                    "human_insight", "single_minded_proposition", "creative_concept",
                    "why_this_can_work", "activation_system", "channel_roles",
                    "deliverables", "kpi_hypothesis", "creative_direction",
                    "client_explanation", "assumptions", "open_questions",
                    "cultural_or_brand_risks",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "opportunity": {"type": "string"},
                    "business_objective": {"type": "string"},
                    "audience": {"type": "string"},
                    "human_insight": {"type": "string"},
                    "single_minded_proposition": {"type": "string"},
                    "creative_concept": {"type": "string"},
                    "why_this_can_work": {"type": "string"},
                    "activation_system": {"type": "array", "items": {"type": "string"}, "minItems": 3},
                    "channel_roles": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                    "deliverables": {"type": "array", "items": {"type": "string"}, "minItems": 3},
                    "kpi_hypothesis": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                    "creative_direction": {"type": "string"},
                    "client_explanation": {"type": "string"},
                    "assumptions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "open_questions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "cultural_or_brand_risks": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                },
            },
        }
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _industries(market: str) -> list[str]:
    return INDUSTRIES_MM if market == "MM" else INDUSTRIES_SG


def daily_slots(day: date | None = None) -> list[dict[str, str]]:
    """Return three deterministic, varied work assignments for a calendar day.

    Deterministic rotation is intentional: it lets the founder plan capacity,
    prevents duplicated categories, and eventually covers every sector without
    relying on a model to remember what it already produced.
    """
    day = day or date.today()
    n = day.toordinal()
    lane_offsets = (0, 3, 5)
    slots: list[dict[str, str]] = []
    for position, offset in enumerate(lane_offsets, start=1):
        lane = WORK_LANES[(n + offset) % len(WORK_LANES)]
        market = MARKETS[(n + position - 1) % len(MARKETS)]
        industry = _industries(market)[(n * 3 + offset) % len(_industries(market))]
        slots.append({
            "slot": str(position),
            "slot_id": f"{day.isoformat()}-{position}",
            "market": market,
            "industry": industry,
            "lane": lane["key"],
            "lane_label": lane["label"],
            "lane_brief": lane["brief"],
            "production_lane": lane["production_lane"],
            "seasonal_context": SEASONAL_CONTEXT.get(day.strftime("%B"), ""),
        })
    return slots


def _system_prompt() -> str:
    return (
        "You are ZYNTH's Daily Agency Workforce: a joint senior strategist, creative director, "
        "event producer and proposal writer serving Myanmar and Singapore. Produce commercially "
        "useful internal concept packages, not generic marketing ideas. Each package must have a "
        "clear human tension, a defensible strategic proposition, a distinctive creative system, "
        "realistic channels and measurable KPI hypotheses. Treat supplied occasion and industry "
        "context as direction, not proof. Never invent a client's facts, partnerships, legal "
        "permissions, performance results, cultural claims, prices or dates. State assumptions and "
        "open questions plainly. Work may be reviewed internally only: do not claim it is client "
        "approved, ready to publish, or approved for production. Avoid text inside generated images; "
        "final typography is applied in controlled composition."
    )


def _user_prompt(slots: list[dict[str, str]], day: date) -> str:
    lines = [
        f"Prepare exactly three distinct internal ZYNTH Concept Packages for {day.isoformat()}.",
        "The package positions are fixed below. Preserve the market, industry and work lane in the corresponding output order.",
        "Do not repeat an idea, visual trope, objective or channel mechanic across the three packages.",
        "A TikTok/social challenge must have participation mechanics and basic brand-safety considerations. "
        "An event/stage concept must state capacity, venue and fabrication assumptions rather than invent them. "
        "A seasonal/cultural activation must explain relevance without using stereotypes or unsupported cultural claims.",
        "KPIs are hypotheses, not promises, and must identify a sensible measurement signal.",
        "",
    ]
    for slot in slots:
        lines.extend([
            f"PACKAGE {slot['slot']} — {slot['lane_label']}",
            f"Market: {slot['market']} | Industry: {slot['industry']}",
            f"Assignment: {slot['lane_brief']}",
            f"Current month context: {slot['seasonal_context']}",
            f"Preferred future production lane: {slot['production_lane']}",
            "",
        ])
    return "\n".join(lines)


def _normalise(packages: list[dict[str, Any]], slots: list[dict[str, str]], day: date) -> list[dict[str, Any]]:
    """Attach non-negotiable routing and approval fields to model output."""
    normalised: list[dict[str, Any]] = []
    for package, slot in zip(packages[:3], slots):
        row = dict(package)
        row.update({
            "id": slot["slot_id"],
            "date": day.isoformat(),
            "market": slot["market"],
            "industry": slot["industry"],
            "work_lane": slot["lane"],
            "work_lane_label": slot["lane_label"],
            "production_lane": slot["production_lane"],
            "status": "internal_draft",
            "approval_status": "founder_review_required",
            "client_contact_allowed": False,
            "production_allowed": False,
            "publishing_allowed": False,
        })
        normalised.append(row)
    return normalised


def save_daily_run(payload: dict[str, Any]) -> Path:
    """Persist one immutable-ish daily run under the durable proposal-pool tree."""
    day = str(payload.get("date") or date.today().isoformat())[:10]
    _ROOT.mkdir(parents=True, exist_ok=True)
    path = _ROOT / f"{day}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_daily_run(day: str) -> dict[str, Any] | None:
    path = _ROOT / f"{str(day)[:10]}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


async def run_daily_workforce(
    *,
    day: date | None = None,
    llm_client: LLMClient | None = None,
) -> dict[str, Any]:
    """Generate and persist the daily internal proposal pack.

    The method deliberately has no side effects outside durable internal storage.
    The scheduler may notify the founder, but neither this function nor its model
    prompt can message clients, launch campaigns or drain production queues.
    """
    day = day or date.today()
    slots = daily_slots(day)
    llm = llm_client or LLMClient()
    data, response = await llm.complete_json(
        system=_system_prompt(),
        user_prompt=_user_prompt(slots, day),
        schema=_PACKAGE_SCHEMA,
        max_tokens=7000,
    )
    packages = _normalise(data.get("packages", []), slots, day)
    if len(packages) != 3:
        raise ValueError("Daily workforce must produce exactly three concept packages")
    payload = {
        "date": day.isoformat(),
        "generated_at": _now(),
        "status": "founder_review_required",
        "mocked": bool(response.mocked),
        "model_usage": {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        },
        "slots": slots,
        "packages": packages,
    }
    path = save_daily_run(payload)
    payload["path"] = str(path)
    return payload


def summary_text(payload: dict[str, Any]) -> str:
    """Founder-facing status text; deliberately says review rather than release."""
    packs = payload.get("packages") or []
    lines = [
        f"🏭 <b>Daily Agency Workforce — {payload.get('date', '')}</b>",
        "3 internal concept packages are ready for founder review. No client contact, publication or production has been authorised.",
        "",
    ]
    for p in packs:
        lines.append(
            f"{p.get('id', '')} · <b>{p.get('work_lane_label', 'Concept')}</b> · "
            f"{p.get('industry', '')} ({p.get('market', '')})\n"
            f"{p.get('title', 'Untitled')}"
        )
    lines.append("\nReview, assign to a real lead/project, or archive. A founder approval is required before any production route opens.")
    return "\n\n".join(lines)


__all__ = [
    "MARKETS", "WORK_LANES", "daily_slots", "run_daily_workforce",
    "save_daily_run", "load_daily_run", "summary_text",
]
