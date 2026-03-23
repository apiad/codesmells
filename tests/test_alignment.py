from codesmells.alignment import FuzzyAlignmentEngine
from codesmells.models import Token, TokenClass
import math

def test_score_match_literal_match():
    engine = FuzzyAlignmentEngine()
    t1 = Token(TokenClass.LITERAL, "1", weight=0.2)
    t2 = Token(TokenClass.LITERAL, "1", weight=0.2)
    assert engine.score_match(t1, t2) == 0.4

def test_score_match_literal_mismatch():
    engine = FuzzyAlignmentEngine()
    t1 = Token(TokenClass.LITERAL, "1", weight=0.2)
    t2 = Token(TokenClass.LITERAL, "2", weight=0.2)
    assert engine.score_match(t1, t2) == float("-inf")

def test_score_match_sigil():
    engine = FuzzyAlignmentEngine()
    tc = Token(TokenClass.IDENTIFIER, "my_var", weight=0.5)
    te = Token(TokenClass.SIGIL, "$VAR", weight=1.0)
    assert engine.score_match(tc, te) == 0.5

def test_score_match_gap():
    engine = FuzzyAlignmentEngine()
    tc = Token(TokenClass.IDENTIFIER, "my_var", weight=0.5)
    te = Token(TokenClass.GAP, "-", weight=0.0)
    assert engine.score_match(tc, te) == 0.0

def test_score_match_mismatched_types():
    engine = FuzzyAlignmentEngine()
    tc = Token(TokenClass.IDENTIFIER, "my_var", weight=0.5)
    te = Token(TokenClass.KEYWORD, "if", weight=1.0)
    assert engine.score_match(tc, te) == float("-inf")
