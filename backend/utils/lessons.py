"""Learned lessons — the memory that makes ZYNTH get better, better, better.

The self-improvement loop distils recurring mistakes into durable LESSONS. Those
lessons are the whole point: they are rendered into a knowledge file
(`knowledge/01_learned_lessons.md`) which `utils/knowledge.py` injects into EVERY
agent's system prompt. So a lesson learned once changes how the entire agency
behaves on every future run — the flywheel.

Source of truth is the committed pool JSON (survives redeploys); the markdown is
regenerated from it and the prompt cache refreshed so lessons take effect at once.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

_JSON = Path("outputs/proposal_pool/lessons.json")
_CAP = 80  # keep the injected block bounded


def _md_path() -> Path:
    try:
        from utils.knowledge import KNOWLEDGE_DIR
        return KNOWLEDGE_DIR / "01_learned_lessons.md"
    except Exception:
        return Path(__file__).resolve().parent.parent / "knowledge" / "01_learned_lessons.md"


def _load() -> list[dict]:
    if _JSON.exists():
        try:
            return json.loads(_JSON.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(rows: list[dict]) -> None:
    _JSON.parent.mkdir(parents=True, exist_ok=True)
    _JSON.write_text(json.dumps(rows[-_CAP:], ensure_ascii=False, indent=2), encoding="utf-8")


def all_lessons() -> list[dict]:
    return _load()


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


def add(area: str, lesson: str, source: str = "improver") -> bool:
    """Add a lesson if it's genuinely new. Returns True if added. Refreshes prompts."""
    lesson = (lesson or "").strip()
    if len(lesson) < 8:
        return False
    rows = _load()
    key = _norm(lesson)[:60]
    for r in rows:
        if _norm(r.get("lesson", ""))[:60] == key:  # already know this
            return False
    rows.append({
        "at": datetime.now().strftime("%Y-%m-%d"),
        "area": (area or "general")[:40],
        "lesson": lesson[:400],
        "source": source[:40],
    })
    _save(rows)
    write_md()
    refresh_prompt_cache()
    return True


def add_many(items: list[dict], source: str = "improver") -> int:
    n = 0
    for it in items or []:
        if add(it.get("area", "general"), it.get("lesson", ""), source):
            n += 1
    return n


def write_md() -> str:
    """Render lessons into the injected knowledge file. Grouped by area."""
    rows = _load()
    lines = [
        "# 01 — Learned Lessons (auto-updated by the self-improvement loop)",
        "",
        "> These are hard-won lessons from ZYNTH's own past work and mistakes. They are",
        "> binding: do not repeat the mistakes they encode. The self-improvement agent",
        "> adds to this file every cycle — the agency gets better, better, better.",
        "",
    ]
    if not rows:
        lines.append("_No lessons recorded yet._")
    else:
        by_area: dict[str, list[dict]] = {}
        for r in rows:
            by_area.setdefault(r.get("area", "general"), []).append(r)
        for area in sorted(by_area):
            lines.append(f"## {area}")
            for r in by_area[area]:
                lines.append(f"- {r['lesson']}  _(learned {r.get('at','')})_")
            lines.append("")
    text = "\n".join(lines).strip() + "\n"
    try:
        p = _md_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    except Exception:
        pass
    return text


def refresh_prompt_cache() -> None:
    """Force every agent to pick up the new lessons on their next call."""
    try:
        from utils.knowledge import load_knowledge
        load_knowledge(force=True)
    except Exception:
        pass


def sync_from_pool() -> None:
    """Regenerate the markdown from the pool JSON (call at startup)."""
    write_md()
    refresh_prompt_cache()


def summary_line() -> str:
    rows = _load()
    if not rows:
        return "No lessons yet."
    areas = {}
    for r in rows:
        areas[r.get("area", "general")] = areas.get(r.get("area", "general"), 0) + 1
    top = ", ".join(f"{a} ({n})" for a, n in sorted(areas.items(), key=lambda x: -x[1])[:4])
    return f"{len(rows)} lessons · {top}"
