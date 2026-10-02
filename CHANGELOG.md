# Changelog

All notable changes to ledgerkit are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).
See [dev-docs/versioning.md](dev-docs/versioning.md) for the versioning policy.

---

## [Unreleased]

### CodeCompass upgrade + clean-room documentation reconstruction — plan amended — 2026-10-02

Full detail: [dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md](dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md)

**Human:** reviewed the plan below (same day, fresh session) and reported
8 concrete defects, plus resolutions for all 5 of the plan's own open
questions, directing an in-place amendment — explicitly still not to
implement Phase 1.

**Claude:** fixed all 8 in `29-codecompass-upgrade-and-clean-room-docs.md`
(same file, same six-phase structure, amended not replaced): moved every
existing-documentation comparison (including the `api-spec.md` coverage
check) out of Phase 3 and into Phase 5, closing a real clean-room-leakage
defect in the plan's own first draft (§4, §6.4); added a complete
9-document inventory/disposition table so Phase 4's drafted set matches
Phase 5's replaced set exactly (§5.1); separated reconstructable
current-shipped-state fact from forward-looking roadmap intent, the
latter excluded from evidence-checking entirely and reintroduced only
deliberately in Phase 5 (§4.1, §5.1, §6.1); added a small,
deterministic, stdlib-only `check_snapshot.py` that fails closed on five
named integrity conditions, gating Phase 4 (§3.7); corrected the
isolation success criterion so a disclosed `best-effort` tier is never
reported as "enforced" — split into three separately-reported Phase 6
checks instead (§3.4, §7.1); added explicit revision-pinning for both
`codecompass` and `codecompass-template` as Phase 1's first step,
recorded in a new `PINNED-REVISIONS.md` (§2.0); reclassified
`dev-docs/compat-register/*.yaml` as a derived evidence index rather than
primary evidence, requiring material compatibility claims to trace to
their underlying differential-test evidence or get a targeted re-check
(§3.2); and restricted `ledgerkit-editor` inspection to its source/tests,
excluding its own narrative docs. Resolved all 5 original open questions
(ROADMAP.md placement — a new "Tooling & Process Initiatives" section,
not a Stage letter; `knowledge/*.md` stays excluded until Phase 5;
`CLAUDE.md`'s stale folder-structure diagram gets fixed during Phase 1;
six-phase structure retained; `dev-docs/hledger-compatibility.md` is
reconciliation-first, not a blind redraft). Added a new §8
Part-A/Part-B split (the original questions vs. the review's 8 findings,
labelled F1–F8) after finding the two lists' shared 1–8 numbering had
caused several of this document's own cross-references to point at the
wrong item — a self-inflicted defect, caught and fixed by a dedicated
internal-consistency pass (new §12), not left for a future session to
discover. No `ledgerkit/`/`tests/` code touched; no implementation begun;
935 tests still pass (regression guard only).

---

### CodeCompass upgrade + clean-room documentation reconstruction — plan — 2026-10-02

Full detail: [dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md](dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md)

**Human:** directed planning a phase to (1) bring Ledgerkit's CodeCompass
integration current and (2) use the upgraded tooling for a genuine
clean-room reconstruction of the project's human-facing documentation,
with old documentation held out of the reconstruction and reintroduced
only afterward for comparison; explicitly not to implement yet.

