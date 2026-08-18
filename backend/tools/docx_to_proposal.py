#!/usr/bin/env python3
"""Convert a full .docx proposal into a vault proposal that keeps ALL its content.

The short `**Field.**` proposals in the vault carry five fields. Real client
documents carry twenty sections, tables and all. This writes the long form:
YAML front matter for the index fields, then every heading, paragraph and table
from the source document, in document order.

    python backend/tools/docx_to_proposal.py <file.docx> [--slug name] [--sector S]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    sys.exit("pip install python-docx")

ROOT = Path(__file__).resolve().parent.parent.parent
VAULT = ROOT / "vault" / "ZYNTH-OS" / "Proposal-Library"


def body_items(document):
    """Yield paragraphs and tables in true document order."""
    parent = document.element.body
    for child in parent.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


def table_to_md(tbl) -> list[str]:
    rows = []
    for r in tbl.rows:
        cells = [re.sub(r"\s*\n\s*", " ", c.text).strip().replace("|", "\\|") for c in r.cells]
        rows.append(cells)
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return out


def convert(path: Path, slug: str | None, meta: dict) -> Path:
    d = docx.Document(str(path))
    title, lines, seen_title = "", [], False

    for item in body_items(d):
        if isinstance(item, Table):
            md = table_to_md(item)
            if md:
                lines.append("")
                lines.extend(md)
                lines.append("")
            continue
        text = item.text.strip()
        if not text:
            continue
        style = item.style.name or ""
        is_head = style.startswith("Heading") or style == "Title"
        if is_head and not seen_title:
            title, seen_title = text, True
            continue
        if is_head:
            level = 2
            m = re.search(r"Heading (\d)", style)
            if m:
                level = min(4, max(2, int(m.group(1)) + 1))
            lines.append("")
            lines.append("#" * level + " " + text)
            lines.append("")
        else:
            bullet = style.lower().startswith("list")
            lines.append(("- " if bullet else "") + text)

    title = title or path.stem.replace("_", " ").title()
    slug = slug or re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")[:70]

    fm = ["---", f"title: {title}", "tags: [zynth, proposal, client-ready, full-document]"]
    for k, v in meta.items():
        if v:
            fm.append(f"{k}: {v}")
    fm.append("---")

    head = [
        "", f"# {title} ★ full client-ready", "",
        f"**Sector.** {meta.get('sector','')}", "",
        f"**Market.** {meta.get('market','')}", "",
        f"**Type.** {meta.get('type','')}", "",
    ]
    body = "\n".join(fm + head + lines)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

    VAULT.mkdir(parents=True, exist_ok=True)
    out = VAULT / f"{slug}.md"
    out.write_text(body, encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--slug")
    ap.add_argument("--sector", default="")
    ap.add_argument("--market", default="")
    ap.add_argument("--type", dest="ptype", default="")
    ap.add_argument("--doc-url", dest="doc_url", default="")
    a = ap.parse_args()
    out = convert(Path(a.docx), a.slug,
                  {"sector": a.sector, "market": a.market, "type": a.ptype, "doc_url": a.doc_url})
    print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
