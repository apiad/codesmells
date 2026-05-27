# Codesmells — Agent-First Vision

**Date:** 2026-05-27
**Status:** design, supersedes `research/design.md` and `plans/project-roadmap.md`
**Implementation path:** hybrid — keep `lexer.py` + `alignment.py`, rewrite the surface

---

## 1. Vision

Codesmells is a deterministic, agent-first CLI for detecting code anti-patterns. Two principles separate it from existing linters:

1. **Rules are deterministic; fixes are agentic.** Author-written `.smell.md` rules encode *what* a smell is. The agent decides *how* to fix it. The tool never decides whether something is a smell — that judgement is encoded in committed rules, reviewed like any other code.

2. **One tool, two consumers.** The same binary serves an agent doing interactive refactoring (Claude says "check this repo for smells" → runs `codesmells scan` → drills in per finding → fixes) and a CI gate that returns rc=1 if any unresolved smell exists. The agent's output and CI's output share one terse natural-language format — no JSON, no decoration, designed so an agent parses it with `read()` and a human reads it without thinking.

Both consumers benefit from the same property: codesmells localizes the work. The agent doesn't grep the codebase; it asks the tool for the local context it needs to act. The CI doesn't run a full static-analysis pass; it asks the same question with a stricter exit-code contract.

---

## 2. Architecture

### 2.1 Module layout after rebuild

| Module | Status | Role |
|---|---|---|
| `codesmells/lexer.py` | keep | Probabilistic regex lexer (KW / IDENT / LITERAL / OP / SIGIL / GAP) |
| `codesmells/alignment.py` | keep | Smith-Waterman + affine gaps + CSP-on-traceback |
| `codesmells/types.py` | new — replaces `models.py` | Minimal dataclasses: `Token`, `Rule`, `Finding` |
| `codesmells/rules.py` | new — replaces parts of `storage.py` | `.smell.md` parse, language detection, library access, copy/refresh |
| `codesmells/scanner.py` | new | Windowed multi-fire matcher; produces `Finding`s |
| `codesmells/cli.py` | rewrite | Built on `microcli`; terse text output; stateless commands |
| `codesmells/library/*.smell.md` | new | Bundled curated rule set |

The cut line is clean: lexer + alignment + their 17 algorithmic tests survive untouched. Everything else gets rewritten against the new vision.

### 2.2 Dependencies

- **Add:** `microcli-toolkit` — decorator-based agent-first CLI framework (commands, stdin, `--learn`, `.explain()`)
- **Remove:** `typer`, `rich` — replaced by microcli's `ok/fail/info/warn/step` helpers
- **Keep:** `pyyaml` — `.smell.md` frontmatter parsing

### 2.3 State model

**Stateless.** No `session.json`. Each invocation is a complete computation from rules + source code. The only durable artefacts are:

- `.codesmells/*.smell.md` — the project's active rule files (each is a copy of a library rule or a hand-written rule, freely edited)
- Per-site `# codesmells: ignore <rule-id>` comments inside source files

`Finding` IDs are deterministic hashes derived from rule + file + anchor line + canonical snippet, so `inspect <id>` re-runs the scan and finds the same finding across calls.

---

## 3. CLI surface

All commands are non-interactive, one-shot, agent-callable. Inputs via flags or stdin; outputs via microcli's terse helpers; exit codes carry semantics.

| Command | Purpose | Exit code |
|---|---|---|
| `codesmells init [--all \| --select <ids> \| <stdin>]` | Detect languages, probe library, copy picked rules to `.codesmells/`. No-arg form is preview-only. | 0 |
| `codesmells scan [dir]` | List all findings, one per line. | 0 always |
| `codesmells inspect <id>` | Print the finding's local context (snippet, bindings, why). | 0 / non-zero if id unknown |
| `codesmells suggest <id>` | Print the hydrated refactor template + explanation. | 0 / non-zero if id unknown |
| `codesmells ignore <id> <stdin>` | Pattern-mode exception: gate-validated, appended to rule's `### Safe`. | 0 / non-zero with per-gate diagnostic on failure |
| `codesmells ignore <id> --here --reason="<txt>"` | Per-site comment inserted at the finding's anchor line. `--reason` required. | 0 / non-zero on failure |
| `codesmells check [dir]` | Same scan as `scan`; rc=1 if any finding exists. For CI. | 0 if clean, 1 if smells found |
| `codesmells add <rule-id>` | Copy a specific library rule into the project (post-init). | 0 |
| `codesmells refresh <rule-id>` | Re-copy library version of a rule; warns if local has divergent `### Safe`. | 0 / 2 if divergence |
| `codesmells --learn [<cmd>]` | Free affordance from microcli; agent uses it to self-discover the tool. | 0 |

