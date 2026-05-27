# Codesmells Agent-First Rebuild — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild codesmells around the agent-first vision in `research/2026-05-27-agent-vision-design.md` — stateless CLI on microcli, windowed multi-fire scanner, curated rule library, pattern + per-site ignore machinery, CI gate.

**Architecture:** Hybrid — keep `lexer.py` + `alignment.py` (and their 17 tests) untouched. Rewrite everything else around new modules: `types.py` (dataclasses), `rules.py` (rule parsing + library), `scanner.py` (windowed matcher), `cli.py` (microcli commands). Stateless: rules are the only durable artifact. Each invocation is a complete computation.

**Tech Stack:** Python 3.13, `microcli-toolkit`, `pyyaml`. Test runner `pytest`. Build system `uv` + `hatchling`.

**Vertical slicing:** Slice 3 is the first end-to-end testable point — `codesmells scan` against a fixture finds smells. Slices 4–8 add commands incrementally. Slice 9 cleans up and releases.

---

## File Structure

**Created:**
- `src/codesmells/types.py` — `Token`, `Rule`, `Finding`, `IgnoreEntry` dataclasses (replaces `models.py`)
- `src/codesmells/rules.py` — `.smell.md` parsing, library access, language detection
- `src/codesmells/scanner.py` — windowed multi-fire matcher
- `src/codesmells/library/python/catch-all-exception.smell.md`
- `src/codesmells/library/python/print-instead-of-log.smell.md`
- `src/codesmells/library/python/mutable-default-argument.smell.md`
- `src/codesmells/library/python/bare-return.smell.md`
- `src/codesmells/library/generic/todo-fixme.smell.md`
- `tests/test_rules.py`
- `tests/test_scanner.py`
- `tests/test_cli_microcli.py`
- `tests/fixtures/sample_project/processor.py`
- `tests/fixtures/sample_project/utils.py`

**Modified:**
- `src/codesmells/__init__.py` — re-export new public API
- `src/codesmells/cli.py` — full rewrite around microcli
- `src/codesmells/main.py` — re-import wiring
- `src/codesmells/lexer.py` — import `Token` from `types.py` instead of `models.py`
- `src/codesmells/alignment.py` — drop spurious `2.0×` divisor (normalization fix); import `Token`/`TokenClass` from `types.py`
- `tests/test_alignment.py` — recalibrate two hardcoded score expectations after normalization fix
- `tests/test_lexer.py` — update `Token` import path
- `pyproject.toml` — remove `typer`/`rich`; add `microcli-toolkit`; bump to `0.3.0`; declare `[tool.hatch.build]` includes for the library
- `README.md` — replace Quick Start with new commands
- `CHANGELOG.md` — `0.3.0` entry summarizing the rebuild
- `TASKS.md` — close Milestone 4 entry; add Rebuild milestone marked complete on finish

**Deleted:**
- `src/codesmells/models.py`
- `src/codesmells/storage.py`
- `tests/test_cli.py`
- `tests/test_milestone3.py`
- `tests/test_storage.py`
- `repro_parser.py`
- `examples/.codesmells/session.json`

---

# Slice 0 — Preparation

### Task 0.1: Snapshot current green state

**Files:** none (verification only)

- [ ] **Step 1:** Run the full test suite to confirm baseline

Run: `uv sync && uv run pytest -q`
Expected: `33 passed`

- [ ] **Step 2:** Note the baseline in commit message preamble

If any test fails, STOP — investigate before starting the rebuild.

### Task 0.2: Delete dev debris

**Files:**
- Delete: `repro_parser.py`
- Delete: `examples/.codesmells/session.json`

- [ ] **Step 1:** Remove the files

Run:
```bash
rm repro_parser.py examples/.codesmells/session.json
```

- [ ] **Step 2:** Verify

Run: `git status -sb`
Expected: two deletions, no other changes.

- [ ] **Step 3:** Commit

```bash
git add -A
git commit -m "chore: remove dev debris (repro_parser, stale session.json)"
```

### Task 0.3: Swap CLI deps

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1:** Edit `pyproject.toml` — replace `dependencies = [...]` block

```toml
dependencies = [
    "microcli-toolkit>=0.4.0",
    "pyyaml>=6.0.3",
]
```

- [ ] **Step 2:** Re-sync

Run: `uv sync`
Expected: `microcli-toolkit` installed, `typer`/`rich` removed.

- [ ] **Step 3:** The existing CLI uses typer — it'll break import. Don't run tests yet; the next slices replace it.

- [ ] **Step 4:** Commit

```bash
git add pyproject.toml uv.lock
git commit -m "build: swap typer/rich for microcli-toolkit"
```

---

# Slice 1 — Types + rule parsing

### Task 1.1: Create `types.py`

**Files:**
- Create: `src/codesmells/types.py`

- [ ] **Step 1:** Write `src/codesmells/types.py`

```python
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class TokenClass(Enum):
    KEYWORD = auto()
    OPERATOR = auto()
    IDENTIFIER = auto()
    LITERAL = auto()
    GAP = auto()
    SIGIL = auto()


@dataclass(frozen=True)
class Token:
    token_class: TokenClass
    value: str
    weight: float = 1.0
    line_num: int = 0
    col_num: int = 0


@dataclass
class Rule:
    id: str
    lang: list[str] = field(default_factory=list)
    tau: float = 0.7
    severity: str = "warn"
    description: str = ""
    pre_filters: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    safe_patterns: list[str] = field(default_factory=list)
    refactor_template: Optional[str] = None
    refactor_explanation: str = ""
    source_path: Optional[str] = None  # absolute path to the .smell.md the rule was loaded from


@dataclass
class Finding:
    id: str
    rule_id: str
    file_path: str
    anchor_line: int
    end_line: int
    snippet: str
    bindings: dict[str, str] = field(default_factory=dict)
    score: float = 0.0


@dataclass
class IgnoreEntry:
    rule_id: str
    line: int  # the line the comment is ON; applies to itself + next non-blank
```

- [ ] **Step 2:** Repoint `lexer.py` import

Edit `src/codesmells/lexer.py` line 3:

```python
from codesmells.types import Token, TokenClass
```

- [ ] **Step 3:** Repoint `alignment.py` import

Edit `src/codesmells/alignment.py` line 2:

```python
from codesmells.types import Token, TokenClass
```

- [ ] **Step 4:** Repoint `tests/test_lexer.py` and `tests/test_alignment.py`

In both files, change `from codesmells.models import ...` to `from codesmells.types import ...`.

- [ ] **Step 5:** Sanity check — lexer + alignment tests should still pass

The CLI is broken; restrict pytest to the two known-good test files:

Run: `uv run pytest tests/test_lexer.py tests/test_alignment.py -q`
Expected: lexer + alignment tests still pass.

- [ ] **Step 6:** Commit

```bash
git add src/codesmells/types.py src/codesmells/lexer.py src/codesmells/alignment.py tests/test_lexer.py tests/test_alignment.py
git commit -m "refactor: introduce types.py; lexer + alignment import from it"
```

### Task 1.2: Delete `models.py`

**Files:**
- Delete: `src/codesmells/models.py`

- [ ] **Step 1:** Confirm no other module imports `codesmells.models`

