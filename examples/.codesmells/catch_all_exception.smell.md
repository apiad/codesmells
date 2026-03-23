---
tau: 0.8
pre_filters:
  - "except Exception"
---

# Avoid Catch-All Exceptions

Catching `Exception` broadly can hide unexpected errors (like typos, syntax errors, or critical system failures), making debugging difficult. Always catch specific exceptions that you expect and know how to handle.

### Anti-Pattern

```python
try:
    ...
except Exception as $VAR:
    ...
```

### Safe

```python
try:
    ...
except ValueError as $VAR:
    ...
```

### Refactoring

```python
try:
    ...
# TODO: Replace ValueError with the specific expected exception type.
except ValueError as $VAR:
    ...
```
