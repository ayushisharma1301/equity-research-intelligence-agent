# Architecture

## Dynamic flow

1. **Company Resolver** — accepts arbitrary NSE/BSE input and uses live search to resolve the requested security.
2. **Financial Agent** — runs targeted live searches for financial statements, historical results, earnings calls, management commentary and market snapshot; Gemini analyzes the evidence.
3. **Industry Agent** — runs live searches for competitors, current sector news, reports and macro drivers; Gemini analyzes the evidence.
4. **Synthesis Agent** — combines both packs and creates READ NOW / REVIEW / MONITOR / IGNORE priorities.
5. **Streamlit** — renders the resulting evidence, metrics, movements, industry intelligence and source room.

## Separation of concerns

- **Tavily:** retrieval and source discovery.
- **Gemini:** reasoning, extraction, interpretation and prioritization.
- **Local Python:** simple derived financial calculations and presentation.
- **Streamlit:** user interaction and dashboard.

There is no static watchlist and no fixed company universe.
