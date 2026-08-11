---
name: zynth-video-use
description: Drop raw footage in a folder, chat with the AI agent, get a fully edited final.mp4 back using transcript reading and visual composites.
author: Manus AI (adapted from browser-use/video-use)
version: 1.0
---

# ZYNTH Video-Use (Autonomous Video Editing) Skill

This skill enables the ZYNTH AI agent to autonomously edit raw footage by "reading" transcripts (Layer 1) and generating visual composites at decision points (Layer 2), exactly like the browser-use video-use framework.

## How to Use This Skill

When pointing the agent at a folder of raw video takes, the agent will:
1.  **Transcribe & Pack**: Generate word-level timestamps and speaker diarization into a packed transcript file (`takes_packed.md`).
2.  **Strategy Proposal**: Analyze the transcript, propose an editing strategy, and wait for user sign-off.
3.  **EDL Generation**: Generate an Edit Decision List (EDL) cutting out filler words (`um`, `uh`) and dead space.
4.  **Render & Self-Eval**: Render the output and run a self-evaluation loop on cut boundaries to check for audio pops or visual jumps before showing the final preview.

## Pipeline Architecture
```
Transcribe ──> Pack ──> LLM Reasons ──> EDL ──> Render ──> Self-Eval
                                                              │
                                                              └─ issue? fix + re-render (max 3)
```
