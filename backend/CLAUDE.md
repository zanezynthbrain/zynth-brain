# ZYNTH Agent Backend

A production-oriented, async multi-agent backend for ZYNTH (www.zynth.asia)
covering market research/SEO, content creation, lead generation/outreach,
and paid ads/analytics — coordinated by an Orchestrator agent that routes
requests, runs agents in dependency order, and gates every output through
an LLM-as-judge QA review before it's considered final.

This file (and the surrounding `backend/` directory) is intentionally
self-contained: it does not replace the existing Next.js frontend in
`zynth-brain/` (the chat UI with ZARA/BRIX/CALI/KAI/SOMI/ANA personas).
Think of this backend as the heavier, structured-workflow engine that the
frontend (or any other client) can call into via `server.py`, while the
existing Next.js chat app remains the lightweight conversational surface.

## Project Structure

```
backend/
  agents/
    base.py          BaseAgent abstract class, AgentResult, AgentError
    orchestrator.py   OrchestratorAgent: routing, DAG execution, QA gate
    research_seo.py   Market Research & SEO Agent
    copywriter.py      Content & Creative Copywriter Agent
    lead_gen.py        Lead Generation & Outreach Agent
    paid_ads.py         Paid Ads & Analytics Agent
  utils/
    state.py          SharedMemory: async-safe centralized state/memory
    llm_client.py      Claude API wrapper: retries, token budget, JSON repair, mock mode
    tools.py           HTTP, file read/write, JSON validation tool mockups
    logging_config.py  Logging setup
  config/
    settings.py        Env-driven settings (pydantic-settings)
    brand.py            ZYNTH brand voice/persona constants
  tests/                pytest suite (runs fully offline via mock mode)
  main.py               Async CLI entrypoint
  server.py              Optional FastAPI HTTP surface
  requirements.txt
  .env.example
```

## How the pieces fit together

1. **`SharedMemory`** (`utils/state.py`) is a namespaced, `asyncio.Lock`-guarded
   key-value store passed into every agent call. Each agent writes its
   structured output to its own namespace (e.g. `research_seo`,
   `copywriter`) and may read any other agent's namespace. This is how the
   Research Agent's keyword/competitor findings flow directly into the
   Copywriter Agent's prompt, and how the Copywriter's ad copy flows into
   the Paid Ads Agent's campaign structure — no agent calls another agent
   directly; they only ever talk through state.

2. **`BaseAgent`** (`agents/base.py`) gives every concrete agent: a brand-
   consistent system prompt (ZYNTH voice + role), a JSON Schema contract
   for its output, and a `run()` method that calls the LLM, validates the
   result against the schema (auto-repairing malformed JSON), persists it
   to `SharedMemory`, and logs an audit entry. Concrete agents only
   implement `build_user_prompt()` and declare `output_schema`.

3. **`OrchestratorAgent`** (`agents/orchestrator.py`) is "The Director":
   - `route_request(text)` classifies a free-text client ask into one of
     the predefined workflows using an LLM call against an enum schema.
   - `run_workflow(client_brief, workflow=...)` resolves the workflow's
     step graph into dependency-ordered parallel groups (via topological
     sort), runs each group with `asyncio.gather`, and checks the
     workflow-wide token budget before every group — aborting gracefully
     (marking remaining steps "skipped") if the budget is exhausted.
   - `_run_with_qa_gate()` wraps every agent call: after the agent
     produces output, a second LLM call (the QA gate) scores it for
     brand-voice consistency, completeness, and actionability. If it
     scores below `ZYNTH_QA_MIN_PASS_SCORE`, the agent is re-run with the
     QA feedback appended to its prompt, up to `ZYNTH_MAX_AGENT_RETRIES`
     times.

4. **`LLMClient`** (`utils/llm_client.py`) is the only place that talks to
   Claude. It handles exponential-backoff retries on transient failures,
   enforces per-call token budgets, and — critically — `complete_json()`
   guarantees schema-conforming output: if the model's JSON fails
   validation, the exact `jsonschema` error is fed back to the model and
   it's asked to self-correct, up to `ZYNTH_MAX_JSON_REPAIR_ATTEMPTS`
   times, before raising `MalformedOutputError`.

5. **Mock mode**: if `ANTHROPIC_API_KEY` is unset, `LLMClient` never
   constructs a real Anthropic client. `complete()` returns a static mock
   string; `complete_json()` synthesizes a schema-conforming placeholder
   object directly from the JSON Schema (no LLM call at all). This means
   the entire orchestrator — routing, parallel DAG execution, the QA gate,
   token accounting, CSV-driven ROAS math — runs deterministically offline.
   This is how the test suite and `main.py` work without any credentials.

