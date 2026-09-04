from __future__ import annotations
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient
from llm.tavily_client import TavilyResearchClient, format_results

SCHEMA = {"type":"object"}

PROMPT = """
You are the INDUSTRY INTELLIGENCE AGENT for an institutional equity analyst.
Target company: {company} ({exchange}:{symbol})
Date: {date}

The following results were retrieved LIVE from the web immediately before this analysis. Do not use a static company universe. Identify the actual industry and competitors from the evidence.

LIVE SEARCH RESULTS:
{evidence}

TASKS
1) Identify the primary industry and 3-6 economically relevant competitors.
2) Cover current news from the last 7 days and material developments from the last 30 days. Separate company-specific news from sector-wide news.
3) Track competitor earnings, capacity/capex, pricing, product moves, M&A, financing, geography, technology, regulation and other competitive changes.
4) Track macro signals only when there is a clear transmission mechanism to revenue, margins, capex, financing or valuation.
5) Identify useful industry research/report findings.
6) Deduplicate repeated headlines.
7) For every material development explain WHAT HAPPENED -> AFFECTED COMPANIES -> ECONOMIC MECHANISM -> WHAT THE ANALYST SHOULD CHECK NEXT.
8) Rank implications by materiality and novelty.

OUTPUT ONLY JSON with keys:
company, ticker, exchange, industry, as_of, industry_snapshot, competitors, macro_signals, industry_reports, news, implications, research_actions, sources

Do not issue buy/sell recommendations. Never invent current facts or URLs.
"""


class IndustryAgent:
    def __init__(self, gemini: GeminiResearchClient, search: TavilyResearchClient):
        self.gemini = gemini
        self.search = search

    def run(self, company: str, exchange: str, symbol: str, date: str) -> Dict[str, Any]:
        q = f"{company} {symbol} {exchange}"
        searches = [
            {"query": f"{q} industry competitors market share sector India", "max_results": 7},
            {"query": f"{q} competitors latest earnings capacity capex pricing expansion India", "max_results": 8},
            {"query": f"{q} sector industry latest news India regulation demand commodity rates FX", "max_results": 8, "topic": "news", "time_range": "week"},
            {"query": f"{q} industry report research outlook India latest", "max_results": 6},
        ]
        results = self.search.search_many(searches)
        prompt = PROMPT.format(company=company, exchange=exchange, symbol=symbol, date=date, evidence=format_results(results, 32))
        data = self.gemini.research(prompt, SCHEMA)
        data.setdefault("sources", [])
        for r in results:
            url = r.get("url")
            if url and not any(s.get("url") == url for s in data["sources"] if isinstance(s, dict)):
                data["sources"].append({"title": r.get("title","Search result"), "url": url, "publisher": url.split('/')[2], "source_type":"Tavily live search"})
        return data
