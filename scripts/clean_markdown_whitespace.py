#!/usr/bin/env python3
"""Normalize generated markdown whitespace without changing meaningful content."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "vault" / "ZYNTH-OS" / "Roles", ROOT / "vault" / "ZYNTH-OS" / "Skills Index.md"]


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"
    if cleaned == text:
        return False
    path.write_text(cleaned, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for target in TARGETS:
        files = target.glob("*.md") if target.is_dir() else [target]
        for path in files:
            if path.is_file() and normalize(path):
                changed.append(path)
    print(f"Normalized {len(changed)} markdown file(s)")


if __name__ == "__main__":
    main()
