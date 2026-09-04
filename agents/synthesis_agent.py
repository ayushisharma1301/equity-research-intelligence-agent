from __future__ import annotations
import json
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient

SCHEMA = {"type":"object"}

PROMPT = """
You are the SENIOR EQUITY-RESEARCH SYNTHESIS AGENT.
Target: {ticker}

FINANCIAL AGENT PACK:
{financial}

INDUSTRY AGENT PACK:
{industry}

Turn these fresh research packs into a concise analyst work queue. Prioritize changes that could alter earnings power, cash generation, balance-sheet risk, competitive position, valuation assumptions or management credibility.

Each action must use exactly one priority: READ NOW, REVIEW, MONITOR, or IGNORE. Include priority, title, evidence, why_it_matters, analyst_question, confidence (0-100).

Return ONLY JSON with keys: verdict, confidence, executive_summary, actions, top_three, watch_next.
Do not issue a buy/sell recommendation.
"""


class SynthesisAgent:
    def __init__(self, gemini: GeminiResearchClient):
        self.gemini = gemini

    def run(self, ticker: str, financial: Dict[str, Any], industry: Dict[str, Any]) -> Dict[str, Any]:
        prompt = PROMPT.format(
            ticker=ticker,
            financial=json.dumps(financial, ensure_ascii=False)[:60000],
            industry=json.dumps(industry, ensure_ascii=False)[:50000],
        )
        return self.gemini.research(prompt, SCHEMA)
