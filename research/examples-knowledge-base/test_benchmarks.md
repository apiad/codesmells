# Quality Benchmarks for Smell Tests

This document defines what constitutes a high-quality `.smell.test.md` file for validating CodeSmells rules.

## 1. Robust Pattern Definition

### Candidates (Bad Code)
*   **Coverage:** Include at least 3-5 variations of the smell.
*   **Minimalism:** Each candidate should focus *only* on the smell being tested.
*   **Realism:** Snippets should look like real code, not just "test cases".
*   **Edge Cases:** Include variations like different spacing, comments, or variable naming.

### Safe (Good Code)
*   **Contrast:** For every candidate, there should be a corresponding "Safe" snippet showing the refactored version.
*   **False Positives:** Include code that *looks* like the smell but isn't (e.g., a function named `save_and_email` that actually has a single responsibility but a poor name).
*   **Standard Patterns:** Include common idiomatic patterns for that language that must *not* trigger the rule.

## 2. Language-Specific Considerations

### Syntax Edge Cases
*   **Comments:** Ensure rules don't trigger on comments (e.g., "TODO: fix hardcoded api key").
*   **Strings vs Code:** Distinguish between actual code patterns and strings containing those patterns.
*   **Multi-line Patterns:** For languages like Python or JS, test how the rule handles different indentation and line breaks.

## 3. Benchmark Scoring for Rules

A "Gold Standard" rule must:
1.  **Pass 100% of its tests.**
2.  **Have a Tau value (0.0 to 1.0)** that balances precision and recall (usually 0.7 to 0.9).
3.  **Include clear "Why" documentation** in its `rule.md` front-matter.
4.  **Provide actionable "Next Steps"** for the user when a candidate is detected.
