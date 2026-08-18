#!/usr/bin/env python3
"""ZYNTH — repo/vault → dashboard data layer.

Scans every real source in the repo and emits `backend/outputs/vault-index.json`.
The command dashboard renders straight from that file, so the UI is the repo:

    add a proposal    -> it appears on the next scan
    delete a proposal -> it disappears
    nothing is hardcoded in the interface

Run:  python backend/build_vault_index.py

Sources (all optional — a missing one yields an empty list, never a crash):

    vault/ZYNTH-OS/Proposal-Library/*.md        fully composed, client-ready
    backend/outputs/proposal_pool/index.json    the generated concept pool
    backend/agents/specs/*.md                   the agent workforce
    .claude/skills/*/                           the skill library
    outputs/3d_stage_exhibition_library/        3D stage + exhibition concepts
    deliverables/**/*.md                        produced deliverables
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "backend" / "outputs" / "vault-index.json"

# ---------------------------------------------------------------- helpers
def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def field(text: str, label: str) -> str:
    """Pull a `**Label.** value` block out of a vault proposal."""
    m = re.search(r"\*\*" + re.escape(label) + r"\.?\*\*\s*(.+?)(?=\n\n|\n\*\*|\Z)", text, re.S)
    return clean(m.group(1)) if m else ""


def bullets(text: str, label: str) -> list[str]:
    m = re.search(r"\*\*" + re.escape(label) + r"\.?\*\*[^\n]*\n((?:[ \t]*[-*] [^\n]+\n?)+)", text)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith(("-", "*")):
            continue
        out.append(clean(re.sub(r"^[-*]\s*", "", line)))
    return out


_TIER = re.compile(r"\*?\*?([A-Z][a-zA-Z]+)\*?\*?\s+([\d.,]+\s*[MB]?)", re.U)


def tiers(investment: str) -> list[dict]:
    """`Essential 24M · **Signature 46M (recommended)** · Flagship 82M MMK` → 3 tiers."""
    if not investment:
        return []
    unit = "MMK" if "MMK" in investment else ("SGD" if "SGD" in investment else "")
    out = []
    for name, price in _TIER.findall(investment)[:3]:
        if name.lower() in {"deposit", "market", "fx"}:
            continue
        seg = ""
        i = investment.find(name)
        if i >= 0:
            # stop at the separator so one tier cannot claim the next tier's marker
            rest = investment[i:]
            cut = min([x for x in (rest.find("\u00b7"), rest.find(" | ")) if x > 0] or [len(rest)])
            seg = rest[:cut].lower()
        out.append({
            "name": name,
            "price": f"{price.strip()} {unit}".strip(),
            "rec": "recommend" in seg,
        })
    return out


_FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def front_matter(text: str) -> dict:
    m = _FM.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        if _:
            out[k.strip()] = v.strip()
    return out


def sections(text: str) -> list[dict]:
    """Every `## heading` and its body, so a full client document survives the scan.

    Short five-field proposals have no `##` headings and yield [] — they keep
    rendering from their fields, unchanged.
    """
    body = _FM.sub("", text)
    parts = re.split(r"^(#{2,4})\s+(.+)$", body, flags=re.M)
    if len(parts) < 4:
        return []
    out = []
    for i in range(1, len(parts), 3):
        hashes, heading, chunk = parts[i], parts[i + 1], parts[i + 2]
        md = chunk.strip()
        if md:
            out.append({"level": len(hashes), "h": heading.strip(), "md": md})
    if out:
        # a .docx may start at Heading 2; rebase so the shallowest heading is
        # always level 2, otherwise the reader's table of contents is empty
        base = min(x["level"] for x in out)
        for x in out:
            x["level"] = x["level"] - base + 2
    return out


def markdown_link(text: str) -> str:
    m = re.search(r"\[Open [^\]]*\]\((https?://[^\s)]+)\)", text)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- sources
def composed_proposals() -> list[dict]:
    """The fully composed, client-ready proposals in the Obsidian vault."""
    d = ROOT / "vault" / "ZYNTH-OS" / "Proposal-Library"
    items = []
    if not d.is_dir():
        return items
    for f in sorted(d.glob("*.md")):
        if f.name.startswith("00"):
            continue
        t = f.read_text(encoding="utf-8")
        fm = front_matter(t)
        secs = sections(t)
        h1 = re.search(r"^#\s+(.+)$", t, re.M)
        title = re.sub(r"\s*★.*$", "", h1.group(1) if h1 else f.stem).strip()
        inv = field(t, "Investment (3 tiers)") or field(t, "Investment")
        budget = field(t, "Indicative budget")
        items.append({
            "id": f.stem,
            "title": title,
            "file": str(f.relative_to(ROOT)),
            "sector": field(t, "Sector"),
            "market": field(t, "Market"),
            "type": field(t, "Type"),
            "idea": field(t, "The big idea"),
            "deliverables": bullets(t, "Key deliverables"),
            "kpis": field(t, "KPIs"),
            "investment": inv or budget,
            "pricing_model": "tiers" if inv else ("range" if budget else "none"),
            "tiers": tiers(inv),
            "edge": field(t, "ZYNTH edge"),
            "url": markdown_link(t),
            "doc_url": fm.get("doc_url", ""),
            "drive_url": fm.get("drive_url", ""),
            "sections": secs,
            "full": bool(secs),
            "words": len(t.split()),
            "composed": True,
        })
    return items


def pooled_proposals() -> list[dict]:
    """The generated concept pool — the other 60-odd proposals nobody was showing."""
    p = ROOT / "backend" / "outputs" / "proposal_pool" / "index.json"
    if not p.is_file():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(raw, dict):
        raw = raw.get("proposals", [])
    items = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        items.append({
            "id": r.get("proposal_id", ""),
            "title": r.get("title", ""),
            "file": r.get("file", ""),
            "sector": r.get("industry", ""),
            "market": r.get("market", ""),
            "type": r.get("type", ""),
            "month": r.get("month", ""),
            "created_at": r.get("created_at", ""),
            "composed": False,
        })
    return items


def agents() -> list[dict]:
    d = ROOT / "backend" / "agents" / "specs"
    out = []
    for f in sorted(d.glob("*.md")) if d.is_dir() else []:
        head = ""
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    head = line[2:].strip()
                    break
        except Exception:
            pass
        out.append({"id": f.stem, "label": head or f.stem.replace("_", " ")})
    return out


def skills() -> list[str]:
    d = ROOT / ".claude" / "skills"
    return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.is_dir() else []


def stages() -> list[dict]:
    d = ROOT / "outputs" / "3d_stage_exhibition_library"
    out = []
    if not d.is_dir():
        return out
    for cat in sorted(p for p in d.iterdir() if p.is_dir()):
        for concept in sorted(p for p in cat.iterdir() if p.is_dir()):
            name = concept.name
            code, _, title = name.partition("_")
            market = "SG" if "-SG-" in code else "MM"
            out.append({
                "id": name,
                "title": title.replace("-", " ") or name,
                "code": code,
                "market": market,
                "category": re.sub(r"^\d+_", "", cat.name).replace("_", " ").title(),
            })
    return out


def deliverables() -> list[dict]:
    out = []
    d = ROOT / "deliverables"
    if d.is_dir():
        for f in sorted(d.rglob("*.md")):
            out.append({
                "id": f.stem,
                "title": f.stem.replace("_", " "),
                "file": str(f.relative_to(ROOT)),
                "kind": f.parent.name if f.parent != d else "deliverable",
            })
    man = ROOT / "backend" / "outputs" / "proposal_pool" / "deliverables" / "proposals"
    if man.is_dir():
        for f in sorted(man.glob("*.html")):
            out.append({"id": f.stem, "title": f.stem.replace("_", " "),
                        "file": str(f.relative_to(ROOT)), "kind": "proposal-doc"})
    return out


# ---------------------------------------------------------------- main
def build() -> dict:
    comp = composed_proposals()
    pool = pooled_proposals()
    seen = {p["title"].lower() for p in comp}
    pool = [p for p in pool if p["title"].lower() not in seen]
    data = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "proposals": comp + pool,
        "agents": agents(),
        "skills": skills(),
        "stages": stages(),
        "deliverables": deliverables(),
    }
    data["counts"] = {
        "proposals": len(data["proposals"]),
        "composed": len(comp),
        "full_documents": sum(1 for p in comp if p.get("full")),
        "in_drive": sum(1 for p in comp if p.get("drive_url") or p.get("doc_url")),
        "pooled": len(pool),
        "agents": len(data["agents"]),
        "skills": len(data["skills"]),
        "stages": len(data["stages"]),
        "deliverables": len(data["deliverables"]),
    }
    return data


def main() -> None:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(json.dumps(data["counts"], indent=1))


if __name__ == "__main__":
    main()
