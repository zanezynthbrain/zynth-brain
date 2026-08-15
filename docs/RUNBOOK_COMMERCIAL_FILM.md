# Runbook — producing a commercial film at ZYNTH

**Updated:** 15 August 2026
**Owner:** MD approval gates every step marked 🔒

This is the corrected path, written after THE BREAK LINE v1→v3. It exists so no
future film repeats the two mistakes that film made: shots generated without a
common anchor, and a sound-led idea generated on a model that produces no sound.

Read `.claude/skills/zynth-creative-video-director/references/ai-hybrid-production.md`
for the craft detail. This page is the order of operations and the money.

---

## The six steps

| # | Step | Cost | Gate |
|---|---|---|---|
| 1 | Write the idea and the **sound** in the same breath | free | 🔒 MD approves the idea |
| 2 | **Smart Shot** `preview-shot-plan` — the production-design sheet | 60 | 🔒 MD approves the staging |
| 3 | **One anchor frame** — the single style reference | 15–40 | 🔒 MD approves the look |
| 4 | Remaining frames by **image2image from the anchor** | 15–40 each | — |
| 5 | Animate on an **audio-native model** | 175–400 per 5s | 🔒 MD approves the spend |
| 6 | Edit, grade, mix, typeset | free (craft) | 🔒 MD approves release |

A three-shot film with real sound costs roughly **600 credits**. A ten-shot
hero-quality film costs roughly **4,000**. Say the number before generating.

---

## Step 1 — the idea and the sound are one decision

Write the sound design *before* choosing any model. If the idea depends on
something being heard — a snap, an impact, a whisper, a silence — that decides
the model in step 5, and the wrong choice there cannot be fixed in the edit.

State in one sentence: what the viewer hears at the moment the idea lands.

## Step 2 — Smart Shot (OpenArt's "Director")

`preview-shot-plan`, quality `medium`, 60 credits. Feed it the scene description
plus up to three product reference images. It returns one wide sheet: reference
views, set design, top-down camera floor plan, storyboard frames, lighting notes
— plus a `videoPrompt` and a ready-to-submit render payload.

**Always run this before spending on video.** It is the cheapest reviewable
pre-production document we have, and it is what the MD signs off on.

Do not use its one-call `generate-shot-video` as the master. A single 5-second
clip cannot hold a multi-beat film at the pace a commercial needs. Use it as a
comparison if useful; generate shot by shot for control.

## Step 3–4 — one anchor, everything else derived

Generate **one** frame first and treat it as the shoot. Every other frame is
`image2image` **from that frame**, with the prompt opening: *"Using the reference
image as the exact style, lighting and texture anchor: the SAME subject, same
grain, same colour, same key light…"*

This is the difference between four renders and one shoot. Skipping it is what
made v1 look like four unrelated pictures.

## Step 5 — the audio rule

| Model | Audio | ~Credits / 5s | Use for |
|---|---|---|---|
| PixVerse V6 (540p) | **none** | 50 | volume B-roll only |
| Wan 2.7 (720p) | **none** | 125 | shots scored by hand in post |
| Kling 3 Omni (std) | generated | 175 | the workhorse — sound at the lowest price |
| Seedance 2.0 Mini (720p) | generated | 200 | cheap sound with better realism |
| Gemini Omni Flash | generated | 250 | the hero SFX shot |
| Seedance 2.0 (720p) | generated | 400 | realism + lip-sync |

**PixVerse V6 and Wan 2.7 generate no audio.** Their files still carry an audio
flag; the track is silent.

Write the sound into the prompt as **its own paragraph, by exclusion** — name
what must NOT appear as well as what must:

> NO music, NO score, NO voice, NO narration, NO whoosh, NO riser, NO bass drop,
> NO stock cinematic impact.

Unconstrained, every one of these models reaches for generic trailer score. This
single habit is the largest quality difference available for free.

Submit video jobs **one at a time** — parallel submissions fail with
`PARALLEL_LIMIT_EXCEEDED`.

## Step 6 — what generation never does

- **No logo.** Licensed lockups are typeset by hand from the official asset.
- **No Burmese in-frame.** Burmese is written first, then typeset in Pyidaungsu.
  It is never generated inside an image or video model.
- **No mix.** Generated audio is raw material. The mix is craft work in Resolve.
- Delivery: 48 kHz, −14 LUFS, −1.5 dBTP, Rec.709, 1080p minimum for a master.

---

## Spec work

A film made for a brand that has not commissioned it is **spec**. It must be
labelled as such in its own document, must use no brand assets, must not
generate the wordmark, and does not go to the brand except as a clearly
labelled capability piece. See
`deliverables/spec/2026-08-15_SpecFilm_KitKat_The-Break-Line_v3.md`.

Prefer subjects ZYNTH can actually publish. A beautiful film that can never be
released is worth less than a plain one that can.

---

*ZYNTH — The Intelligence of Creativity · zynth.asia*
