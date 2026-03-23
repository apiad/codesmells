---
id: py-ls-non-idiomatic-loops
title: Non-idiomatic Loops
description: Iterating with `range(len(list))` is a non-idiomatic pattern that increases complexity and reduces readability. Python's direct iteration and `enumerate()` provide a cleaner, more efficient way to access both elements and their indices.
pre_filters:
  - "for"
tau: 0.61
---

# Non-idiomatic Loops

### Anti-Pattern

This code example demonstrates the Non-idiomatic Loops anti-pattern.

```python
for $I in range(len($L)):
```

### Refactoring

Use direct iteration if the index is not needed, or `enumerate()` if it is.

```python
for $I, $X in enumerate($L):
```

### Refactor Explanation
Python allows you to iterate directly over the items of any collection. If you also need the index, `enumerate()` provides both in a clean, efficient way. Manual counters or `range(len())` are remnants of C-style programming and are not idiomatic in Python.
