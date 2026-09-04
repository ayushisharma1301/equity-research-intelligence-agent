from __future__ import annotations
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient

SCHEMA = {
    "type":"object","properties":{
        "company":{"type":"string"},"ticker":{"type":"string"},"industry":{"type":"string"},"as_of":{"type":"string"},
        "industry_snapshot":{"type":"string"},"competitors":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "macro_signals":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "industry_reports":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "news":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "implications":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "research_actions":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","additionalProperties":True}}
    },"required":["company","ticker","industry","as_of","industry_snapshot","competitors","macro_signals","industry_reports","news","implications","research_actions","sources"]
}

PROMPT = """
You are the INDUSTRY INTELLIGENCE AGENT for an institutional equity analyst.
Target company/ticker: {ticker}
Date: {date}

Perform a fresh, company-specific industry scan using web search grounding. Do not use a static dataset.

1. Identify the company's actual primary industry in India and the 3-6 competitors that most directly matter to its economics. Use NSE/BSE classifications and company disclosures where available.
2. Search the last 72 hours for material news affecting the company or its industry. Also search the last 30 days for important developments that remain economically relevant.
3. Search competitor disclosures, NSE/BSE announcements, earnings releases, investor presentations, annual reports, capacity/capex announcements, pricing commentary, product moves, M&A, financing, geographic expansion, layoffs/hiring, technology and regulatory developments.
4. Search reputable industry research/report sources and summarize the most decision-useful recent findings.
5. Track macro signals relevant to the economics of the company: rates, inflation, commodities, FX, demand, regulation, supply chain, etc. Only include signals with a clear transmission mechanism.
6. Deduplicate stories. A repeated headline is one development, not five.
7. For each material development explain: WHAT HAPPENED -> AFFECTED COMPANIES -> ECONOMIC MECHANISM -> WHAT AN EQUITY ANALYST SHOULD CHECK NEXT.
8. Rank implications by materiality and novelty.

SOURCE RULES
Use primary company/regulator sources where possible, then high-quality industry research and reputable news. Include URL, title, publisher, publication date and source type for every material item. Do not invent current prices, dates or statistics.

Return strict JSON matching the schema. No buy/sell recommendation.
"""

class IndustryAgent:
    def __init__(self, client: GeminiResearchClient): self.client = client
    def run(self, ticker: str, date: str) -> Dict[str, Any]:
        return self.client.research(PROMPT.format(ticker=ticker, date=date), SCHEMA)
