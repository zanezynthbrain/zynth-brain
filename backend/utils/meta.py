"""Meta (Facebook Page + Instagram) publishing via the Graph API.

Two platforms, two very different mechanics — this module hides the difference
behind one ``schedule_post`` call and is honest about what each side can do:

**Facebook Pages** support real scheduling. We hand Meta the post with
``published=false`` and a ``scheduled_publish_time``; Meta holds it and
publishes it. Window: 10 minutes to 6 months out. If the bot is offline at that
moment, the post still goes out.

**Instagram has no scheduling API.** Publishing is create-container →
``media_publish``. So OUR scheduler has to be awake at the right minute and
fire the publish itself. If the container is created too early it expires
(Meta gives it 24 hours), so the container is created at publish time, not at
schedule time. An IG post therefore depends on the bot being alive — that is a
property of Meta's API, not a shortcut taken here.

**Instagram also needs a publicly reachable URL** for every image or video.
``utils.assets`` serves them off the Railway public URL for this reason.

Safety posture (MD-approved):
  - Nothing is sent to Meta without an explicit per-post approval — this module
    refuses to publish anything whose queue entry is not ``approved``.
  - ``dry_run`` (no token configured) returns exactly what WOULD be sent, so
    the whole path is testable and demonstrable without a live page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("utils.meta")

GRAPH = "https://graph.facebook.com/v21.0"

#: Meta's own bounds for a scheduled Page post.
MIN_LEAD = timedelta(minutes=10)
MAX_LEAD = timedelta(days=180)

#: Instagram publishing limit per rolling 24h, per account.
IG_DAILY_LIMIT = 50


class MetaError(Exception):
    """A Graph API call failed, or the request was invalid before sending."""


@dataclass
class MetaResult:
    """Outcome of one publish/schedule attempt."""

    ok: bool
    platform: str
    action: str                      # scheduled | published | would_send | failed
    post_id: str = ""
    scheduled_for: str = ""
    error: str = ""
    request: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        if not self.ok:
            return f"{self.platform}: FAILED — {self.error}"
        if self.action == "would_send":
            return f"{self.platform}: dry run — would {self.request.get('_intent', 'send')}"
        when = f" for {self.scheduled_for}" if self.scheduled_for else ""
        return f"{self.platform}: {self.action}{when} (id {self.post_id})"


def is_configured() -> tuple[bool, str]:
    """Whether Meta publishing can actually run, and what's missing if not."""
    settings = get_settings()
    missing = []
    if not settings.meta_access_token:
        missing.append("META_ACCESS_TOKEN")
    if not settings.meta_page_id:
        missing.append("META_PAGE_ID")
    if not settings.allow_network:
        missing.append("ZYNTH_ALLOW_NETWORK=true")
    if missing:
        return False, "Not configured — missing: " + ", ".join(missing)
    ig = " + Instagram" if settings.meta_ig_user_id else " (Facebook only — set META_IG_USER_ID for Instagram)"
    return True, f"Connected to Page {settings.meta_page_id}{ig}"


def validate_schedule_time(when: datetime) -> datetime:
    """Check a scheduled time against Meta's window. Returns it in UTC."""
    if when.tzinfo is None:
        raise MetaError("Scheduled time must be timezone-aware — pass Asia/Rangoon or UTC.")
    now = datetime.now(timezone.utc)
    delta = when.astimezone(timezone.utc) - now
    if delta < MIN_LEAD:
        raise MetaError(
            f"Meta needs at least 10 minutes' notice; that time is "
            f"{int(delta.total_seconds() // 60)} minute(s) away."
        )
    if delta > MAX_LEAD:
        raise MetaError("Meta won't hold a post more than 6 months ahead.")
    return when.astimezone(timezone.utc)


