from typer.testing import CliRunner
from codesmells.cli import app

runner = CliRunner()

def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan directory for anti-patterns" in result.stdout

def test_scan_basic():
    with runner.isolated_filesystem():
        # Without rules, it should fail with helpful message
        result = runner.invoke(app, ["scan"])
        assert result.exit_code != 0
        assert "No rule templates found" in result.stdout
        
        # Now init and add a rule
        runner.invoke(app, ["init"])
        runner.invoke(app, ["add", "Test Rule", "desc"])
        
        result_with_rules = runner.invoke(app, ["scan"])
        assert result_with_rules.exit_code == 0
        assert "Scanning" in result_with_rules.stdout

def test_validate_functional():
    with runner.isolated_filesystem():
        runner.invoke(app, ["init"])
        # add creates both .smell.md and .smell.test.md
        runner.invoke(app, ["add", "Test Smell", "desc"])
        
        # Manually fill files with valid data
        rule_path = Path(".codesmells/test-smell.smell.md")
        rule_path.write_text("""---
tau: 0.8
pre_filters: ["bad_func"]
---
### Anti-Pattern
```python
def bad_func():
    pass
```
""")
        
        test_path = Path(".codesmells/test-smell.smell.test.md")
        test_path.write_text("""### Anti-Pattern
```python
def bad_func():
    pass
```

### Safe
```python
def good_func():
    pass
```
""")
        
        # Test validation success
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0
        assert "Validating test-smell" in result.stdout
        assert "Anti-Pattern #1 matched" in result.stdout
        assert "Safe Pattern #1 correctly ignored" in result.stdout
        assert "1 passed" in result.stdout
        
        # Test validation failure (lowering tau or changing test to something that matches)
        test_path.write_text("""### Anti-Pattern
```python
def bad_func():
    pass
```

### Safe
```python
def bad_func():
    pass
```
""")
        result_fail = runner.invoke(app, ["validate"])
        assert result_fail.exit_code != 0
        assert "Safe Pattern #1 failed" in result_fail.stdout
        assert "1 failed" in result_fail.stdout

import json
from pathlib import Path

def test_scan_functional():
    with runner.isolated_filesystem():
        Path(".codesmells").mkdir()
        rule_content = """---
tau: 0.5
pre_filters:
  - "def bad_func"
---
### Anti-Pattern
```python
def bad_func():
    $X = 1
```
"""
        Path(".codesmells/bad_rule.smell.md").write_text(rule_content)
        
        target_content = """
def bad_func():
    y = 1
"""
        Path("target.py").write_text(target_content)
        
        result = runner.invoke(app, ["scan"])
        assert result.exit_code == 0
        assert "target.py" in result.stdout
        assert "bad_rule" in result.stdout
        
        session_file = Path(".codesmells/session.json")
        assert session_file.exists()
        
        data = json.loads(session_file.read_text())
        assert len(data["candidates"]) == 1
        c = data["candidates"][0]
        assert c["rule_id"] == "bad_rule"
        assert c["file_path"] == "target.py"
        
        c_id = c["id"]
        
        # Test inspect success
        inspect_result = runner.invoke(app, ["inspect", c_id])
        assert inspect_result.exit_code == 0
        assert c_id in inspect_result.stdout
        assert "bad_rule" in inspect_result.stdout
        # Assuming the output contains the raw snippet and bindings
        assert "bad_func" in inspect_result.stdout
        
        # Test inspect not found
        inspect_not_found = runner.invoke(app, ["inspect", "nonexistent_id"])
        assert inspect_not_found.exit_code != 0 or "not found" in inspect_not_found.stdout.lower()
        assert "not found" in inspect_not_found.stdout.lower()

def test_suggest_functional():
    with runner.isolated_filesystem():
        Path(".codesmells").mkdir()
        rule_content = """---
tau: 0.5
pre_filters:
  - "def bad_func"
---
### Anti-Pattern
```python
def bad_func():
    $X = 1
```

### Refactoring
```python
def good_func():
    $X = 2
```
"""
        Path(".codesmells/bad_rule.smell.md").write_text(rule_content)
        
        target_content = """
def bad_func():
    y = 1
"""
        Path("target.py").write_text(target_content)
        
        runner.invoke(app, ["scan"])
        
        session_file = Path(".codesmells/session.json")
        data = json.loads(session_file.read_text())
        c_id = data["candidates"][0]["id"]
        
        # Test suggest success
        suggest_result = runner.invoke(app, ["suggest", c_id])
        assert suggest_result.exit_code == 0
        assert "good_func" in suggest_result.stdout
        assert "y = 2" in suggest_result.stdout
        
        # Test suggest not found
        suggest_not_found = runner.invoke(app, ["suggest", "nonexistent_id"])
        assert suggest_not_found.exit_code != 0 or "not found" in suggest_not_found.stdout.lower()
        assert "not found" in suggest_not_found.stdout.lower()

def test_suggest_no_template():
    with runner.isolated_filesystem():
        Path(".codesmells").mkdir()
        rule_content = """---
tau: 0.5
pre_filters:
  - "def bad_func"
---
### Anti-Pattern
```python
def bad_func():
    $X = 1
```
"""
        Path(".codesmells/bad_rule.smell.md").write_text(rule_content)
        
        target_content = """
def bad_func():
    y = 1
"""
        Path("target.py").write_text(target_content)
        
        runner.invoke(app, ["scan"])
        
        session_file = Path(".codesmells/session.json")
        data = json.loads(session_file.read_text())
        c_id = data["candidates"][0]["id"]
        
        suggest_no_template = runner.invoke(app, ["suggest", c_id])
        assert suggest_no_template.exit_code != 0 or "no refactoring template" in suggest_no_template.stdout.lower()
        assert "no refactoring template" in suggest_no_template.stdout.lower()

def test_init_basic():
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Initialized CodeSmells" in result.stdout
        assert "codesmells add" in result.stdout
        
        codesmells_dir = Path(".codesmells")
        assert codesmells_dir.is_dir()
        
        gitignore_file = codesmells_dir / ".gitignore"
        assert gitignore_file.exists()
        assert "session.json" in gitignore_file.read_text()
        
        # Test repeat init fails
        result_repeat = runner.invoke(app, ["init"])
        assert result_repeat.exit_code != 0
        assert "already exists" in result_repeat.stdout

def test_add_basic():
    with runner.isolated_filesystem():
        # First init
        runner.invoke(app, ["init"])
        
        # Then add
        result = runner.invoke(app, ["add", "My Smell", "A sample description"])
        assert result.exit_code == 0
        assert "Created rule" in result.stdout
        assert "my-smell.smell.md" in result.stdout
        assert "Next Step:" in result.stdout
        assert "pre_filters" in result.stdout
        
        rule_file = Path(".codesmells/my-smell.smell.md")
        assert rule_file.exists()
        
        content = rule_file.read_text()
        assert "tau: 0.4" in content
        assert "# My Smell" in content
        assert "A sample description" in content
        assert "### Anti-Pattern" in content
        assert "### Refactoring" in content
