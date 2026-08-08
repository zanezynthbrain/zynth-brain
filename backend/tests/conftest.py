import os
import sys

import pytest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

# Force mock mode + disable network for deterministic, offline test runs,
# regardless of what's in the developer's local .env.
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["ZYNTH_ALLOW_NETWORK"] = "false"

from config import get_settings  # noqa: E402

get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _never_write_the_real_knowledge_file(tmp_path, monkeypatch):
    """Keep the suite from mutating tracked repo files.

    ``lessons._JSON`` is relative, so ``monkeypatch.chdir(tmp_path)`` isolates
    it — but ``lessons._md_path()`` resolves from KNOWLEDGE_DIR/``__file__`` and
    is absolute, so it wrote straight into ``backend/knowledge/`` on every run.
    That re-stamped the lesson's "learned" date daily and left the working tree
    dirty after a plain ``pytest``.

    Resolution happens at call time and defers to ``KNOWLEDGE_DIR`` whenever a
    test has pointed it somewhere of its own — so tests that assert on the
    markdown still work — and only falls back to this fixture's temp file. The
    one path it will never return is the real repo file.
    """
    try:
        from utils import lessons
        import utils.knowledge as kb
    except Exception:                       # not importable in some runs
        yield
        return

    real_dir = (BACKEND_ROOT / "knowledge").resolve()
    # Distinct dir name: tests use tmp_path/"knowledge" themselves and call
    # mkdir() without exist_ok, so this must never collide with theirs.
    fallback = tmp_path / "_lessons_isolation" / "01_learned_lessons.md"
    fallback.parent.mkdir(parents=True, exist_ok=True)

    def _safe_md_path():
        current = getattr(kb, "KNOWLEDGE_DIR", None)
        if current is not None and Path(current).resolve() != real_dir:
            return Path(current) / "01_learned_lessons.md"
        return fallback

    monkeypatch.setattr(lessons, "_md_path", _safe_md_path)
    yield
