#!/usr/bin/env python3
"""ZYNTH — build the command dashboard from the vault index.

    python backend/build_vault_index.py   # scan the repo  -> vault-index.json
    python backend/build_dashboard.py     # inject the data -> zynth-command.html

The template holds no inventory of its own: every proposal, agent, skill, stage
and deliverable it shows comes from the scan. Add a file to the repo, re-run
both scripts, and it is in the interface. Delete one and it is gone.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "backend" / "templates" / "dashboard_template.html"
INDEX = ROOT / "backend" / "outputs" / "vault-index.json"
OUT = ROOT / "backend" / "outputs" / "zynth-command.html"
MARKER = "/*__VAULT_JSON__*/"


def build() -> Path:
    if not INDEX.is_file():
        raise SystemExit("no vault-index.json — run: python backend/build_vault_index.py")
    html = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in html:
        raise SystemExit(f"template is missing the {MARKER} marker")
    data = json.loads(INDEX.read_text(encoding="utf-8"))

    # the marker is followed by a placeholder literal; replace marker+placeholder
    head, _, tail = html.partition(MARKER)
    depth, end = 0, 0
    for i, ch in enumerate(tail):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # </script> inside data would close the tag early
    payload = payload.replace("</", "<\\/")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + payload + tail[end:], encoding="utf-8")
    c = data.get("counts", {})
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")
    print(f"  {c.get('proposals',0)} proposals ({c.get('composed',0)} composed, "
          f"{c.get('pooled',0)} concepts) · {c.get('agents',0)} agents · "
          f"{c.get('skills',0)} skills · {c.get('stages',0)} stages · "
          f"{c.get('deliverables',0)} deliverables")
    return OUT


if __name__ == "__main__":
    build()
