# Equity Research Intelligence Agent

A dynamic, live-web equity research workflow for **any NSE or BSE listed company**.

## What makes it dynamic
- No hard-coded company universe.
- User selects NSE or BSE and types any company name, symbol or BSE scrip.
- Tavily retrieves fresh public web evidence at run time.
- Gemini analyzes that evidence through separate Financial, Industry and Synthesis agents.
- Switching companies triggers a new research cycle.

## Architecture

```text
User -> NSE/BSE Company Resolver -> Financial Agent
                                  -> Industry Agent
                                  -> Synthesis Agent
                                  -> Streamlit Dashboard

Tavily = live web retrieval
Gemini = reasoning / analysis
```

## Required secrets

```toml
GEMINI_API_KEY = "your-gemini-key"
TAVILY_API_KEY = "your-tavily-key"
GEMINI_MODEL = "gemini-2.5-flash-lite"
```

Do not commit API keys to GitHub.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deploy `app.py` from the repository root on Streamlit Community Cloud and add the three secrets in the app's Secrets settings.

## Live research behavior

The app uses Tavily search for exchange resolution, financial research, competitor/industry research, recent news and macro context. Gemini receives the retrieved evidence and produces structured JSON for the dashboard. Gemini Google Search grounding is intentionally disabled so the app does not depend on that separate Gemini grounding quota.
