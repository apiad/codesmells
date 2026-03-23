# Plan: Implement `init` and `add` Commands

## Objective
Add two new commands to the CodeSmells CLI:
1. `init`: Scaffolds the `.codesmells` environment in the current directory.
2. `add`: Quickly generates a boilerplate `.smell.md` rule file.

## 1. Context & Rationale
Currently, users must manually create the `.codesmells` folder and rule files. Providing `init` and `add` improves onboarding and ensures consistency in rule formatting.

## 2. Proposed Changes

### `src/codesmells/cli.py`
- Add `@app.command()` for `init`.
- Add `@app.command()` for `add`.

#### `init` Implementation:
- Check if `.codesmells` directory exists.
- If it exists, print a warning and exit with `typer.Exit(code=1)`.
- Create `.codesmells/` directory.
- Create `.codesmells/.gitignore` containing `session.json`.
- Print a success message and a call-to-action for the AI to initialize the codebase with rules.

#### `add` Implementation:
- Arguments: `name` (str), `description` (str).
- Convert `name` to kebab-case (e.g., "My Smell" -> "my-smell").
- Construct file path: `.codesmells/{kebab_name}.smell.md`.
- Check if file exists; if so, warn and exit.
- Generate boilerplate content using a template.
- Print success message instructing the AI to fill in the details.

### `src/codesmells/storage.py`
- (Optional) Add a method to `StorageManager` to handle boilerplate generation if logic gets complex, but for now, simple string templates in `cli.py` or a dedicated constant file should suffice.

## 3. Boilerplate Template
The template for `.smell.md` will include:
```markdown
---
tau: 0.4
pre_filters:
  - "relevant_keyword"
---
# [Smell Name]

[Short Description]

### Anti-Pattern
<!-- Describe the code pattern to avoid -->
```python
# Insert anti-pattern code here
```

### Refactoring
<!-- Describe the improved version -->
```python
# Insert refactored code here
```

### Refactor Explanation
<!-- Why is this better? -->

### Safe
<!-- Optional: examples that look like the anti-pattern but are safe -->
```python
# Insert safe example here
```
```

## 4. Verification Plan
- **Manual Test `init`**: Run `codesmells init`. Verify `.codesmells/` and `.gitignore` are created. Run again and verify it exits with a warning.
- **Manual Test `add`**: Run `codesmells add "My Rule" "A description"`. Verify `my-rule.smell.md` is created with the correct boilerplate.
- **Automated Tests**: Add new test cases in `tests/test_cli.py` for `test_init_basic` and `test_add_basic`.
