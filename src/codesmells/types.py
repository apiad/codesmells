from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


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
class Rule:
    id: str
    lang: list[str] = field(default_factory=list)
    tau: float = 0.4
    severity: str = "warn"
    description: str = ""
    pre_filters: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    safe_patterns: list[str] = field(default_factory=list)
    refactor_template: Optional[str] = None
    refactor_explanation: str = ""
    source_path: Optional[str] = None


@dataclass
class Finding:
    id: str
    rule_id: str
    file_path: str
    anchor_line: int
    end_line: int
    snippet: str
    bindings: dict[str, str] = field(default_factory=dict)
    score: float = 0.0


@dataclass
class IgnoreEntry:
    rule_id: str
    line: int
