from __future__ import annotations
import json
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient

SCHEMA = {"type":"object","properties":{
    "verdict":{"type":"string"},"confidence":{"type":"integer"},"executive_summary":{"type":"string"},
    "actions":{"type":"array","items":{"type":"object","additionalProperties":True}},
    "top_three":{"type":"array","items":{"type":"string"}},"watch_next":{"type":"array","items":{"type":"string"}}
},"required":["verdict","confidence","executive_summary","actions","top_three","watch_next"]}

PROMPT = """
You are the SENIOR EQUITY-RESEARCH SYNTHESIS AGENT.
Target: {ticker}

Below are two fresh research packs produced from web-grounded research.
FINANCIAL PACK:
{financial}
INDUSTRY PACK:
{industry}

Your job is to turn them into an analyst work queue. Do not repeat everything.
Prioritize changes that could alter earnings power, cash generation, balance-sheet risk, competitive position, valuation assumptions or management credibility.

For each action use exactly one priority: READ NOW, REVIEW, MONITOR, IGNORE.
Each action should contain: priority, title, evidence, why_it_matters, analyst_question, confidence (0-100).
Do not issue a buy/sell recommendation. This is research prioritization.

Return strict JSON matching the schema.
"""

class SynthesisAgent:
    def __init__(self, client: GeminiResearchClient): self.client = client
    def run(self, ticker: str, financial: Dict[str,Any], industry: Dict[str,Any]) -> Dict[str,Any]:
        return self.client.research(PROMPT.format(ticker=ticker, financial=json.dumps(financial)[:50000], industry=json.dumps(industry)[:40000]), SCHEMA)
