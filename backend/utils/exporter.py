"""Export prospects to a spreadsheet-friendly CSV.

Works with zero credentials — the instant way to get the JSON database into
Google Sheets / Excel (open the CSV, or File → Import). utf-8-sig so Excel and
Myanmar text open correctly.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

# Column order shared by CSV, Google Sheets, and HubSpot mapping.
# Includes the deep BD-intelligence fields the researcher now produces. Contact
# fields stay blank unless genuinely verified — never fabricated.
FIELDS = [
    "id", "company", "industry", "sub_sector", "location", "size",
    "fit_score", "service_fit", "why_fit",
    "company_analysis", "online_activities", "onground_activities",
    "marketing_gap", "zynth_approach", "target_role",
    "website", "facebook",
    "contact_name", "contact_title", "email", "phone", "linkedin",
    "status", "source", "created_at",
]

_OUT = Path("outputs/exports")


def prospects_csv() -> tuple[Path, int]:
    """Write all prospects to a timestamped CSV. Returns (path, row_count)."""
    from utils.prospects import all_prospects, seed_if_empty
    seed_if_empty()
    rows = all_prospects()
    _OUT.mkdir(parents=True, exist_ok=True)
    path = _OUT / f"zynth_prospects_{datetime.now():%Y%m%d_%H%M}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    return path, len(rows)
