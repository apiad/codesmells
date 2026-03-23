---
rule_id: py-ls-non-idiomatic-loops
---

### Anti-Pattern #1 (range len)
```python
for i in range(len(items)):
    print(items[i])
```

### Safe #1 (enumerate)
```python
for i, x in enumerate(items):
    print(i, x)
```

### Safe #2 (range with start)
```python
for i in range(1, 10):
    print(i)
```

### Safe #3 (direct iteration)
```python
for x in items:
    print(x)
```