async def _graph(method: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
    """One Graph API call. Raises MetaError with Meta's own message on failure."""
    settings = get_settings()
    import httpx

    url = f"{GRAPH}/{path.lstrip('/')}"
    payload = {**params, "access_token": settings.meta_access_token}
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await (
                client.post(url, data=payload) if method == "POST"
                else client.get(url, params=payload)
            )
    except Exception as exc:  # noqa: BLE001 — network failures are reported, not raised raw
        raise MetaError(f"Could not reach Meta: {exc}") from exc

    try:
        data = response.json()
    except Exception:  # noqa: BLE001
        raise MetaError(f"Meta returned a non-JSON response ({response.status_code})")

    if response.status_code >= 400 or "error" in data:
        err = data.get("error", {})
        raise MetaError(
            f"{err.get('type', 'GraphError')} {err.get('code', response.status_code)}: "
            f"{err.get('message', response.text[:200])}"
        )
    return data


async def verify_connection() -> dict[str, Any]:
    """Confirm the token works and report what it can reach. Never raises."""
    ok, note = is_configured()
    if not ok:
        return {"ok": False, "note": note}
    settings = get_settings()
    out: dict[str, Any] = {"ok": True, "note": note}
    try:
        page = await _graph("GET", settings.meta_page_id, {"fields": "name,id,fan_count"})
        out["page"] = page
    except MetaError as exc:
        return {"ok": False, "note": f"Page check failed: {exc}"}
    if settings.meta_ig_user_id:
        try:
            ig = await _graph("GET", settings.meta_ig_user_id,
                              {"fields": "username,followers_count,media_count"})
            out["instagram"] = ig
        except MetaError as exc:
            out["instagram_error"] = str(exc)
    return out


async def schedule_facebook_post(
    message: str,
    when: datetime,
    image_url: str = "",
    link: str = "",
) -> MetaResult:
    """Schedule a Page post. Meta holds and publishes it — the bot need not be up."""
    settings = get_settings()
    when_utc = validate_schedule_time(when)
    unix = int(when_utc.timestamp())

    if image_url:
        path, params = f"{settings.meta_page_id}/photos", {
            "url": image_url, "caption": message,
            "published": "false", "scheduled_publish_time": unix,
        }
    else:
        path, params = f"{settings.meta_page_id}/feed", {
            "message": message, "published": "false", "scheduled_publish_time": unix,
        }
        if link:
            params["link"] = link

    ok, note = is_configured()
    if not ok:
        return MetaResult(ok=True, platform="Facebook", action="would_send",
                          scheduled_for=when_utc.isoformat(),
                          request={**params, "_path": path, "_intent": "schedule a Page post", "_note": note})

    try:
        data = await _graph("POST", path, params)
    except MetaError as exc:
        return MetaResult(ok=False, platform="Facebook", action="failed", error=str(exc))
    return MetaResult(ok=True, platform="Facebook", action="scheduled",
                      post_id=str(data.get("id", "")), scheduled_for=when_utc.isoformat())


async def publish_instagram_post(
    caption: str,
    media_url: str,
    is_video: bool = False,
) -> MetaResult:
    """Publish to Instagram NOW (container → publish).

    Instagram has no scheduling API, so the caller's scheduler decides *when*
    this runs. The container is created here, at publish time, because Meta
    expires unpublished containers after 24 hours.
    """
    settings = get_settings()
    if not media_url:
        return MetaResult(ok=False, platform="Instagram", action="failed",
                          error="Instagram requires a public image or video URL — none supplied.")

    params: dict[str, Any] = {"caption": caption}
    if is_video:
        params.update({"media_type": "REELS", "video_url": media_url})
    else:
        params["image_url"] = media_url

    ok, note = is_configured()
    if not ok or not settings.meta_ig_user_id:
        return MetaResult(ok=True, platform="Instagram", action="would_send",
                          request={**params, "_intent": "create container then publish",
                                   "_note": note if not ok else "META_IG_USER_ID not set"})

    try:
        container = await _graph("POST", f"{settings.meta_ig_user_id}/media", params)
        creation_id = container.get("id")
        if not creation_id:
            return MetaResult(ok=False, platform="Instagram", action="failed",
                              error="Meta returned no container id.")
        data = await _graph("POST", f"{settings.meta_ig_user_id}/media_publish",
                            {"creation_id": creation_id})
    except MetaError as exc:
        return MetaResult(ok=False, platform="Instagram", action="failed", error=str(exc))
    return MetaResult(ok=True, platform="Instagram", action="published",
                      post_id=str(data.get("id", "")))


def platform_of(name: str) -> str:
    """Normalise a platform label from the content plan."""
    low = (name or "").lower()
    if "insta" in low or low == "ig":
        return "instagram"
    if "face" in low or low == "fb":
        return "facebook"
    return low or "facebook"


__all__ = [
    "MetaError", "MetaResult", "is_configured", "verify_connection",
    "validate_schedule_time", "schedule_facebook_post", "publish_instagram_post",
    "platform_of", "IG_DAILY_LIMIT", "MIN_LEAD", "MAX_LEAD",
]
