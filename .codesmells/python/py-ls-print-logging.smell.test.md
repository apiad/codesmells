---
rule_id: py-ls-print-logging
---

### Anti-Pattern #1 (Simple Print)

This code example demonstrates the Print instead of Logging anti-pattern. Specifically, it illustrates the `Simple Print` case.

```python
print("Something happened")
```

### Anti-Pattern #2 (Print with Variable)

This code example demonstrates the Print instead of Logging anti-pattern. Specifically, it illustrates the `Print with Variable` case.

```python
print(f"User {name} logged in")
```

### Safe #1 (Logger)

This code example demonstrates a safe approach for the Print instead of Logging issue. Specifically, it illustrates the `Logger` case.

```python
logger.info("Something happened")
```

### Safe #2 (Logger with Level)

This code example demonstrates a safe approach for the Print instead of Logging issue. Specifically, it illustrates the `Logger with Level` case.

```python
logger.error(f"Error: {e}")
```
