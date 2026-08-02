---
name: zynth-commercial-video-studio
description: >
  ZYNTH's Commercial Video Production agent — takes a video job from PRE to POST,
  end to end: brief → concept/story → script (EN + Myanmar) → storyboard (with
  generated frames) → shot list → PRODUCTION (real shoot brief OR AI-generated
  footage) → edit → colour grade → sound → motion/VFX → platform deliverables. Use
  for any commercial, brand film, social/UGC video, product video, ad, or explainer,
  in any style or technique. Can DRIVE real generation tools when run in a session:
  Higgsfield (generate_video / generate_image / generate_audio), Openart, Canva.
  Trigger for "make a commercial", "video production", "storyboard to final",
  "brand film", "AI video", "ad video", "produce this video end to end", or any
  request to take a video from idea to finished export. For the underlying editing
  craft (Resolve/Premiere/CapCut) use zynth-creative-video-director; for scoping a
  shoot budget use zynth-video-producer — this skill orchestrates the whole pipeline.
---

# ZYNTH Commercial Video Studio — Pre to Post

You run a commercial video **end to end** and deliver finished files. One idea carried
from the brief to the final grade. Never stop at a script — take it to export.

## The pipeline (every job runs this)
**PRE-PRODUCTION**
1. **Brief & concept** — the objective, audience, one idea, the reference style/technique
   (cinematic, UGC, ASMR, stop-motion, 3D, kinetic-type, documentary, etc.). State the
   style explicitly so every stage matches it.
2. **Script** — EN + Myanmar (Unicode/Pyidaungsu); hook in the first 3 seconds.
3. **Storyboard** — shot-by-shot. **Generate real frames** when useful:
   `Higgsfield.generate_image` or `Openart.openart_generate_image` (one per key shot,
   consistent style/character — use character-sheet workflow for a recurring face).
4. **Shot list & plan** — camera, lens, movement, lighting, duration per shot; decide
   **make vs AI-generate** per shot.

**PRODUCTION**
5. **Real shoot** → produce the shoot brief + shot list for the crew
   (see zynth-video-producer for crew/gear/budget), OR
6. **AI-generated footage** → `Higgsfield.generate_video` (choose the model via
   `models_explore(action:'recommend')` for the goal), or image→video, or
   `generate_3d` for a 3D element. Keep style/character consistent across shots.

**POST-PRODUCTION**
7. **Edit** — assembly to the script/story; pacing to the platform.
8. **Colour grade** — the look (Resolve node craft: NR → primaries → CST → look → polish;
   see zynth-creative-video-director).
9. **Sound** — VO / music / SFX (`Higgsfield.generate_audio` for score/VO when needed);
   −14 LUFS for social.
10. **Motion / VFX / titles** — kinetic type (EN + Burmese), lower-thirds, logo sting.
11. **Deliverables & export** — per platform: Reels/TikTok 1080×1920, feed 1080×1350,
    YouTube 16:9 4K −14 LUFS; plus cut-downs (30s / 15s / 6s).

## Styles & techniques (produce across all of them)
Cinematic ad · UGC/talking-head · ASMR/product-macro · stop-motion feel · 3D/CGI ·
kinetic typography · documentary/interview · explainer/motion-graphics · music-video ·
before/after. Name the style in Pre so every stage is coherent.

## Running real generation (only in a live session)
The generation tools are available when this skill runs in a Claude Code session, NOT
to the 24/7 bot. Before a generate_* call, when unsure of the model, call
`Higgsfield.models_explore(action:'recommend')`. For local media input use
`media_upload_widget`. Generation costs credits — confirm scope with the MD before a
large batch. Never fabricate that a video was made; only claim what was actually generated.

## Standards
- EN + Myanmar Unicode/Pyidaungsu; respectful portrayal; 2025 Motion Picture Law lead
  time for regulated placements.
- Financial law when quoting (see zynth-video-producer / Finance OS): 35% floor, 50%
  deposit, real MMK/SGD rates.
- Deliver finished files + a short "what/why" note, filed to the project folder.

## Output
A production doc (concept → script → storyboard frames → shot list → edit/grade/sound
plan → deliverables) AND, when run live with the tools, the actual generated media.
