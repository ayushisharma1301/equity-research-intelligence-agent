from __future__ import annotations
import json
from typing import Dict, Any
from llm.gemini_client import GeminiResearchClient

SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "daily_read": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "top_three": {"type": "array", "items": {"type": "string"}},
        "watch_next": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["daily_read", "actions", "top_three", "watch_next"],
}

PROMPT = """
You are the senior research triage layer of an equity-research intelligence system. Convert the financial and industry research below into a concise analyst work queue.

FINANCIAL RESEARCH:
{financial}

INDUSTRY RESEARCH:
{industry}

Create:
- daily_read: 2-4 sentences describing the most important cross-company/sector change.
- actions: rank up to 8 items. Each must contain priority (READ NOW/REVIEW/MONITOR/IGNORE), company_or_sector, development, why_it_matters, action, confidence (0-100).
- top_three: exactly three short items an analyst should know today.
- watch_next: 3-5 concrete signals/data points that would change the current read.

Rules: prioritize materiality and novelty; do not simply repeat headlines; do not provide buy/sell recommendations; distinguish fact from inference; never invent missing numbers.
Return JSON.
"""


class SynthesisAgent:
    def __init__(self, client: GeminiResearchClient):
        self.client = client

    def run(self, financial: Dict[str, Any], industry: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.research(PROMPT.format(financial=json.dumps(financial)[:40000], industry=json.dumps(industry)[:40000]), SYNTHESIS_SCHEMA)
