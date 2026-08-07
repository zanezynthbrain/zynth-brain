---
name: zynth-davinci-post
description: Professional post-production automation for DaVinci Resolve (cut, color grade, audio cleanup, captions, multi-platform export) via Python API and agentic workflows.
author: Manus AI (adapted from ChaiWithJai)
version: 1.0
---

# ZYNTH DaVinci Resolve Post-Production Skill

This skill provides the ZYNTH AI agent with professional post-production capabilities using DaVinci Resolve 20. It moves the agent from conceptual video planning to executable timeline generation, audio cleanup, color grading, and multi-platform rendering.

## How to Use This Skill

When the user provides raw video footage or a cut brief, the agent should use this skill to:
1.  **Ingest & Organize**: Set up bins, timelines, and render presets.
2.  **Cut & Clean**: Remove dead air, false starts, and filler words.
3.  **Enhance Audio**: Clean podcast/interview audio (denoise, de-hum, dialogue level, music ducking).
4.  **Color Grade**: Apply broadcast-quality color correction and matching for webcam/interview footage.
5.  **Finish & Export**: Add captions, lower thirds, and export across multiple aspect ratios (YouTube 16:9, Shorts 9:16, LinkedIn square).

## Key Jobs & Modules

-   **`davinci-resolve-cut-screen-recording`**: Turn long screen recordings into tight demos.
-   **`davinci-resolve-color-grade-webcam`**: Broadcast-quality skin tones and exposure.
-   **`davinci-resolve-audio-cleanup-podcast`**: Professional dialogue leveling and music ducking.
-   **`davinci-resolve-social-editor`**: Speaker-led social edits with semantic cuts, B-roll, and captions.
-   **`davinci-resolve-export-multi-platform`**: Multi-format rendering automation via Python API.

## Python Automation & API

To drive Resolve via external scripting:
```python
import DaVinciResolveScript as dvr
scriptapp = dvr.scriptapp
resolve = scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
```
Ensure External Scripting is set to **Local** in DaVinci Resolve Preferences > System > General.
