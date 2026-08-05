# Rewrite-Safe Provider Imports Design

## Problem

The upstream sync rewrites provider-local test imports into the inlined Music
Assistant package path. Two tests currently use this form:

```python
from provider import provider as provider_module
```

The canonical rewrite first expands `from provider import`, then matches the
remaining `import provider as` fragment again. The generated upstream test is
invalid Python, so both linting and pytest collection fail in
`music-assistant/server` PR 3611.

## Design

Use the supported aliased dotted-import form in both affected tests:

```python
import provider.provider as provider_module
```

The canonical transform rewrites this once to:

```python
import music_assistant.providers.dlna_receiver.provider as provider_module
```

The alias and monkeypatch behavior remain unchanged. Production provider code
and the shared `ma-provider-tools` transformer stay out of scope.

## Release Metadata

Add a `1.2.6` changelog entry under `Fixed` describing the repaired upstream
test synchronization, and update `VERSION` from `1.2.5` to `1.2.6`. The patch
release is required so the provider pipeline republishes and resynchronizes the
corrected tests to the integration and upstream branches.

## Verification

The regression check runs the real canonical forward transform from
`ma-provider-tools` against `tests/test_provider.py` and parses the generated
Python with `ast.parse`. Before the fix it must reproduce the SyntaxError; after
the fix it must parse and contain both expected inlined imports. The provider's
full pytest suite and pre-commit suite must also pass.

## Scope and Risk

Only two test imports and release metadata change. Runtime behavior is
unaffected. The main residual risk is drift in the external transform after
this release. Improving the shared rewrite-safety guard belongs in
`ma-provider-tools` and is intentionally outside this provider-only fix.
