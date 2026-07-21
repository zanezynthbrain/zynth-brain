"""Daily API cost tracker with hard budget enforcement.

Tracks cumulative Anthropic API spend for the current calendar day
(Yangon timezone). Sends Telegram alerts at 80% of daily budget and
blocks further LLM calls at 100%.

Persists to outputs/cost_tracker/YYYY-MM-DD.json so totals survive process
restarts (e.g. if the bot crashes and restarts mid-day).
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path

import pytz

# Anthropic pricing in USD per million tokens (Jul 2026)
_INPUT_PRICE_PER_MTOK: dict[str, float] = {
    "claude-sonnet-4-6": 3.00,
    "claude-sonnet-4-5": 3.00,
    "claude-sonnet-5": 3.00,
    "claude-fable-5": 3.00,
    "claude-haiku-4-5-20251001": 0.80,
    "claude-haiku-4-5": 0.80,
    "claude-opus-4-8": 15.00,
}
_OUTPUT_PRICE_PER_MTOK: dict[str, float] = {
    "claude-sonnet-4-6": 15.00,
    "claude-sonnet-4-5": 15.00,
    "claude-sonnet-5": 15.00,
    "claude-fable-5": 15.00,
    "claude-haiku-4-5-20251001": 4.00,
    "claude-haiku-4-5": 4.00,
    "claude-opus-4-8": 75.00,
}
_DEFAULT_INPUT = 3.00
_DEFAULT_OUTPUT = 15.00
USD_TO_SGD = 1.35


class CostBudgetExceeded(Exception):
    """Raised when the daily S$ budget cap is reached. Callers should abort the LLM call."""


class CostTracker:
    """Async-safe daily cost accumulator with file-backed persistence."""

    def __init__(self, daily_budget_sgd: float = 5.0, output_dir: str = "outputs") -> None:
        self.daily_budget_sgd = daily_budget_sgd
        self._lock = asyncio.Lock()
        self._dir = Path(output_dir) / "cost_tracker"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._alerted_80 = False

    def _today(self) -> str:
        tz = pytz.timezone("Asia/Rangoon")
        return datetime.now(tz).strftime("%Y-%m-%d")

    def _file(self) -> Path:
        return self._dir / f"{self._today()}.json"

    def _load(self) -> dict:
        f = self._file()
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"date": self._today(), "usd": 0.0, "sgd": 0.0, "calls": 0}

    def _save(self, data: dict) -> None:
        self._file().write_text(json.dumps(data, indent=2), encoding="utf-8")

    def call_cost_usd(self, model: str, input_tokens: int, output_tokens: int) -> float:
        in_p = _INPUT_PRICE_PER_MTOK.get(model, _DEFAULT_INPUT)
        out_p = _OUTPUT_PRICE_PER_MTOK.get(model, _DEFAULT_OUTPUT)
        return (input_tokens * in_p + output_tokens * out_p) / 1_000_000

    async def record(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Record a completed API call. Returns cumulative SGD spend today.

        Raises :class:`CostBudgetExceeded` if the daily cap is hit — the
        caller should catch this and abort further LLM work for the day.
        """
        usd = self.call_cost_usd(model, input_tokens, output_tokens)
        sgd = usd * USD_TO_SGD

        async with self._lock:
            data = self._load()
            data["usd"] += usd
            data["sgd"] += sgd
            data["calls"] += 1
            self._save(data)
            total_sgd = data["sgd"]

        pct = total_sgd / self.daily_budget_sgd * 100

        if pct >= 80 and not self._alerted_80:
            self._alerted_80 = True
            await self._alert(
                f"⚠️ <b>Cost Warning</b>\n"
                f"S${total_sgd:.2f} spent today ({pct:.0f}% of S${self.daily_budget_sgd:.0f} limit).\n"
                f"API calls continue but watch spend."
            )

        if total_sgd >= self.daily_budget_sgd:
            await self._alert(
                f"🚫 <b>Daily budget reached</b>\n"
                f"S${total_sgd:.2f} / S${self.daily_budget_sgd:.0f} — halting API calls for today.\n"
                f"Resets at midnight Yangon time."
            )
            raise CostBudgetExceeded(
                f"Daily budget S${self.daily_budget_sgd:.0f} reached (S${total_sgd:.2f} spent)"
            )

        return total_sgd

    async def today_summary(self) -> dict:
        async with self._lock:
            return dict(self._load())

    async def _alert(self, msg: str) -> None:
        try:
            from utils.telegram import send_message  # lazy to avoid circular import
            await send_message(msg)
        except Exception:
            pass


_tracker: CostTracker | None = None
_tracker_lock = asyncio.Lock()


async def get_cost_tracker() -> CostTracker:
    """Return the process-wide singleton CostTracker, initialised from settings."""
    global _tracker
    if _tracker is None:
        from config import get_settings
        s = get_settings()
        budget = getattr(s, "daily_budget_sgd", 5.0)
        _tracker = CostTracker(daily_budget_sgd=budget, output_dir=s.output_dir)
    return _tracker
