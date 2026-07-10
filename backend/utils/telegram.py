"""Telegram notification utilities for the ZYNTH agent backend.

Agents call :func:`send_message` or :func:`send_report` to push updates
directly to the founder's Telegram chat. When ``TELEGRAM_BOT_TOKEN`` /
``TELEGRAM_CHAT_ID`` are not configured, calls are silently logged so the
rest of the pipeline is never blocked by a missing notification channel.

Setup (5 minutes):
    1. Message @BotFather on Telegram → /newbot → copy the token
    2. Start your new bot in Telegram, then call:
       https://api.telegram.org/bot<TOKEN>/getUpdates  → find your chat_id
    3. Add both to your .env file:
       TELEGRAM_BOT_TOKEN=...
       TELEGRAM_CHAT_ID=...

ဘော့တ်ဖန်တီးဖို့: Telegram မှာ @BotFather ကို message ပို့ → /newbot ဆိုတဲ့ command ပေး
→ TOKEN ရမယ် → .env ထဲ ထည့်ရမည်။
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


async def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send a plain message to the configured Telegram chat. Returns True on success."""
    settings = get_settings()
    if not settings.has_telegram:
        logger.info("[Telegram not configured] Would send: %s", text[:120])
        return False

    url = TELEGRAM_API.format(token=settings.telegram_bot_token, method="sendMessage")
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return True
    except Exception as exc:
        logger.warning("Telegram send_message failed: %s", exc)
        return False


async def send_report(report: dict[str, Any], title: str = "ZYNTH Daily Brief") -> bool:
    """Format and send a structured department report as a Telegram message."""
    text = _format_report(report, title)
    # Telegram has a 4096-char limit per message; split if needed
    chunks = _chunk_message(text, max_len=4000)
    success = True
    for chunk in chunks:
        if not await send_message(chunk):
            success = False
    return success


async def send_ceo_daily_brief(ceo_output: dict[str, Any], date: str | None = None) -> bool:
    """Send the CEO's daily brief in a well-formatted mobile-readable message."""
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
    lines += ["", "─────────────────────", "Reply with a command:", "/status  /run_creative  /report"]

    return await send_message("\n".join(lines))


async def send_department_update(dept_name: str, summary: str, emoji: str = "📁") -> bool:
    """Send a brief department status update."""
    text = f"{emoji} <b>{dept_name} Update</b>\n\n{summary}"
    return await send_message(text)


def _format_report(report: dict[str, Any], title: str) -> str:
    lines = [f"<b>{title}</b>", ""]
    for key, value in report.items():
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"<b>{label}:</b>")
            for item in value[:5]:  # cap for readability
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
