---
rule_id: cpp-ls-manual-memory
---

### Anti-Pattern #1 (Raw New/Delete)

This code example demonstrates the Manual Memory Management (Non-RAII) anti-pattern. Specifically, it illustrates the `Raw New/Delete` case.

```cpp
void process() {
    int* data = new int[100];
    // ... use data
    delete[] data;
}
```

### Anti-Pattern #2 (Malloc/Free)

This code example demonstrates the Manual Memory Management (Non-RAII) anti-pattern. Specifically, it illustrates the `Malloc/Free` case.

```cpp
void legacy() {
    char* buf = (char*)malloc(256);
    // ...
    free(buf);
}
```

### Safe #1 (Unique Ptr)

This code example demonstrates a safe approach for the Manual Memory Management (Non-RAII) issue. Specifically, it illustrates the `Unique Ptr` case.

```cpp
void safe() {
    auto data = std::make_unique<int[]>(100);
}
```

### Safe #2 (Vector)

This code example demonstrates a safe approach for the Manual Memory Management (Non-RAII) issue. Specifically, it illustrates the `Vector` case.

```cpp
void modern() {
    std::vector<int> data(100);
}
```
