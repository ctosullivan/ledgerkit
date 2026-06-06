# Changelog

All notable changes to ledgerkit are recorded here.

Each entry corresponds to one GitHub commit. The **Human** line summarises what
the user directed or decided; the **Claude** line summarises what Claude
researched, designed, or implemented.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

---

## [0.2.0] — 2026-06-06

### [Milestone 4 — Comprehensive Format Compatibility]

Full detail: [dev-docs/changelog/MILESTONE-4.md](dev-docs/changelog/MILESTONE-4.md)

**Summary:** Added comprehensive hledger format compatibility. New model fields `Transaction.date2` (secondary date) and `Posting.cost_raw` (cost annotation text). New `ParseWarning` class for non-fatal parser notices. Amount parser now handles sign-after-prefix-symbol (`$-300`), cost/lot annotations (`@ $180`, `{$182}`), quoted commodity suffix (`3 "Chocolate Frogs"`), space digit-group separators (`1 000 000 JPY`), and E-notation (`1E3 EUR`). New directives: `Y` (default year), `D` (default commodity), `apply account`/`end apply account`. Periodic (`~`) and auto-posting (`=`) rule blocks skipped gracefully with `ParseWarning`. Zero hard errors on the comprehensive fixture; 575 tests pass.

---

## [0.1.0] — 2026-05-29

### Rename: PyLedger → ledgerkit

**Human:** Rename the project to `ledgerkit` for the PyPI release (`pyledger` was already taken).

**Claude:** Renamed source package directory `PyLedger/` → `ledgerkit/`. Updated all internal imports, `pyproject.toml` (name, scripts, packages.find), CLI prog name and error prefixes, all doc and knowledge files, and all test imports. 538 tests continue to pass.

### Python 3.8+ compatibility

**Human:** Lower the minimum Python requirement from 3.10 to 3.8.

**Claude:** Confirmed all source files already have `from __future__ import annotations` (PEP 563), making `str | None`/`list[str]` annotation syntax safe in Python 3.8. No code changes required. Updated `pyproject.toml` (`requires-python = ">=3.8"`, `target-version = ["py38"]`) and `README.md`.

### Commodity display style (`CommodityStyle`)

**Human:** Implement hledger commodity display style inference and CLI `-c` flag.

**Claude:** Created `ledgerkit/commodity_style.py` with `CommodityStyle` dataclass, `infer()` classmethod (detects prefix/suffix, spacing, decimal mark, group separator, precision from raw amount string), `format()` method (applies inferred style; prefix-symbol negatives as `£-5.00`, suffix-symbol negatives as `-5.00 EUR`), and `parse_style_override()` (parses `-c` CLI strings). Added `Amount.raw` field to models so the parser preserves the original amount text. Added `Journal._commodity_directive_raws` to capture style-declaring `commodity` directives. Added `Journal.commodity_styles` property that merges inferred and directive-based styles with directive priority. Updated `cli.py` to use styles in `balance`, `register`, and `print` output and accept `-c`/`--commodity-style` override flag. 29 new tests in `tests/test_commodity_style.py`.

### Pandas DataFrame export (optional)

**Human:** Add optional pandas export with `pip install ledgerkit[pandas]`.

**Claude:** Created `ledgerkit/_pandas_compat.py` (lazy import helper). Added `[project.optional-dependencies] pandas = ["pandas>=1.3"]` to `pyproject.toml`. Added `Journal.to_dataframe(query)` returning one row per posting. Added transparent result wrappers `BalanceResult`, `RegisterResult`, `AccountsResult` (with `__eq__` for existing-code compatibility) and `ReportSectionResult.to_dataframe()`. Updated `balance()`, `register()`, `accounts()` to return wrappers; updated `balance_from_spec()` to pass commodity styles. Exported new types from `ledgerkit/__init__.py`. 24 new tests in `tests/test_dataframe.py` (skipped gracefully if pandas absent).

### Version bump and classifiers

**Human:** Bump version to `0.1.0`, add PyPI classifiers.

**Claude:** Set `version = "0.1.0"` in `pyproject.toml` and `__version__` in `__init__.py`. Added `Topic :: Office/Business :: Financial :: Accounting` and Python 3.8–3.12 programming language classifiers. Added pandas ecosystem section to `README.md`.

---

## [Unreleased]

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

## How to add a changelog entry

When work is ready to commit, add a new entry at the top of the `[Unreleased]`
section following this template:

```markdown
### [0.x.y-dev.N] — Short title

**What changed:**
- Bullet list of files/modules affected and what changed in each

**Human:** One or two sentences on what the user directed, decided, or specified.

**Claude:** One or two sentences on what Claude researched, designed, or implemented.
```

Once the GitHub commit is made, move the entry out of `[Unreleased]` and
replace the dev tag with the actual commit hash or release version:

```markdown
## [abc1234] — 2026-04-14 — Short title
```

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
### [Milestone N — <Title>] — YYYY-MM-DD

Full detail: [dev-docs/changelog/MILESTONE-N.md](dev-docs/changelog/MILESTONE-N.md)

**Summary:** One or two sentences describing what the milestone delivered.
```

3. **Update `ROADMAP.md`** to mark the milestone `[DONE]` if not already done.

This keeps `CHANGELOG.md` scannable as the project grows while preserving the
full per-commit history in the archive files.
