from __future__ import annotations
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

The evidence below was retrieved LIVE immediately before this request. Prefer official company/exchange documents and
reported figures over secondary commentary. Use ONLY the supplied evidence. Never invent a number.

IMPORTANT DATA-QUALITY RULES
- If a figure is present in the evidence, extract it into the requested field even if other fields are unavailable.
- Preserve the reported unit and currency. For Indian company reports, figures are commonly ₹ crore.
- Use the latest reported quarter as latest_period.
- Do not leave the entire financial pack empty just because one field is missing.
- periods should contain every comparable period you can verify from the evidence; 4-8 periods is acceptable.
- latest must contain the latest verified period's values.
- market_snapshot should be populated from evidence when available.
- management_commentary must contain actual management statements/findings when the evidence contains an earnings call, presentation or press release; otherwise explain exactly what was unavailable.
- sources must point to the URLs actually supplied in the evidence.

LIVE SEARCH RESULTS:
{evidence}

RESEARCH OBJECTIVE
1) Market snapshot: latest price, daily change %, market cap and 52-week high/low if verifiable.
2) Financial statements: latest quarter plus historical quarterly/annual series. Extract revenue, operating income/EBIT or EBITDA when that is what is reported, net income/PAT, EPS, CFO, capex, debt, cash, receivables, inventory, payables, assets and equity where available.
3) Derive revenue growth, operating margin, net margin, CFO conversion, FCF, net debt and working capital only when inputs are available.
4) Detect margin breaks, cash-flow divergence, working-capital build, leverage changes, capex spikes, acquisitions, disposals, impairments, restructuring, dividends, buybacks, dilution, tax effects and one-offs.
5) Summarize latest management commentary and guidance from the supplied evidence.
6) Identify strategy/capital-allocation developments.
7) Score financial health 0-100 with 3-6 evidence-based drivers.
8) Give 3-6 analyst research questions.

OUTPUT ONLY ONE JSON OBJECT with exactly these top-level keys:
company, ticker, exchange, as_of, currency, latest_period, market_snapshot, latest, periods, movements, financial_health, capital_allocation, research_actions, management_commentary, sources

periods: list of objects with period plus any verified metrics.
management_commentary: list of objects with topic, comment, source where possible.
sources: list of objects with title, url, publisher, publication_date/as_of and source_type where available.
"""


class FinancialAgent:
    def __init__(self, gemini: GeminiResearchClient, search: TavilyResearchClient):
        self.gemini = gemini
        self.search = search

    def run(self, company: str, exchange: str, symbol: str, date: str) -> Dict[str, Any]:
        q = f'"{company}" "{symbol}" {exchange}'
        searches = [
            {"query": f"{q} latest quarterly results revenue EBITDA PAT net profit CFO capex", "max_results": 6, "search_depth": "advanced", "include_raw_content": True},
            {"query": f"{q} latest investor presentation financial results quarterly", "max_results": 5, "search_depth": "advanced", "include_raw_content": True, "include_domains": ["ril.com", "nseindia.com", "bseindia.com"]},
            {"query": f"{q} historical quarterly results FY2026 FY2025 FY2024 revenue profit cash flow", "max_results": 6, "search_depth": "advanced", "include_raw_content": True},
            {"query": f"{q} earnings call management commentary guidance capex dividend buyback", "max_results": 6, "search_depth": "advanced", "include_raw_content": True},
            {"query": f"{q} share price market cap 52 week high low latest", "max_results": 5, "search_depth": "basic"},
        ]
        # Remove RIL-only domain targeting for other companies while retaining the dynamic query.
        if symbol.upper() != "RELIANCE":
            searches[1]["include_domains"] = ["nseindia.com", "bseindia.com"]

        results = self.search.search_many(searches)
        prompt = PROMPT.format(company=company, exchange=exchange, symbol=symbol, date=date, evidence=format_results(results, 28))
        data = self.gemini.research(prompt, SCHEMA)
        data = data if isinstance(data, dict) else {}
        periods = data.get("periods") if isinstance(data.get("periods"), list) else []
        data["periods"] = enrich_periods(periods)
        if data["periods"]:
            data["latest"] = {**data["periods"][-1], **(data.get("latest") or {})}
        data.setdefault("latest", {})
        data.setdefault("market_snapshot", {})
        data.setdefault("financial_health", {})
        data.setdefault("capital_allocation", [])
        data.setdefault("management_commentary", [])
        data.setdefault("research_actions", [])
        data.setdefault("sources", [])
        existing = data["sources"] if isinstance(data["sources"], list) else []
        data["sources"] = existing
        for r in results:
            url = r.get("url")
            if url and not any(isinstance(s, dict) and s.get("url") == url for s in data["sources"]):
                data["sources"].append({"title": r.get("title","Search result"), "url": url, "publisher": url.split('/')[2] if '//' in url else "", "source_type":"Tavily live search"})
        return data
