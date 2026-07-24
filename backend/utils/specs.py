"""Seven-block agent spec loader.

Each agent can have a deep spec at `backend/agents/specs/<agent_key>.md` that is
injected into its system prompt — turning a one-line role into a full charter:
Mandate · Capability model · Method library (ZYNTH IP) · Input contract ·
Output contract · Decision rules (incl. financial law) · Handoff protocol.

Gracefully returns "" if no spec exists, so agents without one are unaffected.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_SPECS_DIR = Path(__file__).resolve().parent.parent / "agents" / "specs"
_MAX_CHARS = 6000  # keep per-agent injection bounded


@lru_cache(maxsize=64)
def load_spec(agent_key: str) -> str:
    """Return the spec block for an agent, or '' if none. Cached per process."""
    if not agent_key:
        return ""
    path = _SPECS_DIR / f"{agent_key}.md"
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""
    if not text:
        return ""
    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS] + "\n…(spec truncated)"
    return f"\n\n===== YOUR OPERATING SPEC (follow exactly) =====\n{text}\n===== END SPEC =====\n"
