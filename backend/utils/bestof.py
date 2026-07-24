"""Rotating best-of proposal pool — the bar that only rises.

Instead of one fixed few-shot exemplar, we keep the top-3 Critic-scored approved
proposals (skeletonised, ~8-10k chars total) as the gold-standard references
injected into every new proposal prompt. When a new proposal out-scores the
lowest of the three, it rotates in. So every proposal competes with our best.

Seeded by backend/data/proposal_exemplar.md until real approved proposals exist.
Persisted to outputs/proposal_pool/bestof.json (survives redeploys).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

_FILE = Path("outputs/proposal_pool/bestof.json")
_EXEMPLAR = Path(__file__).resolve().parent.parent / "data" / "proposal_exemplar.md"
_MAX = 3
_TOTAL_BUDGET = 10000  # chars across all references
_PER = _TOTAL_BUDGET // _MAX


def _load() -> list[dict]:
    if _FILE.exists():
        try:
            return json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(rows: list[dict]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def _skeletonise(text: str) -> str:
    """Trim a proposal to a reference skeleton within the per-item budget."""
    text = (text or "").strip()
    return text[:_PER] + ("…" if len(text) > _PER else "")


def consider(title: str, proposal_text: str, score: float) -> bool:
    """Offer an approved, Critic-scored proposal to the pool. Returns True if it
    rotated in (either filled a slot or beat the lowest of the top-3)."""
    rows = _load()
    entry = {
        "title": title, "score": round(float(score), 2),
        "skeleton": _skeletonise(proposal_text),
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    if len(rows) < _MAX:
        rows.append(entry)
        rows.sort(key=lambda r: r.get("score", 0), reverse=True)
        _save(rows)
        return True
    lowest = min(rows, key=lambda r: r.get("score", 0))
    if entry["score"] > lowest.get("score", 0):
        rows.remove(lowest)
        rows.append(entry)
        rows.sort(key=lambda r: r.get("score", 0), reverse=True)
        _save(rows)
        return True
    return False


def best_of_block() -> str:
    """Return the few-shot gold-standard reference block for proposal prompts.
    Falls back to the seed exemplar until real approved proposals exist."""
    rows = _load()
    if not rows:
        try:
            seed = _EXEMPLAR.read_text(encoding="utf-8")
        except Exception:
            return ""
        return (
            "\n\n=== GOLD-STANDARD REFERENCE (match or beat this) ===\n"
            f"{seed[:_TOTAL_BUDGET]}\n=== END REFERENCE ===\n"
        )
    parts = [
        f"[Best-of #{i+1} · Critic {r.get('score')}/10 · {r.get('title','')}]\n{r.get('skeleton','')}"
        for i, r in enumerate(rows)
    ]
    return (
        "\n\n=== GOLD-STANDARD REFERENCES — your proposal must match or beat these ===\n"
        + "\n\n".join(parts)
        + "\n=== END REFERENCES ===\n"
    )