**Claude:** investigated live, rather than trusting prior notes — found
CodeCompass's editable install already runs current code
(`context-graph.db`'s `schema_version` already matches the live
`_SCHEMA_VERSION` exactly; only a routine re-sync is needed, not a version
migration) and found CodeCompass's own upstream project independently
built almost exactly the requested methodology already (Phase 79's
clean-room pipeline, `decisions/0066`'s isolation findings, and a
portable, MIT-licensed `optional-clean-room-workflow/` template shipped to
`codecompass-template` — read-only clone, inspected this session).
Produced a six-phase plan (`29-codecompass-upgrade-and-clean-room-docs.md`)
that adopts that template directly rather than re-deriving it: Phase 1
reconciles Ledgerkit's four drifted local agent-brief copies against
upstream and imports two new roles (`implementation-reconstructor`,
`domain-skeptic`); Phase 2 adopts the template's isolation-preflight
discipline, honestly expecting a `best-effort`/`filesystem-only,
network-exposed` result (not `verified`) since Ledgerkit is itself a
public GitHub repository, same structural finding CodeCompass's own ADR
already confirmed for itself; Phase 3 builds evidence-cited, snapshot-
frozen assertions per module topic and independently reconstructs/
compares each; Phase 4 drafts replacement README/architecture/usage/
roadmap documentation from the snapshots alone; Phase 5 reintroduces old
documentation only now, classifies every claim (five-way scheme), and
replaces the live documents; Phase 6 runs an independent
`release-phase-auditor` Definition-of-Done audit against six explicit,
separately-reported validation criteria. Five open questions flagged for
explicit confirmation before Phase 1 starts (`§8`), including where this
sits in `ROADMAP.md` (recommended: its own section, not a Stage letter)
and the evidence/excluded boundary for `knowledge/*.md`. No `ledgerkit/`
or `tests/` code touched; no implementation begun.

---

### [Stage C — Query system] — 2026-09-27

Full detail: [dev-docs/changelog/STAGE-C.md](dev-docs/changelog/STAGE-C.md)

**Summary:** Built a complete, hledger-faithful query language across nine
phases: a standalone `ledgerkit/query/` AST/parser/evaluator subpackage
(Phase 1) wired into `balance`/`register`/`accounts`/`stats` (Phase 2) and
`print` (Phase 3) via `-q`/`--query`; a tag data model (Phase 4); `depth:`
redesigned as a report-display option, never a selection predicate (Phase
5); CodeCompass workflow adoption (Phase 5A, process-only); full
`tag:NAME[=REGEX]` effective-tag matching with the four-source union and
no-shadowing precedence rule (Phase 6); rejection of the empty regex
pattern, matching real hledger (Phase 7); convergence of the legacy
`ledgerkit.models.Query` dataclass onto the same canonical AST/evaluator
every other query path uses, eliminating a second, parallel matching path
(Phase 8); and rejection of empty-alternation-branch regex syntax (Phase
9). Every phase from Phase 6 onward followed a design → human-approval →
fresh-agent-implementation → independent-verification process, several
requiring one or more design-review correction passes before approval.
Zero open `unexplained_mismatch` compat-register entries remain. A
Stage-wide `docs-maintainer` reconciliation pass and two converging rounds
of independent `docs-reconstructor` drift audit, plus an independent
`release-phase-auditor` pass against Stage C's own Definition of Done
(PASS WITH NON-BLOCKING OBSERVATIONS, both closed out), preceded this
archiving. `PythonRegex` (a planned Python-regex escape hatch) was
explicitly resolved as deferred, not implemented or dropped; `cur:`,
hledger's smart/period date expressions, a standalone `--depth`/`-N` CLI
flag, and `check`'s intentional non-wiring from `-q` all remain confirmed,
documented, non-blocking deferrals. Stage C is `[DONE]`.

---

### Confirmed and pinned the hledger reference binary — 2026-09-13

**Human:** directed running a command to verify hledger availability and
pin it as the target version.

