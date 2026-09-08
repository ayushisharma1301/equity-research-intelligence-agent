from __future__ import annotations
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient
from llm.tavily_client import TavilyResearchClient, format_results

SCHEMA = {"type":"object"}

PROMPT = """
You are the INDUSTRY INTELLIGENCE AGENT for an institutional equity analyst.
Target company: {company} ({exchange}:{symbol})
Date: {date}

The following results were retrieved LIVE from the web immediately before this analysis. Do not use a static company universe. Identify the actual business model, primary industry and economically relevant competitor set from the evidence. For diversified companies, do NOT force the company into a single manufacturing/industrial category; represent the company as diversified and identify competitors by material business segment.

LIVE SEARCH RESULTS:
{evidence}

TASKS
1) Identify the primary industry and 3-6 economically relevant competitors. If the company is diversified, say "Diversified conglomerate" and group competitors by major segment (for RIL, consider Jio, Retail, O2C, New Energy and Media rather than inventing one narrow industry).
2) Cover current news from the last 7 days and material developments from the last 30 days. Separate company-specific news from sector-wide news.
3) Track competitor earnings, capacity/capex, pricing, product moves, M&A, financing, geography, technology, regulation and other competitive changes.
4) Track macro signals only when there is a clear transmission mechanism to revenue, margins, capex, financing or valuation.
5) Identify useful industry research/report findings.
6) Deduplicate repeated headlines.
7) For every material development explain WHAT HAPPENED -> AFFECTED COMPANIES -> ECONOMIC MECHANISM -> WHAT THE ANALYST SHOULD CHECK NEXT.
8) Rank implications by materiality and novelty.

OUTPUT ONLY JSON with keys:
company, ticker, exchange, industry, as_of, industry_snapshot, competitors, macro_signals, industry_reports, news, implications, research_actions, sources

Do not issue buy/sell recommendations. Never invent current facts or URLs. Never output a competitor with an empty development field: if no current evidence exists, omit that competitor. Never output an empty macro signal; omit it instead.
"""


class IndustryAgent:
    def __init__(self, gemini: GeminiResearchClient, search: TavilyResearchClient):
        self.gemini = gemini
        self.search = search

    def run(self, company: str, exchange: str, symbol: str, date: str) -> Dict[str, Any]:
        q = f"{company} {symbol} {exchange}"
        searches = [
            {"query": f"{q} business segments industry competitors market share India", "max_results": 8},
            {"query": f"{q} competitors latest earnings capacity capex pricing expansion India", "max_results": 8},
            {"query": f"{q} latest news competitors strategy expansion India", "max_results": 8, "topic": "news", "time_range": "week"},
            {"query": f"{q} industry report research outlook India latest", "max_results": 7},
            {"query": f"{q} investor presentation business segments Jio Retail O2C new energy competitors", "max_results": 7, "include_domains": ["ril.com"] if "reliance" in company.lower() else None},
            {"query": f"{q} sector macro crude oil telecom retail consumer energy India current", "max_results": 7, "topic": "news", "time_range": "week"},
        ]
        searches = [{k: v for k, v in spec.items() if v is not None} for spec in searches]
        results = self.search.search_many(searches)
        prompt = PROMPT.format(company=company, exchange=exchange, symbol=symbol, date=date, evidence=format_results(results, 32))
        data = self.gemini.research(prompt, SCHEMA)
        data.setdefault("sources", [])
        for r in results:
            url = r.get("url")
            if url and not any(s.get("url") == url for s in data["sources"] if isinstance(s, dict)):
                data["sources"].append({"title": r.get("title","Search result"), "url": url, "publisher": url.split('/')[2], "source_type":"Tavily live search"})
        return data
