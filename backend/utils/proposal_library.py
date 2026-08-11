"""Proposal library — make the pool readable.

The factory writes proposals into ``outputs/proposal_pool/<sector>/<month>.json``
and records a stub in ``index.json``. That is a fine database and a useless
reading surface: the MD asked "where do I check all these proposals?" and the
honest answer was "nowhere, they are trapped in JSON".

This module is the reading layer. It joins the index to the sector files, so
the dashboard can list, filter and open any proposal without the MD ever
touching a file. Read-only — it never writes to the pool.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_POOL = Path("outputs/proposal_pool")
_INDEX = _POOL / "index.json"
_DELIVERABLES = _POOL / "deliverables" / "proposals"


def _read(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return default


def _rows(data: Any) -> list[dict]:
    """The pool files are sometimes a bare list, sometimes wrapped."""
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        for key in ("proposals", "items", "results"):
            v = data.get(key)
            if isinstance(v, list):
                return [r for r in v if isinstance(r, dict)]
    return []


def index() -> list[dict[str, Any]]:
    """Every proposal stub, newest first."""
    rows = _rows(_read(_INDEX, []))
    return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)


@lru_cache(maxsize=64)
def _sector_file(rel: str) -> tuple:
    """Cached read of one sector file — the dashboard polls often."""
    return tuple(json.dumps(r) for r in _rows(_read(_POOL / rel, [])))


def full(proposal_id: str) -> dict[str, Any] | None:
    """The complete proposal body, found via its index stub."""
    stub = next((r for r in index() if r.get("proposal_id") == proposal_id), None)
    if not stub:
        return None
    for blob in _sector_file(stub.get("file", "")):
        row = json.loads(blob)
        if row.get("proposal_id") == proposal_id or row.get("title") == stub.get("title"):
            return {**stub, **row}
    return stub          # stub only — better than nothing, and honest about it


def facets() -> dict[str, list[str]]:
    """The filter values actually present, so the UI never offers an empty filter."""
    rows = index()
    def uniq(key):
        return sorted({str(r.get(key, "")).strip() for r in rows if r.get(key)})
    return {"industry": uniq("industry"), "market": uniq("market"),
            "month": uniq("month"), "type": uniq("type")}


def search(q: str = "", industry: str = "", market: str = "",
           limit: int = 200) -> list[dict[str, Any]]:
    """Filter the library. ``q`` matches title, type or industry."""
    q = (q or "").lower().strip()
    out = []
    for r in index():
        if industry and r.get("industry") != industry:
            continue
        if market and r.get("market") != market:
            continue
        if q:
            blob = f"{r.get('title','')} {r.get('type','')} {r.get('industry','')}".lower()
            if q not in blob:
                continue
        out.append(r)
        if len(out) >= limit:
            break
    return out


def documents() -> list[dict[str, Any]]:
    """Finished, client-ready proposal documents (the gold-standard ones)."""
    out = []
    if _DELIVERABLES.is_dir():
        for p in sorted(_DELIVERABLES.glob("*.html"), reverse=True):
            out.append({"name": p.stem, "path": str(p), "kind": "html",
                        "size_kb": round(p.stat().st_size / 1024, 1)})
    return out


def stats() -> dict[str, Any]:
    rows = index()
    by_industry: dict[str, int] = {}
    by_market: dict[str, int] = {}
    for r in rows:
        by_industry[r.get("industry", "—")] = by_industry.get(r.get("industry", "—"), 0) + 1
        by_market[r.get("market", "—")] = by_market.get(r.get("market", "—"), 0) + 1
    return {
        "total": len(rows),
        "documents": len(documents()),
        "sectors": len(by_industry),
        "by_industry": dict(sorted(by_industry.items(), key=lambda kv: -kv[1])),
        "by_market": by_market,
        "latest": rows[0]["created_at"][:10] if rows and rows[0].get("created_at") else "",
    }


def handle_api(data: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Dispatch ``/api/proposals``. Read-only, so every action is safe."""
    action = (data or {}).get("action", "list")
    if action == "list":
        return {"ok": True, "stats": stats(), "facets": facets(),
                "rows": search(data.get("q", ""), data.get("industry", ""),
                               data.get("market", ""), int(data.get("limit") or 60)),
                "documents": documents()}, 200
    if action == "open":
        row = full(data.get("id", ""))
        if not row:
            return {"ok": False, "error": "proposal not found"}, 404
        return {"ok": True, "proposal": row}, 200
    return {"ok": False, "error": f"unknown action {action!r}"}, 400


__all__ = ["index", "full", "search", "facets", "documents", "stats", "handle_api"]
