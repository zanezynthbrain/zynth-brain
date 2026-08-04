<!-- TEMPLATE -->
<!-- Reference document, not knowledge-base prose. Injected as a gold-standard
     art-direction example into the Design Director and Designer prompts. -->

# Visual Briefs — ZYNTH Service Lines

Written to the ZYNTH Art Director standard (`.claude/skills/zynth-art-director`).
These exist because the first pass at service designs was template-level: type on
a coloured field, no idea underneath. A brief is what prevents that. Every visual
below traces to a thought a competitor could not paste their logo onto.

**The governing principle:** ZYNTH sells judgement. Judgement cannot be
photographed directly — so each service is represented by *the moment the
judgement happens*, not by the deliverable it produces. No cameras-as-props, no
laptops-with-graphs, no handshake-in-a-ballroom.

---

## Brief 01 — Video Production

**Concept: "The First 1.5 Seconds"**

Attention is won or lost before a viewer decides to watch. So the image is not a
camera or a crew — it is a *monitor*, the surface where a director decides
whether the frame earns the next second. What is inside the frame survives;
everything outside it falls into darkness. That is literally what editing is.

### THE IDEA
Video is not a production service. It is a decision about what to leave out.

### THE FEELING
Focused, controlled, slightly tense. The quiet before a take. Premium but working
— sweat, not gloss.

### THE AUDIENCE
Myanmar SME owners and corporate marketing managers who have paid for a beautiful
film nobody watched. They recognise a real set instantly; they have been on one.

### VISUAL DIRECTION
- **Layout:** Photograph carries the top two-thirds; type occupies the lower
  third over a scrim. Poster logic, not card logic.
- **Typography:** One headline, ≤ 7 words, Inter 700 at 64–72pt. Burmese stacked
  below a gold rule at 1.9 line-height.
- **Imagery:** Director's field monitor sharp in foreground; room falling into
  navy shadow; one gold practical rimming the edge. Handheld 35mm, shallow DOF.
- **Colour:** Navy #12203A shadows, one warm gold #B88A2A light source. Graded
  toward navy at ~28% so it sits with the other two services.
- **Motion (video use):** Rack focus from the room to the monitor. No logo open.

### WHAT THIS IS NOT
- Not a camera held up heroically against a sunset.
- Not a smiling crew posed for a group photo.
- Not colour-saturated "cinematic" teal-and-orange — the grade is restrained.

### VISUAL REFERENCES (described)
1. Behind-the-scenes stills from A24 press kits — observational, low light, real.
2. Reuters photojournalism from Yangon — available light, no fill, honest grain.
3. Apple's "Shot on iPhone" BTS films — the tool in use, never the tool posed.

### MANDATORY
ZYNTH wordmark bottom-left in the clear zone. Gold entry rule above the headline.
Bottom 220px clear of critical elements.

---

## Brief 02 — Social Media Management

**Concept: "Arm's Length"**

The work is not consumed on a designer's calibrated monitor. It is consumed on a
mid-range Android, one-handed, at a teashop table, at night, with a glass of tea
sweating next to it. Designing for that is the whole service. So the photograph
is the real viewing condition — and it doubles as the reason a brand needs us.

### THE IDEA
We design for the thumb in daylight glare, not for the mockup.

### THE FEELING
Familiar, warm, unglamorous, true. A Yangon evening. The opposite of a laptop on
a marble desk.

### THE AUDIENCE
Owner-operators who scroll their own page at 10pm and know exactly what a feed
looks like at arm's length.

### VISUAL DIRECTION
- **Layout:** Overhead frame; type lands in the empty tabletop space at the top,
  or lower third over scrim — whichever the plate gives.
- **Typography:** Same system as 01. Burmese may lead here — this is the most
  Myanmar-native of the three.
- **Imagery:** Hand + mid-range Android, screen glowing but unreadable, tea glass
  with condensation, worn metal table, plastic stool edge. Tungsten warm against
  cool evening blue.
- **Colour:** Navy shadow, gold from street tungsten. No neon.

### WHAT THIS IS NOT
- Not a flat-lay of a new iPhone with a perfect Instagram grid on screen.
- Not a café in a Western city standing in for Yangon.
- Not legible UI — a readable feed dates the asset and invites nitpicking.

### VISUAL REFERENCES (described)
1. Ogilvy's SEA "real conditions" campaigns — product where it is actually used.
2. Magnum street photography, night — colour from practical sources only.
3. Grab's Myanmar social work at its best: local, specific, unposed.

### MANDATORY
Screen content always blurred/unreadable. No competitor brand marks in frame.

---

## Brief 03 — Event Management

**Concept: "Two Hours Before Doors"**

Nobody photographs the hour that decides an event. The client's memory is the
gala; ours is the empty room at 16:00 with cables being taped and LED being
tested. Selling the empty room is the proof that we know what the job actually
is — and it is the visual argument for the 10% contingency line.

### THE IDEA
The event is won before a single guest arrives.

### THE FEELING
Calm, competent, slightly cinematic. The room holding its breath. Not lonely —
*prepared*.

### THE AUDIENCE
Corporate marketing managers and SME owners who have watched a beautiful event
overrun and cost more than the quote. This image says: we have been here at 16:00.

### VISUAL DIRECTION
- **Layout:** Wide plate, dark upper half carrying the headline; the price/scope
  ledger sits in the lower third.
- **Typography:** As the system. The events line is where numbers appear — keep
  the figure row to one line so the photograph still breathes.
- **Imagery:** Empty banquet chairs in darkness, stage half-lit, LED wall at flat
  blank glow, gold uplight on a column, taped cable runs, one crew silhouette in
  motion blur.
- **Colour:** Deepest navy of the three (#0D1729 field). Gold only from the
  uplights — no added accent.

### WHAT THIS IS NOT
- Not a full ballroom mid-applause.
- Not a stage with a confetti cannon firing.
- Not a chandelier close-up standing in for "premium".

### VISUAL REFERENCES (described)
1. Load-in photography from touring music production — process as the subject.
2. Gregory Crewdson's staged emptiness — light doing the storytelling.
3. IGNITE's own build documentation — the in-public build we already publish.

### MANDATORY
No recognisable venue branding. No guests' faces. Gold from practicals only.

---

## Production note — how these are executed

1. **Generate the plate** on OpenArt (GPT Image 2, 4:5, 2K, ~40 credits) using
   the prompt derived from the Visual Direction above. Prompts never request
   text, logos, or readable screens.
2. **Grade toward navy** (~28%) so three plates from three prompts read as one
   brand, then apply the bottom scrim.
3. **Typeset everything over it** — headline, Burmese, ledger, CTA chip, wordmark
   — in `utils/compositor.py`. Burmese is NEVER generated inside the image model;
   Myanmar diacritic stacking breaks unpredictably.
4. **Check** on the review board before anything is approved.