**Claude:** confirmed a real `hledger` executable exists at
`/home/cormac/.local/bin/hledger` (`1.52.4-g33fa849e7-20260910,
linux-aarch64`, sha256 `c212db5f25daddf82f5767011ae73d3b7329c244db617e010fafe481cd07d747`),
building from the exact same commit (`33fa849e7ae841968bd21c427094c4fb4a4ec38d`,
tag `1.52.4`) as the local hledger source clone `hledger-researcher`
already used for the Stage C Phase 1 semantics brief. Recorded the pin in
`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.1 and
corrected `dev-docs/compat-register/README.md`'s now-superseded "no
pinned binary" note. Recorded the decision in `knowledge/DECISIONS.md`.
This resolves a blocker noted repeatedly since Stage A closeout — it does
not itself run any differential verification, which remains separate,
not-yet-started work for `compat-differential-tester`.

---

### Added: standing commit/push pre-authorisation — 2026-09-13

**Human:** directed updating project instructions so commits happen at
logical intervals and pushes happen automatically at the end of each
successful phase, rather than asking each time.

**Claude:** added a "Commit & Push Cadence" section to `CLAUDE.md`:
commit at any coherent, self-contained, internally-consistent unit of
change; push once a phase is "successful" (exit criteria met, tests
passing, retro written) — same granularity `dev-docs/retros/` already
uses. Force-push, history rewrites, and branch deletion explicitly remain
outside this pre-authorisation. Updated `dev-docs/retros/README.md`'s
lifecycle diagram, `roadmap-context-curator.md` (commits/pushes as part of
its phase-end job), and `release-phase-auditor.md` (new DoD check #9:
committed and pushed). Recorded rationale in `knowledge/DECISIONS.md`.

---

### [Stage B — Core Model] — 2026-09-13

Full detail: [dev-docs/changelog/STAGE-B.md](dev-docs/changelog/STAGE-B.md)

**Summary:** Independently verified `ledgerkit-editor`'s actual `ledgerkit`
usage against its real source (Phase 1), correcting three inaccuracies in
an earlier README-inferred inventory — most notably, `EditorDocument` is
not actually used anywhere in its shipped code. Independently reviewed
whether `models.py` needs structural change to accommodate Stage E/F's
planned `Cost`/`Lot`/`PriceGraph`/valuation types (Phase 2): confirmed it
doesn't, except that account-type semantics must be added as a new field
rather than by retyping `Journal.declared_accounts`, which `ledgerkit-editor`
depends on. Both phases were read-only; no `ledgerkit/`/`tests/` code
changed. Stage B is `[DONE]`; Stage C (query system) is next.

---

### Added: per-phase retro report process — 2026-09-12

**Human:** asked whether ledgerkit had a retro convention similar to the
sibling `codecompass` project's, directed adopting one, then corrected the
initial scoping to fire per phase (matching the rest of the agent roster's
cadence) rather than only at Milestone/Stage completion.

**Claude:** added `dev-docs/retros/` (`README.md`, `TEMPLATE.md`), a new
"Retro Reports" section in `CLAUDE.md` (and the folder in its Folder
Structure block), and a step in `ROADMAP.md`'s "Deciding What Goes Into a
Milestone or Stage" process: a retro (`dev-docs/retros/<STAGE-OR-
MILESTONE>[-PHASE-K].md`) is authored at the end of every phase, the same
cadence `release-phase-auditor` and `docs-reconstructor` already use — not
only when a Milestone/Stage itself reaches `[DONE]`. Updated
`release-phase-auditor.md` to check a substantive per-phase retro exists as
part of its Definition-of-Done audit, and `roadmap-context-curator.md` to
author retros at phase-end and read them during its existing
learning-triage job. Recorded the decision and rationale in `knowledge/
DECISIONS.md`. Wrote `dev-docs/retros/STAGE-A.md` retroactively for the
already-`[DONE]` Stage A, since no retro existed for it yet. No
`ledgerkit/`/`tests/` code touched.

---

### [Stage A — Development Foundation] — 2026-09-12

Full detail: [dev-docs/changelog/STAGE-A.md](dev-docs/changelog/STAGE-A.md)

**Summary:** Relicensed ledgerkit from MIT to GPL-3.0-or-later to match
hledger's own licence (enabling directly-recorded use of hledger's
documentation, source, and test suite as compatibility evidence); redefined
the product goal from "a Python hledger clone" to "a deterministic,
Python-native accounting and query engine with a documented
hledger-compatible foundation"; migrated `ROADMAP.md` to the new Stage A–I
structure; built the seven-role agent roster (`.claude/agents/`); and built
the compatibility-register harness (`dev-docs/compat-register/`), including
25 first-wave entries covering directives, validation checks, and
genuinely-unsupported features, all `status: proposed` pending executable
verification. Stage A is `[DONE]`; Stage B (Core model) is next.

---

## [1.0.0] — 2026-06-07

First public release on PyPI.

---

### Added
- Parse `.journal` files compatible with hledger 1.52 format
- Core CLI commands: `balance`, `register`, `print`, `accounts`, `stats`, `check`
- Pure Python, no third-party runtime dependencies
- Python 3.8–3.12 support
- Comprehensive directive support: `include`, `account`, `commodity`, `payee`,
  `alias`, `P` (market prices), `Y` (default year), `D` (default commodity),
  `apply account` / `end apply account`
- Amount parsing: prefix/suffix commodity symbols, digit-group separators,
  decimal mark variants, quoted commodity names, E-notation, cost/lot
  annotations (`@ PRICE`, `{COST}`), sign-after-prefix-symbol (`$-300`)
- Secondary dates (`date2`) on transactions
- Full balance assertions (`=`, `==`, `=*`, `==*`) with `-I`/`--ignore-assertions` flag
- Strict mode (`-s`) checks that all accounts and commodities are declared
- Multi-commodity `balance()` with `tree=True` hierarchical rollup
- `parse_string_lenient` — never-raises parser for editor integrations
- `EditorDocument` — in-memory load/add/update/delete/save/reload for journal files
- `writer.py` — round-trip `transaction_to_text` and `journal_to_text`
- `SourceSpan` — byte-level source location for every transaction
- Commodity display style inference and `-c`/`--commodity-style` CLI flag
- Optional pandas export: `pip install ledgerkit[pandas]`
  - `Journal.to_dataframe()`, `BalanceResult.to_dataframe()`,
    `RegisterResult.to_dataframe()`, `AccountsResult.to_dataframe()`,
    `ReportSectionResult.to_dataframe()`
- `ReportSpec` / `ReportSection` / `balance_from_spec` for structured custom reports
- `ParseWarning` for non-fatal parser notices (periodic/auto-posting rule blocks)

---

## Pre-release development history

The entries below document the AI-assisted development workflow used to build
ledgerkit from the ground up across five milestones. They use a Human/Claude
attribution format and are preserved here for traceability. Detailed per-commit
records are in `dev-docs/changelog/`.

---

## [Unreleased]

---

### Publishing readiness for v0.2.0

**Human:** Prepare LedgerKit for its first PyPI release: packaging metadata, CI/CD workflows, documentation, and repository presentation. No parser or feature changes.

**Claude:** Updated `pyproject.toml` with `readme`, `license`, `keywords`, and `[project.urls]` fields; changed `description` to a clearer one-liner. Updated `README.md` Installation section with `pip install ledgerkit` primary command and development-install instructions; added CI badge. Created `.github/workflows/tests.yml` (matrix: Python 3.8–3.12, ubuntu-latest) and `.github/workflows/publish.yml` (OIDC Trusted Publishing; manual `workflow_dispatch` to Test PyPI; auto-publish to PyPI on `v*` tags). Created `dev-docs/pypi-trusted-publishing.md` with one-time setup instructions. Removed completed `pip install packaging & docs` backlog item from `ROADMAP.md`. Build verified: `python -m build` produces `ledgerkit-0.2.0-py3-none-any.whl` and `ledgerkit-0.2.0.tar.gz`; `twine check` passes both artifacts. 575 tests continue to pass.

---

## [0.2.0] — 2026-06-06

---

### [Milestone 4 — Comprehensive Format Compatibility]

Full detail: [dev-docs/changelog/MILESTONE-4.md](dev-docs/changelog/MILESTONE-4.md)

**Summary:** Added comprehensive hledger format compatibility. New model fields `Transaction.date2` (secondary date) and `Posting.cost_raw` (cost annotation text). New `ParseWarning` class for non-fatal parser notices. Amount parser now handles sign-after-prefix-symbol (`$-300`), cost/lot annotations (`@ $180`, `{$182}`), quoted commodity suffix (`3 "Chocolate Frogs"`), space digit-group separators (`1 000 000 JPY`), and E-notation (`1E3 EUR`). New directives: `Y` (default year), `D` (default commodity), `apply account`/`end apply account`. Periodic (`~`) and auto-posting (`=`) rule blocks skipped gracefully with `ParseWarning`. Zero hard errors on the comprehensive fixture; 575 tests pass.

---

## [0.1.0] — 2026-05-29

---

### Rename: PyLedger → ledgerkit

**Human:** Rename the project to `ledgerkit` for the PyPI release (`pyledger` was already taken).

**Claude:** Renamed source package directory `PyLedger/` → `ledgerkit/`. Updated all internal imports, `pyproject.toml` (name, scripts, packages.find), CLI prog name and error prefixes, all doc and knowledge files, and all test imports. 538 tests continue to pass.

---

### Python 3.8+ compatibility

**Human:** Lower the minimum Python requirement from 3.10 to 3.8.

**Claude:** Confirmed all source files already have `from __future__ import annotations` (PEP 563), making `str | None`/`list[str]` annotation syntax safe in Python 3.8. No code changes required. Updated `pyproject.toml` (`requires-python = ">=3.8"`, `target-version = ["py38"]`) and `README.md`.

---

### Commodity display style (`CommodityStyle`)

**Human:** Implement hledger commodity display style inference and CLI `-c` flag.

**Claude:** Created `ledgerkit/commodity_style.py` with `CommodityStyle` dataclass, `infer()` classmethod (detects prefix/suffix, spacing, decimal mark, group separator, precision from raw amount string), `format()` method (applies inferred style; prefix-symbol negatives as `£-5.00`, suffix-symbol negatives as `-5.00 EUR`), and `parse_style_override()` (parses `-c` CLI strings). Added `Amount.raw` field to models so the parser preserves the original amount text. Added `Journal._commodity_directive_raws` to capture style-declaring `commodity` directives. Added `Journal.commodity_styles` property that merges inferred and directive-based styles with directive priority. Updated `cli.py` to use styles in `balance`, `register`, and `print` output and accept `-c`/`--commodity-style` override flag. 29 new tests in `tests/test_commodity_style.py`.

---

### Pandas DataFrame export (optional)

**Human:** Add optional pandas export with `pip install ledgerkit[pandas]`.

**Claude:** Created `ledgerkit/_pandas_compat.py` (lazy import helper). Added `[project.optional-dependencies] pandas = ["pandas>=1.3"]` to `pyproject.toml`. Added `Journal.to_dataframe(query)` returning one row per posting. Added transparent result wrappers `BalanceResult`, `RegisterResult`, `AccountsResult` (with `__eq__` for existing-code compatibility) and `ReportSectionResult.to_dataframe()`. Updated `balance()`, `register()`, `accounts()` to return wrappers; updated `balance_from_spec()` to pass commodity styles. Exported new types from `ledgerkit/__init__.py`. 24 new tests in `tests/test_dataframe.py` (skipped gracefully if pandas absent).

---

### Version bump and classifiers

**Human:** Bump version to `0.1.0`, add PyPI classifiers.

**Claude:** Set `version = "0.1.0"` in `pyproject.toml` and `__version__` in `__init__.py`. Added `Topic :: Office/Business :: Financial :: Accounting` and Python 3.8–3.12 programming language classifiers. Added pandas ecosystem section to `README.md`.

---

## [Unreleased]

---

### Fix: column-0 `;`/`#` comment lines inside open transaction blocks

