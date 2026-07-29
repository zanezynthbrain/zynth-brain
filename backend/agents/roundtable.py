"""Roundtable — the ZYNTH agents actually DISCUSS each other's work and improve it.

Most multi-agent systems run agents in parallel and staple the outputs together. This
is different: several distinct agent VOICES critique a draft from their own angle, a
reviser integrates the discussion into a sharper version, and the Critic scores it —
looping until it passes or the rounds run out. The result is an artifact that has
survived an argument, which is how you get an outstanding result instead of an average one.

Every round is captured in a transcript (the discussion), and recurring weaknesses feed
the self-improvement loop so the whole agency gets better over time.

Mock-safe offline like every other agent.
"""

from __future__ import annotations

import asyncio
from typing import Any

from agents.critic import CriticAgent
from utils.llm_client import LLMClient

# The voices at the table — each attacks the work from a different, real angle.
VOICES = [
    ("Strategist", "sharpen the strategic logic and force it down to ONE clear idea; cut anything that doesn't serve the objective"),
    ("Creative Director", "push the idea to be more distinctive, ownable and vivid — could a competitor have pitched this? make the reader SEE it"),
    ("Commercial Lead", "stress-test the money: real MM/SG rates at market FX, the 35% margin floor, and whether the client's VALUE/ROI is one unmistakable number"),
    ("Client Skeptic", "attack it as a hard-to-please client would — find every reason to say NO, every vague claim, every unproven number"),
]


async def _voice(llm: LLMClient, name: str, brief: str, artifact: str, kind: str) -> str:
    system = (
        f"You are ZYNTH's {name} in a working review. Your job is to make the {kind} WIN. "
        f"In 2–4 sharp, specific, constructive bullets, {brief}. No vague praise; name the "
        "exact fix. If something is genuinely strong, say so in one line so it's protected."
    )
    resp = await llm.complete(system=system, user_prompt=f"The {kind} under review:\n\n{artifact[:8000]}", max_tokens=450)
    return resp.text.strip()


async def _revise(llm: LLMClient, artifact: str, critiques: list[tuple[str, str]], kind: str) -> str:
    discussion = "\n\n".join(f"[{name}]\n{note}" for name, note in critiques)
    system = (
        f"You are ZYNTH's lead producer. Integrate the team's critique into a STRONGER, "
        f"complete version of the {kind}. Fix everything they raised, protect what they "
        "praised, keep it fully populated (no placeholders), hold the financial law and "
        "market FX, and make the client's result unmistakable. Return the improved "
        f"{kind} in full."
    )
    resp = await llm.complete(
        system=system,
        user_prompt=f"CURRENT {kind.upper()}:\n{artifact[:9000]}\n\nTEAM DISCUSSION:\n{discussion}\n\nReturn the improved version:",
        max_tokens=4000,
    )
    return resp.text.strip()


async def run_roundtable(artifact: str, kind: str = "proposal", rounds: int = 2,
                         llm: LLMClient | None = None) -> dict[str, Any]:
    """Run the discussion→revise→score loop. Returns the best version + the transcript."""
    llm = llm or LLMClient()
    critic = CriticAgent(llm)
    current = artifact
    transcript: list[dict[str, Any]] = []
    best = {"artifact": current, "score": 0.0}
    last_round = 0

    for r in range(1, max(1, rounds) + 1):
        last_round = r
        # 1) the voices critique in parallel (they "discuss")
        notes = await asyncio.gather(*[_voice(llm, name, brief, current, kind) for name, brief in VOICES])
        pairs = list(zip([v[0] for v in VOICES], notes))
        for name, note in pairs:
            transcript.append({"round": r, "voice": name, "note": note})
        # 2) a reviser integrates the discussion
        current = await _revise(llm, current, pairs, kind)
        transcript.append({"round": r, "voice": "Reviser", "note": "Integrated the discussion into a sharper version."})
        # 3) the Critic scores the result
        crit = await critic.critique(current, kind=kind)
        score = float(crit.get("overall_score", 0) or 0)
        verdict = crit.get("verdict", "revise")
        transcript.append({"round": r, "voice": "Critic", "note": f"{verdict} · {score}/10",
                           "score": score, "verdict": verdict,
                           "must_fix": crit.get("must_fix") or crit.get("reasons") or []})
        if score >= best["score"]:
            best = {"artifact": current, "score": score}
        if verdict == "pass":
            break

    # feed the loop: if it never passed, that's a weakness worth logging
    try:
        if best["score"] < 8:
            from utils import mistakes
            mistakes.record("roundtable", f"{kind} did not reach pass after {last_round} round(s)",
                            f"best {best['score']}/10", "warn")
    except Exception:
        pass

    return {"final": best["artifact"], "score": best["score"], "rounds": last_round,
            "passed": best["score"] >= 8, "transcript": transcript}


def summary(result: dict[str, Any]) -> str:
    """Short Telegram summary of a roundtable."""
    icon = "🏆" if result.get("passed") else "🔁"
    voices = len({t["voice"] for t in result.get("transcript", []) if t["voice"] not in ("Reviser", "Critic")})
    return f"{icon} Roundtable: {voices} voices · {result.get('rounds')} round(s) · best {result.get('score')}/10"
