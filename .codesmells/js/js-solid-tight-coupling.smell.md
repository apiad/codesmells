---
id: js-solid-tight-coupling
title: Tight Coupling (New-ing dependencies)
description: Instantiating dependencies directly inside a class using `new` creates rigid coupling that makes testing and modular replacement impossible. Employing Dependency Injection (DI) allows for more flexible, decoupled designs that are easier to unit test with mocks.
pre_filters:
  - "new"
  - "this"
tau: 0.46
---

# Tight Coupling

### Anti-Pattern

```javascript
this.$DEP = new $CLASS(...)
```

### Refactoring

Inject the dependency through the constructor or as a function parameter.

```javascript
constructor($DEP) {
    this.$DEP = $DEP
}
```

### Refactor Explanation
Tightly coupled code is hard to test because you cannot easily mock the dependencies. Dependency Injection allows you to swap implementations (e.g., using a MockDatabase for tests and a PostgresDatabase for production), leading to more flexible and testable systems.
