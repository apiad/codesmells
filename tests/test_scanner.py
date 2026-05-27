from pathlib import Path
from codesmells.scanner import scan_path
from codesmells.rules import parse_rule_file


def _make_rule(tmp_path: Path, name: str, anti: str, pre_filter: str, tau: float = 0.4, safe: str = ""):
    p = tmp_path / f"{name}.smell.md"
    body = f"""---
id: {name}
lang: [python]
tau: {tau}
pre_filters:
  - "{pre_filter}"
---

# {name}

### Anti-Pattern

```python
{anti}
```
"""
    if safe:
        body += f"""
### Safe

```python
{safe}
```
"""
    body += """
### Refactoring

```python
pass
```
"""
    p.write_text(body)
    return parse_rule_file(p)


def _make_source(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body)
    return p


def test_scan_finds_single_match(tmp_path):
    rule = _make_rule(tmp_path, "catch_all", "try:\n    ...\nexcept Exception as $VAR:\n    ...", "except Exception")
    _make_source(tmp_path, "src.py", """
def f():
    try:
        run()
    except Exception as e:
        log(e)
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "src.py"]
    assert len(findings_in_src) == 1, f"expected 1, got {len(findings_in_src)}: {findings_in_src}"
    f = findings_in_src[0]
    assert f.rule_id == "catch_all"
    assert f.bindings.get("$VAR") == "e"


def test_scan_finds_multiple_instances(tmp_path):
    rule = _make_rule(tmp_path, "print_rule", "print($MSG)", "print")
    _make_source(tmp_path, "many.py", """
def main():
    print("a")
    print("b")
    print("c")
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "many.py"]
    assert len(findings_in_src) == 3, f"expected 3, got {len(findings_in_src)}: {[(f.anchor_line, f.snippet[:30]) for f in findings_in_src]}"
    anchors = sorted(f.anchor_line for f in findings_in_src)
    assert anchors == [3, 4, 5]


def test_scan_skips_safe_patterns(tmp_path):
    rule = _make_rule(
        tmp_path,
        "print_rule",
        "print($MSG)",
        "print",
        safe='print($MSG, file=sys.stderr)',
    )
    _make_source(tmp_path, "mixed.py", """
print("loud")
print("stderr", file=sys.stderr)
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "mixed.py"]
    assert len(findings_in_src) == 1, f"expected 1, got {len(findings_in_src)}"
    assert findings_in_src[0].anchor_line == 2


def test_scan_respects_per_site_ignore(tmp_path):
    rule = _make_rule(tmp_path, "catch_all", "try:\n    ...\nexcept Exception as $VAR:\n    ...", "except Exception")
    _make_source(tmp_path, "ig.py", """
try:
    run()
# codesmells: ignore catch_all
except Exception as e:
    pass
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "ig.py"]
    assert findings_in_src == [], f"expected suppressed, got {findings_in_src}"


def test_finding_id_is_deterministic(tmp_path):
    rule = _make_rule(tmp_path, "catch_all", "try:\n    ...\nexcept Exception as $VAR:\n    ...", "except Exception")
    _make_source(tmp_path, "src.py", """
try:
    f()
except Exception as e:
    pass
""")
    f1 = scan_path(tmp_path, [rule])
    f2 = scan_path(tmp_path, [rule])
    ids1 = sorted(x.id for x in f1)
    ids2 = sorted(x.id for x in f2)
    assert ids1 == ids2
