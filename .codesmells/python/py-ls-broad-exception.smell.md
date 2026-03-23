---
id: py-ls-broad-exception
title: Broad Exception Catching
description: Catching generic exceptions like `Exception` or using a bare `except:` masks unexpected errors and prevents them from being properly handled or diagnosed. This anti-pattern can hide critical failures, such as `KeyboardInterrupt` or syntax errors, making debugging significantly more difficult.
pre_filters:
  - "except"
tau: 0.75
---

# Broad Exception Catching

### Anti-Pattern

This code example demonstrates the Broad Exception Catching anti-pattern.

```python
except Exception as $E:
```

### Anti-Pattern

This code example demonstrates the Broad Exception Catching anti-pattern.

```python
except Exception:
```

### Anti-Pattern

This code example demonstrates the Broad Exception Catching anti-pattern.

```python
except:
```

### Refactoring

Catch specific exceptions that you expect and know how to handle.

```python
except ($EXCS) as $E:
```

### Refactor Explanation
Catching generic exceptions can mask unexpected errors (like `KeyboardInterrupt`, `SystemExit`, or typos in your code). It's better to catch only the specific exceptions your code is prepared to handle.
