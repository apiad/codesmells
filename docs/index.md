# CodeSmells: Agentic Architectural Refactoring

**CodeSmells** is a modern, agentic tool designed to detect and suggest refactorings for architectural anti-patterns in Python codebases. Unlike traditional linters that rely on rigid Abstract Syntax Trees (ASTs), CodeSmells uses **probabilistic lexing** and **fuzzy alignment** to identify problematic code structures even when they don't perfectly match a template.

## Core Concepts

- **Fuzzy Alignment:** Uses the Smith-Waterman algorithm with affine gap penalties to find the best local alignment between your code and a rule template.
- **Probabilistic Lexing:** A weighted tokenization approach that prioritizes keywords and sigils over generic identifiers, allowing for flexible matching.
- **Agentic Workflow:** Designed to be used by both humans and AI agents (like Gemini or Claude) to interactively scan, inspect, and refactor code.

## Quick Start

1. **Initialize:** Set up the `.codesmells/` environment in your project.
   ```bash
   codesmells init
   ```

2. **Add a Rule:** Create a new rule template from a boilerplate.
   ```bash
   codesmells add "Catch All Exception" "Avoid bare except: blocks."
   ```

3. **Scan:** Look for architectural smells in your codebase.
   ```bash
   codesmells scan .
   ```

4. **Refactor:** Inspect detected candidates and generate suggestions.
   ```bash
   codesmells inspect <id>
   codesmells suggest <id>
   ```

## Next Steps

- Learn how to [Install and Deploy](deploy.md) CodeSmells.
- Understand the [Internal Design](design.md) and algorithms.
- Master [Writing Custom Rules](rules.md) for your project.
- Check the [Contributor's Guide](develop.md) to help improve the tool.
