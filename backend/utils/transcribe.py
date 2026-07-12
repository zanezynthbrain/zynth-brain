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


def has_transcription() -> bool:
    return bool(get_settings().gemini_api_key)


async def transcribe_voice(audio: bytes, mime_type: str = "audio/ogg") -> str:
    """Transcribe a voice clip. Raises on failure; caller shows the error."""
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
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(url, params={"key": settings.gemini_api_key}, json=payload)
        resp.raise_for_status()
        data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    logger.info("Transcribed %d bytes of audio -> %d chars", len(audio), len(text))
    return text
