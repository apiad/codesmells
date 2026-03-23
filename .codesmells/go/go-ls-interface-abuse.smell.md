---
id: go-ls-interface-abuse
title: Interface{} Abuse
description: Using `interface{}` (or `any`) for everything in Go bypasses type safety and requires constant type assertions. Prefer using specific types or interfaces that define the required behavior.
pre_filters:
  - "interface{}"
  - "any"
tau: 0.44
---

# Interface{} Abuse

### Anti-Pattern

```go
func $FUNC(data interface{}) {
```

### Anti-Pattern

```go
type $NAME struct {
    Value interface{}
}
```

### Refactoring

Use a specific interface that defines the required methods, or use generics (Go 1.18+).

```go
func $FUNC[T any](data T) {
```

### Refactor Explanation
`interface{}` accepts any type, but it provides no compile-time guarantees about what that type can do. This leads to code that is harder to reason about and more prone to runtime panics during type assertions. Specifying behavior through interfaces or using generics preserves type safety and intent.
