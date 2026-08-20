#!/usr/bin/env python3
"""Seed the variety registry with what has already been produced.

Without this the registry starts empty and the first automated cycle happily
reproduces an idea the library already contains. The classifications below are
recorded by hand because they are judgements about the work, not something to
infer from a title — including the honest one: five consecutive proposals used
a published-performance-record mechanic.

    python backend/tools/backfill_variety.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.variety_registry import VarietyRegistry  # noqa: E402

# title fragment -> the seven dimensions actually used
PRIOR = [
    ("Built to be Trusted", "Manufacturing / B2B", "open-house / site visit",
     "transparency", "quality cannot be verified before buying", "book a visit",
     "published performance record", "mid-weight integrated", "no seasonal hook"),
    ("The Promise You Can Track", "Logistics & supply chain", "digital-only campaign",
     "proof over promise", "the promise is not believed", "switch supplier",
     "published performance record", "mid-weight integrated", "monsoon"),
    ("The Hours You Don't Lose", "Energy & renewables", "open-house / site visit",
     "continuity and reliability", "price is the only comparison", "book a visit",
     "free diagnostic audit", "flagship multi-market", "monsoon"),
    ("The Village Gets the Report First", "NGO / social impact", "community programme",
     "generosity", "the service disappears after the sale", "attend a recurring session",
     "community report-back", "lean pilot", "year-end / New Year"),
    ("Ask for the Cook", "Food & Beverage / FMCG", "loyalty / membership launch",
     "recognition of the overlooked", "the staff are anonymous", "request a named person",
     "named-staff request", "mid-weight integrated", "no seasonal hook"),
    ("You Will Understand Before You Decide", "Healthcare", "workshop series",
     "competence and safety", "nobody explains anything",
     "complete a follow-up appointment", "teach-back / comprehension check",
     "mid-weight integrated", "no seasonal hook"),
    ("Worth the Trip", "Retail & shopping malls", "community programme",
     "belonging", "convenience beat the relationship", "attend a recurring session",
     "recurring timetable", "flagship multi-market", "no seasonal hook"),
    ("KPAY THADINGYUT", "Financial services", "sponsorship activation",
     "heritage reframed", "the category is invisible", "opt in to a reminder channel",
     "source-coded redemption", "flagship multi-market", "Thadingyut"),
    ("WAVE PAY PREMIUM LAUNCH", "Financial services", "product launch",
     "status and arrival", "the buyer fears being oversold", "sign a multi-period commitment",
     "registration and attendance", "flagship multi-market", "no seasonal hook"),
    ("ZYNTH Marketing Agency Growth", "Marketing & advertising", "digital-only campaign",
     "craft and mastery", "the category is invisible", "refer a peer",
     "referral code", "lean pilot", "no seasonal hook"),
    ("Shwe Pay", "Financial services", "brand activation",
     "status and arrival", "price is the only comparison", "return within 60 days",
     "source-coded redemption", "flagship multi-market", "no seasonal hook"),
    ("Dry Fry", "Food & Beverage / FMCG", "product launch",
     "playfulness", "the category is invisible", "return within 60 days",
     "trial unit", "mid-weight integrated", "no seasonal hook"),
]

FIELDS = ("industry", "form", "territory", "tension", "behaviour",
          "mechanic", "budget_scale", "season")


def main() -> None:
    reg = VarietyRegistry()
    have = {(c.get("title") or "") for c in reg.data["concepts"]}
    added = []
    for row in PRIOR:
        title, rest = row[0], row[1:]
        if title in have:
            continue
        c = dict(zip(FIELDS, rest))
        c["title"] = title
        c["source"] = "backfill"
        reg.data["concepts"].append(c)
        added.append(title)
    # one synthetic cycle per industry already covered, so rotation skips them
    seen = {c["industry"] for c in reg.data["cycles"]}
    for c in reg.data["concepts"]:
        if c["industry"] not in seen:
            reg.data["cycles"].append({"industry": c["industry"],
                                       "run_id": "backfill", "count": 0})
            seen.add(c["industry"])
    reg.save()

    print(f"backfilled {len(added)} concepts")
    m = reg._used_counts("mechanic")
    for k, v in sorted(m.items(), key=lambda x: -x[1]):
        flag = "  <-- already used " + str(v) + "x, now blocked from repeating" if v >= 2 else ""
        print(f"  {v}x  {k}{flag}")
    cov = reg.coverage()
    print(f"\nindustries covered: {len(cov['industries_done'])}")
    print(f"industries left   : {', '.join(cov['industries_left']) or 'none'}")


if __name__ == "__main__":
    main()
