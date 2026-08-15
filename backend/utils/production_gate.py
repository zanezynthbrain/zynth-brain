"""Founder-controlled bridge from daily ideas to creative production.

Daily Agency Workforce output is intentionally internal. This module is the only
route for a daily package to enter the creative queue: it verifies the linked
real project, confirms the founder's recorded approval, logs the decision and
constrains automation to approved image templates. 3D stays founder-triggered
until a durable Blender runner and modular scene-library validation are live.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from utils import creative_queue, daily_workforce, projects

AUTOMATION_MODES = ("founder_triggered", "template_auto")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _find_package(payload: dict[str, Any], package_id: str) -> dict[str, Any] | None:
    for package in payload.get("packages", []):
        if package.get("id") == package_id:
            return package
    return None


def _kind_for(package: dict[str, Any]) -> str:
    production_lane = package.get("production_lane")
    if production_lane == "scene3d":
        return "scene3d"
    # Storyboard outputs are image frames at this point. Video itself stays
    # outside autonomous execution until the provider route is verified.
    return "image"


def _prompt_for(package: dict[str, Any], project: dict[str, Any]) -> str:
    """Build a tool-ready prompt without asserting unsupported client facts."""
    market = "Myanmar" if package.get("market") == "MM" else "Singapore"
    return (
        f"Create a premium, client-reviewable {package.get('work_lane_label', 'marketing')} visual concept "
        f"for the {project.get('kind', 'campaign')} project '{project.get('name', 'ZYNTH project')}'. "
        f"Market context: {market}; industry: {package.get('industry', '')}. "
        f"Creative concept: {package.get('creative_concept', '')}. "
        f"Visual direction: {package.get('creative_direction', '')}. "
        f"The visual must express this proposition: {package.get('single_minded_proposition', '')}. "
        "Use original, brand-neutral placeholder geometry where an unverified logo or product would appear. "
        "Do not render readable text, brand marks, Burmese typography, legal claims, celebrities or identifiable public figures; "
        "final typography, logo and legal copy will be composed after review."
    )


def authorise_package(
    *,
    day: str,
    package_id: str,
    project_id: str,
    approved_by: str,
    automation_mode: str = "founder_triggered",
    template_id: str = "",
    note: str = "",
) -> dict[str, Any]:
    """Approve one daily package for a linked, real project and queue its job.

    The founder decision on the real project is mandatory. ``template_auto`` is
    limited to a pre-approved image template; all 3D jobs and all untemplated
    work are founder-triggered, even after they enter the queue.
    """
    if automation_mode not in AUTOMATION_MODES:
        raise ValueError(f"automation_mode must be one of {AUTOMATION_MODES}")
    if not (approved_by or "").strip():
        raise ValueError("approved_by is required")

    project = projects.get(project_id)
    if not project:
        raise LookupError("linked project not found")
    if project.get("founder_confirmation_required") and project.get("founder_approval") != "approved":
        raise PermissionError("founder confirmation is required for the linked project")

    payload = daily_workforce.load_daily_run(day)
    if not payload:
        raise LookupError("daily workforce package not found")
    package = _find_package(payload, package_id)
    if not package:
        raise LookupError("package not found in daily workforce run")
    if package.get("status") != "internal_draft":
        raise ValueError("package has already been authorised, archived or otherwise resolved")

    kind = _kind_for(package)
    if automation_mode == "template_auto":
        if kind != "image":
            raise PermissionError("template_auto is currently limited to approved image templates; 3D remains founder-triggered")
        if not template_id.strip():
            raise ValueError("template_id is required for template_auto production")

    approval = {
        "approved_by": approved_by.strip()[:60],
        "approved_at": _now(),
        "project_id": project["id"],
        "project_name": project["name"],
        "automation_mode": automation_mode,
        "template_id": template_id.strip()[:80],
        "note": note.strip()[:300],
    }
    job = creative_queue.add(
        kind,
        project.get("client") or project["name"],
        package.get("title") or package_id,
        _prompt_for(package, project),
        notes=(
            "Daily Agency Workforce package; internal creative job only. "
            "Do not send to client, publish or use in paid media without the separate release process."
        ),
        spec={
            "daily_package_id": package_id,
            "daily_package_date": str(day)[:10],
            "project_id": project["id"],
            "work_lane": package.get("work_lane"),
            "production_lane": package.get("production_lane"),
            "automation_mode": automation_mode,
            "template_id": template_id.strip()[:80],
            "render_variants": 1,
        },
        source="daily_workforce",
        approval=approval,
    )

    package["status"] = "production_authorised"
    package["approval_status"] = "founder_approved"
    package["production_allowed"] = True
    package["production_authorised_at"] = approval["approved_at"]
    package["production_authorised_by"] = approval["approved_by"]
    package["linked_project_id"] = project["id"]
    package["creative_queue_job_id"] = job["id"]
    package["automation_mode"] = automation_mode
    daily_workforce.save_daily_run(payload)

    return {"package": package, "job": job, "project": project}


__all__ = ["AUTOMATION_MODES", "authorise_package"]
