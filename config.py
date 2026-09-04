import os
import streamlit as st

DEFAULT_WATCHLIST = ["AAPL", "MSFT", "NVDA", "JPM", "RELIANCE.NS"]


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return os.getenv(name, value)


def get_config():
    watchlist_raw = _secret("WATCHLIST", ",".join(DEFAULT_WATCHLIST))
    watchlist = [x.strip().upper() for x in watchlist_raw.split(",") if x.strip()]
    return {
        "gemini_api_key": _secret("GEMINI_API_KEY"),
        "gemini_model": _secret("GEMINI_MODEL", "gemini-2.5-flash"),
        "watchlist": watchlist or DEFAULT_WATCHLIST,
        "max_companies_per_run": int(_secret("MAX_COMPANIES_PER_RUN", "5")),
    }
