# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ghprj` is a GitHub repository metadata extraction and transformation utility. It fetches repo info via the GitHub CLI (`gh`), parses JSON output, and converts it to various formats (TSV, dict). Written in Python with Japanese docstrings/comments.

## Build & Development Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Build distribution
uv build

# Run the CLI
uv run ghprj

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Lint
uv run ruff check src/

# Format
uv run black src/

# Type check (strict mode)
uv run mypy src/
```

## Architecture

The project is a single-module utility library at `src/ghprj/main.py` with functional design (no classes). The package entry point re-exports `main` from `__init__.py`.

**Core functions in `main.py`:**
- `run_command` / `run_command_simple` — Execute CLI commands (e.g., `gh repo list`) and capture output
- `load_json_array` / `save_as_json` / `save_file` — File I/O with validation
- `array_to_dict` — Convert list-of-dicts to dict-of-dicts keyed by a specified field
- `array_to_tsv` — Convert list-of-dicts to TSV format, serializing nested structures as JSON

**`main()` entry point flow:** loads `repos.json` → converts to TSV with predefined headers → saves `repos.tsv` → prints parsed data.

## Code Style & Tooling

- **Python target:** 3.14 (`.python-version` specifies 3.14.0)
- **Formatter:** Black, line length 88
- **Linter:** Ruff with rules E, F, I, N (E501 ignored — delegated to Black)
- **Type checker:** MyPy in strict mode
- **Build backend:** `uv_build`
- **Docstrings/comments:** Written in Japanese
