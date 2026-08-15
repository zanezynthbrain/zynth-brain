# AI-Hybrid Commercial Production — the discipline that makes it pass

> ZYNTH generates plates and clips, then edits them like a commercial. That is a
> legitimate production model — but it fails in specific, repeatable ways. This
> file is the list of those failures and the workflow that prevents them.
>
> Written from a real teardown: a 45s Galaxy S25 Ultra spec film, Aug 2026.

---

## The five failures that mark a film as AI-made

Fix these and most viewers stop being able to tell.

### 1. Character drift
The same character has a slightly different face across shots. This is the
loudest tell — the human eye is specialised for faces and catches a 5% change
instantly, even when the viewer can't name what's wrong.

**Fix — lock the character before you generate a single scene:**
1. Generate a **character sheet** first (front, 3/4, profile; neutral
   expression; consistent wardrobe). One image, one seed, one identity.
2. Use that sheet as an **element / identity reference** on every subsequent
   generation (`element2video`, not `image2video`, when the scene changes).
3. Keep wardrobe *identical* across a sequence unless a time-jump is part of
   the story. A jacket change reads as a different person when the face is
   already 95% similar.
4. If two shots still disagree, they cannot be adjacent in the cut. Separate
   them with a cutaway (product, hands, environment).

### 2. Product infidelity
The hero product is invented, or changes between shots — a different button
layout, a wrong camera array, a stylus that doesn't exist on that model.

**In client work this is fatal.** A brand team checks the product first and
stops watching after the first error.

**Fix:**
- The product is **never** generated from a text prompt alone. Supply real
  product photography as a reference image, or composite the real product in.
- Product close-ups are the shots to **actually film** — a phone on a turntable
  with one soft source is an hour of work and removes the whole risk class.
- QC pass: freeze on every frame the product appears. Same device, same colour,
  same button positions, same camera array? If not, it does not ship.

### 3. Gibberish text
Any writing inside a generated frame — UI labels, signage, packaging — comes out
as pseudo-glyphs. Burmese breaks completely.

**Fix:**
- Prompt **against** text: "no text, no logos, no readable UI."
- Every screen the audience should read is **composited in post** — build the
  UI as a graphic in Fusion/After Effects and screen-replace with a corner-pin.
- Signage in the background: keep it out of focus, or replace it.
- Burmese is always typeset (Pyidaungsu / Noto Sans Myanmar), never generated.

### 4. Geography that lies
A "Yangon" skyline with supertall towers that Yangon does not have. Local
viewers spot it in under a second, and it costs you the local-authority
positioning that is your whole differentiator.

**Fix:**
- Name the *real* place in the prompt with its actual characteristics: Yangon =
  low-rise, colonial grid downtown, Shwedagon dominant on the skyline, no
  supertalls.
- Better: use **real establishing footage** (drone or stock of the actual city)
  and generate only the shots where geography is not identifiable.
- Rule: **one real landmark + one invented skyline = the whole film reads
  fake.** Consistency matters more than either shot alone.

### 5. The plastic look
Too clean. No grain, no motion blur, no lens artefacts, perfect symmetry of
light.

**Fix in the grade (see color-grading.md), applied to every clip:**
- Add **grain** (Resolve: Film Grain OFX, 35mm 200T, ~0.3–0.5 strength).
- Add **motion blur** where movement is unnaturally crisp.
- Add a subtle **halation** on highlights and a touch of **chromatic
  aberration** at the frame edge.
- **Vignette** — barely visible, but it tells the eye there is a lens.
- Slight **highlight rolloff** instead of clipping to white.

---

## The AI-hybrid workflow (concept → delivery)

**Pre-production is where the film is won — the same as any shoot.**

1. **Treatment** (1 page) — the idea, the feeling, the structure. Before any
   generation. See `concept-and-storyboard.md`.
2. **Shot list with intent** — for every shot: framing, lens, movement,
   duration, and *what job it does*. A shot with no job gets cut later anyway;
   cut it now and save the credits.
3. **Character sheet + product reference** — locked, before scene one.
4. **Plate generation, shot by shot**, against the shot list. Generate the
   *background/scene* — never the text, never the logo.
5. **Selects** — generate 2–3 variants of the hero shots only. Volume shots get
   one attempt; if it fails twice, change the shot, not the seed.
6. **Assembly cut** — story order, no effects, no music. Does it work silent
   and ugly? If not, no amount of grade or sound will save it.
7. **Fine cut to picture-lock** — pacing, rhythm, the hook inside 1.5s.
8. **Grade** — normalise every clip to a common look first (this is what makes
   ten generations feel like one film), then build the look.
9. **Sound design + mix** — see `motion-vfx-and-sound.md` and the loudness
   targets below.
10. **QC + delivery** — the checklist at the bottom of this file.

---

