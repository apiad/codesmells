---
rule_id: c-sec-buffer-overflow
---

### Anti-Pattern #1 (strcpy)

This code example demonstrates the Potential Buffer Overflow anti-pattern. Specifically, it illustrates the `strcpy` case.

```c
void unsafe() {
    char dest[10];
    strcpy(dest, "this is too long");
}
```

### Anti-Pattern #2 (gets)

This code example demonstrates the Potential Buffer Overflow anti-pattern. Specifically, it illustrates the `gets` case.

```c
void vulnerable() {
    char buf[256];
    gets(buf);
}
```

### Safe #1 (strncpy)

This code example demonstrates a safe approach for the Potential Buffer Overflow issue. Specifically, it illustrates the `strncpy` case.

```c
void safe() {
    char dest[10];
    strncpy(dest, "limited", sizeof(dest) - 1);
}
```

### Safe #2 (snprintf)

This code example demonstrates a safe approach for the Potential Buffer Overflow issue. Specifically, it illustrates the `snprintf` case.

```c
void better() {
    char buf[128];
    snprintf(buf, sizeof(buf), "Value: %d", 42);
}
```
