---
tau: 0.4
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

Using a more specific exception (like `ValueError` or a custom exception) ensures that only the errors you're prepared to handle are caught, while letting others propagate and be properly diagnosed.

```python
try:
    ...
# TODO: Replace ValueError with the specific expected exception type.
except ValueError as $VAR:
    ...
```
