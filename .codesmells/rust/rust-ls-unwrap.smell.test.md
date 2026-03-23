---
rule_id: rust-ls-unwrap
---

### Anti-Pattern #1 (Simple Unwrap)

This code example demonstrates the Unnecessary Unwrap anti-pattern. Specifically, it illustrates the `Simple Unwrap` case.

```rust
let config = read_config().unwrap();
```

### Anti-Pattern #2 (Chained Unwrap)

This code example demonstrates the Unnecessary Unwrap anti-pattern. Specifically, it illustrates the `Chained Unwrap` case.

```rust
let val = map.get("key").unwrap().parse::<i32>().unwrap();
```

### Safe #1 (Error Propagation)

This code example demonstrates a safe approach for the Unnecessary Unwrap issue. Specifically, it illustrates the `Error Propagation` case.

```rust
let config = read_config()?;
```

### Safe #2 (Expect)

This code example demonstrates a safe approach for the Unnecessary Unwrap issue. Specifically, it illustrates the `Expect` case.

```rust
let val = map.get("key").expect("key must exist in config");
```

### Safe #3 (Pattern Match)

This code example demonstrates a safe approach for the Unnecessary Unwrap issue. Specifically, it illustrates the `Pattern Match` case.

```rust
if let Some(val) = map.get("key") {
    process(val);
}
```
