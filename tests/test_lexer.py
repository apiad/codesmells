from codesmells.lexer import ProbabilisticLexer
from codesmells.types import TokenClass

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

def test_tokenize_operators():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("== => { } ( ) [ ] , ; + - * /")
    operators = [t.value for t in tokens if t.token_class == TokenClass.OPERATOR]
    assert "==" in operators
    assert "=>" in operators
    assert "{" in operators
    assert "}" in operators
    assert "+" in operators
    assert "-" in operators
    for t in tokens:
        if t.token_class == TokenClass.OPERATOR:
            assert t.weight == 1.0

def test_tokenize_keywords():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("def class import return if else for while try except with as lambda in is not and or")
    keywords = [t.value for t in tokens if t.token_class == TokenClass.KEYWORD]
    assert "def" in keywords
    assert "class" in keywords
    assert "if" in keywords
    for t in tokens:
        if t.token_class == TokenClass.KEYWORD:
            assert t.weight == 1.0

def test_tokenize_identifiers():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("my_var _var123 VAR")
    identifiers = [t.value for t in tokens if t.token_class == TokenClass.IDENTIFIER]
    assert "my_var" in identifiers
    assert "_var123" in identifiers
    assert "VAR" in identifiers
    for t in tokens:
        if t.token_class == TokenClass.IDENTIFIER:
            assert t.weight == 0.5

def test_tokenize_literals():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize('123 45.6 "hello" \'world\'')
    literals = [t.value for t in tokens if t.token_class == TokenClass.LITERAL]
    assert "123" in literals
    assert "45.6" in literals
    assert '"hello"' in literals
    assert "'world'" in literals
    for t in tokens:
        if t.token_class == TokenClass.LITERAL:
            assert t.weight == 0.2

def test_tokenize_complex_line():
    lexer = ProbabilisticLexer()
    # Adding spaces to avoid clustering of usually separate operators if we want to test them individually,
    # or just accept the clustering.
    code = 'def $NAME(x): ... return "done"'
    tokens = lexer.tokenize(code)
    
    # Expected token classes in order (skipping whitespace)
    # Note: '):' will be clustered into one OPERATOR token because there's no space
    expected_classes = [
        TokenClass.KEYWORD,    # def
        TokenClass.SIGIL,      # $NAME
        TokenClass.OPERATOR,   # (
        TokenClass.IDENTIFIER, # x
        TokenClass.OPERATOR,   # ):
        TokenClass.GAP,        # ...
        TokenClass.KEYWORD,    # return
        TokenClass.LITERAL     # "done"
    ]
    
    token_classes = [t.token_class for t in tokens]
    assert token_classes == expected_classes

def test_tokenize_operator_clustering():
    lexer = ProbabilisticLexer()
    tokens = lexer.tokenize("x != y")
    operators = [t.value for t in tokens if t.token_class == TokenClass.OPERATOR]
    assert "!=" in operators
    
    tokens = lexer.tokenize("a=b+c")
    # Here "=b" is NOT a cluster because b is alphanumeric.
    # So "=" is a cluster, "b" is identifier, "+" is a cluster.
    values = [t.value for t in tokens]
    assert values == ["a", "=", "b", "+", "c"]
