---
rule_id: ts-ls-any-usage
---

### Anti-Pattern #1 (Type Annotation)

This code example demonstrates the Any-script Usage anti-pattern. Specifically, it illustrates the `Type Annotation` case.

```typescript
let x: any = 1;
```

### Anti-Pattern #2 (Type Assertion)

This code example demonstrates the Any-script Usage anti-pattern. Specifically, it illustrates the `Type Assertion` case.

```typescript
const y = z as any;
```

### Anti-Pattern #3 (Function Arg)

This code example demonstrates the Any-script Usage anti-pattern. Specifically, it illustrates the `Function Arg` case.

```typescript
function f(arg: any) { }
```

### Safe #1 (Specific Type)

This code example demonstrates a safe approach for the Any-script Usage issue. Specifically, it illustrates the `Specific Type` case.

```typescript
let x: number = 1;
```

### Safe #2 (Unknown)

This code example demonstrates a safe approach for the Any-script Usage issue. Specifically, it illustrates the `Unknown` case.

```typescript
let y: unknown = z;
```
