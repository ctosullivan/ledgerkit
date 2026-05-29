# Changelog — Milestone 1: Journal Parser

Archived on: 2026-04-26
GitHub commits: 0.1.0-dev.1 … 0.1.0-dev.10 · 11c35f8 · 17207ce · a2d68b3 · 860f6b8 · 4f3382a · ff8c115 · c5eb960 · 92af4d7 (and subsequent refactor / type-fix commits)


### [a2d68b3] — 2026-04-17 — Structural updates: docs split, packaging, module API, roadmap

**What changed:**
- `docs/` renamed → `dev-docs/` (git mv; all cross-references updated)
- `dev-docs/SYNC.md` — stale `hledger/` refs fixed to `ledgerkit/`; human-docs
  sync rule added
- `dev-docs/api-spec.md` — all `ledgerkit/` refs → `ledgerkit/`; `Journal` report
  methods, `load()`, `PriceDirective`, and `python -m ledgerkit` usage added
- `dev-docs/hledger-compatibility.md` — P directive and alias directive moved
  from Undecided/Out of Scope → **In Scope (v1)**; Directives table added
- `CLAUDE.md` — all `docs/` refs → `dev-docs/`; folder diagram corrected
  (`ledgerkit/` → `ledgerkit/`, `MANIFEST.in` and `__main__.py` added, `docs/`
  human section added); SYNC table updated; milestone archive path updated
- `README.md` — CLI command updated to `ledgerkit`; Python library example added;
  docs table added; Contributing section with sparse-checkout command added
- `ROADMAP.md` — all `docs/` refs → `dev-docs/`; Milestone 1 scope extended with
  P directive, alias directive, and module-level API; `ledgerkit.cli` → `ledgerkit`;
  Commodity price directives removed from backlog (now in Milestone 1)
- `pyproject.toml` — script entry `ledgerkit = "ledgerkit.cli:main"` →
  `ledgerkit = "ledgerkit.cli:main"`; `include = ["ledgerkit*"]` → `["ledgerkit*"]`
- `MANIFEST.in` — new file; excludes `CLAUDE.md`, `CHANGELOG.md`, `ROADMAP.md`,
  `dev-docs/` from sdist
- `ledgerkit/models.py` — `PriceDirective` dataclass added; `Journal.prices` field
  added; four report methods added to `Journal` (lazy-import delegation to reports)
- `ledgerkit/__init__.py` — `load()` convenience function exported
- `ledgerkit/__main__.py` — new file; enables `python -m ledgerkit`
- `ledgerkit/cli.py` — `prog="ledgerkit"` → `prog="ledgerkit"`
- `docs/` — new human-facing documentation folder created with four guides:
  `getting-started.md`, `usage.md`, `journal-format.md`, `python-api.md`

**Human:** Directed the structural refactor: rename `docs/` to `dev-docs/`,
create a human `docs/` folder, add sparse-checkout clone command, fix packaging
capitalisation, add `load()` + `__main__` + Journal report methods, extend
Milestone 1 to include P directive and alias directive.

**Claude:** Executed the full plan across 18 files: git mv for the folder rename,
updated all cross-references, created `MANIFEST.in`, added `PriceDirective` and
Journal methods with lazy-import pattern, created `__main__.py`, and authored all
four human guide files.

---

### [17207ce] — 2026-04-15 — Fix: normalise internal imports to ledgerkit (capital P)

**What changed:**
- `ledgerkit/parser.py` — `from ledgerkit.models import` → `from ledgerkit.models import`
- `ledgerkit/reports.py` — `from ledgerkit.models import` → `from ledgerkit.models import`
- `ledgerkit/cli.py` — all three `ledgerkit` references updated to `ledgerkit`
- `ledgerkit/parser.py` — posting-outside-block guard restored: indented lines
  outside a transaction block still raise `ParseError`; non-indented lines outside
  a block are silently skipped

**Human:** Directed that all internal imports be normalised to `ledgerkit`
(capital P) to match the package directory name and resolve the
`ModuleNotFoundError` that prevented the test suite from running.

**Claude:** Updated all cross-module imports in the three affected files, ran the
suite (36 tests), diagnosed one regression in `test_posting_outside_block_raises`
caused by the indentation relaxation, restored the guard for indented lines
outside a block, and confirmed 36/36 pass.

---

### [0.1.0-dev.10] — Fix: relax posting-line indentation requirement

