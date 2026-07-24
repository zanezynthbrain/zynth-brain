#!/usr/bin/env python3
"""Refresh bridge/ — the one-pass build-state snapshot for the MD's consultant.

Copies the latest HANDOFF.md + CONTEXT.md + backend/knowledge/*.md into the
repo-root bridge/ folder. Run at the end of every working session:

    python backend/tools/refresh_bridge.py

Part of the session definition-of-done (see CONTEXT.md Standing Rules).
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root
BRIDGE = ROOT / "bridge"


def main() -> None:
    BRIDGE.mkdir(exist_ok=True)
    copied: list[str] = []

    for name in ("HANDOFF.md", "CONTEXT.md"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, BRIDGE / name)
            copied.append(name)

    kb_src = ROOT / "backend" / "knowledge"
    if kb_src.is_dir():
        kb_dst = BRIDGE / "knowledge"
        kb_dst.mkdir(exist_ok=True)
        for md in sorted(kb_src.glob("*.md")):
            shutil.copy2(md, kb_dst / md.name)
            copied.append(f"knowledge/{md.name}")

    print(f"bridge/ refreshed — {len(copied)} files:")
    for c in copied:
        print(f"  · {c}")


if __name__ == "__main__":
    main()
