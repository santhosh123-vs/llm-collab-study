import random
from datetime import datetime, timedelta
from src.models import Session, Turn, new_session_id
from src.classifier import classify_and_update
from src.store import save_session

TASK_DESCRIPTIONS = {
    "generation": [
        "Write a binary search function in Python",
        "Implement a linked list with insert and delete",
        "Create a REST API endpoint for user registration",
        "Write a function to find all permutations of a string",
        "Implement a LRU cache class",
    ],
    "debugging": [
        "Fix the off-by-one error in this loop",
        "Debug why this recursive function causes stack overflow",
        "Find the memory leak in this class",
        "Fix the race condition in this threaded code",
        "Debug why the API returns 500 on certain inputs",
    ],
    "refactoring": [
        "Refactor this function to use list comprehensions",
        "Convert this class to use the Strategy pattern",
        "Refactor to remove code duplication",
        "Convert callbacks to async/await",
        "Refactor this monolith into separate modules",
    ],
}


def _random_turns(task_type, scenario):
    turns = []
    tid = 0

    turns.append(Turn(turn_id=tid, role="user", content=random.choice(TASK_DESCRIPTIONS[task_type])))
    tid += 1

    if scenario == "linear_flow":
        turns.append(Turn(turn_id=tid, role="assistant", content="Here is the implementation...",
                          fluency_score=random.randint(4, 5), correctness_score=random.randint(4, 5)))
        tid += 1
        turns.append(Turn(turn_id=tid, role="user", content="Looks good, thanks!"))

    elif scenario == "iterative_refinement":
        turns.append(Turn(turn_id=tid, role="assistant", content="Here is my first attempt...",
                          fluency_score=random.randint(3, 5), correctness_score=random.randint(2, 3)))
        tid += 1
        turns.append(Turn(turn_id=tid, role="user", content="That's not quite right, handle edge cases...", has_correction=True))
        tid += 1
        turns.append(Turn(turn_id=tid, role="assistant", content="Here's the corrected version...",
                          fluency_score=random.randint(4, 5), correctness_score=random.randint(4, 5)))
        tid += 1
        if random.random() < 0.4:
            turns.append(Turn(turn_id=tid, role="user", content="One more issue with complexity...",
                              has_correction=True, has_constraint=True))
            tid += 1
            turns.append(Turn(turn_id=tid, role="assistant", content="Updated to O(n) using hash map...",
                              fluency_score=random.randint(3, 5), correctness_score=random.randint(3, 5)))

    elif scenario == "instruction_failure":
        turns.append(Turn(turn_id=tid, role="assistant", content="Here's the solution using recursion...",
                          fluency_score=random.randint(4, 5), correctness_score=random.randint(2, 3),
                          instruction_violated=True))
        tid += 1
        turns.append(Turn(turn_id=tid, role="user", content="I said NO recursion! Use iteration.",
                          has_correction=True, has_constraint=True))
        tid += 1
        turns.append(Turn(turn_id=tid, role="assistant", content="Sorry, here is the iterative version...",
                          fluency_score=random.randint(3, 5), correctness_score=random.randint(3, 4)))

    elif scenario == "over_trust":
        turns.append(Turn(turn_id=tid, role="assistant", content="Here's a clean, well-structured solution...",
                          fluency_score=random.randint(4, 5), correctness_score=random.randint(1, 2)))
        tid += 1
        turns.append(Turn(turn_id=tid, role="user", content="Looks great, I'll use this!"))

    return turns


def generate_sample_sessions(n=15):
    sessions = []
    base_time = datetime.now() - timedelta(days=14)

    scenarios_pool = ["linear_flow"] * 6 + ["iterative_refinement"] * 6 + ["instruction_failure"] * 2 + ["over_trust"] * 1
    random.shuffle(scenarios_pool)

    task_types = ["generation"] * 5 + ["debugging"] * 5 + ["refactoring"] * 5
    random.shuffle(task_types)

    for i in range(n):
        scenario = scenarios_pool[i % len(scenarios_pool)]
        task_type = task_types[i % len(task_types)]
        turns = _random_turns(task_type, scenario)

        if scenario == "over_trust":
            outcome = "success"
        elif scenario == "instruction_failure":
            outcome = random.choice(["failure", "partial"])
        elif scenario == "iterative_refinement":
            outcome = random.choice(["success", "success", "failure"])
        else:
            outcome = "success"

        session = Session(
            session_id=new_session_id(), task_type=task_type, turns=turns,
            outcome=outcome, task_description=random.choice(TASK_DESCRIPTIONS[task_type]),
            timestamp=(base_time + timedelta(days=i)).isoformat(),
        )
        classify_and_update(session)
        save_session(session)
        sessions.append(session)
        print(f"  Created session {session.session_id} | {task_type:13s} | {session.final_pattern}")

    return sessions


if __name__ == "__main__":
    print("Generating 15 sample sessions...")
    generate_sample_sessions(15)
    print("Done! Sessions saved in data/sessions/")