**What changed:**
- `ledgerkit/parser.py` — state machine restructured: transaction-header and
  directive checks now run before posting detection; posting branch changed from
  `line.startswith("  ") or line.startswith("\t")` to `current_txn is not None`,
  making indentation conventional rather than mandatory; `parse_string` docstring
  updated to document the relaxed rule; posting-branch inline comment updated
- `docs/hledger-compatibility.md` — first delimiter rule updated (user-applied):
  posting indentation noted as conventional, not required

**Human:** Identified that the strict 2+ space / tab gate in `parse_string`
contradicted the updated compatibility doc stating indentation is not a
requirement; directed the parser to be updated to match.

**Claude:** Restructured the state-machine branch order so that transaction-header
and directive checks run first, then any unmatched line inside an open block is
treated as a posting regardless of indentation.

---

### [0.1.0-dev.1] — Feature: journal parser + tests

**What changed:**
- `ledgerkit/parser.py` — `parse_string` and `parse_file` implemented;
  private helpers `_parse_txn_header`, `_parse_amount`, `_parse_posting` added
- `tests/test_parser.py` — created with 18 assertions across 10 test classes
  (happy paths: date/description/flag/code/comment/commodity/thousands;
  error paths: posting outside block, two elided amounts)

**Human:** Specified the required test cases, the at-most-one-elided-amount
rule, and the decision to accept unbalanced transactions silently in the parser
(deferred to reports layer).

**Claude:** Designed the line-by-line state machine, wrote the regex patterns,
implemented all helpers, and authored the test file.

---

### [0.1.0-dev.2] — Docs: transaction block structure

**What changed:**
- `docs/hledger-compatibility.md` — new "Transaction Block Structure" section
  with annotated diagram, fixed field-order rule, and delimiter rules
- `docs/api-spec.md` — models (`Amount`, `Posting`, `Transaction`, `Journal`,
  `ParseError`, `parse_string`, `parse_file`) marked `[IMPLEMENTED]`; wire→model
  mapping diagram added to `Transaction` section

**Human:** Requested that the docs be updated to make the transaction block
format (begin/end delimiters, optional field ordering) explicit before any
parser implementation, to serve as the canonical format reference.

**Claude:** Designed the annotated diagram and delimiter rule wording, applied
the `[IMPLEMENTED]` status updates, and wrote the wire→model mapping.

---

### [0.1.0-dev.3] — Docs & style: regex documentation rule

**What changed:**
- `CLAUDE.md` — new "Regex Documentation Rule" in the Code Style section:
  every regex must be accompanied by a multiline comment covering purpose,
  group breakdown, and edge cases
- `ledgerkit/parser.py` — all four regexes (`_TXN_HEADER`, `_AMOUNT`, the
  date-check `re.match`, and the posting-split `re.split`) updated with full
  explanatory comments per the new rule

**Human:** Directed that all regexes must carry detailed explanatory comments
for debugging; specified the three required comment sections (purpose, groups,
edge cases).

**Claude:** Drafted the rule, wrote the worked example in `CLAUDE.md`, and
applied the rule retroactively to all existing regexes in `parser.py`.

---

### [0.1.0-dev.4] — Docs: mandatory double-space posting separator

**What changed:**
- `docs/hledger-compatibility.md` — posting table row and block-structure rules
  updated to state that two or more spaces between account name and amount is
  mandatory, not optional formatting
- `docs/api-spec.md` — `Posting` section now explains the separator rule and
  why single spaces are preserved (account names containing spaces)

**Human:** Identified that the double-space separator rule was not explicitly
documented as a hard requirement in the compatibility spec or API docs, and
directed the update.

**Claude:** Located the three affected passages across two doc files, applied
the wording changes, and verified no code changes were needed (the parser
already implements the rule via `re.split(r"\s{2,}", ...)`).

---

### [0.1.0-dev.5] — Docs & spec: supported file formats

**What changed:**
- `docs/hledger-compatibility.md` — new "Supported File Formats" section
  documenting the `.journal` and `.ledger` extensions as the only accepted
  formats; full deviation table listing all seven hledger 1.52 format families
  and ledgerkit's stance on each (with reference to the hledger 1.52 spec)
- `docs/api-spec.md` — `parse_file` docstring updated to state supported
  extensions and new `ParseError` condition for unsupported extensions;
  `Journal.source_file` comment updated accordingly
- `CLAUDE.md` — "Format target" updated to list both supported extensions
- `ledgerkit/parser.py` — `_SUPPORTED_EXTENSIONS` constant added; `parse_file`
  extended with an extension check that raises `ParseError` for unsupported
  formats (`.csv`, `.timeclock`, `.j`, etc.)
