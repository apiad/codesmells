# Writing Custom Rules & Tests

CodeSmells uses a human-readable Markdown format for defining architectural rules.

## Rule Template Format (`.smell.md`)

Each rule consists of a YAML frontmatter section followed by specific Markdown headers.

```markdown
---
tau: 0.4
pre_filters:
  - "important_keyword"
---
# Rule Name

Description of the architectural smell.

### Anti-Pattern
<!-- The code to avoid -->
```python
import $LIB
...
$LIB.dangerous_call()
```

### Refactoring
<!-- The improved version -->
```python
import $LIB
...
with $LIB.safe_context():
    $LIB.dangerous_call()
```

### Safe
<!-- Optional: examples that look like the anti-pattern but are safe -->
```python
# This is okay because it uses a different pattern
```
```

### Key Elements

- **Tau ($\tau$):** The similarity threshold (0.0 to 1.0). Higher values require stricter matches.
- **Pre-filters:** A list of strings that *must* be present in a file for the rule to even be considered. This significantly speeds up scanning.
- **Sigils ($SIGIL):** Identifiers starting with `$` act as variables. They will match any identifier or literal and their value will be used during refactoring.
- **Gaps (...):** The ellipsis matches any sequence of tokens.

## Rule Validation (`.smell.test.md`)

To ensure your rules are accurate, CodeSmells uses a companion test file.

```markdown
# Test: Rule Name

### Anti-Pattern
<!-- Snippets that MUST trigger the rule -->
```python
import os
os.system("rm -rf /")
```

### Safe
<!-- Snippets that MUST NOT trigger the rule -->
```python
import subprocess
subprocess.run(["ls"])
```
```

Run validation using:
```bash
codesmells validate
```
