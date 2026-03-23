---
id: cs-ls-empty-catch
title: Empty Catch Block
description: Swallowing exceptions with an empty `catch` block hides errors and makes debugging nearly impossible. Always log or handle the exception in some way.
pre_filters:
  - "catch"
  - "{"
  - "}"
tau: 0.73
---

# Empty Catch Block

### Anti-Pattern

This code example demonstrates the Empty Catch Block anti-pattern.

```csharp
catch ($TYPE $EX) { }
```

### Anti-Pattern

This code example demonstrates the Empty Catch Block anti-pattern.

```csharp
catch { }
```

### Refactoring

Log the exception or re-throw it if you cannot handle it.

```csharp
catch (Exception ex) {
    _logger.LogError(ex, "An error occurred");
    throw;
}
```

### Refactor Explanation
Exceptions indicate that something unexpected happened. By swallowing them, you leave the application in an inconsistent state without any record of what went wrong. Even if you want to ignore an error, adding a comment explaining *why* is essential for future maintainers.
