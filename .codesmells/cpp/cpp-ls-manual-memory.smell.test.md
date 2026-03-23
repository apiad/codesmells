---
rule_id: cpp-ls-manual-memory
---

### Anti-Pattern #1 (Raw New/Delete)
```cpp
void process() {
    int* data = new int[100];
    // ... use data
    delete[] data;
}
```

### Anti-Pattern #2 (Malloc/Free)
```cpp
void legacy() {
    char* buf = (char*)malloc(256);
    // ...
    free(buf);
}
```

### Safe #1 (Unique Ptr)
```cpp
void safe() {
    auto data = std::make_unique<int[]>(100);
}
```

### Safe #2 (Vector)
```cpp
void modern() {
    std::vector<int> data(100);
}
```