- `tests/test_parser.py` — 5 new assertions (3 unsupported extension cases,
  2 accepted extension cases including a `.ledger` tempfile round-trip)

**Human:** Specified that ledgerkit should support `.journal` and `.ledger` only,
identified this as a deliberate deviation from hledger 1.52, and provided the
hledger 1.52 data-formats reference URL for the full format list.

**Claude:** Fetched and parsed the hledger 1.52 data-formats page to compile
the complete format matrix, applied doc updates across four files, implemented
the extension guard in `parse_file`, and added tests for all new behaviour.

---

### [0.1.0-dev.6] — Feature: simple date formats

**What changed:**
- `ledgerkit/parser.py` — `_TXN_HEADER` date group broadened to capture all
  simple date variants; new `_SIMPLE_DATE` regex added with full group/edge-case
  comments; new `_parse_simple_date()` helper handles year inference; transaction
  header detection updated to match year-omitted dates; `parse_string` gains an
  optional `default_year` parameter (defaults to current calendar year)
- `docs/hledger-compatibility.md` — "Simple date" row updated to show all
  accepted formats; "Date formats" row removed from Out of Scope; "Smart dates"
  added to Undecided/Future
- `docs/api-spec.md` — `parse_string` signature and docstring updated with new
  `default_year` parameter and accepted date format descriptions
- `tests/test_parser.py` — 8 new assertions covering hyphen/slash/dot separators,
  optional leading zeros, year-omitted with explicit and default year, and
  invalid calendar date rejection

**Human:** Specified the full hledger simple dates spec (three separators,
optional leading zeros, optional year with inference rules), provided the
hledger 1.52 reference URL, and noted smart dates as undecided.

**Claude:** Redesigned the date-capture regex and parsing pipeline, implemented
year inference via `default_year`, updated all affected docs and the test suite.

---

### [0.1.0-dev.7] — Feature: block comments + comment coverage audit

**What changed:**
- `ledgerkit/parser.py` — `in_block_comment` state variable added to
  `parse_string`; `comment` directive detected before the silent-skip
  fallthrough and enters block-comment mode (flushing any open transaction);
  all lines in block-comment mode are consumed until `end comment` or EOF;
  whole-line comment branch comment updated to document that it also catches
  indented follow-on `;` lines via `lstrip()`
- `docs/hledger-compatibility.md` — Comments table expanded from 3 to 6 rows
  covering all implemented comment types (whole-line `;`, whole-line `#`,
  inline `;` on transaction, inline `;` on posting, follow-on indented `;`,
  block comment); "Other syntax" added to Undecided/Future
- `tests/test_parser.py` — 5 new assertions in `TestBlockComments`: block
  between transactions, block at file start, unclosed block runs to EOF,
  follow-on comment lines skipped, `end comment` outside block silently ignored

**Human:** Requested full implementation of the hledger 1.52 comments spec;
specified that "Other syntax" features remain undecided.

**Claude:** Fetched the hledger 1.52 comments spec, audited existing parser
coverage (whole-line, inline, and follow-on comments already handled), identified
block comments as the sole gap, implemented and tested the `comment`/`end comment`
state machine, and updated docs accordingly.

---

### [0.1.0-dev.8] — Docs: MIT License and acknowledgements

