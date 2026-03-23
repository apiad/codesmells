---
rule_id: py-ls-mutable-defaults
---

### Anti-Pattern #1 (List Default)
```python
def add_to(item, list=[]):
    list.append(item)
    return list
```

### Anti-Pattern #2 (Dict Default)
```python
def get_config(overrides={}):
    config = {"default": True}
    config.update(overrides)
    return config
```

### Anti-Pattern #3 (Class __init__)
```python
class User:
    def __init__(self, roles=[]):
        self.roles = roles
```

### Safe #1 (None Default)
```python
def add_to(item, list=None):
    if list is None:
        list = []
    list.append(item)
    return list
```

### Safe #2 (Scalar Default)
```python
def process(data, version=1):
    print(f"v{version}: {data}")
```

### Safe #3 (Constant Default)
```python
DEFAULT_CONFIG = {}
def get_config(overrides=DEFAULT_CONFIG):
    return overrides
```
