# 6. Core architecture plan

## 6.1 What stays true from today's architecture

`dev-docs/architecture.md`'s pipeline (`loader → parser → models →
commodity_style → checks → reports → cli`) and its design principles
("each module imports only from modules below it", "reports don't print",
"no global mutable state") already satisfy most of Core's structural
requirements. This plan **extends** that pipeline rather than replacing it.

```
Journal file(s)
      │
  [ loader.py ]        (unchanged responsibility)
      │
  [ parser.py ]         (unchanged responsibility; gains: retain lot/cost
      │                  data instead of discarding it — prerequisite for
      │                  Stage F, see 08-accounting-semantics-roadmap.md)
      │
  [ models.py ]          (unchanged; gains accounting-semantics types as
      │                   Stage E/F land — Price/Cost/Lot/Valuation records)
      │
  [ query/ ]  ← NEW      query text → AST → semantic evaluation
      │                  (07-query-regex.md)
      │
  [ commodity_style.py ] (unchanged)
      │
  [ checks.py ]          (unchanged responsibility; gains new checks as
      │                   Stage E semantics land — e.g. valuation-consistency)
      │
  [ reports.py ]         (unchanged responsibility; consumes query/ instead
      │                   of matching Query fields ad hoc per report)
      │
  [ cli.py ]             (unchanged responsibility; routes filter flags
      │                   through query/ instead of building Query directly)
      │
  [ _pandas_compat.py ]  (unchanged — optional adapter boundary)
