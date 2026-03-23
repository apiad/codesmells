from typer.testing import CliRunner
from codesmells.cli import app
from pathlib import Path
import json
import pytest

runner = CliRunner()

@pytest.fixture
def setup_project():
    with runner.isolated_filesystem() as fs:
        Path(".codesmells").mkdir()
        rule_content = """---
tau: 0.5
pre_filters:
  - "def bad_func"
---
### Anti-Pattern
```python
def bad_func():
    print($X)
```

### Refactoring
```python
def good_func():
    logger.info($X)
```
"""
        rule_path = Path(".codesmells/bad_rule.smell.md")
        rule_path.write_text(rule_content)
        
        target_content = "def bad_func():\n    print(y)\n"
        Path("target.py").write_text(target_content)
        
        runner.invoke(app, ["scan"])
        
        session_file = Path(".codesmells/session.json")
        data = json.loads(session_file.read_text())
        candidate_id = data["candidates"][0]["id"]
        
        yield {
            "fs": fs,
            "rule_path": rule_path,
            "candidate_id": candidate_id,
            "target_content": target_content
        }

def test_ignore_success(setup_project):
    c_id = setup_project["candidate_id"]
    # Template that matches snippet perfectly and passes Gate 3 (0.916 score < 0.95)
    template = "def bad_func():\n    print($Y)"
    
    result = runner.invoke(app, ["ignore", c_id, "--template", template])
    
    assert result.exit_code == 0
    assert "marked as IGNORED" in result.stdout
    assert "bad_rule.smell.md" in result.stdout
    
    # Check session.json status
    session_file = Path(".codesmells/session.json")
    data = json.loads(session_file.read_text())
    assert data["candidates"][0]["status"] == "IGNORED"
    
    # Check rule file content
    rule_content = setup_project["rule_path"].read_text()
    assert "### Safe" in rule_content
    assert "print($Y)" in rule_content

def test_ignore_gate1_failure(setup_project):
    c_id = setup_project["candidate_id"]
    template = "def completely_different():\n    $Z = 99"
    result = runner.invoke(app, ["ignore", c_id, "--template", template])
    assert result.exit_code != 0
    assert "Validation Failure (Gate 1)" in result.stdout

def test_ignore_gate2_failure(setup_project):
    c_id = setup_project["candidate_id"]
    template = "def bad_func():\n    print(y)"
    result = runner.invoke(app, ["ignore", c_id, "--template", template])
    # This might fail Gate 2 if it doesn't have $ or ...
    # Wait, the template has no $ or ...
    assert result.exit_code != 0
    assert "Validation Failure (Gate 2)" in result.stdout

def test_ignore_gate3_failure(setup_project):
    c_id = setup_project["candidate_id"]
    # Exactly the same as anti-pattern
    template = "def bad_func():\n    print($X)"
    result = runner.invoke(app, ["ignore", c_id, "--template", template])
    assert result.exit_code != 0
    assert "Validation Failure (Gate 3)" in result.stdout
