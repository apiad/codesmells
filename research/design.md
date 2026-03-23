# CodeSmells: Agentic Implementation Specification

## 1. System Overview & Agent Directives
This document is the implementation blueprint for `CodeSmells`, a neuro-symbolic CLI tool that orchestrates LLM agents through architectural refactoring.

**Directive to the Implementing AI:**
* **Architecture First:** Adhere strictly to the defined module boundaries. Do not merge the matching logic with the CLI routing logic.
* **Fail-Safe Parsing:** The system must never crash on malformed syntax. Assume all input text is highly entropic.
* **Stateless Execution, Stateful Storage:** The CLI commands must be stateless scripts that read/write mutations exclusively to the local SQLite database.

---

## 2. Module 1: The Probabilistic Lexer (`lexer.py`)
This module maps raw source code into the continuous similarity space. It does not construct an AST.

### 2.1. Data Structures
Define a `Token` dataclass:
* `token_class`: Enum (`KEYWORD`, `OPERATOR`, `IDENTIFIER`, `LITERAL`, `GAP`, `SIGIL`).
* `value`: String (the raw text).
* `weight`: Float (Information density).
* `line_num`, `col_num`: Integers (for trace reporting).

### 2.2. Lexical Heuristics (The Fallible Scanner)
Implement a regex-based scanner that categorizes tokens using a cascading fallback:
1.  **Gaps & Sigils:** Match `...` as `GAP`. Match `$([A-Z0-9_]+)` as `SIGIL`.
2.  **Operators:** Match non-alphanumeric clusters (e.g., `==`, `=>`, `{`). Assign $w = 1.0$.
3.  **Keywords:** Match against a provided set of generic multi-language keywords (`def`, `class`, `import`, `return`). Assign $w = 1.0$.
4.  **Identifiers:** Match standard word boundaries. Assign $w = 0.5$.
5.  **Literals:** Match string contents and numbers. Assign $w = 0.2$.

---

## 3. Module 2: The Fuzzy Alignment Engine (`alignment.py`)
This is the core algorithmic engine. It computes the similarity index between a candidate sequence $C$ and an example template $E$.

### 3.1. The Substitution Matrix $M$
Implement a scoring function $M(t_c, t_e)$ for two tokens:
* If $t_e$ is `GAP`: Score is $0$ (handled by affine penalties).
* If $t_e$ is `SIGIL`: Score is $t_c.weight$ (deferred to CSP validation).
* If $t_c.value == t_e.value$: Score is $t_c.weight \times 2$.
* Else: Score is $-\infty$ (mismatch penalty).

### 3.2. Smith-Waterman with Affine Gaps
Implement the dynamic programming matrix $H$ where $H_{i,j}$ is the maximum similarity of $C[1..i]$ and $E[1..j]$.
Use affine gap penalties: Gap Open ($\gamma = -2.0$), Gap Extension ($\epsilon = -0.1$).

The recurrence relation is:
$$H_{i,j} = \max \begin{cases} 0 \\ H_{i-1, j-1} + M(C_i, E_j) \\ \max_{k \ge 1} (H_{i-k, j} - (\gamma + k\epsilon)) \\ \max_{l \ge 1} (H_{i, j-l} - (\gamma + l\epsilon)) \end{cases}$$

### 3.3. The Binding Constraint Solver (CSP)
During the traceback of the alignment matrix, collect all pairs where $t_e$ is a `SIGIL` and $t_c$ is an `IDENTIFIER`.
1.  Initialize an empty dictionary `bindings = {}`.
2.  For each pair $(s, id)$:
    * If $s \notin bindings$: `bindings[s] = id.value`.
    * If $s \in bindings$ and $bindings[s] \neq id.value$: The constraint fails. Reject this alignment path.

### 3.4. Similarity Index Calculation
Normalize the final raw score $A(C,E)$ from the traceback:
$$S(C, E) = \frac{A(C, E)}{\sum_{t \in E} t.weight}$$
If $S(C, E) > \tau$ (where $\tau$ is defined in the rule's YAML), flag as a match.

---

## 4. Module 3: Knowledge Base & State (`storage.py`)
### 4.1. YAML/Markdown Parser
Implement a parser that reads `.smell.md`.
* Extract `pre_filters` from YAML frontmatter.
* Extract code blocks under `### Anti-Pattern`, `### Safe`, and `### Refactoring`.

### 4.2. Local SQLite Schema
Initialize `.codesmells/session.db` with the following schema:
* `table_candidates`: `id` (hash), `rule_id`, `file_path`, `line_num`, `raw_snippet`, `status` (PENDING, ACCEPTED, IGNORED).
* `table_bindings`: `candidate_id`, `sigil`, `bound_value`.

---

## 5. Module 4: The CLI Orchestrator (`cli.py`)
Implement `argparse` or `click` routing for the following commands. Ensure output is strictly formatted for LLM consumption.

### 5.1. `scan [dir]`
1.  Parse all `.smell.md` files.
2.  Walk directory. Apply deterministic `pre_filters` (regex).
3.  Pass pre-filtered snippets to `alignment.py`.
4.  Write matches to `table_candidates`.
5.  **Output:** Tabular list of pending IDs. Append `[NEXT_STEP]` instructing the use of `inspect`.

### 5.2. `inspect <id>`
1.  Fetch candidate and `bindings` from DB.
2.  Fetch Semantic Rule text from `.smell.md`.
3.  **Output:** Formatted Binding Trace (e.g., `$DB -> pool`). Append `[NEXT_STEP]` instructing `suggest` or `ignore`.

### 5.3. `suggest <id>`
1.  Fetch `### Refactoring` template from `.smell.md`.
2.  Perform string substitution replacing all `$SIGIL` occurrences with the values from `table_bindings`.
3.  **Output:** The hydrated code block.

### 5.4. `ignore <id> --template "<str>"`
1.  **Validation Gate 1:** Run `alignment.py` between the `--template` and the candidate's `raw_snippet`. Assert $S > 0.9$.
2.  **Validation Gate 2:** Assert the template contains at least one `$SIGIL` or `...`.
3.  **Validation Gate 3:** Run `alignment.py` between the `--template` and all `### Anti-Pattern` blocks for that rule. Assert $S < 0.5$.
4.  If all pass, append the template to the `.smell.md` file under `### Safe`. Update DB status to IGNORED.

---

## 6. Execution Constraints
* **Dependencies:** Standard library only where possible, supplemented by `pyyaml` for manifest parsing and `sqlite3` for state. Do not introduce heavy ML frameworks (no PyTorch/TensorFlow). The matrix operations must be implemented natively.
* **Performance:** The Smith-Waterman alignment must only trigger on snippets that pass the $O(1)$ YAML pre-filters to prevent blocking the event loop during `scan`.
