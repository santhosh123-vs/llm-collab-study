import json
import os
from typing import List, Optional
from src.models import Session

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sessions")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_session(session: Session) -> str:
    _ensure_dir()
    path = os.path.join(DATA_DIR, f"{session.session_id}.json")
    with open(path, "w") as f:
        json.dump(session.to_dict(), f, indent=2)
    return path


def load_session(session_id: str) -> Optional[Session]:
    path = os.path.join(DATA_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return Session.from_dict(json.load(f))


def load_all_sessions() -> List[Session]:
    _ensure_dir()
    sessions = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(DATA_DIR, fname)
            with open(path) as f:
                sessions.append(Session.from_dict(json.load(f)))
    return sessions


def list_session_ids() -> List[str]:
    _ensure_dir()
    return [f.replace(".json", "") for f in sorted(os.listdir(DATA_DIR)) if f.endswith(".json")]
