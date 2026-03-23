---
rule_id: cpp-ls-pointer-arithmetic
---

### Anti-Pattern #1 (Base + Offset)

This code example demonstrates the Unsafe Pointer Arithmetic anti-pattern. Specifically, it illustrates the `Base + Offset` case.

```cpp
void move() {
    char* p = buffer + 10;
}
```

### Anti-Pattern #2 (Increment)

This code example demonstrates the Unsafe Pointer Arithmetic anti-pattern. Specifically, it illustrates the `Increment` case.

```cpp
void walk() {
    p++;
}
```

### Safe #1 (Advance Iterator)

This code example demonstrates a safe approach for the Unsafe Pointer Arithmetic issue. Specifically, it illustrates the `Advance Iterator` case.

```cpp
void safe() {
    std::advance(it, 10);
}
```

### Safe #2 (Indexing)

This code example demonstrates a safe approach for the Unsafe Pointer Arithmetic issue. Specifically, it illustrates the `Indexing` case.

```cpp
void index() {
    char c = buffer[10];
}
```
