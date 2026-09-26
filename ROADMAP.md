# ledgerkit Roadmap

Milestones track the planned development path. Each milestone corresponds to one
or more GitHub commits and should leave the codebase in a releasable, tested state.

**Status key:** `[DONE]` · `[IN PROGRESS]` · `[PLANNED]` · `[BACKLOG]` · `[SUPERSEDED]`

> **2026-09-12 — Core redefinition.** Ledgerkit's product goal was redefined
> from "a Python implementation of the hledger journal format" to a
> deterministic, Python-native accounting and query engine with a
> documented hledger-compatible foundation — see
> `dev-docs/planning/core-redefinition/01-product-goal.md`. Milestones 0–4
> below are retained unchanged as completed history and map directly into
> the new structure (`dev-docs/planning/core-redefinition/12-roadmap-migration.md`).
> Milestone 5 is superseded (see below). Forward-looking work now proceeds
> as **Stages A–I**, summarised at the bottom of this file; full detail is
> in `dev-docs/planning/core-redefinition/`. Human-decision-gate status for
> this redefinition: `dev-docs/planning/core-redefinition/14-human-decision-gates.md`.

---

## Milestone 0 — Project Foundation `[DONE]`

Establish the project structure, tooling contracts, and data models so that all
subsequent work has a clean, documented base to build on.

