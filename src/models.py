from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal
from datetime import datetime
import uuid

@dataclass
class Turn:
    turn_id: int
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    has_correction: bool = False
    has_constraint: bool = False
    instruction_violated: bool = False
    fluency_score: Optional[int] = None
    correctness_score: Optional[int] = None

@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_type: str = "generation"
    language: str = "python"
    task_description: str = ""
    turns: List[Turn] = field(default_factory=list)
    outcome: str = "success"
    final_pattern: Optional[str] = None
    researcher_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def num_turns(self): return len(self.turns)
    @property
    def num_user_turns(self): return sum(1 for t in self.turns if t.role=="user")
    @property
    def num_corrections(self): return sum(1 for t in self.turns if t.has_correction)
    @property
    def num_instruction_violations(self): return sum(1 for t in self.turns if t.instruction_violated)
    @property
    def retry_rate(self): return self.num_corrections/self.num_user_turns if self.num_user_turns else 0.0
    @property
    def avg_fluency(self):
        s=[t.fluency_score for t in self.turns if t.role=="assistant" and t.fluency_score]
        return sum(s)/len(s) if s else None
    @property
    def avg_correctness(self):
        s=[t.correctness_score for t in self.turns if t.role=="assistant" and t.correctness_score]
        return sum(s)/len(s) if s else None
    def to_dict(self):
        d=asdict(self)
        d.update(num_turns=self.num_turns,num_user_turns=self.num_user_turns,
                 num_corrections=self.num_corrections,
                 num_instruction_violations=self.num_instruction_violations,
                 retry_rate=self.retry_rate,avg_fluency=self.avg_fluency,
                 avg_correctness=self.avg_correctness)
        return d
