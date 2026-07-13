"""Voice transcription for Telegram voice messages (Burmese + English).

Uses Google Gemini's audio understanding via plain REST (httpx — already a
dependency). Gemini has a generous free tier and handles Burmese, English,
and mixed-language speech well.

Setup: create a free API key at https://aistudio.google.com → set
GEMINI_API_KEY in the environment. Without a key the voice handler
replies with setup instructions instead of failing.
"""

from __future__ import annotations

import base64

import httpx

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("transcribe")

_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

_PROMPT = (
    "Transcribe this voice message exactly as spoken. It may be in Burmese "
    "(Myanmar language), English, or a mix of both. Write Burmese speech in "
    "Burmese script. Return ONLY the transcription text — no commentary, no "
    "labels, no translation."
)


class TranscriptionError(Exception):
    """User-safe transcription failure — message never contains the API key."""


def has_transcription() -> bool:
    return bool(get_settings().gemini_api_key)


async def transcribe_voice(audio: bytes, mime_type: str = "audio/ogg") -> str:
    """Transcribe a voice clip. Raises TranscriptionError with a safe message."""
    settings = get_settings()
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _PROMPT},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(audio).decode(),
                        }
                    },
                ]
            }
        ]
    }
    url = _GEMINI_URL.format(model=settings.transcribe_model_name)
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            # Key goes in the header — newer 'AQ.'-style AI Studio keys are
            # not accepted as a ?key= query param, and headers keep the key
            # out of URLs/logs entirely.
            resp = await client.post(
                url,
                headers={"x-goog-api-key": settings.gemini_api_key},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        # NEVER propagate the raw error — it may reference the request URL.
        status = exc.response.status_code
        detail = ""
        try:
            detail = exc.response.json().get("error", {}).get("message", "")[:200]
        except Exception:
            pass
        logger.warning("Gemini transcription HTTP %s: %s", status, detail)
        if status in (400, 401, 403, 404):
            raise TranscriptionError(
                f"Google rejected the request (HTTP {status}). "
                f"Check GEMINI_API_KEY in Railway Variables. {detail}"
            ) from None
        raise TranscriptionError(f"Google transcription service error (HTTP {status}). Try again.") from None
    except httpx.HTTPError as exc:
        logger.warning("Gemini transcription network error: %s", type(exc).__name__)
        raise TranscriptionError("Network problem reaching Google — try again in a minute.") from None

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise TranscriptionError("Google returned an empty transcription — try a longer/clearer clip.") from None
    logger.info("Transcribed %d bytes of audio -> %d chars", len(audio), len(text))
    return text
