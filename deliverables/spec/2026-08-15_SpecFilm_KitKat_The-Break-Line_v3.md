# THE BREAK LINE — KitKat spec commercial

**Client:** KitKat / Nestlé — **SPEC WORK, NOT COMMISSIONED**
**Produced by:** ZYNTH · zynth.asia
**Date:** 15 August 2026 · **Version:** v3 — sound pass
**Format:** 20s hero · cutdowns 15s / 6s · 16:9, 9:16, 1:1

---

## ⚠️ Status of this document — read first

This is an **unsolicited spec film**. It is a creative demonstration of ZYNTH's
product-animation capability, using a real brand as the subject the way agencies
have always made spec work.

- It is **not** official Nestlé communication and must not be published as such.
- **No Nestlé photography, footage or brand assets were used.** Every frame here
  was generated from scratch by ZYNTH.
- **No wordmark or logo was generated.** Models render type badly and the KitKat
  trademark is not ours to synthesise. The lockup is typeset by hand at the
  endframe from the official asset — which only Nestlé can supply.
- Any real use requires Nestlé's approval and a licensed brand-asset pack.

If this goes to Nestlé at all, it goes as a **capability piece**, clearly labelled.

---

## 1. The idea

**THE BREAK LINE.**

KitKat has owned "have a break" for ninety years, and every film about it
animates the same thing: the snap. The snap is the payoff, the hero, the money
shot. It is also, by now, the most predictable four frames in confectionery
advertising.

So this film does not treat the break as a payoff. It treats it as **grammar**.

**The groove between the fingers is a fault line, and every cut in the film
happens along it.** The frame splits where the bar splits. The product's own
geometry becomes the edit.

The break is not shown to you. **The break performs the edit.**

### Why this and not the obvious one

The obvious film is: busy day, stress, snap, relief, logo. It is a good structure
and it has been made a thousand times, which means it says nothing a competitor
could not say next month with a different bar.

Making the groove the transition device is ownable in a way a feeling is not.
Nobody else's product has that geometry. A rival can film a snap; they cannot
film *this* snap as a wipe, because their bar does not have four parallel
canyons running down it.

It also solves a real craft problem: product films are usually a sequence of
beautiful, disconnected macro shots held together by music. Here the shots are
held together by the product itself.

### The line

**EN:** "Break the line."
**MM:** "မျဉ်းကို ချိုးလိုက်ပါ။"

Double meaning intended in both languages — the line of the groove, and the line
you have been holding all day.

---

## 2. Art direction

