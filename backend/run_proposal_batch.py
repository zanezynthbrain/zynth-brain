"""One-shot Proposal Factory runner — designed for CI (GitHub Actions).

Generates proposal batches and exits. Each run picks the next uncovered
(industry × month) combos for the given market, or a specific combo if
--industry/--month are passed. Proposals are persisted to
outputs/proposal_pool/ which CI commits back to the repository, so the
repo itself is the data pool.

Usage:
    python run_proposal_batch.py --market MM --batches 3
    python run_proposal_batch.py --market SG --industry "F&B & Restaurant" --month July
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from agents.proposal_factory import ProposalFactoryAgent
from config import get_settings
from utils.llm_client import LLMClient
from utils.logging_config import configure_logging, get_logger
from utils.proposal_pool import ProposalPool
from utils.state import SharedMemory
from utils.telegram import send_message

logger = get_logger("run_proposal_batch")


async def main(market: str, batches: int, industry: str | None, month: str | None) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)

    # Respect the master switch: proposal production is OFF unless the MD turns it on.
    # Stops the daily CI/scheduler from producing proposals (and burning API budget).
    try:
        from utils import switches
        if not switches.enabled("daily_proposals"):
            logger.info("Proposal production is switched OFF (MD-only mode). Skipping.")
            print("Proposal production OFF — skipped (turn on with /switch daily_proposals on).")
            return 0
    except Exception:
        pass

    llm = LLMClient()
    memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "ci_proposal_batch"})
    agent = ProposalFactoryAgent(llm)
    pool = ProposalPool()

    generated: list[str] = []
    for _ in range(batches):
        if industry and month:
            combo = (industry, month)
            industry = month = None  # explicit combo only applies to the first batch
        else:
            combo = agent.next_uncovered(market, pool)
        if combo is None:
            logger.info("Pool fully covered for market %s — nothing left to generate.", market)
            break

        ind, mo = combo
        logger.info("Generating: %s × %s × %s", ind, mo, market)
        proposals = await agent.generate_batch(ind, mo, market, memory, pool)
        generated.append(f"{ind} × {mo} ({len(proposals)} proposals)")
        logger.info("Saved %d proposals for %s × %s", len(proposals), ind, mo)

    stats = pool.get_stats()
    summary = (
        f"🏭 <b>Proposal Factory ({market})</b>\n\n"
        + ("\n".join(f"✅ {g}" for g in generated) if generated else "Nothing new to generate.")
        + f"\n\n📊 Pool total: <b>{stats['total']}</b> proposals"
    )
    print(summary.replace("<b>", "").replace("</b>", ""))

    if settings.has_telegram and generated:
        try:
            await send_message(summary)
        except Exception as exc:  # Telegram failure shouldn't fail the CI run
            logger.warning("Telegram notify failed: %s", exc)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate proposal batches for the pool.")
    parser.add_argument("--market", default="MM", choices=["MM", "SG", "mm", "sg"])
    parser.add_argument("--batches", type=int, default=2, help="How many industry×month combos to fill")
    parser.add_argument("--industry", default=None, help="Exact industry name (optional)")
    parser.add_argument("--month", default=None, help="Month name e.g. July (optional)")
    args = parser.parse_args()

    sys.exit(asyncio.run(main(args.market.upper(), args.batches, args.industry, args.month)))
