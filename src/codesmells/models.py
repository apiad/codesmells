from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

class TokenClass(Enum):
    KEYWORD = auto()
    OPERATOR = auto()
    IDENTIFIER = auto()
    LITERAL = auto()
    GAP = auto()
    SIGIL = auto()

@dataclass(frozen=True)
class Token:
    token_class: TokenClass
    value: str
    weight: float = 1.0
    line_num: int = 0
    col_num: int = 0

@dataclass
class Binding:
    candidate_id: str
    sigil: str
    bound_value: str

@dataclass
class Candidate:
    id: str
    rule_id: str
    file_path: str
    line_num: int
    raw_snippet: str
    status: str = "PENDING" # PENDING, ACCEPTED, IGNORED
    bindings: List[Binding] = field(default_factory=list)

@dataclass
class Rule:
    id: str
    tau: float = 0.8
    pre_filters: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    safe_patterns: List[str] = field(default_factory=list)
    refactor_template: Optional[str] = None
