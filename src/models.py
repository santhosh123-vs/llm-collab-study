from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal
import json
import uuid

TaskType = Literal["generation", "debugging", "refactoring"]
Outcome = Literal["success", "failure", "partial"]
Pattern = Literal["linear_flow", "iterative_refinement", "instruction_failure", "over_trust"]


@dataclass
class Turn:
    turn_id: int
    role: Literal["user", "assistant"]
    content: str
    has_correction: bool = False
    has_constraint: bool = False
    instruction_violated: bool = False
    fluency_score: Optional[int] = None
    correctness_score: Optional[int] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Session:
    session_id: str
    task_type: TaskType
    turns: List[Turn] = field(default_factory=list)
    outcome: Outcome = "partial"
    final_pattern: Optional[Pattern] = None
    task_description: str = ""
    timestamp: str = ""

    @property
    def num_turns(self) -> int:
        return len(self.turns)

    @property
    def num_user_turns(self) -> int:
        return len([t for t in self.turns if t.role == "user"])

    @property
    def num_assistant_turns(self) -> int:
        return len([t for t in self.turns if t.role == "assistant"])

    @property
    def num_corrections(self) -> int:
        return len([t for t in self.turns if t.has_correction])

    @property
    def num_constraints(self) -> int:
        return len([t for t in self.turns if t.has_constraint])

    @property
    def num_instruction_violations(self) -> int:
        return len([t for t in self.turns if t.instruction_violated])

    @property
    def retry_rate(self) -> float:
        user_turns = self.num_user_turns
        if user_turns == 0:
            return 0.0
        return self.num_corrections / user_turns

    @property
    def avg_fluency(self) -> float:
        scores = [t.fluency_score for t in self.turns if t.fluency_score is not None]
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def avg_correctness(self) -> float:
        scores = [t.correctness_score for t in self.turns if t.correctness_score is not None]
        return sum(scores) / len(scores) if scores else 0.0

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "task_type": self.task_type,
            "turns": [t.to_dict() for t in self.turns],
            "outcome": self.outcome,
            "final_pattern": self.final_pattern,
            "task_description": self.task_description,
            "timestamp": self.timestamp,
            "num_turns": self.num_turns,
            "num_corrections": self.num_corrections,
            "num_instruction_violations": self.num_instruction_violations,
            "retry_rate": round(self.retry_rate, 3),
            "avg_fluency": round(self.avg_fluency, 2),
            "avg_correctness": round(self.avg_correctness, 2),
        }

    @classmethod
    def from_dict(cls, data):
        turns = [Turn.from_dict(t) for t in data.get("turns", [])]
        return cls(
            session_id=data["session_id"],
            task_type=data["task_type"],
            turns=turns,
            outcome=data.get("outcome", "partial"),
            final_pattern=data.get("final_pattern"),
            task_description=data.get("task_description", ""),
            timestamp=data.get("timestamp", ""),
        )


def new_session_id() -> str:
    return uuid.uuid4().hex[:8]
