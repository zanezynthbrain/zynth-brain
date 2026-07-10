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

async def _send_to_chat(
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    reply_markup: dict | None = None,
) -> bool:
    """Internal: send text to an arbitrary chat_id. Returns True on success."""
    settings = get_settings()
    if not settings.telegram_bot_token:
        logger.info("[Telegram not configured] Would send to %s: %s", chat_id, text[:80])
        return False
    if not chat_id:
        logger.info("[Telegram] chat_id not set — skipping: %s", text[:80])
        return False

    url = TELEGRAM_API.format(token=settings.telegram_bot_token, method="sendMessage")
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
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

def _format_prospect_block(idx: int, total: int, p: dict[str, Any]) -> str:
    """Format a single prospect in the ZYNTH BD Brief style."""
    company = p.get("company", "?")
    market = p.get("market", "?")
    what = p.get("what_they_do", "")
    role = p.get("contact_title", "?")
    fit = p.get("fit_score", 0)
    fit_pct = int(fit * 100)
    why_now = p.get("why_now", "")
    angle = p.get("angle", "")
    outreach = p.get("outreach_message", "")
    move = p.get("expected_move", "")
    services = ", ".join(p.get("suggested_services", []))
    budget = p.get("budget_estimate", "")

    lines = [
        f"━━━ {idx}/{total} — {market} ━━━",
        f"🎯 <b>TARGET</b>",
        f"{company} — {what}",
        f"Contact: {role} | Fit: {fit_pct}%",
        "",
        f"💡 <b>ANGLE</b>",
        f"{angle}",
        f"<i>Why now: {why_now}</i>",
        "",
        f"📲 <b>OUTREACH</b>",
        f"<code>{outreach}</code>",
        "",
        f"⚡ <b>EXPECTED MOVE</b>",
        f"{move}",
        "",
        f"🛠 Pitch: {services}",
        f"💰 Budget est: {budget}",
    ]
    return "\n".join(lines)


async def send_bd_brief(lead_gen_output: dict[str, Any], date: str | None = None) -> bool:
    """Send all 3 BD prospects to ZYNTH BD Department group (read-only, no buttons)."""
    settings = get_settings()
    today = date or datetime.now().strftime("%d %b %Y")
    prospects = lead_gen_output.get("prospects", [])
    is_mock = not get_settings().has_llm_credentials

    header = [
        f"📊 <b>ZYNTH BD BRIEF — {today}</b>",
        f"<i>NOVA | {len(prospects)} prospects</i>",
        "",
    ]

    blocks = []
    for i, p in enumerate(prospects[:3]):
        blocks.append(_format_prospect_block(i + 1, len(prospects[:3]), p))

    source_note = (
        "⚠️ <i>Data: AI knowledge base (Aug 2025). Verify details before outreach.</i>\n"
        "<i>Add SERPER_API_KEY + ZYNTH_ALLOW_NETWORK=true for live web research.</i>"
        if not is_mock else
        "🔵 <i>MOCK MODE — add ANTHROPIC_API_KEY for real AI-generated prospects.</i>"
    )

    full_text = "\n".join(header) + "\n\n" + "\n\n".join(blocks) + "\n\n" + source_note
    return await _send_chunks(settings.telegram_bd_chat_id, full_text)


async def send_bd_brief_interactive(
    lead_gen_output: dict[str, Any],
    personal_chat_id: str,
    date: str | None = None,
) -> bool:
    """Send 3 BD prospects to the MD's personal chat with approve/skip buttons.

    Each prospect gets its own message + inline keyboard so the MD can
    tap ✅ Approve or ⏭ Skip directly. No typing required.
    """
    today = date or datetime.now().strftime("%d %b %Y")
    prospects = lead_gen_output.get("prospects", [])
    is_mock = not get_settings().has_llm_credentials

    # Send header first
    header = (
        f"📊 <b>ZYNTH BD BRIEF — {today}</b>\n"
        f"NOVA found {len(prospects[:3])} prospects. Tap to approve or skip each one.\n"
    )
    if is_mock:
        header += "\n🔵 <i>MOCK MODE — add ANTHROPIC_API_KEY for real prospects.</i>"
    else:
        header += "\n⚠️ <i>AI knowledge base. Verify before reaching out.</i>"

    await _send_to_chat(personal_chat_id, header)

    # Send each prospect as its own message with inline buttons
    success = True
    for i, p in enumerate(prospects[:3]):
        text = _format_prospect_block(i + 1, len(prospects[:3]), p)
        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ Approve — add to pipeline", "callback_data": f"bd_approve_{i}"},
                {"text": "⏭ Skip", "callback_data": f"bd_skip_{i}"},
            ]]
        }
        if not await _send_to_chat(personal_chat_id, text, reply_markup=keyboard):
            success = False

    return success


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
