---
rule_id: go-ls-ignoring-errors
---

### Anti-Pattern #1 (Ignore with short decl)
```go
data, _ := os.ReadFile("config.json")
```

### Anti-Pattern #2 (Ignore with assignment)
```go
n, _ = writer.Write(buf)
```

### Safe #1 (Handled)
```go
data, err := os.ReadFile("config.json")
if err != nil {
    log.Fatal(err)
}
```

### Safe #2 (Check only)
```go
if err := process(); err != nil {
    return err
}
```
