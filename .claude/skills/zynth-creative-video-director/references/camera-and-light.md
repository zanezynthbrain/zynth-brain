# Camera & Light — the fundamentals nobody taught you

> For the ZYNTH director who came up through editing and AI, not through a
> camera department. This is what a DP knows in their hands. Learn it and you
> can brief a shoot, judge a frame, and write prompts that look photographed
> instead of rendered.

---

## 1. The exposure triangle — three ways to control one thing

Light hits the sensor. Three controls decide how much:

| Control | What it does | What it COSTS you |
|---|---|---|
| **Aperture** (f/1.4 → f/22) | How wide the lens opens | Depth of field. f/1.4 = creamy blur, f/8 = everything sharp |
| **Shutter** (1/50, 1/100…) | How long each frame is exposed | Motion blur. Long = smeary, short = stuttery |
| **ISO** (100 → 12800) | Sensor amplification | Noise. High ISO = grain, muddy shadows, weak colour |

**In video you do not get to choose freely.** Shutter is locked by the 180°
rule (below), so you expose with aperture, ISO and ND filters. That's why every
serious shoot carries NDs — they are sunglasses for the lens, letting you keep
f/2.8 in daylight without breaking shutter.

**Lower f-number = more light + more blur.** The number is a fraction; f/1.4 is
a *bigger* opening than f/8. That trips up everyone at the start.

---

## 2. The 180° shutter rule — why footage looks like film or like video

**Shutter speed = 1 ÷ (frame rate × 2).**

- 24fps → 1/48 (use 1/50)
- 25fps → 1/50
- 30fps → 1/60
- 60fps → 1/120

This gives the motion blur the eye reads as "cinema." Break it deliberately,
never accidentally:

- **Faster shutter (1/500)** — crisp, stuttery, harsh. Saving Private Ryan
  combat, sports, impact moments.
- **Slower shutter (1/25 at 24fps)** — dreamy smear. Nightclub, memory,
  intoxication.

**Your video is 24fps.** Anything generated for it should carry ~1/48 motion
blur. AI clips often render *too clean* — no blur at all — which is one reason
they read as fake. Adding a touch of motion blur in post fixes more than people
expect.

---

## 3. Focal length — the most under-used storytelling tool

Focal length is not "zoom." It changes the *relationship between the subject
and the world behind them*.

| Lens | Field | What it says |
|---|---|---|
| **14–24mm** ultra-wide | Huge | Overwhelm, space, isolation. Distorts faces — never a beauty lens |
| **35mm** | Wide-normal | "You are there." Documentary, environment + subject together |
| **50mm** | Normal | Neutral, honest. Closest to human perception |
| **85mm** | Short tele | Flattering portraits. Background melts. Intimacy |
| **135mm+** | Long tele | Compression. Background looms close. Surveillance, longing, isolation-in-a-crowd |

**Compression is the trick most people miss.** Shoot a person at 24mm and the
pagoda behind them is a distant speck. Walk back and shoot the same framing at
135mm and the pagoda towers over their shoulder. Same subject size, completely
different meaning. **If you want Shwedagon to feel monumental behind a person,
that is a long lens from far away — not a wide lens up close.**

For prompts: say *"shot on 85mm, compressed background"* rather than
*"zoomed in."*

---

## 4. Depth of field — where the audience is allowed to look

Shallow DOF (f/1.4–f/2.8) isolates. Deep DOF (f/8–f/16) includes.

Controlled by: aperture · focal length (longer = shallower) · distance to
subject (closer = shallower) · sensor size (bigger = shallower).

**Commercial rule:** the product is *always* in the sharp plane. If the phone is
soft and the face is sharp, you have shot a portrait, not a product ad.

**Rack focus** — pulling focus from one plane to another mid-shot — is the
cheapest way to make a shot feel directed. Use it to move attention from the
face to the product at the exact moment the VO names the product.

---

## 5. Light — the actual craft

Cameras record light. Everything else is bookkeeping.

