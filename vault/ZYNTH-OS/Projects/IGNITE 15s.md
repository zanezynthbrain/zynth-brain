<!-- TEMPLATE -->
<!-- Generated mirror — the knowledge loader skips this file on purpose. -->
---
generated: true
source: backend/data/project_ignite_15s.md
mirrored: 2026-08-06 14:20
---

> **Generated mirror of `backend/data/project_ignite_15s.md`.** Edit the source in the repo, not this
> file — the next `/mirror` overwrites whatever is here.

<!-- Worked example: one 15s commercial taken through the full ZYNTH pipeline.
     Reference for the video agents and for any future commercial project. -->

# IGNITE 15" — "The Room"

**Client:** ZYNTH (own IP) · **Deliverable:** 15s film, 9:16 + 1:1 + 16:9
**In market:** from 8 Sep 2026 · **Event:** 14 Nov 2026, Yangon
**Objective:** sponsor deck requests (primary) · seat registrations (secondary)

---

## 1. Treatment

### The idea
**"A room is worth more than a reach number."**

Every marketing person in Yangon is buying impressions. IGNITE sells the
opposite: 300 specific people in one room, and the conversations that only
happen when they are physically together. So the film never shows a crowd
cheering. It shows **the room before anyone is in it**, and fills it — one
chair at a time — with the kind of person who will be sitting there.

### Why this idea and not "an exciting summit video"
A montage of applause, confetti and stage lights is what every event promo in
the region looks like, and it says nothing a competitor could not say. The
empty room is a proposition: *we know exactly who will be here*. It is also
honest — in September we genuinely have an empty room and a list.

### Tone
Composed, deliberate, quietly expensive. No hype cuts. The energy comes from
the build, not from speed.

### Structure (the 15s spine)
| Beat | Time | Job |
|---|---|---|
| **Hook** | 0.0–1.5s | A single chair in a dark room, a name card placed on it |
| **Turn** | 1.5–6.0s | Chairs multiply; each cut is a different kind of decision-maker |
| **Proof** | 6.0–11.0s | The room is full and the light comes up — Yangon, 14 Nov |
| **Ask** | 11.0–15.0s | Date, seats, and the one line for sponsors |

### The line
**EN:** "Three hundred decisions. One room."
**MM:** "ဆုံးဖြတ်ချက် သုံးရာ။ အခန်းတစ်ခန်း။"
*(4+4 rhythm; reads in one breath — passes the breath test.)*

---

## 2. Visual script (two-column)

| PICTURE | SOUND |
|---|---|
| **0.0** Black. One banquet chair in a hard pool of light. A hand places a name card on it. Rack focus to the card. | Room tone only. The card's paper contact — close, dry. |
| **1.5** Cut wide: a second chair lights. Third. Fourth. Each cut adds chairs and pulls back. | A low sub note enters, one pulse per cut, rising in pitch. |
| **3.5** Insert: a lanyard swinging, out of focus behind it a face half-lit. | Lanyard clip tick. |
| **4.5** Insert: hands exchanging a business card across a table. | Card slide, a low murmur of voices beginning. |
| **6.0** Wide: the room now full of chairs, house lights lifting. Gold uplight finds the columns. | Voices swell to a real room murmur; sub resolves to a warm chord. |
| **9.0** Shwedagon at blue hour through a window — held, still. | Murmur drops away. One clean sustained tone. |
| **11.0** Type: **300 DECISIONS. ONE ROOM.** then **14 NOVEMBER 2026 · YANGON** | Silence under the type. |
| **13.0** Endcard: IGNITE lockup, small line "Sponsor tiers close 30 September". | Single low resonant hit on the lockup, then out. |

---

## 3. Shot list — lens, movement, intent, source

| # | Time | Shot | Lens | Movement | Source | Intent |
|---|---|---|---|---|---|---|
| 1 | 0.0–1.5 | Chair in pool of light, name card placed | 85mm | Static, rack focus to card | **FILM** | Hook. One object, one action. Shallow DOF isolates |
| 2 | 1.5–2.3 | Two chairs light | 35mm | Slow dolly back | **FILM** | Turn begins. Wide-normal keeps room honest |
| 3 | 2.3–3.1 | Six chairs | 35mm | Dolly back, faster | **FILM** | Accumulation |
| 4 | 3.1–3.5 | Twenty chairs | 24mm | Dolly back | GEN | Scale — no faces, no geography |
| 5 | 3.5–4.5 | Lanyard swings, face half-lit behind | 85mm | Handheld, slight | **FILM** | Human specificity. Compression melts background |
| 6 | 4.5–6.0 | Business card exchange, hands only | 50mm | Static | **FILM** | Proof of the actual value: the meeting |
| 7 | 6.0–9.0 | Full room, house lights lifting | 24mm | Slow crane up | GEN + film plate | The payoff. Generated only if the venue isn't available |
| 8 | 9.0–11.0 | Shwedagon at blue hour, through glass | 135mm | Locked off | **FILM** | Compression makes the pagoda loom. Real geography, non-negotiable |
| 9 | 11.0–15.0 | Type + endcard | — | — | Composited | Ask |

**Filmed : generated = 6 : 2.** Everything identifiable — the venue, the city,
the hands, the lanyard — is filmed. That is the lesson from the last teardown
applied: one invented skyline beside a real landmark makes the whole film fake.

