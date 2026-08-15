"""Publisher — takes an APPROVED queue entry and does the right thing per platform.

Facebook: hand it to Meta with a scheduled time; Meta owns it from there.
Instagram: it can't be scheduled at Meta, so the entry stays approved and the
scheduler calls ``run_due_instagram`` when its minute arrives.

The one rule this module enforces above everything else: an entry that is not
``approved`` is never sent. Approval is the MD's, not the pipeline's.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from utils import publish_queue as Q
from utils.logging_config import get_logger
from utils.meta import (
    MetaResult,
    platform_of,
    publish_instagram_post,
    schedule_facebook_post,
)

logger = get_logger("utils.publisher")


class NotApproved(Exception):
    """Refused: the entry has not been approved by the MD."""


def compose_caption(entry: dict[str, Any]) -> str:
    """Build the caption exactly as it will appear on the platform.

    Myanmar first (that's the audience), English beneath, hashtags last — one
    blank line between blocks so it reads on a phone.
    """
    blocks = [entry.get("caption_mm", "").strip(), entry.get("caption_en", "").strip()]
    tags = " ".join(t if t.startswith("#") else f"#{t}" for t in (entry.get("hashtags") or []))
    if tags:
        blocks.append(tags)
    return "\n\n".join(b for b in blocks if b)


def _asset_url(entry: dict[str, Any]) -> str:
    """The public URL for this entry's asset, if one has been published."""
    if entry.get("asset_url"):
        return entry["asset_url"]
    if entry.get("asset_path"):
        from utils.assets import public_url
        from pathlib import Path
        return public_url(Path(entry["asset_path"]).name)
    return ""


async def publish_entry(entry_id: str) -> MetaResult:
    """Send one approved entry: schedule on Facebook, or publish now on Instagram."""
    entry = Q.get(entry_id)
    if not entry:
        raise NotApproved(f"No queue entry '{entry_id}'.")
    if entry.get("state") != "approved":
        raise NotApproved(
            f"{entry_id} is '{entry.get('state')}' — only an MD-approved entry can be sent."
        )

    caption = compose_caption(entry)
    platform = platform_of(entry.get("platform", ""))
    url = _asset_url(entry)

    if platform == "instagram":
        is_video = entry.get("content_type") == "short_video"
        result = await publish_instagram_post(caption, media_url=url, is_video=is_video)
        if result.ok and result.action == "published":
            Q.mark_published(entry_id, result.post_id)
        elif not result.ok:
            Q.mark_failed(entry_id, result.error)
        return result

    # Facebook (and anything not IG) — Meta holds the schedule.
    try:
        when = datetime.fromisoformat(entry["publish_at"])
    except Exception as exc:  # noqa: BLE001
        Q.mark_failed(entry_id, f"Bad publish_at: {exc}")
        return MetaResult(ok=False, platform="Facebook", action="failed", error=str(exc))
    if when.tzinfo is None:
        when = when.replace(tzinfo=Q.YANGON)

    result = await schedule_facebook_post(caption, when, image_url=url)
    if result.ok and result.action == "scheduled":
        Q.mark_scheduled(entry_id, result.post_id, result.scheduled_for)
    elif not result.ok:
        Q.mark_failed(entry_id, result.error)
    return result


async def run_due_instagram(now: datetime | None = None) -> list[MetaResult]:
    """Publish every approved Instagram entry whose time has come.

    Called by the scheduler on a short interval. Instagram has no scheduling
    API, so this IS the scheduling — which is why it also catches entries whose
    minute passed during a restart rather than dropping them.
    """
    results: list[MetaResult] = []
    for entry in Q.due_instagram(now):
        try:
            results.append(await publish_entry(entry["id"]))
        except NotApproved as exc:
            logger.warning("Skipped %s: %s", entry.get("id"), exc)
    if results:
        logger.info("Instagram: fired %d due post(s)", len(results))
    return results


def readiness(entry: dict[str, Any]) -> tuple[bool, str]:
    """Whether this entry can actually be sent, and what's missing if not."""
    platform = platform_of(entry.get("platform", ""))
    if not compose_caption(entry).strip():
        return False, "no caption"
    if platform == "instagram" and not _asset_url(entry):
        return False, "Instagram needs a public asset URL — attach the asset and set ZYNTH_PUBLIC_URL"
    if entry.get("needs_design") and not entry.get("asset_path"):
        return False, "designed post with no asset attached"
    return True, "ready"


__all__ = ["NotApproved", "compose_caption", "publish_entry", "run_due_instagram", "readiness"]
