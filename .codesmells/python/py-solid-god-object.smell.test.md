---
rule_id: py-solid-god-object
---

### Anti-Pattern #1 (God Class)
```python
class Manager:
    def process(self): pass
    def save(self): pass
    def log(self): pass
    def notify(self): pass
    def delete(self): pass
```

### Safe #1 (Small Class)
```python
class Saver:
    def save(self): pass
```

### Safe #2 (Multiple Small Classes)
```python
class Logger:
    def log(self): pass

class Notifier:
    def notify(self): pass
```
