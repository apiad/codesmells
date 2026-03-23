---
rule_id: ts-ls-any-usage
---

### Anti-Pattern #1 (Type Annotation)
```typescript
let x: any = 1;
```

### Anti-Pattern #2 (Type Assertion)
```typescript
const y = z as any;
```

### Anti-Pattern #3 (Function Arg)
```typescript
function f(arg: any) { }
```

### Safe #1 (Specific Type)
```typescript
let x: number = 1;
```

### Safe #2 (Unknown)
```typescript
let y: unknown = z;
```
