# Contributing

Thank you for your interest in contributing.

This document provides a quick overview. For full development details, see:

* `docs/development.md`

## Development setup

Quick start:

```bash
python -m tools.devtools bootstrap dev
```

Activate the virtual environment:

* Linux/macOS:

  ```bash
  source .venv/bin/activate
  ```

* Windows (PowerShell):

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

Optional dependencies (e.g. Qt widget support):

```bash
python -m tools.devtools install qt-widget
```

## Code standards

* Python 3.11+
* Strict type checking (Pyright)
* Linting: Ruff
* Code must follow the project’s formatting and lint configuration

## Pre-commit

All commits **must pass pre-commit checks**.

Run manually:

```bash
python -m tools.devtools run pre-commit
```

Notes:

* Pre-commit hooks are installed automatically during bootstrap
* Commits will be rejected if checks fail
* Fix all reported issues before committing

## Tests

Run all tests:

```bash
python -m tools.devtools test all
```

Run specific scopes:

```bash
python -m tools.devtools test engine-all
python -m tools.devtools test qt-widget-all
```

Requirements:

* All changes must include relevant tests
* Existing tests must pass
* CI must be green before merging

For deeper testing guidelines, see:

* `docs/development.md`

## Commits

Commits **must** follow the Conventional Commits specification.

Examples:

* `feat: add board animation support`
* `fix: correct move validation bug`
* `refactor: simplify controller state handling`
* `docs: update API usage examples`

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

## Pull requests

* Keep PRs focused and minimal
* Ensure all CI checks are passing
* All commits must pass pre-commit checks
* Include tests for all behavior changes
* Update documentation when relevant
* Large or breaking changes must be discussed in an issue first

## Questions and discussions

Open an issue for:

* Design discussions
* Feature proposals
* Clarifications before large changes

## Summary

* Use `tools.devtools` for all workflows
* Follow strict typing and lint rules
* All commits must pass pre-commit checks
* Write tests for all changes
* Use Conventional Commits
* Refer to `docs/development.md` for full details
