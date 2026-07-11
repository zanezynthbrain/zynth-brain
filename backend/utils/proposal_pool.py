"""Proposal Pool — local JSON data pool for AI-generated Event & Campaign proposals.

Proposals are stored as:
  outputs/proposal_pool/{industry_slug}/{month_lower}.json   ← one file per combo
  outputs/proposal_pool/index.json                          ← master index

Each batch file holds an array of proposal objects for that industry × month.
New batches are appended to the existing file so re-running the same combo
accumulates proposals rather than overwriting them.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

_DEFAULT_DIR = Path("outputs/proposal_pool")


def _slug(text: str) -> str:
    return (
        text.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "_")
        .strip("_-")
    )


class ProposalPool:
    def __init__(self, base_dir: Path | str = _DEFAULT_DIR):
        self._dir = Path(base_dir)
        self._index_path = self._dir / "index.json"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._index: list[dict] = self._load_index()

    # ── persistence ───────────────────────────────────────────────────────────

    def _load_index(self) -> list[dict]:
        if self._index_path.exists():
            try:
                return json.loads(self._index_path.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save_index(self) -> None:
        self._index_path.write_text(
            json.dumps(self._index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ── write ─────────────────────────────────────────────────────────────────

    def add_batch(
        self,
        industry: str,
        month: str,
        market: str,
        proposals: list[dict[str, Any]],
    ) -> list[str]:
        """Persist a batch of proposals and update the index. Returns assigned IDs."""
        folder = self._dir / _slug(industry)
        folder.mkdir(parents=True, exist_ok=True)
        batch_path = folder / f"{month.lower()}.json"

        # Load existing proposals for this combo (accumulate, don't overwrite)
        existing: list[dict] = []
        if batch_path.exists():
            try:
                existing = json.loads(batch_path.read_text(encoding="utf-8"))
            except Exception:
                existing = []

        ids: list[str] = []
        now = datetime.now().isoformat()
        rel_path = str(batch_path.relative_to(self._dir))

        for p in proposals:
            pid = str(uuid.uuid4())[:8]
            p["proposal_id"] = pid
            p["industry"] = industry
            p["market"] = market
            p["month"] = month
            p["created_at"] = now
            existing.append(p)
            ids.append(pid)

            self._index.append({
                "proposal_id": pid,
                "title": p.get("title", ""),
                "type": p.get("type", ""),
                "industry": industry,
                "market": market,
                "month": month,
                "created_at": now,
                "file": rel_path,
            })

        batch_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        self._save_index()
        return ids

    # ── read ──────────────────────────────────────────────────────────────────

    def search(
        self,
        industry: str | None = None,
        month: str | None = None,
        market: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Return most-recent matching index entries (newest first)."""
        results = list(self._index)
        if industry:
            results = [r for r in results if industry.lower() in r.get("industry", "").lower()]
        if month:
            results = [r for r in results if month.lower() == r.get("month", "").lower()]
        if market:
            results = [r for r in results if market.upper() == r.get("market", "").upper()]
        return list(reversed(results[-limit:]))

    def load_batch(self, industry: str, month: str) -> list[dict]:
        """Load all proposals for an industry × month combo."""
        path = self._dir / _slug(industry) / f"{month.lower()}.json"
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def covered_combos(self) -> set[tuple[str, str, str]]:
        """Set of (industry, month, market) already generated."""
        return {(r["industry"], r["month"], r["market"]) for r in self._index}

    def get_stats(self) -> dict[str, Any]:
        total = len(self._index)
        industries: dict[str, int] = {}
        months: dict[str, int] = {}
        markets: dict[str, int] = {}
        for r in self._index:
            ind = r.get("industry", "?")
            industries[ind] = industries.get(ind, 0) + 1
            m = r.get("month", "?")
            months[m] = months.get(m, 0) + 1
            mk = r.get("market", "?")
            markets[mk] = markets.get(mk, 0) + 1
        return {
            "total": total,
            "by_industry": dict(sorted(industries.items(), key=lambda x: -x[1])),
            "by_month": months,
            "by_market": markets,
        }
