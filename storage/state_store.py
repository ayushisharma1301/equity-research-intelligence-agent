from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


def save_session(snapshot: dict, path: Path | None = None):
    path = path or ROOT / "session_snapshot.json"
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")


def load_session(path: Path | None = None):
    path = path or ROOT / "session_snapshot.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def timestamp():
    return datetime.now(timezone.utc).isoformat()
