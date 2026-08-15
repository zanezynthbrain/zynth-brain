"""Minimal smoke check for the real-data ZYNTH Second Brain model."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT / "backend")
sys.path.insert(0, str(ROOT / "backend"))

from utils.second_brain import build_state  # noqa: E402
from utils.second_brain_ui import render  # noqa: E402


state = build_state()
node_ids = {node["id"] for node in state["nodes"]}
required = {
    "hub:core", "hub:capability", "hub:knowledge", "hub:operations",
    "hub:outputs", "hub:monitoring", "hub:learning", "doc:capability-standard",
}
missing = sorted(required - node_ids)
if missing:
    raise SystemExit(f"Missing required Second Brain nodes: {', '.join(missing)}")
if not state["clusters"] or not state["edges"]:
    raise SystemExit("Second Brain must contain both clusters and relationships")
html = render(state)
for marker in ("ZYNTH SECOND BRAIN", "__STATE__", "Live system sphere"):
    if marker == "__STATE__":
        if marker in html:
            raise SystemExit("Second Brain state was not embedded into UI")
    elif marker not in html:
        raise SystemExit(f"Second Brain UI missing expected marker: {marker}")
print(
    "Second Brain smoke check passed: "
    f"{len(state['nodes'])} nodes · {len(state['edges'])} relationships · "
    f"{state['summary']['alerts']} current signals"
)
