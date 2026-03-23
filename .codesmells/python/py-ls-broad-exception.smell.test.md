---
rule_id: py-ls-broad-exception
---

### Anti-Pattern #1 (Generic Exception)
```python
try:
    process()
except Exception:
    pass
```

### Anti-Pattern #2 (Bare Except)
```python
try:
    do_something()
except:
    logger.error("Failed")
```

### Safe #1 (Specific Exception)
```python
try:
    with open("f.txt") as f:
        data = f.read()
except FileNotFoundError:
    print("File missing")
```

### Safe #2 (Multiple Specific Exceptions)
```python
try:
    val = int(input())
except (ValueError, EOFError):
    print("Invalid input")
```
