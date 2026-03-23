from codesmells.alignment import FuzzyAlignmentEngine
from codesmells.models import Token, TokenClass

def test_score_match_literal():
    engine = FuzzyAlignmentEngine()
    t1 = Token(TokenClass.LITERAL, "1", weight=0.2)
    t2 = Token(TokenClass.LITERAL, "1", weight=0.2)
    assert engine.score_match(t1, t2) == 0.4

def test_score_match_sigil():
    engine = FuzzyAlignmentEngine()
    tc = Token(TokenClass.IDENTIFIER, "my_var", weight=0.5)
    te = Token(TokenClass.SIGIL, "$VAR", weight=1.0)
    assert engine.score_match(tc, te) == 0.5
