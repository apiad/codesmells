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

def test_align_simple_match():
    engine = FuzzyAlignmentEngine()
    # def foo(): pass
    candidate = [
        Token(TokenClass.KEYWORD, "def", weight=1.0),
        Token(TokenClass.IDENTIFIER, "foo", weight=0.5),
        Token(TokenClass.OPERATOR, "(", weight=1.0),
        Token(TokenClass.OPERATOR, ")", weight=1.0),
        Token(TokenClass.OPERATOR, ":", weight=1.0),
        Token(TokenClass.KEYWORD, "pass", weight=1.0),
    ]
    # def $NAME(): ...
    template = [
        Token(TokenClass.KEYWORD, "def", weight=1.0),
        Token(TokenClass.SIGIL, "$NAME", weight=1.0),
        Token(TokenClass.OPERATOR, "(", weight=1.0),
        Token(TokenClass.OPERATOR, ")", weight=1.0),
        Token(TokenClass.OPERATOR, ":", weight=1.0),
        Token(TokenClass.GAP, "...", weight=0.0),
    ]
    
    # Expected scores:
    # def matches def: 1.0 * 2 = 2.0
    # foo matches $NAME: 0.5
    # ( matches (: 1.0 * 2 = 2.0
    # ) matches ): 1.0 * 2 = 2.0
    # : matches :: 1.0 * 2 = 2.0
    # pass matches ...: 0.0
    # Total raw: 2.0 + 0.5 + 2.0 + 2.0 + 2.0 + 0.0 = 8.5
    # Template weights: 1.0 + 1.0 + 1.0 + 1.0 + 1.0 + 0.0 = 5.0
    # Normalized: 8.5 / (2.0 * 5.0) = 0.85
    
    score, bindings = engine.align(candidate, template)
    assert math.isclose(score, 0.85)

def test_align_with_gaps():
    engine = FuzzyAlignmentEngine(gap_open=-2.0, gap_extend=-0.1)
    # def foo(x): pass
    candidate = [
        Token(TokenClass.KEYWORD, "def", weight=1.0),
        Token(TokenClass.IDENTIFIER, "foo", weight=0.5),
        Token(TokenClass.OPERATOR, "(", weight=1.0),
        Token(TokenClass.IDENTIFIER, "x", weight=0.5),
        Token(TokenClass.OPERATOR, ")", weight=1.0),
        Token(TokenClass.OPERATOR, ":", weight=1.0),
        Token(TokenClass.KEYWORD, "pass", weight=1.0),
    ]
    # def foo(): ...
    template = [
        Token(TokenClass.KEYWORD, "def", weight=1.0),
        Token(TokenClass.IDENTIFIER, "foo", weight=0.5),
        Token(TokenClass.OPERATOR, "(", weight=1.0),
        Token(TokenClass.OPERATOR, ")", weight=1.0),
        Token(TokenClass.OPERATOR, ":", weight=1.0),
        Token(TokenClass.GAP, "...", weight=0.0),
    ]
    
    # Expected alignment:
    # def matches def (2.0)
    # foo matches foo (1.0)
    # ( matches ( (2.0)
    # x is a gap in template (-2.1)
    # ) matches ) (2.0)
    # : matches : (2.0)
    # pass matches ... (0.0)
    # Total raw: 2.0 + 1.0 + 2.0 - 2.1 + 2.0 + 2.0 + 0.0 = 6.9
    # Template weights: 1.0 + 0.5 + 1.0 + 1.0 + 1.0 + 0.0 = 4.5
    # Normalized: 6.9 / (2.0 * 4.5) = 0.7666...
    
    score, _ = engine.align(candidate, template)
    assert math.isclose(score, 6.9 / 9.0)

def test_align_repeated_sigils_match():
    engine = FuzzyAlignmentEngine()
    # x = x
    candidate = [
        Token(TokenClass.IDENTIFIER, "x", weight=0.5),
        Token(TokenClass.OPERATOR, "=", weight=1.0),
        Token(TokenClass.IDENTIFIER, "x", weight=0.5),
    ]
    # $VAR = $VAR
    template = [
        Token(TokenClass.SIGIL, "$VAR", weight=1.0),
        Token(TokenClass.OPERATOR, "=", weight=1.0),
        Token(TokenClass.SIGIL, "$VAR", weight=1.0),
    ]
    score, bindings = engine.align(candidate, template)
    assert bindings == {"$VAR": "x"}
    # match 1: $VAR matches x -> 0.5
    # match 2: = matches = -> 2.0
    # match 3: $VAR matches x -> 0.5
    # Total: 3.0. Template weights: 1.0 + 1.0 + 1.0 = 3.0. Score: 3.0 / 6.0 = 0.5.
    assert math.isclose(score, 0.5)

def test_align_repeated_sigils_mismatch():
    engine = FuzzyAlignmentEngine()
    # x = y
    candidate = [
        Token(TokenClass.IDENTIFIER, "x", weight=0.5),
        Token(TokenClass.OPERATOR, "=", weight=1.0),
        Token(TokenClass.IDENTIFIER, "y", weight=0.5),
    ]
    # $VAR = $VAR
    template = [
        Token(TokenClass.SIGIL, "$VAR", weight=1.0),
        Token(TokenClass.OPERATOR, "=", weight=1.0),
        Token(TokenClass.SIGIL, "$VAR", weight=1.0),
    ]
    score, bindings = engine.align(candidate, template)
    # The path where $VAR matches x and $VAR matches y should be rejected.
    # If the path is rejected, the score should not include those matches.
    # Possible alternative alignments:
    # 1. "=" matches "=": score 2.0. Norm: 2.0 / 3.0 = 0.666
    # 2. "$VAR =" matches "x =": score 2.5. Norm: 2.5 / 3.0 = 0.833
    # 3. "= $VAR" matches "= y": score 2.5. Norm: 2.5 / 3.0 = 0.833
    assert score < 1.0
    assert bindings == {"$VAR": "x"} or bindings == {"$VAR": "y"}
