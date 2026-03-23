---
rule_id: go-ls-ignoring-errors
---

### Anti-Pattern #1 (Ignore with short decl)

This code example demonstrates the Ignoring Errors anti-pattern. Specifically, it illustrates the `Ignore with short decl` case.

```go
data, _ := os.ReadFile("config.json")
```

### Anti-Pattern #2 (Ignore with assignment)

This code example demonstrates the Ignoring Errors anti-pattern. Specifically, it illustrates the `Ignore with assignment` case.

```go
n, _ = writer.Write(buf)
```

### Safe #1 (Handled)

This code example demonstrates a safe approach for the Ignoring Errors issue. Specifically, it illustrates the `Handled` case.

```go
data, err := os.ReadFile("config.json")
if err != nil {
    log.Fatal(err)
}
```

### Safe #2 (Check only)

This code example demonstrates a safe approach for the Ignoring Errors issue. Specifically, it illustrates the `Check only` case.

```go
if err := process(); err != nil {
    return err
}
```
