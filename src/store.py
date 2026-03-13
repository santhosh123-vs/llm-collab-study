import json, os
from src.models import Session, Turn

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sessions")

def _path(sid):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{sid}.json")

def save(s):
    p = _path(s.session_id)
    with open(p,"w") as f: json.dump(s.to_dict(), f, indent=2)
    return p

def load_all():
    if not os.path.exists(DATA_DIR): return []
    sessions = []
    skip = {"num_turns","num_user_turns","num_corrections","num_instruction_violations","retry_rate","avg_fluency","avg_correctness"}
    for fn in os.listdir(DATA_DIR):
        if not fn.endswith(".json"): continue
        with open(os.path.join(DATA_DIR,fn)) as f:
            d = json.load(f)
        raw = {k:v for k,v in d.items() if k not in skip}
        turns = [Turn(**t) for t in raw.pop("turns",[])]
        sessions.append(Session(turns=turns,**raw))
    return sessions
