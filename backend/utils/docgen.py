"""Word document generation for client-facing ZYNTH proposals.

Renders a master proposal (title + numbered sections) into a .docx file
per the ZYNTH document standard: no emoji, numbered sections, clean
client-grade formatting. Files are written to outputs/proposals/.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor

_OUT_DIR = Path("outputs/proposals")

_ZYNTH_DARK = RGBColor(0x1A, 0x1A, 0x2E)
_ZYNTH_ACCENT = RGBColor(0x4A, 0x4A, 0x8A)


def _safe_filename(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip()
    return re.sub(r"[\s]+", "_", text)[:80] or "proposal"


def build_proposal_docx(
    title: str,
    client: str,
    market: str,
    sections: list[dict[str, str]],
    prepared_by: str = "ZYNTH — The Intelligence of Creativity",
) -> Path:
    """Render the proposal to .docx and return the file path."""
    doc = Document()

    # Base style
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # ── Cover block ────────────────────────────────────────────────────────
    h = doc.add_heading(title, level=0)
    for run in h.runs:
        run.font.color.rgb = _ZYNTH_DARK

    meta = doc.add_paragraph()
    meta_run = meta.add_run(
        f"Prepared for: {client}\n"
        f"Market: {market}\n"
        f"Date: {datetime.now().strftime('%d %B %Y')}\n"
        f"Prepared by: {prepared_by}"
    )
    meta_run.font.size = Pt(10)
    meta_run.font.color.rgb = _ZYNTH_ACCENT

    doc.add_paragraph()

    # ── Numbered sections ──────────────────────────────────────────────────
    for i, section in enumerate(sections, start=1):
        heading = doc.add_heading(f"{i}. {section.get('heading', f'Section {i}')}", level=1)
        for run in heading.runs:
            run.font.color.rgb = _ZYNTH_DARK

        body = section.get("body", "")
        for block in body.split("\n\n"):
            block = block.strip()
            if not block:
                continue
            # Render simple markdown-ish bullet lines as real bullets
            lines = block.split("\n")
            if all(line.lstrip().startswith(("-", "•", "*")) for line in lines if line.strip()):
                for line in lines:
                    text = line.lstrip().lstrip("-•*").strip()
                    if text:
                        doc.add_paragraph(text, style="List Bullet")
            else:
                doc.add_paragraph(block.replace("\n", " "))

        # Structured tables — this is what makes a proposal executable
        for tbl in section.get("tables") or []:
            headers = [h for h in (tbl.get("headers") or []) if str(h).strip()]
            rows = tbl.get("rows") or []
            if not headers or not rows:
                continue
            if tbl.get("title"):
                cap = doc.add_paragraph()
                cap_run = cap.add_run(tbl["title"])
                cap_run.bold = True
                cap_run.font.size = Pt(10)
                cap_run.font.color.rgb = _ZYNTH_ACCENT
            table = doc.add_table(rows=1, cols=len(headers))
            try:
                table.style = "Light Grid Accent 1"
            except Exception:
                table.style = "Table Grid"
            for j, h in enumerate(headers):
                cell = table.rows[0].cells[j]
                cell.text = str(h)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.bold = True
            for row in rows:
                cells = table.add_row().cells
                for j in range(len(headers)):
                    cells[j].text = str(row[j]) if j < len(row) else ""
            doc.add_paragraph()

    # ── Footer note (deposit clause is business law R2) ────────────────────
    doc.add_paragraph()
    note = doc.add_paragraph()
    note_run = note.add_run(
        "Commercial terms: a 50% deposit is required before work commences. "
        "All rates quoted are estimates pending vendor confirmation."
    )
    note_run.font.size = Pt(9)
    note_run.font.color.rgb = _ZYNTH_ACCENT

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    path = _OUT_DIR / f"{_safe_filename(title)}_{stamp}.docx"
    doc.save(str(path))
    return path
