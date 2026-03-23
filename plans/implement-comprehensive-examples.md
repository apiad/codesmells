# Implementation Plan: Comprehensive Multi-Language Example Knowledge Base

This plan outlines the steps to populate the `examples/` directory with high-quality, validated code smells across 10 mainstream languages.

## 1. Project Overview
Expand the `examples/` knowledge base to provide a "batteries-included" experience for CodeSmells users. We will implement 5 smells per language, covering Security, SOLID, and Language-specific categories.

## 2. Phased Rollout

### Phase 1: Dynamic & Scripting (High Immediate Value)
- **Languages:** Python, JavaScript, TypeScript
- **Target Smells (Python):** Broad Exception, Mutable Default, Non-idiomatic loops, Hardcoded API Key (Security), God Object (SOLID).
- **Target Smells (JS/TS):** Callback Hell, 'Any'-script, Var Usage, Unescaped innerHTML (Security), Tight Coupling (SOLID).

### Phase 2: System & Compiled (Core Performance)
- **Languages:** C, C++, Rust, Go
- **Target Smells (C/C++):** Unsafe Pointer Arithmetic, Manual Memory (No RAII), Lack of Const, Buffer Overflow (Security), Interface Segregation violation (SOLID).
- **Target Smells (Rust/Go):** Unnecessary Unwrap (Rust), Interface{} Abuse (Go), Ignoring Errors (Go), Large Unsafe Blocks (Rust), Single Responsibility violation (SOLID).

### Phase 3: Enterprise & Web (Ecosystem Coverage)
- **Languages:** Java, C#, HTML, CSS
- **Target Smells (Java/C#):** Deep Inheritance, Empty Catch, God Object, SQL Injection (Security), Dependency Inversion violation (SOLID).
- **Target Smells (HTML/CSS):** Div Soup, !important Overuse, Magic Numbers, XSS in HTML (Security), Open/Closed violation in CSS (SOLID).

## 3. Implementation Checklist per Smell
For each smell `examples/<lang>/<smell-name>/`:
- [ ] Create `<smell-name>.bad.<ext>` (Demonstration of the smell).
- [ ] Create `<smell-name>.good.<ext>` (Refactored/Safe version).
- [ ] Author `<smell-name>.smell.md` (CodeSmells rule template with front-matter).
- [ ] Author `<smell-name>.smell.test.md` (.smell.test.md validation suite).
- [ ] Run `codesmells validate` and ensure it passes.

## 4. Standard Library Strategy
- After implementation, create a `Standard Library` manifest that allows users to easily import these rules.
- Update the `install-skill` command if necessary to point to this new library.

## 5. Verification & Finalization
- [ ] All 50 smells (10 langs x 5 smells) pass `codesmells validate`.
- [ ] `examples/` directory structure is consistent.
- [ ] Documentation updated to point to the new examples.