Removed from current impl: `status`, `accept`, `finish` — all stateful, no longer meaningful.

### 3.1 Output style

Predictable line shapes. No boxes, no colors as semantic carriers (microcli may use a leading symbol like `✓`/`✗`/`→` — that's fine; it's noise an agent strips). Every command ends with a `next:` hint pointing at the most likely follow-up command, derived via microcli's `.explain()`.

Examples:

```
$ codesmells scan
3 smells in 1 file

a3b2  catch-all-exception   src/processor.py:21
9f81  print-instead-of-log  src/processor.py:5
9f82  print-instead-of-log  src/processor.py:8

next: codesmells inspect a3b2
```

```
$ codesmells inspect a3b2
rule:  catch-all-exception
file:  src/processor.py:21

  19  try:
  20      data = json.load(f)
  21  except Exception as e:
  22      print(f"error: {e}")
  23      return None

bindings: $VAR=e

why: catching Exception broadly hides errors. Catch specific types.

next: codesmells suggest a3b2 | codesmells ignore a3b2 [--here]
```

```
$ codesmells check
1 smell remaining

a3b2  catch-all-exception   src/processor.py:21

exit 1
```

---

## 4. Rule format & library

### 4.1 `.smell.md` schema

```markdown
---
id: catch-all-exception          # explicit, decoupled from filename
lang: [python]                   # NEW — one or more language tags
tau: 0.7                         # similarity threshold (recalibrated, see §5.4)
severity: warn                   # NEW — info | warn | error (reserved for CI gating)
pre_filters:
  - "except Exception"
---

# Avoid Catch-All Exceptions

Catching `Exception` broadly hides errors. Catch specific types you expect.

### Anti-Pattern

```python
try:
    ...
except Exception as $VAR:
    ...
```

### Safe

```python
try:
    ...
except ValueError as $VAR:
    ...
```

### Refactoring

Replace `Exception` with the specific type you expect to handle.

```python
try:
    ...
except ValueError as $VAR:
    ...
```
```

Three frontmatter additions vs current: `id` (explicit), `lang` (list), `severity` (reserved). Section semantics (`### Anti-Pattern` / `### Safe` / `### Refactoring`) and `$SIGIL` / `...` template syntax are unchanged.

### 4.2 Library structure

```
codesmells/library/
  python/
    catch-all-exception.smell.md
    print-instead-of-log.smell.md
    mutable-default-argument.smell.md
    bare-return.smell.md
    ...
  generic/
    todo-fixme.smell.md       # lang: [any]
    ...
```

Layout-by-language is for human navigation; `lang:` in frontmatter is authoritative. The MVP curated set is ~5–10 rules across `python/` plus 1–2 in `generic/`. Exact list deferred to the implementation plan.

### 4.3 Project layout after `init`

```
.codesmells/
  catch-all-exception.smell.md     # copied from library
  print-instead-of-log.smell.md    # copied from library
  acme-specific-rule.smell.md      # project-authored
```

Flat directory of `*.smell.md`. No manifest, no config file at this layer. Library rules and project rules are interchangeable from the scanner's perspective.

---

## 5. Scanning model

### 5.1 Pipeline per file

1. **Read + lex.** Tokenize the file once; keep the full token stream with line/column info.
2. **Pre-filter gate.** For each rule, check `pre_filters` against raw file text. Skip the rule entirely if any required filter is absent.
3. **Per-site ignore harvest.** Scan the file text for `codesmells: ignore <rule-id>` comments (comment syntax determined by file extension — Python `#`, JS/TS/Go `//`). Build an ignore-set keyed by `(rule_id, line_range)`.
4. **Windowed match.** For each surviving (file, rule) pair, slide a token-window over the file's token stream. Window size ≈ `2 × len(anti_pattern_tokens)`, clamped to a minimum. For each window, run `alignment.align(window, anti_pattern_tokens)`. If `score >= rule.tau` and the match's anchor line is not in the ignore-set, emit a `Finding`.
5. **Safe-pattern guard.** Before emitting, re-align the matching window against every `### Safe` pattern of the rule. If any safe-score `>= tau_safe` (constant, e.g. 0.7), suppress the finding.
6. **Dedup.** Collapse findings to one per `(rule_id, file, anchor_line)`. Anchor is the first matched token's line.

