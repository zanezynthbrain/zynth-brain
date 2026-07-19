# Motion Graphics, VFX & Sound Design

The "wow" and the "half the picture" layers. Principles are tool-agnostic;
execute in After Effects / Fusion (heavy), or Premiere/Resolve/CapCut (light).

---

## PART A — Motion graphics & animation

### The 12-principle shortlist that makes motion feel pro
- **Easing** — nothing in life moves linearly. Always ease in/out (Bezier / F9 Easy Ease in AE; spline editor in Fusion; graph in Premiere). Linear keyframes = amateur.
- **Anticipation & follow-through** — a tiny pull-back before a move, and overshoot/settle after. Text that snaps in and slightly overshoots feels alive.
- **Offset & stagger** — animate elements a few frames apart, not all at once (letters, list items, logo parts).
- **Squash & stretch** — subtle scale on impacts for energy.
- **Motion blur** — turn it ON for fast moves; without it, motion looks stroboscopic and cheap.
- **Weight & spacing** — heavier things accelerate slower; spacing between frames = velocity.

### The velocity graph is where quality lives
Shape the **speed graph** (AE Graph Editor / Fusion spline / Premiere velocity): steep = fast, flat = slow. A smooth ease curve on position + scale is the difference between "template" and "designed."

### Common commercial motion jobs
- **Kinetic typography** — words hit on the beat/VO; use offset per word, mask reveals, and a consistent type system.
- **Logo sting** — build/reveal in 1–2s; animate the logo's own geometry, add a light sweep, land with a settle + SFX.
- **Lower thirds / callouts** — pin to subject (track it); animate a bar with a text reveal; keep on screen long enough to read twice.
- **Product callouts** — track a point on the moving product (Fusion Tracker / Mocha AE) and pin the label so it sticks.
- **Data/number count-ups** — expressions in AE (`Math.round(effect...)`) or CapCut keyframed text swaps.
- **Transitions with graphics** — shape wipes, liquid/blob transitions, light leaks — motivated by the cut, not decoration.

### Tool routing
- Simple slides/lower-thirds/count-ups → Premiere Essential Graphics or Resolve Text+ / CapCut text animations.
- Anything tracked, 3D, particle, or "hero" → **After Effects** (Dynamic Link) or **Fusion**.

---

## PART B — VFX (invisible more than explosions, at commercial level)

Most commercial VFX is **clean-up and enhancement**, not spectacle:
- **Object / rig / logo removal** — AE Content-Aware Fill, Fusion Paint, Resolve Magic Mask + Patch Replacer. Remove a stray sign, a boom, a competitor brand.
- **Screen replacement** — Mocha AE planar track / Fusion Planar Tracker → insert clean UI on a phone/laptop screen (essential for app/fintech ads like WavePay).
- **Sky replacement / set extension** — mask + track + comp.
- **Green screen keying** — AE Keylight/Ultra Key, Fusion Delta Keyer, CapCut Chroma key. Light the screen evenly on set; add a **light wrap** so the subject sits in the new environment; match grain and grade.
- **Beauty / retouch** — subtle skin smoothing (Resolve Magic Mask + soft blur mix; never plastic).
- **Compositing discipline** — match **grain, grade, motion blur, black levels, and light direction** between plate and element, or the eye clocks the fake instantly.
- **Set-extension / particles** — AE (Particular) or Fusion (pEmitter) for embers, dust, snow, bokeh; keep it atmospheric, not gamey.

**Rule:** the best VFX is the one nobody notices. Integrate, don't announce (unless the idea is the spectacle).

---

## PART C — Sound design (a cut isn't done until it's designed)

Sound is ~50% of perceived quality. A mediocre picture with great sound beats the reverse.

### Layers of a soundtrack
1. **Dialogue / VO** — clean, clear, front. Clean it: noise reduction, de-reverb, de-hum, EQ (roll off <80Hz rumble, gentle presence lift ~3–5kHz), de-ess. Compress for consistency.
2. **Music** — sets tempo & emotion. Edit music to the picture (or picture to music). Duck it under VO (sidechain/auto-duck ~ −6 to −12 dB under dialogue).
3. **SFX** — sells reality and impact: whooshes on fast moves, impacts on cuts/logo, UI ticks, foley (footsteps, cloth, product clicks). A product "click" or "tap" on a fintech app makes it feel premium.
4. **Ambience / room tone** — a bed under everything so cuts don't "drop to silence." Always lay room tone under dialogue gaps.

### Mixing targets (loudness)
- **Online (YouTube/IG/TikTok):** integrated **−14 LUFS** (−16 to −13 acceptable); true peak **< −1 dBTP**.
- **Broadcast TV:** **−23 LUFS** (EBU R128) / −24 LKFS (ATSC); peaks < −1 dBTP.
- Check the loudness meter (Fairlight/Essential Sound/Audition). Don't just make it "loud" — platforms normalise; a hyper-limited mix gets turned down and sounds squashed.

### Practical mix order
Clean dialogue → set dialogue level as the anchor → sit music under it (duck) → place SFX for impact → add ambience bed → bus compression/limiter on the master → final loudness check → −1 dBTP ceiling.

### Music licensing (say this for client work)
Use **licensed / royalty-free** music (Artlist, Epidemic, Musicbed, licensed local composers). TikTok/CapCut trending tracks are **not** cleared for brand ads — using them exposes the client. For MM market, consider commissioning a local track for ownable sonic branding.

### Tools
- **Resolve Fairlight** (built-in, Voice Isolation [Studio] is excellent), **Premiere Essential Sound + Audition**, **CapCut** (basic — fine for social, not for a mix-critical TVC). For a real commercial mix, finish audio in Fairlight/Audition, not CapCut.

---

## Quick "make it feel expensive" checklist
- [ ] Easing on every animation; motion blur on fast moves.
- [ ] Graphics tracked to motion, on screen long enough to read.
- [ ] VFX integrated (grain/grade/light matched).
- [ ] Room tone under everything; no silent drops.
- [ ] Music ducked under VO; SFX on impacts; product sounds present.
- [ ] Mixed to −14 LUFS (online), peaks < −1 dBTP.
- [ ] Licensed music for client work.
