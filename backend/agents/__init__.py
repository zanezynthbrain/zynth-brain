from .base import AgentError, AgentResult, BaseAgent
from .research_seo import MarketResearchSEOAgent
from .copywriter import ContentCopywriterAgent
from .lead_gen import LeadGenOutreachAgent
from .paid_ads import PaidAdsAnalyticsAgent
from .orchestrator import OrchestratorAgent, FinalReport, WorkflowStep, WORKFLOWS

__all__ = [
    "AgentError",
    "AgentResult",
    "BaseAgent",
    "MarketResearchSEOAgent",
    "ContentCopywriterAgent",
    "LeadGenOutreachAgent",
    "PaidAdsAnalyticsAgent",
    "OrchestratorAgent",
    "FinalReport",
    "WorkflowStep",
    "WORKFLOWS",
    "build_default_agents",
]


def build_default_agents(llm_client=None) -> dict[str, BaseAgent]:
    """Construct one instance of each specialist agent, sharing an LLM client."""
    from utils.llm_client import LLMClient

    shared_llm = llm_client or LLMClient()
    return {
        "research_seo": MarketResearchSEOAgent(shared_llm),
        "copywriter": ContentCopywriterAgent(shared_llm),
        "lead_gen": LeadGenOutreachAgent(shared_llm),
        "paid_ads": PaidAdsAnalyticsAgent(shared_llm),
    }
