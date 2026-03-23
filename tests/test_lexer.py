from codesmells.lexer import ProbabilisticLexer
from codesmells.models import TokenClass

def test_tokenize_basic():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("def hello(): pass")
    assert any(t.token_class == TokenClass.KEYWORD and t.value == "def" for t in tokens)

def test_tokenize_sigil():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("$VAR = 1")
    assert any(t.token_class == TokenClass.SIGIL and t.value == "$VAR" for t in tokens)

def test_tokenize_gap():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("...")
    assert any(t.token_class == TokenClass.GAP and t.value == "..." for t in tokens)
