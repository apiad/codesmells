---
rule_id: go-ls-interface-abuse
---

### Anti-Pattern #1 (Empty Interface Arg)
```go
func process(obj interface{}) {
    fmt.Println(obj)
}
```

### Anti-Pattern #2 (Struct Field)
```go
type Container struct {
    Item interface{}
}
```

### Safe #1 (Specific Interface)
```go
type Stringer interface {
    String() string
}

func log(obj Stringer) {
    fmt.Println(obj.String())
}
```

### Safe #2 (Generics)
```go
func process[T any](obj T) {
    fmt.Println(obj)
}
```