## Running

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY to go live; leave blank for mock mode
```

Run the default end-to-end campaign workflow (sample brief, mock mode if
no API key is set):

```bash
python main.py
python main.py --workflow research_only
python main.py --brief '{"company": "Acme SaaS", "industry": "fintech"}'
python main.py --csv path/inside/outputs/perf.csv --workflow ads_only
python main.py --request "We just need cold emails and a prospect list"
```

Each run writes the full state snapshot (every agent's structured output,
the audit log, and token usage) to `outputs/report.json` (configurable via
`--out`), and prints a short status summary to stdout.

Run as an HTTP service (for the Next.js frontend or any other client):

```bash
uvicorn server:app --reload --port 8000
# POST /workflow/run    {"client_brief": {...}, "workflow": "full_campaign"}
# POST /workflow/route  {"request_text": "free text client ask"}
# GET  /health
```

## Testing

```bash
pytest
```

The suite (`tests/`) runs entirely offline in mock mode — `tests/conftest.py`
forces `ANTHROPIC_API_KEY=""` and `ZYNTH_ALLOW_NETWORK=false` regardless of
the developer's local `.env`, so CI never needs real credentials. Coverage
includes: `SharedMemory` concurrency/correctness, the HTTP/file/JSON tool
mockups (including a path-traversal rejection test), the LLM client's
retry/mock/JSON-repair behavior, each agent's prompt building against
upstream state, the deterministic CSV → ROAS math, and the orchestrator's
dependency-ordered execution, workflow selection, and routing.

When you add a new agent or change an `output_schema`, add a focused test
in `tests/test_agents.py` rather than relying on the orchestrator tests to
catch regressions — the mock-mode synthesis will happily produce *some*
JSON for almost any schema, so schema-shape bugs need an explicit assertion
to be caught.

## Extending the framework

**Add a new agent:**
1. Subclass `BaseAgent` in `agents/`, set `agent_key`, `display_name`,
   `role_description`, and `output_schema`.
2. Implement `build_user_prompt(self, memory, **kwargs)` — read whatever
   upstream namespaces you need via `await memory.get("other_agent_key")`.
3. Register it in `agents/__init__.py::build_default_agents()`.
4. Add it to a workflow in `agents/orchestrator.py::WORKFLOWS` (or a new
   workflow) with the right `depends_on` list.

**Wire up a real research/SEO API:** replace the `http_get` calls in
`agents/research_seo.py` with real Serper/SEMrush/Jina endpoints, set the
corresponding API key in `.env`, and flip `ZYNTH_ALLOW_NETWORK=true`.
`utils/tools.py::http_get/http_post` already do real `httpx` calls when
network is enabled — only the URLs/auth headers need to change.

**Scale beyond a single process:**
- Swap `asyncio.gather` group execution in `OrchestratorAgent.run_workflow`
  for a task queue (Celery/RQ/Temporal) if agent calls need to survive
  process restarts or run on separate workers — `SharedMemory` would move
  from in-process to Redis/Postgres-backed, but the agent interface
  (`run(memory, **kwargs) -> AgentResult`) doesn't need to change.
- The custom DAG executor (`_topological_groups`) is intentionally small
  and dependency-free; if the workflow graph grows complex (conditional
  branches, human-in-the-loop approval steps, cycles with bounded
  iteration), consider migrating it to LangGraph or AutoGen — `BaseAgent.run()`
  already returns a clean `AgentResult` that maps onto either framework's
  node contract with minimal changes.
- For higher-throughput production use, replace the per-call
  `AsyncAnthropic` client in `utils/llm_client.py` with a pooled/cached
  client and add response caching (e.g. for repeated competitor/keyword
  research on the same client) keyed on `(agent_key, prompt_hash)`.
- `ZYNTH_MAX_TOKENS_PER_WORKFLOW` currently aborts the workflow when
  exceeded; for production you likely want this to trigger a cheaper
  fallback model (`ZYNTH_FALLBACK_MODEL_NAME` is already defined in
  settings but not yet wired into `LLMClient` — that's the natural next
  hook) rather than aborting outright.
- Persist `SharedMemory` snapshots (already JSON-serializable via
  `.snapshot()`) to a real datastore per `workflow_id` so client workflows
  can be resumed, audited, or re-run from a specific step.