### 5.2 Deterministic ID

```
id = md5(rule_id + ":" + file_path + ":" + anchor_line + ":" + canonical_snippet).hexdigest()[:8]
```

`canonical_snippet` is whitespace-normalized — trivial reformatting doesn't churn IDs. Same smell at the same place produces the same id across runs, which is what makes `inspect <id>` work in a stateless world.

### 5.3 Finding payload

```python
@dataclass
class Finding:
    id: str
    rule_id: str
    file_path: str
    anchor_line: int
    end_line: int
    snippet: str              # source lines ±5 around the anchor
    bindings: dict[str, str]  # e.g. {"$VAR": "e"}
    score: float
```

Never persisted. Produced fresh per `scan`/`inspect`/`check`. `inspect <id>` re-scans only the file containing that id — cheap because IDs encode the file path.

### 5.4 Normalization

The current code computes:

```
S(C, E) = raw_score / (2.0 × sum(t.weight for t in template))
```

This is correct math: `score_match` returns `tc.weight × 2.0` for an exact match, so a perfect alignment has raw score `2.0 × Σ_t.weight`. Dividing by the same `2.0 × Σ_t.weight` puts scores in `[0, 1]` for typical matches.

(The earlier spec at `research/design.md` §3.4 wrote the formula as `A / Σ_t.weight` and omitted the 2× — that was an incomplete spec, not a code bug. The rebuild keeps the existing implementation untouched and recalibrates the thresholds against the `[0, 1]` range it actually produces.)

Default thresholds (calibrated against the `[0, 1]` range the existing implementation produces; matches what the current `cli.py` ignore command already uses in practice):

- Rule `tau` (anti-pattern firing): `>= 0.4` to `>= 0.7` per rule (per-rule override in frontmatter)
- `tau_safe` (safe-pattern guard): `0.7`
- Gate 1 (faithful): `>= 0.7`
- Gate 3 (distinct): `< 0.9` for all anti-patterns of the rule

The `0.9` distinct threshold is deliberately loose — sigil-substituted anti-patterns can score around 0.7–0.8 against each other even when semantically distinct (e.g., `except Exception` vs `except ValueError`), so the gate only rejects near-identical resubmissions of the anti-pattern itself.

---

## 6. Exception machinery

Two paths, with pattern-mode strongly preferred by the UX.

### 6.1 Pattern mode (primary)

Template read from stdin:

```bash
codesmells ignore a3b2 <<EOF
try:
    ...
except $EXC_TYPE as $VAR:
    $LOG.warning(...)
    ...
EOF
```

Three gates (thresholds per §5.4):

| Gate | Check | Threshold |
|---|---|---|
| 1. faithful | template aligns to candidate's snippet | `score >= 0.7` |
| 2. generic | template contains at least one `$SIGIL` or `...` | structural |
| 3. distinct | template does NOT align to any `### Anti-Pattern` of this rule | `score < 0.9` for all |

On success: append under `### Safe` in `.codesmells/<rule-id>.smell.md`, `m.ok` confirmation. On failure: per-gate diagnostic via `m.fail`, no file mutation, agent reads and retries.

### 6.2 Per-site mode (fallback)

```bash
codesmells ignore a3b2 --here --reason="top-level supervisor"
```

`--reason` required — every per-site ignore self-documents. Comment syntax per file language (Python `#`, JS/TS/Go `//`). Comment applies to its own line and the next non-blank source line. Other scopes (block, file-level) deferred to v0.4+.

### 6.3 Rule-file evolution

The same rule file is the locus of three kinds of durable change:

1. Library refresh via `codesmells refresh <rule-id>` (manual, opt-in)
2. Project-specific `### Safe` patterns added by pattern-mode ignores
3. Direct hand-edits by the team

After enough `### Safe` patterns accumulate, the rule file documents the team's exception conventions. That's the learn-over-time loop.

---

## 7. Init flow

Non-interactive, fully agent-callable.

### 7.1 Preview (no writes)

```bash
$ codesmells init
detected: python (47 files), markdown (8 files)
loaded library: 7 rules matching detected languages

candidates (rules that actually fire):

catch-all-exception     python   broad except clauses                 3 hits
print-instead-of-log    python   print() in production code           12 hits
mutable-default-arg     python   def foo(x=[])                        1 hit
bare-return             python   return without value                 2 hits

next: codesmells init --select <ids>  |  codesmells init --all
```

