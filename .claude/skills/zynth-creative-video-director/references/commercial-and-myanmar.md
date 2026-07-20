# Commercial Standards, Delivery Specs & Myanmar Realities

What "commercial level" actually means in specs, and how to make it real on a
Myanmar/Singapore SME budget and infrastructure.

---

## 1. Platform delivery specs (get these right or it looks amateur)

| Platform / use | Aspect | Resolution | Frame rate | Length | Codec/notes |
|---|---|---|---|---|---|
| YouTube (hero/TVC) | 16:9 | 1080p / 4K | 24/25/30 | 15–90s ad | H.264/265, 16–65 Mb/s |
| Instagram/FB Reels | 9:16 | 1080×1920 | 30 | ≤90s (hook <1.5s) | captions on |
| TikTok | 9:16 | 1080×1920 | 30 | 9–34s sweet spot | trend-aware |
| FB/IG in-feed | 1:1 or 4:5 | 1080×1080 / 1080×1350 | 30 | ≤60s | 4:5 wins feed space |
| Stories | 9:16 | 1080×1920 | 30 | ≤15s/card | safe zones! |
| LED / event screen | check pixel map | native panel res | 25/30 | loop | test on the actual wall |
| Broadcast TVC (MRTV/MITV/Mahar etc.) | 16:9 | 1080i/p | 25 (PAL region) | 15/30/45s exact | −23 LUFS, broadcast-legal, station spec sheet |

**Safe zones:** keep text/logos away from edges; on 9:16 avoid the top ~10% and bottom ~20% (UI covers it). Design captions inside the safe area.

**Always deliver:** master (ProRes/DNxHR) + platform H.264 versions + subtitled versions (burned-in for social, .srt sidecar for YouTube) + a thumbnail still. Name files clearly: `Client_Project_Version_Aspect_Date.mp4`.

---

## 2. What separates "commercial level" from "content"
- **Intentional everything** — framing, movement, cut, grade, sound each chosen for a reason.
- **Consistency** — one look, one type system, one sonic identity across the film and its cutdowns.
- **Finish** — clean keys, matched grades, designed sound, legal levels, correct specs.
- **Restraint** — knowing what to leave out. Trend effects and transitions used only when they serve the idea.
- **The edit was planned** — it matches an approved storyboard; the shoot delivered the cut.

---

## 3. Frame rate & motion intent
- **24fps** — cinematic, filmic (TVC, brand films). Shutter ~1/48–1/50.
- **25fps** — PAL broadcast standard (Myanmar/SG region TV).
- **30fps** — clean, "video," common for social/corporate.
- **50/60fps** — smooth motion, sports, or to retime into slow-mo (shoot high, deliver at 24/30).
- Shoot slow-mo in-camera (high fps) when possible — always beats software interpolation.

---

## 4. Myanmar production realities (plan around these)
- **Power** — outages are routine. On shoots: generator + battery backup for lights/monitors. In post: **save every few minutes, enable auto-save/backup**, use a UPS on the edit machine, keep project backups on cloud + drive (Railway-style "assume the machine can die").
- **Hardware** — many edits happen on modest laptops. Use **proxies/optimised media** (Resolve/Premiere), edit offline at low-res, relink to full-res for final. Free **DaVinci Resolve** is the best value (no subscription); recommend it as ZYNTH's core.
- **Internet** — large file transfer is painful. Compress proxies for client review (send a 1080p H.264, not the ProRes master); use resumable uploads.
- **Fonts & language** — use proper **Myanmar Unicode** fonts (Pyidaungsu, Noto Sans Myanmar) that render stacking correctly; test that CapCut/Premiere/Resolve display MM text properly (some fonts break). Give Burmese text more line-height than English.
- **Music/licensing** — don't ship trending TikTok audio on a paid brand ad. Use royalty-free libraries or commission a local composer; it's cheap insurance and can become the brand's sonic signature.
- **Talent & release** — get signed usage rights; verify what footage can be used and for how long.

---

## 5. Bilingual delivery (MM + EN)
- Decide per deliverable: MM voice + EN subs, EN voice + MM subs, or two full versions.
- **Transcreate** taglines, don't translate — a Burmese line must feel native, not like subtitles of an English idea.
- On-screen text: short lines, correct Unicode, tested rendering, comfortable line-height, legible size on a phone.
- Keep an EN master and an MM master so the client can run both markets.

---

## 6. The ZYNTH commercial workflow (concept → delivery)
1. **Brief** → strategy, objective, platform, budget, language(s), deadline.
2. **Concept + treatment** (this skill) → client approves the idea.
3. **Storyboard + AV script** (this skill) → client approves the film on paper.
4. **Pre-pro** → shot list, schedule, look-dev; line-produce via **zynth-video-producer** + **zynth-vendor-finder**.
5. **Shoot** → capture the approved board + coverage; ZYNTH rep on set.
6. **Post** → assembly → picture lock → sound → graphics/VFX → grade → finish (this skill's tool refs).
7. **Deliver** → masters + all platform/aspect/language versions + subs + thumbnail.
8. **Learn** → what performed; feed insight back to **zynth-content-strategist** / analytics.

**Standard:** 2 revision rounds included; picture lock before finishing; nothing graded or graphic'd before lock. Charge extra rounds kindly but firmly (see zynth-video-producer).

---

## 6a. Myanmar production rates & vendors (indicative — always RFQ)

**Crew day-rates (MMK/day):** Director 1.5M–5M+ · DP 800k–2.5M (excl. gear) ·
Gaffer 300k–600k · Sound recordist 250k–500k · Production manager 400k–800k ·
Editor 500k–1.5M · Colorist 800k–2M.

**Equipment rental — Yangon (MMK/day):** Blackmagic URSA Mini 4.6K ~40k · URSA
Mini Pro ~50k · Canon 5D IV ~50k · Sony A7S III ~60–80k · DJI Ronin RS3 ~70k ·
RED Komodo body ~150–250k.

**Rental / production houses (indicative — verify contacts, cross-check `/vendor`):**
Shwe Sin Oo (mid-range gear) · Wyne Camera Rental (DSLR/mirrorless, social) ·
Mandalay Productions (high-end cinema, fixing) · CMB Films Myanmar (lighting/grip).

**Legal:** commercials & internet films technically need approval under the 2025
Motion Picture Law amendments — build clearance lead-time in. Myanmar text in
**Unicode (Pyidaungsu)**, never Zawgyi. Respect elders/monks/religious sites.

Always take 3 quotes; tag any rate you quote a client "indicative — pending RFQ".

## 7. Fast answers you should always have ready
- "What fps?" → 24 filmic / 25 MM-broadcast / 30 social.
- "What loudness?" → −14 LUFS online, −23 broadcast, peaks < −1 dBTP.
- "What for the vertical version?" → 1080×1920, safe zones, re-check grade/contrast for phone.
- "Which tool?" → Resolve to grade/finish, CapCut for social volume, Premiere/AE for Adobe pipelines and heavy motion.
- "Can we use this song?" → not if it's a trending/commercial track without a licence.
