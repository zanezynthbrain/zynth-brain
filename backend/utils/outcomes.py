"""Outcome register — how the system learns from reality, not from itself.

ZYNTH already has an *internal* reflective loop: `utils/mistakes.py` records
failures, `utils/lessons.py` distils them into durable lessons that go back into
prompts, and `utils/bestof.py` promotes the highest-scored approved work into
the few-shot exemplars. All of that is the system grading its own homework.

This closes the other half: **what actually happened in the world.** A post's
real engagement, whether a pitch was won or lost, what an event actually cost
against its budget. Then it compares that to an external benchmark and turns the
gap into a lesson the agents read on their next run.

The chain:

    record_outcome()  →  compare vs BENCHMARKS  →  verdict (beat/met/missed)
                                                        ↓
                               promote_learnings() → utils.lessons → prompts

Rules kept from the rest of the system:
  - An outcome with no real number is `verified: false` and never counts toward
    a benchmark. Agents may not present it as fact.
  - Benchmarks are tagged with their source. A benchmark nobody sourced is a
    guess wearing a suit.
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.logging_config import get_logger

logger = get_logger("utils.outcomes")

_FILE = Path("outputs/proposal_pool/outcomes.json")

#: What kind of thing produced this outcome.
KINDS = ("post", "campaign", "pitch", "event", "video", "outreach")

#: External benchmarks the system measures itself against.
#: Source is recorded because an unsourced benchmark is not a benchmark.
#: See knowledge/25_marketing_campaign_playbook.md.
BENCHMARKS: dict[str, dict[str, Any]] = {
    "engagement_rate": {
        "unit": "%", "good": 5.0, "ok": 3.0, "higher_is_better": True,
        "source": "knowledge/25 — social engagement 1–5% [UNVERIFIED — Manus]",
    },
    "ctr_social": {
        "unit": "%", "good": 2.0, "ok": 0.5, "higher_is_better": True,
        "source": "knowledge/25 — social CTR 0.5–2%",
    },
    "ctr_search": {
        "unit": "%", "good": 5.0, "ok": 2.0, "higher_is_better": True,
        "source": "knowledge/25 — search CTR 2–5%",
    },
    "roas": {
        "unit": "x", "good": 5.0, "ok": 3.0, "higher_is_better": True,
        "source": "knowledge/25 — e-commerce ROAS target 3–5x+",
    },
    "saves_per_post": {
        "unit": "count", "good": 20.0, "ok": 10.0, "higher_is_better": True,
        "source": "ZYNTH September plan KPI — saves predict enquiries in this category",
    },
    "pitch_win_rate": {
        "unit": "%", "good": 33.0, "ok": 20.0, "higher_is_better": True,
        "source": "ZYNTH internal target — 1 in 3 pitches",
    },
    "gross_margin": {
        "unit": "%", "good": 40.0, "ok": 35.0, "higher_is_better": True,
        "source": "R1 financial law — 35% floor, 40% target",
    },
    "budget_variance": {
        # "good" is 5%, not 0% — a benchmark only perfection can beat is a
        # benchmark nobody learns from. 10% is the contingency line (R-law).
        "unit": "%", "good": 5.0, "ok": 10.0, "higher_is_better": False,
        "source": "ZYNTH — quoted vs actual; 10% contingency is the outer limit",
    },
    "reply_rate": {
        "unit": "%", "good": 10.0, "ok": 5.0, "higher_is_better": True,
        "source": "ZYNTH BD — cold outreach reply rate",
    },
}


def _load() -> list[dict]:
    try:
        if _FILE.exists():
            data = json.loads(_FILE.read_text(encoding="utf-8"))
            return data.get("outcomes", data) if isinstance(data, dict) else data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read outcomes: %s", exc)
    return []


def _save(rows: list[dict]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def judge(metric: str, value: float) -> dict[str, Any]:
    """Score one measurement against its external benchmark."""
    bench = BENCHMARKS.get(metric)
    if not bench:
        return {"metric": metric, "value": value, "verdict": "no_benchmark",
                "note": f"No benchmark defined for '{metric}' — add one before judging it."}
    good, ok, higher = bench["good"], bench["ok"], bench["higher_is_better"]
    if higher:
        verdict = "beat" if value >= good else "met" if value >= ok else "missed"
    else:
        verdict = "beat" if value <= good else "met" if value <= ok else "missed"
    return {
        "metric": metric, "value": value, "unit": bench["unit"],
        "benchmark_good": good, "benchmark_ok": ok,
        "verdict": verdict, "source": bench["source"],
    }


def record_outcome(
    ref: str,
    kind: str,
    metrics: dict[str, float],
    brand: str = "",
    note: str = "",
    verified: bool = False,
) -> dict[str, Any]:
    """Log what actually happened, judged against the benchmarks.

    ``ref`` links back to the artifact — a post ref (P04), a proposal title, an
    event name. ``verified`` means a human read the number off the real
    dashboard; unverified rows are kept but excluded from every aggregate.
    """
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if not metrics:
        raise ValueError("An outcome needs at least one measured metric.")

    judged = [judge(m, float(v)) for m, v in metrics.items()]
    row = {
        "ref": ref, "kind": kind, "brand": brand, "note": note,
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "verified": bool(verified),
        "metrics": judged,
        "summary": {
            "beat": sum(1 for j in judged if j["verdict"] == "beat"),
            "met": sum(1 for j in judged if j["verdict"] == "met"),
            "missed": sum(1 for j in judged if j["verdict"] == "missed"),
        },
    }
    rows = _load()
    rows.append(row)
    _save(rows)
    logger.info("Outcome recorded for %s (%s)", ref, kind)
    return row


def verify_outcome(ref: str) -> dict | None:
    """Mark an outcome as confirmed against the real dashboard."""
    rows = _load()
    for i, row in enumerate(rows):
        if row.get("ref") == ref and not row.get("verified"):
            row["verified"] = True
            row["verified_at"] = datetime.now().isoformat(timespec="seconds")
            rows[i] = row
            _save(rows)
            return row
    return None


def all_outcomes(verified_only: bool = False) -> list[dict]:
    rows = _load()
    return [r for r in rows if r.get("verified")] if verified_only else rows


def performance(kind: str = "", verified_only: bool = True) -> dict[str, Any]:
    """Aggregate: where the system beats the outside world and where it misses."""
    rows = [r for r in all_outcomes(verified_only) if not kind or r.get("kind") == kind]
    if not rows:
        return {"count": 0, "note": "No verified outcomes yet — the loop has nothing real to learn from."}

    by_metric: dict[str, list[float]] = {}
    verdicts: dict[str, int] = {"beat": 0, "met": 0, "missed": 0, "no_benchmark": 0}
    for row in rows:
        for judged in row["metrics"]:
            verdicts[judged["verdict"]] = verdicts.get(judged["verdict"], 0) + 1
            by_metric.setdefault(judged["metric"], []).append(judged["value"])

    averages = {
        metric: {
            "average": round(statistics.mean(values), 2),
            "samples": len(values),
            **{k: v for k, v in judge(metric, statistics.mean(values)).items()
               if k in ("verdict", "benchmark_good", "benchmark_ok", "unit", "source")},
        }
        for metric, values in by_metric.items()
    }
    total = sum(verdicts.values()) or 1
    return {
        "count": len(rows),
        "verdicts": verdicts,
        "hit_rate_pct": round(100 * (verdicts["beat"] + verdicts["met"]) / total, 1),
        "by_metric": averages,
        "weakest": sorted(
            (m for m, d in averages.items() if d.get("verdict") == "missed"),
            key=lambda m: averages[m]["samples"], reverse=True,
        ),
    }


def promote_learnings(min_samples: int = 3) -> list[str]:
    """Turn measured under-performance into durable lessons the agents read.

    This is the promotion step: a metric that misses its benchmark across
    ``min_samples`` verified outcomes becomes a lesson in `utils.lessons`, which
    is injected into agent prompts — so the next month's work is written by a
    system that knows what actually underperformed.
    """
    report = performance(verified_only=True)
    if not report.get("by_metric"):
        return []

    promoted: list[str] = []
    for metric, data in report["by_metric"].items():
        if data.get("verdict") != "missed" or data["samples"] < min_samples:
            continue
        text = (
            f"MEASURED UNDER-PERFORMANCE — {metric}: our average is "
            f"{data['average']}{data.get('unit', '')} across {data['samples']} verified "
            f"results, against a benchmark of {data.get('benchmark_ok')} (acceptable) / "
            f"{data.get('benchmark_good')} (good). Source: {data.get('source', 'n/a')}. "
            f"Change the approach on the next run rather than repeating it."
        )
        from utils.lessons import add
        # Deliberately NOT wrapped in a bare except: a silently-swallowed write
        # here would mean the loop looks like it is learning while nothing
        # reaches the prompts.
        add(area="performance", lesson=text, source="outcomes")
        promoted.append(text)
    if promoted:
        logger.info("Promoted %d measured lesson(s) into the prompt layer", len(promoted))
    return promoted


def format_report(kind: str = "") -> str:
    """Telegram-ready performance summary."""
    report = performance(kind)
    if not report.get("count"):
        return ("📊 <b>Outcomes</b>\n\nNo verified results yet.\n\n"
                "Record one: <code>/outcome P04 post engagement_rate=4.2 saves_per_post=18</code>\n"
                "Then confirm it against the real dashboard: <code>/outcome verify P04</code>")
    lines = [
        f"📊 <b>Performance vs the outside world</b>{' · ' + kind if kind else ''}",
        f"{report['count']} verified outcome(s) · hit rate {report['hit_rate_pct']}%",
        f"beat {report['verdicts']['beat']} · met {report['verdicts']['met']} · missed {report['verdicts']['missed']}",
        "",
    ]
    for metric, data in sorted(report["by_metric"].items(), key=lambda kv: kv[1]["samples"], reverse=True):
        icon = {"beat": "🟢", "met": "🟡", "missed": "🔴"}.get(data.get("verdict"), "⚪")
        lines.append(
            f"{icon} <b>{metric}</b>: {data['average']}{data.get('unit', '')} "
            f"(bench {data.get('benchmark_ok')}/{data.get('benchmark_good')}, n={data['samples']})"
        )
    if report["weakest"]:
        lines += ["", "Weakest, most-sampled: " + ", ".join(report["weakest"][:3]),
                  "Run <code>/outcome learn</code> to push these into the agents' prompts."]
    return "\n".join(lines)


__all__ = [
    "KINDS", "BENCHMARKS", "judge", "record_outcome", "verify_outcome",
    "all_outcomes", "performance", "promote_learnings", "format_report",
]
