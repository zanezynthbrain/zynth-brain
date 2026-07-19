# Adobe Premiere Pro — Deep Craft Reference

Premiere is the editorial hub of the Adobe ecosystem; heavy motion/VFX hands off
to **After Effects (AE)** via Dynamic Link. Give click-paths: *Panel → menu →
tool → setting → value*. Assume a recent CC version (2024/2025).

---

## 0. Project & sequence setup
- **New Sequence** matched to footage: drag a clip onto "New Item" or File → New → Sequence → pick a preset (or Match Source on first drop). Frame rate/resolution set here.
- **Preferences → Media Cache** on a fast drive; **Ingest/Proxies** (Project Settings → Ingest → Create Proxies, ProRes/H.264) for smooth cutting on laptops.
- Workspaces (top): **Editing**, **Color**, **Effects**, **Audio** — switch per task.

---

## 1. Editing core
- **Panels:** Project (bins), Source & Program monitors, Timeline, Effect Controls, Effects, Lumetri Color, Essential Graphics, Essential Sound.
- **Key tools/keys:** `V` selection, `A` track select forward, `B` ripple, `N` rolling, `C` razor, `Y` slip, `U` slide, `Q` ripple-trim to playhead (back), `W` (forward). `I`/`O` marks, `,` insert, `.` overwrite, `Shift+Del` ripple delete.
- **Three/four-point editing** from Source monitor; drag to timeline or use insert/overwrite.
- **Trim:** double-click an edit point for Trim mode; ripple vs roll; `Shift+←/→` nudge 5 frames.
- **Speed:** right-click → **Speed/Duration** (check "Ripple edit" and "Maintain audio pitch"); or **Rate Stretch** tool (`R`). Time remapping: clip → right-click fx badge → Time Remapping → Speed → keyframe in the timeline, drag to ramp, split keyframes for ease.
- **Optical Flow** for slow-mo: Speed/Duration → Time Interpolation → **Optical Flow**, then render (quality varies — Resolve's Speed Warp is better; for hero slow-mo consider shooting high-fps).
- **Multicam:** select clips → Create Multi-Camera Source Sequence (sync by audio/TC) → enable multicam in Program → cut live with number keys.

---

## 2. Effects & Effect Controls
- **Effects panel** → drag onto clip → adjust in **Effect Controls** (top-left). Every clip has intrinsic **Motion** (Position, Scale, Rotation, Anchor Point), **Opacity** (+ blend modes + mask), **Time Remapping**.
- **Keyframing:** click the stopwatch on a property → move playhead → change value. Right-click keyframe → **Ease In/Ease Out** (Bezier); open the graph (expand property) to shape velocity.
- **Masks:** in Effect Controls under an effect or Opacity → draw ellipse/pen mask → **Track** (play-forward) to follow motion; feather the edge.
- **Workhorse effects:** Gaussian/Directional Blur, Transform (has its own motion blur + lets you keyframe pre-composite), Warp Stabilizer (Effects → Distort → **Warp Stabilizer** — set Smoothness; "Subspace Warp" default, switch to "Position/Scale/Rotation" if it distorts), Ultra Key (chroma key — see below), Lumetri (colour), Ultra/DeNoise, Lens Distortion, Mosaic (censor), VR effects.
- **Green screen (Ultra Key):** Effects → Keying → **Ultra Key** → eyedropper the green → Setting: Aggressive → refine Matte Generation (Transparency/Highlight/Shadow) → Matte Cleanup (Choke/Soften) → check with Output = Alpha Channel.
- **Adjustment layer** (Project → New Item → Adjustment Layer) → put on top track → effects apply to everything below (grades, blurs, LUTs across the whole cut).

---

## 3. Titles & motion graphics — Essential Graphics (MOGRTs)
- **Window → Essential Graphics.** Browse tab = templates (incl. AE-made .mogrt); Edit tab = create.
- **Type tool (`T`)** on the Program monitor → text becomes a graphic layer; style in Essential Graphics (font, stroke, shadow, background, align). Responsive Design → **Pin** text to a background so a bar auto-sizes.
- **Animate** via Effect Controls (Transform on the graphic) or use a pre-animated MOGRT.
- For anything beyond simple slides/lower-thirds, **build it in After Effects** and either export a MOGRT (Essential Graphics → Export) or Dynamic Link the comp.

---

## 4. After Effects handoff (when Premiere isn't enough)
- **Dynamic Link:** right-click clip → **Replace With After Effects Composition** → animate in AE → it updates live in Premiere (no render/export step). Use for: complex title sequences, tracked callouts, screen replacements, logo builds, particle/VFX.
- AE essentials to know: comps & layers, keyframes + Graph Editor (F9 = Easy Ease), Anchor Point discipline, **parenting**, **masks & shape layers**, **track mattes** (alpha/luma), **3D layers + camera**, **Roto Brush** (masking moving subjects), **Mocha AE** planar tracking (screen inserts), **Motion Blur** toggle, expressions (e.g. `wiggle(2,20)` for organic motion, `loopOut()` for cycles).
- **Puppet tool** for character/prop animation; **Content-Aware Fill** for object removal.
- Recommend AE for the "wow" graphic moments; keep the cut and grade in Premiere.

---

## 5. Colour — Lumetri
- **Window → Lumetri Color** + **Lumetri Scopes** (Waveform/Parade/Vectorscope).
- Sections in order: **Basic Correction** (White Balance, Tone: exposure/contrast/highlights/shadows/whites/blacks; Input LUT for log footage) → **Creative** (Look/LUT + intensity, faded film, vibrance) → **Curves** (RGB + Hue/Sat curves — Hue vs Sat to tame a colour) → **Color Wheels** (Shadows/Mids/Highlights) → **HSL Secondary** (isolate a colour/skin, then push) → **Vignette**.
- Put a Lumetri on an **Adjustment Layer** for a whole-timeline grade; per-clip Lumetri for shot matching. **Comparison View** (Program monitor) to match shots side by side.
- Correct first (neutral, scopes), then style. See `color-grading.md`.

---

## 6. Audio — Essential Sound
- **Window → Essential Sound.** Assign each clip a type: **Dialogue / Music / SFX / Ambience**.
- Dialogue: **Loudness → Auto-Match**, **Repair** (Reduce Noise, DeReverb, DeHum), **Clarity** (dynamics, EQ presets). Music: **Duck** against dialogue (auto sidechain). 
- Target **−16 to −14 LUFS** online, peaks < −1 dBTP. See sound reference.

---

## 7. Export (Media Encoder / File → Export)
- **Export panel (Ctrl/Cmd+M):** Format **H.264** (delivery) or **H.265**; Preset "Match Source – High bitrate" or a platform preset (YouTube 1080p/4K).
- **Bitrate (VBR 2-pass):** 1080p ≈ 16–24 Mb/s; 4K ≈ 45–65 Mb/s.
- Master/archival: **QuickTime → ProRes 422 HQ**.
- **Captions:** Window → Text → Captions → Create; export burned-in or as sidecar .srt.
- Queue to **Media Encoder** to keep editing while it renders; duplicate the job for 9:16 / 1:1 versions (change sequence or use Auto Reframe — Effects → **Auto Reframe** / sequence → Auto Reframe Sequence for AI reframing to vertical).

---

## 8. Fast recipes (click-paths)
- **Punch-in second angle:** duplicate clip to track above → Effect Controls → Scale 120–140 → reposition. Cut on dialogue.
- **Speed ramp:** Time Remapping → add keyframes → drag between them → split a keyframe and pull the handles for smooth ramp.
- **Vertical from horizontal:** select sequence → **Auto Reframe Sequence** (9:16) → tweak the AI tracking keyframes.
- **Text tracked to motion:** mask/track in AE via Dynamic Link, or Mocha AE, then it flows back.
- **Whip pan:** Directional Blur keyframed up at A's out and down at B's in; align a fast pan in each clip.
- **Clean noisy dialogue:** Essential Sound → Dialogue → Repair → Reduce Noise; heavier cases → **Audition** (Edit in Audition) → Noise Reduction (process).
- **LUT across whole film:** Adjustment Layer on top → Lumetri → Creative → Input/Look LUT.

Premiere strengths: editorial speed, team workflows, tight Adobe integration. For grading depth Resolve wins; for motion/VFX depth AE wins — know when to hand off.
