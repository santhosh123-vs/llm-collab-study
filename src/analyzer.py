from typing import List, Dict, Any
from collections import Counter
import math
from src.models import Session
from src.classifier import classify_and_update


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _pearson(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = _mean(x), _mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if dx * dy == 0:
        return 0.0
    return num / (dx * dy)


def _group_metrics(sessions: List[Session]) -> Dict[str, Any]:
    if not sessions:
        return {"count": 0, "avg_turns": 0, "avg_retry_rate": 0, "success_rate": 0, "avg_fluency": 0, "avg_correctness": 0}
    return {
        "count": len(sessions),
        "avg_turns": round(_mean([s.num_turns for s in sessions]), 2),
        "avg_retry_rate": round(_mean([s.retry_rate for s in sessions]), 3),
        "success_rate": round(len([s for s in sessions if s.outcome == "success"]) / len(sessions), 3),
        "avg_fluency": round(_mean([s.avg_fluency for s in sessions]), 2),
        "avg_correctness": round(_mean([s.avg_correctness for s in sessions]), 2),
    }


def full_report(sessions: List[Session]) -> Dict[str, Any]:
    for s in sessions:
        classify_and_update(s)

    total = len(sessions)
    if total == 0:
        return {"error": "No sessions to analyse"}

    pattern_counts = Counter(s.final_pattern for s in sessions)
    pattern_pcts = {k: round(v / total * 100, 1) for k, v in pattern_counts.items()}

    task_types = set(s.task_type for s in sessions)
    per_task = {}
    for tt in task_types:
        group = [s for s in sessions if s.task_type == tt]
        per_task[tt] = _group_metrics(group)

    successes = [s for s in sessions if s.outcome == "success"]
    failures = [s for s in sessions if s.outcome == "failure"]
    partials = [s for s in sessions if s.outcome == "partial"]
    high_correction = [s for s in sessions if s.num_corrections >= 2]
    low_correction = [s for s in sessions if s.num_corrections < 2]

    fluency_vals = [s.avg_fluency for s in sessions if s.avg_fluency > 0]
    correct_vals = [s.avg_correctness for s in sessions if s.avg_correctness > 0]
    min_len = min(len(fluency_vals), len(correct_vals))
    correlation = _pearson(fluency_vals[:min_len], correct_vals[:min_len])

    over_trust_sessions = [s for s in sessions if s.final_pattern == "over_trust"]

    return {
        "total_sessions": total,
        "rq1_pattern_distribution": {"counts": dict(pattern_counts), "percentages": pattern_pcts},
        "rq2_per_task_stats": per_task,
        "rq3_failure_analysis": {
            "success_metrics": _group_metrics(successes),
            "failure_metrics": _group_metrics(failures),
            "partial_metrics": _group_metrics(partials),
            "high_correction_success_rate": round(len([s for s in high_correction if s.outcome == "success"]) / len(high_correction), 3) if high_correction else "N/A",
            "low_correction_success_rate": round(len([s for s in low_correction if s.outcome == "success"]) / len(low_correction), 3) if low_correction else "N/A",
        },
        "rq4_trust_calibration": {
            "avg_fluency": round(_mean(fluency_vals), 2),
            "avg_correctness": round(_mean(correct_vals), 2),
            "fluency_correctness_correlation": round(correlation, 3),
            "over_trust_count": len(over_trust_sessions),
            "over_trust_percentage": round(len(over_trust_sessions) / total * 100, 1),
        },
    }
