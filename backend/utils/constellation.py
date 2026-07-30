"""Proposal Constellation — a living sphere where every proposal we make is a star.

Reads the real proposal manifest (deliverables/proposals/index.json) and renders the
gold sphere. Each filed proposal becomes a node; the sphere fills as the library grows.
Served on the dashboard at /constellation. When a new proposal is added to the manifest,
the sphere gains a star automatically — no code change.
"""

from __future__ import annotations

import json
from pathlib import Path

_MANIFEST = Path("outputs/proposal_pool/deliverables/proposals/index.json")
_TEMPLATE = Path(__file__).resolve().parent / "constellation_template.html"


def proposals() -> list[dict]:
    """The real proposals, newest first. Empty list if none yet."""
    try:
        if _MANIFEST.exists():
            rows = json.loads(_MANIFEST.read_text(encoding="utf-8"))
            return rows if isinstance(rows, list) else []
    except Exception:
        pass
    return []


def add_proposal(name: str, line: str, sector: str, market: str = "MM",
                 date: str = "", file: str = "", url: str = "") -> dict:
    """Append a proposal to the manifest so the constellation grows by one."""
    rows = proposals()
    entry = {"name": name, "line": line, "sector": sector, "market": market,
             "date": date, "file": file, "url": url}
    rows.append(entry)
    try:
        _MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        _MANIFEST.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return entry


def render() -> str:
    """The constellation page with the real proposals injected."""
    data = json.dumps(proposals(), ensure_ascii=False)
    try:
        tpl = _TEMPLATE.read_text(encoding="utf-8")
    except Exception:
        return "<!doctype html><body style='background:#060505;color:#D4AF37;font-family:monospace'>Constellation template missing.</body>"
    return tpl.replace("__PROPOSALS__", data)
