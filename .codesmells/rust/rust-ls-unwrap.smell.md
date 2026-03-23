---
id: rust-ls-unwrap
title: Unnecessary Unwrap
description: Using `.unwrap()` on `Option` or `Result` types can cause the program to panic if the value is `None` or `Err`. Prefer using pattern matching (`match`, `if let`) or error propagation (`?`) for safer handling.
pre_filters:
  - ".unwrap("
tau: 0.67
---

# Unnecessary Unwrap

### Anti-Pattern

```rust
$VAR.unwrap()
```

### Refactoring

Handle the potential absence of a value or error gracefully.

```rust
let $VAL = $VAR.expect("Detailed error message");
```

Wait! `expect` is also a bit of a smell in production code.

```rust
let $VAL = $VAR?;
```

### Refactor Explanation
Rust's type system uses `Option` and `Result` to force explicit handling of null-like values or errors. `.unwrap()` bypasses this safety, potentially leading to runtime panics. Using `?` or pattern matching ensures that errors are either handled or propagated correctly.
