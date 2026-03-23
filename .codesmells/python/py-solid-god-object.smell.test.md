---
rule_id: py-solid-god-object
---

### Anti-Pattern #1 (God Class)

This code example demonstrates the God Object anti-pattern. Specifically, it illustrates the `God Class` case.

```python
class Manager:
    def process(self): pass
    def save(self): pass
    def log(self): pass
    def notify(self): pass
    def delete(self): pass
```

### Safe #1 (Small Class)

This code example demonstrates a safe approach for the God Object issue. Specifically, it illustrates the `Small Class` case.

```python
class Saver:
    def save(self): pass
```

### Safe #2 (Multiple Small Classes)

This code example demonstrates a safe approach for the God Object issue. Specifically, it illustrates the `Multiple Small Classes` case.

```python
class Logger:
    def log(self): pass

class Notifier:
    def notify(self): pass
```
