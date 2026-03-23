# CodeSmells: Expert Agentic Refactoring

This skill provides expert procedural guidance for AI agents interacting with the `codesmells` CLI to manage architectural anti-patterns through fuzzy alignment and probabilistic lexing.

## Strategic Core Mandates

1.  **Empirical Detection:** Never guess if a pattern is a smell. Use `codesmells scan` and `codesmells inspect` to confirm occurrences with concrete similarity scores and sigil bindings.
2.  **Verifiable Rules:** Every new rule (`.smell.md`) MUST have a corresponding test suite (`.smell.test.md`). A rule is not complete until `codesmells validate` passes.
3.  **Conservative Refactoring:** Always use `codesmells suggest` to preview a refactoring before applying changes to the source code.

## Comprehensive Workflow

### 1. Initialization & Discovery
-   **When to `init`:** Run `codesmells init` at the start of any new project engagement to set up the `.codesmells/` environment.
-   **When to `add`:** Create a new rule whenever you identify a recurring architectural anti-pattern (e.g., bare exceptions, improper resource handling, hardcoded configurations).
    ```bash
    codesmells add "My New Rule" "Brief description of the smell"
    ```

### 2. Rule Engineering & Validation
-   **Anatomy of a Rule:** 
    -   Use `$SIGILS` for variable parts of the code (identifiers, literals).
    -   Use `...` (gaps) to skip irrelevant middle code.
    -   Adjust `tau` (threshold) in the frontmatter if matches are too loose or too strict.
-   **Testing:** Populate the `### Anti-Pattern` and `### Safe` sections in the `.smell.test.md` file.
-   **Verification:** Run `codesmells validate` to ensure your rule correctly catches bad patterns and ignores safe ones.

### 3. Scanning & Analysis
-   **Scanning:** Run `codesmells scan .` to find all matches for active rules.
-   **Reviewing:** Use `codesmells status` to get an overview of the session.
-   **Deep Dive:** Use `codesmells inspect <id>` to see the exact code snippet, its similarity score, and how sigils were bound to actual values.

### 4. Refactoring & Resolution
-   **Previewing Fixes:** Run `codesmells suggest <id>` to see how the rule's `refactor_template` hydrates with the captured sigil bindings.
-   **Applying Fixes:** If the suggestion is correct, manually apply it to the source code and then run `codesmells accept <id>`.
-   **Handling False Positives:** If a match is safe but caught by a rule, use `codesmells ignore <id> --template "<safe-pattern>"` to add a specific safe example to the rule definition.
    -   **Rule for Ignoring:** The template provided to `ignore` MUST contain at least one `$SIGIL` or `...` and must pass the internal validation gates (similarity to snippet > 0.7, similarity to anti-pattern < 0.9).

### 5. Session Finalization
-   Run `codesmells finish` once all candidates are either `ACCEPTED` or `IGNORED`. This prints a summary report and clears the session state.

## Best Practices for AI Agents

-   **High Precision:** Prefer adding `pre_filters` to your rules to avoid scanning files that don't contain relevant keywords.
-   **Binding Awareness:** When inspecting, pay close attention to the **Bindings** table. If a sigil is bound to the wrong value, your rule might be too generic.
-   **Documentation:** Use the `### Refactor Explanation` section in your rules to provide "why" context for future maintainers.
