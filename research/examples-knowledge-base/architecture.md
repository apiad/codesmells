# Knowledge Base Architecture for CodeSmells

This document outlines the proposed structure for the `examples/` directory to support a multi-language, scalable knowledge base of code smells.

## 1. Directory Hierarchy
The structure should follow a language-first approach, then category, then the specific smell.

```text
examples/
├── <language>/             # e.g., python, js, rust
│   ├── <category>/         # e.g., security, solid, complexity
│   │   ├── <smell_id>/     # e.g., hardcoded_secrets, large_method
│   │   │   ├── bad.<ext>   # File containing the "smell"
│   │   │   ├── good.<ext>  # File containing the "refactored" version
│   │   │   ├── rule.md     # The actual CodeSmells rule template
│   │   │   └── test.md     # The .smell.test.md for this rule
```

## 2. Standardized File Naming
*   **bad.<ext>**: Contains at least one clear instance of the smell. This file should be used for demonstration and manual testing.
*   **good.<ext>**: Contains the refactored version of `bad.<ext>`. This serves as documentation for the user.
*   **rule.md**: The production rule file that will be placed in `.codesmells/` in real projects.
*   **test.md**: The validation test suite for that rule. This should include both the `bad.<ext>` snippets as "Candidates" and `good.<ext>` snippets as "Safe".

## 3. Metadata and Tags
Each `rule.md` should include front-matter metadata to help categorize and search for smells:

```yaml
---
id: "lang-category-smell"
title: "Readable Title"
description: "Detailed description of the smell."
tags: ["security", "solid", "language-specific"]
tau: 0.8
---
```

## 4. Multi-language Mapping
Some smells are universal (e.g., "Hardcoded Secrets"). These should have separate entries in each language folder to ensure the patterns are accurate for that language's syntax:

- `examples/python/security/hardcoded_secrets/`
- `examples/js/security/hardcoded_secrets/`
- `examples/rust/security/hardcoded_secrets/`
