"""Storage abstraction for ZYNTH agent outputs.

Agents call :func:`save_document` to persist deliverables. Depending on
what's configured, documents are written locally (always) AND optionally
to Google Drive (when ``ZYNTH_GDRIVE_FOLDER_ID`` is set and the Google
Drive MCP server is available).

Storage layer map:
  local outputs/         → always; fastest; backed up to GitHub on commit
  Google Drive           → enable with ZYNTH_GDRIVE_FOLDER_ID; great for sharing with team
  GitHub (code/SOPs)     → commit backend/ folder; history + version control
  Obsidian vault         → future; sync via iCloud when laptop is nearby

ဒေတာ သိုလှောင်ခြင်း:
  - outputs/ folder   → အမြဲတမ်း local ထားမည်
  - Google Drive      → GDRIVE_FOLDER_ID ထည့်ရင် auto-upload ဖြစ်မည်
  - GitHub            → code commit လုပ်တိုင်း backup ဖြစ်မည်
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import get_settings
from utils.logging_config import get_logger
from utils.tools import write_file, ToolResult
from utils.dual_store import save_output

logger = get_logger("utils.storage")


def save_document(
    filename: str,
    content: str | dict[str, Any],
    department: str = "general",
    overwrite: bool = True,
) -> ToolResult:
    """Save agent output to the local outputs directory, organized by department.

    Args:
        filename: e.g. "vendor_list.json" or "event_proposal_acme.md"
        content:  string or dict (dicts are JSON-serialized automatically)
        department: sub-folder name, e.g. "operations", "creative", "finance"
        overwrite: if False, timestamps the filename to avoid collisions

    Returns a ToolResult with the saved path on success.
    """
    settings = get_settings()

    if isinstance(content, (dict, list)):
        text = json.dumps(content, indent=2, default=str)
        if not filename.endswith(".json"):
            filename = filename + ".json"
    else:
        text = str(content)

    if not overwrite:
        stem = Path(filename).stem
        ext = Path(filename).suffix
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stem}_{ts}{ext}"

    relative_path = f"{department}/{filename}"
    result = write_file(relative_path, text)

    if result.ok:
        logger.info("Saved document: outputs/%s", relative_path)
        _maybe_upload_to_gdrive(relative_path, text, department)
    else:
        logger.warning("Failed to save document %s: %s", relative_path, result.error)

    return result


def save_report(report_data: dict[str, Any], report_type: str, department: str = "reports") -> ToolResult:
    """Save a timestamped report JSON, used by CEO for daily brief archives."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{report_type}_{date_str}.json"
    return save_document(filename, report_data, department=department, overwrite=True)


def load_document(filename: str, department: str = "general") -> str | None:
    """Load a previously saved document. Returns None if not found."""
    from utils.tools import read_file
    relative_path = f"{department}/{filename}"
    result = read_file(relative_path)
    if result.ok:
        return result.data
    logger.debug("Document not found: outputs/%s", relative_path)
    return None


def load_latest_report(report_type: str, department: str = "reports") -> dict[str, Any] | None:
    """Load the most recent saved report of a given type."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{report_type}_{date_str}.json"
    raw = load_document(filename, department)
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


def _maybe_upload_to_gdrive(relative_path: str, content: str, department: str) -> None:
    """Mirror the saved document through the durable GitHub + Drive writer.

    The dual-save path is deliberately best-effort: when Railway does not yet
    provide GOOGLE_SERVICE_ACCOUNT_JSON and DRIVE_DELIVERABLES_FOLDER it
    records Drive as pending while preserving the local output. This keeps
    internal 24/7 workstreams productive without turning an unavailable Drive
    credential into a failed agent run.
    """
    path = Path(relative_path)
    ext = path.suffix.lstrip(".") or "txt"
    title = path.stem
    status = save_output(
        title=title,
        content=content,
        department=department,
        kind="agent_document",
        ext=ext,
    )
    logger.info("Dual-save status for %s: github=%s drive=%s", relative_path, status.get("github"), status.get("drive"))
