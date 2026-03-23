# Installation & Execution Guide

CodeSmells is built with modern Python tooling and is easiest to manage using `uv`.

## Installation

### Using `uv` (Recommended)

If you have `uv` installed, you can run CodeSmells directly or install it into your environment:

```bash
# Run without installing
uv run codesmells --help

# Install as a tool
uv tool install codesmells
```

### Using `pip`

You can also install it via `pip` from the source directory:

```bash
pip install .
```

## Running CodeSmells

The primary entry point is the `codesmells` command. 

### Basic Commands

| Command | Description |
| :--- | :--- |
| `init` | Creates the `.codesmells/` directory and initial configuration. |
| `add <name> <desc>` | Adds a new `.smell.md` rule and a `.smell.test.md` test file. |
| `scan [dir]` | Scans the specified directory (defaults to `.`) for matches. |
| `status` | Shows the results of the last scan and pending candidates. |
| `validate` | Runs the internal validation suite for your rules. |

### Advanced Usage

#### Installing AI Agent Skills
To enable AI agents to use CodeSmells effectively, install the `SKILL.md` file into your agent's configuration directory (e.g., `.gemini/skills/`):

```bash
codesmells install-skill .gemini/skills/
```

#### Environment Variables
- `PYTHONPATH`: Ensure the `src` directory is in your path if running from source.
