"""Telegram notification utilities for the ZYNTH agent backend.

Agents call :func:`send_message` or department-specific helpers to push
updates to the founder's personal chat or to the real ZYNTH team groups.
When credentials are missing the calls are silently logged so the pipeline
is never blocked by a missing notification channel.

Group routing:
    send_message()            → founder personal chat (TELEGRAM_CHAT_ID)
    send_bd_brief()           → ZYNTH BD Department group
    send_to_creative_group()  → ZYNTH Creative Department group
    send_to_marketing_group() → ZYNTH Marketing Firm group
    send_to_gm_group()        → ZYNTH GM / leadership group
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import httpx

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("utils.telegram")

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


# ---------------------------------------------------------------------------
# Core send helper
# ---------------------------------------------------------------------------

async def _send_to_chat(chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """Internal: send text to an arbitrary chat_id. Returns True on success."""
    settings = get_settings()
    if not settings.telegram_bot_token:
        logger.info("[Telegram not configured] Would send to %s: %s", chat_id, text[:80])
        return False
    if not chat_id:
        logger.info("[Telegram] chat_id not set — skipping: %s", text[:80])
        return False

    url = TELEGRAM_API.format(token=settings.telegram_bot_token, method="sendMessage")
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return True
    except Exception as exc:
        logger.warning("Telegram send failed (chat %s): %s", chat_id, exc)
        return False


async def _send_chunks(chat_id: str, text: str) -> bool:
    chunks = _chunk_message(text)
    success = True
    for chunk in chunks:
        if not await _send_to_chat(chat_id, chunk):
            success = False
    return success


# ---------------------------------------------------------------------------
# Public API — founder personal chat
# ---------------------------------------------------------------------------

async def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send a message to the founder's personal Telegram chat."""
    settings = get_settings()
    if not settings.has_telegram:
        logger.info("[Telegram not configured] Would send: %s", text[:120])
        return False
    return await _send_to_chat(settings.telegram_chat_id, text, parse_mode)


async def send_report(report: dict[str, Any], title: str = "ZYNTH Daily Brief") -> bool:
    """Format and send a structured department report to the founder's chat."""
    text = _format_report(report, title)
    return await _send_chunks(get_settings().telegram_chat_id, text)


async def send_ceo_daily_brief(ceo_output: dict[str, Any], date: str | None = None) -> bool:
    """Send the CEO daily brief to the founder's personal chat."""
    today = date or datetime.now().strftime("%B %d, %Y")
    lines = [
        f"🧠 <b>ZYNTH Daily Brief — {today}</b>",
        f"📋 Theme: {ceo_output.get('daily_theme', 'N/A')}",
        "",
        "📌 <b>Key Decisions:</b>",
    ]
    for d in ceo_output.get("key_decisions", []):
        lines.append(f"  • {d}")

    lines += ["", "✅ <b>Action Items:</b>"]
    for item in ceo_output.get("action_items", []):
        dept = item.get("assigned_to", "?")
        task = item.get("item", "?")
        due = item.get("due", "?")
        lines.append(f"  [{dept}] {task} (due: {due})")

    lines += ["", f"📊 {ceo_output.get('executive_summary', '')}"]
    lines += ["", "─────────────────────", "/status  /brief  /report"]

    return await send_message("\n".join(lines))


async def send_department_update(dept_name: str, summary: str, emoji: str = "📁") -> bool:
    """Send a brief department status update to the founder's personal chat."""
    text = f"{emoji} <b>{dept_name} Update</b>\n\n{summary}"
    return await send_message(text)


# ---------------------------------------------------------------------------
# Department group routing
# ---------------------------------------------------------------------------

async def send_bd_brief(lead_gen_output: dict[str, Any], date: str | None = None) -> bool:
    """Send BD outreach brief to ZYNTH BD Department group.

    Matches the existing ZYNTH MD format:
    🎯 TARGET / 💡 ANGLE / 📲 OUTREACH / ⚡ EXPECTED MOVE
    """
    settings = get_settings()
    today = date or datetime.now().strftime("%d %b %Y")
    prospects = lead_gen_output.get("prospect_list", [])
    emails = lead_gen_output.get("cold_emails", [])
    personas = lead_gen_output.get("personas", [])

    lines = [f"📊 <b>ZYNTH BD Brief — {today}</b>", ""]

    for i, prospect in enumerate(prospects[:3]):
        company = prospect.get("company", "?")
        role = prospect.get("contact_title", "?")
        fit = prospect.get("fit_score", 0)
        email = emails[i] if i < len(emails) else {}
        persona = personas[i] if i < len(personas) else {}
        pain = (persona.get("pain_points") or ["—"])[0]
        channels = ", ".join(persona.get("channels", ["Direct"]))

        lines += [
            f"━━━ Prospect {i + 1} ━━━",
            f"🎯 <b>TARGET</b>: {company} — {role} (Fit: {int(fit * 10)}/10)",
            f"💡 <b>ANGLE</b>: {pain}",
            f"📲 <b>OUTREACH</b>: {channels}",
            f"⚡ <b>EXPECTED MOVE</b>: {email.get('subject', 'Schedule intro call')}",
            "",
        ]

    qual = lead_gen_output.get("inbound_lead_evaluation", {})
    if qual.get("qualification_notes"):
        lines += [f"📋 <b>Lead Notes:</b> {qual['qualification_notes'][:200]}"]

    lines += ["", "─────────────────────", "Powered by ZYNTH AI 🤖"]
    return await _send_chunks(settings.telegram_bd_chat_id, "\n".join(lines))


