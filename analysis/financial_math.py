from __future__ import annotations
from typing import Dict, List


def pct_change(current, previous):
    if previous in (None, 0):
        return None
    return (current - previous) / abs(previous) * 100


def margin(value, revenue):
    if revenue in (None, 0):
        return None
    return value / revenue * 100


def build_derived_metrics(periods: List[Dict]) -> List[Dict]:
    out = []
    for p in periods:
        revenue = p.get("revenue")
        operating_income = p.get("operating_income")
        net_income = p.get("net_income")
        cfo = p.get("cash_from_operations")
        capex = p.get("capital_expenditure")
        debt = p.get("total_debt")
        cash = p.get("cash")
        row = dict(p)
        row["operating_margin"] = margin(operating_income, revenue)
        row["net_margin"] = margin(net_income, revenue)
        row["fcf"] = (cfo - abs(capex)) if cfo is not None and capex is not None else None
        row["net_debt"] = (debt - cash) if debt is not None and cash is not None else None
        out.append(row)
    return out


def latest_movements(periods: List[Dict]) -> Dict:
    if len(periods) < 2:
        return {}
    cur, prev = periods[-1], periods[-2]
    keys = [
        "revenue", "operating_income", "net_income", "cash_from_operations",
        "capital_expenditure", "total_debt", "cash", "inventory", "receivables",
    ]
    movement = {}
    for key in keys:
        movement[key] = pct_change(cur.get(key), prev.get(key))
    return movement
