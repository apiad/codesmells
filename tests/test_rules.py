from pathlib import Path
import pytest
from codesmells.rules import (
    parse_rule_file,
    load_rules_from_dir,
    detect_languages,
    library_rules_for_languages,
    RuleParseError,
)


def _write_rule(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / f"{name}.smell.md"
    p.write_text(body)
    return p


def test_parse_minimal_rule(tmp_path):
    p = _write_rule(tmp_path, "test_rule", """---
id: test_rule
lang: [python]
tau: 0.7
severity: warn
pre_filters:
  - "except Exception"
---

# Test

Short description.

### Anti-Pattern

```python
except Exception as $VAR:
    ...
```

### Refactoring

Use specific exception.

```python
except ValueError as $VAR:
    ...
```
""")
    rule = parse_rule_file(p)
    assert rule.id == "test_rule"
    assert rule.lang == ["python"]
    assert rule.tau == 0.7
    assert rule.severity == "warn"
    assert rule.pre_filters == ["except Exception"]
    assert len(rule.anti_patterns) == 1
    assert "except Exception" in rule.anti_patterns[0]
    assert rule.refactor_template is not None
    assert "ValueError" in rule.refactor_template
    assert rule.description.startswith("Short description")
    assert rule.source_path == str(p)


def test_parse_rule_with_safe_block(tmp_path):
    p = _write_rule(tmp_path, "test_rule_safe", """---
id: test_rule_safe
lang: [python]
tau: 0.7
---

# Test

### Anti-Pattern

```python
print($MSG)
```

### Safe

```python
logger.info($MSG)
```

### Refactoring

```python
logger.info($MSG)
```
""")
    rule = parse_rule_file(p)
    assert len(rule.safe_patterns) == 1
    assert "logger.info" in rule.safe_patterns[0]


def test_parse_missing_id_raises(tmp_path):
    p = _write_rule(tmp_path, "no_id", """---
lang: [python]
---

### Anti-Pattern

```python
pass
```
""")
    with pytest.raises(RuleParseError, match="id"):
        parse_rule_file(p)


def test_parse_missing_anti_pattern_raises(tmp_path):
    p = _write_rule(tmp_path, "no_ap", """---
id: no_ap
lang: [python]
---

### Refactoring

```python
pass
```
""")
    with pytest.raises(RuleParseError, match="Anti-Pattern"):
        parse_rule_file(p)


def test_load_rules_from_dir(tmp_path):
    (tmp_path / "a.smell.md").write_text("""---
id: a
lang: [python]
---

### Anti-Pattern

```python
pass
```
""")
    (tmp_path / "b.smell.md").write_text("""---
id: b
lang: [python]
---

### Anti-Pattern

```python
pass
```
""")
    (tmp_path / "ignore_me.txt").write_text("not a rule")
    rules = load_rules_from_dir(tmp_path)
    assert sorted(r.id for r in rules) == ["a", "b"]


def test_load_rules_skips_malformed(tmp_path, capsys):
    (tmp_path / "good.smell.md").write_text("""---
id: good
lang: [python]
---

### Anti-Pattern

```python
pass
```
""")
    (tmp_path / "bad.smell.md").write_text("---\nid:\n---\n")
    rules = load_rules_from_dir(tmp_path)
    assert [r.id for r in rules] == ["good"]
    err = capsys.readouterr().err
    assert "bad.smell.md" in err


def test_detect_languages(tmp_path):
    (tmp_path / "main.py").write_text("print(1)")
    (tmp_path / "lib.py").write_text("print(2)")
    (tmp_path / "README.md").write_text("# hi")
    langs = detect_languages(tmp_path)
    assert "python" in langs
    assert "markdown" in langs


def test_library_rules_for_languages_empty_when_no_library():
    # Library not yet populated — should return [] without crashing
    rules = library_rules_for_languages({"python"})
    assert isinstance(rules, list)
