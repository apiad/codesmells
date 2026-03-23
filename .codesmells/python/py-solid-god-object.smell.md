---
id: py-solid-god-object
title: God Object
description: A God Object consolidates too many unrelated responsibilities into a single class, violating the Single Responsibility Principle. This leads to tightly coupled, rigid codebases that are difficult to test, maintain, and extend.
pre_filters:
  - "class"
tau: 0.44
---

# God Object

### Anti-Pattern

This code example demonstrates the God Object anti-pattern.

```python
class $GOD:
    def $M1(...): ...
    def $M2(...): ...
    def $M3(...): ...
    def $M4(...): ...
    def $M5(...): ...
```

### Refactoring

Break down the large class into smaller, focused classes, each with a single responsibility.

```python
class $NEW_NAME:
    def $M1(...): ...
```

### Refactor Explanation
Large "God" objects are hard to maintain, test, and understand. They lead to tight coupling and make the codebase brittle. Refactoring them into smaller classes improves cohesion and makes the system more modular.
