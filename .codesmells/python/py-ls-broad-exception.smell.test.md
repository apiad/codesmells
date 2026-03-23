---
rule_id: py-ls-broad-exception
---

### Anti-Pattern #1 (Generic Exception)

This code example demonstrates the Broad Exception Catching anti-pattern. Specifically, it illustrates the `Generic Exception` case.

```python
try:
    process()
except Exception:
    pass
```

### Anti-Pattern #2 (Bare Except)

This code example demonstrates the Broad Exception Catching anti-pattern. Specifically, it illustrates the `Bare Except` case.

```python
try:
    do_something()
except:
    logger.error("Failed")
```

### Safe #1 (Specific Exception)

This code example demonstrates a safe approach for the Broad Exception Catching issue. Specifically, it illustrates the `Specific Exception` case.

```python
try:
    with open("f.txt") as f:
        data = f.read()
except FileNotFoundError:
    print("File missing")
```

### Safe #2 (Multiple Specific Exceptions)

This code example demonstrates a safe approach for the Broad Exception Catching issue. Specifically, it illustrates the `Multiple Specific Exceptions` case.

```python
try:
    val = int(input())
except (ValueError, EOFError):
    print("Invalid input")
```
