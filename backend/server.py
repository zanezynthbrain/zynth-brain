"""Optional production HTTP surface for the ZYNTH agent backend.

Wraps the same :class:`~agents.OrchestratorAgent` used by ``main.py`` in a
small FastAPI app so the existing Next.js frontend (or any other client)
can trigger workflows over HTTP instead of shelling out to the CLI.

Run with:

    uvicorn server:app --reload --port 8000
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents import OrchestratorAgent, WORKFLOWS, build_default_agents
from config import get_settings
from utils.logging_config import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="ZYNTH Agent Backend", version="1.0.0")

_agents = build_default_agents()
_orchestrator = OrchestratorAgent(agents=_agents)


class WorkflowRequest(BaseModel):
    client_brief: dict[str, Any]
    workflow: str = "full_campaign"
    csv_relative_path: str | None = None


class RouteRequest(BaseModel):
    request_text: str


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "mock_mode": _orchestrator.llm.is_mocked, "workflows": list(WORKFLOWS)}


@app.post("/workflow/run")
async def run_workflow(payload: WorkflowRequest) -> dict[str, Any]:
    if payload.workflow not in WORKFLOWS:
        raise HTTPException(status_code=400, detail=f"Unknown workflow '{payload.workflow}'")

    agent_kwargs = {}
    if payload.csv_relative_path:
        agent_kwargs["paid_ads"] = {"csv_relative_path": payload.csv_relative_path}

    report = await _orchestrator.run_workflow(
        payload.client_brief, workflow=payload.workflow, agent_kwargs=agent_kwargs
    )
    return {
        "workflow": report.workflow,
        "status": report.status,
        "total_tokens": report.total_tokens,
        "results": {
            key: {"success": r.success, "data": r.data, "error": r.error}
            for key, r in report.agent_results.items()
        },
    }


@app.post("/workflow/route")
async def route(payload: RouteRequest) -> dict[str, str]:
    workflow = await _orchestrator.route_request(payload.request_text)
    return {"workflow": workflow}
