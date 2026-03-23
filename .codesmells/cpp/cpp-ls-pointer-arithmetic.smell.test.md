---
rule_id: cpp-ls-pointer-arithmetic
---

### Anti-Pattern #1 (Base + Offset)
```cpp
void move() {
    char* p = buffer + 10;
}
```

### Anti-Pattern #2 (Increment)
```cpp
void walk() {
    p++;
}
```

### Safe #1 (Advance Iterator)
```cpp
void safe() {
    std::advance(it, 10);
}
```

### Safe #2 (Indexing)
```cpp
void index() {
    char c = buffer[10];
}
```
