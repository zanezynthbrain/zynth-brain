# Where everything lives, and how it connects

**Updated:** 18 August 2026

One question this answers: *when I want something produced, where do I ask?*

---

## Where to ask for work

| You want… | Ask here | What happens |
|---|---|---|
| A proposal, production, project or program | **`/command` → Proposals → ASK ZYNTH TO PRODUCE** | Queues into the founder task list → appears in Telegram → produced |
| The same, by message | **Telegram bot** — `/proposal`, `/content`, `/event` | Runs the matching agent immediately |
| Deep creative work, code, anything unusual | **This chat (Claude Code)** | Full repo access; commits and deploys |
| A quick look at the whole library | **`/constellation`** | The gold star map — unchanged, still live |

The interface **queues**; Telegram and this chat **execute**. The interface is
deliberately not an execution surface — nothing spends money without passing
through the founder.

---

## Where things are stored

| Thing | Path | Notes |
|---|---|---|
| Composed proposals | `vault/ZYNTH-OS/Proposal-Library/*.md` | The source of truth. 15 today. |
| Concept pool | `backend/outputs/proposal_pool/index.json` | 75 titles awaiting writing |
| Exported .docx | `deliverables/proposals/docx/` | 15 files, dated, served at `/docs/<name>` |
| Films & spec work | `deliverables/` | KitKat spec, OUT OF CHAOS |
| 3D stage concepts | `outputs/3d_stage_exhibition_library/` | 8 concepts in 7 categories |
| Agents | `backend/agents/` + `specs/*.md` | 25 |
| Skills | `.claude/skills/` | 36 |
| The scan output | `backend/outputs/vault-index.json` | Generated, not committed |
| The interface | `backend/templates/dashboard_template.html` | Holds no data of its own |

---

## How it connects

```
   repo + vault
        │
        ▼
   build_vault_index.py ──► vault-index.json ──► build_dashboard.py ──► /command
        │                                   └──► proposals_to_docx.py ──► /docs/*.docx
        │
        └──► Telegram bot (24/7 on Railway) ──► founder brief, task queue
```

**One rule makes this work:** the interface reads the scan and nothing else.
Add a proposal to the vault → it appears. Delete it → it disappears. There is
no second copy to keep in sync.

## Live URLs

- `https://zynth-ai-marketing-firm.up.railway.app/command` — the command dashboard
- `…/constellation` — the proposal constellation
- `…/docs/<filename>.docx` — any exported proposal
- `…/second-brain`, `…/health` — unchanged

## The one gap

**Google Drive is not connected.** `GOOGLE_SERVICE_ACCOUNT_JSON` and
`DRIVE_DELIVERABLES_FOLDER` are unset on Railway, so no upload has ever run.
The .docx files are real and download from Railway today; the Drive button
lights up the moment those two variables exist. See `docs/DRIVE_SETUP_GUIDE.md`.
