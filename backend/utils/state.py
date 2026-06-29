"""Centralized, async-safe state/memory engine.

A single :class:`SharedMemory` instance is threaded through an entire
client workflow. Each agent reads whatever upstream context it needs (e.g.
the Copywriter reads the Research Agent's keyword findings) and writes its
own output back under a namespaced key, so downstream agents -- and the
Orchestrator's QA gate -- always see a consistent, append-only history.
"""

from __future__ import annotations

import asyncio
import copy
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogEntry:
    """A single audit-trail entry recorded during workflow execution."""

    timestamp: float
    agent: str
    event: str
    detail: dict[str, Any] = field(default_factory=dict)


class SharedMemory:
    """Thread/async-safe key-value store shared across all agents.

    Namespacing convention: each agent owns a top-level key matching its
    ``agent_key`` (e.g. ``"research_seo"``, ``"copywriter"``). Agents should
    only *write* to their own namespace, but may *read* any namespace to
    pull context produced by upstream agents.
    """

    def __init__(self, client_brief: dict[str, Any] | None = None) -> None:
        self._lock = asyncio.Lock()
        self._store: dict[str, Any] = {"client_brief": client_brief or {}}
        self._log: list[LogEntry] = []
        self._token_usage: dict[str, int] = {"input": 0, "output": 0}

    async def set(self, namespace: str, value: Any) -> None:
        async with self._lock:
            self._store[namespace] = value

    async def update(self, namespace: str, **kwargs: Any) -> None:
        async with self._lock:
            existing = self._store.get(namespace, {})
            if isinstance(existing, dict):
                existing.update(kwargs)
                self._store[namespace] = existing
            else:
                self._store[namespace] = kwargs

    async def get(self, namespace: str, default: Any = None) -> Any:
        async with self._lock:
            return copy.deepcopy(self._store.get(namespace, default))

    async def record_tokens(self, input_tokens: int, output_tokens: int) -> None:
        async with self._lock:
            self._token_usage["input"] += input_tokens
            self._token_usage["output"] += output_tokens

    async def total_tokens(self) -> int:
        async with self._lock:
            return self._token_usage["input"] + self._token_usage["output"]

    async def log(self, agent: str, event: str, **detail: Any) -> None:
        async with self._lock:
            self._log.append(
                LogEntry(timestamp=time.time(), agent=agent, event=event, detail=detail)
            )

    async def snapshot(self) -> dict[str, Any]:
        """Return a deep-copied, JSON-serializable view of the full state."""
        async with self._lock:
            return {
                "store": copy.deepcopy(self._store),
                "token_usage": dict(self._token_usage),
                "log": [
                    {
                        "timestamp": entry.timestamp,
                        "agent": entry.agent,
                        "event": entry.event,
                        "detail": entry.detail,
                    }
                    for entry in self._log
                ],
            }


@dataclass
class WorkflowState:
    """Lightweight wrapper bundling a workflow's memory with run metadata."""

    workflow_id: str
    memory: SharedMemory
    started_at: float = field(default_factory=time.time)
    status: str = "pending"
    error: str | None = None
