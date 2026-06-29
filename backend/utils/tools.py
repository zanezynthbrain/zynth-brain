"""Basic tool mockups shared by every agent.

These wrap the three tool categories required by the agency workflows:
outbound HTTP calls (SEO/research APIs, CRM webhooks, ad platform APIs),
local file I/O (reading CSV exports, writing generated content to disk),
and JSON validation (guaranteeing structured agent output is well-formed
before it's handed to the next agent).

Network calls are mocked by default (``ZYNTH_ALLOW_NETWORK=false``) so the
framework runs deterministically in CI/sandboxes without external
dependencies or API keys. Flip the flag once real credentials are wired
up.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Directory agents are sandboxed to for file read/write tools.
_SANDBOX_ROOT = Path(__file__).resolve().parent.parent / "outputs"
_SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)


@dataclass
class ToolResult:
    """Uniform envelope returned by every tool call."""

    ok: bool
    data: Any = None
    error: str | None = None
    mocked: bool = False


def _resolve_sandbox_path(relative_path: str) -> Path:
    """Resolve a user-supplied relative path inside the output sandbox.

    Raises ``ValueError`` if the resolved path would escape the sandbox,
    preventing path-traversal writes/reads from agent-generated paths.
    """
    candidate = (_SANDBOX_ROOT / relative_path).resolve()
    if _SANDBOX_ROOT not in candidate.parents and candidate != _SANDBOX_ROOT:
        raise ValueError(f"Path '{relative_path}' escapes the sandboxed output directory")
    return candidate


async def http_get(url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> ToolResult:
    """Perform an HTTP GET, or return a deterministic mock when network access is disabled."""
    settings = get_settings()
    if not settings.allow_network:
        logger.info("http_get mocked (ZYNTH_ALLOW_NETWORK=false): %s", url)
        return ToolResult(ok=True, mocked=True, data={"url": url, "params": params or {}, "mock": True})

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return ToolResult(ok=True, data=response.json() if _looks_like_json(response) else response.text)
    except httpx.HTTPError as exc:
        logger.warning("http_get failed for %s: %s", url, exc)
        return ToolResult(ok=False, error=str(exc))


async def http_post(url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> ToolResult:
    """Perform an HTTP POST, or return a deterministic mock when network access is disabled."""
    settings = get_settings()
    if not settings.allow_network:
        logger.info("http_post mocked (ZYNTH_ALLOW_NETWORK=false): %s", url)
        return ToolResult(ok=True, mocked=True, data={"url": url, "payload": payload or {}, "mock": True})

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return ToolResult(ok=True, data=response.json() if _looks_like_json(response) else response.text)
    except httpx.HTTPError as exc:
        logger.warning("http_post failed for %s: %s", url, exc)
        return ToolResult(ok=False, error=str(exc))


def _looks_like_json(response: httpx.Response) -> bool:
    return "application/json" in response.headers.get("content-type", "")


def read_file(relative_path: str) -> ToolResult:
    """Read a UTF-8 text file from the sandboxed output directory."""
    try:
        path = _resolve_sandbox_path(relative_path)
        if not path.is_file():
            return ToolResult(ok=False, error=f"File not found: {relative_path}")
        return ToolResult(ok=True, data=path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return ToolResult(ok=False, error=str(exc))


def write_file(relative_path: str, content: str) -> ToolResult:
    """Write UTF-8 text content into the sandboxed output directory."""
    try:
        path = _resolve_sandbox_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return ToolResult(ok=True, data={"path": str(path)})
    except (ValueError, OSError) as exc:
        return ToolResult(ok=False, error=str(exc))


def validate_json(payload: str | dict[str, Any], schema: dict[str, Any]) -> ToolResult:
    """Validate a JSON string or dict against a JSON Schema.

    Returns ``ok=True`` with the parsed object in ``data`` on success, or
    ``ok=False`` with a human-readable ``error`` describing the first
    validation failure.
    """
    try:
        obj = json.loads(payload) if isinstance(payload, str) else payload
    except json.JSONDecodeError as exc:
        return ToolResult(ok=False, error=f"Invalid JSON: {exc}")

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(obj))
    if errors:
        worst = best_match(errors)
        return ToolResult(ok=False, error=str(worst))
    return ToolResult(ok=True, data=obj)
