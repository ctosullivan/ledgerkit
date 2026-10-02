<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
# Assertion: current-state-001

## Statement
The package's declared version in `pyproject.toml` is `1.0.0.dev1`, and `requires-python` is `>=3.8`, with zero runtime `dependencies` declared (an optional `pandas` extra exists under `[project.optional-dependencies]`).

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command: `cat /home/cormac/projects/ledgerkit/pyproject.toml`
Exact relevant lines:
```
[project]
name = "ledgerkit"
version = "1.0.0.dev1"
...
requires-python = ">=3.8"
dependencies = []
...
[project.optional-dependencies]
pandas = ["pandas>=1.3"]
```

Evidence-paths: [pyproject.toml]

## Justification
Directly read from the single source of truth for package metadata; no inference required.
## Examples
`version = "1.0.0.dev1"` and `dependencies = []` are the literal TOML key-value pairs in the file.
## Counterexamples
not applicable
## Depends on
none
## Open questions
none
## Evidence-support state
supported
## Status
verified
## Supersedes
