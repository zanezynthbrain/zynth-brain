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


def _manifest_rows() -> list[dict]:
    try:
        if _MANIFEST.exists():
            rows = json.loads(_MANIFEST.read_text(encoding="utf-8"))
            return rows if isinstance(rows, list) else []
    except Exception:
        pass
    return []


def proposals() -> list[dict]:
    """Every proposal in the library, newest first.

    Two sources, because the library holds two kinds of thing and the sphere
    should show both:

    * **documents** — finished, client-ready proposals with a URL to open.
    * **concepts** — the pooled proposals the factory produces daily. They have
      no URL, so a star carries its ``id`` and the page opens its detail from
      /api/proposals instead of doing nothing when clicked.

    Every node therefore has something to open, which is the point of a star
    being clickable. Sorted newest first so the sphere reads as a timeline.
    """
    out: list[dict] = []

    for r in _manifest_rows():
        out.append({
            "name": r.get("name", ""), "line": r.get("line", ""),
            "sector": r.get("sector", ""), "market": r.get("market", "MM"),
            "date": r.get("date", ""), "type": r.get("type", "Full proposal"),
            "kind": "document", "url": r.get("url", ""), "id": "",
        })

    try:
        from utils import proposal_library
        for r in proposal_library.index():
            out.append({
                "name": r.get("title", ""), "line": r.get("type", ""),
                "sector": r.get("industry", ""), "market": r.get("market", "MM"),
                "date": (r.get("created_at") or "")[:10],
                "type": r.get("type", "Concept"),
                "kind": "concept", "url": "", "id": r.get("proposal_id", ""),
            })
    except Exception:
        pass

    out.sort(key=lambda r: r.get("date", ""), reverse=True)
    return out


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
