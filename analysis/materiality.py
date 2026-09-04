from __future__ import annotations

def score_movement(movement: dict) -> int:
    severity = str(movement.get("severity", "medium")).lower()
    novelty = str(movement.get("novelty", "medium")).lower()
    impact = str(movement.get("impact", "medium")).lower()
    weights = {"low": 20, "medium": 50, "high": 80, "critical": 100}
    return round((weights.get(severity, 50) + weights.get(novelty, 50) + weights.get(impact, 50))/3)
