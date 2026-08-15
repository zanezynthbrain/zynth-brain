#!/usr/bin/env python3
"""Refresh ZYNTH's repository-to-Vault operating-document mirror."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from utils.obsidian import mirror_repo_docs  # noqa: E402


if __name__ == "__main__":
    written = mirror_repo_docs()
    print(f"Mirrored {len(written)} document(s)")
    for path in written:
        print(path)
