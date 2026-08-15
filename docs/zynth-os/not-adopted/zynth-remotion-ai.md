---
name: zynth-remotion-ai
description: End-to-end programmatic video generation using React (Remotion), ElevenLabs voiceover, Ideogram 4, and LTX-2 video clips.
author: Manus AI (adapted from digitalsamba)
version: 1.0
---

# ZYNTH Remotion & AI Video Generation Skill

This skill provides the ZYNTH agent with the toolchain to write scripts, generate voiceovers, create AI visual cards and video clips, and compose programmatic videos using Remotion and Python (MoviePy).

## How to Use This Skill

When the user requests a fully generated promotional video, launch ad, or explainer short:
1.  **Scripting & Voiceover**: Generate the script and call ElevenLabs/Qwen3-TTS API for voiceover generation.
2.  **Asset Generation**: Use Ideogram 4 for branded title cards and LTX-2/Flux for video clips and background assets.
3.  **Composition (Remotion)**: Assemble scenes using React-based Remotion compositions with professional transitions (glitch, zoomBlur, lightLeak).
4.  **Rendering**: Export the final MP4 with burned-in captions and multi-platform aspect ratios.
