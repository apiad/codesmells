from typer.testing import CliRunner
from codesmells.cli import app

runner = CliRunner()

def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan directory for anti-patterns" in result.stdout

def test_scan_basic():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "Scanning" in result.stdout

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
        
        rule_file = Path(".codesmells/my-smell.smell.md")
        assert rule_file.exists()
        
        content = rule_file.read_text()
        assert "tau: 0.4" in content
        assert "# My Smell" in content
        assert "A sample description" in content
        assert "### Anti-Pattern" in content
        assert "### Refactoring" in content
