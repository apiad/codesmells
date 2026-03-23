---
id: py-ls-print-logging
title: Print instead of Logging
description: Using `print` for production messaging lacks the severity levels, structured formatting, and output redirection capabilities of the `logging` module. Logging is essential for monitoring and debugging production environments without cluttering standard output.
pre_filters:
  - "print"
tau: 0.83
---

# Print instead of Logging

### Anti-Pattern

```python
print(
```

### Refactoring

Use the `logging` module for production messages.

```python
import logging
logger = logging.getLogger(__name__)
logger.info($MSG)
```

### Refactor Explanation
`print` output is harder to manage in production. The `logging` module provides built-in support for different severity levels (DEBUG, INFO, ERROR), timestamps, and output destinations (files, network, etc.), making it more suitable for real applications.
