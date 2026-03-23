---
id: cpp-ls-pointer-arithmetic
title: Unsafe Pointer Arithmetic
description: Performing arithmetic directly on raw pointers is error-prone and can easily lead to out-of-bounds memory access. Prefer using iterators, indices, or container methods.
pre_filters:
  - "*"
  - "+"
  - "-"
tau: 0.42
---

# Unsafe Pointer Arithmetic

### Anti-Pattern

This code example demonstrates the Unsafe Pointer Arithmetic anti-pattern.

```cpp
$PTR = $BASE + $OFFSET;
```

### Anti-Pattern

This code example demonstrates the Unsafe Pointer Arithmetic anti-pattern.

```cpp
$PTR++;
```

### Refactoring

Use safe container methods or iterators instead of raw pointer arithmetic.

```cpp
auto $IT = $CONTAINER.begin();
std::advance($IT, $OFFSET);
```

### Refactor Explanation
Raw pointer arithmetic assumes that the memory layout is contiguous and that the offset is within valid bounds. This is often not checked at runtime, leading to security vulnerabilities. Using higher-level abstractions like iterators or `std::span` provides better safety and intent.
