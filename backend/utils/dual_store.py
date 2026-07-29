"""Dual storage — every result saved to GitHub AND Google Drive at the same time.

One call, two homes:
  • GitHub  → written into the committed proposal pool (outputs/proposal_pool/
    deliverables/<department>/), which gitsync/CI push to the repo. Works now.
  • Drive   → uploaded to a Drive folder via a SERVICE ACCOUNT so the 24/7 bot can
    write to Drive on its own (not just when a human runs a session). Activates when
    GOOGLE_SERVICE_ACCOUNT_JSON + DRIVE_DELIVERABLES_FOLDER are set in Railway; until
    then it degrades gracefully (the GitHub copy still saves, Drive is marked pending).

Nothing here ever raises into the caller — a storage hiccup must not lose the work.

Setup to switch Drive on (one-time):
  1. Google Cloud → create a service account → enable Drive API → download its JSON key.
  2. Share the target Drive folder with the service account's email (Editor).
  3. Railway vars:  GOOGLE_SERVICE_ACCOUNT_JSON = <the JSON>   (or a file path)
                    DRIVE_DELIVERABLES_FOLDER   = <the folder id>
  4. requirements already tolerant; add google-api-python-client google-auth if missing.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path("outputs/proposal_pool/deliverables")
_INDEX = _ROOT / "index.json"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "untitled").lower()).strip("-")[:60] or "untitled"


def _load_index() -> list[dict]:
    if _INDEX.exists():
        try:
            return json.loads(_INDEX.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_index(rows: list[dict]) -> None:
    _INDEX.parent.mkdir(parents=True, exist_ok=True)
    _INDEX.write_text(json.dumps(rows[-500:], ensure_ascii=False, indent=2), encoding="utf-8")


# ── GitHub side (the committed pool) ─────────────────────────────────────────
def _github_save(title: str, content: str, department: str, ext: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    folder = _ROOT / _slug(department or "general")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{date}-{_slug(title)}.{ext}"
    path.write_text(content, encoding="utf-8")
    return str(path)


# ── Drive side (service account; inert until configured) ─────────────────────
def drive_enabled() -> bool:
    return bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") and os.getenv("DRIVE_DELIVERABLES_FOLDER"))


def _service_account_info() -> dict | None:
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        return None
    try:
        if raw.startswith("{"):
            return json.loads(raw)
        p = Path(raw)  # treat as a path
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _drive_save(title: str, content: str, department: str, ext: str) -> str:
    """Upload to Drive via a service account. Returns a status string (never raises)."""
    if not drive_enabled():
        return "pending (no service account configured)"
    info = _service_account_info()
    folder = os.getenv("DRIVE_DELIVERABLES_FOLDER", "").strip()
    if not info or not folder:
        return "pending (bad credentials/folder)"
    try:
        from google.oauth2 import service_account  # type: ignore
        from googleapiclient.discovery import build  # type: ignore
        from googleapiclient.http import MediaInMemoryUpload  # type: ignore
    except Exception:
        return "pending (google libs not installed — add google-api-python-client google-auth)"
    try:
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive.file"])
        svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        mime = "text/markdown" if ext == "md" else "text/plain"
        # convert markdown → Google Doc for readability
        meta = {"name": f"{title} — {department}", "parents": [folder],
                "mimeType": "application/vnd.google-apps.document"}
        media = MediaInMemoryUpload(content.encode("utf-8"), mimetype=mime, resumable=False)
        f = svc.files().create(body=meta, media_body=media, fields="id,webViewLink").execute()
        return f.get("webViewLink") or f.get("id") or "saved"
    except Exception as exc:  # never lose the work over a Drive error
        return f"error ({type(exc).__name__})"


# ── The one call the whole system uses ───────────────────────────────────────
def save_output(title: str, content: str, department: str = "General",
                kind: str = "deliverable", ext: str = "md") -> dict[str, Any]:
    """Persist a result to GitHub (pool) AND Drive at once. Returns where it went."""
    gh, dr = "", ""
    try:
        gh = _github_save(title, content, department, ext)
    except Exception as exc:
        gh = f"error ({type(exc).__name__})"
    try:
        dr = _drive_save(title, content, department, ext)
    except Exception as exc:
        dr = f"error ({type(exc).__name__})"
    entry = {
        "id": f"D{len(_load_index()) + 1:04d}",
        "title": title, "department": department, "kind": kind,
        "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "github": gh, "drive": dr,
    }
    try:
        rows = _load_index()
        rows.append(entry)
        _save_index(rows)
    except Exception:
        pass
    return entry


def list_deliverables(n: int = 30) -> list[dict]:
    return _load_index()[-n:][::-1]


def status_line() -> str:
    rows = _load_index()
    drv = "Drive ON (service account)" if drive_enabled() else "Drive pending (set service account in Railway)"
    return f"{len(rows)} deliverables saved · GitHub ON · {drv}"
