from __future__ import annotations
from typing import Any
import math


def num(x):
    try:
        if x is None or x == "": return None
        return float(x)
    except Exception:
        return None


def derive_period(p: dict) -> dict:
    p = dict(p)
    revenue, op, ni, cfo, capex, debt, cash = [num(p.get(k)) for k in ("revenue","operating_income","net_income","cfo","capex","total_debt","cash")]
    if revenue:
        p["operating_margin"] = round(op / revenue * 100, 2) if op is not None else None
        p["net_margin"] = round(ni / revenue * 100, 2) if ni is not None else None
    if cfo is not None and capex is not None:
        p["fcf"] = round(cfo - abs(capex), 2)
    if debt is not None and cash is not None:
        p["net_debt"] = round(debt - cash, 2)
    return p


def enrich_periods(periods: list[dict]) -> list[dict]:
    rows = [derive_period(x) for x in periods if isinstance(x, dict)]
    for i, row in enumerate(rows):
        prev = rows[i-1] if i else None
        if prev:
            for key in ("revenue","operating_income","net_income","cfo","capex","fcf","total_debt","cash","net_debt","operating_margin","net_margin"):
                a, b = num(row.get(key)), num(prev.get(key))
                if a is not None and b not in (None, 0):
                    row[f"{key}_yoy"] = round((a-b)/abs(b)*100, 2)
    return rows