| | |
|---|---|
| **Palette** | Crimson red (#D0021B ballpark) · chocolate brown · cream wafer · true black. Nothing else enters frame. |
| **Light** | Single hard key, low and raking, to carve the grooves. Deep falloff to black. One warm backlight for rim separation. |
| **Lens** | 100mm macro throughout. Anamorphic feel on the wide. f/8 for the groove work, f/4 for the cross-section. |
| **Motion** | The product never moves except when it breaks. Only the camera moves. This restraint is what makes the break land. |
| **Texture** | Cocoa grain visible. Real specular sheen, not plastic gloss. Crumbs are allowed — perfection reads as CGI. |
| **Sound** | Room tone, then the snap at full dynamic range with no music under it. Music enters *after* the break, not before. |

---

## 3. Shot list — v2, consistency pass

**All four shots are generated from a single style anchor** (the groove macro),
via image2image. That is what makes them read as one shoot rather than four
separate renders: same chocolate colour, same cocoa grain, same crimson, same
hard raking key.

| # | Shot | Movement | Purpose |
|---|---|---|---|
| 1 | **The groove** — overhead macro along the channels | Slow dolly-in down the groove | Establishes the fault line as a place |
| 2 | **The monoliths** — fingers upright, low angle, haze | Lateral drift, parallax through the channels | Scale. Makes a chocolate bar architectural |
| 3 | **The snap** — fracture, shards suspended | Ultra slow motion, halves parting | The film's centre. Everything before is setup |
| 4 | **The endframe** — whole bar, clean red field | Almost imperceptible push, highlight drifts | The ask. Negative space left for the lockup |

Shot 4 is deliberately composed with **empty red space above and below** so the
KitKat lockup and the line can be typeset into it without recomposing.

### The edit rule

Every cut is a **wipe along a groove angle** — not a dissolve, not a hard cut.
The transition travels down the same diagonal as the fault line in the outgoing
shot. Four shots, four grooves, one geometry.

At 0:11 the film does the thing it has been building to: **the snap wipes to the
next shot.** The break is the transition.

## 4. Twenty seconds

| Time | Picture | Sound |
|---|---|---|
| 0:00–0:04 | Black. The groove appears, camera pushing slowly down it. | Room tone only. |
| 0:04–0:09 | The monoliths. Camera drifts, haze moves, red rim glows. | A single low sustained note enters. |
| 0:09–0:11 | Hold. The bar sits still. The note holds. | Everything gets quieter. |
| 0:11–0:12 | **THE SNAP.** Full dynamic range, no music under it. | The snap, alone, loud. |
| 0:12–0:16 | Slow motion: halves parting, crumbs suspended, layers revealed. | Silence, then the chord resolves warm. |
| 0:16–0:18 | The cross-section. Held. Still. | Warm chord sustains. |
| 0:18–0:20 | Endframe: red field, lockup, the line. | One low resonant hit, then out. |

**The silence at 0:09 is the most expensive sound in the film.** It is what makes
the snap land. Do not let anyone fill it.

---

## 4b. The sound pass — what was wrong and what changed

### What was wrong

Every clip in v1 and v2 was generated on **Wan 2.7**. Wan 2.7 does not generate
audio at all. The files carry an audio flag, so they look like they have sound;
the track is silent. The sound design written into section 4 above was never
produced — it existed only on paper.

That was a model-selection error on our side, not a limitation of the idea. A
film whose entire structure is built around one snap and the silence before it
cannot be generated on a silent model.

### What changed in v3

Three shots were regenerated on **audio-native** models, from the same v2 anchor
frames, so the picture continuity of v2 is preserved and the sound is now real.

| # | Shot | Model | Audio | Credits |
|---|---|---|---|---|
| 1 | The groove | Kling 3 Omni (`generateSound`) | room tone + sub-bass drone | 175 |
| 2 | The monoliths | Kling 3 Omni (`generateSound`) | one held bowed note | 175 |
| 3 | **The snap** | Gemini Omni Flash (native audio) | silence → the crack → grains landing | 250 |
| — | Director test | Seedance 2.0 `element2video` from the Shot Plan | full four-beat sequence with audio | 400 |

The sound was written into each prompt as its own paragraph and — this is the
part that matters — written by **exclusion**. Left unconstrained, all of these
models reach for the same generic trailer score. Every prompt explicitly bans
music, voice, whoosh, riser, bass drop and stock impact. What is left is the
room, one note, and the snap.

### Smart Shot — the OpenArt "Director" feature

The feature is called **Smart Shot**. From a scene description plus product
reference images it produces a **Shot Plan**: one wide production-design sheet
carrying reference views, set design, a top-down camera floor plan, storyboard
frames and lighting notes — and it hands back a `videoPrompt` plus a
ready-to-submit render payload.

We ran it two ways for this film:

- **`preview-shot-plan` (60 credits)** — the sheet alone. This is the one to
  run habitually: it is cheap, it is reviewable before any money is spent on
  video, and it is the closest thing in the toolchain to a real pre-production
  document.
- **The plan's own render path** — its suggested next step was Seedance 2.0
  `element2video` with the sheet as a visual reference. We ran that at 720p with
  audio (400 credits) to see whether a planned four-beat sequence in one clip
  beats four separately anchored clips.

### The v3 assets

| Asset | Link |
|---|---|
| Shot Plan sheet (Smart Shot) | [open](https://cdn.openart.ai/openart-ai/production/2026-08/create-image/zQlwAWg6g9rSn0INEuso/gpt-image-2-responses-image_1786813667683_9e6d5043.png) |
| Shot 1 — the groove, with sound | [open](https://cdn.openart.ai/openart-ai/production/2026-08/create-video/zQlwAWg6g9rSn0INEuso/098b0146c5ffcf3d7d2c22b7632314df-6d3fac09-66dc-4727-90a2-ede2cec22240_1786813658646_c8e47dbf.mp4) |
| Shot 2 — the monoliths, with sound | [open](https://cdn.openart.ai/openart-ai/production/2026-08/create-video/zQlwAWg6g9rSn0INEuso/463072da336ac14c1c36ec8aea52d0a1-47b08dd7-9893-4d0b-ab37-cdb25df9484c_1786813892267_d0b27831.mp4) |
| Shot 3 — **the snap**, with sound | [open](https://cdn.openart.ai/openart-ai/production/2026-08/create-video/zQlwAWg6g9rSn0INEuso/video_1786813759389_ecd8b2bb_1786813759465_8a4d6736.mp4) |
| Director test — full sequence, one clip | [open](https://cdn.openart.ai/openart-ai/production/2026-08/create-video/zQlwAWg6g9rSn0INEuso/02178681399974800000000000000000000ffffc0a88538fdfb15_1786814135218_b94406a1.mp4) |

**Recommendation:** use `preview-shot-plan` on every multi-shot film from here,
as the step before generation. Use its one-clip render as a *comparison* rather
than the master — a single 5-second clip cannot hold four beats at the pace this
film needs, and shot-by-shot generation from a locked anchor frame still gives
more control over each individual frame.

---

## 5. Deliverables

| Cut | Aspect | Use |
|---|---|---|
| Hero 20s | 16:9 1080p | YouTube, cinema, in-store |
| Social 15s | 9:16 1080×1920 | Reels, TikTok, Stories |
| Feed 6s | 1:1 / 4:5 | Bumper, feed |
| Stills | 2K 16:9 | Key visuals, OOH base |

All: 48 kHz, −14 LUFS, −1.5 dBTP, Rec.709. Burmese subtitles in Pyidaungsu,
typeset — never generated inside the frame.

---

## 6. What it cost, and what is still missing

**Total spent: 2,060 OpenArt credits** across three passes.

| Pass | Work | Credits |
|---|---|---|
| v1 | 4 frames text2image + 3 clips (Wan 2.7, silent) | 435 |
| v2 | 4 frames image2image from anchor + 4 clips (Wan 2.7, silent) | 560 |
| v3 | Smart Shot plan + 2 Kling 3 Omni + 1 Gemini Omni Flash + 1 Seedance 2.0 | 1,065 |
| | **Balance: 2,795 → 735** | |

**Fixed in v2:** continuity. Every shot derives from one anchor frame, so the
chocolate, the red and the light match across the film.

**Fixed in v3:** sound. The three shots that carry the film now come out of
audio-native models with the sound design actually generated, not just written
down. Plus a Shot Plan from Smart Shot to plan against.

**Still missing — honestly:**

1. **No logo.** The endframe is composed for it but the official KitKat lockup is
   a licensed asset. It cannot be generated and should not be.
2. **Not edited.** Individual clips, not a cut film. The groove wipes, grade, the
   mix and the silence at 0:09 are an edit pass in Resolve — that is craft work,
   not generation, and it is where the film becomes a film. The generated audio
   is raw material for that mix, not a finished mix.
3. **The endframe is still silent.** Shot 4 was left on the v2 Wan 2.7 clip; its
   single low resonant hit is cheaper to place by hand in the edit than to
   regenerate at 175 credits.
4. **No Burmese typesetting.** Subtitles and the endframe line are a hand pass in
   Pyidaungsu, never generated in-frame.
5. **720p.** Fine for review and social; a broadcast master would need a 1080p
   regeneration pass.

**What it would take to finish:** the edit. No more generation is required.

---

## 7. The standing lesson

The rule that came out of this pass is now written into
`.claude/skills/zynth-creative-video-director/references/ai-hybrid-production.md`
so no future ZYNTH film repeats it:

> Decide the sound of a shot before picking its model. PixVerse V6 and Wan 2.7
> generate no audio. Any shot whose sound carries meaning goes to Kling 3 Omni,
> Seedance 2.x or Gemini Omni Flash — and the sound is written into the prompt
> by exclusion, naming what must not appear as well as what must.

---

*ZYNTH — The Intelligence of Creativity · zynth.asia*
*Spec work. Not commissioned by, affiliated with, or approved by Nestlé.*
