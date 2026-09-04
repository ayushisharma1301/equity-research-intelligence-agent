from __future__ import annotations
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient
from analysis.financial_math import enrich_periods

SCHEMA = {
    "type":"object","properties":{
        "company":{"type":"string"},"ticker":{"type":"string"},"as_of":{"type":"string"},"currency":{"type":"string"},
        "latest_period":{"type":"string"},"market_snapshot":{"type":"object","additionalProperties":True},"latest":{"type":"object","additionalProperties":True},
        "periods":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "movements":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "financial_health":{"type":"object","additionalProperties":True},
        "capital_allocation":{"type":"array","items":{"type":"object","additionalProperties":True}},
        "research_actions":{"type":"array","items":{"type":"string"}},
        "sources":{"type":"array","items":{"type":"object","additionalProperties":True}},
    },"required":["company","ticker","as_of","currency","latest_period","market_snapshot","latest","periods","movements","financial_health","capital_allocation","research_actions","sources"]
}

PROMPT = """
You are the FINANCIAL INTELLIGENCE AGENT inside an institutional equity-research workflow.
Company: {ticker}
Date: {date}

You have web search grounding. Perform fresh research now. This is NOT a generic company summary and NOT a static demo.

SOURCE HIERARCHY FOR INDIAN LISTED COMPANIES
1. Company investor-relations website, annual report, quarterly results, results presentation, investor presentation and official earnings-call transcript/webcast materials.
2. NSE India / BSE India corporate announcements and filings, plus SEBI/regulator disclosures where relevant.
3. Reputable financial press and established research/report publishers for context.
For NSE/BSE companies, do not default to SEC sources.
Never invent a number. If a value cannot be verified, return null.

REQUIRED RESEARCH
A) FIRST search for a current market snapshot: latest traded/quoted price, daily change %, market cap and 52-week high/low if verifiable. State the timestamp/source.

B) Retrieve the latest reported quarter and at least 7 comparable historical quarters when available (otherwise use the best available annual/semiannual series). Use REAL REPORTED figures, preserving units and currency.
For each period try to capture: revenue, operating income/EBIT, net income, EPS, CFO, capex, total debt, cash, receivables, inventory, payables, total assets, equity.

C) Calculate/derive locally where possible: revenue growth, operating margin, net margin, CFO conversion, FCF = CFO - capex, net debt, and major working-capital movements. Do not present derived figures as reported figures.

D) Detect meaningful movement versus the company's own history. Specifically look for: margin breaks, cash-flow divergence, working-capital build, leverage change, capex spike, acquisition/asset sale, impairment, restructuring, buyback/dividend change, dilution, unusual tax effects, one-offs and accounting changes.

E) Search for the latest earnings-call transcript, earnings-call summary, management commentary and investor Q&A. Extract evidence-supported explanations for major movements and assess whether management's explanation is consistent with the financial data and other sources. If a full transcript is unavailable, use the best verifiable call summary and label it clearly.

F) Search recent company reports, annual/quarterly reports and investor materials for strategy, segment performance, capacity, order book, guidance and capital-allocation decisions that affect valuation.

G) Give a financial-health score 0-100 with the drivers behind it. This is an analytical score, not an investment rating.

H) Give 3-6 research actions phrased as questions the analyst should investigate next.

SOURCE REQUIREMENT
Every material number, event and management claim must have a source. Include source title, URL, publisher, publication date/as-of date, and source type. Prefer direct primary-source URLs. Use the sources array for traceability.

Return strict JSON matching the schema.
"""

class FinancialAgent:
    def __init__(self, client: GeminiResearchClient): self.client = client
    def run(self, ticker: str, date: str) -> Dict[str, Any]:
        data = self.client.research(PROMPT.format(ticker=ticker, date=date), SCHEMA)
        data["periods"] = enrich_periods(data.get("periods") or [])
        if data["periods"]:
            data["latest"] = {**data["periods"][-1], **(data.get("latest") or {})}
        return data
