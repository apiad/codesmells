import re
from typing import List
from codesmells.models import Token, TokenClass

class ProbabilisticLexer:
    def __init__(self):
        # Cascading fallback regex patterns
        self.patterns = [
            (r"\.\.\.", TokenClass.GAP, 1.0),
            (r"\$([A-Z0-9_]+)", TokenClass.SIGIL, 1.0),
            (r"(==|=>|[{}()\[\],;])", TokenClass.OPERATOR, 1.0),
            (r"\b(def|class|import|return|if|else|for|while|try|except|with|as|lambda|in|is|not|and|or)\b", TokenClass.KEYWORD, 1.0),
            (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", TokenClass.IDENTIFIER, 0.5),
            (r"\d+\.?\d*|\"[^\"]*\"|'[^']*'", TokenClass.LITERAL, 0.2),
        ]

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        lines = code.splitlines()
        for line_idx, line in enumerate(lines):
            # Simple tokenization for now
            pos = 0
            while pos < len(line):
                # Skip whitespace
                if line[pos].isspace():
                    pos += 1
                    continue
                
                matched = False
                for pattern, t_class, weight in self.patterns:
                    match = re.match(pattern, line[pos:])
                    if match:
                        value = match.group(0)
                        tokens.append(Token(
                            token_class=t_class,
                            value=value,
                            weight=weight,
                            line_num=line_idx + 1,
                            col_num=pos + 1
                        ))
                        pos += len(value)
                        matched = True
                        break
                
                if not matched:
                    # Fallback for unknown character
                    pos += 1
        return tokens
