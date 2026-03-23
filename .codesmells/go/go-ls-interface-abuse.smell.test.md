---
rule_id: go-ls-interface-abuse
---

### Anti-Pattern #1 (Empty Interface Arg)

This code example demonstrates the Interface{} Abuse anti-pattern. Specifically, it illustrates the `Empty Interface Arg` case.

```go
func process(obj interface{}) {
    fmt.Println(obj)
}
```

### Anti-Pattern #2 (Struct Field)

This code example demonstrates the Interface{} Abuse anti-pattern. Specifically, it illustrates the `Struct Field` case.

```go
type Container struct {
    Item interface{}
}
```

### Safe #1 (Specific Interface)

This code example demonstrates a safe approach for the Interface{} Abuse issue. Specifically, it illustrates the `Specific Interface` case.

```go
type Stringer interface {
    String() string
}

func log(obj Stringer) {
    fmt.Println(obj.String())
}
```

### Safe #2 (Generics)

This code example demonstrates a safe approach for the Interface{} Abuse issue. Specifically, it illustrates the `Generics` case.

```go
func process[T any](obj T) {
    fmt.Println(obj)
}
```
