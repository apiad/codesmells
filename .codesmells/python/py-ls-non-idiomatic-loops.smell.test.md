---
rule_id: py-ls-non-idiomatic-loops
---

### Anti-Pattern #1 (range len)

This code example demonstrates the Non-idiomatic Loops anti-pattern. Specifically, it illustrates the `range len` case.

```python
for i in range(len(items)):
    print(items[i])
```

### Safe #1 (enumerate)

This code example demonstrates a safe approach for the Non-idiomatic Loops issue. Specifically, it illustrates the `enumerate` case.

```python
for i, x in enumerate(items):
    print(i, x)
```

### Safe #2 (range with start)

This code example demonstrates a safe approach for the Non-idiomatic Loops issue. Specifically, it illustrates the `range with start` case.

```python
for i in range(1, 10):
    print(i)
```

### Safe #3 (direct iteration)

This code example demonstrates a safe approach for the Non-idiomatic Loops issue. Specifically, it illustrates the `direct iteration` case.

```python
for x in items:
    print(x)
```
