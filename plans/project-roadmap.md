# CodeSmells Project Roadmap

## Objective
To fully implement the `CodeSmells` neuro-symbolic CLI tool based on the specifications in `research/design.md`. This tool orchestrates LLM agents through architectural refactoring by identifying code patterns. The implementation will rely on a probabilistic lexer and a fuzzy alignment engine using the Smith-Waterman algorithm. State persistence will be strictly managed via JSON (replacing the initially specified SQLite).

## Architectural Impact
The implementation introduces a robust, four-stage pipeline:
1. **Lexing**: Converting highly entropic source code into a stream of categorized, weighted tokens without relying on strict AST generation.
2. **Alignment**: Utilizing dynamic programming (Smith-Waterman with affine gaps) to compute fuzzy match scores between code snippets and defined anti-patterns, while simultaneously solving for constraint bindings (`$SIGILS`).
3. **Storage**: Parsing `.smell.md` rule schemas and maintaining a stateful `.codesmells/session.json` to track candidate matches and their status (PENDING, ACCEPTED, IGNORED).
4. **CLI**: Providing a stateless interface (`scan`, `inspect`, `suggest`, `ignore`) that interacts with the JSON storage and coordinates the algorithmic core.

## Milestone 1: MVP - Core Engine (Lexer, Smith-Waterman, basic Storage)
*Focus: Implement the fundamental algorithmic blocks for parsing code and finding fuzzy matches.*

**Tasks:**
- [ ] **Enhance Lexer (`lexer.py`)**: Implement cascading fallback regex heuristics (Gaps, Sigils, Operators, Keywords, Identifiers, Literals) to robustly assign `TokenClass` and Information Density `weight`.
- [ ] **Implement Substitution Matrix (`alignment.py`)**: Create the scoring function $M(t_c, t_e)$ handling gaps, sigils, matches, and mismatches.
- [ ] **Implement Smith-Waterman Algorithm (`alignment.py`)**: Code the dynamic programming matrix $H$ with affine gap penalties ($\gamma = -2.0, \epsilon = -0.1$) to compute the maximal local alignment.
- [ ] **Implement CSP Solver (`alignment.py`)**: Extract bindings during the traceback phase, ensuring `$SIGIL` consistency across the match.
- [ ] **Implement Similarity Index (`alignment.py`)**: Calculate the normalized similarity score $S(C, E)$ and apply the $\tau$ threshold logic.
- [ ] **Implement JSON Storage (`storage.py`)**: Create functions to initialize `session.json` and handle CRUD operations for candidates and bindings using standard JSON (replacing SQLite).
- [ ] **Implement Rule Parser (`storage.py`)**: Develop a parser for `.smell.md` files to extract YAML frontmatter (`pre_filters`, $\tau$) and Markdown code blocks (`### Anti-Pattern`, `### Safe`, `### Refactoring`).

## Milestone 2: Functional CLI - (Scan, Inspect, Suggest)
*Focus: Connect the core engine to the command-line interface for user interaction.*

**Tasks:**
- [ ] **Implement `scan` Command (`cli.py`)**:
  - Parse all `.smell.md` rules via `storage.py`.
  - Walk the directory tree, applying $O(1)$ regex `pre_filters`.
  - Execute `alignment.py` on filtered snippets.
  - Write positive matches ($S > \tau$) to the JSON storage as `PENDING` candidates.
  - Render a tabular output of discovered IDs using `rich`.
- [ ] **Implement `inspect <id>` Command (`cli.py`)**:
  - Retrieve candidate and binding details from JSON storage.
  - Display the matched raw snippet, the specific rule triggered, and the extracted `$SIGIL` trace (e.g., `$DB -> pool`).
- [ ] **Implement `suggest <id>` Command (`cli.py`)**:
  - Fetch the `### Refactoring` template for the candidate's rule.
  - Perform string substitution, replacing `$SIGIL` occurrences with bound values from the JSON state.
  - Output the hydrated code block.

## Milestone 3: Advanced Features - (Ignore with validation, Refactoring templates)
*Focus: Implement the sophisticated ignore mechanism and dynamic safe-pattern generation.*

**Tasks:**
- [ ] **Implement `ignore <id> --template "<str>"` Command (`cli.py`)**:
  - **Validation Gate 1**: Execute alignment between the user's `--template` and the candidate's `raw_snippet` (Assert $S > 0.9$).
  - **Validation Gate 2**: Validate template complexity (Ensure it contains at least one `$SIGIL` or `...`).
  - **Validation Gate 3**: Execute alignment against all `### Anti-Pattern` blocks for the rule (Assert $S < 0.5$).
- [ ] **Dynamic Rule Updates (`storage.py`)**: Implement logic to safely append validated ignore templates to the respective `.smell.md` file under the `### Safe` section.
- [ ] **Update State (`storage.py`)**: Change the candidate's status to `IGNORED` in `session.json`.
- [ ] **Advanced Template Support**: Ensure the substitution engine securely handles multi-line templates, complex indentation, and overlapping `$SIGIL` definitions.

## Milestone 4: Production Ready - (Performance optimization, Multi-language support, Documentation, Packaging)
*Focus: Refine the tool for real-world usage and distribution.*

**Tasks:**
- [ ] **Performance Profiling**: Analyze the Smith-Waterman implementation using Python's `cProfile`. Optimize matrix operations natively to prevent blocking the event loop during extensive `scan` operations.
- [ ] **Multi-Language Lexing (`lexer.py`)**: Expand the generic keyword list and operator regex to encompass standard syntax from major languages (e.g., JS/TS, Go, Rust, Java).
- [ ] **Documentation (`README.md`, `docs/`)**: Write comprehensive user guides detailing rule creation (`.smell.md` syntax), CLI usage examples, and architectural concepts.
- [ ] **Packaging (`pyproject.toml`)**: Ensure all dependencies (e.g., `typer`, `rich`, `pyyaml`) are correctly specified. Verify standard entry points for the `codesmells` CLI via `uv.lock`.
