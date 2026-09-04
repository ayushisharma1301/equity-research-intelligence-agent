from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

STATE = Path(".research_state.json")

def save(ticker: str, financial, industry, synthesis):
    state = {}
    if STATE.exists():
        try: state = json.loads(STATE.read_text())
        except Exception: state = {}
    state[ticker] = {"updated_at": datetime.now(timezone.utc).isoformat(), "financial": financial, "industry": industry, "synthesis": synthesis}
    STATE.write_text(json.dumps(state, indent=2, default=str))

def load(ticker: str):
    if not STATE.exists(): return None
    try: return json.loads(STATE.read_text()).get(ticker)
    except Exception: return None
