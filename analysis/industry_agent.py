from __future__ import annotations
from typing import Dict, Any, List
from llm.gemini_client import GeminiResearchClient

INDUSTRY_SCHEMA = {
    "type": "object",
    "properties": {
        "industry": {"type": "string"},
        "as_of": {"type": "string"},
        "macro_snapshot": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "competitor_moves": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "sector_news": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "industry_read": {"type": "string"},
        "affected_companies": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "research_queue": {"type": "array", "items": {"type": "string"}},
        "sources": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
    },
    "required": ["industry", "as_of", "macro_snapshot", "competitor_moves", "sector_news", "industry_read", "affected_companies", "research_queue", "sources"],
}

PROMPT = """
You are an institutional equity-research industry intelligence agent. Use current web research and prioritize primary company/regulator sources plus high-quality financial/news sources.

Watchlist companies: {companies}

TASK
1) Infer the relevant industries/sectors represented by the watchlist. Focus on the industries that matter to these companies, not a generic market overview.
2) Find material developments from the last 24-72 hours where possible: competitor capacity/capex, pricing, product launches, M&A, financing, hiring/layoffs, geographic expansion, technology, regulation, supply-chain changes, demand signals, and major strategic announcements.
3) Track macro/economic variables that directly affect those industries (rates, inflation, commodities, FX, demand, regulation). Give direction and why it matters.
4) Deduplicate overlapping stories. Rank developments by materiality, not headline count.
5) For every important development state: what happened -> which companies are affected -> mechanism of impact -> analyst action.
6) Produce a concise industry read and a research queue.

RULES
- Search the web for current information.
- Avoid unsupported numbers. Use null where verification is unavailable.
- Include source URL, publisher, publication date and source type for each material item.
- Do not give buy/sell advice.
- Return JSON matching the schema.
"""


class IndustryAgent:
    def __init__(self, client: GeminiResearchClient):
        self.client = client

    def run(self, companies: List[str]) -> Dict[str, Any]:
        return self.client.research(PROMPT.format(companies=", ".join(companies)), INDUSTRY_SCHEMA)