async def send_to_creative_group(portfolio_output: dict[str, Any], date: str | None = None) -> bool:
    """Send today's creative direction to ZYNTH Creative Department group."""
    settings = get_settings()
    today = date or datetime.now().strftime("%d %b %Y")
    brand = portfolio_output.get("brand", "Unknown")
    direction = portfolio_output.get("creative_direction", {})
    deliverables = portfolio_output.get("deliverables", [])

    lines = [
        f"🎨 <b>ZYNTH Creative Brief — {today}</b>",
        f"",
        f"<b>Brand:</b> {brand}",
        f"<b>Tagline:</b> <i>{direction.get('tagline', '—')}</i>",
        f"<b>Tone:</b> {direction.get('tone', '—')}",
        f"<b>Visual Style:</b> {direction.get('visual_style', '—')}",
        "",
        "📦 <b>Deliverables:</b>",
    ]
    for d in deliverables[:5]:
        if isinstance(d, dict):
            lines.append(f"  • {d.get('type', '?')} — {d.get('description', '')[:80]}")
        else:
            lines.append(f"  • {str(d)[:80]}")

    color_palette = direction.get("color_palette", [])
    if color_palette:
        lines += ["", f"🎨 Palette: {', '.join(str(c) for c in color_palette[:4])}"]

    lines += ["", "─────────────────────", "Powered by ZYNTH AI 🤖"]
    return await _send_chunks(settings.telegram_creative_chat_id, "\n".join(lines))


async def send_to_marketing_group(research_output: dict[str, Any], date: str | None = None) -> bool:
    """Send market research highlights to ZYNTH Marketing Firm group."""
    settings = get_settings()
    today = date or datetime.now().strftime("%d %b %Y")
    keywords = research_output.get("high_intent_keywords", [])
    insights = research_output.get("competitor_analysis", {})
    focus_areas = research_output.get("recommended_focus_areas", [])

    lines = [
        f"📈 <b>ZYNTH Market Intel — {today}</b>",
        "",
        "🔑 <b>Top Keywords:</b>",
    ]
    for kw in keywords[:5]:
        if isinstance(kw, dict):
            vol = kw.get("monthly_volume", "?")
            diff = kw.get("difficulty", "?")
            lines.append(f"  • {kw.get('keyword')} (vol: {vol}, diff: {diff})")
        else:
            lines.append(f"  • {kw}")

    if focus_areas:
        lines += ["", "🎯 <b>Focus Areas:</b>"]
        for area in focus_areas[:4]:
            lines.append(f"  • {area}")

    gap = insights.get("content_gap_opportunity", "") if isinstance(insights, dict) else ""
    if gap:
        lines += ["", f"💡 <b>Opportunity:</b> {str(gap)[:200]}"]

    lines += ["", "─────────────────────", "Powered by ZYNTH AI 🤖"]
    return await _send_chunks(settings.telegram_marketing_chat_id, "\n".join(lines))


async def send_to_gm_group(ceo_output: dict[str, Any], date: str | None = None) -> bool:
    """Send CEO leadership summary to ZYNTH GM group."""
    settings = get_settings()
    today = date or datetime.now().strftime("%d %b %Y")
    lines = [
        f"🏢 <b>ZYNTH Leadership Summary — {today}</b>",
        f"Theme: {ceo_output.get('daily_theme', 'N/A')}",
        "",
        "📌 <b>Decisions:</b>",
    ]
    for d in ceo_output.get("key_decisions", [])[:5]:
        lines.append(f"  • {d}")

    lines += ["", "✅ <b>Action Items:</b>"]
    for item in ceo_output.get("action_items", [])[:6]:
        lines.append(f"  [{item.get('assigned_to', '?')}] {item.get('item', '?')}")

    summary = ceo_output.get("executive_summary", "")
    if summary:
        lines += ["", f"📊 {summary[:300]}"]

    lines += ["", "─────────────────────", "Powered by ZYNTH AI 🤖"]
    return await _send_chunks(settings.telegram_gm_chat_id, "\n".join(lines))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _format_report(report: dict[str, Any], title: str) -> str:
    lines = [f"<b>{title}</b>", ""]
    for key, value in report.items():
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"<b>{label}:</b>")
            for item in value[:5]:
                lines.append(f"  • {item if isinstance(item, str) else json.dumps(item)[:80]}")
        elif isinstance(value, dict):
            lines.append(f"<b>{label}:</b> {str(value)[:120]}")
        else:
            lines.append(f"<b>{label}:</b> {str(value)[:200]}")
    return "\n".join(lines)


def _chunk_message(text: str, max_len: int = 4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        chunk = text[:max_len]
        last_newline = chunk.rfind("\n")
        if last_newline > max_len // 2:
            chunk = text[:last_newline]
        chunks.append(chunk)
        text = text[len(chunk):]
    return chunks
