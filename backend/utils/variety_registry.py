"""Stop proposals overlapping each other.

The founder's production spec (§5 Required Diversity Rules, §10 Scheduled
Cadence) asks for one cycle every two hours where nothing repeats — not the
industry, not the event form, not the creative territory, not the mechanic.

Left to itself a generator drifts: it finds one idea that works and reruns it
with a new noun. That happened in this repo already — five consecutive
gold-standard proposals all used a "publish the number" mechanic. Good idea,
wrong to use five times.

This module is the cumulative memory that prevents it. It records what every
past proposal used across seven dimensions, and hands the next cycle a brief
that cannot collide with anything already produced.

    reg = VarietyRegistry()
    industry = reg.next_industry()          # rotation, never the previous one
    briefs   = reg.plan_cycle(industry, 10) # 10 non-overlapping concept briefs
    reg.claim_cycle(industry, briefs)       # record them

State lives in backend/outputs/variety_registry.json.
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "outputs" / "variety_registry.json"

# Industry rotation — the founder's recommended order (spec, Table 3)
ROTATION = [
    "Financial services",
    "Hospitality / tourism / MICE",
    "Beauty / wellness",
    "Automotive / EV",
    "Education",
    "Telecom / technology",
    "Real estate",
    "Manufacturing / B2B",
    "Healthcare",
    "NGO / social impact",
    "Food & Beverage / FMCG",
    "Retail & shopping malls",
    "Logistics & supply chain",
    "Energy & renewables",
]

# The seven dimensions from the spec, each with a vocabulary the planner draws
# from. A concept is a tuple across all seven; two concepts may share at most
# MAX_SHARED of them (see _collides).
DIMENSIONS = {
    "form": [
        "brand activation", "product launch", "press preview", "trade show",
        "roadshow", "pop-up retail", "conference / summit", "workshop series",
        "sampling programme", "open-house / site visit", "awards / recognition",
        "community programme", "digital-only campaign", "creator collaboration",
        "loyalty / membership launch", "sponsorship activation",
    ],
    "territory": [
        "transparency", "craft and mastery", "belonging", "status and arrival",
        "relief from friction", "heritage reframed", "proof over promise",
        "generosity", "competence and safety", "playfulness",
        "continuity and reliability", "recognition of the overlooked",
        "curiosity and discovery", "care for the next generation",
    ],
    "tension": [
        "price is the only comparison", "nobody explains anything",
        "the promise is not believed", "the category is invisible",
        "choice is overwhelming", "the first purchase never repeats",
        "the staff are anonymous", "quality cannot be verified before buying",
        "the buyer fears being oversold", "the service disappears after the sale",
        "the customer is embarrassed to ask", "convenience beat the relationship",
    ],
    "behaviour": [
        "book a visit", "request a named person", "attend a recurring session",
        "complete a follow-up appointment", "switch supplier", "refer a peer",
        "sign a multi-period commitment", "opt in to a reminder channel",
        "bring a decision-maker along", "submit their own data for assessment",
        "return within 60 days", "upgrade tier",
    ],
    "mechanic": [
        "source-coded redemption", "appointment booking", "retail scan",
        "registration and attendance", "free diagnostic audit",
        "published performance record", "named-staff request", "trial unit",
        "recurring timetable", "referral code", "community report-back",
        "site-visit programme", "teach-back / comprehension check",
        "membership enrolment",
    ],
    "budget_scale": [
        "lean pilot", "mid-weight integrated", "flagship multi-market",
    ],
    "season": [
        "no seasonal hook", "Thadingyut", "Thingyan", "year-end / New Year",
        "school intake", "monsoon", "harvest / year-end business cycle",
        "festival gifting season",
    ],
}

# Two concepts may share at most this many dimensions before they read as
# variants of each other rather than distinct ideas.
MAX_SHARED = 2
# Dimensions that must NEVER repeat inside a single 10-concept cycle.
UNIQUE_IN_CYCLE = ("form", "territory", "tension", "mechanic")


def _empty() -> dict:
    return {"cycles": [], "concepts": [], "updated": ""}


class VarietyRegistry:
    def __init__(self, path: Path | None = None):
        self.path = path or STATE
        self.data = self._load()

    # ---------------------------------------------------------------- io
    def _load(self) -> dict:
        try:
            d = json.loads(self.path.read_text(encoding="utf-8"))
            for k in ("cycles", "concepts"):
                d.setdefault(k, [])
            return d
        except Exception:
            return _empty()

    def save(self) -> None:
        self.data["updated"] = datetime.now().isoformat(timespec="seconds")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1),
                             encoding="utf-8")

    # ------------------------------------------------------------ industry
    def recent_industries(self, n: int = 3) -> list[str]:
        return [c["industry"] for c in self.data["cycles"][-n:]]

    def next_industry(self) -> str:
        """Next in rotation, skipping anything used in the last 3 cycles."""
        recent = self.recent_industries(3)
        done = [c["industry"] for c in self.data["cycles"]]
        for ind in ROTATION:
            if ind not in done:
                return ind                      # unseen industries first
        # every industry has run at least once — continue the rotation from
        # whichever is least recently used
        order = sorted(ROTATION, key=lambda i: max(
            (n for n, c in enumerate(self.data["cycles"]) if c["industry"] == i),
            default=-1))
        for ind in order:
            if ind not in recent:
                return ind
        return order[0]

    # ------------------------------------------------------------- overlap
    def _used_counts(self, dim: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.data["concepts"]:
            v = c.get(dim)
            if v:
                out[v] = out.get(v, 0) + 1
        return out

    @staticmethod
    def _shared(a: dict, b: dict) -> int:
        return sum(1 for d in DIMENSIONS if a.get(d) and a.get(d) == b.get(d))

    def _collides(self, brief: dict, others: list[dict]) -> bool:
        for o in others:
            if self._shared(brief, o) > MAX_SHARED:
                return True
            # a shared mechanic AND a shared territory is the specific failure
            # mode that produced five near-identical proposals
            if brief.get("mechanic") == o.get("mechanic") and \
               brief.get("territory") == o.get("territory"):
                return True
        return False

    def _pick(self, dim: str, taken: set[str], rng: random.Random,
              in_cycle: dict[str, int] | None = None) -> str:
        """Least-used value first, so the vocabulary spreads instead of clumping.

        `taken` is a hard exclusion (dimensions that must be unique in a cycle).
        `in_cycle` counts what this cycle has used so far and is a soft weight —
        without it, a dimension with a small vocabulary (budget_scale has three
        values) picks the same least-used value for all ten concepts, which is
        how a cycle ends up entirely "lean pilot".
        """
        counts = self._used_counts(dim)
        in_cycle = in_cycle or {}
        pool = [v for v in DIMENSIONS[dim] if v not in taken]
        if not pool:                       # cycle longer than the vocabulary
            pool = list(DIMENSIONS[dim])
        # in-cycle usage dominates history, so a cycle spreads across the
        # vocabulary before it starts optimising against the archive
        def weight(v: str) -> tuple[int, int]:
            return (in_cycle.get(v, 0), counts.get(v, 0))
        least = min(weight(v) for v in pool)
        best = [v for v in pool if weight(v) == least]
        return rng.choice(best)

    # ---------------------------------------------------------------- plan
    def plan_cycle(self, industry: str, count: int = 10, seed: int | None = None) -> list[dict]:
        """`count` concept briefs that overlap neither each other nor history."""
        rng = random.Random(seed if seed is not None else len(self.data["concepts"]) * 7919 + 13)
        history = self.data["concepts"]
        briefs: list[dict] = []
        taken = {d: set() for d in DIMENSIONS}
        in_cycle: dict[str, dict[str, int]] = {d: {} for d in DIMENSIONS}

        for i in range(count):
            for _attempt in range(400):
                b = {"industry": industry, "n": i + 1}
                for d in DIMENSIONS:
                    b[d] = self._pick(d, taken[d] if d in UNIQUE_IN_CYCLE else set(),
                                      rng, in_cycle[d])
                if not self._collides(b, briefs) and not self._collides(b, history):
                    break
            else:
                # exhausted: accept the best available rather than fail the run,
                # and mark it so the report is honest about the compromise
                b["relaxed"] = True
            for d in UNIQUE_IN_CYCLE:
                taken[d].add(b[d])
            for d in DIMENSIONS:
                in_cycle[d][b[d]] = in_cycle[d].get(b[d], 0) + 1
            briefs.append(b)
        return briefs

    def claim_cycle(self, industry: str, briefs: list[dict], run_id: str = "") -> None:
        self.data["cycles"].append({
            "industry": industry,
            "run_id": run_id or datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "count": len(briefs),
        })
        self.data["concepts"].extend(briefs)
        self.save()

    # -------------------------------------------------------------- report
    def coverage(self) -> dict:
        return {
            "cycles": len(self.data["cycles"]),
            "concepts": len(self.data["concepts"]),
            "industries_done": sorted({c["industry"] for c in self.data["cycles"]}),
            "industries_left": [i for i in ROTATION
                                if i not in {c["industry"] for c in self.data["cycles"]}],
            "dimension_usage": {d: len(self._used_counts(d)) for d in DIMENSIONS},
            "dimension_total": {d: len(v) for d, v in DIMENSIONS.items()},
        }
