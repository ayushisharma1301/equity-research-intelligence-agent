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
9) IMPORTANT: competitors are required even when there is no recent news. Return 3-6 listed competitors with company, segment, symbol/exchange if known. A competitor may have development = \"No material verified development in the current window\". Do NOT omit the competitor merely because news is unavailable.
10) Current competitor market data are required where available: latest share price, daily change %, market cap, price_as_of and source_url. Never invent numbers.

OUTPUT ONLY JSON with keys:
company, ticker, exchange, industry, as_of, industry_snapshot, competitors, macro_signals, industry_reports, news, implications, research_actions, sources

Do not issue buy/sell recommendations. Never invent current facts or URLs. Never invent a competitor or a market number. If no current development exists, explicitly use \"No material verified development in the current window\". Competitor identity and market data should still be returned when supported. Never output an empty macro signal; omit it instead.
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

        # Normalize AI output before it reaches the dashboard. Competitor identity
        # must survive even when there is no current news. Market data are enriched
        # separately from fresh Tavily searches below.
        def clean_dict_list(value):
            if not isinstance(value, list):
                return []
            return [x for x in value if isinstance(x, dict)]

        competitors = clean_dict_list(data.get("competitors"))
        normalized_competitors = []
        for x in competitors:
            name = str(x.get("company", x.get("name", ""))).strip()
            if not name:
                continue
            development = str(x.get("development", x.get("move", ""))).strip()
            if not development or development.lower() in {"no verified development", "no verified development.", "—", "-"}:
                development = "No material verified development in the current window."
            x["company"] = name
            x["development"] = development
            normalized_competitors.append(x)
        data["competitors"] = normalized_competitors[:6]
        # Enrich each competitor with current market data. This runs even when
        # there is no competitor news, because the dashboard should always provide
        # a live peer-set snapshot.
        import re
        competitor_specs = []
        for x in data["competitors"][:6]:
            name = x.get("company", "")
            competitor_specs.append({
                "query": f"{name} NSE BSE share price today current price market cap daily change September 2026",
                "max_results": 4,
                "topic": "news",
                "time_range": "day",
            })
        if competitor_specs:
            peer_results = self.search.search_many(competitor_specs)
        else:
            peer_results = []

        def extract_market_fields(items):
            best = None
            for r in items:
                text = " ".join([str(r.get("title") or ""), str(r.get("content") or ""), str(r.get("raw_content") or "")])
                lower = text.lower()
                price = None
                for pat in [
                    r"(?:₹|rs\.?|inr)\s*([0-9][0-9,]*(?:\.\d+)?)",
                    r"(?:share price|stock price|trading at|last traded|ltp)[^₹0-9]{0,40}(?:₹|rs\.?|inr)?\s*([0-9][0-9,]*(?:\.\d+)?)",
                ]:
                    m = re.search(pat, text, re.I)
                    if m:
                        try:
                            v = float(m.group(1).replace(",", ""))
                            if 1 <= v <= 100000:
                                price = v
                                break
                        except ValueError:
                            pass
                market_cap = None
                for pat in [
                    r"(?:market cap|market capitalization|m[- ]?cap)[^₹0-9]{0,50}(?:₹|rs\.?|inr)?\s*([0-9][0-9,]*(?:\.\d+)?)\s*(lakh crore|crore|cr|bn|billion|trillion)?",
                    r"(?:₹|rs\.?|inr)\s*([0-9][0-9,]*(?:\.\d+)?)\s*(lakh crore|crore|cr|bn|billion|trillion)[^\n]{0,30}(?:market cap|market capitalization)",
                ]:
                    m = re.search(pat, text, re.I)
                    if m:
                        try:
                            n = float(m.group(1).replace(",", ""))
                            unit = (m.group(2) or "").lower()
                            if unit in {"crore", "cr"}:
                                market_cap = f"₹{n:,.0f} Cr"
                            elif unit == "lakh crore":
                                market_cap = f"₹{n:,.2f} Lakh Cr"
                            else:
                                market_cap = f"{n:,.2f} {unit.title()}"
                            break
                        except ValueError:
                            pass
                change = None
                m = re.search(r"(?:down|fell|declined|up|gained|rose|change|change of)[^%\d-]{0,20}(-?\d+(?:\.\d+)?)%", lower, re.I)
                if m:
                    try:
                        change = float(m.group(1))
                        if any(w in lower for w in ["down", "fell", "declined"]):
                            change = -abs(change)
                    except ValueError:
                        pass
                if price is not None or market_cap is not None:
                    best = {"price": price, "market_cap": market_cap, "daily_change_pct": change, "source_url": r.get("url"), "as_of": date}
                    break
            return best or {}

        # Map search results back to competitors using name tokens.
        for x in data["competitors"]:
            name = x.get("company", "")
            name_tokens = [t.lower() for t in re.findall(r"[A-Za-z0-9]+", name) if len(t) >= 4]
            candidates = []
            for r in peer_results:
                hay = (str(r.get("title") or "") + " " + str(r.get("content") or "")).lower()
                if not name_tokens or sum(t in hay for t in name_tokens) >= max(1, min(2, len(name_tokens))):
                    candidates.append(r)
            fields = extract_market_fields(candidates or peer_results[:4])
            x.update({k: v for k, v in fields.items() if v is not None})

        data["macro_signals"] = [
            x for x in clean_dict_list(data.get("macro_signals"))
            if str(x.get("implication", x.get("why_it_matters", ""))).strip()
        ]
        data["industry_reports"] = [
            x for x in clean_dict_list(data.get("industry_reports"))
            if str(x.get("finding", x.get("summary", ""))).strip()
        ]
        data["news"] = clean_dict_list(data.get("news"))
        data.setdefault("sources", [])
        for r in results:
            url = r.get("url")
            if url and not any(s.get("url") == url for s in data["sources"] if isinstance(s, dict)):
                data["sources"].append({"title": r.get("title","Search result"), "url": url, "publisher": url.split('/')[2], "source_type":"Tavily live search"})
        return data
