---
id: py-ls-mutable-defaults
title: Mutable Default Arguments
description: Using mutable objects like `[]` or `{}` as default arguments in Python leads to unexpected state sharing across all function calls. This often causes subtle, hard-to-trace bugs where data from previous calls persists in subsequent ones.
pre_filters:
  - "def"
tau: 0.54
---

# Mutable Default Arguments

### Anti-Pattern

```python
def $NAME(... $ARG = [])
```

### Anti-Pattern

```python
def $NAME(... $ARG = {})
```

### Refactoring

Use `None` as the default value and initialize the mutable object inside the function if it's `None`.

```python
def $NAME(..., $ARG=None):
    if $ARG is None:
        $ARG = []
    ...
```

### Refactor Explanation
In Python, default arguments are evaluated once at function definition time, not every time the function is called. If you use a mutable object like a list or dictionary, any modifications to that object will persist across subsequent calls.

### Next Steps
1. Change the default value to `None`.
2. Inside the function, check if the argument is `None`.
3. If it is `None`, initialize it to a new mutable object (e.g., `[]` or `{}`).
