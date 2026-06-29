"""Paid Ads & Analytics Agent.

Conceptualizes Meta/Google campaign structures, sets ROAS/CPA targets,
parses CSV performance exports with deterministic Python math (never left
to the LLM), and drafts optimization recommendations grounded in that
math.
"""

from __future__ import annotations

import csv
import io
import statistics
from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory
from utils.tools import read_file


def analyze_performance_csv(csv_text: str) -> dict[str, Any]:
    """Deterministically compute ROAS/CPA metrics from a performance CSV.

    Expected columns (case-insensitive): ``campaign``, ``spend``, ``revenue``.
    Optional: ``clicks``, ``conversions``. Returns per-campaign and overall
    aggregates -- intentionally computed in plain Python rather than by the
    LLM, since arithmetic correctness matters for client-facing reporting.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = [{k.lower().strip(): v for k, v in row.items()} for row in reader]
    if not rows:
        return {"campaigns": [], "overall_roas": 0.0, "total_spend": 0.0, "total_revenue": 0.0}

    campaigns: list[dict[str, Any]] = []
    total_spend = 0.0
    total_revenue = 0.0
    for row in rows:
        spend = float(row.get("spend", 0) or 0)
        revenue = float(row.get("revenue", 0) or 0)
        total_spend += spend
        total_revenue += revenue
        campaigns.append(
            {
                "campaign": row.get("campaign", "unknown"),
                "spend": spend,
                "revenue": revenue,
                "roas": round(revenue / spend, 2) if spend else 0.0,
            }
        )

    campaigns.sort(key=lambda c: c["roas"], reverse=True)
    return {
        "campaigns": campaigns,
        "overall_roas": round(total_revenue / total_spend, 2) if total_spend else 0.0,
        "total_spend": round(total_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "median_roas": round(statistics.median(c["roas"] for c in campaigns), 2) if campaigns else 0.0,
    }


class PaidAdsAnalyticsAgent(BaseAgent):
    """Campaign structure, ROAS targets, CSV analysis, and optimization calls."""

    agent_key = "paid_ads"
    display_name = "Paid Ads & Analytics Agent"
    role_description = (
        "You are ZYNTH's Performance Marketing Lead. You design Meta/Google "
        "campaign structures, set realistic ROAS/CPA targets, and turn raw "
        "performance data into specific, prioritized optimization actions. "
        "You never hand-wave numbers -- you cite the data you were given."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": [
            "campaign_structure",
            "roas_targets",
            "performance_analysis",
            "optimization_recommendations",
        ],
        "properties": {
            "campaign_structure": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["platform", "campaign_name", "ad_sets", "budget_allocation_pct"],
                    "properties": {
                        "platform": {"type": "string"},
                        "campaign_name": {"type": "string"},
                        "ad_sets": {"type": "array", "items": {"type": "string"}},
                        "budget_allocation_pct": {"type": "number"},
                    },
                },
            },
            "roas_targets": {
                "type": "object",
                "required": ["target_roas", "target_cpa"],
                "properties": {
                    "target_roas": {"type": "number"},
                    "target_cpa": {"type": "number"},
                },
            },
            "performance_analysis": {
                "type": "object",
                "required": ["summary", "top_performers", "underperformers"],
                "properties": {
                    "summary": {"type": "string"},
                    "top_performers": {"type": "array", "items": {"type": "string"}},
                    "underperformers": {"type": "array", "items": {"type": "string"}},
                },
            },
            "optimization_recommendations": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        client_brief = await memory.get("client_brief", {})
        copy_assets = await memory.get("copywriter", {})
        qa_feedback = kwargs.get("qa_feedback")
        csv_relative_path = kwargs.get("csv_relative_path")

        metrics_summary: dict[str, Any] = {}
        if csv_relative_path:
            file_result = read_file(csv_relative_path)
            if file_result.ok:
                metrics_summary = analyze_performance_csv(file_result.data)
                await memory.update("paid_ads_raw_metrics", **metrics_summary)
            else:
                metrics_summary = {"error": file_result.error}

        prompt = (
            "Client brief:\n"
            f"{client_brief}\n\n"
            "Ad copy already produced by the Copywriter Agent (reuse headlines/CTAs where "
            "sensible instead of inventing new ones):\n"
            f"{copy_assets.get('ad_copy', 'none yet')}\n\n"
            "Deterministically computed performance metrics from CSV (empty if no data "
            "supplied yet -- in that case set sane initial targets instead):\n"
            f"{metrics_summary}\n\n"
            "Produce: (1) a Meta + Google campaign structure with ad sets and budget "
            "allocation percentages summing to 100 per platform, (2) ROAS/CPA targets, "
            "(3) a performance analysis citing the metrics above (or noting none exist "
            "yet), and (4) prioritized optimization recommendations."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback on your previous attempt -- address this directly: {qa_feedback}"
        return prompt
