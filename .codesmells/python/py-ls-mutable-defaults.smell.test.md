---
rule_id: py-ls-mutable-defaults
---

### Anti-Pattern #1 (List Default)

This code example demonstrates the Mutable Default Arguments anti-pattern. Specifically, it illustrates the `List Default` case.

```python
def add_to(item, list=[]):
    list.append(item)
    return list
```

### Anti-Pattern #2 (Dict Default)

This code example demonstrates the Mutable Default Arguments anti-pattern. Specifically, it illustrates the `Dict Default` case.

```python
def get_config(overrides={}):
    config = {"default": True}
    config.update(overrides)
    return config
```

### Anti-Pattern #3 (Class __init__)

This code example demonstrates the Mutable Default Arguments anti-pattern. Specifically, it illustrates the `Class __init__` case.

```python
class User:
    def __init__(self, roles=[]):
        self.roles = roles
```

### Safe #1 (None Default)

This code example demonstrates a safe approach for the Mutable Default Arguments issue. Specifically, it illustrates the `None Default` case.

```python
def add_to(item, list=None):
    if list is None:
        list = []
    list.append(item)
    return list
```

### Safe #2 (Scalar Default)

This code example demonstrates a safe approach for the Mutable Default Arguments issue. Specifically, it illustrates the `Scalar Default` case.

```python
def process(data, version=1):
    print(f"v{version}: {data}")
```

### Safe #3 (Constant Default)

This code example demonstrates a safe approach for the Mutable Default Arguments issue. Specifically, it illustrates the `Constant Default` case.

```python
DEFAULT_CONFIG = {}
def get_config(overrides=DEFAULT_CONFIG):
    return overrides
```
