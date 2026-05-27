import re
from typing import List
from codesmells.types import Token, TokenClass

class ProbabilisticLexer:
    """
    A regex-based scanner that categorizes tokens using a cascading fallback.
    It does not construct an AST but maps source code into a sequence of weighted tokens.
    """
    def __init__(self):
        # Generic multi-language keywords
        keywords = [
            "def", "class", "import", "return", "if", "else", "for", "while",
            "try", "except", "catch", "finally", "with", "as", "lambda", "in",
            "is", "not", "and", "or", "function", "func", "var", "let", "const",
            "type", "interface", "public", "private", "protected", "static",
            "final", "break", "continue", "switch", "case", "default",
            "null", "true", "false", "new", "delete", "typeof", "instanceof",
            "yield", "await", "async", "do", "throw", "throws"
        ]
        kw_pattern = r"\b(" + "|".join(keywords) + r")\b"

        # Cascading fallback regex patterns as per design spec
        # 1. Gaps & Sigils
        # 2. Operators (non-alphanumeric clusters)
        # 3. Keywords
        # 4. Identifiers
        # 5. Literals
        self.patterns = [
            (r"\.\.\.", TokenClass.GAP, 1.0),
            (r"\$[A-Z0-9_]+", TokenClass.SIGIL, 1.0),
            (r"[^\w\s\"']+", TokenClass.OPERATOR, 1.0),
            (kw_pattern, TokenClass.KEYWORD, 1.0),
            (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", TokenClass.IDENTIFIER, 0.5),
            (r"(\d+\.?\d*|\"[^\"]*\"|'[^']*')", TokenClass.LITERAL, 0.2),
        ]

    def tokenize(self, code: str) -> List[Token]:
        """
        Tokenize the input code into a list of Token objects.
        
        Args:
            code: The raw source code to tokenize.
            
        Returns:
            A list of Token objects.
        """
        tokens = []
        lines = code.splitlines()
        for line_idx, line in enumerate(lines):
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
                    # Fallback for unknown character (should only be " or ' if they didn't match a literal)
                    # We create a fallback token or just skip it. 
                    # Given the spec "The system must never crash on malformed syntax",
                    # we just skip or treat as an operator of last resort.
                    pos += 1
        return tokens
