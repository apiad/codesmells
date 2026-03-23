import os
import tempfile
import json
from pathlib import Path
from codesmells.storage import StorageManager
from codesmells.models import Rule, Candidate

def test_load_rules():
    with tempfile.TemporaryDirectory() as tmpdir:
        rule_content = """---
pre_filters:
  - "import .*db"
tau: 0.85
---

# Global Database Connection

### Anti-Pattern
```python
import database
db = database.connect()
```

### Safe
```python
from myapp import get_db
db = get_db()
```

### Refactoring
```python
from myapp import get_db
$DB = get_db()
```
"""
        rule_path = Path(tmpdir) / "global_db.smell.md"
        rule_path.write_text(rule_content)

        storage = StorageManager(root_dir=tmpdir)
        rules = storage.load_rules(tmpdir)

        assert len(rules) == 1
        rule = rules[0]
        assert rule.id == "global_db"
        assert rule.tau == 0.85
        assert "import .*db" in rule.pre_filters
        assert len(rule.anti_patterns) == 1
        assert "import database" in rule.anti_patterns[0]
        assert len(rule.safe_patterns) == 1
        assert "from myapp import get_db" in rule.safe_patterns[0]
        assert rule.refactor_template is not None
        assert "$DB = get_db()" in rule.refactor_template

def test_load_rules_no_frontmatter():
    with tempfile.TemporaryDirectory() as tmpdir:
        rule_content = """# Rule Name

### Anti-Pattern
```python
bad_code()
```
"""
        rule_path = Path(tmpdir) / "no_fm.smell.md"
        rule_path.write_text(rule_content)

        storage = StorageManager(root_dir=tmpdir)
        rules = storage.load_rules(tmpdir)

        assert len(rules) == 1
        rule = rules[0]
        assert rule.id == "no_fm"
        assert rule.tau == 0.8 # default
        assert rule.pre_filters == []
        assert rule.anti_patterns == ["bad_code()"]

def test_load_rules_multiple_blocks():
    with tempfile.TemporaryDirectory() as tmpdir:
        rule_content = """### Anti-Pattern
```python
bad1()
```

### Anti-Pattern
```python
bad2()
```

### Safe
```python
safe1()
```
```python
safe2()
```
"""
        rule_path = Path(tmpdir) / "multiple.smell.md"
        rule_path.write_text(rule_content)

        storage = StorageManager(root_dir=tmpdir)
        rules = storage.load_rules(tmpdir)

        assert len(rules) == 1
        rule = rules[0]
        assert rule.anti_patterns == ["bad1()", "bad2()"]
        assert rule.safe_patterns == ["safe1()", "safe2()"]

def test_storage_session_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageManager(root_dir=tmpdir)
        session_file = Path(tmpdir) / "session.json"
        assert session_file.exists()
        
        with open(session_file, 'r') as f:
            data = json.load(f)
            assert "candidates" in data
            assert data["candidates"] == []

def test_save_load_candidates():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageManager(root_dir=tmpdir)
        candidates = [
            Candidate(
                id="cand1",
                rule_id="rule1",
                file_path="src/main.py",
                line_num=10,
                raw_snippet="print('hello')",
                status="PENDING"
            )
        ]
        storage.save_candidates(candidates)
        
        loaded = storage.load_candidates()
        assert len(loaded) == 1
        assert loaded[0].id == "cand1"
        assert loaded[0].rule_id == "rule1"
        assert loaded[0].file_path == "src/main.py"
        assert loaded[0].line_num == 10
        assert loaded[0].raw_snippet == "print('hello')"
        assert loaded[0].status == "PENDING"

def test_update_candidate_status():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageManager(root_dir=tmpdir)
        candidates = [
            Candidate(
                id="cand1",
                rule_id="rule1",
                file_path="src/main.py",
                line_num=10,
                raw_snippet="print('hello')",
                status="PENDING"
            )
        ]
        storage.save_candidates(candidates)
        
        storage.update_candidate_status("cand1", "ACCEPTED")
        
        loaded = storage.load_candidates()
        assert len(loaded) == 1
        assert loaded[0].status == "ACCEPTED"
