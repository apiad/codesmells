# Plan: Implement `install-skill` Command

## Objective
Add a new command `install-skill` to the `codesmells` CLI that installs a `SKILL.md` file for AI agents (Gemini CLI, Claude Code, etc.), providing detailed instructions on how to use the tool effectively.

## Proposed Changes

### 1. Template Creation
- **File**: `src/codesmells/templates/SKILL.md`
- **Content**:
    - Comprehensive guide for AI agents on using `codesmells`.
    - Detailed explanation of the `init -> add -> validate -> scan -> status -> inspect -> suggest -> accept/ignore -> finish` workflow.
    - Template structures for `.smell.md` and `.smell.test.md`.
    - Best practices for rule creation and refactoring suggestions.

### 2. CLI Command Implementation
- **File**: `src/codesmells/cli.py`
- **Function**: `install_skill(skills_path: str = None)`
- **Logic**:
    - **No Arguments**: Print instructions on default skill directory locations for various agents (e.g., `.gemini/skills`, `.claude/skills`).
    - **With Argument**:
        - Create the destination directory if it doesn't exist (e.g., `<skills_path>/codesmells/`).
        - Copy/write the content from the `src/codesmells/templates/SKILL.md` template.
        - **Idempotency**: Inform the user if the skill is already installed; only overwrite if a `--force` flag is provided (optional).
- **Integration**:
    - Register the command in the main CLI entry point.
    - Append a "final note" to the CLI's main output or session finalization to suggest `install-skill` for AI agents.

### 3. File Management
- Ensure `src/codesmells/templates/` is included in the package distribution (update `pyproject.toml` if necessary).

## Verification Plan

### Manual Verification
1. Run `uv run codesmells install-skill` and verify the instructions for AI agents are displayed.
2. Run `uv run codesmells install-skill .test-skills/` and verify that `.test-skills/codesmells/SKILL.md` is created correctly.
3. Run the same command again to ensure it handles the existing file gracefully.

### Automated Testing
1. Add a new test file `tests/test_install_skill.py`.
2. Mock the file system to verify that the template is read and written to the correct location.
3. Assert that the command output matches expectations for both the "instructions" and "installation" modes.
