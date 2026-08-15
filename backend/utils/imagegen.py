"""Image rendering for the design studio — OpenAI Images (gpt-image-1).

The Designer agent always produces a written design spec plus a render prompt.
This module turns those prompts into actual PNG files when an OpenAI key is
configured; without a key it returns a clean "not configured" result and the
studio still delivers the full spec pack. Nothing here is required for the
studio to work — rendering is the bonus layer, not the deliverable.

Cost discipline (same rules as the LLM path):
  - Rendering NEVER happens automatically inside a pipeline run. The bot asks
    first, then calls render_batch() on the MD's tap.
  - Hard cap per run (ZYNTH_MAX_IMAGES_PER_RUN, default 4).
  - Every render is logged with an estimated cost so /costaudit can see it.
"""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("utils.imagegen")

_API_URL = "https://api.openai.com/v1/images/generations"
_OUT_DIR = Path("outputs/designs")

#: Indicative USD per image for gpt-image-1 at standard quality, by size.
#: Used for the cost note shown to the MD — not a billing source of truth.
_EST_USD = {"1024x1024": 0.04, "1024x1536": 0.06, "1536x1024": 0.06}

#: Platform aspect → the sizes the API accepts.
SIZE_FOR_FORMAT = {
    "square": "1024x1024",       # 1:1 feed post
    "portrait": "1024x1536",     # 4:5 feed / 9:16 story-safe crop
    "story": "1024x1536",        # 9:16
    "reel": "1024x1536",
    "landscape": "1536x1024",    # 16:9 / LinkedIn
    "carousel": "1024x1024",
}


@dataclass
class RenderedImage:
    """One render attempt — success carries a path, failure carries a reason."""

    prompt: str
    label: str
    path: Path | None = None
    error: str = ""
    est_usd: float = 0.0

    @property
    def ok(self) -> bool:
        return self.path is not None


def is_configured() -> bool:
    """Whether image rendering can actually run (OpenAI key present)."""
    settings = get_settings()
    return bool(getattr(settings, "openai_api_key", "") and settings.allow_network)


def status_note() -> str:
    """One line explaining the current rendering capability, for the MD."""
    settings = get_settings()
    if not getattr(settings, "openai_api_key", ""):
        return ("Image rendering OFF — set OPENAI_API_KEY (and ZYNTH_ALLOW_NETWORK=true) "
                "to render artwork. Design specs and prompts are produced either way.")
    if not settings.allow_network:
        return "Image rendering OFF — OPENAI_API_KEY is set but ZYNTH_ALLOW_NETWORK=false."
    return f"Image rendering ON — {settings.image_model_name}, max {settings.max_images_per_run} per run."


def size_for(format_hint: str) -> str:
    """Map a content format ('carousel', 'reel', '9:16') to an API size."""
    hint = (format_hint or "").lower()
    for key, size in SIZE_FOR_FORMAT.items():
        if key in hint:
            return size
    if "9:16" in hint or "vertical" in hint:
        return "1024x1536"
    if "16:9" in hint or "wide" in hint:
        return "1536x1024"
    return "1024x1024"


async def render_image(prompt: str, label: str = "design", format_hint: str = "square") -> RenderedImage:
    """Render one image. Never raises — failures come back on the result."""
    settings = get_settings()
    if not is_configured():
        return RenderedImage(prompt=prompt, label=label, error=status_note())

    size = size_for(format_hint)
    payload = {
        "model": settings.image_model_name,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    try:
        import httpx

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                _API_URL,
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json=payload,
            )
            if response.status_code >= 400:
                detail = response.text[:300]
                logger.warning("Image render failed (%s): %s", response.status_code, detail)
                return RenderedImage(prompt=prompt, label=label,
                                     error=f"OpenAI {response.status_code}: {detail}")
            data = response.json()
    except Exception as exc:  # noqa: BLE001 — network/SDK errors are reported, not raised
        logger.warning("Image render error: %s", exc)
        return RenderedImage(prompt=prompt, label=label, error=str(exc))

    try:
        item = data["data"][0]
        raw = base64.b64decode(item["b64_json"]) if item.get("b64_json") else None
        if raw is None:
            return RenderedImage(prompt=prompt, label=label,
                                 error="Response contained no image data (URL-only response).")
    except Exception as exc:  # noqa: BLE001
        return RenderedImage(prompt=prompt, label=label, error=f"Unexpected response shape: {exc}")

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in label)[:48] or "design"
    path = _OUT_DIR / f"{datetime.now():%Y%m%d-%H%M%S}_{safe}.png"
    path.write_bytes(raw)
    return RenderedImage(prompt=prompt, label=label, path=path, est_usd=_EST_USD.get(size, 0.04))


async def render_batch(specs: list[dict], limit: int | None = None) -> list[RenderedImage]:
    """Render a list of {prompt, label, format} specs, capped and run in parallel.

    Returns one result per attempted spec (in order). Specs beyond the cap are
    not attempted — the caller reports how many were skipped.
    """
    settings = get_settings()
    cap = limit or settings.max_images_per_run
    batch = specs[: max(0, cap)]
    if not batch:
        return []
    results = await asyncio.gather(*[
        render_image(
            prompt=s.get("prompt", ""),
            label=s.get("label", f"design-{i + 1}"),
            format_hint=s.get("format", "square"),
        )
        for i, s in enumerate(batch)
    ])
    rendered = [r for r in results if r.ok]
    if rendered:
        logger.info("Rendered %d image(s), est US$%.2f", len(rendered), sum(r.est_usd for r in rendered))
    return list(results)


__all__ = [
    "RenderedImage", "is_configured", "status_note", "size_for",
    "render_image", "render_batch", "SIZE_FOR_FORMAT",
]
