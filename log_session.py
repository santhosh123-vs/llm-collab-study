import sys
import json
from datetime import datetime
from src.models import Session, Turn, new_session_id
from src.classifier import classify_and_update
from src.store import save_session, load_all_sessions, list_session_ids
from src.analyzer import full_report


def interactive_log():
    print("\nLog a New Session")
    print("=" * 40)
    sid = new_session_id()
    print(f"Session ID: {sid}")

    print("\nTask types: 1) generation  2) debugging  3) refactoring")
    choice = input("Choose (1/2/3): ").strip()
    task_map = {"1": "generation", "2": "debugging", "3": "refactoring"}
    task_type = task_map.get(choice, "generation")

    desc = input("Brief task description: ").strip()

    turns = []
    tid = 0
    print("\nEnter turns (type 'done' to finish):")
    while True:
        role = input(f"\n  Turn {tid} role (user/assistant) or 'done': ").strip().lower()
        if role == "done":
            break
        if role not in ("user", "assistant"):
            print("  Invalid role.")
            continue
        content = input(f"  Content: ").strip()
        has_correction = has_constraint = instruction_violated = False
        fluency = correctness = None
        if role == "user":
            has_correction = input("  Is this a correction? (y/n): ").strip().lower() == "y"
            has_constraint = input("  Does it add a constraint? (y/n): ").strip().lower() == "y"
        else:
            instruction_violated = input("  Did model violate instructions? (y/n): ").strip().lower() == "y"
            try:
                fluency = int(input("  Fluency score (1-5): ").strip())
                correctness = int(input("  Correctness score (1-5): ").strip())
            except ValueError:
                pass
        turns.append(Turn(turn_id=tid, role=role, content=content, has_correction=has_correction,
                          has_constraint=has_constraint, instruction_violated=instruction_violated,
                          fluency_score=fluency, correctness_score=correctness))
        tid += 1

    print("\nOutcome: 1) success  2) failure  3) partial")
    oc = input("Choose (1/2/3): ").strip()
    outcome_map = {"1": "success", "2": "failure", "3": "partial"}
    outcome = outcome_map.get(oc, "partial")

    session = Session(session_id=sid, task_type=task_type, turns=turns, outcome=outcome,
                      task_description=desc, timestamp=datetime.now().isoformat())
    classify_and_update(session)
    path = save_session(session)
    print(f"\nSession saved! Pattern: {session.final_pattern} | File: {path}")


def show_report():
    sessions = load_all_sessions()
    if not sessions:
        print("No sessions found.")
        return
    result = full_report(sessions)
    print(json.dumps(result, indent=2))
    import os
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/report.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nReport saved to outputs/report.json")


def list_sessions_cmd():
    ids = list_session_ids()
    if not ids:
        print("No sessions yet.")
        return
    print(f"\n{len(ids)} sessions:")
    for sid in ids:
        print(f"  - {sid}")


if __name__ == "__main__":
    if "--report" in sys.argv:
        show_report()
    elif "--list" in sys.argv:
        list_sessions_cmd()
    else:
        interactive_log()
