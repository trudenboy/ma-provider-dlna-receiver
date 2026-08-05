# Rewrite-Safe Provider Imports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the provider tests survive the canonical upstream import-path rewrite and release the correction as version 1.2.6.

**Architecture:** Replace the two overlapping `from provider import provider` statements with the supported aliased dotted-import form. Keep runtime code unchanged, then verify the synced test source by executing the real `ma-provider-tools` transform and parsing its output before publishing patch-release metadata.

**Tech Stack:** Python 3.12+, pytest, Ruff, mypy, pre-commit, `ma-provider-tools/scripts/_transform.py`.

## Global Constraints

- Work only in `trudenboy/ma-provider-dlna-receiver`; do not edit `music-assistant/server` or `trudenboy/ma-server` directly.
- Keep production provider behavior unchanged.
- Use version `1.2.6` and changelog date `2026-08-05`.
- Preserve both tests' `provider_module` alias and monkeypatch behavior.
- Validate the generated upstream source with the canonical transform, not a locally reimplemented rewrite.

---

### Task 1: Make provider-module imports rewrite-safe

**Files:**
- Modify: `tests/test_provider.py:199`
- Modify: `tests/test_provider.py:248`
- Test: canonical transformed output of `tests/test_provider.py`

**Interfaces:**
- Consumes: `ma-provider-tools/scripts/_transform.py forward-test-content dlna_receiver`.
- Produces: two valid imports of `music_assistant.providers.dlna_receiver.provider as provider_module` in the transformed test source.

- [ ] **Step 1: Run the regression check against the current source**

```bash
python3 - <<'PY'
import ast
import subprocess
from pathlib import Path

source = Path("tests/test_provider.py").read_text(encoding="utf-8")
result = subprocess.run(
    [
        "python3",
        "/mnt/data/Projects/mass/ma-provider-tools/scripts/_transform.py",
        "forward-test-content",
        "dlna_receiver",
    ],
    input=source,
    text=True,
    capture_output=True,
    check=True,
)
try:
    ast.parse(result.stdout)
except SyntaxError as err:
    raise AssertionError(f"rewritten tests are invalid: {err}") from err
expected = (
    "import music_assistant.providers.dlna_receiver.provider "
    "as provider_module  # noqa: PLC0415"
)
assert result.stdout.count(expected) == 2
PY
```

Expected: FAIL with `AssertionError: rewritten tests are invalid` caused by the generated import on line 199.

- [ ] **Step 2: Apply the minimal import change**

Replace both occurrences of:

```python
from provider import provider as provider_module  # noqa: PLC0415
```

with:

```python
import provider.provider as provider_module  # noqa: PLC0415
```

- [ ] **Step 3: Run the regression check again**

```bash
python3 - <<'PY'
import ast
import subprocess
from pathlib import Path

source = Path("tests/test_provider.py").read_text(encoding="utf-8")
result = subprocess.run(
    [
        "python3",
        "/mnt/data/Projects/mass/ma-provider-tools/scripts/_transform.py",
        "forward-test-content",
        "dlna_receiver",
    ],
    input=source,
    text=True,
    capture_output=True,
    check=True,
)
ast.parse(result.stdout)
expected = (
    "import music_assistant.providers.dlna_receiver.provider "
    "as provider_module  # noqa: PLC0415"
)
assert result.stdout.count(expected) == 2
PY
```

Expected: exit code 0; the transformed source parses and contains exactly two expected imports.

- [ ] **Step 4: Run the two affected behavioral tests**

```bash
pytest -q \
  tests/test_provider.py::test_loaded_publishes_registry_instances_while_start_is_in_progress \
  tests/test_provider.py::test_loaded_reports_registry_start_failure_and_returns
```

Expected: `2 passed`.

- [ ] **Step 5: Commit the rewrite-safe imports**

```bash
git add tests/test_provider.py
git commit -m "test: make provider module imports rewrite-safe"
```

### Task 2: Publish patch-release metadata

**Files:**
- Modify: `CHANGELOG.md:3`
- Modify: `VERSION:1`

**Interfaces:**
- Consumes: current version `1.2.5` and the repository's Keep a Changelog format.
- Produces: version `1.2.6` with one canonical `Fixed` entry.

- [ ] **Step 1: Add the changelog entry**

Insert above `1.2.5`:

```markdown
## [1.2.6] - 2026-08-05

### Fixed

- Provider tests now retain valid module imports when synchronized into the Music Assistant server repository.
```

- [ ] **Step 2: Update the version file**

Replace the complete contents of `VERSION` with:

```text
1.2.6
```

- [ ] **Step 3: Verify release metadata exactly**

```bash
test "$(tr -d '\r\n' < VERSION)" = "1.2.6"
python3 - <<'PY'
from pathlib import Path

text = Path("CHANGELOG.md").read_text(encoding="utf-8")
assert text.count("## [1.2.6] - 2026-08-05") == 1
assert text.index("## [1.2.6]") < text.index("## [1.2.5]")
PY
```

Expected: exit code 0.

- [ ] **Step 4: Commit release metadata**

```bash
git add CHANGELOG.md VERSION
git commit -m "release: bump version to 1.2.6"
```

### Task 3: Run the complete verification gate

**Files:**
- Verify: `tests/test_provider.py`
- Verify: `CHANGELOG.md`
- Verify: `VERSION`

**Interfaces:**
- Consumes: the completed Task 1 and Task 2 commits.
- Produces: evidence that local tests, style/type gates, and transformed upstream syntax all pass.

- [ ] **Step 1: Run the full provider test suite**

```bash
pytest -q
```

Expected: 139 tests pass with zero failures.

- [ ] **Step 2: Run all pre-commit hooks**

```bash
pre-commit run --all-files
```

Expected: every applicable hook passes, including Ruff and mypy.

- [ ] **Step 3: Re-run the canonical transform regression check**

```bash
python3 - <<'PY'
import ast
import subprocess
from pathlib import Path

source = Path("tests/test_provider.py").read_text(encoding="utf-8")
result = subprocess.run(
    [
        "python3",
        "/mnt/data/Projects/mass/ma-provider-tools/scripts/_transform.py",
        "forward-test-content",
        "dlna_receiver",
    ],
    input=source,
    text=True,
    capture_output=True,
    check=True,
)
ast.parse(result.stdout)
expected = (
    "import music_assistant.providers.dlna_receiver.provider "
    "as provider_module  # noqa: PLC0415"
)
assert result.stdout.count(expected) == 2
PY
```

Expected: exit code 0 and exactly two valid inlined imports.

- [ ] **Step 4: Review the final branch scope**

```bash
git status -sb
git diff --check dev...HEAD
git diff --stat dev...HEAD
git log --oneline --decorate dev..HEAD
```

Expected: a clean worktree; changes limited to the two design/plan documents, `tests/test_provider.py`, `CHANGELOG.md`, and `VERSION`.
