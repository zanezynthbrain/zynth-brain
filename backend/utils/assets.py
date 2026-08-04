"""Public asset hosting — the URLs Instagram insists on.

Instagram's publishing API will not accept an uploaded file: it fetches the
image or video from a public URL. The bot already exposes a public HTTP server
on Railway for the dashboard, so assets ride on that rather than adding a
bucket and another credential.

Design:
  - Files live in ``outputs/assets/`` (git-ignored — regenerable artwork).
  - They're served read-only at ``/assets/<name>``, with a token in the path
    when ZYNTH_ASSET_TOKEN is set, so the URL isn't guessable.
  - Only whitelisted extensions are served, and the filename is sanitised, so
    the route can't be walked out of the directory.

If ZYNTH_PUBLIC_URL isn't set, ``public_url`` returns "" and the publisher
reports Instagram as blocked rather than sending Meta a URL it can't fetch.
"""

from __future__ import annotations

import mimetypes
import re
import shutil
from pathlib import Path

from config import get_settings

ASSET_DIR = Path("outputs/assets")

#: What may be served. Instagram accepts JPEG for images and MP4/MOV for video.
ALLOWED = {".png", ".jpg", ".jpeg", ".mp4", ".mov"}

_SAFE = re.compile(r"[^A-Za-z0-9._-]")


def safe_name(name: str) -> str:
    """Reduce any input to a flat, safe filename — no separators survive."""
    flat = Path(name).name
    cleaned = _SAFE.sub("-", flat).lstrip(".-") or "asset"
    return cleaned[:120]


def publish_file(path: str | Path, name: str = "") -> Path:
    """Copy a file into the public asset directory and return its served path."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"No such asset: {source}")
    if source.suffix.lower() not in ALLOWED:
        raise ValueError(f"Refusing to publish {source.suffix} — allowed: {sorted(ALLOWED)}")
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    target = ASSET_DIR / safe_name(name or source.name)
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target


def public_url(name: str) -> str:
    """The URL Meta will fetch, or '' when public hosting isn't configured."""
    settings = get_settings()
    base = (settings.public_url or "").rstrip("/")
    if not base:
        return ""
    token = settings.asset_token
    prefix = f"/assets/{token}" if token else "/assets"
    return f"{base}{prefix}/{safe_name(name)}"


def resolve_request(path: str) -> tuple[Path | None, str]:
    """Map an incoming '/assets/...' request to a file. Returns (path, mimetype).

    Returns (None, "") for anything that isn't a valid, allowed, existing asset
    — including a wrong or missing token.
    """
    settings = get_settings()
    parts = [p for p in path.split("?")[0].split("/") if p]
    if not parts or parts[0] != "assets":
        return None, ""
    rest = parts[1:]
    if settings.asset_token:
        if not rest or rest[0] != settings.asset_token:
            return None, ""
        rest = rest[1:]
    if len(rest) != 1:
        return None, ""
    target = ASSET_DIR / safe_name(rest[0])
    if target.suffix.lower() not in ALLOWED or not target.is_file():
        return None, ""
    return target, mimetypes.guess_type(target.name)[0] or "application/octet-stream"


def hosting_status() -> str:
    """One line on whether Instagram publishing can fetch our media."""
    settings = get_settings()
    if not settings.public_url:
        return ("Asset hosting OFF — set ZYNTH_PUBLIC_URL to the Railway public URL. "
                "Facebook still works (it accepts our upload); Instagram needs the URL.")
    token = " (token-protected)" if settings.asset_token else " (no token — set ZYNTH_ASSET_TOKEN)"
    return f"Asset hosting ON at {settings.public_url.rstrip('/')}/assets{token}"


__all__ = ["ASSET_DIR", "ALLOWED", "safe_name", "publish_file", "public_url",
           "resolve_request", "hosting_status"]
