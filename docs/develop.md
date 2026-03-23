# Contributor's Guide

Welcome to the CodeSmells project! This guide outlines the development workflow and coding standards for contributors.

## Development Setup

CodeSmells uses `uv` for dependency management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/apiad/codesmells.git
    cd codesmells
    ```

2.  **Sync dependencies:**
    ```bash
    uv sync
    ```

3.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

## Core Workflow

### Testing
We use `pytest` for all unit and integration tests.
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_lexer.py
```

### Linting & Formatting
We use `ruff` for linting and code formatting.
```bash
# Check for issues
make lint

# Automatically fix issues
ruff check . --fix
```

### Building
The `makefile` provides shortcuts for common tasks:
- `make all`: Run linting and tests.
- `make clean`: Remove build artifacts and caches.

## Coding Standards

- **Type Hints:** All new code must be fully type-hinted.
- **Docstrings:** Use Google-style docstrings for all public classes and methods.
- **Modern Python:** We target Python 3.13+. Use modern features like `match` statements and `dataclasses`.
- **Architectural Integrity:** CodeSmells is designed to be modular. Avoid tight coupling between the CLI and the core engines.

## Git Workflow

- Use descriptive branch names (e.g., `feature/add-alignment-heuristics`).
- Prefer atomic commits with clear messages.
- Always run `make all` before submitting a pull request.
