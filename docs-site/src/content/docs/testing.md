---
title: Testing
---

[← Development](development.md) · [← Contributing](contributing.md) · [README](../README.md)

# DLNA Receiver — Testing Guide

## Quick Start

```bash
uv run pytest tests/ -v
```

With coverage report:

```bash
uv run pytest tests/ -v --cov=provider/ --cov-report=term-missing
```

## CI Pipeline

`test.yml` runs the reusable `ma-provider-tools` test workflow on pull requests
and weekly. Pushes to `dev` run the same gate through `pipeline.yml` before any
release or fork sync.

| Check | What it does |
|-------|-------------|
| pytest | Runs the full suite against the installed Music Assistant package |
| ruff | Lint and format check |
| mypy | Strict type check of `provider/` and `tests/` |
| codespell / pre-commit | Repository hygiene and upstream rule gates |

There is no Codecov upload in this repository; coverage is reported in the job
log and can be generated locally as shown below.


## Tools

| Tool | Purpose |
|------|---------|
| `uv` | Virtual environment and dependency management |
| `Python 3.14` | Target Python version |
| `pytest` | Test framework |
| `pytest-cov` | Coverage collection |
| `ruff` | Python linter and formatter |
| `mypy` | Static type checker |
| `codespell` | Spell-checking for source code |
| `pre-commit` | Pre-commit hook runner |

## Running Linters Locally

Run all pre-commit hooks (recommended before opening a PR):

```bash
uv run pre-commit run --all-files
```

Type checking only:

```bash
uv run mypy provider/
```

Linting only:

```bash
uv run ruff check provider/
uv run ruff format --check provider/
```

## Coverage

Coverage is printed in the CI job log. To view it locally:

```bash
uv run pytest tests/ --cov=provider/ --cov-report=html
open htmlcov/index.html
```

## When CI Fails

When tests or linters fail in CI, a GitHub issue is automatically created with the `incident:ci` label.
See [Incident Management](incident-management.md) for how the incident workflow operates.
