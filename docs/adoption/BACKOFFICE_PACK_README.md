# ZYNTH Back-Office Build — drop-in pack

Five finalised, drop-in files. Tree mirrors `zynth-brain`.

## What's here
```
skills/
  zb-icp/SKILL.md          # BD: define + score a prospect  (adapts realkimbarrett/avatar-extraction)
  zb-offer/SKILL.md        # BD: build a costed, compelling offer  (adapts realkimbarrett/offer-extraction)
  zb-objections/SKILL.md   # BD: pre-empt + neutralise objections  (adapts realkimbarrett/objection-crusher)
  zb-pitch-kit/SKILL.md    # Sales: assemble the pitch package  (adapts coreyhaines31/sales-enablement)
  yadana-finance/SKILL.md  # Finance dept + YADANA controller  (built from scratch — no adopt exists)
```

## How they chain
`zb-icp` (who + fears) → `zb-offer` (the offer) → `YADANA` (the price + margin check) → `zb-objections` (pre-empts) → `zb-pitch-kit` (assembles deck + one-pager). One spine, one set of numbers.

## Put them in the repo
Each `SKILL.md` is dual-purpose (Claude Code subagent **and** skill). Drop the folders under your skills path; for the ones you want as callable subagents, also symlink/copy into `.claude/agents/`. `yadana-finance` doubles as your Finance department OS — cross-link it from `docs/departments/`.

```bash
# from your local zynth-brain clone
cp -r skills/zb-icp skills/zb-offer skills/zb-objections skills/zb-pitch-kit skills/yadana-finance  <repo>/skills/
git add skills/
git commit -m "Add back-office build: zb- BD/sales cluster + YADANA finance dept"
git push
```
Nothing here is in your GitHub until you run that. There is no auto-sync from this chat.

## Still to build (next artifacts)
- **The live Finance workbook** (`.xlsx`) to the §10 spec in `yadana-finance` — Quote Builder that enforces the R1 margin floor, Project P&L, 13-week cashflow, KPI dashboard.
- **Reconcile R1–R5**: the margin law in `yadana-finance` is a clean working version. If your existing R1–R5 in `zynth-brain` differs, yours wins — swap that block.

---

## Trust-map of the list you pasted

I checked the non-obvious repos. Use this before wiring anything in — an MCP is *hands* (tool access), a skill is *brains* (domain knowledge). Your back-office gap is a brains gap; most of the list below is hands.

**✅ Real — safe to use**
- `ahujasid/blender-mcp` — real (16k+ stars, MIT). Your 3D/VERA path. Note: `execute_blender_code` runs arbitrary Python — powerful, use with care.
- `punkpeye/awesome-mcp-servers` — real; the main MCP index.
- `OthmanAdi/planning-with-files` — real (~22k stars). Genuinely useful for long-running event planning (context survives across sessions). Good pick.
- Figma MCP, FFmpeg-based video MCPs, Make MCP, Zapier MCP, HubSpot MCP (you have it), Stripe MCP, Google Workspace MCP — all real.

**❌ Does NOT exist — hallucinated**
- `rodneymbrown1/MCP-blender-video-editor` / "VideoDraft MCP" — no such repo. Real video-edit MCPs instead: `KyaniteLabs/kinocut` (guardrailed, agent-friendly, Apache-2.0), `chandler767/mcp-video-editor` (FFmpeg + Go), `burningion/video-editing-mcp`.

**⚠️ Verify before relying**
- "Chargebee MCP", "QuickBooks connectors", "Taskade MCP" — versions exist but quality/maintenance varies; check the actual repo before trusting.
- "claude-code-prompts", "role-specific repos for C-level / contract / HR compliance" — vague, unverified. Treat as marketing until you see the actual repo.

**🛑 Don't fork your stack**
- CrewAI / AutoGen are real, but they're *alternative orchestration frameworks*. You've already committed to Claude Code subagents + n8n. Adding them = running two agent stacks. Skip unless you deliberately migrate.

## The one distinction that matters
Your list is almost all **MCP servers = tool access**. They let an agent *do* things (push an invoice, cut a clip, drive Blender). They do **not** contain the *knowledge* of how to price a ZYNTH event or build a P&L — that's what the skills in this pack are. Wire the MCPs for hands; use these skills for brains. QuickBooks MCP + `yadana-finance` together = an agent that can both reason about margin and post the invoice.
