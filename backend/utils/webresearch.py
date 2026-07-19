"""Best-effort live web research for proposals — closes the gap with
one-shot research agents (Manus etc.) that browse the web at generation time.

The ZYNTH proposal agent generates from its baked-in knowledge + databases.
This helper adds a thin layer of LIVE market context (real venue names,
vendor signals, recent market notes) pulled at generation time, so a fresh
proposal reflects what's actually out there — not just what was in the image.

Design rules (match fx.py):
  * Best-effort only. Network is flaky / may be bot-blocked. NEVER raise into
    the caller — a failed fetch just returns "" and generation proceeds.
  * Cheap + capped. A few short result snippets, trimmed to a small budget,
    so it costs almost nothing in prompt tokens.
  * Uses the standard proxy via httpx trust_env (default) — no TLS tampering.
"""

from __future__ import annotations

import re

import httpx

from utils.logging_config import get_logger

logger = get_logger("webresearch")

_DDG_HTML = "https://html.duckduckgo.com/html/"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

_SNIPPET_CAP = 220   # chars per snippet
_TOTAL_CAP = 1400    # chars for the whole research block
_MAX_RESULTS = 5


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


async def _search(query: str, timeout: float = 12.0) -> list[str]:
    """Return a few 'title — snippet' strings for a query (best-effort)."""
    try:
        async with httpx.AsyncClient(
            timeout=timeout, headers=_HEADERS, follow_redirects=True, trust_env=True
        ) as client:
            resp = await client.post(_DDG_HTML, data={"q": query})
            resp.raise_for_status()
            html = resp.text
    except Exception as exc:
        logger.info("Web research unavailable for %r (%s).", query[:40], type(exc).__name__)
        return []

    results: list[str] = []
    # DDG HTML: result titles in a.result__a, snippets in a.result__snippet
    titles = re.findall(r'result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    for i, title in enumerate(titles[:_MAX_RESULTS]):
        t = _clean(title)
        s = _clean(snippets[i]) if i < len(snippets) else ""
        line = (f"{t} — {s}" if s else t)[:_SNIPPET_CAP]
        if t:
            results.append(line)
    return results


def _queries(brief: str) -> list[str]:
    b = (brief or "").strip()
    if not b:
        return []
    short = b[:80]
    # A small, targeted set — venue, vendor, and market signal.
    return [
        f"{short} Yangon event venue 2026",
        f"{short} Myanmar event production vendor",
        f"{short} Myanmar market 2026",
    ]


async def research_block(brief: str) -> str:
    """A compact LIVE MARKET CONTEXT block for the proposal prompt, or ''."""
    lines: list[str] = []
    seen: set[str] = set()
    for q in _queries(brief):
        for item in await _search(q):
            key = item[:60].lower()
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"- {item}")
        if sum(len(x) for x in lines) > _TOTAL_CAP:
            break

    if not lines:
        return ""

    block = "\n".join(lines)
    if len(block) > _TOTAL_CAP:
        block = block[:_TOTAL_CAP].rsplit("\n", 1)[0]
    return (
        "\n\n===== LIVE MARKET CONTEXT (fetched now, best-effort — verify before "
        "quoting) =====\n"
        f"{block}\n"
        "Use these only as current signals (real venue/vendor names, market notes). "
        "Anything used in a client-facing number must be tagged 'Indicative' until "
        "confirmed. Do NOT invent citations.\n"
        "===== END LIVE MARKET CONTEXT =====\n"
    )
