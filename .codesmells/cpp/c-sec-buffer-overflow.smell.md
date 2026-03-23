---
id: c-sec-buffer-overflow
title: Potential Buffer Overflow
description: Using unsafe string functions like `strcpy`, `gets`, or `sprintf` can lead to buffer overflows if the input is not strictly bounded. Prefer safer alternatives like `strncpy`, `fgets`, or `snprintf`.
pre_filters:
  - "strcpy"
  - "gets"
  - "sprintf"
tau: 0.67
---

# Potential Buffer Overflow

### Anti-Pattern

```c
strcpy($DEST, $SRC)
```

### Anti-Pattern

```c
gets($BUF)
```

### Anti-Pattern

```c
sprintf($BUF, $FORMAT, ...)
```

### Refactoring

Use bounded versions of these functions to prevent writing beyond the buffer size.

```c
strncpy($DEST, $SRC, sizeof($DEST) - 1)
```

### Refactor Explanation
Unsafe string functions do not check the size of the destination buffer, allowing an attacker to overwrite adjacent memory. This is a classic security vulnerability that can lead to crashes or arbitrary code execution. Bounded versions (like `snprintf`) ensure that no more than a specified number of bytes are written.
