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
