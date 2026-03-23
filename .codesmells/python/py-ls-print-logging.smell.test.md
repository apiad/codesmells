---
rule_id: py-ls-print-logging
---

### Anti-Pattern #1 (Simple Print)
```python
print("Something happened")
```

### Anti-Pattern #2 (Print with Variable)
```python
print(f"User {name} logged in")
```

### Safe #1 (Logger)
```python
logger.info("Something happened")
```

### Safe #2 (Logger with Level)
```python
logger.error(f"Error: {e}")
```