**What changed:**
- `LICENSE` — MIT License added; Acknowledgements section credits John Wiegley
  and the Ledger project (https://github.com/ledger/ledger) and Simon Michael
  and hledger contributors (https://github.com/simonmichael/hledger), with a
  pointer to the full hledger CREDITS file

**Human:** Directed that an MIT License be added with acknowledgements to the
Ledger project / John Wiegley and the hledger project / Simon Michael and
contributors. Human subsequently manually copied acknowledgements to Readme.md

**Claude:** Created `LICENSE` with standard MIT terms and a plain-English
Acknowledgements section naming both upstream projects and linking to the
hledger CREDITS page.

---

### [11c35f8] — 2026-04-15 — Process: milestone archiving rule + Milestone 0 archive

**What changed:**
- `CLAUDE.md` — "Changelog & Roadmap Rules" bullet updated: milestones may only
  be marked `[DONE]` when the user explicitly states completion; "Milestone
  archiving" heading clarified to match
- `ROADMAP.md` — "Deciding What Goes Into a Milestone" step 4 updated with the
  same explicit-user-approval requirement
- `dev-docs/changelog/MILESTONE-0.md` — created; contains the `[0.1.0-dev.0]`
  scaffold entry (oldest first), archive date, and commit placeholder
- `CHANGELOG.md` — `[0.1.0-dev.0]` replaced with a single summary line linking
  to the archive file

**Human:** Directed that milestones should only be marked complete when
explicitly specified by the user; confirmed Milestone 0 is complete and directed
execution of the archiving procedure.

**Claude:** Updated the rule in `CLAUDE.md` and `ROADMAP.md`, created
`dev-docs/changelog/` and `MILESTONE-0.md`, and replaced the dev.0 entry with a
summary link.

---

### [0.1.0-dev.10] — Fix: relax posting-line indentation requirement

**What changed:**
- `ledgerkit/parser.py` — state machine restructured: transaction-header and
  directive checks now run before posting detection; posting branch changed from
  `line.startswith("  ") or line.startswith("\t")` to `current_txn is not None`,
  making indentation conventional rather than mandatory; `parse_string` docstring
  updated to document the relaxed rule; posting-branch inline comment updated
- `docs/hledger-compatibility.md` — first delimiter rule updated (user-applied):
  posting indentation noted as conventional, not required

**Human:** Identified that the strict 2+ space / tab gate in `parse_string`
contradicted the updated compatibility doc stating indentation is not a
requirement; directed the parser to be updated to match.

**Claude:** Restructured the state-machine branch order so that transaction-header
and directive checks run first, then any unmatched line inside an open block is
treated as a posting regardless of indentation.

---

### [17207ce] — 2026-04-15 — Fix: normalise internal imports to ledgerkit (capital P)

**What changed:**
- `ledgerkit/parser.py` — `from ledgerkit.models import` → `from ledgerkit.models import`
- `ledgerkit/reports.py` — `from ledgerkit.models import` → `from ledgerkit.models import`
- `ledgerkit/cli.py` — all three `ledgerkit` references updated to `ledgerkit`
- `ledgerkit/parser.py` — posting-outside-block guard restored: indented lines
  outside a transaction block still raise `ParseError`; non-indented lines outside
  a block are silently skipped

**Human:** Directed that all internal imports be normalised to `ledgerkit`
(capital P) to match the package directory name and resolve the
`ModuleNotFoundError` that prevented the test suite from running.

**Claude:** Updated all cross-module imports in the three affected files, ran the
suite (36 tests), diagnosed one regression in `test_posting_outside_block_raises`
caused by the indentation relaxation, restored the guard for indented lines
outside a block, and confirmed 36/36 pass.

---

### [a2d68b3] — 2026-04-17 — Structural updates: docs split, packaging, module API, roadmap

**What changed:**
- `docs/` renamed → `dev-docs/` (git mv; all cross-references updated)
- `dev-docs/SYNC.md` — stale `hledger/` refs fixed to `ledgerkit/`; human-docs
  sync rule added
- `dev-docs/api-spec.md` — all `ledgerkit/` refs → `ledgerkit/`; `Journal` report
  methods, `load()`, `PriceDirective`, and `python -m ledgerkit` usage added
- `dev-docs/hledger-compatibility.md` — P directive and alias directive moved
  from Undecided/Out of Scope → **In Scope (v1)**; Directives table added
- `CLAUDE.md` — all `docs/` refs → `dev-docs/`; folder diagram corrected
  (`ledgerkit/` → `ledgerkit/`, `MANIFEST.in` and `__main__.py` added, `docs/`
  human section added); SYNC table updated; milestone archive path updated
- `README.md` — CLI command updated to `ledgerkit`; Python library example added;
  docs table added; Contributing section with sparse-checkout command added
- `ROADMAP.md` — all `docs/` refs → `dev-docs/`; Milestone 1 scope extended with
  P directive, alias directive, and module-level API; `ledgerkit.cli` → `ledgerkit`;
  Commodity price directives removed from backlog (now in Milestone 1)
- `pyproject.toml` — script entry `ledgerkit = "ledgerkit.cli:main"` →
  `ledgerkit = "ledgerkit.cli:main"`; `include = ["ledgerkit*"]` → `["ledgerkit*"]`
- `MANIFEST.in` — new file; excludes `CLAUDE.md`, `CHANGELOG.md`, `ROADMAP.md`,
  `dev-docs/` from sdist
- `ledgerkit/models.py` — `PriceDirective` dataclass added; `Journal.prices` field
  added; four report methods added to `Journal` (lazy-import delegation to reports)
- `ledgerkit/__init__.py` — `load()` convenience function exported
- `ledgerkit/__main__.py` — new file; enables `python -m ledgerkit`
- `ledgerkit/cli.py` — `prog="ledgerkit"` → `prog="ledgerkit"`
- `docs/` — new human-facing documentation folder created with four guides:
  `getting-started.md`, `usage.md`, `journal-format.md`, `python-api.md`

**Human:** Directed the structural refactor: rename `docs/` to `dev-docs/`,
create a human `docs/` folder, add sparse-checkout clone command, fix packaging
capitalisation, add `load()` + `__main__` + Journal report methods, extend
Milestone 1 to include P directive and alias directive.

**Claude:** Executed the full plan across 18 files: git mv for the folder rename,
updated all cross-references, created `MANIFEST.in`, added `PriceDirective` and
Journal methods with lazy-import pattern, created `__main__.py`, and authored all
four human guide files.

---

### [Unreleased] — Scope: add `include` directive to Milestone 1

**What changed:**
- `dev-docs/hledger-compatibility.md` — `include` directive moved from Out of
  Scope → **In Scope (v1)** Directives table; behaviour documented (inline
  embedding, parent-directive propagation, `.journal`/`.ledger` targets only,
  `ParseError` on unsupported extension); removed from "Directives" catch-all
  Out of Scope row
- `ROADMAP.md` — `include` directive added to Milestone 1 scope block and exit
  criteria; removed from Future/Backlog table

**Human:** Directed that the `include` directive is in scope for v1, referencing
the hledger 1.52 specification.

**Claude:** Fetched the hledger 1.52 `include` directive spec, updated the
compatibility doc and roadmap accordingly.

---

### [Unreleased] — Docs: correct P directive scope description

**What changed:**
- `docs/journal-format.md` — P directive section rewritten: removed incorrect
  "global" scope claim; added explanation of `journal.prices` (a list of
  `PriceDirective` objects, one per directive, in file order, each recording
  date, commodity, and price amount); removed milestone language from human doc
- `dev-docs/hledger-compatibility.md` — P directive notes updated: "global"
  removed; scope behaviour (file-local vs propagated via `include`) documented
  as TBD at implementation; commodity valuation noted as in-scope for Milestone 2
- `dev-docs/api-spec.md` — `PriceDirective` section updated: note added that
  commodity valuation is in scope for v1 (Milestone 2)
- `ROADMAP.md` — Milestone 2 candidate scope updated: commodity valuation using
  `Journal.prices` added as an explicit line item

**Human:** Identified that the P directive docs incorrectly stated "global
(apply to all entries in the file)"; clarified that P directives declare a
commodity price at a point in time, that `journal.prices` should be explained
to human readers, and that commodity valuation is in scope for v1.

**Claude:** Updated all four files; removed "global" claim; explained
`journal.prices` in human docs; moved commodity valuation into Milestone 2
candidate scope in the roadmap.

---

### [Unreleased] — Project: add CONTRIBUTING.md and CODE_OF_CONDUCT.md

**What changed:**
- `CONTRIBUTING.md` added at project root (moved from `ledgerkit/` subfolder);
  title corrected from "hledger-textual" to "ledgerkit"; test command updated
  from `uv run pytest` to `python -m unittest tests.test_parser -v`
- `CODE_OF_CONDUCT.md` added at project root (moved from `ledgerkit/` subfolder)
- `README.md` — Contributing section updated with brief reference to
  `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`
- `CLAUDE.md` — Commit Message Format subsection added under Changelog & Roadmap
  Rules; specifies Conventional Commits standard with types, imperative mood,
  72-char limit, no trailing period, blank line + body for complex changes

**Human:** Added `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`; directed that
contribution guidelines should be referenced briefly in README and that Claude
should follow the commit message format defined in CONTRIBUTING.md.

**Claude:** Moved both files to project root; corrected project name and test
command in CONTRIBUTING.md; updated README.md Contributing section; added commit
message format rule to CLAUDE.md.

---

### [Unreleased] — chore: switch to stable setuptools build backend

**Human:** Update `pyproject.toml` to use `setuptools.build_meta` and drop the version pin on `setuptools`.
**Claude:** Replaced `setuptools.backends.legacy:build` with `setuptools.build_meta` and changed `requires` from `["setuptools>=68"]` to `["setuptools"]`.

---

### [Unreleased] — feat: implement `stats` report (full hledger 1.52 spec)

**Human:** Implement the `stats` command matching the full hledger 1.52 spec,
including `-v`/`--verbose`, `-1`, and `-o`/`--output-file` flags; add roadmap
items for unimplementable features (memory stats, reporting interval).

**Claude:** Expanded `JournalStats` to 18 fields (included files, last txn,
span days, per-day rates, last-7/30 days, payee count, account depth, commodity
list, price count); implemented `reports.stats()`; rewrote CLI stats block with
runtime timing and all three flags; added `TYPE_CHECKING` guard and return type
to `Journal.stats()` in models.py; re-exported `JournalStats` from
`ledgerkit.__init__`; added 30 tests in `tests/test_reports.py`; updated
`dev-docs/api-spec.md` (status → `[IMPLEMENTED]`, expanded dataclass, CLI flags);
added three roadmap items to `ROADMAP.md`.

---

### [Unreleased] — chore: release v0.1.1

**Human:** Bump version to v0.1.1.
**Claude:** Updated `version` in `ledgerkit/__init__.py` and `pyproject.toml` from `0.1.0` to `0.1.1`.

---

### [Unreleased] — docs: add module size & refactoring guidelines to CLAUDE.md

**Human:** Add a rule to CLAUDE.md that flags modules/tests exceeding 300–500 lines or handling too many responsibilities, and requires explicit user approval before any major refactor.
**Claude:** Added a new `## Module Size & Refactoring` section to `CLAUDE.md` after `## Code Style`, defining the size threshold, the three-step flag-propose-approve process, and clarifying that "major refactor" means cross-file reorganisation (not intra-function tidying).

---

### [Unreleased] — feat: add loader.py module and implement include directive

**Human:** Implement a file loader in a separate module and implement the `include` directive (full hledger 1.52 spec). This is a major upgrade — refactor as necessary, update dev-docs/user docs, and update the public API.

**Claude:** Extracted all file I/O into a new `ledgerkit/loader.py` module (`load_journal()`). Implemented the `include` directive with text-expansion strategy: relative/absolute/tilde paths, glob patterns (`*`, `**`, `?`, `[range]`), recursive expansion, circular include detection, format-prefix rejection, and `FileNotFoundError` for missing non-glob targets. Added `Journal.included_files: int = 0` field to models.py. Removed `parse_file()` and `_SUPPORTED_EXTENSIONS` from parser.py (pure text-only module). Updated `ledgerkit.load` alias, cli.py, reports.py. Added 10 fixture files and 40+ tests in `tests/test_loader.py`. Updated architecture.md, api-spec.md, hledger-compatibility.md, journal-format.md, python-api.md, and ROADMAP.md. All 102 tests pass.

---

### [Unreleased] — chore: release v0.1.2

**Human:** Update version number to 0.1.2.
**Claude:** Updated `version` in `ledgerkit/__init__.py` and `pyproject.toml` from `0.1.1` to `0.1.2`.

---

### [Unreleased] — feat: implement -f/--file CLI flag

**Human:** Implement the `-f`/`--file` flag in the CLI interface per the hledger spec: repeatable, stdin support (`-`), and fallback to `$LEDGER_FILE` / `~/.hledger.journal` when no file is specified.

**Claude:** Added `-f`/`--file` flag to `cli.py` (`action='append'`, repeatable). Made the positional `journal` argument optional (backward-compatible shorthand for a single `-f`; error if both given). Added `_resolve_files()` helper with full fallback chain. Added `load_journal_stdin()` and `merge_journals()` to `loader.py`. Updated `main()` to load all specified files and merge. Added `TestMergeJournals` (9 tests) to `test_loader.py` and new `tests/test_cli.py` (15 tests). Updated `api-spec.md`, `architecture.md`, `docs/usage.md`. All 128 tests pass.

---

### [Unreleased] — feat: checks module, strict mode, and account/commodity/payee directives

**Human:** Extend Milestone 1 to include: `account`, `commodity`, and `payee` directive parsing; a new `checks.py` module with `autobalanced`, `accounts`, `commodities`, `payees`, `ordereddates`, and `uniqueleafnames` checks; default autobalanced validation on all CLI commands; `-s`/`--strict` flag; and a `check [NAME...]` CLI command.

**Claude:** Added `declared_accounts`, `declared_commodities`, `declared_payees` fields to `Journal` (models.py). Added `account`, `commodity`, and `payee` directive parsing to `parser.py` (with 2-space comment separator rule, subdirective consumption, quoted payee/commodity support, and full hledger 1.52 symbol-extraction algorithm). Extended `merge_journals()` to concatenate all three declared-* lists. Created `ledgerkit/checks.py` with `CheckError` dataclass, seven check functions, and three runners (`run_basic_checks`, `run_strict_checks`, `run_checks`). Updated `cli.py`: default basic-check gate on all commands, `-s`/`--strict` flag, `check [NAME...]` command, and `nargs="*"` for the positional to support multiple check names. Re-exported `CheckError` from `ledgerkit.__init__`. Added `tests/test_checks.py` (56 tests), extended `test_parser.py` (26 new tests), `test_loader.py` (5 new tests), and `test_cli.py` (3 updated tests). Added `tests/fixtures/strict_valid.journal`. Updated `api-spec.md`, `architecture.md`, `hledger-compatibility.md`, `docs/usage.md`. All 213 tests pass.

---

### [Unreleased] — feat: hledger-style strict check error output with source context

**Human:** Update `-s`/`--strict` error output to match hledger behaviour: stop after the first failing account/commodity, show the source file path and line number, display the transaction context with carets underlining the problematic account or amount, and include the "Consider adding a directive" suggestion text.

**Claude:** Added `source_line: int | None` field to `Posting` and `Transaction` models (recorded by `_parse_txn_header` and `_parse_posting` in parser.py). Added private helpers `_fmt_txn_header`, `_fmt_amount`, `_fmt_posting`, and `_build_strict_context` to `checks.py`. Refactored `check_accounts` and `check_commodities` to stop at the first error and return a multi-line message with `Error: <path>:<line>:` header, transaction context, caret underline, and suggestion text matching hledger 1.52 format. Changed `CheckError.message` docstring from "single line" to "may be multi-line". Updated `TestCheckAccounts.test_no_declarations_flags_all` → `test_no_declarations_reports_first` (now expects 1 error, matching hledger stop-at-first). Updated 4 CLI test assertions from `"accounts/commodities check"` to `"has not been declared"`. Updated `api-spec.md`. All 216 tests pass.

---

### [Unreleased] — feat: tag directive and decimal-mark directive

**Human:** Implement the `tag` and `decimal-mark` directives from hledger 1.52 in ledgerkit.

**Claude:** Added `declared_tags: list[str]` field to `Journal` (models.py). Added `tag TAGNAME` directive parsing to `parse_string()` (parser.py) — strips inline comments with the 2-space rule, consumes indented subdirectives, stores names in `declared_tags`. Added `decimal-mark .` / `decimal-mark ,` directive parsing — switches amount parsing mode for all subsequent postings; default is period-decimal. Added `_AMOUNT_COMMA` regex for EU-style comma-decimal amounts (e.g. `1.234,56` → `Decimal("1234.56")`); `_parse_amount` and `_parse_posting` accept a `decimal_mark` parameter. Extended `merge_journals()` in `loader.py` to concatenate `declared_tags`. Added `TestTagDirective` (6 tests) and `TestDecimalMarkDirective` (8 tests) to `test_parser.py`; added `test_merge_declared_tags_concatenated` to `test_loader.py`. Updated `api-spec.md` and `hledger-compatibility.md`. Periodic transactions (`~`) remain silently ignored (out of scope).

---

### [Unreleased] — feat: P directive parsing (market price declarations)

**Human:** Implement the P directive which declares a market price relationship between two commodities, per hledger 1.52 spec.

**Claude:** Added `PriceDirective` to the `parser.py` import. Added `_P_DIRECTIVE` regex (with full doc comment). Added `prices: list[PriceDirective]` state variable to `parse_string()`. Added P directive handler in the main loop — parses date via `_parse_simple_date`, price amount via `_parse_amount`, strips inline comments with `_strip_directive_comment`. Passes `prices` to the returned `Journal`. Added `TestPDirective` (9 tests) to `test_parser.py`. Updated `hledger-compatibility.md` to mark P directive `[IMPLEMENTED]`. No changes to `models.py`, `loader.py`, or `api-spec.md` — those were already correct.

---

### [Unreleased] — feat: alias directive (account name rewriting)

**Human:** Implement the alias directive which rewrites account names before generating reports, per hledger 1.52 spec. Command-line `--alias` option deferred to a future milestone.

**Claude:** Updated `_TWO_SPACE_SEP` to `r"\s{2,}[;#]"` so that both `;` and `#` are recognised as inline comment introducers in all directive bodies (affects all existing directive handlers). Added `_ALIAS_DIRECTIVE` and `_END_ALIASES` module-level regexes with full documentation. Added `_parse_alias_body()` private helper (parses basic and regex alias bodies, validates regex at parse time, raises `ParseError` for malformed input). Added `_apply_aliases()` private helper (applies alias list in LIFO order; basic aliases use prefix matching; regex aliases use `re.sub` with IGNORECASE and backreference support). Added `aliases: list[tuple[str, str, bool]]` state variable to `parse_string()`. Added alias handler and end-aliases handler in the main loop (after P directive handler, before posting handler); end-aliases handler uses `_strip_directive_comment` before matching so trailing `;`/`#` comments are tolerated. Applied aliases in the account directive handler and in the posting handler. Added `TestAliasDirective` (17 tests) to `test_parser.py`. Updated `hledger-compatibility.md` to mark alias directive `[IMPLEMENTED]` and document the file-scoping deviation. Updated `docs/journal-format.md` with user-facing alias documentation. No changes to `models.py`, `loader.py`, or `api-spec.md`.

---

### [Unreleased] — chore: move test_checks, test_cli, test_loader into subfolders

**Human:** Move `test_checks.py`, `test_cli.py`, and `test_loader.py` into matching subfolders (`test_checks/`, `test_cli/`, `test_loader/`) for consistency with the folder structure established in the previous refactor.

**Claude:** Created `tests/test_checks/test_checks.py`, `tests/test_cli/test_cli.py`, and `tests/test_loader/test_loader.py` with updated `FIXTURES` paths (`pathlib.Path(__file__).parent.parent / "fixtures"`). Added `__init__.py` to each new subdirectory (and retroactively to `test_parser/` and `test_directives/` — the previous refactor omitted these, causing Python 3.13 `unittest discover` to silently skip those subdirectories, which went unnoticed because the flat files were still counted; with all `__init__.py` files in place, all 265 tests are now discovered and run). Deleted the three original flat test files. Updated `tests/README.md` and `CLAUDE.md` folder structure diagram. All 265 tests pass.

---

### [Unreleased] — chore: test refactor, Black formatter config, and directive # comment tests

**Human:** Refactor test suite into named subfolders (`test_parser/`, `test_directives/`, `test_reports/`), add Black formatter VS Code and pyproject.toml config, and ensure all directive test classes cover `#` inline comment stripping (not just `;`).

**Claude:** Split `tests/test_parser.py` (814 lines, 19 classes) into `tests/test_parser/test_parser.py` (12 core parser test classes) and `tests/test_directives/test_directives.py` (7 directive test classes). Deleted the original flat file. Created `tests/test_reports/` directory earmarked for future report tests. Each test subdirectory has an `__init__.py` — required by Python 3.13's `unittest discover` to recurse into subdirectories (namespace-package-only subdirectories are silently skipped). Updated `tests/README.md` with new folder layout, updated run commands (now `-s tests -t . -v`), and added note about the `".."` in the fixtures path for subdirectory test files. Updated `CLAUDE.md` test run command and folder structure diagram. Created `.vscode/settings.json` with Black formatter on-save settings. Added `[tool.black]` section to `pyproject.toml`. Renamed 5 existing `;`-only comment tests across `TestAccountDirective`, `TestCommodityDirective`, `TestPayeeDirective`, `TestTagDirective`, and `TestPDirective` to `_semicolon_comment_stripped` for naming consistency with `TestAliasDirective`. Added 6 new `#` comment tests (`test_account_hash_comment_stripped`, `test_commodity_hash_comment_stripped`, `test_payee_hash_comment_stripped`, `test_tag_hash_comment_stripped`, `test_decimal_mark_semicolon_comment_stripped`, `test_decimal_mark_hash_comment_stripped`, `test_p_directive_hash_comment_stripped`).

---

### [Unreleased] — test: guard Optional amount access with assert-not-None

**Human:** Fix Pylance `reportOptionalMemberAccess` warnings on `Posting.amount` across the test suite.

**Claude:** Added `assert amt is not None` after each `posting.amount` assignment in `tests/test_parser/test_parser.py` (5 sites) and `tests/test_directives/test_directives.py` (12 sites). Used bare `assert` (not `self.assertIsNotNone`) because Pylance recognises the former as a type-narrowing guard. All 265 tests pass.
