# Setup Guide

## 1. Create API keys

Create one Gemini API key and one Tavily API key.

## 2. Streamlit Secrets

In Streamlit Community Cloud, open the app settings and add:

```toml
GEMINI_API_KEY = "..."
TAVILY_API_KEY = "..."
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

## 3. GitHub root

The repository root must contain:

```text
app.py
config.py
requirements.txt
agents/
analysis/
llm/
.streamlit/
```

Do not put these files under an extra `eri_rebuild/` folder.

## 4. Test

Try different companies to verify dynamic behavior, for example:
- NSE: Tata Motors
- NSE: HDFCBANK
- BSE: Infosys
- NSE: UltraTech Cement

These are examples only; the code does not store them as a universe.
