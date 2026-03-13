from src.models import Session
from typing import Tuple

def classify(session: Session) -> Tuple[str, str]:
    if session.num_instruction_violations >= 1:
        return "instruction_failure", f"{session.num_instruction_violations} violation(s)"
    if (session.avg_fluency and session.avg_correctness and
            session.avg_fluency >= 4 and session.avg_correctness <= 2 and
            session.outcome == "success"):
        return "over_trust", "High fluency, low correctness"
    if session.num_corrections >= 1:
        return "iterative_refinement", f"{session.num_corrections} correction(s)"
    return "linear_flow", "No corrections or violations"

def classify_and_annotate(session: Session) -> Session:
    pattern, _ = classify(session)
    session.final_pattern = pattern
    return session
