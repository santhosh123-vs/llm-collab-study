from collections import defaultdict
import statistics
from src.models import Session

def _mean(v): return statistics.mean(v) if v else 0.0

def full_report(sessions):
    counts = defaultdict(int)
    for s in sessions: counts[s.final_pattern or "unclassified"] += 1
    total = len(sessions)

    by_task = defaultdict(list)
    for s in sessions: by_task[s.task_type].append(s)
    task_stats = {}
    for task, g in by_task.items():
        task_stats[task] = {
            "count": len(g),
            "avg_turns": round(_mean([s.num_turns for s in g]), 2),
            "avg_corrections": round(_mean([s.num_corrections for s in g]), 2),
            "success_rate": round(sum(1 for s in g if s.outcome=="success")/len(g)*100, 1),
        }

    pairs = [(s.avg_fluency, s.avg_correctness) for s in sessions if s.avg_fluency and s.avg_correctness]
    f,c = ([p[0] for p in pairs],[p[1] for p in pairs]) if pairs else ([],[])
    corr = 0
    if len(f) > 1:
        mx,my = _mean(f),_mean(c)
        num = sum((x-mx)*(y-my) for x,y in zip(f,c))
        dx = sum((x-mx)**2 for x in f)**0.5
        dy = sum((y-my)**2 for y in c)**0.5
        corr = round(num/(dx*dy),3) if dx*dy else 0

    return {
        "rq1_patterns": {"total": total, "counts": dict(counts),
            "percentages": {k: round(v/total*100,1) for k,v in counts.items()} if total else {}},
        "rq2_by_task": task_stats,
        "rq4_trust": {"avg_fluency": round(_mean(f),2), "avg_correctness": round(_mean(c),2),
            "correlation": corr, "over_trust_cases": sum(1 for a,b in pairs if a>=4 and b<=2)},
        "summary": {"total": total,
            "success_rate": round(sum(1 for s in sessions if s.outcome=="success")/total*100,1) if total else 0,
            "avg_turns": round(_mean([s.num_turns for s in sessions]),2)}
    }
