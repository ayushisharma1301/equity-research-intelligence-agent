from __future__ import annotations
import re
from typing import Any, Dict
from llm.tavily_client import TavilyResearchClient


def _clean_name(query: str) -> str:
    q = re.sub(r"\s+", " ", query.strip())
    return q.title() if q.isupper() else q


def _first_symbol(results: list[dict[str, Any]], exchange: str, query: str) -> str:
    # Prefer explicit exchange labels / symbol fields in search snippets.
    for r in results:
        text = f"{r.get('title','')} {r.get('content','')}".upper()
        patterns = [
            r"NSE\s*(?:SYMBOL|CODE|TICKER)?\s*[:=-]\s*([A-Z][A-Z0-9&.-]{1,20})",
            r"SYMBOL\s*[:=-]\s*([A-Z][A-Z0-9&.-]{1,20})",
            r"BSE\s*(?:CODE|SCRIP)?\s*[:=-]\s*(\d{4,7})",
            r"SCRIP\s*(?:CODE|ID)?\s*[:=-]\s*(\d{4,7})",
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1).strip(" .")
    # Common input is already a symbol/scrip.
    q = query.strip().upper()
    if exchange == "NSE" and re.fullmatch(r"[A-Z][A-Z0-9&.-]{1,15}", q):
        return q
    if exchange == "BSE" and re.fullmatch(r"\d{4,7}", q):
        return q
    return ""


class CompanyResolver:
    """Resolve an arbitrary NSE/BSE query using live exchange-focused search."""

    def __init__(self, search_client: TavilyResearchClient):
        self.search = search_client

    def resolve(self, query: str, exchange: str, date: str) -> Dict[str, Any]:
        if not query.strip():
            raise RuntimeError("Enter a company name, NSE symbol or BSE scrip first.")

        domains = ["nseindia.com"] if exchange == "NSE" else ["bseindia.com"]
        results = self.search.search_many([
            {
                "query": f"{query} {exchange} listed company symbol scrip {date}",
                "max_results": 6,
                "include_domains": domains,
            },
            {
                "query": f"{query} {exchange} company investor relations stock",
                "max_results": 5,
            },
        ])
        symbol = _first_symbol(results, exchange, query)
        top = results[0] if results else {}
        title = top.get("title") or ""
        company_name = re.sub(r"\s*[-|].*$", "", title).strip() or _clean_name(query)
        # Avoid treating generic exchange pages as company names.
        if len(company_name) < 3 or company_name.lower() in {"nse india", "bse india"}:
            company_name = _clean_name(query)

        sources = [
            {
                "title": r.get("title") or "Search result",
                "url": r.get("url") or "",
                "publisher": (r.get("url") or "").split("/")[2] if r.get("url") else "",
                "source_type": "live web search",
                "publication_date": "",
            }
            for r in results if r.get("url")
        ]
        return {
            "company_name": company_name,
            "exchange": exchange,
            "symbol": symbol or query.strip().upper(),
            "isin": "",
            "sector": "",
            "industry": "",
            "confirmation": (
                f"Resolved from live {exchange} and web search. Verify the exchange identifier shown "
                "against the source room if the input was ambiguous."
            ),
            "sources": sources,
            "resolver_results": results[:10],
        }
