from .base import AgentError, AgentResult, BaseAgent
from .orchestrator import OrchestratorAgent, FinalReport, WorkflowStep, WORKFLOWS

# Original specialist agents
from .research_seo import MarketResearchSEOAgent
from .copywriter import ContentCopywriterAgent
from .lead_gen import LeadGenOutreachAgent
from .paid_ads import PaidAdsAnalyticsAgent

# Leadership tier
from .ceo import CEOAgent
from .cmo import CMOAgent
from .coo import COOAgent
from .cfo import CFOAgent
from .hr import HRAgent

# Specialist department agents
from .event_manager import EventManagerAgent
from .operations import OperationsAgent
from .portfolio import PortfolioAgent

__all__ = [
    # Base
    "AgentError", "AgentResult", "BaseAgent",
    # Orchestrator
    "OrchestratorAgent", "FinalReport", "WorkflowStep", "WORKFLOWS",
    # Original specialists
    "MarketResearchSEOAgent", "ContentCopywriterAgent",
    "LeadGenOutreachAgent", "PaidAdsAnalyticsAgent",
    # Leadership
    "CEOAgent", "CMOAgent", "COOAgent", "CFOAgent", "HRAgent",
    # Department specialists
    "EventManagerAgent", "OperationsAgent", "PortfolioAgent",
    # Factory functions
    "build_default_agents", "build_full_agency",
]


def build_default_agents(llm_client=None) -> dict[str, BaseAgent]:
    """Build the original 4 marketing-workflow specialist agents (backward-compatible)."""
    from utils.llm_client import LLMClient
    shared_llm = llm_client or LLMClient()
    return {
        "research_seo": MarketResearchSEOAgent(shared_llm),
        "copywriter": ContentCopywriterAgent(shared_llm),
        "lead_gen": LeadGenOutreachAgent(shared_llm),
        "paid_ads": PaidAdsAnalyticsAgent(shared_llm),
    }


def build_full_agency(llm_client=None) -> dict[str, BaseAgent]:
    """Build the complete ZYNTH agency team: leadership + all specialists.

    This is the full agent roster used by the CEO Agent and the scheduler.
    All agents share one LLM client instance so a single token budget and
    retry configuration applies to the whole agency run.
    """
    from utils.llm_client import LLMClient
    shared_llm = llm_client or LLMClient()
    return {
        # Leadership
        "cmo": CMOAgent(shared_llm),
        "coo": COOAgent(shared_llm),
        "cfo": CFOAgent(shared_llm),
        "hr": HRAgent(shared_llm),
        # Original specialists (now report to CMO)
        "research_seo": MarketResearchSEOAgent(shared_llm),
        "copywriter": ContentCopywriterAgent(shared_llm),
        "lead_gen": LeadGenOutreachAgent(shared_llm),
        "paid_ads": PaidAdsAnalyticsAgent(shared_llm),
        # Department specialists (report to COO/CMO)
        "event_manager": EventManagerAgent(shared_llm),
        "operations": OperationsAgent(shared_llm),
        "portfolio": PortfolioAgent(shared_llm),
    }
