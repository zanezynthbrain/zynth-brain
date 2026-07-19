# DaVinci Resolve — Deep Craft Reference

Resolve is one app with **seven pages** (bottom toolbar): Media, Cut, Edit,
Fusion, Color, Fairlight, Deliver. Give click-paths: *Page → panel → tool →
setting → value*. Studio-only features are tagged **[Studio]**.

---

## 0. Project setup (do first — avoids re-work)
- **Project Settings (Shift+9) → Master Settings:** Timeline resolution (1920×1080 or 3840×2160), frame rate (**set before importing — cannot change after clips are on the timeline**), colour science (**DaVinci YRGB Color Managed** is the easy correct default).
- **Color Management:** for log footage, set Input Color Space per clip (right-click clip → Input Color Space) or use a Color Space Transform node. Output = Rec.709 Gamma 2.4 for standard delivery.
- **Optimized Media / Proxies:** right-click clips → Generate Optimized Media for smooth editing on modest machines (important on MM/SG laptop specs). Playback → Timeline Proxy Mode.

---

## 1. Cut & Edit pages (assembly → fine cut)

**Cut page** = fast first assembly (great for social/quick turnarounds): Source Tape, Smart Insert, **Sync Bin** for multicam, Close-Up button auto-punches a CU.

**Edit page** = the real edit.
- **Core keys:** `I`/`O` in/out, `A` select, `B` blade, `T` trim, `Q` toggle source/timeline, `\` play around, spacebar play. Ripple delete = `Shift+Del`; insert = `F9`; overwrite = `F10`.
- **Trimming:** Trim tool (`T`) → drag edit points; ripple, roll, slip, slide. Dynamic Trim (`S`) with `J K L` for feel-based trimming.
- **Retime:** right-click clip → **Change Clip Speed**, or `R` for the retime bar → speed ramps via retime curve (Clip → Retime Curve). For smooth slow-mo enable **[Studio] Optical Flow** + Speed Warp (Inspector → Retime and Scaling → Motion Estimation → Speed Warp).
- **Transitions:** `Ctrl/Cmd+T` = default cross-dissolve on the edit point. Effects Library → Video Transitions for others. **Rule: cut on action; use dissolves for time passing, not to hide weak cuts.**
- **Inspector (top-right):** Transform (zoom/pan/rotate), Cropping, Dynamic Zoom (auto Ken Burns), Composite (blend modes + opacity), Stabilization (Inspector → Stabilization → Similarity/Perspective), Lens Correction, Retime, Scaling.
- **Speed Editor / keyboard** aside — the **Inspector + Effects Library** is where 90% of looks live.

**Text & titles:** Effects Library → Titles → **Text+** (Fusion title, far more powerful than plain Text). Style in Inspector; animate in the Keyframe panel or Fusion page.

---

## 2. Fusion page (motion graphics & VFX — node-based)

Fusion is a **node compositor** (like Nuke/AE-hybrid). Flow = left→right; nodes connect output→input.

**Essential nodes:**
- **MediaIn / MediaOut** — your clip in/out of Fusion.
- **Background / Rectangle / Ellipse** (masks & shapes) → feed into **Merge**.
- **Merge** — the workhorse: combines Background (orange input) + Foreground (green) + Mask; controls blend, apply mode, opacity. Chain Merges to stack layers.
- **Text+** — full title control (fonts, shading, follower for per-character animation).
- **Transform / DVE** — move/scale/rotate.
- **Tracker** — track a point/region; connect to a Text or mask to pin graphics to moving footage. **Planar Tracker [Studio]** for screen replacements/surfaces.
- **Delta Keyer** — best green-screen keyer. Feed matte into a Merge over new BG. Clean with Matte Control + erode/blur.
- **Paint** — remove blemishes/rigs.
- **Camera3D / Image Plane 3D / Renderer3D** — true 3D scenes and parallax.
- **Follower** — animate text one character at a time.

**Animate:** select a parameter → keyframe (small diamond) → move playhead → change value. Open **Spline editor** for easing (ease in/out), **Keyframes editor** for timing. Ctrl+drag to add ease.

**Common Fusion jobs:** animated lower-thirds, logo stings, screen replacement, sky/object removal, callout graphics tracked to a product, particle systems (pEmitter → pRender).

---

## 3. Color page (grading — Resolve's crown jewel)

Node-based grading. Nodes flow left→right in the **Node Editor** (top-right).

### Read the scopes first (never grade by eye alone)
- **Waveform** — luminance/exposure (blacks near 0, highlights near 1023 on 10-bit; don't clip unless intended).
- **Parade (RGB)** — white balance (align R/G/B in neutrals).
- **Vectorscope** — hue & saturation; skin-tone line (upper-left) for correct skin.
- View: bottom toolbar → scopes icon.

### Correction node order (node 1 = primary)
1. **Balance/exposure:** Lift (shadows), Gamma (mids), Gain (highlights) wheels → set black point, white point, mids. Offset wheel for overall WB.
2. **White balance:** use Temp/Tint or the White Balance picker on a neutral.
3. **Saturation & contrast:** primary palette sliders.

### Then the look (new serial node — `Alt/Opt+S`)
- **Curves:** Custom curve for contrast (gentle S-curve); Hue vs Hue / Hue vs Sat / Lum vs Sat for targeted tweaks (e.g. pull saturation out of a distracting colour).
- **Qualifier (HSL)** — isolate a colour/skin (the eyedropper), refine with the matte, then push that range only. Show the matte with the highlight button.
- **Power Windows** — shapes (circle/linear/poly/curve) to grade part of the frame (vignette, sky, face). Enable **Tracking** (window → track forward) to follow motion.
- **Color Warper** [Studio] — intuitive hue-sat grid pushing.
- **LUTs** — apply a creative LUT on its own node (drag from LUT browser), then dial back with Key output gain or node opacity. Use LUTs as a *start*, not the finish.

### Node structure discipline
- Serial nodes = sequential; **Parallel/Layer** nodes = blend multiple grades; **Outside node** = grade everything *except* a window; **Compound node** to group.
- Keep correction and look on separate nodes so you can tweak independently.
- **Clip vs Timeline node graph:** grade per-clip, then use a **Timeline-level node** (Clips menu → Timeline) for a look/LUT across the whole film.

### Skin & the "cinematic" look
- Fix skin on the vectorscope skin line; use a qualifier to protect skin while shifting the rest.
- The teal-and-orange "commercial" look = push shadows slightly cyan/teal (Lift), keep skin warm (protected), lift highlights toward amber — subtly. Overdone = amateur.
- Add subtle **film grain** (Effects → ResolveFX → Film Grain / OpenFX) and a soft vignette to sit shots together.
- See `color-grading.md` for cross-tool colour theory and looks.

### Match shots
- Right-click a clip → **Shot Match to this Clip** for an auto first pass, then refine manually on scopes. Use **stills** (right-click viewer → Grab Still) in the Gallery to compare; wipe with the still to match.

---

## 4. Fairlight page (audio — see also motion-vfx-and-sound.md)
- Mixer, clip EQ, dynamics (compressor/limiter/gate) per track.
- **[Studio] Voice Isolation** (clip/track → cleans dialogue noise — huge for run-and-gun MM shoots).
- Normalize dialogue to about **−16 to −14 LUFS** for online, **−23 LUFS** for broadcast; peaks under −1 dBTP. Fairlight → meters show LUFS.
- Add room tone under cuts; SFX and music on separate buses; automation for ducking music under VO (or use a sidechain compressor).

---

## 5. Deliver page (export)
- **Render Settings (top-left):** pick a preset (YouTube/Vimeo/H.264/H.265) or Custom.
- **Format/Codec:** H.264 or H.265 for delivery; **QuickTime + DNxHR/ProRes** for masters/archival.
- **Bitrate:** 1080p social ≈ 16–24 Mb/s; 4K ≈ 45–65 Mb/s; "Restrict to" or set quality.
- **Data levels:** Auto; **Rec.709 A** if unsure.
- Enable **subtitles** track if burned-in or as sidecar (.srt).
- Add to Render Queue → Render All. For platform sets, duplicate the job and change resolution/aspect (16:9 master → 9:16 + 1:1).

---

## 6. Fast recipes (give these as click-paths)
- **Ken Burns on a still:** Edit → select clip → Inspector → **Dynamic Zoom** (on) → set start/end frames in the viewer.
- **Smooth slow-mo:** Inspector → Retime and Scaling → Motion Estimation → **Speed Warp [Studio]**; then Change Clip Speed to 40–50%.
- **Stabilize shaky shot:** Inspector → **Stabilization** → mode Perspective → Stabilize (lower Smooth if it warps).
- **Speed ramp:** `R` → right-click retime bar → add speed point → drag; enable retime curve for smooth ramp; Speed Warp for clean slow section.
- **Punch-in "second camera":** duplicate clip on track above → Transform Zoom 1.2–1.4 → reframe. Cut between them on dialogue.
- **Text tracked to a moving product:** Fusion → Tracker → track region → connect Text+ Transform to Tracker → publish.
- **Whip-pan transition:** blur+directional motion at out-point of A and in-point of B (Effects → Directional Blur, keyframed) or use the built-in "Whip Pan" transition on the Cut page.
- **Green screen:** Fusion → MediaIn → **Delta Keyer** → Merge over new BG → refine matte (erode/blur) → light-wrap for realism.

---

## 7. Free vs Studio
Free Resolve is genuinely full-featured. **[Studio] (paid, one-time)** unlocks: Speed Warp/Optical Flow, Voice Isolation, Magic Mask, Planar Tracker, some ResolveFX, 4K+ on some GPUs faster, HDR grading, collaboration. For commercial work, Studio pays for itself fast — recommend it for ZYNTH.
