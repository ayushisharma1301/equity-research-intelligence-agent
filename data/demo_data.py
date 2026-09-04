from __future__ import annotations
from datetime import datetime

DEMO = {
    "generated_at": datetime.now().strftime("%d %b %Y, %H:%M"),
    "market_ticker": [
        {"label": "SYSTEM", "value": "DEMO MODE", "delta": ""},
        {"label": "Coverage", "value": "5 companies", "delta": ""},
        {"label": "Financial", "value": "Ready", "delta": ""},
        {"label": "Industry", "value": "Ready", "delta": ""},
        {"label": "Sources", "value": "Gemini Search", "delta": ""},
    ],
    "actions": [
        {"priority": "READ NOW", "company_or_sector": "AAPL", "development": "Run live analysis to populate", "why_it_matters": "Demo state only", "action": "Click Run Research", "confidence": 0},
        {"priority": "REVIEW", "company_or_sector": "Industry", "development": "Live competitor and macro scan pending", "why_it_matters": "Demo state only", "action": "Run Industry Scan", "confidence": 0},
        {"priority": "MONITOR", "company_or_sector": "Watchlist", "development": "No live snapshot yet", "why_it_matters": "Demo state only", "action": "Run Research", "confidence": 0},
    ],
}
