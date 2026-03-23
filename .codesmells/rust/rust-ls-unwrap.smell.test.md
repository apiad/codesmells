---
rule_id: rust-ls-unwrap
---

### Anti-Pattern #1 (Simple Unwrap)
```rust
let config = read_config().unwrap();
```

### Anti-Pattern #2 (Chained Unwrap)
```rust
let val = map.get("key").unwrap().parse::<i32>().unwrap();
```

### Safe #1 (Error Propagation)
```rust
let config = read_config()?;
```

### Safe #2 (Expect)
```rust
let val = map.get("key").expect("key must exist in config");
```

### Safe #3 (Pattern Match)
```rust
if let Some(val) = map.get("key") {
    process(val);
}
```
