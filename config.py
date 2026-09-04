from __future__ import annotations
import os
import streamlit as st

def get_config():
    def secret(name, default=''):
        try: return st.secrets.get(name, default)
        except Exception: return os.getenv(name, default)
    return {
        'GEMINI_API_KEY': secret('GEMINI_API_KEY'),
        'GEMINI_MODEL': secret('GEMINI_MODEL','gemini-2.5-flash'),
    }
