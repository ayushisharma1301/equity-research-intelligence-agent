from __future__ import annotations
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient
from llm.tavily_client import TavilyResearchClient, format_results

SCHEMA = {"type":"object"}

PROMPT = """
You are the INDUSTRY INTELLIGENCE AGENT for an institutional equity analyst.
Target company: {company} ({exchange}:{symbol})
Date: {date}

The evidence below was retrieved LIVE immediately before this analysis. Use only that evidence. Do not invent competitors,
news, dates, events or URLs.

IMPORTANT DATA-QUALITY RULES
- Do not output a competitor name unless the evidence contains a concrete relevant development for that company.
- For a diversified company, identify economically relevant peers by business segment and state the segment.
- Every competitor move and every news item must contain a concrete event/development, not only a company name.
- If a category has no evidence, return an empty list rather than placeholder dashes.
- Every material news/competitor item should have a source URL from the supplied evidence.
- Prefer recent evidence; prioritize the last 7 days for news and the last 30 days for material developments.

LIVE SEARCH RESULTS:
{evidence}

TASKS
1) Identify the primary industry and relevant business segments.
2) Identify 3-6 economically relevant competitors with evidence-backed current moves.
3) Cover current company/sector news from the last 7 days and material developments from the last 30 days.
4) Track competitor earnings, capacity/capex, pricing, product moves, M&A, financing, geography, technology and regulation.
5) Track macro signals only when there is a clear transmission mechanism to revenue, margins, capex, financing or valuation.
6) Identify useful industry research/report findings.
7) For every material development explain WHAT HAPPENED -> AFFECTED COMPANIES -> ECONOMIC MECHANISM -> WHAT THE ANALYST SHOULD CHECK NEXT.
8) Rank implications by materiality and novelty.

OUTPUT ONLY JSON with keys:
company, ticker, exchange, industry, as_of, industry_snapshot, competitors, macro_signals, industry_reports, news, implications, research_actions, sources

competitors/news/industry_reports/macro_signals should be lists of objects. Each competitor object should include company, segment, development, why_it_matters, source. Each news object should include title, date, summary, why_it_matters, source.
"""


class IndustryAgent:
    def __init__(self, gemini: GeminiResearchClient, search: TavilyResearchClient):
        self.gemini = gemini
        self.search = search

    def run(self, company: str, exchange: str, symbol: str, date: str) -> Dict[str, Any]:
        q = f'"{company}" "{symbol}" {exchange}'
        searches = [
            {"query": f"{q} industry business segments competitors market share India", "max_results": 6, "search_depth": "advanced", "include_raw_content": True},
            {"query": f"{q} competitors latest earnings capacity capex pricing expansion India", "max_results": 7, "search_depth": "advanced", "include_raw_content": True},
            {"query": f"{q} latest news India sector regulation demand commodity rates FX", "max_results": 8, "topic": "news", "time_range": "week", "search_depth": "advanced", "include_raw_content": True},
            {"query": f"{q} industry report research outlook India latest", "max_results": 5, "search_depth": "advanced", "include_raw_content": True},
        ]
        results = self.search.search_many(searches)
        prompt = PROMPT.format(company=company, exchange=exchange, symbol=symbol, date=date, evidence=format_results(results, 30))
        data = self.gemini.research(prompt, SCHEMA)
        data = data if isinstance(data, dict) else {}
        for key in ["competitors", "macro_signals", "industry_reports", "news", "implications", "research_actions"]:
            if not isinstance(data.get(key), list):
                data[key] = []
        data.setdefault("industry_snapshot", "")
        data.setdefault("sources", [])
        if not isinstance(data["sources"], list):
            data["sources"] = []
        for r in results:
            url = r.get("url")
            if url and not any(isinstance(s, dict) and s.get("url") == url for s in data["sources"]):
                data["sources"].append({"title": r.get("title","Search result"), "url": url, "publisher": url.split('/')[2] if '//' in url else "", "source_type":"Tavily live search"})
        return data