### 7.2 Selection modes

```bash
codesmells init --all
codesmells init --select catch-all-exception,print-instead-of-log
codesmells init < picks.txt           # newline-separated rule IDs
```

Each writes `.codesmells/<rule-id>.smell.md` (overwriting if present, with a warning if existing local copy diverges from the library version).

### 7.3 Detection

Language detection is by file extension only at MVP (`*.py` → python, `*.ts` → typescript, etc.). Pre-filter probing means a rule must produce at least one pre-filter hit in the codebase to appear in the candidate list — keeps the suggestion tight and obviously relevant.

---

## 8. CI mode

`codesmells check` is the gate. Identical scan logic to `codesmells scan`; differs only in exit code:

- 0 if no findings
- 1 if any finding exists

Output is one summary line + one line per finding. No `next:` hint (CI consumes only rc + log). Designed for pre-commit hooks and CI workflows. Same rules, same exceptions (`### Safe` and per-site) honoured — codesmells is green ⟺ all current findings are either fixed or formally excepted.

---

## 9. Errors & edge cases

- **Malformed `.smell.md`** (bad YAML, missing required sections): skip with `m.warn("rule <id>: <reason>")` to stderr; scan continues with remaining rules. One bad rule never aborts a run.
- **Unparseable source file** (binary, weird encoding): file skipped silently.
- **Unknown finding id** (`inspect ZZZZ`): `m.fail("no finding with id ZZZZ — run 'codesmells scan' to refresh ids")`, rc≠0.
- **No `.codesmells/` directory**: `scan`/`check` print `m.fail("no rules — run 'codesmells init' to set up")`, rc≠0. `init` itself does not require it.
- **Per-site comment over a clean line**: `--here` validated at insert time — only operates on a line that currently contains a finding.
- **Three-gate failure**: each gate reports independently in the failure message; agent sees which specific gate failed and why.
- **`refresh` over a divergent local rule**: warn loudly with a diff summary, refuse to overwrite without `--force`.

---

## 10. Testing

| Test file | Status | Role |
|---|---|---|
| `tests/test_alignment.py` | keep | Algorithmic contract (17 tests, all green) |
| `tests/test_lexer.py` | keep | Lexer behaviour |
| `tests/test_cli.py` | drop | Tests the typer/session machinery being removed |
| `tests/test_milestone3.py` | drop | Same |
| `tests/test_storage.py` | drop | Storage layer being rewritten |
| `tests/test_scanner.py` | new | Windowed multi-fire, deterministic IDs, pre-filter chain, safe-pattern guard, ignore-comment harvest |
| `tests/test_rules.py` | new | `.smell.md` parsing (incl. `lang`/`severity`/`id`), library lookup, copy mechanics |
| `tests/test_cli_microcli.py` | new | Per-command exit codes and key output lines via subprocess + fixture codebase |
| `tests/fixtures/` | new | Synthetic codebases with known smell inventories; end-to-end `init`→`scan`→`ignore`→`scan` integration |

---

## 11. Out of scope for MVP

Deferred to v0.4+ once the core is proven:

- Multi-language rule library beyond Python (architecture is multi-language ready; rule curation effort is the bottleneck)
- Per-site ignore scopes beyond line + next-line (block-level, file-level)
- Library packaging as separate distributable rule packs
- `--reference` mode for `init` (rules live in library, not copied)
- Performance optimizations: rule caching, parallel file scanning, incremental rescans
- Severity-based CI gating (`--fail-on=error` style)
- Plugin hooks for custom matchers beyond Smith-Waterman

---

## 12. Migration notes

The existing repo holds:

- `lexer.py`, `alignment.py` — survive untouched
- `cli.py`, `storage.py`, `models.py` — replaced
- `repro_parser.py` — delete (dev debris)
- `examples/` — keep as integration fixtures, possibly move under `tests/fixtures/`
- `research/design.md`, `plans/project-roadmap.md` — historical, leave in place; this document is the new canonical design
- `TASKS.md`, `CHANGELOG.md` — update as part of implementation
- `pyproject.toml` version — current `0.1.0` (CHANGELOG mentions 0.2.0 but that release didn't fully run); next release is `0.3.0` reflecting the rebuild

The `.gemini/` scaffolding stays; it documents how Gemini-CLI agents interact with the repo and is orthogonal to the codesmells tool itself.