```

New top-level concern, **not a pipeline stage**, sitting alongside the
above: the **compatibility register** (`dev-docs/compat-register/`,
`09-compatibility-system.md`) — data, not code, consulted by
`hledger-researcher`/`compat-differential-tester`/`docs-maintainer`, not
imported by `ledgerkit/` itself.

## 6.2 Package boundary: one package, not `ledgerkit-core` + consumers

**Decision: keep a single `ledgerkit` package.** No evidence justifies a
split:

- Zero mandatory runtime dependencies today; the "Core must not include
  MCP/DuckDB/pandas-mandatory/ML/GUI/web-server" boundary is already true
  by construction, not something a package split is needed to enforce.
- `ledgerkit-editor` already imports the single `ledgerkit` package
  successfully — there's no packaging friction motivating a split.
- A split adds real cost now (two release cadences, two version numbers to
  keep in sync, duplicated CI) for a boundary that can instead be enforced
  by **convention + a lint/CI check**: a module inside `ledgerkit/` may not
  import `pandas`, `duckdb`, any MCP/server framework, or any GUI toolkit
  except through the existing lazy-import adapter pattern
  `_pandas_compat.py` already establishes. Add this as an explicit CI
  check (a simple import-graph assertion) at Stage A, rather than a
  packaging boundary.
- Revisit only if a concrete future adapter (DuckDB, MCP) needs a release
  cadence genuinely decoupled from Core's — not speculatively now.

## 6.3 Module-by-module plan for the areas the task calls out

| Task's Core area | Current state | Plan |
|---|---|---|
| Journal/accounting model | `models.py`, solid | Extend with `Cost`, `Lot`, `PriceGraph`/valuation types as Stage E/F land (`08-...md`). No structural change needed now — **confirmed** by Stage B Phase 2's review (`16-model-review.md`), with two guardrails recorded there: account-type data must be added as a new field alongside `declared_accounts`, never by changing its `list[str]` shape (`ledgerkit-editor` depends on that shape); new `Posting`/`Transaction` fields must make a deliberate `compare=` choice, matching the existing `source_line`/`raw_text`/`inline_comment` precedent. |
| Parser and writer | `parser.py`, `writer.py`, solid | Parser must **stop discarding** lot annotation data (`{cost}`, `[date]`, `(label)`) — currently parsed and thrown away (`dev-docs/hledger-compatibility.md`, "Lot annotations... discarded (not stored v1)"). This is a concrete, already-identified prerequisite for Stage F, not new scope. |
| Source locations/diagnostics | `SourceSpan`, `source_line`, already present | No structural change; extend to query/report layers for error messages that cite source position. |
| Query AST and semantics | Does not exist — `Query` dataclass with substring/regex matching only | New `ledgerkit/query/` subpackage: `ast.py` (typed nodes), `parser.py` (query text → AST), `eval.py` (AST → predicate over `Transaction`/`Posting`). See `07-query-regex.md`. |
| Compatibility regex handling | Plain `re.search`, undocumented semantics gap vs hledger's regex-tdfa | `ledgerkit/query/regex.py`: `HledgerRegex` / `PythonRegex`. See `07-query-regex.md`. |
| Accounting calculations | Balance/autobalance only | Stage E (`08-...md`): prices, costs, valuation, conversion. |
| Commodities/prices | `PriceDirective` parsed, **not applied** to reports | Stage E: apply stored prices to valuation reports (already flagged in `dev-docs/api-spec.md` as "in scope for v1... Milestone 2", never actually done — a genuine gap being formally rescheduled, not invented). |
| Costs and valuation | `cost_raw` stored as text only, never computed | Stage E. |
| Lot/investment semantics | Explicitly out of scope today | Stage F, once parser retains lot data (above). |
| Generated transactions | Periodic/auto-posting lines recognised and skipped with a `ParseWarning`, never expanded | Stage G. |
| Report engine | `reports.py`, already returns structured data | Extend to consume `query/` instead of the `Query` dataclass directly; keep the "reports don't print" principle unchanged. |
| Validation | `checks.py`, solid, tiered | Extend with new tiers as Stage E/F add invariants (e.g. a lot-consistency check) — same `CheckError` shape, no redesign. |
| Structured output / public Python API | Mostly present (`BalanceRow`, `RegisterRow`, `ReportSectionResult`) | Formalise as a stated stability contract (§6.4) rather than an implicit side effect. |

## 6.4 Public Python API stability

Today, `dev-docs/api-spec.md` documents the API but `CLAUDE.md`'s
Unauthorised Change Rule already protects it from silent changes. Stage I
(Core 1.0) should:

- Declare which of today's exports are the **stable v1 API surface**
  (everything currently re-exported from `ledgerkit/__init__.py`) versus
  what's still `[STUB]`/internal.
- Add the query AST's public entry points (`ledgerkit.query.parse`,
  or similar — exact naming decided at Stage C implementation time, not
  here) to that surface once they stabilise.
- Keep `dev-docs/versioning.md`'s existing SemVer rules unchanged — they
  already correctly define a breaking change as "removed/renamed public
  export" or "changed dataclass shape", which is exactly the discipline a
  stable Core API needs; no new versioning policy is required, just
  enforcement as the surface grows.

## 6.5 Ledgerkit Editor impact

**Verified** (Stage B Phase 1, `15-editor-compat-inventory.md` — supersedes
this section's earlier README-inference claim and refines
`14-human-decision-gates.md` G8): `ledgerkit-editor` actually imports and
uses at runtime `Query` (constructed with only `account`/`payee`/
`date_from`/`date_to`), `parse_string_lenient`, `checks.run_basic_checks`,
`commodity_style.CommodityStyle`, `parser.{ParseError,ParseWarning}`,
`load`, `writer.{transaction_to_text,journal_to_text}`. `models.
{Journal,Transaction,Posting}` are `TYPE_CHECKING`-only in its shipped
code (runtime only in its own test suite). **`EditorDocument` is not
actually used anywhere in `ledgerkit-editor`'s shipped code** — the
earlier assumption that it was is not supported by the source; see
`15-editor-compat-inventory.md` §15.3. `ledgerkit-editor` also
deliberately avoids importing `reports`'s private matching helpers,
duplicating that logic locally instead (§15.2) — full detail, including
exactly which call sites use which symbol, in `15-editor-compat-inventory.md`.

Concrete compatibility commitments for Stage B/C:

- `parse_string_lenient`, `writer.*`, `checks.run_basic_checks`,
  `commodity_style.CommodityStyle`, `parser.{ParseError,ParseWarning}`,
  `load`, `Query`'s `account`/`payee`/`date_from`/`date_to` constructor
  shape, and `Transaction`/`Posting`/`Amount` field shapes are treated as
  the frozen v1 API surface until Core 1.0 explicitly revises them with a
  documented breaking change and a major version bump. `EditorDocument` is
  not included in this list on `ledgerkit-editor`'s account specifically —
  no verified dependency on it exists today (it may still warrant frozen
  status for other reasons, e.g. its own `api-spec.md` stability
  commitment, just not this one).
- If/when the `Query` dataclass is superseded by the query AST
  (`07-query-regex.md`), the old `Query(account=..., date_from=..., ...)`
  constructor keeps working as a compatibility shim compiling down to the
  new AST, for at least one full major version, specifically so
  `ledgerkit-editor` (and any other consumer) is not forced to migrate in
  lockstep with Core.
- `EditorDocument`'s known v1 limitation (include directives silently
  ignored, per `dev-docs/api-spec.md`) is Stage B backlog, not blocking —
  see `12-roadmap-migration.md`.

## 6.6 Post-Core adapter layering (deferred, boundary only)

```
                 Ledgerkit Core
                      │
       ┌──────────────┼──────────────┬───────────────┐
       ▼              ▼              ▼               ▼
  ledgerkit CLI  ledgerkit-editor  future MCP    future DuckDB /
  (in-tree)      (external repo)   adapter       analytics adapter
       │              │              │               │
       └──────────────┴──────────────┴───────────────┘
                      ▼
                  applications
```

None of the right-hand boxes beyond the CLI and `ledgerkit-editor` are
built during Core development. The only architectural obligation Core
carries for them is: **don't design an API only the CLI could use.**
Concretely — every report function must be callable and useful from pure
Python without going through `cli.py`'s argument parsing or output
formatting (already true today; stays a stated invariant, checked by
`release-phase-auditor` at Core 1.0).