## Budgeting generated video honestly

Cost = duration ÷ 5s × the model's per-clip rate. State it before generating.

| Tier | Model | Audio | ~Credits / 5s |
|---|---|---|---|
| Volume B-roll | PixVerse V6 (540p) | **none** | 50 |
| Controlled camera | Wan 2.7 (720p) | **none** | 125 |
| Sound included | Kling 3 Omni (std) | generated | 175 |
| Sound included, cheap | Seedance 2.0 Mini (720p) | generated | 200 |
| Best synchronised SFX | Gemini Omni Flash | generated | 250 |
| Hero, realism + lip-sync | Seedance 2.0 (720p) | generated | 400 |
| Shot planning only | Smart Shot `preview-shot-plan` | n/a | 60 |

A 45s film at hero quality is ~9 clips × 400 = **3,600 credits**. That is why
the tiering matters: hero the two shots that carry the idea, run everything else
at volume rate.

### The audio rule — read before choosing a model

**PixVerse V6 and Wan 2.7 generate NO audio.** Their files may still carry an
audio track flag; the track is silent. If a shot's sound is part of the idea —
a snap, an impact, a whisper, a beat drop, anything the viewer is supposed to
*hear* — those two models are the wrong choice no matter how good the picture
is, and a review will come back saying the sound is unsatisfying.

Rules:

1. Decide the sound of a shot **before** picking its model, not after.
2. Any shot whose sound carries meaning goes to an audio-native model:
   Kling 3 Omni (`generateSound: true`), Seedance 2.0 / 2.0 Mini / 2.5
   (`generateAudio: true`), or Gemini Omni Flash (audio is always native).
3. Silent-model clips are only acceptable for shots that will be scored and
   sound-designed by hand in post — say so explicitly in the brief.
4. Write the sound into the prompt as its own paragraph, and write it by
   **exclusion**: name what must NOT appear (no music, no voice, no whoosh, no
   riser, no stock impact) as well as what must. Left unconstrained, every one
   of these models reaches for generic trailer score.

### Smart Shot — the "Director" feature

Smart Shot turns a scene description plus product/character references into a
**Shot Plan**: one wide production-design sheet with reference views, set
design, a top-down camera floor plan, storyboard frames and lighting notes. It
returns a `videoPrompt` and a ready-to-submit `nextStep` payload.

- `preview-shot-plan` (60) — the plan alone. Cheap. Run this before committing
  budget to a sequence, and put the sheet in front of the founder.
- `generate-shot-video` (235) — plan and render in one call.

Use it when a film has to hold together across several shots. It does not
replace the anchor-frame discipline above; it replaces the guessing about
staging that happens before the anchor frame exists.

---

## Delivery specs — where amateur is visible in the file itself

| Spec | Amateur | Commercial |
|---|---|---|
| Resolution | 720p | 1080p minimum; 4K for brand film / archive |
| Video bitrate | 2–3 Mbps | 10–12 Mbps (1080p24 H.264), 40+ (4K) |
| Audio sample rate | 44.1 kHz | **48 kHz** — the video standard |
| Integrated loudness | −8 to −11 LUFS ("loud") | **−14 LUFS** for social/YouTube |
| True peak | 0 or above (clipping) | **−1.5 dBTP** for lossy platforms |
| Colour | Untagged | Rec.709, tagged |

Platforms normalise loudness *down* to about −14 LUFS. Delivering at −11 does
not make you louder — it makes the platform attenuate you, and your mix ends up
sounding flatter than a properly mastered one at the same perceived volume.

---

## Pre-flight QC checklist

- [ ] Hook lands inside **1.5 seconds** — a visual event, not a logo
- [ ] Same face, same wardrobe, every shot (freeze and compare)
- [ ] Product identical in every appearance, and always in the sharp plane
- [ ] No readable generated text anywhere; all UI composited
- [ ] Geography consistent — no invented skyline beside a real landmark
- [ ] Grain, motion blur and highlight rolloff applied across all clips
- [ ] One grade across the film: skin tones match shot to shot
- [ ] Subtitles burned in, both languages, sound-off legible
- [ ] Endcard **2–3 seconds**, not six
- [ ] −14 LUFS integrated, −1.5 dBTP, 48 kHz
- [ ] 1080p+, 10 Mbps+, Rec.709 tagged
- [ ] Watched once at phone size, in daylight, with sound off

---

## The legal line on spec work

A film using a real brand's name, product or trade dress — Samsung, Galaxy,
anyone — is **spec work**. It may be shown as a portfolio piece clearly labelled
"spec / concept, not affiliated with or commissioned by [brand]". It must not be
published as if it were the brand's campaign, must not run as paid media, and
must never be presented to a client as work ZYNTH was hired to make. When in
doubt, rebrand the film to a fictional product and the problem disappears while
the craft still shows.
