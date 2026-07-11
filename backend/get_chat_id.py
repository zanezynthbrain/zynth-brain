"""Helper script to discover Telegram chat IDs for the ZYNTH bot.

Run this on YOUR LOCAL MACHINE (not the server) after:
  1. Adding @zynth_md_approval_bot to each of your groups
  2. Sending at least one message in each group (so it appears in getUpdates)

Usage:
    cd backend
    python get_chat_id.py

It will print every chat the bot has seen — personal chat + all groups.
Copy the IDs into your .env file.
"""

from __future__ import annotations

import asyncio
import os
import sys

import httpx

TELEGRAM_API = "https://api.telegram.org/bot{token}/getUpdates"


async def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        # Try reading from .env in the same directory
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            for line in open(env_path):
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found.")
        print("Set it in your .env file or export it as an env variable.")
        sys.exit(1)

    url = TELEGRAM_API.format(token=token)
    print(f"\n🔍 Fetching updates from @zynth_md_approval_bot ...\n")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params={"limit": 100, "timeout": 0})
            r.raise_for_status()
            data = r.json()
    except Exception as exc:
        print(f"ERROR: Could not reach Telegram API: {exc}")
        sys.exit(1)

    updates = data.get("result", [])
    if not updates:
        print("No updates found.")
        print("\nMake sure you have:")
        print("  1. Added @zynth_md_approval_bot to each group")
        print("  2. Sent at least one message in each group after adding the bot")
        print("  3. Sent a /start message to the bot in your personal chat")
        return

    seen: dict[str, dict] = {}
    for update in updates:
        for msg_key in ("message", "my_chat_member", "chat_member"):
            msg = update.get(msg_key, {})
            chat = msg.get("chat", {})
            if chat:
                cid = str(chat["id"])
                seen[cid] = {
                    "id": cid,
                    "type": chat.get("type", "?"),
                    "title": chat.get("title") or chat.get("first_name", "?"),
                }

    print("━" * 50)
    print("  CHAT IDs FOUND — copy these into your .env")
    print("━" * 50)
    for info in seen.values():
        emoji = {"private": "👤", "group": "👥", "supergroup": "👥", "channel": "📢"}.get(info["type"], "💬")
        print(f"\n{emoji}  {info['title']}")
        print(f"     Type:    {info['type']}")
        print(f"     Chat ID: {info['id']}")

    print("\n" + "━" * 50)
    print("\n📋 .env values to fill in:\n")
    for info in seen.values():
        t = info["type"]
        cid = info["id"]
        title = info["title"]
        if t == "private":
            print(f"TELEGRAM_CHAT_ID={cid}          # {title} (your personal chat)")
        elif "bd" in title.lower() or "business" in title.lower():
            print(f"TELEGRAM_BD_CHAT_ID={cid}        # {title}")
        elif "creative" in title.lower():
            print(f"TELEGRAM_CREATIVE_CHAT_ID={cid}  # {title}")
        elif "marketing" in title.lower():
            print(f"TELEGRAM_MARKETING_CHAT_ID={cid} # {title}")
        elif "gm" in title.lower() or "leadership" in title.lower():
            print(f"TELEGRAM_GM_CHAT_ID={cid}        # {title}")
        else:
            print(f"# {title}: {cid}")

    print("\nAfter filling in .env, run: python scheduler.py --run-now brief")


if __name__ == "__main__":
    asyncio.run(main())