Run: `grep -rn "from codesmells.models" src/ tests/`
Expected: only matches inside `storage.py` and `cli.py` (which we're rewriting); none elsewhere.

- [ ] **Step 2:** Delete `models.py`

Run: `rm src/codesmells/models.py`

- [ ] **Step 3:** Commit (storage.py + old cli.py won't import — that's fine, they get rewritten next)

```bash
git add -A
git commit -m "refactor: drop models.py (replaced by types.py)"
```

### Task 1.3: Write failing tests for `rules.parse`

**Files:**
- Create: `tests/test_rules.py`

- [ ] **Step 1:** Write the test file

```python
from pathlib import Path
import pytest
from codesmells.rules import parse_rule_file, RuleParseError


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
```

- [ ] **Step 2:** Run — verify imports fail (module doesn't exist yet)

Run: `uv run pytest tests/test_rules.py -q`
Expected: `ModuleNotFoundError: codesmells.rules`

### Task 1.4: Implement `rules.parse_rule_file`

**Files:**
- Create: `src/codesmells/rules.py`

- [ ] **Step 1:** Write `src/codesmells/rules.py`

```python
import re
import yaml
from pathlib import Path
from codesmells.types import Rule


class RuleParseError(Exception):
    pass


_CODE_BLOCK = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)


def parse_rule_file(path: Path) -> Rule:
    """Parse a .smell.md file into a Rule. Raises RuleParseError on malformed input."""
    text = path.read_text()
    frontmatter, body = _split_frontmatter(text)
    if not frontmatter.get("id"):
        raise RuleParseError(f"{path}: missing required field 'id'")

    anti = _extract_code_blocks(body, "### Anti-Pattern")
    if not anti:
        raise RuleParseError(f"{path}: missing required section '### Anti-Pattern' with code block")
    safe = _extract_code_blocks(body, "### Safe")
    refactor = _extract_code_blocks(body, "### Refactoring")

    return Rule(
        id=str(frontmatter["id"]),
        lang=list(frontmatter.get("lang", [])),
        tau=float(frontmatter.get("tau", 0.7)),
        severity=str(frontmatter.get("severity", "warn")),
        description=_extract_description(body),
        pre_filters=list(frontmatter.get("pre_filters", [])),
        anti_patterns=anti,
        safe_patterns=safe,
        refactor_template=refactor[0] if refactor else None,
        refactor_explanation=_extract_explanation(body, "### Refactoring"),
        source_path=str(path),
    )


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise RuleParseError(f"invalid YAML frontmatter: {e}") from e
    return fm, parts[2]


def _section(body: str, header: str) -> str:
    parts = body.split(header, 1)
    if len(parts) < 2:
        return ""
    rest = parts[1]
    nxt = re.search(r"\n#{1,3} ", rest)
    return rest[:nxt.start()] if nxt else rest


def _extract_code_blocks(body: str, header: str) -> list[str]:
    section = _section(body, header)
    return [m.group(1).strip() for m in _CODE_BLOCK.finditer(section)]


def _extract_description(body: str) -> str:
    # Text from the first H1 (or start) up to the first ### header
    nxt = re.search(r"\n### ", body)
    head = body[:nxt.start()] if nxt else body
    head = re.sub(r"^#\s+.*\n", "", head, flags=re.MULTILINE)  # drop H1 title line
    return head.strip()


def _extract_explanation(body: str, header: str) -> str:
    section = _section(body, header)
    return _CODE_BLOCK.sub("", section).strip()
```

- [ ] **Step 2:** Run the test file

Run: `uv run pytest tests/test_rules.py -q`
Expected: 4 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/rules.py tests/test_rules.py
git commit -m "feat(rules): parse .smell.md into Rule with lang/severity/id frontmatter"
```

### Task 1.5: Add `load_rules_from_dir` + language detection

**Files:**
- Modify: `src/codesmells/rules.py`
- Modify: `tests/test_rules.py`

- [ ] **Step 1:** Add failing tests at the bottom of `tests/test_rules.py`

```python
from codesmells.rules import load_rules_from_dir, detect_languages


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
    (tmp_path / "bad.smell.md").write_text("not yaml\n---\nblah")
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
```

- [ ] **Step 2:** Run — expect import errors

Run: `uv run pytest tests/test_rules.py::test_load_rules_from_dir -q`
Expected: ImportError or AttributeError.

- [ ] **Step 3:** Append to `src/codesmells/rules.py`

```python
import sys


_LANG_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".md": "markdown",
}


def load_rules_from_dir(dir_path: Path) -> list[Rule]:
    """Load every *.smell.md from dir_path. Warn on malformed; skip them."""
    rules = []
    for p in sorted(Path(dir_path).glob("*.smell.md")):
        try:
            rules.append(parse_rule_file(p))
        except RuleParseError as e:
            print(f"warn: rule {p.name}: {e}", file=sys.stderr)
    return rules


def detect_languages(root: Path) -> set[str]:
    """Walk root, return set of language tags inferred from file extensions."""
    seen = set()
    for p in Path(root).rglob("*"):
        if not p.is_file():
            continue
        # Skip common noise directories
        if any(part in {".git", ".venv", "node_modules", ".codesmells"} for part in p.parts):
            continue
        lang = _LANG_BY_EXT.get(p.suffix)
        if lang:
            seen.add(lang)
    return seen
```

- [ ] **Step 4:** Run tests

Run: `uv run pytest tests/test_rules.py -q`
Expected: 7 passed.

- [ ] **Step 5:** Commit

```bash
git add src/codesmells/rules.py tests/test_rules.py
git commit -m "feat(rules): add load_rules_from_dir + language detection"
```

### Task 1.6: Library access helpers

**Files:**
- Modify: `src/codesmells/rules.py`
- Modify: `tests/test_rules.py`
- Modify: `pyproject.toml` (declare library files as package data)

- [ ] **Step 1:** Add a temporary fixture library at `src/codesmells/library/python/sample.smell.md` so the test has something to read

```bash
mkdir -p src/codesmells/library/python
```

Write `src/codesmells/library/python/sample.smell.md`:

```markdown
---
id: sample
lang: [python]
tau: 0.7
pre_filters: []
---

# Sample

### Anti-Pattern

```python
pass
```

### Refactoring

```python
pass
```
```

- [ ] **Step 2:** Append failing test to `tests/test_rules.py`

```python
from codesmells.rules import library_rules_for_languages


def test_library_rules_for_languages_returns_python_rules():
    rules = library_rules_for_languages({"python"})
    ids = {r.id for r in rules}
    assert "sample" in ids


def test_library_rules_for_languages_filters_by_lang():
    rules = library_rules_for_languages({"go"})  # no go rules yet
    assert all("python" not in r.lang for r in rules)
```

- [ ] **Step 3:** Run — expect failure

Run: `uv run pytest tests/test_rules.py::test_library_rules_for_languages_returns_python_rules -q`
Expected: ImportError.

- [ ] **Step 4:** Append to `src/codesmells/rules.py`

```python
import importlib.resources


def library_rules_for_languages(langs: set[str]) -> list[Rule]:
    """Return library rules whose `lang` intersects `langs` OR whose lang is empty/['any']."""
    rules = _load_library_rules()
    out = []
    for r in rules:
        rlangs = set(r.lang)
        if not rlangs or "any" in rlangs or rlangs & langs:
            out.append(r)
    return out


def _load_library_rules() -> list[Rule]:
    rules = []
    pkg = importlib.resources.files("codesmells.library")
    for child in pkg.iterdir():
        if not child.is_dir():
            continue
        for entry in child.iterdir():
            if entry.name.endswith(".smell.md"):
                with importlib.resources.as_file(entry) as p:
                    try:
                        rules.append(parse_rule_file(p))
                    except RuleParseError as e:
                        print(f"warn: library rule {entry.name}: {e}", file=sys.stderr)
    return rules
```

- [ ] **Step 5:** Update `pyproject.toml` to include `library/*` as package data. Add at top level (or in `[tool.hatch.build.targets.wheel]`):

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/codesmells"]

[tool.hatch.build.targets.wheel.force-include]
"src/codesmells/library" = "codesmells/library"
```

- [ ] **Step 6:** Re-sync

Run: `uv sync`
Expected: no errors.

- [ ] **Step 7:** Run tests

Run: `uv run pytest tests/test_rules.py -q`
Expected: 9 passed.

- [ ] **Step 8:** Commit

```bash
git add src/codesmells/rules.py src/codesmells/library/ tests/test_rules.py pyproject.toml
git commit -m "feat(rules): library access via importlib.resources"
```

---

# Slice 2 — Scanner with windowed multi-fire

> Note: `alignment.py` and its tests remain untouched. The existing `/ (2.0 × Σ_t.weight)` normalization is correct math (see spec §5.4 update from 2026-05-27): the match-score function multiplies by 2.0 for exact matches, so dividing by `2.0 × Σ_t.weight` produces scores in `[0, 1]`. Thresholds throughout this plan are calibrated to that range.

### Task 2.2: Failing scanner test — single match

**Files:**
- Create: `tests/test_scanner.py`

- [ ] **Step 1:** Write `tests/test_scanner.py`

```python
from pathlib import Path
import pytest
from codesmells.scanner import scan_path
from codesmells.rules import parse_rule_file


def _make_rule(tmp_path: Path, name: str, anti: str, pre_filter: str, tau: float = 0.4):
    p = tmp_path / f"{name}.smell.md"
    p.write_text(f"""---
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

### Refactoring

```python
pass
```
""")
    return parse_rule_file(p)


def _make_source(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body)
    return p


def test_scan_finds_single_match(tmp_path):
    rule = _make_rule(tmp_path, "catch_all", "except Exception as $VAR:\n    ...", "except Exception")
    source = _make_source(tmp_path, "src.py", """
def f():
    try:
        run()
    except Exception as e:
        log(e)
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "src.py"]
    assert len(findings_in_src) == 1
    f = findings_in_src[0]
    assert f.rule_id == "catch_all"
    assert f.anchor_line >= 4  # except is at line 5 in the source
    assert f.bindings.get("$VAR") == "e"
```

- [ ] **Step 2:** Run — expect import failure

Run: `uv run pytest tests/test_scanner.py::test_scan_finds_single_match -q`
Expected: ModuleNotFoundError: codesmells.scanner.

### Task 2.3: Implement the windowed scanner

**Files:**
- Create: `src/codesmells/scanner.py`

- [ ] **Step 1:** Write `src/codesmells/scanner.py`

```python
import hashlib
import re
from pathlib import Path
from codesmells.types import Rule, Finding
from codesmells.lexer import ProbabilisticLexer
from codesmells.alignment import FuzzyAlignmentEngine


_TAU_SAFE = 0.7  # threshold for safe-pattern guard
_MIN_WINDOW = 20  # token-window minimum size
_SOURCE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb"}


def scan_path(root: Path, rules: list[Rule]) -> list[Finding]:
    """Scan every source file under root against every rule; return all findings."""
    findings: list[Finding] = []
    lexer = ProbabilisticLexer()
    engine = FuzzyAlignmentEngine()
    for f in _iter_source_files(Path(root)):
        try:
            text = f.read_text()
        except UnicodeDecodeError:
            continue
        findings.extend(_scan_file(f, text, rules, lexer, engine))
    return findings


def _iter_source_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", ".codesmells", "__pycache__"} for part in p.parts):
            continue
        if p.suffix in _SOURCE_EXTS:
            yield p


def _scan_file(file_path: Path, text: str, rules: list[Rule], lexer, engine) -> list[Finding]:
    file_tokens = lexer.tokenize(text)
    if not file_tokens:
        return []
    ignore_set = _harvest_ignores(text, file_path.suffix)
    out: list[Finding] = []
    seen_anchors: set[tuple[str, int]] = set()  # (rule_id, anchor_line)

    for rule in rules:
        # Pre-filter gate
        if any(pf not in text for pf in rule.pre_filters):
            continue
        for anti in rule.anti_patterns:
            anti_tokens = lexer.tokenize(anti)
            if not anti_tokens:
                continue
            window_size = max(_MIN_WINDOW, 2 * len(anti_tokens))
            for window_start in range(0, len(file_tokens), max(1, window_size // 2)):
                window = file_tokens[window_start:window_start + window_size]
                if len(window) < len(anti_tokens):
                    continue
                score, bindings, indices = engine.align(window, anti_tokens)
                if score < rule.tau:
                    continue
                if not indices:
                    continue
                # Translate local window indices to absolute file token indices
                abs_start = window_start + indices[0]
                abs_end = window_start + indices[1]
                anchor_line = window[indices[0]].line_num
                end_line = window[indices[1]].line_num

                # Per-site ignore check
                if (rule.id, anchor_line) in ignore_set:
                    continue

                # Safe-pattern guard
                if _matches_any_safe(window, rule, lexer, engine):
                    continue

                # Dedup by anchor
                key = (rule.id, anchor_line)
                if key in seen_anchors:
                    continue
                seen_anchors.add(key)

                snippet = _build_snippet(text, anchor_line, end_line)
                fid = _finding_id(rule.id, str(file_path), anchor_line, snippet)
                out.append(Finding(
                    id=fid,
                    rule_id=rule.id,
                    file_path=str(file_path),
                    anchor_line=anchor_line,
                    end_line=end_line,
                    snippet=snippet,
                    bindings=dict(bindings) if bindings else {},
                    score=score,
                ))
    return out


def _matches_any_safe(window, rule, lexer, engine) -> bool:
    for safe in rule.safe_patterns:
        st = lexer.tokenize(safe)
        if not st:
            continue
        s, _, _ = engine.align(window, st)
        if s >= _TAU_SAFE:
            return True
    return False


def _harvest_ignores(text: str, suffix: str) -> set[tuple[str, int]]:
    """Return a set of (rule_id, line_num_the_smell_lands_on).

    Comment applies to its own line AND the next non-blank source line.
    """
    out: set[tuple[str, int]] = set()
    lines = text.splitlines()
    comment_prefix = _comment_prefix(suffix)
    pattern = re.compile(re.escape(comment_prefix) + r"\s*codesmells:\s*ignore\s+(\S+)")
    for i, line in enumerate(lines, start=1):
        m = pattern.search(line)
        if not m:
            continue
        rule_id = m.group(1).rstrip(",")
        out.add((rule_id, i))
        # next non-blank line
        for j in range(i + 1, len(lines) + 1):
            if lines[j - 1].strip():
                out.add((rule_id, j))
                break
    return out


def _comment_prefix(suffix: str) -> str:
    if suffix in {".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}:
        return "//"
    return "#"


def _build_snippet(text: str, anchor_line: int, end_line: int, context: int = 5) -> str:
    lines = text.splitlines()
    start = max(0, anchor_line - 1 - context)
    end = min(len(lines), end_line + context)
    return "\n".join(lines[start:end])


def _finding_id(rule_id: str, file_path: str, anchor_line: int, snippet: str) -> str:
    canonical = re.sub(r"\s+", " ", snippet).strip()
    payload = f"{rule_id}:{file_path}:{anchor_line}:{canonical}"
    return hashlib.md5(payload.encode()).hexdigest()[:8]
```

- [ ] **Step 2:** Run the failing test

Run: `uv run pytest tests/test_scanner.py -q`
Expected: 1 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/scanner.py tests/test_scanner.py
git commit -m "feat(scanner): windowed multi-fire matcher with safe-pattern guard"
```

### Task 2.4: Add tests for multi-fire and per-site ignores

**Files:**
- Modify: `tests/test_scanner.py`

- [ ] **Step 1:** Append to `tests/test_scanner.py`

```python
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
    assert len(findings_in_src) == 3
    anchors = sorted(f.anchor_line for f in findings_in_src)
    assert anchors == [3, 4, 5]


def test_scan_skips_safe_patterns(tmp_path):
    rule_text = """---
id: print_rule
lang: [python]
tau: 0.4
pre_filters:
  - "print"
---

### Anti-Pattern

```python
print($MSG)
```

### Safe

```python
print($MSG, file=sys.stderr)
```
"""
    (tmp_path / "print_rule.smell.md").write_text(rule_text)
    rule = parse_rule_file(tmp_path / "print_rule.smell.md")
    _make_source(tmp_path, "mixed.py", """
print("loud")
print("stderr", file=sys.stderr)
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "mixed.py"]
    # Only the bare print should fire; the file=sys.stderr variant should be suppressed
    assert len(findings_in_src) == 1
    assert findings_in_src[0].anchor_line == 2


def test_scan_respects_per_site_ignore(tmp_path):
    rule = _make_rule(tmp_path, "catch_all", "except Exception as $VAR:\n    ...", "except Exception")
    _make_source(tmp_path, "ig.py", """
try:
    run()
# codesmells: ignore catch_all
except Exception as e:
    pass
""")
    findings = scan_path(tmp_path, [rule])
    findings_in_src = [f for f in findings if Path(f.file_path).name == "ig.py"]
    assert findings_in_src == []


def test_finding_id_is_deterministic(tmp_path):
    rule = _make_rule(tmp_path, "catch_all", "except Exception as $VAR:\n    ...", "except Exception")
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
```

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_scanner.py -q`
Expected: 5 passed (all 5 scanner tests).

If `test_scan_finds_multiple_instances` reports fewer than 3 findings, the windowing step needs to be smaller — adjust the window stride. If `test_scan_skips_safe_patterns` fails, lower `_TAU_SAFE` to debug; the safe-pattern's score should exceed the constant.

- [ ] **Step 3:** Commit

```bash
git add tests/test_scanner.py
git commit -m "test(scanner): multi-fire, safe guard, per-site ignore, deterministic id"
```

---

# Slice 3 — First library rules + scan command (end-to-end)

### Task 3.1: Write the curated library rules

**Files:**
- Create: `src/codesmells/library/python/catch-all-exception.smell.md`
- Create: `src/codesmells/library/python/print-instead-of-log.smell.md`
- Create: `src/codesmells/library/python/mutable-default-argument.smell.md`
- Create: `src/codesmells/library/python/bare-return.smell.md`
- Create: `src/codesmells/library/generic/todo-fixme.smell.md`
- Delete: `src/codesmells/library/python/sample.smell.md`

- [ ] **Step 1:** Create `src/codesmells/library/python/catch-all-exception.smell.md`

```markdown
---
id: catch-all-exception
lang: [python]
tau: 0.5
severity: warn
pre_filters:
  - "except Exception"
---

# Avoid Catch-All Exceptions

Catching `Exception` broadly hides errors. Catch specific types you expect to handle.

### Anti-Pattern

```python
try:
    ...
except Exception as $VAR:
    ...
```

### Refactoring

Replace `Exception` with the specific type you expect.

```python
try:
    ...
except ValueError as $VAR:
    ...
```
```

- [ ] **Step 2:** Create `src/codesmells/library/python/print-instead-of-log.smell.md`

```markdown
---
id: print-instead-of-log
lang: [python]
tau: 0.5
severity: info
pre_filters:
  - "print"
---

# Use Logging Instead of Print

Use the `logging` module instead of `print` in production code — `print` cannot be redirected, formatted, or filtered by severity.

### Anti-Pattern

```python
print($MESSAGE)
```

### Refactoring

```python
logger.info($MESSAGE)
```
```

- [ ] **Step 3:** Create `src/codesmells/library/python/mutable-default-argument.smell.md`

```markdown
---
id: mutable-default-argument
lang: [python]
tau: 0.5
severity: warn
pre_filters:
  - "def "
---

# Mutable Default Argument

Default values are evaluated once at function definition. Mutable defaults (`[]`, `{}`) are shared across calls and cause subtle bugs.

### Anti-Pattern

```python
def $FUNC($ARG=[]):
    ...
```

### Refactoring

Use `None` as the sentinel and create the mutable inside the body.

```python
def $FUNC($ARG=None):
    if $ARG is None:
        $ARG = []
    ...
```
```

- [ ] **Step 4:** Create `src/codesmells/library/python/bare-return.smell.md`

```markdown
---
id: bare-return
lang: [python]
tau: 0.6
severity: info
pre_filters:
  - "return"
---

# Bare Return

A bare `return` in a function that elsewhere returns a value is usually a placeholder or accidental early-exit. Prefer `return None` explicitly when intentional.

### Anti-Pattern

```python
def $FUNC(...):
    ...
    return
    ...
```

### Refactoring

```python
def $FUNC(...):
    ...
    return None
    ...
```
```

- [ ] **Step 5:** Create `src/codesmells/library/generic/todo-fixme.smell.md`

```markdown
---
id: todo-fixme
lang: [any]
tau: 0.5
severity: info
pre_filters:
  - "TODO"
---

# TODO / FIXME Marker

A `TODO` or `FIXME` comment is unfinished work. Either resolve it or convert to a tracked issue.

### Anti-Pattern

```python
# TODO: ...
```

### Refactoring

Track the work in your issue tracker and remove the inline marker.

```python
# (resolved)
```
```

- [ ] **Step 6:** Remove the sample rule

Run: `rm src/codesmells/library/python/sample.smell.md`

- [ ] **Step 7:** Update the `test_library_rules_for_languages_returns_python_rules` test to assert against the real rules

In `tests/test_rules.py`, change:

```python
def test_library_rules_for_languages_returns_python_rules():
    rules = library_rules_for_languages({"python"})
    ids = {r.id for r in rules}
    assert "sample" in ids
```

to:

```python
def test_library_rules_for_languages_returns_python_rules():
    rules = library_rules_for_languages({"python"})
    ids = {r.id for r in rules}
    assert "catch-all-exception" in ids
    assert "print-instead-of-log" in ids
```

- [ ] **Step 8:** Run

Run: `uv run pytest tests/test_rules.py tests/test_scanner.py -q`
Expected: 14 passed.

- [ ] **Step 9:** Commit

```bash
git add src/codesmells/library/ tests/test_rules.py
git commit -m "feat(library): curated rule set — catch-all/print/mutable-default/bare-return/todo"
```

### Task 3.2: Write the fixture project

**Files:**
- Create: `tests/fixtures/sample_project/processor.py`
- Create: `tests/fixtures/sample_project/utils.py`

- [ ] **Step 1:** Create `tests/fixtures/sample_project/processor.py`

```python
import json


def process_user_data(file_path):
    print(f"Starting {file_path}")
    try:
        with open(file_path) as f:
            data = json.load(f)
        return [d for d in data if d.get("active")]
    except Exception as e:
        print(f"error: {e}")
        return None


def cache_results(items, cache={}):
    for item in items:
        cache[item["id"]] = item
    return cache
```

- [ ] **Step 2:** Create `tests/fixtures/sample_project/utils.py`

```python
def shorten(s, max_len=80):
    if len(s) > max_len:
        return s[:max_len] + "..."
    return


def find_first(items, predicate):
    # TODO: also return index
    for item in items:
        if predicate(item):
            return item
    return None
```

- [ ] **Step 3:** Commit

```bash
git add tests/fixtures/sample_project/
git commit -m "test(fixtures): sample_project with known smell inventory"
```

### Task 3.3: Write the `scan` command via microcli — TDD

**Files:**
- Create: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Write `tests/test_cli_microcli.py`

```python
import subprocess
from pathlib import Path
import shutil

FIXTURE = Path(__file__).parent / "fixtures" / "sample_project"


def _prepare_project(tmp_path: Path) -> Path:
    """Copy the fixture and seed .codesmells/ with the bundled python rules."""
    proj = tmp_path / "proj"
    shutil.copytree(FIXTURE, proj)
    (proj / ".codesmells").mkdir()
    # Find the installed library and copy a couple of rules into the project
    import codesmells.rules as r
    for rule in r.library_rules_for_languages({"python"}):
        if rule.id in {"catch-all-exception", "print-instead-of-log", "mutable-default-argument", "bare-return"}:
            target = proj / ".codesmells" / f"{rule.id}.smell.md"
            target.write_text(Path(rule.source_path).read_text())
    return proj


def _run(args, cwd):
    return subprocess.run(
        ["uv", "run", "codesmells", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_scan_reports_findings(tmp_path):
    proj = _prepare_project(tmp_path)
    result = _run(["scan", "."], cwd=proj)
    assert result.returncode == 0
    # At least the catch-all and at least one print should be reported
    assert "catch-all-exception" in result.stdout
    assert "print-instead-of-log" in result.stdout
    # The summary line
    assert "smells" in result.stdout
```

- [ ] **Step 2:** Run — expect failure (cli.py is still the old typer-based one and `typer` isn't installed)

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: failure (import error or typer-missing).

### Task 3.4: Replace `cli.py` with microcli-based scaffolding + `scan`

**Files:**
- Modify (full rewrite): `src/codesmells/cli.py`
- Modify: `src/codesmells/__init__.py`
- Modify: `src/codesmells/main.py`
- Delete: `src/codesmells/storage.py`
- Delete: `tests/test_cli.py`
- Delete: `tests/test_milestone3.py`
- Delete: `tests/test_storage.py`

- [ ] **Step 1:** Replace `src/codesmells/cli.py` entirely with

```python
from pathlib import Path
import microcli as m
from codesmells.rules import load_rules_from_dir
from codesmells.scanner import scan_path

app = m.App(
    name="codesmells",
    description="Deterministic code smell detection for agentic refactoring",
)


def _load_project_rules(project_dir: Path):
    rules_dir = project_dir / ".codesmells"
    if not rules_dir.is_dir():
        m.fail(f"no rules — run 'codesmells init' from {project_dir} to set up")
    rules = load_rules_from_dir(rules_dir)
    if not rules:
        m.fail(f"no rules in {rules_dir} — add some with 'codesmells init' or 'codesmells add <rule>'")
    return rules


def _run_scan(directory: str):
    project_dir = Path(directory).resolve()
    rules = _load_project_rules(project_dir)
    return scan_path(project_dir, rules), project_dir


@app.command
def scan(directory: str = "."):
    """Scan a directory for smells."""
    findings, project_dir = _run_scan(directory)
    if not findings:
        m.ok(f"no smells in {directory}")
        return
    file_count = len({f.file_path for f in findings})
    m.info(f"{len(findings)} smells in {file_count} file{'s' if file_count != 1 else ''}")
    print()
    for f in findings:
        rel = Path(f.file_path).relative_to(project_dir) if Path(f.file_path).is_relative_to(project_dir) else Path(f.file_path)
        print(f"{f.id}  {f.rule_id:24s}  {rel}:{f.anchor_line}")
    print()
    m.info(f"next: codesmells inspect {findings[0].id}")


def main():
    app.main()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2:** Update `src/codesmells/__init__.py`

```python
from codesmells.cli import main

__all__ = ["main"]
```

- [ ] **Step 3:** Update `src/codesmells/main.py`

```python
from codesmells.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4:** Delete dead modules + their tests

Run:
```bash
rm src/codesmells/storage.py
rm tests/test_cli.py tests/test_milestone3.py tests/test_storage.py
```

- [ ] **Step 5:** Run the CLI test

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 1 passed.

- [ ] **Step 6:** Run the full suite

Run: `uv run pytest -q`
Expected: lexer (8) + alignment (17) + rules (9) + scanner (5) + cli (1) = 40 passed.

- [ ] **Step 7:** Smoke-check the CLI by hand

Run from `tests/fixtures/sample_project/`:
```bash
cd tests/fixtures/sample_project && cp ../../src/codesmells/library/python/*.smell.md .codesmells/ 2>/dev/null || mkdir -p .codesmells
# manual sanity only — not a test gate
```

(This is a sanity step; the test in step 5 is the real gate.)

- [ ] **Step 8:** Commit

```bash
git add -A
git commit -m "feat(cli): rewrite around microcli; scan command end-to-end"
```

---

# Slice 4 — inspect + suggest

### Task 4.1: Add `inspect` — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append to `tests/test_cli_microcli.py`

```python
def test_inspect_prints_finding_detail(tmp_path):
    proj = _prepare_project(tmp_path)
    scan_out = _run(["scan", "."], cwd=proj).stdout
    # Grab the first finding id from the scan output
    first_id = None
    for line in scan_out.splitlines():
        parts = line.split()
        if parts and len(parts[0]) == 8 and parts[0].isalnum():
            first_id = parts[0]
            break
    assert first_id, "scan output didn't surface a finding id"

    result = _run(["inspect", first_id], cwd=proj)
    assert result.returncode == 0
    assert "rule:" in result.stdout
    assert "file:" in result.stdout
    assert "why:" in result.stdout


def test_inspect_unknown_id_fails(tmp_path):
    proj = _prepare_project(tmp_path)
    result = _run(["inspect", "deadbeef"], cwd=proj)
    assert result.returncode != 0
    assert "deadbeef" in (result.stdout + result.stderr)
```

- [ ] **Step 2:** Run — expect failure (command not defined)

Run: `uv run pytest tests/test_cli_microcli.py::test_inspect_prints_finding_detail -q`
Expected: nonzero rc; microcli reports unknown command.

### Task 4.2: Implement `inspect`

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append to `src/codesmells/cli.py` (before `main`)

```python
def _find_finding(directory: str, id: str):
    findings, project_dir = _run_scan(directory)
    for f in findings:
        if f.id == id:
            return f, project_dir
    m.fail(f"no finding with id {id} — run 'codesmells scan' to refresh ids")


def _load_rule(rule_id: str, project_dir: Path):
    rules = load_rules_from_dir(project_dir / ".codesmells")
    for r in rules:
        if r.id == rule_id:
            return r
    m.fail(f"rule {rule_id} not found in {project_dir}/.codesmells")


@app.command
def inspect(id: str, directory: str = "."):
    """Print the local detail of a single finding."""
    finding, project_dir = _find_finding(directory, id)
    rule = _load_rule(finding.rule_id, project_dir)
    rel = Path(finding.file_path).relative_to(project_dir) if Path(finding.file_path).is_relative_to(project_dir) else Path(finding.file_path)
    print(f"rule:  {finding.rule_id}")
    print(f"file:  {rel}:{finding.anchor_line}")
    print()
    # Snippet with line numbers
    start_line = max(1, finding.anchor_line - 2)
    for offset, line in enumerate(finding.snippet.splitlines()):
        n = start_line + offset
        marker = " "
        print(f"  {n:4d} {marker} {line}")
    print()
    if finding.bindings:
        joined = ", ".join(f"{k}={v}" for k, v in finding.bindings.items())
        print(f"bindings: {joined}")
        print()
    if rule.description:
        print(f"why: {rule.description.splitlines()[0]}")
        print()
    m.info(f"next: codesmells suggest {finding.id} | codesmells ignore {finding.id} [--here]")
```

- [ ] **Step 2:** Run inspect tests

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 3 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): inspect command — per-finding detail with snippet + bindings"
```

### Task 4.3: Add `suggest` — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_suggest_prints_hydrated_refactor(tmp_path):
    proj = _prepare_project(tmp_path)
    scan_out = _run(["scan", "."], cwd=proj).stdout
    # Find a catch-all-exception finding id
    target_id = None
    for line in scan_out.splitlines():
        if "catch-all-exception" in line:
            target_id = line.split()[0]
            break
    assert target_id, "no catch-all-exception finding in fixture"
    result = _run(["suggest", target_id], cwd=proj)
    assert result.returncode == 0
    assert "ValueError" in result.stdout  # the refactor template uses ValueError
    # And the bound variable name should have been substituted
    assert "$VAR" not in result.stdout
```

- [ ] **Step 2:** Run — expect failure

Run: `uv run pytest tests/test_cli_microcli.py::test_suggest_prints_hydrated_refactor -q`
Expected: unknown command.

### Task 4.4: Implement `suggest`

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append to `cli.py`

```python
import re as _re


def _hydrate(template: str, bindings: dict[str, str]) -> str:
    # Substitute longer sigils first so $DB_POOL beats $DB
    out = template
    for sigil, value in sorted(bindings.items(), key=lambda kv: len(kv[0]), reverse=True):
        out = _re.sub(_re.escape(sigil) + r"\b", value, out)
    return out


@app.command
def suggest(id: str, directory: str = "."):
    """Print the hydrated refactor template for a finding."""
    finding, project_dir = _find_finding(directory, id)
    rule = _load_rule(finding.rule_id, project_dir)
    if not rule.refactor_template:
        m.fail(f"rule {rule.id} has no refactoring template")
    hydrated = _hydrate(rule.refactor_template, finding.bindings)
    if rule.refactor_explanation:
        print(rule.refactor_explanation)
        print()
    print(hydrated)
```

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 4 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): suggest command — hydrated refactor template"
```

---

# Slice 5 — Ignore (pattern + per-site)

### Task 5.1: Pattern-mode ignore — failing tests

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_ignore_pattern_mode_passes_three_gates(tmp_path):
    proj = _prepare_project(tmp_path)
    scan_out = _run(["scan", "."], cwd=proj).stdout
    target_id = None
    for line in scan_out.splitlines():
        if "catch-all-exception" in line:
            target_id = line.split()[0]
            break
    assert target_id

    safe_template = "try:\n    ...\nexcept ValueError as $VAR:\n    ...\n"
    result = subprocess.run(
        ["uv", "run", "codesmells", "ignore", target_id],
        cwd=proj,
        input=safe_template,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"

    # Re-scan — the catch-all finding should now be suppressed by the safe pattern
    rescan = _run(["scan", "."], cwd=proj)
    assert "catch-all-exception" not in rescan.stdout


def test_ignore_pattern_mode_fails_on_too_loose_template(tmp_path):
    proj = _prepare_project(tmp_path)
    scan_out = _run(["scan", "."], cwd=proj).stdout
    target_id = None
    for line in scan_out.splitlines():
        if "catch-all-exception" in line:
            target_id = line.split()[0]
            break

    too_loose = "x = 1\n"  # nothing like the snippet
    result = subprocess.run(
        ["uv", "run", "codesmells", "ignore", target_id],
        cwd=proj,
        input=too_loose,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "gate 1" in combined or "faithful" in combined
```

- [ ] **Step 2:** Run — expect failure

Run: `uv run pytest tests/test_cli_microcli.py::test_ignore_pattern_mode_passes_three_gates -q`
Expected: unknown command.

### Task 5.2: Implement pattern-mode ignore

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append to `cli.py`

```python
from codesmells.lexer import ProbabilisticLexer
from codesmells.alignment import FuzzyAlignmentEngine


def _three_gates(template: str, finding, rule):
    lex = ProbabilisticLexer()
    eng = FuzzyAlignmentEngine()
    t_tokens = lex.tokenize(template)
    s_tokens = lex.tokenize(finding.snippet)

    # Gate 1: faithful
    score1, _, _ = eng.align(s_tokens, t_tokens)
    gate1_ok = score1 >= 0.7

    # Gate 2: generic — contains a sigil or gap
    gate2_ok = any(tok.value.startswith("$") or tok.value == "..." for tok in t_tokens)

    # Gate 3: distinct from anti-patterns
    gate3_ok = True
    worst = 0.0
    for anti in rule.anti_patterns:
        a_tokens = lex.tokenize(anti)
        s, _, _ = eng.align(a_tokens, t_tokens)
        worst = max(worst, s)
        if s >= 0.9:
            gate3_ok = False
    return [
        ("gate 1 (faithful)", gate1_ok, f"score {score1:.2f} (need >= 0.7)"),
        ("gate 2 (generic)", gate2_ok, "must contain $SIGIL or ..."),
        ("gate 3 (distinct)", gate3_ok, f"worst anti-pattern match {worst:.2f} (need < 0.9)"),
    ]


def _append_safe(rule, template: str):
    path = Path(rule.source_path)
    content = path.read_text()
    block = f"```python\n{template.rstrip()}\n```"
    if "### Safe" in content:
        # Insert another code block under existing ### Safe
        # Simplest: append a fresh ### Safe block; collapse later if needed
        new = content.rstrip() + f"\n\n### Safe\n\n{block}\n"
    else:
        new = content.rstrip() + f"\n\n### Safe\n\n{block}\n"
    path.write_text(new)


def _insert_per_site_comment(finding, project_dir: Path, reason: str):
    src = Path(finding.file_path)
    text = src.read_text()
    lines = text.splitlines()
    prefix = "//" if src.suffix in {".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"} else "#"
    comment = f"{prefix} codesmells: ignore {finding.rule_id} reason=\"{reason}\""
    # Insert above the anchor line (1-indexed)
    insert_at = max(0, finding.anchor_line - 1)
    # Preserve indentation of the anchor line
    target = lines[insert_at] if insert_at < len(lines) else ""
    indent = target[: len(target) - len(target.lstrip())]
    lines.insert(insert_at, indent + comment)
    src.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""))


@app.command
def ignore(id: str, directory: str = ".", here: bool = False, reason: str = ""):
    """Suppress a finding via a Safe pattern (stdin) or per-site comment (--here)."""
    finding, project_dir = _find_finding(directory, id)
    rule = _load_rule(finding.rule_id, project_dir)

    if here:
        if not reason:
            m.fail("--here requires --reason")
        _insert_per_site_comment(finding, project_dir, reason)
        m.ok(f"per-site ignore inserted for {id} at {finding.file_path}:{finding.anchor_line}")
        return

    import sys as _sys
    template = _sys.stdin.read()
    if not template.strip():
        m.fail("no template on stdin and --here not given — provide a Safe pattern or use --here")

    gates = _three_gates(template, finding, rule)
    failed = [(name, msg) for name, ok, msg in gates if not ok]
    if failed:
        lines = [f"{name}: {msg}" for name, ok, msg in gates]
        report = "\n".join(lines)
        m.fail(report)

    _append_safe(rule, template)
    m.ok(f"safe pattern appended to {Path(rule.source_path).name}")
```

- [ ] **Step 2:** Run ignore tests

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 6 passed (4 prior + 2 new).

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): ignore command — pattern mode (stdin + three gates)"
```

### Task 5.3: Per-site ignore — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_ignore_here_inserts_comment(tmp_path):
    proj = _prepare_project(tmp_path)
    scan_out = _run(["scan", "."], cwd=proj).stdout
    target_id = None
    target_file = None
    target_line = None
    for line in scan_out.splitlines():
        if "catch-all-exception" in line:
            parts = line.split()
            target_id = parts[0]
            loc = parts[-1]
            target_file, target_line = loc.rsplit(":", 1)
            break
    assert target_id

    result = _run(["ignore", target_id, "--here", "--reason=top-level handler"], cwd=proj)
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"

    # The file should now have the comment
    full_path = proj / target_file
    text = full_path.read_text()
    assert "codesmells: ignore catch-all-exception" in text
    assert "top-level handler" in text

    # And the scan should no longer find it
    rescan = _run(["scan", "."], cwd=proj)
    assert "catch-all-exception" not in rescan.stdout


def test_ignore_here_requires_reason(tmp_path):
    proj = _prepare_project(tmp_path)
    scan_out = _run(["scan", "."], cwd=proj).stdout
    target_id = scan_out.splitlines()[3].split()[0]
    result = _run(["ignore", target_id, "--here"], cwd=proj)
    assert result.returncode != 0
    assert "reason" in (result.stdout + result.stderr).lower()
```

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 8 passed.

- [ ] **Step 3:** Commit

```bash
git add tests/test_cli_microcli.py
git commit -m "test(cli): per-site ignore — comment insert + reason required"
```

---

# Slice 6 — Init flow

### Task 6.1: `init` preview — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_init_preview_lists_candidates(tmp_path):
    proj = tmp_path / "freshproj"
    shutil.copytree(FIXTURE, proj)
    # No .codesmells yet
    result = _run(["init"], cwd=proj)
    assert result.returncode == 0
    assert "detected: python" in result.stdout
    assert "catch-all-exception" in result.stdout
    # Nothing should be written yet
    assert not (proj / ".codesmells").exists()


def test_init_select_writes_rule_files(tmp_path):
    proj = tmp_path / "freshproj2"
    shutil.copytree(FIXTURE, proj)
    result = _run(["init", "--select", "catch-all-exception"], cwd=proj)
    assert result.returncode == 0
    assert (proj / ".codesmells" / "catch-all-exception.smell.md").exists()
    assert not (proj / ".codesmells" / "print-instead-of-log.smell.md").exists()


def test_init_all_copies_every_candidate(tmp_path):
    proj = tmp_path / "freshproj3"
    shutil.copytree(FIXTURE, proj)
    result = _run(["init", "--all"], cwd=proj)
    assert result.returncode == 0
    files = sorted(p.name for p in (proj / ".codesmells").glob("*.smell.md"))
    assert "catch-all-exception.smell.md" in files
    assert "print-instead-of-log.smell.md" in files
```

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_cli_microcli.py::test_init_preview_lists_candidates -q`
Expected: unknown command.

### Task 6.2: Implement `init`

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append to `cli.py`

```python
from codesmells.rules import detect_languages, library_rules_for_languages


def _candidate_rules(project_dir: Path):
    langs = detect_languages(project_dir)
    candidates = library_rules_for_languages(langs)
    out = []
    for r in candidates:
        # A rule is a candidate iff some pre-filter actually appears somewhere in the project
        if not r.pre_filters:
            out.append((r, 0))  # accept rules with no pre-filters by default
            continue
        hits = _count_prefilter_hits(project_dir, r)
        if hits > 0:
            out.append((r, hits))
    return langs, out


def _count_prefilter_hits(project_dir: Path, rule) -> int:
    hits = 0
    for f in project_dir.rglob("*"):
        if not f.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", ".codesmells", "__pycache__"} for part in f.parts):
            continue
        try:
            text = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for pf in rule.pre_filters:
            if pf in text:
                hits += text.count(pf)
                break
    return hits


def _copy_rule_to_project(rule, project_dir: Path):
    target_dir = project_dir / ".codesmells"
    target_dir.mkdir(exist_ok=True)
    src = Path(rule.source_path).read_text()
    (target_dir / f"{rule.id}.smell.md").write_text(src)


@app.command
def init(directory: str = ".", all: bool = False, select: str = ""):
    """Detect languages, probe library, copy picked rules into .codesmells/."""
    project_dir = Path(directory).resolve()
    langs, candidates = _candidate_rules(project_dir)

    if not candidates:
        m.ok("no library rules match this project")
        return

    if not all and not select and not _has_stdin():
        # Preview mode
        m.info(f"detected: {', '.join(sorted(langs))}")
        m.info(f"loaded library: {len(candidates)} rules matching detected languages")
        print()
        print("candidates (rules that actually fire):")
        print()
        for rule, hits in candidates:
            tag = ",".join(rule.lang) or "any"
            desc = rule.description.splitlines()[0] if rule.description else ""
            short = desc[:48]
            print(f"  {rule.id:28s}  {tag:10s}  {short:48s}  {hits} hits")
        print()
        m.info("next: codesmells init --select <ids>  |  codesmells init --all")
        return

    # Selection
    if all:
        picks = {r.id for r, _ in candidates}
    elif select:
        picks = {s.strip() for s in select.split(",")}
    else:
        import sys as _sys
        picks = {line.strip() for line in _sys.stdin.read().splitlines() if line.strip()}

    written = []
    for rule, _ in candidates:
        if rule.id in picks:
            _copy_rule_to_project(rule, project_dir)
            written.append(rule.id)
    if not written:
        m.fail(f"no candidate matched the given selection: {sorted(picks)}")
    m.ok(f"copied {len(written)} rule(s) into .codesmells/: {', '.join(written)}")


def _has_stdin() -> bool:
    import sys as _sys
    return not _sys.stdin.isatty()
```

- [ ] **Step 2:** Run init tests

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 11 passed (8 prior + 3 new).

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): init command — detect, probe, preview/select/all"
```

---

# Slice 7 — Check (CI gate)

### Task 7.1: `check` — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_check_returns_nonzero_when_smells_exist(tmp_path):
    proj = _prepare_project(tmp_path)
    result = _run(["check"], cwd=proj)
    assert result.returncode != 0
    assert "smell" in result.stdout.lower()


def test_check_returns_zero_when_clean(tmp_path):
    proj = _prepare_project(tmp_path)
    # Strip the offending lines from the source so the project is clean
    p = proj / "processor.py"
    p.write_text("def noop():\n    return None\n")
    q = proj / "utils.py"
    q.write_text("def noop():\n    return None\n")
    result = _run(["check"], cwd=proj)
    assert result.returncode == 0
```

- [ ] **Step 2:** Run — expect failure

Run: `uv run pytest tests/test_cli_microcli.py::test_check_returns_nonzero_when_smells_exist -q`
Expected: unknown command.

### Task 7.2: Implement `check`

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append

```python
@app.command
def check(directory: str = "."):
    """Stateless CI gate. Exit 1 if any finding exists."""
    findings, project_dir = _run_scan(directory)
    if not findings:
        m.ok(f"no smells in {directory}")
        return
    m.info(f"{len(findings)} smell{'s' if len(findings) != 1 else ''} remaining")
    print()
    for f in findings:
        rel = Path(f.file_path).relative_to(project_dir) if Path(f.file_path).is_relative_to(project_dir) else Path(f.file_path)
        print(f"{f.id}  {f.rule_id:24s}  {rel}:{f.anchor_line}")
    # microcli's m.fail exits 1
    m.fail("")
```

(The trailing `m.fail("")` is the rc=1 carrier; the empty message keeps the output uncluttered.)

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 13 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): check command — CI gate with non-zero exit on findings"
```

---

# Slice 8 — Add + refresh

### Task 8.1: `add` — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_add_copies_library_rule(tmp_path):
    proj = tmp_path / "addproj"
    shutil.copytree(FIXTURE, proj)
    (proj / ".codesmells").mkdir()
    result = _run(["add", "catch-all-exception"], cwd=proj)
    assert result.returncode == 0
    assert (proj / ".codesmells" / "catch-all-exception.smell.md").exists()


def test_add_unknown_rule_fails(tmp_path):
    proj = tmp_path / "addproj2"
    shutil.copytree(FIXTURE, proj)
    (proj / ".codesmells").mkdir()
    result = _run(["add", "no-such-rule"], cwd=proj)
    assert result.returncode != 0
```

- [ ] **Step 2:** Run — expect failure

Run: `uv run pytest tests/test_cli_microcli.py::test_add_copies_library_rule -q`
Expected: unknown command.

### Task 8.2: Implement `add`

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append

```python
@app.command
def add(rule_id: str, directory: str = "."):
    """Copy a specific library rule into the project's .codesmells/."""
    project_dir = Path(directory).resolve()
    # Find the rule across all detected langs in the library
    all_lib = library_rules_for_languages({"python", "javascript", "typescript", "go", "rust", "java", "ruby", "any"})
    rule = next((r for r in all_lib if r.id == rule_id), None)
    if not rule:
        m.fail(f"library has no rule with id '{rule_id}'")
    _copy_rule_to_project(rule, project_dir)
    m.ok(f"added {rule.id} to .codesmells/")
```

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 15 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): add command — copy a library rule into the project"
```

### Task 8.3: `refresh` — failing test

**Files:**
- Modify: `tests/test_cli_microcli.py`

- [ ] **Step 1:** Append

```python
def test_refresh_overwrites_unmodified(tmp_path):
    proj = tmp_path / "refproj"
    shutil.copytree(FIXTURE, proj)
    (proj / ".codesmells").mkdir()
    _run(["add", "catch-all-exception"], cwd=proj)
    # Mutate the local file
    local = proj / ".codesmells" / "catch-all-exception.smell.md"
    local.write_text(local.read_text() + "\n# locally edited\n")
    # refresh without --force should warn and refuse
    result = _run(["refresh", "catch-all-exception"], cwd=proj)
    assert result.returncode != 0
    # with --force should overwrite
    result2 = _run(["refresh", "catch-all-exception", "--force"], cwd=proj)
    assert result2.returncode == 0
    assert "locally edited" not in local.read_text()
```

- [ ] **Step 2:** Run — expect failure

Run: `uv run pytest tests/test_cli_microcli.py::test_refresh_overwrites_unmodified -q`
Expected: unknown command.

### Task 8.4: Implement `refresh`

**Files:**
- Modify: `src/codesmells/cli.py`

- [ ] **Step 1:** Append

```python
@app.command
def refresh(rule_id: str, directory: str = ".", force: bool = False):
    """Re-copy a library rule into the project, overwriting the local copy.

    Warns if the local copy has diverged from the library version (refuses unless --force).
    """
    project_dir = Path(directory).resolve()
    target = project_dir / ".codesmells" / f"{rule_id}.smell.md"
    if not target.exists():
        m.fail(f"project doesn't have {rule_id} — use 'codesmells add {rule_id}' first")

    all_lib = library_rules_for_languages({"python", "javascript", "typescript", "go", "rust", "java", "ruby", "any"})
    rule = next((r for r in all_lib if r.id == rule_id), None)
    if not rule:
        m.fail(f"library has no rule with id '{rule_id}'")

    library_text = Path(rule.source_path).read_text()
    local_text = target.read_text()
    if library_text != local_text and not force:
        m.fail(f"local copy of {rule_id} diverges from library — pass --force to overwrite")

    target.write_text(library_text)
    m.ok(f"refreshed {rule_id}")
```

- [ ] **Step 2:** Run

Run: `uv run pytest tests/test_cli_microcli.py -q`
Expected: 16 passed.

- [ ] **Step 3:** Commit

```bash
git add src/codesmells/cli.py tests/test_cli_microcli.py
git commit -m "feat(cli): refresh command — overwrite local rule from library, --force gate"
```

---

# Slice 9 — Cleanup + 0.3.0 release

### Task 9.1: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1:** Replace `README.md` contents

```markdown
# CodeSmells

Deterministic code smell detection for agentic refactoring.

Rules are author-written `.smell.md` files. The agent's job is to fix smells; codesmells's job is to find them and tell the agent exactly where.

## Install

```bash
uv sync
```

## Quick start

```bash
# In any project directory:
codesmells init                  # preview which library rules fire here
codesmells init --all            # opt every fire-ing rule into .codesmells/

codesmells scan                  # list all smells
codesmells inspect <id>          # local detail
codesmells suggest <id>          # hydrated refactor template

# Exception machinery
codesmells ignore <id> <<EOF     # commit a Safe pattern (three-gate validation)
...
EOF
codesmells ignore <id> --here --reason="..."   # per-site comment

# CI gate
codesmells check                 # exit 1 if any smell remains
```

## Concepts

- **Rules are deterministic; fixes are agentic.** A rule decides *what* is a smell. The agent decides *how* to fix it.
- **Stateless.** Each invocation is a complete computation. The only durable artifacts are the rule files in `.codesmells/` and per-site `# codesmells: ignore ...` comments in your source.
- **Rules learn over time.** When you `ignore <id>` with a Safe pattern, the pattern gets committed to the rule file. Future scans skip anything matching the safe pattern. Your rules document your team's exception conventions.

See `research/2026-05-27-agent-vision-design.md` for the full design.

## License

MIT.
```

- [ ] **Step 2:** Commit

```bash
git add README.md
git commit -m "docs(readme): rewrite for agent-first CLI"
```

### Task 9.2: Update CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1:** Add `0.3.0` entry at the top under any `[Unreleased]`

```markdown
## [v0.3.0] - 2026-05-27

### Agent-first rebuild

- Stateless CLI built on `microcli-toolkit` (removed `typer` + `rich`)
- Windowed multi-fire scanner — finds every instance of a smell, not just the first per rule per file
- Curated rule library bundled with the package (`catch-all-exception`, `print-instead-of-log`, `mutable-default-argument`, `bare-return`, `todo-fixme`)
- New commands: `init`, `add`, `refresh`, `check` (CI gate); rewritten: `scan`, `inspect`, `suggest`, `ignore`
- Pattern-mode ignore reads Safe template from stdin (no interactive prompts); per-site mode via `--here --reason=`
- Removed stateful session.json + commands (`status`, `accept`, `finish`)
- Fixed normalization formula in alignment (dropped spurious 2× divisor)
- New tests: `test_rules`, `test_scanner`, `test_cli_microcli`; deleted obsolete `test_cli`, `test_milestone3`, `test_storage`
- Vision spec: `research/2026-05-27-agent-vision-design.md`
```

- [ ] **Step 2:** Commit

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): v0.3.0 — agent-first rebuild"
```

### Task 9.3: Bump version + final test pass

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1:** In `pyproject.toml`, change `version = "0.1.0"` to `version = "0.3.0"`

- [ ] **Step 2:** Final full test pass

Run: `uv run pytest -q`
Expected: 40+ passed (lexer 8 + alignment 17 + rules 9 + scanner 5 + cli ≥9 = 48 or so).

- [ ] **Step 3:** Commit

```bash
git add pyproject.toml
git commit -m "chore(release): v0.3.0"
```

### Task 9.4: Tag + push

**Files:** none

- [ ] **Step 1:** Annotated tag

```bash
git tag -a v0.3.0 -m "Release v0.3.0 — agent-first rebuild"
```

- [ ] **Step 2:** Push branch + tag

```bash
git push origin main
git push origin v0.3.0
```

- [ ] **Step 3:** GitHub release

```bash
gh release create v0.3.0 --generate-notes --title "v0.3.0"
```

### Task 9.5: Sync workspace journal + repo node

**Files:**
- Modify: `/home/apiad/Workspace/vault/Calendar/Journal/journal-2026-05-27.md`
- Modify: `/home/apiad/Workspace/vault/Efforts/Repos/codesmells.md`

- [ ] **Step 1:** Journal entry

Append to today's journal:

```
> 🤖 HH:MM — milestone: released apiad/codesmells v0.3.0 (agent-first rebuild)
```

- [ ] **Step 2:** Update vault node body to reflect the new shape; bump `last_sync` in frontmatter to now.

---

## Self-Review

Spec coverage check:

- §1 Vision — covered conceptually; no task needed (it's the rationale, not a build target).
- §2 Architecture — Slices 1, 2, 3 build the new modules; Slice 0.3 swaps deps.
- §3 CLI surface — `scan`/`inspect`/`suggest`/`ignore`/`check`/`init`/`add`/`refresh` all covered. `--learn` is free from microcli.
- §4 Rule format & library — Tasks 1.3–1.6, 3.1 cover schema + library + project layout.
- §5 Scanning model — Slice 2 covers pipeline, ID, normalization fix; Task 2.4 covers ignore harvest + safe guard.
- §6 Exception machinery — Slice 5 covers both modes.
- §7 Init flow — Slice 6.
- §8 CI mode — Slice 7.
- §9 Errors & edge cases — covered inline (no-rules error, unknown-id error, three-gate diagnostics, --reason required). Diverging refresh handled in Task 8.4.
- §10 Testing — Tasks 1.3, 1.5, 2.2, 2.4, 3.3, 4.1, 4.3, 5.1, 5.3, 6.1, 7.1, 8.1, 8.3 — and old tests deleted in Task 3.4.
- §11 Out of scope — confirmed not in the plan.
- §12 Migration notes — debris deleted in Task 0.2; old modules deleted in Tasks 1.2 and 3.4; CHANGELOG + pyproject updates in Slice 9.

Placeholder scan: no "TODO", "fill in", or "see above" references. Every step has either code or a precise command.

Type consistency check: `Token`/`TokenClass` defined in Task 1.1 and used in Tasks 1.4–8.4. `Rule` dataclass fields (id, lang, tau, severity, description, pre_filters, anti_patterns, safe_patterns, refactor_template, refactor_explanation, source_path) referenced consistently. `Finding` fields (id, rule_id, file_path, anchor_line, end_line, snippet, bindings, score) referenced consistently. Function signatures `parse_rule_file(path)`, `load_rules_from_dir(dir_path)`, `detect_languages(root)`, `library_rules_for_languages(langs)`, `scan_path(root, rules)` consistent across tasks.
