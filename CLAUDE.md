# ZYNTH — repo entry point for Claude Code

**On session start, read `docs/handoff/2026-08-07.md`** — the latest cross-session
handoff: what is on `main`, what is open, and two things that would break
something if you continue without reading them.

**For the full system map — storage, skills, commands, learning loop, n8n
comparison — read `docs/ZYNTH_MASTER_GUIDE.md`** (bilingual EN + မြန်မာ).

Then, in this order:
1. `CONTEXT.md` — the running decision log. What was decided, when, and why.
2. `NORTH_STAR.md` — what ZYNTH is actually for, if the direction feels unclear.
3. `backend/CLAUDE.md` — how the agent backend is laid out and how to extend it.

The business bible is `docs/playbook/00`–`08`. The tools serve that playbook;
they are not the business.

## Non-negotiables (full list in CONTEXT.md → Standing rules)
- **R1–R5 financial law** lives in `backend/knowledge/01_zynth_services.md` and
  is injected into every agent prompt. That file is the single source of truth —
  if another document disagrees, that document is wrong.
- Never commit `.env` or real keys.
- Data that must survive a redeploy lives in the repo (the pool pattern under
  `backend/outputs/proposal_pool/`), never only in the container.
- Agents may not present an **unverified number** as fact — tag it, or leave it
  blank. Verification is human work.
- Nothing goes to a client, a page or an inbox without **MD approval**.
- **Session definition-of-done:** update `CONTEXT.md`, regenerate `HANDOFF.md`,
  run `python backend/tools/refresh_bridge.py`, commit, push.

## Skills
Repo-versioned skills live in `.claude/skills/<name>/SKILL.md` and travel with
the repo. Skills in `~/.claude/skills/` are user-level and do **not** — put
anything the team relies on in the repo.
