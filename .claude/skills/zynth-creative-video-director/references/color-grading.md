# Colour Grading — Cross-Tool Craft & Looks

Colour theory and look-building that applies in Resolve (best), Premiere Lumetri,
or CapCut Adjustment. Read alongside the tool file for exact click-paths.

---

## 1. Correct before you create (always this order)
1. **Set black & white points** — blacks sit near the bottom of the waveform without crushing (unless intended), highlights near the top without clipping.
2. **Neutralise white balance** — align R/G/B in the neutrals on the **Parade** scope; use a grey/white reference in frame if you have one.
3. **Balance mids** — expose skin correctly (see below).
4. **Match shots** — every shot in a scene must feel like the same moment, camera, and light. Match on scopes, not vibes.

Only when the film is *corrected and consistent* do you apply a look. A look on an unbalanced timeline amplifies the inconsistency.

---

## 2. Skin tone is the anchor
- On the **Vectorscope**, correctly exposed skin of any ethnicity falls along the **skin-tone line** (the I-line, upper-left, ~11 o'clock). Nudge until it sits on the line.
- Protect skin when styling: isolate it with an HSL qualifier / secondary, then push the *rest* of the frame. Warm, clean skin reads as "premium"; green/magenta skin reads as "amateur" instantly.
- For Myanmar/SE-Asian skin under warm tungsten or golden hour, watch for over-orange — pull a touch of saturation and warmth back so it stays natural.

---

## 3. Reading scopes (your source of truth)
- **Waveform** = luminance/exposure top-to-bottom, matches screen left-to-right.
- **RGB Parade** = each channel's levels → white balance & colour casts.
- **Vectorscope** = hue (angle) + saturation (distance) → skin line, overall palette.
- **Histogram** = distribution of tones.
Grade to the scopes; your monitor lies (uncalibrated laptop screens especially).

---

## 4. Building a look (the controls, tool-agnostic)
- **Contrast** — a gentle **S-curve** (lift highlights, drop shadows) adds "cinematic" depth. Don't crush unless the style calls for it.
- **Colour balance by tonal range** — Lift (shadows), Gamma (mids), Gain (highlights) wheels: e.g. cool the shadows, keep mids neutral, warm the highlights.
- **Hue vs Hue / Hue vs Sat curves** — retarget or tame specific colours (kill a distracting green shirt, unify skies).
- **Saturation vs Luminance** — keep shadows less saturated (realism), let mids carry colour.
- **Split toning** — teal shadows + amber highlights = the classic commercial look; keep it *subtle* (dial to ~15–30%).
- **LUTs** — use a creative LUT as a starting point on its own node/layer, then reduce intensity and fix skin. A LUT is a preset, not a grade.
- **Finish** — soft **vignette** to guide the eye, light **film grain** to bind shots and remove the "digital plastic" look, optional **halation/bloom** on highlights for warmth.

---

## 5. Named looks (recipes to reach for)
- **Clean commercial / tech** — neutral WB, slight S-curve, low-sat shadows, crisp whites, minimal split-tone. Feels premium, honest (fintech, corporate, product).
- **Warm lifestyle** — golden highlights, soft contrast, healthy warm skin, gentle bloom (F&B, hospitality, family brands).
- **Teal & orange blockbuster** — teal shadows, orange skin/highlights, strong contrast (energy, launch films) — restraint separates pro from amateur.
- **Moody premium** — low-key, rich shadows, desaturated, one accent colour (luxury, automotive, spirits).
- **Filmic/retro** — faded blacks (lift the shadow point off zero), reduced saturation, grain, slight green or warm bias (nostalgia, fashion).
- **Punchy social** — a touch more saturation and contrast so it pops on small muted phone screens (Reels/TikTok) — but not garish.

---

## 6. Delivery colour hygiene
- Standard online/broadcast output = **Rec.709, Gamma 2.4**. Keep luma within legal range for TV (0–100 IRE / broadcast-safe) if it airs.
- Don't grade on an uncalibrated screen for broadcast; for social, at least check on a phone.
- Export a **still frame** of the hero shot for the client to approve the look before you render the whole film.
- If multiple deliverables (TVC + social), grade the master, then verify the look survives the re-compression on social (bump contrast/sat slightly for the social version if needed).

---

## 7. Common mistakes to call out
- Grading before picture lock (redo work).
- Orange skin / crushed blacks / clipped highlights.
- LUT slapped on at 100% with no correction underneath.
- Inconsistent shots in one scene.
- Over-teal shadows that turn skin sickly.
- Grading by eye on a bad monitor instead of by scopes.
