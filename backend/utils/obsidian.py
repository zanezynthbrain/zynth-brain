"""Obsidian mirror — writes the business's narrative updates into the vault as
markdown notes, so your 'second brain' reflects what the AI is doing.

Design: the STRUCTURED database stays in JSON (and Sheets/HubSpot). Obsidian
gets the human, linkable NARRATIVE — a Home index, a live snapshot, hot
prospects, and a dated research log. Notes use YAML front-matter + [[wikilinks]]
so they graph nicely in Obsidian.

Location: outputs/proposal_pool/vault/ — the folder that (a) the knowledge
loader already reads, (b) the daily pool workflow commits to GitHub, so your
Obsidian Git pulls it. `/note` captures land here too.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

_VAULT = Path("outputs/proposal_pool/vault")


def _slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip()
    return re.sub(r"\s+", "-", text)[:80] or "note"


def write_note(folder: str, title: str, body: str, tags: list[str] | None = None) -> Path:
    """Write/overwrite a markdown note with front-matter. Returns its path."""
    d = _VAULT / folder if folder else _VAULT
    d.mkdir(parents=True, exist_ok=True)
    fm = (
        "---\n"
        f"title: {title}\n"
        f"tags: [{', '.join(tags or ['zynth'])}]\n"
        f"updated: {datetime.now():%Y-%m-%d %H:%M}\n"
        "---\n\n"
    )
    path = d / f"{_slug(title)}.md"
    path.write_text(fm + body.strip() + "\n", encoding="utf-8")
    return path


# ── snapshot notes ────────────────────────────────────────────────────────────

def _counts() -> dict:
    out = {"prospects": 0, "hot": 0, "leads": 0, "suppliers": 0, "venues": 0}
    try:
        from utils.prospects import stats, seed_if_empty
        seed_if_empty()
        s = stats(); out["prospects"] = s["total"]; out["hot"] = s["hot"]
    except Exception:
        pass
    try:
        from utils.leads import all_leads
        out["leads"] = len(all_leads())
    except Exception:
        pass
    try:
        from utils.suppliers import all_suppliers
        out["suppliers"] = len(all_suppliers())
    except Exception:
        pass
    try:
        from utils.venues import all_venues
        out["venues"] = len(all_venues())
    except Exception:
        pass
    return out


def home_note() -> Path:
    c = _counts()
    body = (
        "# 🧠 ZYNTH Brain — Home\n\n"
        "The living index of ZYNTH's AI operating system. Structured data lives in "
        "the databases (and Google Sheets / HubSpot); this vault holds the narrative.\n\n"
        "## Live numbers\n"
        f"- 🎯 Prospects: **{c['prospects']}** ({c['hot']} hot ★★★★+)\n"
        f"- 📇 Leads (pipeline): **{c['leads']}**\n"
        f"- 🧰 Suppliers: **{c['suppliers']}** · 🏛 Venues: **{c['venues']}**\n\n"
        "## Sections\n"
        "- [[What We Built]] — the whole system, in one page\n"
        "- [[Business Snapshot]] — current numbers\n"
        "- [[Hot Prospects]] — the best targets right now\n"
        "- [[Research Log]] — what the market researcher finds, day by day\n\n"
        "## How this stays updated\n"
        "The bot writes these notes; the daily pool workflow commits them to GitHub; "
        "your Obsidian Git pulls them. Quick-capture your own with `/note` in Telegram.\n"
    )
    return write_note("", "00 ZYNTH Home", body, tags=["zynth", "home", "moc"])


def snapshot_note() -> Path:
    c = _counts()
    scorecard = ""
    try:
        from utils.business import scorecard_view
        scorecard = scorecard_view()
    except Exception:
        pass
    body = (
        "# 📊 Business Snapshot\n\n"
        f"_As of {datetime.now():%A %d %b %Y, %H:%M}_\n\n"
        "| Metric | Count |\n|---|---|\n"
        f"| Prospects | {c['prospects']} ({c['hot']} hot) |\n"
        f"| Leads (pipeline) | {c['leads']} |\n"
        f"| Suppliers | {c['suppliers']} |\n"
        f"| Venues | {c['venues']} |\n\n"
        + (f"## Scorecard\n{scorecard}\n\n" if scorecard else "")
        + "Back to [[00 ZYNTH Home]]\n"
    )
    return write_note("", "Business Snapshot", body, tags=["zynth", "snapshot"])


def hot_prospects_note(limit: int = 40) -> Path:
    try:
        from utils.prospects import all_prospects, seed_if_empty
        seed_if_empty()
        rows = sorted(all_prospects(), key=lambda r: -r.get("fit_score", 0))
    except Exception:
        rows = []
    hot = [r for r in rows if r.get("fit_score", 0) >= 4][:limit]
    lines = ["# 🔥 Hot Prospects", "", "Top-fit Myanmar businesses to pursue (★★★★+).", "",
             "| Company | Sector | Fit | Why |", "|---|---|:--:|---|"]
    for r in hot:
        lines.append(
            f"| {r.get('company','')} | {r.get('industry','')} | "
            f"{'★'*r.get('fit_score',0)} | {r.get('why_fit','')} |"
        )
    lines += ["", f"_{len(hot)} shown · full DB via `/prospects` or Google Sheets._",
              "", "Back to [[00 ZYNTH Home]]"]
    return write_note("", "Hot Prospects", "\n".join(lines), tags=["zynth", "bd", "prospects"])


def research_log_entry(sector: str, added: int, total: int, top: list[dict]) -> Path:
    """Append a dated entry to the running research log note."""
    d = _VAULT
    d.mkdir(parents=True, exist_ok=True)
    path = d / "Research Log.md"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = [f"\n## {stamp} — {sector}",
             f"+{added} new prospects · DB now {total}"]
    for p in top[:5]:
        entry.append(f"- **{p.get('company','')}** ({p.get('fit_score','')}★) — {p.get('why_fit','')}")
    if not path.exists():
        header = ("---\ntitle: Research Log\ntags: [zynth, research, log]\n"
                  f"updated: {stamp}\n---\n\n# 🔎 Market Research Log\n\n"
                  "Every daily/on-demand research run, newest at the bottom. "
                  "Back to [[00 ZYNTH Home]]\n")
        path.write_text(header + "\n".join(entry) + "\n", encoding="utf-8")
    else:
        with path.open("a", encoding="utf-8") as f:
            f.write("\n".join(entry) + "\n")
    return path


def what_we_built_note() -> Path:
    body = (
        "# 🏗 What We Built\n\n"
        "ZYNTH's 24/7 AI operating system — the one-page tour.\n\n"
        "## The workforce\n"
        "- **CEO daily cycle** — research → departments → synthesis → report\n"
        "- **Proposal engine** — ZYNTH Proposal Standard, market-FX, one-line ask, attribution\n"
        "- **Event Specialist Team** — concept + design + ops → HITL approve\n"
        "- **Market Researcher** — finds Myanmar business prospects daily\n"
        "- **Creative Video Director** (skill) — concept, storyboard, Resolve/Premiere/CapCut\n\n"
        "## The databases (JSON → Sheets/HubSpot)\n"
        "- Prospects · Leads · Suppliers · Venues · Tasks · Activity · Scorecard\n\n"
        "## Channels\n"
        "- Telegram (commands + voice) · Email · live Dashboard · this Obsidian vault\n\n"
        "## Automation (Yangon time)\n"
        "- 06:30 market research · 07:00 FX · 08:00 brief · 18:00 EOD · 21:00 consolidation\n"
        "- Weekly: MD learning brief, Monday cadence, Friday review\n\n"
        "See the full report in the repo: `docs/PROJECT_REPORT.md`.\n\n"
        "Back to [[00 ZYNTH Home]]\n"
    )
    return write_note("", "What We Built", body, tags=["zynth", "overview"])


def full_sync() -> list[Path]:
    """(Re)write all the standing mirror notes. Safe to run any time."""
    paths = []
    for fn in (home_note, what_we_built_note, snapshot_note, hot_prospects_note):
        try:
            paths.append(fn())
        except Exception:
            pass
    # Then push everything into the vault the MD's Obsidian actually opens.
    for fn in (mirror_repo_docs, mirror_live_notes):
        try:
            paths.extend(fn())
        except Exception:
            pass
    return paths


# ---------------------------------------------------------------------------
# Repo → Obsidian mirror
# ---------------------------------------------------------------------------
# The MD's Obsidian opens the repo-root `vault/` folder (see vault/README.md).
# Everything else — docs/, .claude/skills/, backend/ — is invisible there. So
# the work lands in GitHub but never reaches the second brain.
#
# This mirrors the documents worth READING into vault/, and pulls the live
# narrative notes across from the pool vault so they show up too.
#
# Every generated file opens with the TEMPLATE marker on purpose: the knowledge
# loader skips those, so mirrors stay out of the agents' 30k character budget.
# Agents read the source; the mirror is for the human.

_REPO = Path(__file__).resolve().parent.parent.parent
_OBSIDIAN = _REPO / "vault" / "ZYNTH-OS"

#: source path (repo-relative) → destination inside vault/ZYNTH-OS/
MIRRORED_DOCS: dict[str, str] = {
    "docs/handoff/2026-08-06.md": "Handoffs/2026-08-06 Back-Office Build.md",
    "docs/handoff/2026-08-07.md": "Handoffs/2026-08-07 Studio Meta Learning.md",
    "docs/departments/FINANCE_operating_costs.md": "Finance/Operating Costs.md",
    "docs/departments/FINANCE_operating_system.md": "Finance/Finance Operating System.md",
    "docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md": "Adoption/Back-Office Manifest.md",
    "backend/data/project_ignite_15s.md": "Projects/IGNITE 15s.md",
    "docs/ZYNTH_MASTER_GUIDE.md": "00 MASTER GUIDE.md",
    "docs/zynth-os/Operational_Blueprint.md": "Blueprints/Operational Blueprint.md",
    "docs/zynth-os/Master_Workflows.md": "Blueprints/Master Workflows.md",
    "docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md": "Capability System Standard.md",
    "docs/ZYNTH_SKILL_REBUILD_ARCHITECTURE.md": "Capability Rebuild Architecture.md",
    "docs/ZYNTH_CAPABILITY_REBUILD_VALIDATION.md": "Capability Rebuild Validation.md",
    "docs/ZYNTH_FULL_CLIENT_GRADE_PROPOSAL_STANDARD.md": "Proposals/Full Client-Grade Proposal Standard.md",
    "docs/ZYNTH_SERVICE_PACKAGE_ARCHITECTURE.md": "Business Development/Service Package Architecture.md",
    "docs/ZYNTH_BUSINESS_DEVELOPMENT_PLAYBOOK.md": "Business Development/Business Development Playbook.md",
    "docs/ZYNTH_FOUNDER_ASSISTANT_OPERATING_MODEL.md": "Founder/Founder Assistant Operating Model.md",
    "docs/ZYNTH_ANIMATION_AND_DESIGN_RESOURCE_ASSESSMENT.md": "Creative/Animation and Design Resource Assessment.md",
    "docs/ZYNTH_SECOND_BRAIN_INFORMATION_ARCHITECTURE.md": "Founder/Second Brain Information Architecture.md",
    "docs/ZYNTH_SECOND_BRAIN_SPHERE_EXPERIENCE.md": "Founder/Second Brain Sphere Experience.md",
    "docs/proposal-exemplars/01_FULL_PRODUCT_LAUNCH_PROPOSAL.md": "Proposals/Exemplars/Full Product Launch Proposal.md",
    "docs/proposal-exemplars/02_FULL_PUBLIC_BRAND_EXPERIENCE_PROPOSAL.md": "Proposals/Exemplars/Full Public Brand Experience Proposal.md",
    "research/myanmar_agency_market_findings.md": "Research/Myanmar Agency Market Findings.md",
    "research/singapore_agency_market_findings.md": "Research/Singapore Agency Market Findings.md",
    "research/myanmar_singapore_agency_pricing_signals.md": "Research/Myanmar Singapore Agency Pricing Signals.md",
}

_GENERATED_HEADER = (
    "<!-- TEMPLATE -->\n"
    "<!-- Generated mirror — the knowledge loader skips this file on purpose. -->\n"
    "---\ngenerated: true\nsource: {source}\nmirrored: {when}\n---\n\n"
    "> **Generated mirror of `{source}`.** Edit the source in the repo, not this\n"
    "> file — the next `/mirror` overwrites whatever is here.\n\n"
)


def _strip_mirror_stamp(text: str) -> str:
    """The note minus its `mirrored:` line — i.e. everything that carries meaning."""
    return "\n".join(
        line for line in text.splitlines() if not line.startswith("mirrored:")
    )


def _write_mirror(destination: Path, source_rel: str, body: str) -> Path:
    """Write the mirrored note, but only when its content actually changed.

    The header carries a `mirrored:` timestamp, so a naive write makes every
    run differ from the last even when the source is untouched — which dirties
    every mirrored file in git on each mirror, burying real edits in noise.
    Compare without the stamp and skip the write when nothing meaningful moved.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    header = _GENERATED_HEADER.format(
        source=source_rel, when=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    new = header + body

    if destination.exists():
        try:
            if _strip_mirror_stamp(destination.read_text(encoding="utf-8")) == \
                    _strip_mirror_stamp(new):
                return destination          # unchanged — leave the file alone
        except OSError:
            pass                            # unreadable: fall through and rewrite

    destination.write_text(new, encoding="utf-8")
    return destination


def _frontmatter_description(text: str) -> str:
    """Read a normal or folded YAML ``description`` without adding a YAML dependency.

    Several ZYNTH skills use ``description: >``. The old mirror read only the
    marker itself, making fully developed skills look blank in Drive. This small
    parser deliberately handles the narrow frontmatter form used by the repo.
    """
    rows = text.splitlines()
    if not rows or rows[0].strip() != "---":
        return ""
    for i, line in enumerate(rows[1:], start=1):
        if line.strip() == "---":
            break
        if not line.startswith("description:"):
            continue
        first = line.split(":", 1)[1].strip()
        if first not in {">", "|", ">-", "|-"}:
            return first.strip('"')
        parts: list[str] = []
        for child in rows[i + 1:]:
            if child.strip() == "---" or (child and not child[0].isspace()):
                break
            if child.strip():
                parts.append(child.strip())
        return " ".join(parts)
    return ""


def skills_index_note() -> Path:
    """One page listing every repo-versioned skill, trigger, source and resources."""
    skills_dir = _REPO / ".claude" / "skills"
    rows: list[tuple[str, str, int]] = []
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        name = skill_file.parent.name
        description = ""
        resource_count = 0
        try:
            text = skill_file.read_text(encoding="utf-8")
            description = _frontmatter_description(text)
            resource_count = sum(1 for p in skill_file.parent.rglob("*") if p.is_file() and p.name != "SKILL.md")
        except Exception:
            pass
        rows.append((name, description, resource_count))

    groups = {
        "Back-office (zb- cluster + finance)": lambda n: n.startswith(("zb-", "yadana")),
        "Master planners": lambda n: n.startswith("zynth-master"),
        "Creative & production": lambda n: any(
            k in n for k in ("art-director", "creative", "copywriter", "video", "content", "social")
        ),
        "Growth & BD": lambda n: any(k in n for k in ("bd-", "market", "competitor", "paid", "seo", "pitch")),
        "Operations": lambda n: any(k in n for k in ("account", "project", "event", "vendor", "analytics", "campaign", "brand")),
    }

    lines = [f"# Skills Index — {len(rows)} repo-versioned skills\n",
             "Every skill below lives in `.claude/skills/` and travels with the repo.\n"]
    placed: set[str] = set()
    for title, matcher in groups.items():
        members = [(n, d, r) for n, d, r in rows if matcher(n) and n not in placed]
        if not members:
            continue
        placed.update(n for n, _, _ in members)
        lines.append(f"\n## {title}\n")
        for name, description, resources in members:
            summary = description[:360].rstrip() or "No description was parsed; open the source skill before use."
            lines.append(
                f"- **`{name}`** — {summary}\n"
                f"  - **Full operating source:** `.claude/skills/{name}/SKILL.md`"
                f" · **Supporting resources:** {resources}"
            )
    leftovers = [(n, d, r) for n, d, r in rows if n not in placed]
    if leftovers:
        lines.append("\n## Other\n")
        for name, description, resources in leftovers:
            summary = description[:360].rstrip() or "No description was parsed; open the source skill before use."
            lines.append(
                f"- **`{name}`** — {summary}\n"
                f"  - **Full operating source:** `.claude/skills/{name}/SKILL.md`"
                f" · **Supporting resources:** {resources}"
            )
    return _write_mirror(_OBSIDIAN / "Skills Index.md", ".claude/skills/", "\n".join(lines) + "\n")


def mirror_repo_docs() -> list[Path]:
    """Copy the read-worthy repo docs into the vault Obsidian actually opens."""
    written: list[Path] = []
    for source_rel, dest_rel in MIRRORED_DOCS.items():
        source = _REPO / source_rel
        if not source.is_file():
            continue
        body = source.read_text(encoding="utf-8")
        # Strip a leading TEMPLATE marker from the source so it isn't duplicated.
        body = body.replace("<!-- TEMPLATE -->\n", "", 1)
        written.append(_write_mirror(_OBSIDIAN / dest_rel, source_rel, body))
    try:
        written.append(skills_index_note())
    except Exception:
        pass
    return written


def mirror_live_notes() -> list[Path]:
    """Bring the pool-vault narrative notes into the MD's Obsidian vault.

    `/mirror` writes them to outputs/proposal_pool/vault/, which the agents read
    but the MD's Obsidian never opens. This closes that gap.
    """
    written: list[Path] = []
    if not _VAULT.is_dir():
        return written
    for note in sorted(_VAULT.glob("*.md")):
        body = note.read_text(encoding="utf-8")
        written.append(_write_mirror(
            _OBSIDIAN / "Live" / note.name,
            f"backend/outputs/proposal_pool/vault/{note.name}",
            body,
        ))
    return written
