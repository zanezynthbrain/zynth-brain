#!/usr/bin/env python3
"""One command to rebuild everything, in the order that actually works.

    python backend/refresh.py

Order matters and is easy to get wrong by hand:

    1. scan the repo            -> vault-index.json
    2. export .docx             -> deliverables/proposals/docx/ + docx-manifest.json
    3. scan AGAIN               -> the index now carries each proposal's .docx url
    4. build the dashboard      -> zynth-command.html

Skipping step 3 is the bug this script exists to prevent: the dashboard ships
with .docx buttons missing for anything added since the last run.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    ("scan", [sys.executable, "backend/build_vault_index.py"]),
    ("docx", [sys.executable, "backend/tools/proposals_to_docx.py"]),
    ("rescan (picks up the .docx manifest)", [sys.executable, "backend/build_vault_index.py"]),
    ("dashboard", [sys.executable, "backend/build_dashboard.py"]),
]


def main() -> int:
    for label, cmd in STEPS:
        print(f"\n─── {label}")
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout or "").strip()
        if out:
            print("\n".join(out.splitlines()[-6:]))
        if r.returncode != 0:
            print((r.stderr or "").strip()[-800:])
            return r.returncode
    print("\n✓ everything rebuilt — commit and push to update Railway")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
