# Plan: Implement `validate` Command and Update `add` Command

## Objective
Implement a `validate` command to verify rule correctness against test snippets and update the `add` command to scaffold these tests automatically.

## 1. Context & Rationale
To ensure that rule modifications don't break detection or introduce false positives, we need a verification layer. `.smell.test.md` files will provide "ground truth" examples for each rule.

## 2. Proposed Changes

### `src/codesmells/models.py`
- Add a `RuleTest` model to represent the test cases (Anti-Patterns and Safe examples).

### `src/codesmells/storage.py`
- Add `load_rule_test(rule_id: str)` to `StorageManager`.
- This method will look for `{rule_id}.smell.test.md` and extract code blocks from `### Anti-Pattern` and `### Safe` sections.

### `src/codesmells/cli.py`
- **Update `add` command**:
  - In addition to `.smell.md`, create `.smell.test.md`.
  - Boilerplate should include:
    ```markdown
    # Test: [Rule Name]
    
    ### Anti-Pattern
    ```python
    # Snippet that MUST match
    ```
    
    ### Safe
    ```python
    # Snippet that MUST NOT match
    ```
    ```
  - Update output message to instruct the user to fill the test file and run `validate`.

- **Implement `validate` command**:
  - Signature: `validate(rule_id: Optional[str] = None)`.
  - Logic:
    1. Identify target rules (one or all).
    2. For each rule:
       - Load the rule and its corresponding test file.
       - If test file is missing, skip or warn.
       - For each snippet in `### Anti-Pattern` of test file:
         - Run `engine.align(rule.anti_pattern, snippet)`.
         - Verify `score >= rule.tau`.
       - For each snippet in `### Safe` of test file:
         - Run `engine.align(rule.anti_pattern, snippet)`.
         - Verify `score < rule.tau`.
    3. Print a detailed report of passes and failures.
    4. Exit with code 1 if any test fails.

## 3. Verification Plan
- **Manual Test `add`**: Verify two files are created.
- **Manual Test `validate`**: Create a rule and a test file. Verify that changing `tau` or the snippet affects `validate` output.
- **Automated Tests**:
  - `test_validate_success`: Rule matches its own anti-pattern test.
  - `test_validate_failure`: Rule matches a safe test or fails an anti-pattern test.

## 4. Task Linking
- Add a new task to `TASKS.md` for this feature.
