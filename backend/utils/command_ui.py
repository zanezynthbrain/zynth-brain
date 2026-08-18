"""Serve the ZYNTH Command dashboard live on Railway.

The page holds no inventory of its own: on every (cached) request the repo is
re-scanned and the result injected into the template. Add a proposal to the
repo and it is in the interface on the next redeploy — nothing to hardcode.

Route: GET /command
"""
from __future__ import annotations

import json
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATE = _ROOT / "templates" / "dashboard_template.html"
_PREBUILT = _ROOT / "outputs" / "zynth-command.html"
_MARKER = "/*__VAULT_JSON__*/"
_TTL = 300  # seconds — a scan is cheap but not free

_cache: dict[str, object] = {"html": "", "at": 0.0}


def _inject(template: str, data: dict) -> str:
    """Replace the marker + its placeholder literal with the real payload."""
    head, _, tail = template.partition(_MARKER)
    if not tail:
        return template
    depth = end = 0
    for i, ch in enumerate(tail):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")  # never close the script tag early
    return head + payload + tail[end:]


def render(force: bool = False) -> str:
    """The dashboard HTML, rebuilt from a live repo scan (cached for _TTL)."""
    now = time.time()
    if not force and _cache["html"] and now - float(_cache["at"]) < _TTL:
        return str(_cache["html"])
    html = ""
    try:
        import build_vault_index  # backend/ is on sys.path when the bot runs
        html = _inject(_TEMPLATE.read_text(encoding="utf-8"), build_vault_index.build())
    except Exception:
        # a scan failure must never take the page down — fall back to the
        # version built at commit time, which ships in the image
        try:
            html = _PREBUILT.read_text(encoding="utf-8")
        except Exception:
            html = "<h1>ZYNTH Command</h1><p>Dashboard unavailable — run build_vault_index.py</p>"
    _cache["html"], _cache["at"] = html, now
    return html
