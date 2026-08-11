"""Render a ZYNTH proposal to Markdown (and hand it to docgen for .docx).

One document definition, two outputs. The MD is for reading, diffing and the
Obsidian vault; the .docx is what goes to a client and to Drive. They are
generated from the same structure so they can never drift apart.

Section shape (matches utils.docgen.build_proposal_docx):

    {"heading": str,
     "body": str,                       # paragraphs, blank-line separated
     "tables": [{"title": str,          # optional
                 "headers": [str],
                 "rows": [[str]]}]}
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

_OUT = Path("outputs/proposals")


def _fmt_mmk(n: float) -> str:
    return f"{n:,.0f}"


def money_table(cm: dict[str, Any]) -> dict[str, Any]:
    """The commercial summary, rendered from a computed commercial_model."""
    rows = [
        ["Subtotal (direct costs)", _fmt_mmk(cm["subtotal_mmk"]), ""],
        ["Contingency (10%)", _fmt_mmk(cm["contingency_mmk"]), ""],
        ["Total cost base", _fmt_mmk(cm["cost_base_mmk"]),
         f"USD {cm['cost_base_mmk']/cm['fx_rate']:,.0f}"],
        ["Client investment", _fmt_mmk(cm["client_price_mmk"]),
         f"USD {cm['client_price_usd']:,.0f}"],
        ["ZYNTH margin", f"{cm['margin_pct']}%", cm["band"].upper()],
        ["Deposit due on signature (50%)", _fmt_mmk(cm["deposit_mmk"]), ""],
    ]
    return {"title": f"Commercial summary (1 USD = {cm['fx_rate']:,} MMK, market rate)",
            "headers": ["Item", "MMK", "Note"], "rows": rows}


def budget_table(costing) -> dict[str, Any]:
    rows = [[l.category, l.item, f"{l.qty:g}", _fmt_mmk(l.unit_cost_mmk),
             _fmt_mmk(l.total_mmk)] for l in costing.lines]
    rows.append(["", "SUBTOTAL", "", "", _fmt_mmk(costing.subtotal_mmk)])
    rows.append(["", "Contingency 10%", "", "", _fmt_mmk(costing.contingency_mmk)])
    rows.append(["", "TOTAL COST BASE", "", "", _fmt_mmk(costing.cost_base_mmk)])
    return {"title": "Itemised budget",
            "headers": ["Category", "Item", "Qty", "Unit (MMK)", "Total (MMK)"],
            "rows": rows}


def to_markdown(title: str, meta: dict[str, str], sections: list[dict[str, Any]]) -> str:
    """The whole proposal as Markdown."""
    out: list[str] = [f"# {title}", ""]
    for k, v in meta.items():
        out.append(f"**{k}:** {v}  ")
    out += ["", "---", ""]

    for i, s in enumerate(sections, 1):
        out.append(f"## {i}. {s.get('heading','')}")
        out.append("")
        body = (s.get("body") or "").strip()
        if body:
            out.append(body)
            out.append("")
        for tbl in s.get("tables") or []:
            if tbl.get("title"):
                out.append(f"**{tbl['title']}**")
                out.append("")
            heads = tbl.get("headers") or []
            if heads:
                out.append("| " + " | ".join(heads) + " |")
                out.append("|" + "|".join(["---"] * len(heads)) + "|")
                for r in tbl.get("rows") or []:
                    cells = [str(c).replace("|", "\\|") for c in r]
                    out.append("| " + " | ".join(cells) + " |")
                out.append("")
        out.append("---")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def write_markdown(slug: str, text: str) -> Path:
    _OUT.mkdir(parents=True, exist_ok=True)
    p = _OUT / f"{slug}.md"
    p.write_text(text, encoding="utf-8")
    return p


def render_both(slug: str, title: str, client: str, market: str,
                sections: list[dict[str, Any]], one_line_ask: str = "",
                estimated_value: str = "") -> dict[str, Path]:
    """Write the Markdown and the .docx from one definition. Returns both paths."""
    meta = {
        "Client": client,
        "Market": market,
        "Prepared by": "ZYNTH — The Intelligence of Creativity (zynth.asia)",
        "Date": datetime.now().strftime("%d %B %Y"),
    }
    if estimated_value:
        meta["Investment"] = estimated_value
    md_path = write_markdown(slug, to_markdown(title, meta, sections))

    from utils.docgen import build_proposal_docx
    docx_path = build_proposal_docx(
        title=title, client=client, market=market, sections=sections,
        one_line_ask=one_line_ask, estimated_value=estimated_value,
    )
    return {"md": md_path, "docx": docx_path}


__all__ = ["to_markdown", "write_markdown", "render_both", "money_table", "budget_table"]
