"""Business knowledge base — feeds real ZYNTH context into every agent.

Drop Markdown files into ``backend/knowledge/`` (exported from Obsidian or
written by hand) and every agent automatically reads them as part of its
system prompt. This is how the AI team knows ZYNTH's actual services,
clients, SOPs, and market position instead of guessing.

Rules:
  - Only ``*.md`` files are loaded.
  - ``README.md`` is documentation for humans — always skipped.
  - Files still containing the ``<!-- TEMPLATE -->`` marker are skipped,
    so unfilled starter templates never pollute agent prompts.
  - Each file is capped and the total block is budgeted so knowledge
    never blows up token costs.
"""

from __future__ import annotations

from pathlib import Path

# knowledge/ sits next to agents/ and utils/ inside backend/, so this
# resolves correctly both locally and in the Docker image (/app/knowledge).
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

_TEMPLATE_MARKER = "<!-- TEMPLATE -->"
_PER_FILE_CHAR_CAP = 6_000
_TOTAL_CHAR_BUDGET = 24_000

_cache: str | None = None


def list_knowledge_files() -> list[tuple[str, int, bool]]:
    """Return (filename, size_bytes, active) for every .md file in knowledge/."""
    if not KNOWLEDGE_DIR.is_dir():
        return []
    entries: list[tuple[str, int, bool]] = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        active = path.name.lower() != "readme.md" and _TEMPLATE_MARKER not in text[:300]
        entries.append((path.name, len(text.encode("utf-8")), active))
    return entries


def load_knowledge(force: bool = False) -> str:
    """Return the combined knowledge block for system prompts ('' if none)."""
    global _cache
    if _cache is not None and not force:
        return _cache

    sections: list[str] = []
    total = 0
    if KNOWLEDGE_DIR.is_dir():
        for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            try:
                text = path.read_text(encoding="utf-8").strip()
            except Exception:
                continue
            if not text or _TEMPLATE_MARKER in text[:300]:
                continue
            if len(text) > _PER_FILE_CHAR_CAP:
                text = text[:_PER_FILE_CHAR_CAP] + "\n[...truncated]"
            if total + len(text) > _TOTAL_CHAR_BUDGET:
                break
            sections.append(f"### {path.stem.replace('_', ' ').title()}\n{text}")
            total += len(text)

    _cache = (
        "\n\n--- ZYNTH BUSINESS KNOWLEDGE (real internal context — always use this "
        "over generic assumptions) ---\n\n" + "\n\n".join(sections)
        if sections
        else ""
    )
    return _cache
