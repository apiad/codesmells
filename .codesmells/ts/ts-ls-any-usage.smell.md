---
id: ts-ls-any-usage
title: "Any-script Usage"
description: Employing the `any` type completely bypasses TypeScript's safety features, effectively turning the code back into plain JavaScript. Using specific interfaces or the `unknown` type preserves type safety and leverages the compiler to prevent runtime errors.
pre_filters:
  - "any"
tau: 0.83
---

# 'Any'-script Usage

### Anti-Pattern

This code example demonstrates the Any-script Usage anti-pattern.

```typescript
: any
```

### Anti-Pattern

This code example demonstrates the Any-script Usage anti-pattern.

```typescript
as any
```

### Refactoring

Use a specific type or `unknown` for safer handling.

```typescript
: UserData
```

### Refactor Explanation
The `any` type effectively turns off type checking for that variable. It leads to runtime errors that TypeScript was designed to prevent. Using `unknown` forces you to perform type checks before using the variable, and defining interfaces ensures that the data structure is correctly documented and validated.
