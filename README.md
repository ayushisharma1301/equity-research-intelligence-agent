# Equity Research Intelligence Agent

A zero-budget Streamlit equity-research console built around the Gemini API. It is a complete rebuild of the earlier filing-centric prototype.

## Product promise

**Automate the repetitive research work. Show the analyst the few things worth investigating, why they matter, the evidence behind them, and the next research question.**

The system has three intelligence layers:

1. **Financial Intelligence** — real reported financial-statement numbers, historical movements, margins, FCF, net debt, working capital, anomalies and capital allocation.
2. **Industry Intelligence** — competitor moves, sector news and macro drivers, deduplicated and translated into company impact.
3. **Research Synthesis** — a prioritized daily queue: READ NOW / REVIEW / MONITOR / IGNORE.

## Technology constraint

This project intentionally uses only:
- Gemini API (with Google Search grounding for current public web research)
- Streamlit
- Git/GitHub for source control and deployment

There is **no yfinance, SEC SDK, FRED API, paid news API or proprietary data provider** in the application.

Gemini Search grounding is the data-retrieval layer. Python performs deterministic calculations after Gemini returns the reported values.

## Important data-quality design

The agent is instructed to:
- prefer primary filings, IR releases and official disclosures;
- return `null` instead of inventing an unverified number;
- distinguish reported figures from derived calculations;
- attach source URLs to material facts;
- use historical periods to judge whether a move is unusual.

## Local setup

1. Install Python 3.11+.
2. Create a virtual environment.
3. Install requirements:

```bash
pip install -r requirements.txt
```

4. Set your Gemini API key as an environment variable or Streamlit secret.

For local development, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
WATCHLIST = "AAPL,MSFT,NVDA,JPM,RELIANCE.NS"
MAX_COMPANIES_PER_RUN = "5"
```

5. Run:

```bash
streamlit run app.py
```

## Streamlit Community Cloud

- Push this folder to a new GitHub repository.
- Create a Streamlit Community Cloud app from that repository.
- Main file: `app.py`.
- In the app's settings, add the same secrets shown above.
- Never commit `.streamlit/secrets.toml` or an API key.

## First run

1. Open the app.
2. Confirm the watchlist in the sidebar.
3. Click **Run Full Research Cycle**.
4. Wait while each company is researched.
5. Open Company Intelligence for financial statements and movements.
6. Open Industry Monitor for competitor and sector intelligence.
7. Open Daily Research Brief for the prioritized work queue.

## Free-tier note

Gemini API free-tier availability and quotas can change. A full cycle deliberately requires multiple grounded research calls, so use a small watchlist while developing. Do not schedule automatic polling until you have validated your quota and the quality of the outputs.

## Folder map

```text
equity-research-intelligence-agent/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── agents/
│   ├── financial_agent.py
│   ├── industry_agent.py
│   └── synthesis_agent.py
├── analysis/
│   ├── financial_math.py
│   └── materiality.py
├── data/
│   └── demo_data.py
├── llm/
│   └── gemini_client.py
├── storage/
│   └── state_store.py
└── .streamlit/config.toml
```
