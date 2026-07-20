"""Google Sheets sync for the prospect database (one-way: JSON → Sheet).

Gracefully inert until configured (like the mailer/FX pattern). The bot needs
its OWN Google credential — set two env vars in Railway:

  GOOGLE_SERVICE_ACCOUNT_JSON  = the full service-account JSON key (one line)
  PROSPECTS_SHEET_ID           = the target spreadsheet's ID (from its URL)

Setup: console.cloud.google.com → new project → enable Google Sheets API →
create a Service Account → make a JSON key → paste it into
GOOGLE_SERVICE_ACCOUNT_JSON. Create a Google Sheet, share it (Editor) with the
service-account email, and put its ID in PROSPECTS_SHEET_ID.

Sync is idempotent: it rewrites the 'Prospects' tab with the full DB, so
running it daily just refreshes the view — no duplicates.
"""

from __future__ import annotations

import json
import os

from utils.exporter import FIELDS
from utils.logging_config import get_logger

logger = get_logger("sheets")

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _config() -> tuple[str, str]:
    return os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""), os.getenv("PROSPECTS_SHEET_ID", "")


def is_configured() -> bool:
    sa, sid = _config()
    return bool(sa and sid)


def push_prospects() -> tuple[bool, str]:
    """Rewrite the 'Prospects' tab with the full DB. Returns (ok, message)."""
    sa, sid = _config()
    if not (sa and sid):
        return False, "not configured (set GOOGLE_SERVICE_ACCOUNT_JSON + PROSPECTS_SHEET_ID)"
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception as exc:  # pragma: no cover - dep missing
        return False, f"google libs unavailable: {exc}"
    try:
        info = json.loads(sa)
        creds = Credentials.from_service_account_info(info, scopes=_SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        try:
            ws = sh.worksheet("Prospects")
        except Exception:
            ws = sh.add_worksheet(title="Prospects", rows=2000, cols=len(FIELDS) + 2)

        from utils.prospects import all_prospects, seed_if_empty
        seed_if_empty()
        rows = all_prospects()
        header = [f.replace("_", " ").title() for f in FIELDS]
        values = [header] + [[str(r.get(k, "")) for k in FIELDS] for r in rows]
        ws.clear()
        ws.update("A1", values, value_input_option="RAW")
        logger.info("Sheets sync: %d prospects pushed", len(rows))
        return True, f"synced {len(rows)} prospects to Google Sheets"
    except Exception as exc:
        logger.info("Sheets sync failed: %s", type(exc).__name__)
        return False, f"sheets error: {str(exc)[:180]}"