**Human:** Implement full hledger comment spec; column-0 `;` comments on their own line were not recognised correctly.

**Claude:** Identified that `_parse_string_impl` used `lstrip()` before the startswith check, making it unable to distinguish a column-0 top-level comment from an indented follow-on comment. Added `is_indented = line[0:1].isspace()` and gated comment capture on `if current_txn is not None and is_indented:`. Column-0 `#`/`;` lines are now always silently discarded (no capture, no `source_span` extension) regardless of whether a transaction block is open. Added `TestCommentSpec` with 25 new tests covering: standalone top-level comments (T-series), block comment edge cases (B-series), inline comment delimiters (I-series), follow-on indented comments (F-series), and source span behaviour (S-series). Updated `knowledge/DOMAIN_RULES.md`, `knowledge/EDGE_CASES.md` (EC-014), `dev-docs/hledger-compatibility.md` (corrected Comments table), and `docs/journal-format.md` (full Comments section rewrite). Total test count: 485.

---

### [Milestone 3 — Editor Readiness & Multi-Commodity] — 2026-05-09

Full detail: [dev-docs/changelog/MILESTONE-3.md](dev-docs/changelog/MILESTONE-3.md)

**Summary:** Added `parse_string_lenient` (never-raises parser for on-keystroke use), `CheckError.line_number`, multi-commodity `balance()` returning `dict[str, dict[str, Decimal]]` with `tree=True` mode, `resolve_elision()`, and `BalanceRow`. Added editor-readiness layer: `SourceSpan` dataclass, `Transaction.source_span/raw_text/inline_comment`, `Posting.inline_comment`, `source_file` param on `parse_string`, `check_transaction_autobalanced`, `writer.py` (`transaction_to_text`, `journal_to_text`), and `editor_model.py` (`EditorDocument`). 461 tests across nine test modules.

