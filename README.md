# Equity Research Intelligence Agent — Dynamic NSE/BSE Edition

A Streamlit equity-research console powered by Gemini API + Google Search grounding. There is **no fixed company universe and no static financial dataset**.

## Core workflow
1. Select **NSE** or **BSE**.
2. Type any listed company name, symbol, or scrip identifier.
3. Gemini resolves the exact listed security.
4. Financial Intelligence Agent researches current statements, reports, earnings-call/management commentary, historical financial movement and capital allocation.
5. Industry Intelligence Agent researches competitors, industry reports, macro signals and recent news.
6. Synthesis Agent converts the evidence into a prioritized analyst work queue.
7. Dashboard shows the numbers, movements, evidence, recommendations and source room.

## External interfaces
Only Gemini API / Google Search grounding is used for external research. Streamlit is the UI/runtime and GitHub is the repository/deployment source.

## No static company universe
The sidebar intentionally has no watchlist. A user can research a different NSE/BSE company on every run.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Set `GEMINI_API_KEY` in Streamlit Secrets or the environment.
