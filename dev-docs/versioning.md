# Versioning Policy

ledgerkit follows [Semantic Versioning 2.0.0](https://semver.org/).

## Version format

`MAJOR.MINOR.PATCH`

| Component | When to increment |
|-----------|------------------|
| `MAJOR`   | Breaking change to the public Python API or CLI interface |
| `MINOR`   | New feature, new directive support, or new report capability, backwards-compatible |
| `PATCH`   | Bug fix, documentation correction, or internal refactor with no API change |

## What counts as a breaking change

- Removing or renaming a public function, class, or attribute exported from `ledgerkit.__init__`
- Changing the return type or field names of a public dataclass
- Removing a CLI command or flag
- Changing how an existing CLI command formats its output in a way that breaks scripted consumers

## What does not count as a breaking change

- Adding a new optional keyword argument to an existing public function
- Adding a new field to a dataclass (existing code that doesn't reference it is unaffected)
- Adding a new CLI command or flag
- Adding support for additional hledger journal syntax that previously raised `ParseError`
- Internal refactors not visible through the public API

## Version string locations

The version is defined in exactly two places and must be kept in sync:

1. `pyproject.toml` — `version` field under `[project]`
2. `ledgerkit/__init__.py` — `__version__` string

The CI publish workflow tags the release commit (`v1.0.0`). The tag is the
single source of truth for what is live on PyPI.

## Changelog discipline

Every release must have a corresponding entry in `CHANGELOG.md` added before
the version tag is pushed. See `CHANGELOG.md` for the entry format.

## Pre-1.0.0 history

Development from v0.0.0 to v0.2.0 (Milestones 0–4) is archived in
`dev-docs/changelog/`. These entries use a Human/Claude attribution format
that documents the AI-assisted development workflow; they are not the ongoing
changelog format.

## Licence

Every release through `1.0.0` (and the `1.0.0.dev1` pre-release) was
published under the MIT License and remains so — relicensing is not
retroactive to bytes already shipped. Starting with the first release after
2026-09-12, ledgerkit is licensed under GPL-3.0-or-later. See
`dev-docs/planning/core-redefinition/02-licence-migration.md` for the full
rationale. A licence change is not itself classified as a breaking change
under this document's MAJOR/MINOR/PATCH rules (those cover the API/CLI
surface only), but it should be called out prominently in `CHANGELOG.md`
regardless, since it materially affects how downstream consumers may use
the package.
