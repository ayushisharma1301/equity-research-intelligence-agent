from __future__ import annotations
import os
import streamlit as st


def get_config():
    def secret(name, default=""):
        try:
            value = st.secrets.get(name, default)
            return value if value not in (None, "") else os.getenv(name, default)
        except Exception:
            return os.getenv(name, default)

    return {
        "GEMINI_API_KEY": secret("GEMINI_API_KEY"),
        "GEMINI_MODEL": secret("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        "TAVILY_API_KEY": secret("TAVILY_API_KEY"),
    }
