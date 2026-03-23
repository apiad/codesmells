---
rule_id: c-sec-buffer-overflow
---

### Anti-Pattern #1 (strcpy)
```c
void unsafe() {
    char dest[10];
    strcpy(dest, "this is too long");
}
```

### Anti-Pattern #2 (gets)
```c
void vulnerable() {
    char buf[256];
    gets(buf);
}
```

### Safe #1 (strncpy)
```c
void safe() {
    char dest[10];
    strncpy(dest, "limited", sizeof(dest) - 1);
}
```

### Safe #2 (snprintf)
```c
void better() {
    char buf[128];
    snprintf(buf, sizeof(buf), "Value: %d", 42);
}
```
