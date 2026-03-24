# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-23

### Added
- Comprehensive code smell knowledge base with 35+ rules for 8+ languages (Python, JavaScript, TypeScript, C/C++, Go, Rust, Java, C#).
- Descriptive documentation inside rule markdown files explaining anti-patterns and safe examples.
- Greedy matching for ellipsis (`...`) GAP tokens in the alignment engine for more flexible pattern detection.
- Auto-tuned `tau` (threshold) in the CLI to automatically calibrate rules based on their test cases.
- Recursive rule loading to support organized project-specific rule directories.
- `list` command to the CLI for easy discovery of active rules.
- Support for multi-character operators and refined tokenization in the lexer.

### Fixed
- Extraneous f-string usage in CLI output.
- Improved lexer precision for operator tokens.

## [0.2.0] - 2026-03-23

### Added
- Rule Validation suite with test-driven development for anti-pattern detection.
- Rule Test loading and execution in `StorageManager`.
- `install-skill` command to bootstrap AI agent capabilities in projects.
- New `RuleTest` and `TestPattern` models for enhanced verification.
- Comprehensive documentation: `design.md`, `develop.md`, `deploy.md`, `index.md`, and `rules.md`.
- SKILL.md template for AI agents (Gemini CLI, Claude Code).

### Fixed
- Code cleanup and linting across the codebase.
- Improved CLI experience with better help panels and guidance.

## [0.1.0] - 2026-03-23

### Added
- Initial project setup with Gemini CLI framework.
- Project design specification (`research/design.md`).
- Core architectural modules: `models`, `lexer`, `alignment`, `storage`, and `cli`.
- Comprehensive project roadmap (`plans/project-roadmap.md`).
- Integrated testing with `pytest` and linting with `ruff`.
- Automated builds and checks via `makefile`.
- Modern Python management with `uv`.

[0.3.0]: https://github.com/apiad/codesmells/releases/tag/v0.3.0
[0.2.0]: https://github.com/apiad/codesmells/releases/tag/v0.2.0
[0.1.0]: https://github.com/apiad/codesmells/releases/tag/v0.1.0
