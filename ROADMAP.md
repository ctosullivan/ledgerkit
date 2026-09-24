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
| C | Query system — parser/AST, hledger query semantics, Python `re` extension, CLI/report routing | `[IN PROGRESS]` — Phase 1 done: `hledger-researcher`'s semantics brief (`core-redefinition/17-query-semantics-brief.md`) plus a standalone, tested `ledgerkit/query/` subpackage (AST, `HledgerRegex`-subset validation, parser, evaluator) implementing `acct:`/`desc:`/`date:`(simple)/`depth:`/`status:`/`not:`. Not yet wired into `reports.py`/`cli.py`/`Query`; `tag:`/`cur:`/smart-dates/`PythonRegex` extension deferred. 7 compat-register entries added, all `status: proposed`. **Phase 2 done**: CodeCompass-assisted query/report/CLI integration (`core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md`, retro `dev-docs/retros/STAGE-C-PHASE-2.md`). `-q`/`--query` wired into `balance`/`register`/`accounts`/`stats` via a private, internal-only `reports._query_ast` parameter (no public API change). Differential-verified against the pinned hledger 1.52.4 binary; found and fixed two real CLI defects (EC-016) and corrected a Stage C Phase 1 misclassification (`LK-COMPAT-QUERY-DEPTH-001`, now `intentional_divergence`, EC-017). Ledgerkit's own first-ever real use of the `codecompass` CLI against its live repo, producing the project's first `CC-LK-NNN` finding (`validation/codecompass/findings/CC-LK-001`) — recommendation: not yet warranted as a mandatory workflow step (consistent LOW advantage, six data points across both usage directions). **Phase 3 done**: `-q` wired into `print` too (retro `dev-docs/retros/STAGE-C-PHASE-3.md`) — a matching transaction is shown whole, differential-verified against hledger's own `print` behaviour (`LK-COMPAT-QUERY-PRINT-INTEGRATION-001`). Only `check` remains unwired (by design). **Phase 4 done**: tag data model — parsing/storage only, not the `tag:` query term (retro `dev-docs/retros/STAGE-C-PHASE-4.md`). Split from `tag:` query work mid-phase by explicit user choice, after `hledger-researcher` briefs (`core-redefinition/19-tag-query-semantics-brief.md`, `20-tag-parsing-syntax-brief.md`) showed no tag data model existed at all. New `ledgerkit/tags.py` module (`parse_tags`, `effective_date`/`effective_date2`); new fields `Posting.tags`/`date_override`/`date2_override`, `Transaction.tags`, `Journal.declared_account_tags` (all user-confirmed via `AskUserQuestion` before touching `dev-docs/api-spec.md`); also fixed a real pre-existing gap where `account` directive comments were discarded entirely. Differential-verified against the pinned hledger 1.52.4 binary; 4 new compat-register entries, all `status: verified`. `tag:`/`cur:`/`PythonRegex`/`Query`-as-shim query-matching work untouched — next phase not yet scoped. **Phase 5 done**: `core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md` (retros `dev-docs/retros/STAGE-C-PHASE-5-PLAN.md`, `STAGE-C-PHASE-5.md`) — resolved two issues found in recent Stage C work, user-approved via all six gates ("proceed as recommended"). (a) **Verification independence**: every compat-register entry ever marked `status: verified` (11, across Phases 2-4) had been verified by the same session that implemented the feature, not an independently-dispatched `compat-differential-tester`. Amended `09-compatibility-system.md` §9.6 with a claim-strength-tiered process (new `status: self-verified` for real-but-non-independent evidence; first-time promotion to `verified` now requires an actual separate agent dispatch); relabelled the 11 existing entries honestly. (b) **`depth:` redesign**: `ledgerkit.query.ast.Depth` (a pure boolean exclusion predicate) removed from the selection AST — confirmed via a full source trace of every hledger command consuming a `Query` that `depth:` is always a report-display clipping/aggregation option, never a selection predicate (one exception found and replicated: `stats` genuinely excludes, a source-confirmed hledger quirk). Replaced with `ledgerkit.query.depth.DepthSpec` (`QueryPlan.depth`, general + custom `REGEX=N` + hledger's exact precedence/combination rules); old boolean node kept as Python-API-only `MaxAccountLevel`, no `-q` string syntax. Fixed `print` to correctly ignore `depth:` (previously wrongly excluded everything) and two further pre-existing bugs (`register`/`accounts` had silently excluded on the legacy `Query.depth` too). This phase's own new process was applied to itself: a genuinely separate `compat-differential-tester` dispatch independently re-verified every claim against the pinned binary on a new fixture (`tests/fixtures/depth.journal`) before `LK-COMPAT-QUERY-DEPTH-001`/`LK-COMPAT-QUERY-DEPTH-STATS-001`/`LK-COMPAT-QUERY-PRINT-INTEGRATION-001` were promoted to `status: verified`. 21 new/rewritten tests — 746 total, all passing. `tag:` query-matching, `cur:`, `PythonRegex`, `Query`-as-shim, and a standalone `--depth` CLI flag remain unscoped/deferred. **Phase 5A done**: `core-redefinition/22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md` (retros `STAGE-C-PHASE-5A-PLAN.md` + addendum, `STAGE-C-PHASE-5A.md`) — CodeCompass v1.0.0 installed (`pipx`) and configured against Ledgerkit's real repository. Found and corrected a real error in this phase's own planning pass: `CG-004` (spec-doc-to-spec-doc relation detection) was already fixed upstream (Phase 55b, 2026-09-17), contrary to the plan's original claim — independently re-verified, producing one genuine, non-trivial finding (`CC-LK-002`) rather than assumed. Used `codecompass enrich apply` (agent-facing, no API key configured) to enrich a real relation for the first time. Built a context packet for the genuine next phase (`tag:` query-term matching, G-CC-2) with every finding tagged to one of four provenance categories (`validation/codecompass/context-packets/tag-query-matching.md`) — researched and prepared, not implemented. Filed `CC-LK-002`/`CC-LK-003` (a real, minor `sqlite3`-CLI environment-assumption gap in the generated Skill). Exercised a real edit→re-sync→refresh cycle, confirming staleness detection works end to end. Documented the routine workflow (`04-codecompass-integration.md` §4.7) and added a real `CLAUDE.md` pointer section. Evaluation verdict (per G-CC-5's approved criteria, independently determined, not assumed from the historical baseline): **mixed, not a flat repeat** — the vendor/symbol axis is unchanged (LOW, 0 tracked dependencies), the doc-relation axis shows a genuine, verified improvement since the last Ledgerkit-side evaluation. Recommendation: keep as a routine, low-cost per-phase check going forward. No `ledgerkit/`/`tests/` behaviour changed; `tag:` query-term matching itself needs its own scoping/plan pass before implementation. | `core-redefinition/04`, `05`, `06`, `07`, `16`, `17`, `18`, `19`, `20`, `21`, `22` |
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
