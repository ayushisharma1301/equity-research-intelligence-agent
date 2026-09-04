from __future__ import annotations
from typing import Dict, Any
from llm.gemini_client import GeminiResearchClient
from analysis.financial_math import build_derived_metrics, latest_movements

FINANCIAL_SCHEMA = {
    "type": "object",
    "properties": {
        "company": {"type": "string"},
        "as_of": {"type": "string"},
        "currency": {"type": "string"},
        "periods": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "latest": {"type": "object", "additionalProperties": True},
        "movements": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "financial_health": {"type": "object", "additionalProperties": True},
        "anomalies": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "capital_allocation": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "research_actions": {"type": "array", "items": {"type": "string"}},
        "sources": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
    },
    "required": ["company", "as_of", "currency", "periods", "latest", "movements", "financial_health", "anomalies", "capital_allocation", "research_actions", "sources"],
}

PROMPT = """
You are an institutional equity-research financial intelligence agent. Research the company below using current public web sources. Prefer primary sources: SEC filings/IR filings, annual reports, quarterly results, company investor presentations. Use reputable financial press only for context.

Company/ticker: {ticker}

TASK
Build a compact but numerically useful financial dataset and analyst interpretation. Do NOT write a generic company summary. The output must help an analyst avoid manually reading repetitive financial statements.

1) Retrieve the latest reported quarter/year and at least 7 comparable historical periods where available (prefer quarterly; otherwise annual). Extract REAL reported numbers, not estimates, for: revenue, operating income/EBIT, net income, EPS if available, cash from operations, capital expenditure, total debt, cash, receivables, inventory, payables, total assets, shareholders' equity. Preserve the reporting currency and units.
2) Calculate or report movements: QoQ/YoY revenue growth, operating margin, net margin, CFO conversion versus net income, FCF (CFO minus capex), net debt, working-capital changes, and major capital-allocation moves.
3) Identify unusual changes versus the company's own history. Flag margin breaks, cash-flow divergence, working-capital build, leverage changes, capex spikes, buybacks/dividends, acquisitions, impairments, restructuring, or other material financial decisions.
4) For each important movement, explain the most evidence-supported driver and whether management's explanation is credible based on the sources.
5) Give a 0-100 financial health score and a concise analyst read.
6) Give research actions as questions the analyst should investigate next, not investment advice.

RULES
- Every material number must be traceable to a source in the sources array.
- If a number cannot be verified, use null rather than inventing it.
- Distinguish reported figures from derived calculations.
- Prefer the latest fiscal period; clearly state dates.
- Search the web; do not rely only on model memory.
- Return JSON matching the schema.
"""


class FinancialAgent:
    def __init__(self, client: GeminiResearchClient):
        self.client = client

    def run(self, ticker: str) -> Dict[str, Any]:
        data = self.client.research(PROMPT.format(ticker=ticker), FINANCIAL_SCHEMA)
        periods = data.get("periods") or []
        periods = build_derived_metrics(periods)
        data["periods"] = periods
        if periods:
            data["latest"] = {**periods[-1], **(data.get("latest") or {})}
        # Deterministic local movement calculations supplement Gemini's narrative.
        local_moves = latest_movements(periods)
        if local_moves:
            data["local_movements"] = local_moves
        return data
