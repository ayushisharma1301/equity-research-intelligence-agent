from __future__ import annotations
import json
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient
from llm.tavily_client import TavilyResearchClient, format_results
from analysis.financial_math import enrich_periods

SCHEMA = {"type":"object"}

PROMPT = """
You are the FINANCIAL INTELLIGENCE AGENT in an institutional equity-research workflow for an Indian listed company.
Company: {company}
Exchange: {exchange}
Symbol/scrip: {symbol}
Date: {date}

You are given LIVE WEB SEARCH RESULTS collected immediately before this request. Use only evidence contained in those results or clearly label a field as unavailable. Do not invent numbers.

LIVE SEARCH RESULTS:
{evidence}

RESEARCH OBJECTIVE
Build a decision-useful financial research pack, not a generic company description.

1) Market snapshot: latest price, daily change %, market cap and 52-week high/low if verifiable. Include the source URL and as-of date/time when available.
2) Financial statements: retrieve the latest reported quarter plus the best available historical quarterly/annual series. Aim for at least 8 comparable periods when the sources provide them. For each period extract reported revenue, operating income/EBIT, net income, EPS, CFO, capex, total debt, cash, receivables, inventory, payables, total assets and equity. Preserve units and currency.
3) Derive where possible: revenue growth, operating margin, net margin, CFO conversion, FCF = CFO - capex, net debt, and working-capital movement. Clearly distinguish derived metrics from reported figures.
4) Detect material changes: margin breaks, cash-flow divergence, working-capital build, leverage change, capex spike, acquisitions/assets sales, impairments, restructuring, buybacks/dividends, dilution, unusual tax effects, one-offs and accounting changes.
5) Management: identify the latest earnings call, investor presentation or management commentary found in the evidence. Explain major movements and flag where management commentary is not supported by the financial evidence.
6) Strategy/capital allocation: identify segment performance, capacity/order book/guidance where relevant, capex, M&A, dividends/buybacks and other decisions affecting valuation.
7) Give a financial health score from 0-100 with 3-6 evidence-based drivers.
8) Give 3-6 research questions an analyst should investigate next.

OUTPUT FORMAT
Return ONLY one JSON object with exactly these top-level keys:
company, ticker, exchange, as_of, currency, latest_period, market_snapshot, latest, periods, movements, financial_health, capital_allocation, research_actions, management_commentary, sources

periods must be a list of objects. sources must contain title, url, publisher, publication_date/as_of and source_type where available. Never fabricate a source URL.
"""


class FinancialAgent:
    def __init__(self, gemini: GeminiResearchClient, search: TavilyResearchClient):
        self.gemini = gemini
        self.search = search

    def run(self, company: str, exchange: str, symbol: str, date: str) -> Dict[str, Any]:
        q = f"{company} {symbol} {exchange}"
        searches = [
            {"query": f"{q} latest quarterly results revenue profit cash flow annual report investor presentation", "max_results": 8},
            {"query": f"{q} historical quarterly results FY 2026 FY 2025 FY 2024 financial statements", "max_results": 8},
            {"query": f"{q} latest earnings call management commentary guidance capex dividend buyback", "max_results": 7},
            {"query": f"{q} share price market cap 52 week high low latest", "max_results": 6},
        ]
        results = self.search.search_many(searches)
        prompt = PROMPT.format(company=company, exchange=exchange, symbol=symbol, date=date, evidence=format_results(results, 30))
        data = self.gemini.research(prompt, SCHEMA)
        data["periods"] = enrich_periods(data.get("periods") or [])
        if data["periods"]:
            data["latest"] = {**data["periods"][-1], **(data.get("latest") or {})}
        data.setdefault("sources", [])
        for r in results:
            url = r.get("url")
            if url and not any(s.get("url") == url for s in data["sources"] if isinstance(s, dict)):
                data["sources"].append({"title": r.get("title","Search result"), "url": url, "publisher": url.split('/')[2], "source_type":"Tavily live search"})
        return data