### The three questions for any lit frame
1. **Where is the key coming from?** (the dominant light)
2. **How hard is it?** Hard = small source, sharp shadows (sun, bare bulb).
   Soft = large source relative to subject, gradual shadows (overcast, bounce,
   big diffusion).
3. **What is the ratio?** How much darker is the shadow side than the key side?
   2:1 = gentle, commercial. 8:1 = drama, moody, "premium tech."

### Positions that mean something
- **Key at 45°/45°** (side and above) — classic, dimensional, safe.
- **Backlight / rim** — separates subject from background. This single light is
  what makes a frame look "produced." If a frame feels flat, it usually lacks
  rim.
- **Frontal, on-axis** — flat, honest, beauty/fashion, or interrogation.
- **Underlight** — unnatural, threatening. Almost never in commercial work.
- **Practicals in frame** (neon signs, lamps, phone screen) — motivate your
  light. The audience believes light they can see a source for.

### Golden and blue hour
- **Golden hour** (first/last hour of sun): low, warm, long shadows, kind to
  faces. Your opening hill shot is golden hour and it is the best-looking
  material in the film.
- **Blue hour** (20–30 min after sunset): sky still holds deep blue, city
  lights are already on. **This is the single most valuable window for city
  work** — it is why your night city shots look expensive. Pure black sky
  looks cheaper.

### Colour temperature
Measured in Kelvin. Daylight ≈ 5600K (blue). Tungsten ≈ 3200K (orange).
Mixing them *deliberately* — warm practicals against a cool ambient — is the
foundation of the "night city" look. Mixing them *accidentally* is why amateur
footage has green faces under fluorescents.

---

## 6. Composition — where to put things

- **Rule of thirds** — subject on a third-line, not dead centre. Break it for
  formality and confrontation (Wes Anderson centring is a statement).
- **Headroom** — a little above the head. Too much makes the subject sink.
- **Lead room / nose room** — leave space in the direction the subject looks
  or moves. Without it the frame feels claustrophobic and wrong, and the viewer
  can't say why.
- **Foreground** — shooting through something (leaves, a doorway, a crowd)
  creates depth instantly. AI images rarely do this; adding it to a prompt is
  the fastest way to make a generated frame feel shot.
- **Leading lines** — roads, railings, market awnings pull the eye to the
  subject.
- **Negative space** — where your type will live. Compose for it *before* the
  edit, not after.

---

## 7. Camera movement — every move needs a reason

| Move | Reason to use it |
|---|---|
| **Static (locked off)** | Confidence. Lets performance or product carry the frame |
| **Pan / tilt** | Reveal, follow, connect two things in one breath |
| **Dolly in** | Realisation, intensifying. The audience leans in with the camera |
| **Dolly out** | Isolation, conclusion, scale reveal |
| **Tracking / parallel** | Momentum, "with" the subject |
| **Handheld** | Immediacy, unease, documentary truth |
| **Crane / drone** | Scale and geography — establish, then get out |
| **Push + rack focus together** | The most "commercial" move there is |

**Anti-pattern:** movement in every shot. If everything moves, nothing means
anything. A commercial with three moving shots among nine static ones feels
more expensive than one where the camera never stops.

---

## 8. Stills photography — what transfers directly

Everything above, plus:

- **Shoot for the crop.** 4:5 for feed, 9:16 for stories, 1:1 for grid. Frame
  wide enough that all three survive.
- **Expose to the right (ETTR)** without clipping highlights — recover in post.
  Blown highlights are gone forever; shadows are recoverable.
- **Shoot RAW** for anything that will be graded or printed.
- **The best product light** is a large soft source at 45° plus a black flag on
  the opposite side to deepen the shadow edge. That single setup shoots most
  products convincingly.

---

## 9. Reading a frame like a DP (the 20-second audit)

Ask, in order:
1. Where is the key, and is it motivated?
2. Is there separation between subject and background (rim, contrast, DOF)?
3. Where do my eyes go first? Is that where the story is?
4. Is the product in the sharp plane?
5. Is there depth — foreground, midground, background?
6. Does the lens choice match the emotion?
7. Would this frame still read at thumbnail size on a phone?

If a shot fails three of these, it does not go in the cut.
