from __future__ import annotations
from typing import Any, Dict
from llm.gemini_client import GeminiResearchClient

SCHEMA = {
    'type':'object',
    'properties':{
        'company_name':{'type':'string'},
        'exchange':{'type':'string'},
        'symbol':{'type':'string'},
        'isin':{'type':'string'},
        'sector':{'type':'string'},
        'industry':{'type':'string'},
        'confirmation':{'type':'string'},
        'sources':{'type':'array','items':{'type':'object','additionalProperties':True}},
    },
    'required':['company_name','exchange','symbol','sector','industry','confirmation','sources']
}

PROMPT = '''
You are the COMPANY IDENTIFICATION AGENT for an Indian equity-research system.
The user wants to research ONE company listed on NSE or BSE.
User search: {query}
Preferred exchange: {exchange}
Date: {date}

Use fresh Google Search grounding. Resolve the user's search to the exact currently listed company.
Search authoritative Indian market sources first: NSE India, BSE India, the company's investor-relations website, company filings/exchange announcements, and reputable financial sources.

Rules:
- The user may type a company name, partial name, NSE symbol, BSE scrip name/code, or common abbreviation.
- If Preferred exchange is NSE, prefer the NSE-listed security; if BSE, prefer the BSE-listed security.
- Confirm that the security is actually listed on the requested exchange.
- Do not invent a ticker, ISIN, sector or industry.
- If the request is ambiguous, return the best exact match only when evidence is strong; otherwise state the ambiguity in confirmation.
- Return the exchange-specific symbol/scrip identifier that should be used in subsequent research.
- This is not an investment recommendation.

Return strict JSON matching the schema.
'''

class CompanyResolver:
    def __init__(self, client: GeminiResearchClient):
        self.client = client

    def resolve(self, query: str, exchange: str, date: str) -> Dict[str, Any]:
        return self.client.research(PROMPT.format(query=query, exchange=exchange, date=date), SCHEMA)
