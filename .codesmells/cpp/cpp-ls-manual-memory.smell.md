---
id: cpp-ls-manual-memory
title: Manual Memory Management (Non-RAII)
description: Using manual memory management with `new`/`delete` or `malloc`/`free` is error-prone and leads to memory leaks or double-frees. Modern C++ favors RAII using smart pointers (`std::unique_ptr`, `std::shared_ptr`) or container classes.
pre_filters:
  - "new"
  - "malloc"
tau: 0.28
---

# Manual Memory Management

### Anti-Pattern

This code example demonstrates the Manual Memory Management (Non-RAII) anti-pattern.

```cpp
$TYPE* $VAR = new $TYPE(...);
...
delete $VAR;
```

### Anti-Pattern

This code example demonstrates the Manual Memory Management (Non-RAII) anti-pattern.

```cpp
$TYPE* $VAR = ($TYPE*)malloc(sizeof($TYPE));
...
free($VAR);
```

### Refactoring

Use smart pointers to ensure automatic and safe memory management.

```cpp
auto $VAR = std::make_unique<$TYPE>(...);
```

### Refactor Explanation
Manual memory management requires perfect symmetry between allocation and deallocation, which is difficult to maintain in complex logic or when exceptions are thrown. RAII (Resource Acquisition Is Initialization) ensures that resources are automatically cleaned up when the managing object goes out of scope.
