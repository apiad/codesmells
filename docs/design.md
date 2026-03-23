# Internal Design & Architecture

CodeSmells is built on a modular, data-driven architecture that prioritizes flexibility over strict syntax parsing.

## System Architecture

The core of CodeSmells consists of four primary components:

1.  **Probabilistic Lexer (`lexer.py`):**
    A regex-based scanner that maps source code into a sequence of **weighted tokens**. It avoids building an Abstract Syntax Tree (AST), making it robust to syntax errors and cross-language patterns.
    - **Keywords:** High weight (1.0).
    - **Operators/Sigils:** High weight (1.0).
    - **Identifiers:** Lower weight (0.5) to allow for name variations.
    - **Literals:** Lowest weight (0.2).

2.  **Fuzzy Alignment Engine (`alignment.py`):**
    The heart of the system. It implements the **Smith-Waterman algorithm** with affine gap penalties to find the optimal local alignment between a rule's `anti_pattern` and a target code snippet.
    - **Tau ($\tau$):** A similarity threshold (default 0.4). If the normalized alignment score is $\ge \tau$, a candidate is detected.
    - **Sigils ($VAR):** Special tokens that capture values during alignment and are used for refactoring hydration.
    - **Gaps (...):** Explicit tokens that match any sequence of tokens with zero score, allowing for middle-code skips.

3.  **Storage & Rule Manager (`storage.py`):**
    Handles the parsing of Markdown-based rule templates (`.smell.md`) and rule tests (`.smell.test.md`). It also manages the persistence of scan sessions in `session.json`.

4.  **CLI Interface (`cli.py`):**
    A high-signal interface powered by `Typer` and `Rich`, providing interactive workflows for both humans and AI agents.

## Data Flow

1.  **Ingestion:** The `RuleParser` loads templates from `.codesmells/`.
2.  **Lexing:** The `ProbabilisticLexer` tokenizes both the rule templates and the target codebase.
3.  **Alignment:** The `FuzzyAlignmentEngine` compares target tokens against template tokens, producing a similarity score and sigil bindings.
4.  **Reporting:** Matches exceeding the $\tau$ threshold are saved as `Candidates` and presented via the CLI.
5.  **Refactoring:** The `suggest` command uses captured sigil bindings to "hydrate" the rule's `refactor_template`.