---

### [Milestone 2 — Core Reports] — 2026-05-03

Full detail: [dev-docs/changelog/MILESTONE-2.md](dev-docs/changelog/MILESTONE-2.md)

**Summary:** Implemented the `Query` filter dataclass, all four report functions (`balance`, `register`, `accounts`, `stats`), `ReportSpec`/`ReportSection`/`ReportSectionResult` foundation, hledger-aligned CLI output for `balance` and `register`, full balance assertions (`=`, `==`, `=*`, `==*`) with automatic enforcement and `-I` flag, a project knowledge base, and a trailing-decimal amount fix. 363 tests across seven test modules.

---

### [Milestone 1 — Journal Parser] — 2026-04-26

Full detail: [dev-docs/changelog/MILESTONE-1.md](dev-docs/changelog/MILESTONE-1.md)

**Summary:** Implemented the full journal parser (`parse_string`, `load_journal`, `include` directive, all key hledger directives), the checks module with strict mode, the `stats` report, all five CLI commands, and the complete test suite (265 tests across six subdirectory modules).

---

### [Milestone 0 — Project Foundation] — 2026-04-15

Full detail: [dev-docs/changelog/MILESTONE-0.md](dev-docs/changelog/MILESTONE-0.md)

**Summary:** Established the full project scaffold, core data models, initial
documentation suite, and developer tooling conventions that all subsequent
milestones build on.

