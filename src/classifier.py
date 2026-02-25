from src.models import Session, Pattern


def classify(session: Session) -> Pattern:
    if session.num_instruction_violations >= 1:
        return "instruction_failure"
    if (session.avg_fluency >= 4 and session.avg_correctness <= 2 and session.outcome == "success"):
        return "over_trust"
    if session.num_corrections >= 1:
        return "iterative_refinement"
    return "linear_flow"


def classify_and_update(session: Session) -> Session:
    session.final_pattern = classify(session)
    return session
