---
rule_id: cs-ls-empty-catch
---

### Anti-Pattern #1 (Empty with Var)

This code example demonstrates the Empty Catch Block anti-pattern. Specifically, it illustrates the `Empty with Var` case.

```csharp
try {
    DoWork();
}
catch (Exception ex) { }
```

### Anti-Pattern #2 (Bare Catch)

This code example demonstrates the Empty Catch Block anti-pattern. Specifically, it illustrates the `Bare Catch` case.

```csharp
try {
    DoWork();
}
catch { }
```

### Safe #1 (Handled)

This code example demonstrates a safe approach for the Empty Catch Block issue. Specifically, it illustrates the `Handled` case.

```csharp
try {
    DoWork();
}
catch (Exception ex) {
    Log(ex);
}
```

### Safe #2 (Rethrow)

This code example demonstrates a safe approach for the Empty Catch Block issue. Specifically, it illustrates the `Rethrow` case.

```csharp
try {
    DoWork();
}
catch {
    throw;
}
```
