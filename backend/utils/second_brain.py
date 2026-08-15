"""Real-data model for the founder-facing ZYNTH Second Brain.

The visual layer deliberately receives a curated graph of actual operating assets rather
than invented activity: repository agents/skills/documents plus current dashboard,
projects, proposals, queues, switches, diagnostics, mistakes and lessons.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_SKILLS = _REPO / ".claude" / "skills"
_DOCS = _REPO / "docs"
_RESEARCH = _REPO / "research"

_CLUSTER = {
    "core": {"label": "Agency Core", "color": "#49D6DC", "icon": "◉"},
    "capability": {"label": "Capabilities", "color": "#A997ED", "icon": "◇"},
    "knowledge": {"label": "Knowledge", "color": "#5BB7FF", "icon": "▤"},
    "operations": {"label": "Operations", "color": "#D5AD57", "icon": "◌"},
    "outputs": {"label": "Outputs", "color": "#F0BA61", "icon": "✦"},
    "monitoring": {"label": "Monitoring", "color": "#55C98C", "icon": "◎"},
    "learning": {"label": "Learning", "color": "#E77ED1", "icon": "↻"},
}

# These are relationship *rules* between ZYNTH's actual named agent and skill files.
# They are intentionally explicit, so the graph never implies an unverified runtime call.
_AGENT_SKILLS: dict[str, tuple[str, ...]] = {
    "master_proposal": (
        "zynth-master-proposal-writer", "zynth-campaign-planner",
        "zynth-master-campaign-planner", "zynth-copywriter",
    ),
    "proposal_factory": (
        "zynth-master-proposal-writer", "zynth-campaign-planner",
        "zynth-brand-strategist", "zynth-pitch-packager",
    ),
    "market_researcher": (
        "zynth-market-researcher", "zynth-competitor-analyst", "zb-icp",
    ),
    "lead_gen": ("zynth-bd-researcher", "zb-icp", "zb-offer", "zb-objections"),
    "content_studio": (
        "zynth-content-strategist", "zynth-copywriter", "zynth-social-media-manager",
    ),
    "video_team": ("zynth-commercial-video-studio", "zynth-creative-video-director", "zynth-video-producer"),
    "event_manager": ("zynth-event-manager", "zynth-master-event-planner", "zynth-sponsorship-value"),
    "event_team": ("zynth-event-manager", "zynth-master-event-planner", "zynth-3d-design-studio"),
    "paid_ads": ("zynth-paid-media-specialist", "zynth-analytics-specialist"),
    "research_seo": ("zynth-seo-specialist", "zynth-market-researcher"),
    "copywriter": ("zynth-copywriter",),
    "improver": ("zynth-tactical-prompts",),
    "portfolio": ("zynth-project-manager", "zynth-account-manager"),
    "operations": ("zynth-project-manager", "zynth-vendor-finder"),
}

_KEY_DOCUMENTS: tuple[tuple[str, str, str], ...] = (
    ("docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md", "Capability System Standard", "knowledge"),
    ("docs/ZYNTH_FULL_CLIENT_GRADE_PROPOSAL_STANDARD.md", "Full Client-Grade Proposal Standard", "knowledge"),
    ("docs/ZYNTH_SERVICE_PACKAGE_ARCHITECTURE.md", "Service Package Architecture", "knowledge"),
    ("docs/ZYNTH_BUSINESS_DEVELOPMENT_PLAYBOOK.md", "Business Development Playbook", "knowledge"),
    ("docs/ZYNTH_FOUNDER_ASSISTANT_OPERATING_MODEL.md", "Founder Assistant Operating Model", "knowledge"),
    ("docs/ZYNTH_FOUNDER_OPERATING_GUIDE.md", "Founder Operating Guide", "knowledge"),
    ("docs/ZYNTH_KNOWLEDGE_AND_STORAGE_AUDIT.md", "Knowledge & Storage Audit", "knowledge"),
    ("docs/ZYNTH_ANIMATION_AND_DESIGN_RESOURCE_ASSESSMENT.md", "Animation & Design Resource Assessment", "knowledge"),
    ("docs/ZYNTH_SECOND_BRAIN_INFORMATION_ARCHITECTURE.md", "Second Brain Information Architecture", "knowledge"),
    ("research/myanmar_agency_market_findings.md", "Myanmar Agency Market Findings", "knowledge"),
    ("research/singapore_agency_market_findings.md", "Singapore Agency Market Findings", "knowledge"),
    ("research/myanmar_singapore_agency_pricing_signals.md", "Myanmar–Singapore Pricing Signals", "knowledge"),
)


def _human(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _relative(path: Path) -> str:
    try:
        return path.relative_to(_REPO).as_posix()
    except ValueError:
        return path.as_posix()


def _node(
    node_id: str,
    label: str,
    kind: str,
    cluster: str,
    *,
    status: str = "available",
    description: str = "",
    source: str = "",
    meta: str = "",
    governance: str = "Internal reference; no external action.",
    updated: str = "",
) -> dict[str, str]:
    return {
        "id": node_id,
        "label": label,
        "kind": kind,
        "cluster": cluster,
        "status": status,
        "description": description,
        "source": source,
        "meta": meta,
        "governance": governance,
        "updated": updated,
    }


def _edge(source: str, target: str, relation: str, *, active: bool = False) -> dict[str, Any]:
    return {"source": source, "target": target, "relation": relation, "active": active}


def _agent_nodes() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, Any]] = []
    for path in sorted((_REPO / "backend" / "agents").glob("*.py")):
        if path.name.startswith("_") or path.stem == "base":
            continue
        slug = path.stem
        node_id = f"agent:{slug}"
        nodes.append(_node(
            node_id, _human(slug), "agent", "core",
            description="ZYNTH runtime specialist available to the agency workflow.",
            source=_relative(path), meta="Python agent specification",
            governance="Produces internal work under the ZYNTH Operating Contract; external commitments remain founder-gated.",
        ))
        edges.append(_edge("hub:core", node_id, "orchestrates"))
    return nodes, edges


def _skill_nodes() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, Any]] = []
    for path in sorted(_SKILLS.glob("*/SKILL.md")):
        slug = path.parent.name
        node_id = f"skill:{slug}"
        resources = sum(1 for p in path.parent.rglob("*") if p.is_file() and p.name != "SKILL.md")
        nodes.append(_node(
            node_id, _human(slug), "skill", "capability",
            description="Versioned ZYNTH operating capability with a defined trigger, workflow and quality controls.",
            source=_relative(path), meta=f"{resources} supporting resource{'s' if resources != 1 else ''}",
            governance="Applies the shared operating contract and cannot approve external release.",
        ))
        edges.append(_edge("hub:capability", node_id, "contains"))
        edges.append(_edge(node_id, "doc:capability-standard", "governed by"))
    for agent, skills in _AGENT_SKILLS.items():
        for skill in skills:
            if (_SKILLS / skill / "SKILL.md").is_file():
                edges.append(_edge(f"agent:{agent}", f"skill:{skill}", "uses"))
    return nodes, edges


def _document_nodes() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, Any]] = []
    for source_rel, label, cluster in _KEY_DOCUMENTS:
        path = _REPO / source_rel
        if not path.is_file():
            continue
        slug = "capability-standard" if source_rel.endswith("ZYNTH_CAPABILITY_SYSTEM_STANDARD.md") else path.stem.lower().replace("zynth_", "").replace("_", "-")
        node_id = f"doc:{slug}"
        nodes.append(_node(
            node_id, label, "document", cluster,
            description="Standing ZYNTH documentation retained in the repository and founder knowledge system.",
            source=source_rel, meta="Repository document",
            governance="Evidence/reference document; verify dynamic market facts and client details at point of use.",
            updated=datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
        ))
        edges.append(_edge("hub:knowledge", node_id, "contains"))
        vault_path = _REPO / "vault" / "ZYNTH-OS"
        if vault_path.is_dir():
            edges.append(_edge(node_id, "hub:knowledge", "mirrors to"))
    return nodes, edges


def _live_nodes(dashboard: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, Any]] = []

    projects = dashboard.get("projects") or []
    for row in projects[:18]:
        pid = str(row.get("id") or row.get("name") or "project")
        approved = row.get("founder_approval") == "approved" or row.get("source") in {"dashboard", "md", "owner"}
        pending = bool(row.get("founder_confirmation_required")) and row.get("founder_approval") == "pending"
        status = "review" if pending else ("approved" if approved else "available")
        nodes.append(_node(
            f"project:{pid}", row.get("name") or "Project", "project", "operations", status=status,
            description="Founder project record and commercial operating unit.", source="utils/projects.py",
            meta=" · ".join(x for x in (str(row.get("kind") or ""), str(row.get("market") or ""), str(row.get("stage") or "")) if x),
            governance="Founder confirmation is required before an agent-discovered lead can become a proposal, won, delivery or completion workflow.",
        ))
        edges.append(_edge("hub:operations", f"project:{pid}", "contains", active=True))
        if pending:
            edges.append(_edge(f"project:{pid}", "hub:monitoring", "requires approval", active=True))

    for item in (dashboard.get("deliverables") or [])[:18]:
        title = str(item.get("title") or "Internal output")
        nid = f"output:{abs(hash(title))}"
        nodes.append(_node(
            nid, title, str(item.get("type") or "output"), "outputs", status="internal",
            description="Current internal ZYNTH output available for founder review.", source="proposal library / deliverables",
            meta=str(item.get("meta") or "Internal concept"),
            governance="Internal/review output. It is not a client commitment, publication or released production asset.",
            updated=str(item.get("date") or ""),
        ))
        edges.append(_edge("hub:outputs", nid, "contains", active=True))
        edges.append(_edge("agent:proposal_factory", nid, "creates"))

    for item in (dashboard.get("creative_jobs") or [])[:12]:
        jid = str(item.get("id") or item.get("title") or "creative-job")
        status = "review" if "required" in str(item.get("approval_state", "")).lower() else "approved"
        nodes.append(_node(
            f"creative:{jid}", str(item.get("title") or "Creative job"), str(item.get("kind") or "creative job"), "outputs", status=status,
            description="Prepared image, video or 3D production route.", source="utils/creative_queue.py",
            meta=str(item.get("approval_state") or "review required"),
            governance="Production is blocked until a linked founder-approved project permits the route.",
        ))
        edges.append(_edge("hub:outputs", f"creative:{jid}", "queues", active=True))
        edges.append(_edge(f"creative:{jid}", "hub:monitoring", "requires approval", active=status == "review"))

    for link in ((dashboard.get("connections") or {}).get("links") or []):
        key = str(link.get("key") or link.get("name") or "connection").lower().replace(" ", "-")
        status = str(link.get("status") or "warn")
        nodes.append(_node(
            f"monitor:{key}", str(link.get("name") or key), "monitor", "monitoring", status=status,
            description="Live connection or runtime health diagnostic.", source="utils/connections.py",
            meta=str(link.get("detail") or ""), governance=str(link.get("fix") or "Review the named diagnostic before changing a connection."),
            updated=str((dashboard.get("connections") or {}).get("checked_at") or ""),
        ))
        edges.append(_edge("hub:monitoring", f"monitor:{key}", "monitors", active=status in {"warn", "down"}))

    for switch in dashboard.get("switches") or []:
        if switch.get("master"):
            continue
        name = str(switch.get("name") or "switch")
        state = bool(switch.get("on"))
        nodes.append(_node(
            f"switch:{name}", name, "switch", "monitoring", status="active" if state else "dormant",
            description="Founder-controlled internal automation switch.", source="utils/switches.py",
            meta="ON — internal workflow enabled" if state else "OFF — internal workflow paused",
            governance="Switches may enable internal work only; sending, publishing, spend and release require their own founder approval controls.",
        ))
        edges.append(_edge("hub:monitoring", f"switch:{name}", "controls", active=state))

    totals = dashboard.get("totals") or {}
    nodes.append(_node(
        "data:operating-records", "Operating Records", "data", "operations", status="available",
        description="Live aggregate of ZYNTH prospects, leads, tasks, proposals, vendors, venues and notes.", source="utils/dashboard.py",
        meta=(f"{totals.get('prospects', 0)} prospects · {totals.get('leads', 0)} leads · "
              f"{totals.get('tasks_open', 0)} open tasks · {totals.get('proposals', 0)} proposals"),
        governance="Structured records inform priorities; they do not constitute verified external commitments by themselves.",
    ))
    edges.append(_edge("hub:operations", "data:operating-records", "measures"))
    return nodes, edges


def _learning_nodes() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, Any]] = []
    try:
        from utils import mistakes
        entries = mistakes.recent(10)
        stats = mistakes.stats()
    except Exception:
        entries, stats = [], {"total": 0, "by_area": {}}
    nodes.append(_node(
        "learning:mistakes", "Mistakes & Shortfalls", "error-log", "learning",
        status="warn" if entries else "available", description="Persisted record of failures, shortfalls and revise verdicts that feed the improver loop.",
        source="utils/mistakes.py", meta=f"{stats.get('total', 0)} recorded entries", governance="Errors are recorded for learning; review context before applying a corrective change.",
    ))
    edges.append(_edge("hub:learning", "learning:mistakes", "records", active=bool(entries)))
    nodes.append(_node(
        "agent:improver", "Improver", "agent", "learning", status="active",
        description="Reviews recent observations and turns recurring patterns into durable lessons.", source="backend/agents/improver.py",
        meta="Self-improvement and quality learning", governance="Improvement proposals remain internal until an authorised maintainer accepts a change.",
    ))
    edges.append(_edge("learning:mistakes", "agent:improver", "informs", active=bool(entries)))
    edges.append(_edge("agent:improver", "doc:capability-standard", "improves"))
    for index, entry in enumerate(entries[:6], 1):
        severity = str(entry.get("severity") or "warn")
        nid = f"error:{index}"
        nodes.append(_node(
            nid, str(entry.get("what") or "Recorded observation"), "error", "learning", status=severity,
            description=str(entry.get("detail") or "Recorded system observation."), source="outputs/proposal_pool/mistakes.json",
            meta=f"{entry.get('area', 'general')} · {entry.get('at', '')}", governance="Observation only; investigate before treating it as a production root cause.",
        ))
        edges.append(_edge("learning:mistakes", nid, "contains", active=severity == "error"))
    return nodes, edges


def build_state() -> dict[str, Any]:
    """Return a safe, source-grounded graph state for the Second Brain surface."""
    try:
        from utils.dashboard import build_state as dashboard_state
        dashboard = dashboard_state()
    except Exception:
        dashboard = {}

    nodes: list[dict[str, str]] = []
    edges: list[dict[str, Any]] = []
    for key, meta in _CLUSTER.items():
        nodes.append(_node(
            f"hub:{key}", meta["label"], "hub", key, status="active" if key in {"core", "operations", "monitoring"} else "available",
            description=f"ZYNTH Second Brain {meta['label'].lower()} constellation.", source="Second Brain information architecture",
            meta="Live map cluster", governance="Cluster summary; open a child node for the underlying source and control.",
        ))

    for make in (_agent_nodes, _skill_nodes, _document_nodes):
        made_nodes, made_edges = make()
        nodes.extend(made_nodes); edges.extend(made_edges)
    live_nodes, live_edges = _live_nodes(dashboard)
    learning_nodes, learning_edges = _learning_nodes()
    nodes.extend(live_nodes); nodes.extend(learning_nodes)
    edges.extend(live_edges); edges.extend(learning_edges)

    # A capability standard is a standing governing relationship, not a live execution claim.
    for agent in (n for n in nodes if n.get("kind") == "agent" and n.get("id") != "agent:improver"):
        edges.append(_edge(agent["id"], "doc:capability-standard", "informed by"))

    clusters = []
    for key, meta in _CLUSTER.items():
        cluster_nodes = [n for n in nodes if n.get("cluster") == key and n.get("kind") != "hub"]
        clusters.append({
            "id": key, "label": meta["label"], "color": meta["color"], "icon": meta["icon"],
            "count": len(cluster_nodes), "alert_count": sum(1 for n in cluster_nodes if n.get("status") in {"warn", "down", "error", "review"}),
        })

    return {
        "generated": datetime.now().strftime("%a %d %b %Y, %H:%M"),
        "title": "ZYNTH Second Brain",
        "subtitle": "Real capability, evidence, work, control and learning — connected.",
        "clusters": clusters,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "agents": sum(1 for n in nodes if n.get("kind") == "agent"),
            "skills": sum(1 for n in nodes if n.get("kind") == "skill"),
            "documents": sum(1 for n in nodes if n.get("kind") == "document"),
            "outputs": sum(1 for n in nodes if n.get("cluster") == "outputs" and n.get("kind") != "hub"),
            "alerts": sum(1 for n in nodes if n.get("status") in {"warn", "down", "error", "review"}),
        },
        "dashboard": {
            "generated": dashboard.get("generated", ""),
            "connections": dashboard.get("connections", {}),
            "md_only": dashboard.get("md_only", True),
            "queue": dashboard.get("queue", {}),
        },
    }
