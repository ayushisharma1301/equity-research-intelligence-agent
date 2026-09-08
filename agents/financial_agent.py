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

1) Market snapshot: latest NSE/BSE traded price, daily change %, market cap and 52-week high/low if verifiable. Prefer a source updated today. Include source URL and as-of date/time. Never leave price blank if a current market-price search result contains a quoted price.
2) Financial statements: retrieve the latest reported quarter plus the best available historical quarterly/annual series. Aim for at least 8 comparable periods when the sources provide them. For each period extract reported revenue, operating income/EBIT, net income, EPS, CFO, capex, total debt, cash, receivables, inventory, payables, total assets and equity. Preserve units and currency.
3) Derive where possible: revenue growth, operating margin, net margin, CFO conversion, FCF = CFO - capex, net debt, and working-capital movement. Clearly distinguish derived metrics from reported figures.
4) Detect material changes: margin breaks, cash-flow divergence, working-capital build, leverage change, capex spike, acquisitions/assets sales, impairments, restructuring, buybacks/dividends, dilution, unusual tax effects, one-offs and accounting changes.
5) Management: identify the latest earnings call, investor presentation or management commentary found in the evidence. Explain major movements and flag where management commentary is not supported by the financial evidence.
6) Strategy/capital allocation: identify segment performance, capacity/order book/guidance where relevant, capex, M&A, dividends/buybacks and other decisions affecting valuation.
7) Give a financial health score from 0-100 with 3-6 evidence-based drivers.
8) Give 3-6 research questions an analyst should investigate next.
9) management_commentary MUST be a list. Each item must contain topic, comment, source_url when available. If evidence is unavailable, return one item explaining that clearly rather than an empty object.
10) movements MUST be a list. Each item must contain metric, movement, why_it_matters. Use verified changes from the evidence; if none are verified, return one item saying that no material movement was verifiable rather than an empty list.

OUTPUT FORMAT
Return ONLY one JSON object with exactly these top-level keys:
company, ticker, exchange, as_of, currency, latest_period, market_snapshot, latest, periods, movements, financial_health, capital_allocation, research_actions, management_commentary, sources

periods must be a list of objects. If quarterly data are available in tables, extract the numeric values and units rather than returning prose. For RIL, recognize reported PAT, EBITDA and segment metrics where EBIT is unavailable. sources must contain title, url, publisher, publication_date/as_of and source_type where available. Never fabricate a source URL.
"""


class FinancialAgent:
    def __init__(self, gemini: GeminiResearchClient, search: TavilyResearchClient):
        self.gemini = gemini
        self.search = search

    def run(self, company: str, exchange: str, symbol: str, date: str) -> Dict[str, Any]:
        q = f"{company} {symbol} {exchange}"
        searches = [
            {"query": f"{q} latest quarterly results revenue EBITDA PAT CFO capex investor presentation 2026", "max_results": 8, "include_domains": ["ril.com"] if "reliance" in company.lower() else None},
            {"query": f"{q} historical quarterly results FY 2026 FY 2025 FY 2024 financial statements revenue EBITDA PAT cash flow", "max_results": 8},
            {"query": f"{q} latest earnings call management commentary guidance capex dividend buyback investor presentation transcript", "max_results": 8, "include_domains": ["ril.com"] if "reliance" in company.lower() else None},
            {"query": f"{q} NSE share price today 8 September 2026 live current price day change market cap 52 week high low", "max_results": 8, "topic": "news", "time_range": "day"},
            {"query": f"{q} annual report financial highlights consolidated revenue EBITDA profit cash flow debt cash receivables inventory", "max_results": 7},
        ]
        searches = [{k: v for k, v in spec.items() if v is not None} for spec in searches]
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

        # Defensive live-price fallback: if Gemini did not populate price,
        # recover a clearly quoted current price from the live search text.
        ms = data.get("market_snapshot") if isinstance(data.get("market_snapshot"), dict) else {}
        import re
        if not ms.get("price"):
            price_patterns = [
                r"(?:₹|Rs\.?|INR)\s*([0-9][0-9,]*(?:\.\d+)?)",
                r"(?:price|trading at|last traded|LTP)[^₹0-9]{0,30}(?:₹|Rs\.?|INR)?\s*([0-9][0-9,]*(?:\.\d+)?)",
            ]
            for r in results:
                text = " ".join([(r.get("title") or ""), (r.get("content") or ""), (r.get("raw_content") or "")])
                found = None
                for pat in price_patterns:
                    m = re.search(pat, text, re.I)
                    if m:
                        try:
                            found = float(m.group(1).replace(",", ""))
                            break
                        except ValueError:
                            pass
                if found and 50 <= found <= 100000:
                    ms["price"] = found
                    ms["price_source"] = r.get("url")
                    ms["price_as_of"] = date
                    break
        data["market_snapshot"] = ms
        if not isinstance(data.get("management_commentary"), list):
            mc = data.get("management_commentary")
            data["management_commentary"] = [{"topic":"Management commentary", "comment": str(mc) if mc else "No management commentary was verifiable from the retrieved evidence.", "source_url":""}]
        if not isinstance(data.get("movements"), list):
            data["movements"] = [{"metric":"Financial movement", "movement":"No material movement was returned in structured form.", "why_it_matters":"Review the latest reported period against the historical financial evidence."}]
        return data