**Shot 8 is the geography anchor.** 135mm from distance so Shwedagon compresses
and towers. A wide lens up close would shrink it — the opposite of the intent.

---

## 4. What must be filmed (half a day, one camera)

| Element | Setup | Notes |
|---|---|---|
| Chairs + name card | Ballroom or any dark room, one hard source | Book the venue for a 2-hour recce slot; shoot the empty room while you're there |
| Lanyard | Same room, 85mm, backlight through it | Print the real IGNITE lanyard first |
| Business card exchange | Table, one soft key at 45°, black flag opposite | Hands only — no casting needed |
| Shwedagon, blue hour | 135mm from a rooftop or upper floor | **20–30 minutes only.** Scout the position a day ahead |
| Room ambience | Phone recorder, 5 min | Free, and no library has real Yangon room tone |

Crew: 1 DP + 1 assistant. Gear: body + 24/35/50/85/135 (or a 24–105 + 70–200),
one hard light, one soft source, a black flag, a slider. Half a day.

---

## 5. Character policy

No hero character in this film — deliberately. Faces appear only half-lit and
out of focus (shot 5), so there is no continuity risk and no casting cost.

**If a face is added later:** generate a character sheet first (front, 3/4,
profile, neutral, one wardrobe), lock it as an identity reference on every
generation, and never change wardrobe within the film. See
`ai-hybrid-production.md`.

---

## 6. Grade plan (DaVinci Resolve node tree)

Two looks in one film, joined by a single base.

**Base (every clip, node order):**
1. **Noise reduction** — temporal, light. Generated clips need more than filmed.
2. **Balance / primaries** — set white point on the name card (paper = neutral).
   Lift shadows to a matched floor across all clips. *This node is what makes
   filmed and generated material feel like one film.*
3. **CST** — Log → Rec.709 (or Rec.709 → Rec.709 for the generated clips).
4. **Look** — see below.
5. **Final polish** — grain, halation, vignette.

**Look A — "The Room" (shots 1–7):** shadows pushed to navy (lift toward
#12203A), highlights held warm from the practical uplights. Contrast S-curve,
gentle. Saturation −5, then gold selectively boosted with a qualifier on the
uplight hue only. Ratio feels 6:1 — dramatic, not murky.

**Look B — "Blue Hour" (shot 8):** let the sky stay genuinely blue; only warm
the pagoda's gold with a HSL qualifier + power window. Do not push this shot
toward the room's warmth — the contrast between the two looks is the cut.

**Finish, all clips:** Film Grain OFX (35mm 200T, 0.35), halation on highlights
~0.15, chromatic aberration at frame edge, vignette −0.2. Rec.709 tagged.

---

## 7. Sound design — spotting sheet

| Time | Layer | Element |
|---|---|---|
| 0.0 | Ambience | Room tone alone. **No music.** |
| 0.9 | SFX | Name card contact — close, dry, no reverb |
| 1.5 | Music | Sub note enters, one pulse per cut |
| 1.5–3.5 | SFX | A soft chair-light "thump" per cut, tuned to the sub's root |
| 3.5 | SFX | Lanyard clip tick |
| 4.5 | SFX | Card slide + first voices, distant |
| 6.0 | Music + amb | Sub resolves to a warm chord; real room murmur swells |
| 9.0 | — | **Everything drops.** One sustained tone under Shwedagon |
| 11.0 | — | **Silence** under the type |
| 13.0 | SFX | Single low resonant hit on the lockup, long tail, then out |

**Principles:** silence is the most expensive sound in the film — the drop at
9.0s is what makes the ask land. Real Yangon room tone and voices, not a
library city loop. **No religious sound over Shwedagon** — ambience and tone
only.

**Mix targets:** −14 LUFS integrated · −1.5 dBTP · LRA 6–9 LU · 48 kHz.
Dialogue-free, so the sub carries the low end — high-pass everything else at
80 Hz to keep it clean on phone speakers.

---

## 8. Generation plan and cost

Only two shots are generated, and neither shows geography or faces.

| Shot | Model | Mode | Seconds | Credits |
|---|---|---|---|---|
| 4 — twenty chairs | Wan 2.7 (720p, controlled camera) | image2video | 5 | 125 |
| 7 — full room, lights lifting | Kling 3 Omni (std + sound) | image2video | 5 | 175 |
| Plates for both (stills first) | GPT Image 2 | text2image | — | 80 |
| **Total** | | | | **380 credits** |

Storyboard frames (4 × 40) add 160 if you want them for the sponsor deck.
Generate the still plate first, then animate it — cheaper and far more
controllable than text-to-video.

---

## 9. Delivery

| Cut | Aspect | Use |
|---|---|---|
| Master | 16:9 1080p, 12 Mbps | Deck, YouTube, LED at the venue |
| Social | 9:16 1080×1920 | Reels, TikTok, Stories |
| Feed | 1:1 or 4:5 | Facebook feed |

All: 48 kHz, −14 LUFS, −1.5 dBTP, Rec.709 tagged, burned-in bilingual
subtitles (Pyidaungsu/Noto, 32pt min, navy scrim at 60%).

**Pre-flight:** run the QC checklist in `ai-hybrid-production.md`. Watch it once
at phone size, in daylight, with sound off — if the ask isn't clear that way, it
isn't finished.
