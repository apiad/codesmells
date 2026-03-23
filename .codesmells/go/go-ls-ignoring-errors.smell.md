---
id: go-ls-ignoring-errors
title: Ignoring Errors
description: Using the blank identifier `_` to ignore error returns in Go is a dangerous practice that can hide critical failures. Always check and handle returned errors.
pre_filters:
  - "_"
  - ":="
tau: 0.45
---

# Ignoring Errors

### Anti-Pattern

This code example demonstrates the Ignoring Errors anti-pattern.

```go
$VAL, _ := $FUNC(...)
```

### Anti-Pattern

This code example demonstrates the Ignoring Errors anti-pattern.

```go
$VAL, _ = $FUNC(...)
```

### Refactoring

Always check if the error is `nil` before proceeding.

```go
$VAL, err := $FUNC(...)
if err != nil {
    return err
}
```

### Refactor Explanation
In Go, errors are values that must be handled explicitly. Ignoring an error using `_` means your program continues in an undefined state if a failure occurs, making it much harder to diagnose issues and potentially leading to data corruption or crashes.
