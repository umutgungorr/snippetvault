# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-24

### Added
- Core SQLite WAL storage engine with auto-indexing and schema migration.
- Subcommand suite: `add`, `list`, `find`, `get`, `copy`, `run`, `delete`, `export`, `import`, `stats`.
- Word-level fuzzy similarity search powered by Python standard library `difflib`.
- Safe command execution with parameter confirmation (`--confirm`).
- Native clipboard integration for Windows (`clip`), macOS (`pbcopy`), and Linux (`wl-copy`/`xclip`).
- Clean ANSI formatting and structured `--json` output support for all reader commands.
- Comprehensive automated test suite with 100% core logic coverage.
