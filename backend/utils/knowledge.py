"""Business knowledge base — feeds real ZYNTH context into every agent.

Three sources, all Markdown, merged at read time:
  1. backend/knowledge/*.md      — curated agency knowledge (baked in image)
  2. vault/**/*.md               — Obsidian vault synced via Obsidian Git
                                    (reaches the bot on the next redeploy)
  3. outputs/proposal_pool/vault/**/*.md — instant /note captures, persisted
                                    by the daily pool commit (live, no redeploy)

Every agent reads all three as part of its system prompt, so the AI team
knows ZYNTH's actual services, clients, SOPs, notes, and market position
instead of guessing.

Rules:
  - Only ``*.md`` files. ``README.md`` is skipped (human docs).
  - Files containing ``<!-- TEMPLATE -->`` in the first 300 chars are skipped.
  - Per-file and total char budgets keep token cost bounded.
"""

from __future__ import annotations

from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = _BACKEND / "knowledge"
# Obsidian Git sync target and instant-capture folder. Two vault-root
# candidates cover both layouts: local repo (../vault next to backend/) and
# the Docker image (backend copied to /app, vault copied to /app/vault).
VAULT_DIRS = [
    _BACKEND.parent / "vault",   # local: zynth-brain/vault
    _BACKEND / "vault",          # docker: /app/vault
    Path("outputs/proposal_pool/vault"),  # instant /note captures
]

_TEMPLATE_MARKER = "<!-- TEMPLATE -->"
_PER_FILE_CHAR_CAP = 6_000
_TOTAL_CHAR_BUDGET = 30_000
_VAULT_PER_FILE_CAP = 2_500  # notes are many + small; keep each tight

_cache: str | None = None


def _iter_md(root: Path, recursive: bool) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.rglob("*.md") if recursive else root.glob("*.md"))


def list_knowledge_files() -> list[tuple[str, int, bool]]:
    """Return (name, size_bytes, active) for curated + vault markdown files."""
    entries: list[tuple[str, int, bool]] = []
    paths = _iter_md(KNOWLEDGE_DIR, recursive=False)
    for root in VAULT_DIRS:
        paths += _iter_md(root, recursive=True)
    for path in paths:
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

    def _add(paths: list[Path], cap: int) -> None:
        nonlocal total
        for path in paths:
            if path.name.lower() == "readme.md":
                continue
            try:
                text = path.read_text(encoding="utf-8").strip()
            except Exception:
                continue
            if not text or _TEMPLATE_MARKER in text[:300]:
                continue
            if len(text) > cap:
                text = text[:cap] + "\n[...truncated]"
            if total + len(text) > _TOTAL_CHAR_BUDGET:
                return
            sections.append(f"### {path.stem.replace('_', ' ').title()}\n{text}")
            total += len(text)

    _add(_iter_md(KNOWLEDGE_DIR, recursive=False), _PER_FILE_CHAR_CAP)
    for root in VAULT_DIRS:
        _add(_iter_md(root, recursive=True), _VAULT_PER_FILE_CAP)

    _cache = (
        "\n\n--- ZYNTH BUSINESS KNOWLEDGE (real internal context — always use this "
        "over generic assumptions) ---\n\n" + "\n\n".join(sections)
        if sections
        else ""
    )
    return _cache
