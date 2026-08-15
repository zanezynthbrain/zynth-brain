#!/usr/bin/env python3
"""Inject the shared ZYNTH operating-contract pointer into every skill entry point.

The detailed standard lives in one maintained source. This migration deliberately
adds only a concise pointer, preserving specialist skill methods and preventing
36 divergent copies of governance language.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".claude" / "skills"
MARKER = "## ZYNTH Operating Contract"
BLOCK = """## ZYNTH Operating Contract

Follow the shared [ZYNTH Capability System Standard](../../../docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md). In particular: classify the work band; separate verified facts from assumptions; create three distinct territories for material creative work; make output executable and measurable; pass the relevant quality gate; and preserve founder/project-owner approval before external release, spend, client contact, vendor commitment, or publication.

"""


def inject(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    # Preserve frontmatter and place the standard directly after the first H1.
    first_h1 = text.find("\n# ")
    if first_h1 < 0:
        raise ValueError(f"No H1 found: {path}")
    heading_end = text.find("\n", first_h1 + 1)
    if heading_end < 0:
        heading_end = len(text)
    updated = text[:heading_end + 1] + "\n" + BLOCK + text[heading_end + 1:]
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for path in sorted(SKILL_ROOT.glob("*/SKILL.md")):
        if inject(path):
            changed.append(path.parent.name)
    print(f"Updated {len(changed)} skill(s): {', '.join(changed)}")


if __name__ == "__main__":
    main()
