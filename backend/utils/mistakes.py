"""Mistake / weakness log — the raw material the self-improvement loop learns from.

Anywhere the system fails, falls short, or gets a 'revise' verdict, record it here.
The ImproverAgent reads recent entries, finds the recurring patterns, and turns
them into durable lessons (utils/lessons.py) that feed back into every agent.

Cheap, dependency-free, persisted in the committed proposal pool so it survives
redeploys.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

_FILE = Path("outputs/proposal_pool/mistakes.json")
_CAP = 400  # keep the log bounded


def _load() -> list[dict]:
    if _FILE.exists():
        try:
            return json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(rows: list[dict]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(rows[-_CAP:], ensure_ascii=False, indent=2), encoding="utf-8")


def record(area: str, what: str, detail: str = "", severity: str = "warn") -> None:
    """Log one mistake/shortfall. Never raises — self-observation must not crash work."""
    try:
        rows = _load()
        rows.append({
            "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "area": (area or "general")[:40],
            "what": (what or "")[:300],
            "detail": (detail or "")[:500],
            "severity": severity if severity in ("info", "warn", "error") else "warn",
        })
        _save(rows)
    except Exception:
        pass


def recent(n: int = 40) -> list[dict]:
    return _load()[-n:][::-1]


def stats() -> dict:
    rows = _load()
    by_area: dict[str, int] = {}
    for r in rows:
        by_area[r.get("area", "general")] = by_area.get(r.get("area", "general"), 0) + 1
    return {"total": len(rows), "by_area": by_area}


def digest(n: int = 40) -> str:
    """Compact text block of recent mistakes for the improver's prompt."""
    rows = recent(n)
    if not rows:
        return "(no logged mistakes yet — infer weaknesses from the activity + metrics instead)"
    return "\n".join(f"- [{r['area']}/{r['severity']}] {r['what']}" + (f" — {r['detail']}" if r['detail'] else "")
                     for r in rows)
