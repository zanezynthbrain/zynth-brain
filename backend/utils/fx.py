"""Myanmar market exchange rates (NOT the central bank reference rate).

The MD's rule: every proposal and budget uses the real market rate
(e.g. marketratedaily.com), never the CBM official rate — the gap is
roughly 2x and mispricing a quote by that much is fatal.

Three-layer source of truth:
  1. Live fetch from marketratedaily.com (may be bot-blocked — best effort)
  2. Last successful fetch / manual override, cached in outputs/fx_cache.json
  3. Env-configured defaults (ZYNTH_FX_USD="4290/4400" style)

`get_rates()` and `rates_block()` are synchronous and never hit the
network — safe to call from prompt builders. `refresh_rates()` is async
and is called at bot startup, daily by the scheduler, and via /fx.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import httpx

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("fx")

_SITE_URL = "https://marketratedaily.com/rates"
_CACHE_PATH = Path("outputs/fx_cache.json")
_CURRENCIES = ("USD", "SGD", "THB")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

_memory: dict | None = None  # {"rates": {...}, "source": str, "updated": str}


def _env_defaults() -> dict:
    s = get_settings()
    rates: dict[str, dict[str, float]] = {}
    for cur, raw in (("USD", s.fx_usd), ("SGD", s.fx_sgd), ("THB", s.fx_thb)):
        try:
            buy, sell = (float(x.replace(",", "")) for x in raw.split("/"))
            rates[cur] = {"buy": buy, "sell": sell}
        except Exception:
            continue
    return {"rates": rates, "source": "manual defaults", "updated": "env"}


def _load_cache() -> dict | None:
    try:
        if _CACHE_PATH.exists():
            return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _save_cache(data: dict) -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:  # cache is best-effort
        pass


def get_rates() -> dict:
    """Best available rates, synchronously (memory → file cache → env)."""
    global _memory
    if _memory:
        return _memory
    cached = _load_cache()
    if cached and cached.get("rates"):
        _memory = cached
        return cached
    _memory = _env_defaults()
    return _memory


def set_manual(currency: str, buy: float, sell: float) -> dict:
    """MD manually updates a rate from Telegram (/fx set usd 4290 4400)."""
    data = get_rates()
    rates = dict(data.get("rates", {}))
    rates[currency.upper()] = {"buy": buy, "sell": sell}
    updated = {
        "rates": rates,
        "source": "manual (MD via /fx)",
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    global _memory
    _memory = updated
    _save_cache(updated)
    return updated


async def refresh_rates() -> tuple[bool, dict]:
    """Try a live fetch. Returns (fetched_live, current_best_rates)."""
    try:
        async with httpx.AsyncClient(timeout=20, headers=_HEADERS, follow_redirects=True) as client:
            resp = await client.get(_SITE_URL)
            resp.raise_for_status()
            html = resp.text
    except Exception as exc:
        logger.info("Live FX fetch unavailable (%s) — using cache/manual.", type(exc).__name__)
        return False, get_rates()

    rates: dict[str, dict[str, float]] = {}
    text = re.sub(r"<[^>]+>", " ", html)  # crude de-tag: rows become "USD ... 4,290 4,400"
    for cur in _CURRENCIES:
        m = re.search(cur + r"[^0-9]{1,80}?([\d,]+(?:\.\d+)?)[^0-9]{1,40}?([\d,]+(?:\.\d+)?)", text)
        if m:
            buy = float(m.group(1).replace(",", ""))
            sell = float(m.group(2).replace(",", ""))
            if 0 < buy <= sell * 1.2:  # sanity
                rates[cur] = {"buy": buy, "sell": sell}

    if not rates:
        logger.info("Live FX fetch parsed no rates — using cache/manual.")
        return False, get_rates()

    data = {
        "rates": {**get_rates().get("rates", {}), **rates},
        "source": "marketratedaily.com (live)",
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    global _memory
    _memory = data
    _save_cache(data)
    logger.info("Live FX rates refreshed: %s", ", ".join(rates))
    return True, data


def rates_block() -> str:
    """Compact block for agent prompts — always market rate, never CBM."""
    data = get_rates()
    rates = data.get("rates", {})
    if not rates:
        return ""
    lines = [
        f"{cur}/MMK buy {int(v['buy']):,} · sell {int(v['sell']):,}"
        for cur, v in rates.items()
    ]
    return (
        "\n\nMMK MARKET EXCHANGE RATES "
        f"({data.get('source', '?')}, updated {data.get('updated', '?')}): "
        + " | ".join(lines)
        + ". RULE: always convert with these MARKET rates — never the central bank "
        "reference rate (~half the market rate). Use the sell rate when quoting "
        "costs to clients."
    )