---

## How to add a changelog entry (v1.0.0+)

Add a new entry under `## [Unreleased]` before cutting a release tag:

```markdown

---

## [X.Y.Z] — YYYY-MM-DD

---

### Added
- New features or capabilities

---

### Changed
- Changes to existing behaviour

---

### Fixed
- Bug fixes

---

### Removed
- Removed features (MAJOR version bump required)
```

Before tagging, move the entry out of `[Unreleased]` and set the release date.

---

## Archiving at milestone completion

When a major milestone is marked `[DONE]` in `ROADMAP.md`, all `[Unreleased]`
entries that belong to that milestone are archived as follows:

1. **Create an archive file** at `dev-docs/changelog/MILESTONE-N.md` (e.g.
   `dev-docs/changelog/MILESTONE-1.md`), using this structure:

```markdown
# Changelog — Milestone N: <Milestone Title>

Archived on: YYYY-MM-DD
GitHub commits: <hash> … <hash>

<paste all dev entries that belong to this milestone, oldest first>
```

2. **Replace** the individual dev entries in `CHANGELOG.md` with a single
   summary entry pointing to the archive:

```markdown

---

### [Milestone N — <Title>] — YYYY-MM-DD

Full detail: [dev-docs/changelog/MILESTONE-N.md](dev-docs/changelog/MILESTONE-N.md)

**Summary:** One or two sentences describing what the milestone delivered.
```

3. **Update `ROADMAP.md`** to mark the milestone `[DONE]` if not already done.

This keeps `CHANGELOG.md` scannable as the project grows while preserving the
full per-commit history in the archive files.
