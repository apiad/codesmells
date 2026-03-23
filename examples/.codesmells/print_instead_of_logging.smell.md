---
tau: 0.4
pre_filters:
  - "print"
---

# Use Logging Instead of Print

In production code, we should use the standard `logging` module rather than raw `print` statements, as `print` cannot be easily redirected, formatted, or disabled based on severity levels.

### Anti-Pattern

```python
print($MESSAGE)
```

### Safe

```python
logger.info($MESSAGE)
```

### Refactoring

```python
logger.info($MESSAGE)
```
