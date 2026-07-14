# ZYNTH Vault — Obsidian ↔ Bot bridge

This folder is the live link between your **Obsidian vault** (where you
think and take notes) and the **AI bot** (which reads these notes and uses
them in every proposal, brief, and answer).

Any `.md` file you put here becomes knowledge the agents use — the same as
`backend/knowledge/`, but this folder is meant for the notes you write and
update often: clients, projects, event post-mortems, meeting notes, ideas.

## Two ways your notes reach the bot

**1. Instant — via Telegram (no setup):**
Send `/note <your note>` (typing or voice) to the bot. It files the note
here and the agents can use it immediately. Best for quick capture on the go.

**2. Bulk — via Obsidian Git (one-time setup, then automatic):**
Sync your whole Obsidian vault into this folder so everything you write in
Obsidian flows to the bot.

Setup (once):
1. In Obsidian → Settings → Community plugins → Browse → install **"Obsidian Git"**
2. Point it at this repository's `vault/` folder as your vault location
3. Enable **auto-commit + auto-push** (e.g. every 10 minutes)
4. After it pushes, the bot picks up your notes on its next redeploy (~3 min)

## Rules (same as the knowledge base)
- Only `.md` files are read.
- Add `<!-- TEMPLATE -->` at the top of a file to keep it as a private
  draft the agents ignore.
- Keep notes concise — each note is capped at ~2,500 characters when fed to
  the agents, so write the signal, not the whole transcript.
- No passwords or API keys here — this repo is readable by anyone with access.
