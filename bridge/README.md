# bridge/ — live state for the MD's chat consultant

This folder is the **one place to sync to Google Drive** (`Company OS / 14 — Build State`)
so a fresh Claude session — or the MD's strategy consultant in Claude chat — can read
the current build state in one pass, without cloning the repo.

## What's in here (refreshed every session)
- `HANDOFF.md` — the condensed session digest (copied from repo root).
- `CONTEXT.md` — the full chronological decision log (copied from repo root).
- `knowledge/` — a copy of any new/changed `backend/knowledge/*.md`.

## How to refresh
At the end of a working session, run from the repo root:

```bash
python backend/tools/refresh_bridge.py
```

It copies the latest HANDOFF.md, CONTEXT.md, and knowledge files into `bridge/`.
The MD then syncs this single folder to Drive (or it rides along in the repo,
which is public — the consultant can read it directly on GitHub too).

## Why it exists
The repo is public, so the consultant can already read it on GitHub. `bridge/`
still earns its place as the **curated one-pass snapshot** — the consultant reads
`bridge/HANDOFF.md` first instead of re-deriving state from the whole repo.