**Scope:**
- Project scaffold: folder structure, `pyproject.toml`, `CLAUDE.md` rules
- Core data models: `Amount`, `Posting`, `Transaction`, `Journal`
- Initial documentation: `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
  `dev-docs/hledger-compatibility.md`, `dev-docs/SYNC.md`
- Developer tooling: `.gitignore`, test conventions (`tests/README.md`),
  sample fixture (`tests/fixtures/sample.journal`)

**Exit criteria:** All models importable; `python -m unittest tests.test_parser -v` runs
with no errors (empty suite passes).

---

## Milestone 1 — Journal Parser `[DONE]`

Implement a working parser so that `.journal` files can be loaded into memory as
`Journal` objects, including key hledger directives.

**Scope:**
- `parse_string(text) -> Journal` — pure text parser ✅
- `load_journal(path) -> Journal` — file loader with include support (in `loader.py`) ✅
- `ParseError` with line-number context ✅
- Transaction header parsing (date, flag, code, description, comment) ✅
- Posting parsing (prefix/suffix commodity, thousands separator, elided amount,
  double-space separator rule) ✅
- Simple date formats: all three separators (`-`, `/`, `.`), optional leading
  zeros, year-omitted with inference ✅
- Block comments (`comment` / `end comment` directive) ✅
- **P directive** (`P DATE COMMODITY PRICE`) — market price declarations stored
  in `Journal.prices` as `PriceDirective` objects ✅
- **alias directive** (`alias OLD=NEW` / `alias /REGEX/=REPLACEMENT` /
  `end aliases`) — account names rewritten at parse time within the current file ✅
- **include directive** (`include other.journal`) — embeds entries and directives
  from another `.journal` or `.ledger` file inline; relative, absolute, tilde,
  and glob paths supported; circular include detection; format-prefix rejection ✅
- **account directive** (`account ACCOUNT`) — declares an account name; stored
  in `Journal.declared_accounts` ✅
- **commodity directive** (`commodity $1,000.00` / `commodity EUR`) — declares a
  commodity symbol; stored in `Journal.declared_commodities` ✅
- **payee directive** (`payee PAYEE`) — declares a payee name; stored in
  `Journal.declared_payees` ✅
- **Validation / checks module** (`checks.py`) — `CheckError`, individual check
  functions (`autobalanced`, `accounts`, `commodities`, `payees`,
  `ordereddates`, `uniqueleafnames`), and runners ✅
- **Default autobalanced gate** — all CLI commands validate transaction balance
  before executing ✅
- **`-s`/`--strict` flag** — additionally checks that all accounts and
  commodities are declared ✅
- **`check [NAME...]` command** — run individual or grouped checks on demand ✅
- Module-level API: `Journal` report methods (`.balance()`, `.register()`,
  `.accounts()`, `.stats()`); `ledgerkit.load()` convenience function;
  `python -m ledgerkit` entry point ✅
- Regex documentation rule enforced on all patterns ✅
- `dev-docs/hledger-compatibility.md` updated with transaction block structure,
  P directive, alias directive, include directive, account/commodity/payee
  directives, and validation checks table ✅

**Exit criteria:**
- `python -m unittest tests.test_parser tests.test_reports tests.test_loader tests.test_checks tests.test_cli -v` — all 213 tests pass ✅
- `python -m ledgerkit print tests/fixtures/sample.journal` outputs all
  5 transactions correctly ✅
- P directives parsed and stored in `journal.prices` ✅
- Account aliases applied correctly against a fixture covering both simple and
  regex alias forms ✅
- `include` directive resolves relative, absolute, tilde, and glob paths;
  included file entries appear in the resulting `Journal` as if written inline ✅
- `python -m ledgerkit -s -f tests/fixtures/strict_valid.journal stats` exits 0 ✅
- Unbalanced transaction causes exit 1 on any command ✅
- `python -m ledgerkit check ordereddates -f tests/fixtures/sample.journal` runs cleanly ✅

---

## Milestone 2 — Core Reports `[DONE]`

Implement the `Query` filter dataclass, all four report functions, and the
`ReportSpec` / `ReportSection` foundation for custom report layouts.

**Scope:**
- `Query` dataclass in `models.py` — filter criteria for all report functions ✅
- `accounts(journal, query=None) -> list[str]` — fully implemented ✅
- `balance(journal, query=None) -> dict[str, Decimal]` — fully implemented ✅
- `register(journal, query=None) -> list[RegisterRow]` — fully implemented ✅
- `stats(journal, query=None) -> JournalStats` — extended with partial query support ✅
- `RegisterRow` dataclass moved to `models.py` ✅
- `ReportSection`, `ReportSpec` (frozen), `ReportSectionResult` dataclasses in `models.py` ✅
- `balance_from_spec(journal, spec, query=None)` — proof-of-concept implementation ✅
- All new types re-exported from `ledgerkit.__init__` ✅
- `tests/fixtures/filtered.journal` — 6-transaction, 64-day fixture with elided posting ✅
- Full test suite for all new functionality (`tests/test_reports.py`) — 92 tests ✅
- `dev-docs/api-spec.md` updated to mark all functions `[IMPLEMENTED]` ✅
- `docs/python-api.md` updated with `Query` and `ReportSpec` worked examples ✅
- **Balance assertions** — inline `=`, `==`, `=*`, `==*` syntax parsed and validated ✅
  - `BalanceAssertion` dataclass in `models.py`; `Posting.balance_assertion` field ✅
  - `check_assertions` added to `checks.py` as a basic check (date-order, all variants) ✅
  - `-I`/`--ignore-assertions` CLI flag ✅
  - `assertions_pass.journal` and `assertions_fail.journal` fixtures ✅

**Deferred to Milestone 3:**
- CLI filter flags (`--account`, `--date`, `--payee`) wiring Query to the CLI
- Journal-comment-based `ReportSpec` parsing (`; report` / `; end report` syntax)
- Full `stats` query support (account-level filters on `account_count` / `account_depth`)
- Commodity valuation using `Journal.prices` (multi-commodity balance reports)

**Exit criteria:**
- `python -m unittest discover -s tests -t . -v` — all 363 tests pass ✅
- `from ledgerkit import Query, ReportSpec, ReportSection, ReportSectionResult, balance_from_spec` succeeds ✅
- `balance`, `register`, `accounts`, `stats` each return correct results with no query ✅
- `balance(journal, query=Query(account="expenses"))` returns only expense rows ✅
- `balance(journal, query=Query(depth=1))` returns only top-level account balances ✅
- `balance_from_spec(journal, spec)` returns one `ReportSectionResult` per section ✅
- `stats(journal)` continues to produce identical output to Milestone 1 ✅
- `cli.py` unchanged from Milestone 1 state ✅

---

## Milestone 3 — Editor Readiness & Multi-Commodity `[DONE]`

Deliver multi-commodity balance reporting, a lenient parser for editor integrations,
and a complete in-memory editor layer so that a TUI package can load, mutate, and
save journal files without reaching into ledgerkit internals.

**Completed scope:**
- `parse_string_lenient` — never-raises parser; returns `(Journal, list[ParseError])` ✅
- `CheckError.line_number` — 1-based source line on every check error ✅
- `balance()` returns `dict[str, dict[str, Decimal]]` (multi-commodity per account) ✅
- `balance(tree=True)` returns `list[BalanceRow]` with implicit parent aggregation ✅
- `resolve_elision()` public — N-commodity elided posting generates N inferred postings ✅
- `BalanceRow` dataclass in `models.py` ✅
- `SourceSpan` dataclass; `Transaction.source_span`, `raw_text`, `inline_comment` ✅
- `Posting.inline_comment` — inline `;` comment captured at parse time ✅
- `source_file` parameter on `parse_string` and `parse_string_lenient` ✅
- `check_transaction_autobalanced(txn)` — per-transaction validation without full journal ✅
- `writer.py` — `transaction_to_text`, `journal_to_text` ✅
- `editor_model.py` — `EditorDocument` (load / add / update / delete / save / reload / validate) ✅
- 461 tests across nine test modules ✅

**Deferred to future milestones:**
- CLI filter flags (`--account`, `--date`, `--payee`) wired to `Query`
- Journal-comment `ReportSpec` parsing (`; report` / `; end report` syntax)
- Full `stats` query support (account-level filters on `account_count` / `account_depth`)
- `pip install` packaging and `README.md` / `docs/` update with real usage examples

**Exit criteria met:**
- `python -m unittest discover -s tests -t . -v` — all 461 tests pass ✅
- `python -c "from ledgerkit import writer, editor_model"` succeeds ✅
- `EditorDocument('tests/fixtures/sample.journal')` loads with `dirty=False`, 5 transactions ✅
- Round-trip smoke test: `journal_to_text` output re-parses to same transaction count ✅

---

## Milestone 4 — Comprehensive Format Compatibility `[DONE]`

Enable ledgerkit to load `tests/fixtures/comprehensive-hledger-test.journal`
(and its included `comprehensive-hledger-test-commodities.journal`) with
**zero `ParseError` objects** and `python -m ledgerkit check` exiting 0.

The two fixture files were authored to exercise almost every hledger 1.52
journal-syntax feature and serve as a living regression suite for parser breadth.

**Scope:**

*Amount parser fixes (`parser.py` — `_AMOUNT` regex and `_parse_amount`)*
- Sign after prefix symbol: `$-300`, `£-10` (currently only leading `-$300` works)
- Cost annotations: `@ UNIT_PRICE` / `@@ TOTAL_PRICE` — strip before parsing; store
  raw annotation text on `Posting` for future valuation use
- Lot annotations: `{UNIT}` / `{{TOTAL}}` / `[DATE]` / `(LABEL)` — strip; not stored v1
- Quoted commodity suffix: `-3 "Chocolate Frogs"` (suffix with spaces/special chars)
- Space digit-group separator: `1 000 000 JPY`
- Scientific E-notation: `1E3 EUR`, `1e-2 BTC`

*Transaction header fix (`parser.py` — `_TXN_HEADER` regex and `_parse_txn_header`)*
- Secondary/auxiliary date: `2024-02-20=2024-02-22` → store `Transaction.date2`

*New directives (`parser.py` — `_parse_string_impl`)*
- `D AMOUNT` — set default commodity; applied to no-symbol amounts like `2.00`
- `Y YEAR` — override internal `default_year` from journal file
- `apply account PREFIX` / `end apply account` — prepend PREFIX to every account name
  inside the block (mirrors hledger behaviour)
- `~` periodic-transaction rule lines — recognise header, skip block without error
- `=` auto-posting rule lines — recognise header, skip block without error

*Commodity directive fix (`parser.py` — `_extract_commodity_symbol`)*
- Handle `1,000. "Chocolate Frogs"` form: numeric sample + quoted suffix symbol

*Model change (`models.py`)*
- `Transaction.date2: Optional[datetime.date] = None` — secondary date field

**Exit criteria:**
- `parse_string_lenient(open('tests/fixtures/comprehensive-hledger-test.journal').read())`
  returns `(journal, [])` — zero errors, all transactions parsed
- `python -m ledgerkit check -f tests/fixtures/comprehensive-hledger-test.journal` exits 0
- All 485 existing tests continue to pass
- 20+ new tests in `tests/test_parser/test_parser.py` covering each root cause above
- `dev-docs/api-spec.md` updated with `Transaction.date2`
- `dev-docs/hledger-compatibility.md` updated (all new features added to supported table)
- `CHANGELOG.md` entry added

**Intentionally deferred:**
- `--forecast` periodic transaction generation
- `--auto` auto-posting application
- Lot price tracking / cost-basis reporting
- Virtual posting balance semantics (`()` unbalanced, `[]` balanced)
- Commodity conversion entries (`equity:conversion`)

---

## Milestone 5 — CLI Filter Flags `[SUPERSEDED]`

**Superseded 2026-09-12 by Stage C (Query System) — not implemented as
originally scoped.** Wiring CLI flags directly to today's `Query`
dataclass, as drafted below, would build exactly the narrow ad-hoc
filtering the Core redefinition replaces with a proper query AST shared
across reports, the CLI, and future adapters. The underlying user need
(filter reports from the CLI) is fully preserved — it becomes part of
Stage C's `--query`-flag work instead, routed through the new query engine.
See `dev-docs/planning/core-redefinition/07-query-regex.md` and
`12-roadmap-migration.md` §12.3.

Original scope (kept for reference, not built):
- `--account PATTERN` / `-a PATTERN` — filter by account substring or regex
- `--date-from DATE` / `--date-to DATE` — filter by date range
- `--payee PATTERN` — filter by description substring or regex
- `--depth N` — roll balance up to N levels
- Apply consistently across `balance`, `register`, `accounts`, `stats`

---

## Future / Backlog — reclassified into Stages, 2026-09-12

Every item below was reclassified, not dropped, as part of the Core
redefinition (`dev-docs/planning/core-redefinition/12-roadmap-migration.md`
§12.3). None were implemented by that reclassification — each is now
sequenced within a specific forward Stage instead of sitting unscheduled.

| Item | Old status | New disposition |
|---|---|---|
| Journal-comment `ReportSpec` parsing | `[BACKLOG]` | Stage D (Reporting) |
| Full `stats` query support | `[BACKLOG]` | Stage C (Query System), immediately after the query engine lands |
| `EditorDocument` include-directive support | `[BACKLOG]` | Stage B (Core model) |
| Account type inference | `[BACKLOG]` | Stage E (Accounting semantics) |
| Periodic/auto postings | `[BACKLOG]` ("out of scope for v1") | Stage G (Generated/transformative behaviour) |
| `stats`: peak live memory (`psutil`) | `[BACKLOG]` | Deferred indefinitely — still blocked on third-party-dependency approval, unchanged by the licence migration |
| `stats`: peak allocated memory (`tracemalloc`) | `[BACKLOG]` | Low-priority Core-adjacent backlog — stdlib-only, not blocking any Stage |
| `stats`: per-reporting-interval output | `[BACKLOG]` | Stage D (Reporting), alongside report-engine consolidation |

---

## Stages A–I (Core redefinition — forward roadmap)

Full detail: `dev-docs/planning/core-redefinition/`. One-line summary per
stage; each becomes a `dev-docs/planning/<stage>.md` plan file (per the
"Deciding What Goes Into a Stage" process below) before implementation
begins, exactly as milestones have always worked here.

| Stage | Focus | Status | Plan |
|---|---|---|---|
| A | Development foundation — agent roster, CodeCompass integration, compatibility harness, learning/doc lifecycle | `[DONE]` (2026-09-12, user-confirmed) — licence migration, positioning, roadmap migration, agent-role files (`.claude/agents/*.md`, 7 roles), and the compatibility harness (schema, structure, `UNEXPLAINED.md`, first wave of 25 `status: proposed` register entries) all shipped; full changelog archived to `dev-docs/changelog/STAGE-A.md`. Deliberately not done in Stage A (not blockers, tracked as open follow-up): the finer-grained amount/comment/transaction-field-level register migration, and first real CodeCompass usage under `context-curator` (expected to happen naturally once Stage B/C generate real tasks) | `core-redefinition/03,04,05,09,11` |
| B | Core model — journal/accounting model review, Editor-compatibility confirmation | `[DONE]` (2026-09-13, user-confirmed) — Phase 1: independent `ledgerkit-editor` import inventory, correcting three inaccuracies in G8's earlier inventory. Phase 2: `models.py` structural review confirms "no structural change needed now" for Stage E/F, conditioned on two recorded guardrails. Both read-only; no `ledgerkit/`/`tests/` code touched. Full changelog archived to `dev-docs/changelog/STAGE-B.md`. | `core-redefinition/06`, `15`, `16` |
| C | Query system — parser/AST, hledger query semantics, Python `re` extension, CLI/report routing | `[IN PROGRESS]` — Phase 1 done: `hledger-researcher`'s semantics brief (`core-redefinition/17-query-semantics-brief.md`) plus a standalone, tested `ledgerkit/query/` subpackage (AST, `HledgerRegex`-subset validation, parser, evaluator) implementing `acct:`/`desc:`/`date:`(simple)/`depth:`/`status:`/`not:`. Not yet wired into `reports.py`/`cli.py`/`Query`; `tag:`/`cur:`/smart-dates/`PythonRegex` extension deferred. 7 compat-register entries added, all `status: proposed`. **Phase 2 done**: CodeCompass-assisted query/report/CLI integration (`core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md`, retro `dev-docs/retros/STAGE-C-PHASE-2.md`). `-q`/`--query` wired into `balance`/`register`/`accounts`/`stats` via a private, internal-only `reports._query_ast` parameter (no public API change). Differential-verified against the pinned hledger 1.52.4 binary; found and fixed two real CLI defects (EC-016) and corrected a Stage C Phase 1 misclassification (`LK-COMPAT-QUERY-DEPTH-001`, now `intentional_divergence`, EC-017). Ledgerkit's own first-ever real use of the `codecompass` CLI against its live repo, producing the project's first `CC-LK-NNN` finding (`validation/codecompass/findings/CC-LK-001`) — recommendation: not yet warranted as a mandatory workflow step (consistent LOW advantage, six data points across both usage directions). **Phase 3 done**: `-q` wired into `print` too (retro `dev-docs/retros/STAGE-C-PHASE-3.md`) — a matching transaction is shown whole, differential-verified against hledger's own `print` behaviour (`LK-COMPAT-QUERY-PRINT-INTEGRATION-001`). Only `check` remains unwired (by design). **Phase 4 done**: tag data model — parsing/storage only, not the `tag:` query term (retro `dev-docs/retros/STAGE-C-PHASE-4.md`). Split from `tag:` query work mid-phase by explicit user choice, after `hledger-researcher` briefs (`core-redefinition/19-tag-query-semantics-brief.md`, `20-tag-parsing-syntax-brief.md`) showed no tag data model existed at all. New `ledgerkit/tags.py` module (`parse_tags`, `effective_date`/`effective_date2`); new fields `Posting.tags`/`date_override`/`date2_override`, `Transaction.tags`, `Journal.declared_account_tags` (all user-confirmed via `AskUserQuestion` before touching `dev-docs/api-spec.md`); also fixed a real pre-existing gap where `account` directive comments were discarded entirely. Differential-verified against the pinned hledger 1.52.4 binary; 4 new compat-register entries, all `status: verified`. `tag:`/`cur:`/`PythonRegex`/`Query`-as-shim query-matching work untouched — next phase not yet scoped. **Phase 5 done**: `core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md` (retros `dev-docs/retros/STAGE-C-PHASE-5-PLAN.md`, `STAGE-C-PHASE-5.md`) — resolved two issues found in recent Stage C work, user-approved via all six gates ("proceed as recommended"). (a) **Verification independence**: every compat-register entry ever marked `status: verified` (11, across Phases 2-4) had been verified by the same session that implemented the feature, not an independently-dispatched `compat-differential-tester`. Amended `09-compatibility-system.md` §9.6 with a claim-strength-tiered process (new `status: self-verified` for real-but-non-independent evidence; first-time promotion to `verified` now requires an actual separate agent dispatch); relabelled the 11 existing entries honestly. (b) **`depth:` redesign**: `ledgerkit.query.ast.Depth` (a pure boolean exclusion predicate) removed from the selection AST — confirmed via a full source trace of every hledger command consuming a `Query` that `depth:` is always a report-display clipping/aggregation option, never a selection predicate (one exception found and replicated: `stats` genuinely excludes, a source-confirmed hledger quirk). Replaced with `ledgerkit.query.depth.DepthSpec` (`QueryPlan.depth`, general + custom `REGEX=N` + hledger's exact precedence/combination rules); old boolean node kept as Python-API-only `MaxAccountLevel`, no `-q` string syntax. Fixed `print` to correctly ignore `depth:` (previously wrongly excluded everything) and two further pre-existing bugs (`register`/`accounts` had silently excluded on the legacy `Query.depth` too). This phase's own new process was applied to itself: a genuinely separate `compat-differential-tester` dispatch independently re-verified every claim against the pinned binary on a new fixture (`tests/fixtures/depth.journal`) before `LK-COMPAT-QUERY-DEPTH-001`/`LK-COMPAT-QUERY-DEPTH-STATS-001`/`LK-COMPAT-QUERY-PRINT-INTEGRATION-001` were promoted to `status: verified`. 21 new/rewritten tests — 746 total, all passing. `tag:` query-matching, `cur:`, `PythonRegex`, `Query`-as-shim, and a standalone `--depth` CLI flag remain unscoped/deferred. **Phase 5A done**: `core-redefinition/22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md` (retros `STAGE-C-PHASE-5A-PLAN.md` + addendum, `STAGE-C-PHASE-5A.md`) — CodeCompass v1.0.0 installed (`pipx`) and configured against Ledgerkit's real repository. Found and corrected a real error in this phase's own planning pass: `CG-004` (spec-doc-to-spec-doc relation detection) was already fixed upstream (Phase 55b, 2026-09-17), contrary to the plan's original claim — independently re-verified, producing one genuine, non-trivial finding (`CC-LK-002`) rather than assumed. Used `codecompass enrich apply` (agent-facing, no API key configured) to enrich a real relation for the first time. Built a context packet for the genuine next phase (`tag:` query-term matching, G-CC-2) with every finding tagged to one of four provenance categories (`validation/codecompass/context-packets/tag-query-matching.md`) — researched and prepared, not implemented. Filed `CC-LK-002`/`CC-LK-003` (a real, minor `sqlite3`-CLI environment-assumption gap in the generated Skill). Exercised a real edit→re-sync→refresh cycle, confirming staleness detection works end to end. Documented the routine workflow (`04-codecompass-integration.md` §4.7) and added a real `CLAUDE.md` pointer section. Evaluation verdict (per G-CC-5's approved criteria, independently determined, not assumed from the historical baseline): **mixed, not a flat repeat** — the vendor/symbol axis is unchanged (LOW, 0 tracked dependencies), the doc-relation axis shows a genuine, verified improvement since the last Ledgerkit-side evaluation. Recommendation: keep as a routine, low-cost per-phase check going forward. No `ledgerkit/`/`tests/` behaviour changed; `tag:` query-term matching itself needs its own scoping/plan pass before implementation. **Phase 6 (`tag:` query-term matching) planning checkpoint done, implementation not started**: `core-redefinition/23-tag-query-matching-design.md` (retro `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md`) — first phase to use a new roadmap-objective → context-curation → design-document → human-approval → implementation process. A fresh, independent `context-curator` dispatch re-verified `tag:`'s semantics directly against the pinned hledger binary/source (not trusting the existing Phase 5A packet or brief 19 on faith) — confirmed the four propagation/inheritance rules and, newly, executable-confirmed the always-AND-never-OR combination rule (previously source-only evidence); found a genuinely new architectural fact brief 19 hadn't named (`accounts`' own posting-tag-stripping matching mode, source-confirmed to one call site); found Ledgerkit currently has no tag-inheritance computation at all (`Journal.declared_account_tags` is parsed but never consumed) — the real remaining gap, not just an AST node. The lead's own follow-up verification found one more fact the curator's report hadn't flagged: `matches_transaction`/`matches_posting` receive no `Journal` parameter today, bearing directly on inheritance-implementation cost. Design document distinguishes verified-external/existing-decision/proposed/unresolved throughout; two explicit unresolved questions (inheritance scope; `accounts`' matching mode), each with a stated recommendation, awaiting human approval before any implementation. Zero new CodeCompass findings filed — checked against CodeCompass's own gap register first, nothing novel. **Design document amended after review, same day, before implementation** — found not yet ready for approval: the four A-D propagation rules did not constitute *complete* hledger 1.52.4 effective-tag semantics, omitting commodity-directive tag propagation (`hledger.1:3550-3556`) entirely. A design-review correction, not an implementation defect — no `ledgerkit/`/`tests/` code existed yet. Resolved by direct executable testing, not interpretation: a same-name/different-value precedence matrix run against the pinned binary found **no shadowing at all** between posting/account/commodity-sourced tags (all remain simultaneously matchable), contradicting a literal reading of the manual's "posting tags override account tags override commodity tags" wording — the executable result, not the manual's prose, is now the documented basis. Also traced precisely why account-tag inheritance had already worked correctly in the original document's own tests despite a `False` library default: `auto_posting_tags_` is `True` for every CLI command except `print --output-format=beancount`. Amended: Option A (§9.1) redefined as genuinely complete (four sources); the evaluator-API recommendation softened from a required positional `Journal` parameter to backward-compatible alternatives; the `accounts`-command recommendation reversed (now: replicate hledger's mode, not diverge); new helpers default to private. Confirmed Ledgerkit currently has no commodity-tag storage/parsing substrate at all (`_strip_directive_comment` discards commodity directive comments outright) — a second, distinct gap alongside the already-known missing account-inheritance computation. **Small final correction pass, same day**: found the prior amendment's own `accounts tag:X` finding was still incomplete — stated as "account-inherited tags only" when the actual rule (verified live) is a four-way split: transaction-level and account-inherited tags visible, posting-own and commodity-propagated tags not, since `postingAllTags` (what query matching actually reads) unconditionally re-adds a transaction's own tags regardless of `accounts`' own stripping. Corrected transaction-level matching's stated rule to "own tags directly, OR any posting's effective tags" (sourced to `transactionAllTags`), not "only through its postings." Fixed a real Python error in the evaluator-API recommendation (a keyword-only parameter with no default is still mandatory on every call, contrary to what was claimed) — corrected to `journal: Journal | None = None` as the leading backward-compatible candidate. Resolved the commodity-tag substrate's scope question: in scope for this same phase, not a prerequisite sub-phase. Approval list shortened from five items to two (inheritance scope; `accounts` command mode) — the rest now have stated, overridable defaults. Still stopped for human review — amended §17 is the current approval list. **Phase 6 implementation plan done** (`core-redefinition/24-tag-query-matching-implementation-plan.md`) — resolved the one thing the design left open (evaluator-API shape: `journal: Journal | None = None`), turned the approved design into a file-by-file work list for a fresh implementing agent. **Phase 6 implementation done, independent verification pending**: `tag:NAME[=REGEX]` now implemented end to end by a fresh coding agent per this project's design → plan → implement → verify process (retro `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md`) — new `Journal.declared_commodity_tags` substrate, `ledgerkit/tags.py`'s private `_inherited_account_tags`/`_commodity_tags`/`_effective_tags`/`_accounts_effective_tags`, `ledgerkit.query.ast.Tag`, `_build_tag` parser rule, `matches_transaction`/`matches_posting`'s new `journal` parameter, `accounts`' own narrower tag-visibility dispatch. **Phase 6 `[DONE]`** (user-confirmed 2026-09-25): implementation (`0523426`/`fa05bbc`) and independent verification (`fe9dfe5`) both complete; closeout reconciliation `5887ea8`, `[DONE]` closeout in this same commit. A genuinely separate `compat-differential-tester` dispatch (Stage C Phase 5's own verification-independence process, `09-compatibility-system.md` §9.6) re-checked all 6 new compat-register entries against the pinned hledger 1.52.4 binary on freshly built fixtures, independent of the implementing session's own. 5 promoted to `status: verified` (`LK-COMPAT-QUERY-TAG-COMBINE-001`, `-INHERIT-001` including a dedicated re-check of the no-shadowing/union finding, `-COMMODITY-001`, `-ACCOUNTS-001`, `LK-COMPAT-PARSER-TAG-COMMODITY-001`). One real, pre-existing divergence found and deliberately left unresolved rather than folded into this phase or papered over: `tag:NAME=` (an empty value pattern) — hledger rejects an empty regex at parse time, Ledgerkit currently accepts and matches it; confirmed not `tag:`-specific (same gap for `acct:`/`desc:`) — filed as `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`, `LK-COMPAT-QUERY-TAG-001` itself correctly remains `status: proposed` for this one false claim, every other claim in it independently re-confirmed; not a Phase 6 blocker. `dev-docs/hledger-compatibility.md` updated accordingly. 827 tests passing throughout; no `ledgerkit/`/`tests/` behaviour changed by this closeout. **Remaining Stage C backlog** (Stage C itself remains `[IN PROGRESS]`, not `[DONE]`) — next priorities, in order: (1) scope the cross-cutting empty-regex compatibility fix (`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`, affects `acct:`/`desc:`/`tag:` alike, root cause `ledgerkit.query.regex.compile_hledger_regex`); (2) converge the legacy public `Query` pathway toward the query-AST/compatibility-shim architecture; (3) explicitly resolve the planned `PythonRegex` extension syntax (implement, defer with a stated reason, or drop). Non-blocking follow-on items, unscoped unless separately promoted: `cur:` (currency/commodity query term), hledger's smart/period date expressions, a standalone `--depth`/`-N` CLI flag. **Phase 7 (empty-regex-pattern rejection) planning checkpoint done, implementation not started**: `core-redefinition/26-query-regex-empty-pattern-design.md` (retro `dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-PLAN.md`) — resolves the first Phase 6 backlog item. An independent `compat-differential-tester` dispatch (`core-redefinition/25-query-regex-empty-pattern-matrix.md`) settled the key scoping question live against the pinned binary: hledger rejects only the literal empty pattern string, not any pattern whose semantics merely admit an empty match (`.*`/`a*`/`^$`/`()` are all accepted) — a narrow, fully-characterised, one-function fix (`ledgerkit.query.regex.validate_hledger_regex`), reusing the existing public `UnsupportedRegexConstructError` with no new exception class and no `api-spec.md` signature change. A misdirected `context-curator` dispatch (asked to do general research outside its actual charter) correctly self-refused rather than overstepping — re-routed to `compat-differential-tester` plus direct lead-performed source auditing. **Design amended, same day, before implementation — a targeted correction pass, not a re-scope**: (1) the proposed error message was `tag:`-specific advice baked into a prefix-agnostic shared validator — made fully generic; (2) "no public API change" was inaccurate — signatures/exception type are unchanged, but documented accepted-input *behaviour* changes, correctly framed as a backward-compatible compatibility/correctness fix requiring an `api-spec.md` update, not skipped; (3) the separately-discovered empty-alternation-branch divergence (`(|)` etc.) is now actually filed (`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`), scoped to what's verified on both sides, not left as an informal note; (4) `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`'s eventual resolution corrected to a rename-and-reclassify (new `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` entry) rather than an in-place `kind:` flip. The narrow `pattern == ""` fix itself is unchanged. **Design approved; implemented, independent verification pending**: `ledgerkit.query.regex.validate_hledger_regex` gained one check (`pattern == ""`, raising the existing `UnsupportedRegexConstructError` with a fully generic message — no `tag:`-specific advice, per the amended design) — the single shared chokepoint meant zero changes to any call site. Documented accurately as a **breaking, not backward-compatible**, correction made pre-`1.0.0` (still `1.0.0.dev1`) — `dev-docs/versioning.md` gained a new general "Breaking changes during the `1.0.0.dev1` pre-release" policy section; no version bump invented, per the existing process. The compat-register schema gained a general-purpose resolution-lifecycle mechanism (`dev-docs/compat-register/schema.md`, `09-compatibility-system.md` §9.7): resolving an `unexplained_mismatch` entry now creates a new, settled-`kind` entry (`resolves:` back-link) rather than editing the mismatch entry's `kind:` in place, and the original stays as retained history (`resolved_into:`/`resolved_date:`), moved from `UNEXPLAINED.md`'s "Open entries" to a new "Resolved entries" table — not applied to `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` yet, deliberately deferred until independent verification lands. Also corrected: `implementation`/`tests` may legitimately be empty for `unexplained_mismatch` entries, not only `unsupported` ones. 17 new tests (844 total, up from 827) covering `acct:`/`desc:`/`tag:`/`tag:NAME=`/`depth:=N`/`not:acct:` rejection, the CLI's existing error convention, and explicit regression guards that `.*`/`a*`/`^$`/`()` remain accepted. `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` untouched, still out of scope. Retro: `dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-IMPLEMENTATION.md`. **Independently verified**: a genuinely separate `compat-differential-tester` dispatch (§9.6) confirmed the fix on a fresh fixture — `acct:`/`desc:`/bare `tag:`/`tag:NAME=`/`depth:=N` all now reject identically on both hledger and ledgerkit (including under `not:`), with no overshoot (`.*`/`a*`/`^$`/`()` confirmed still accepted by both). Register resolution mechanism exercised for the first time: `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` created (`resolves: LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`, `status: verified`); the original mismatch entry retained untouched as history (`resolved_into:` added) and moved to `UNEXPLAINED.md`'s "Resolved entries"; `LK-COMPAT-QUERY-TAG-001`'s corrected claim promoted to `status: verified`; `LK-COMPAT-QUERY-ACCT-001`/`DESC-001`/`DEPTH-001` each gained an evidence note (no status change). `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` untouched, still open, still out of scope. Phase 7 is implementation-and-verification-complete — `[DONE]` remains the user's own call. **Phase 8 (`Query`-as-compatibility-shim convergence) planning checkpoint done, implementation not started**: `core-redefinition/27-query-shim-convergence-design.md` (retro `dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md`) — resolves Phase 6's second backlog item. Not a new architectural direction: `07-query-regex.md` §7.2 already specified, at Core-redefinition planning time, that the legacy `ledgerkit.models.Query` dataclass should become a compatibility constructor compiling to the `QueryNode`/`QueryPlan` AST rather than the separate, ad hoc, non-`HledgerRegex`-validated matcher (`reports.py`'s `_posting_matches`/`_matches_pattern`) it still uses today. Key de-risking finding: the one known external consumer, `ledgerkit-editor`, never calls into Ledgerkit's own `Query`-matching code at all (`15-editor-compat-inventory.md` — it uses `Query` only as a plain data container, matched by its own independent logic), and Ledgerkit's own test suite's `Query(...)` usages use no `HledgerRegex`-excluded construct, confirmed by direct grep. Found and flagged a real correctness trap before implementation: `ledgerkit.query.ast.DateSpan.end` is exclusive (matching real hledger `date:` semantics) while `Query.date_to` is inclusive — a naive translation would silently exclude transactions dated exactly `date_to`; the design specifies the correct `+1 day` translation and a named required regression test. **Design amended, same day, before implementation — a design-review correction pass, not a re-scope.** The original "empty blast radius" claim was incomplete: it checked direct `Query(...)` test construction only, missing that `Journal.balance`/`.register`'s deprecated `accounts=[...]` parameter (2+ accounts) internally synthesizes a `Query.account` pattern using `(?:...)` non-capturing groups — an excluded `HledgerRegex` construct, with zero existing test coverage to have caught the regression. Redesigned to build an `Or(...)` AST directly instead. Three further gaps fixed: `balance_from_spec`'s own separate filter still needs `_matches_pattern` (retained, refactored to be `HledgerRegex`-backed, not retired); `stats(query=...)` silently ignores `account`/`not_account` today (a pre-existing `TODO`) — full convergence now closes this as an explicit, disclosed correction, not an incidental side effect; the proposed translator must validate patterns eagerly before constructing AST nodes (mirroring `_build_acct`'s own pattern), not rely on lazy evaluation-time validation that might never run. Also: the translator moves to a new `ledgerkit/query/compat.py` module, not `models.py` (avoiding a real circular import), and the inclusive-to-exclusive date translation is corrected for the `datetime.date.max` overflow edge case. Blast-radius wording corrected from "empty" to the narrower, accurate conclusion: no external consumer affected, but multiple internal/public paths needed explicit migration handling. Approval gate grew from three items to six. **Design amended a second time, same day — another design-review correction pass.** Found by building an actual per-consumer inventory (§5.3, new) rather than trusting the first pass's own completeness claim: `Journal.to_dataframe(query=...)` was missed entirely by both prior passes — it calls `_posting_matches` directly, a live public method that retiring `_posting_matches` would have broken outright; now migrated to the same `_query_to_ast`/`matches_posting` path as everything else. The first pass's own `accounts=[...]` fix had a second bug: zero accounts fell through to the many-accounts branch, producing `Or(())` — an empty OR that matches *nothing*, the opposite of "no filter"; all three cases (zero/one/many) are now handled explicitly. `balance_from_spec`'s **outer** query (not just `ReportSection`) also now converges onto the canonical engine — leaving `ReportSection.accounts`/`.exclude` as the **one** genuinely separate filtering construct left in the codebase, not a whole function's worth of exceptions. §5.2 now states all six intentional behaviour changes explicitly instead of an outdated "no observable change beyond regex strictness" claim. Approval gate (§12) restated with an explicit recommended choice for every item — only regex strictness (Option A) remains a genuinely blocking decision. Core direction unchanged throughout. **Phase 8 approved (Option A regex strictness, the `stats` correction, the `ReportSection`-scope boundary, and `QueryParseError` reuse all confirmed) and implemented, independent verification pending**: a fresh coding agent converged all seven `Query`-shaped filtering call sites (`reports.balance`/`register`/`accounts`/`stats`, `balance_from_spec`'s outer query, `Journal.to_dataframe`, and the deprecated `accounts=[...]` shim's zero/one/many cases) onto a new `ledgerkit/query/compat.py` translator, retiring `reports._posting_matches` entirely (zero remaining callers, confirmed by grep and a dedicated test) while retaining `_matches_pattern` — refactored to be `HledgerRegex`-backed — as the one deliberately separate construct for `ReportSection.accounts`/`.exclude`. All six disclosed, intentional breaking changes from the design's §5.2 landed as specified, including the `stats` account/not_account correction and the `datetime.date.max` overflow fix. 53 new/rewritten tests (897 total, up from 844) all passing. **Independently verified**: a genuinely separate `compat-differential-tester` dispatch confirmed all eight of the design's highest-risk claims on a fresh fixture — `Query`-vs-`-q` parity (including identical rejection of excluded constructs/empty patterns) for `balance`/`register`/`accounts`; `stats`'s genuinely new account/not_account narrowing (matching `-q "acct:..." stats` exactly); `balance_from_spec`/`ReportSection`'s independent strictness; `to_dataframe`'s eager validation against an empty journal; and, most importantly, the deprecated `accounts=[...]` shim's zero/one/many cases (`accounts=[]` confirmed identical to no filter, not `Or(())`) — plus the `date.max` edge case and ordinary inclusive `date_to`. No discrepancies found. `LK-COMPAT-QUERY-SHIM-001` promoted `proposed` → `status: verified` by the independent dispatch itself. Phase 8 is now implementation-and-verification-complete — `[DONE]` remains the user's own call. Retro: `dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md`. **Post-verification correction, same day**: a further review of `LK-COMPAT-QUERY-SHIM-001`'s own text (not a code or behaviour change, and not caught by the independent verification dispatch above) found item 6's `reason:` line overclaimed — it said public behaviour was "preserved for every input the wrapper could previously accept without raising," but a single-account value using a Python-only regex construct outside `HledgerRegex` (e.g. `accounts=[r"\d+"]`) previously reached the old permissive matcher and was accepted; under Option A it now intentionally raises `QueryParseError`, same as every other `Query` field. Corrected the compat-register entry, the design document (§5.2 item 6), and `dev-docs/api-spec.md`'s `accounts=[...]` note to the accurate, narrower claim: `accounts=[]` stays no-filter, an ordinary `HledgerRegex`-portable single-account pattern is unchanged, a Python-only single-account regex now intentionally rejects, and two-or-more accounts retain their OR-matching behaviour via the `Or(...)` AST. A second, genuinely separate `compat-differential-tester` dispatch independently re-verified all four corrected-claim cases (zero/ordinary-single/Python-only-single/multiple) directly against Python-level calls (no hledger-binary equivalent applies to this internal-only parameter) — confirmed exactly as stated, no mismatch found; `status: verified` stands on the corrected, narrower claim. Two regression tests the re-verification found missing were added (`test_balance`/`test_register_one_account_excluded_construct_now_raises`). 899 tests total, all passing (up from 897) — no `ledgerkit/` behaviour changed by this correction, documentation/compat-register/test-coverage only. No remaining unexplained mismatch for this phase. Stage C itself remains `[IN PROGRESS]`; Phase 8 remains not marked `[DONE]` — that stays the user's own explicit call. | `core-redefinition/04`, `05`, `06`, `07`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27` |
| D | Reporting — shared primitives, structured output, render/semantics separation | `[PLANNED]` | `core-redefinition/06` §6.1 |
| E | Accounting semantics — prices, costs, valuation, conversion, account types, virtual postings, assertions | `[PLANNED]` | `core-redefinition/08` |
| F | Investment semantics — lots, cost basis, acquisition/disposal, gains/losses | `[PLANNED]` | `core-redefinition/08` |
| G | Generated/transformative behaviour — periodic transactions, auto postings, forecasting, rewrite/close | `[PLANNED]` | `core-redefinition/08` |
| H | Compatibility and identity — complete register, documented divergences/extensions, drive unexplained mismatches to zero | `[PLANNED]` | `core-redefinition/09` |
| I | Core 1.0 — stable API, performance/reliability, blank-slate docs, independent release audit | `[PLANNED]` | `core-redefinition/12` §12.5 |

---

## Deciding What Goes Into a Milestone or Stage

Before starting a new milestone or Stage, the user specifies the scope
(or confirms a Stage's plan). Claude then:
1. Confirms the scope against `dev-docs/hledger-compatibility.md` and,
   from Stage A onward, the compatibility register (`dev-docs/compat-register/`)
2. For a Stage: confirms any relevant human-decision gate in
   `dev-docs/planning/core-redefinition/14-human-decision-gates.md` is
   resolved before implementation starts
3. Updates this file to move the item from `[PLANNED]` to `[IN PROGRESS]`
4. Implements, tests, and updates docs in the same response
5. Updates this file to `[DONE]` **only when the user explicitly confirms the
   milestone/Stage phase is complete**, and adds a `CHANGELOG.md` entry at
   that point
6. Authors a retro report (`dev-docs/retros/<STAGE-OR-MILESTONE>[-PHASE-K].md`,
   per `CLAUDE.md`'s Retro Reports section and `dev-docs/retros/README.md`)
   **at the end of every phase**, not only when the whole milestone/Stage
   reaches `[DONE]` — a milestone/Stage delivered across several phases
   gets several retros, one per phase, matching `release-phase-auditor`'s
   own per-phase cadence
