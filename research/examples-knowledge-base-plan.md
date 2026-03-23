# CodeSmells Knowledge Base Expansion Plan

## Executive Summary
This research plan outlines a comprehensive strategy for expanding the `examples/` directory of the CodeSmells project into a robust, multi-language knowledge base. We have identified high-impact code smells for 10 mainstream programming languages, mapped abstract security and SOLID principles to detectable patterns, and established an architectural framework for organizing these examples. By implementing this plan, CodeSmells will provide users with immediate value through a library of pre-defined, high-quality rules for Python, JavaScript, TypeScript, C/C++, Java, C#, Rust, Go, HTML, and CSS.

## Research Questions

### 1. Language-Specific Smells & Anti-patterns
High-impact smells have been identified for 10 target languages, focusing on patterns with distinctive structural signatures detectable by CodeSmells' fuzzy alignment engine. Key findings include "Broad Exception Catching" in Python, "'Any'-script" in TypeScript, and "Unsafe Pointer Arithmetic" in C/C++.
- **Detailed Assets:** [language_smells.md](examples-knowledge-base/language_smells.md)

### 2. Security & SOLID Violations as Detectable Patterns
Abstract principles like OWASP Top 10 vulnerabilities and SOLID design principles have been mapped to concrete code patterns. This includes detecting SQL injection via string concatenation and Single Responsibility Principle violations via "And" functions.
- **Detailed Assets:** [security_solid_mapping.md](examples-knowledge-base/security_solid_mapping.md)

### 3. Knowledge Base Architecture
A scalable folder hierarchy has been designed to support multi-language growth: `examples/<lang>/<category>/<smell_id>/`. This structure includes standardized files for "bad" code, "good" code, the rule template, and its validation test.
- **Detailed Assets:** [architecture.md](examples-knowledge-base/architecture.md)

### 4. Quality Benchmarks for Smell Tests
Standardized criteria for "Gold Standard" rules and test files have been established. This includes requirements for robust candidate/safe coverage, handling syntax edge cases like comments, and balancing precision via the `tau` parameter.
- **Detailed Assets:** [test_benchmarks.md](examples-knowledge-base/test_benchmarks.md)

## Conclusions
The CodeSmells engine is well-suited for detecting a wide range of language-specific, security, and design smells. A structured, multi-language approach is essential for scaling the project's knowledge base and providing a "batteries-included" experience for developers.

## Recommendations
1.  **Phase 1 Execution:** Immediately begin populating the `examples/python/` and `examples/js/` directories following the [Architecture Guide](examples-knowledge-base/architecture.md).
2.  **Rule Library:** Package these examples as a "Standard Library" that can be imported into projects using the `install-skill` command (or a future `import-rule` command).
3.  **Community Contributions:** Create a `CONTRIBUTING.md` guide specifically for adding new smells to the knowledge base based on the [Quality Benchmarks](examples-knowledge-base/test_benchmarks.md).
4.  **Follow-up Research:** Investigate more complex "Cross-File Smells" that may require graph-based analysis beyond single-file text alignment.

---
**Note:** Research is complete. You can now use the `/draft` command to turn this executive report into a fully fleshed-out article or implementation roadmap.
