# 1. Product-goal redefinition

## 1.1 Current state (verified against the live repository, 2026-09-12)

- `ledgerkit` v1.0.0 shipped to PyPI 2026-06-07; `main` currently sits at
  `1.0.0.dev1` mid-way through validating the TestPyPI trusted-publishing
  workflow (`CONTEXT.md`, `git log`) — an in-flight administrative task, not
  a design decision. 575 tests pass (`python -m unittest discover`).
- Zero mandatory runtime dependencies; `pandas` is an optional extra.
  Python 3.8–3.12.
- Pipeline: `loader → parser → models → commodity_style → checks → reports
  → cli` (`dev-docs/architecture.md`). Reports already return structured
  data, not printed strings — the CLI is a thin formatter. This is a good
  starting point for "separate accounting semantics from rendering"
  (Stage D of the new roadmap) — largely already true.
- Format coverage is deliberately partial: transactions, postings,
  multi-commodity balances, `P`/`alias`/`include`/`account`/`commodity`/
  `payee`/`tag`/`decimal-mark`/`Y`/`D`/`apply account` directives, balance
  assertions. Explicitly out of scope today: auto postings, periodic
  transactions, timeclock/timedot/CSV formats, virtual postings, lot
  price/cost-basis computation (annotations are parsed and *discarded*),
  multi-currency auto-conversion (`dev-docs/hledger-compatibility.md`).
- Filtering is one ad hoc `Query` dataclass (`account`/`not_account`/
  `payee`/`date_from`/`date_to`/`depth`, substring-or-regex matching) wired
  separately into each report function — exactly the "narrow ad-hoc
  filtering growth" the new goal asks to replace with a real query
  architecture.
- One real downstream consumer exists today: **`ledgerkit-editor`**
  (`https://github.com/ctosullivan/ledgerkit-editor`, MIT, sole author
  `ctosullivan`, Textual TUI), which imports `ledgerkit` **as an in-process
  Python library** (`EditorDocument`, `parse_string_lenient`, `writer`,
  `check_transaction_autobalanced`), not via CLI subprocess. It currently
  pins `ledgerkit==1.0.0.dev1`. This is the concrete "lightweight
  dependency for applications" case the new goal must keep serving — see
  §2 for why this specific consumption pattern (in-process import, not
  subprocess) is the crux of the licensing decision.
- Governance is already mature for a single-package project: `CLAUDE.md`
  (doc-sync rules, regex-documentation rule, unauthorised-change rule),
  `knowledge/{DECISIONS,ANTIPATTERNS,DOMAIN_RULES,EDGE_CASES}.md`,
  `dev-docs/{architecture,api-spec,hledger-compatibility,SYNC,versioning}.md`,
  milestone-archived `CHANGELOG.md`. This is a solid foundation to extend,
  not a gap to fill from scratch — Stage A of the new roadmap should graft
  onto it, not replace it.

## 1.2 New Core goal

> Ledgerkit Core is a deterministic, Python-native accounting and query
> engine that preserves a clearly defined hledger-compatible foundation
> while deliberately supporting documented Ledgerkit-native extensions and
> opinionated behaviour where Python or modern tooling provides a better
> design.

This is a **reframing**, not a rewrite trigger. Every already-implemented
feature keeps its behaviour; what changes is:

1. **The compatibility contract becomes explicit and classified**, instead
   of an implicit "we chose to support X, not Y" narrative scattered across
   `hledger-compatibility.md` and `knowledge/DECISIONS.md`. See
   `09-compatibility-system.md`.
2. **Divergences become named and intentional**, not incidental. Two
   already exist and are already documented informally — they become the
   first two compatibility-register entries (see
   `dev-docs/compat-register/examples/`):
   - alias rules do not propagate across `include` boundaries (a Ledgerkit
     parser-architecture consequence, `knowledge/DECISIONS.md` 2026-04-xx);
   - `include` glob matching uses Python's `glob.glob()` dot-file
     semantics, which differ from hledger's own glob exclusion rules
     (`hledger-compatibility.md`, "Dot-file glob behaviour").
3. **Extensions get a syntax boundary**, starting with regex
   (`07-query-regex.md`), so "this query is portable to real hledger" is a
   checkable property, not a hope.
4. **hledger stops being read only through its manual.** Source, tests, and
   the executable become first-class evidence sources, with the executable
   remaining the arbiter of "does this actually match" (§10).

## 1.3 Relationship to hledger

- hledger is the **primary accounting and compatibility reference** — not
  a spec to clone line-for-line, and not merely an inspiration credited in
  an acknowledgements section (the current framing in `README.md`).
- **hledger 1.52.x is the compatibility baseline** for the reasons in
  `09-compatibility-system.md` §1: it is hledger's actual current stable
  release line (`1.52.4`, published 2026-09-10, `prerelease: false`), it is
  what Ledgerkit's own docs already target, and hledger's own `1.99.x` line
  (`1.99.4`, 2026-09-11, `prerelease: true`) is pre-2.0 development —
  implementing against a moving target simultaneously with the baseline
  would mean chasing two specs at once for no present benefit.
- Architectural separation for a future `hledger-2` profile is planned
  (`06-core-architecture.md` §3) but **not built now** — one profile is
  sufficient until hledger 2.0 actually stabilises and a concrete
  compatibility need is demonstrated (YAGNI, per the task's own "do not
  implement multiple profiles prematurely" instruction).

## 1.4 Opinionated compatibility philosophy

Per-feature test, applied going forward (mirrors the task's ten planning
questions, condensed):

```
Is it foundational to representing/querying/reporting on ledger data?
        │
        ├─ no → not Core (adapter, or out of scope entirely)
        │
        └─ yes
             │
             Is hledger's behaviour the right behaviour to copy?
             │
             ├─ yes, and Python offers no better option
             │        → COMPATIBLE: match hledger exactly, verify against the executable
             │
             ├─ yes, but Python's stdlib/idiom does it better
             │  without breaking the portable subset
             │        → preserve the compatible surface, add an
             │          explicit EXTENDED capability alongside it
             │
             └─ no — hledger's behaviour is a historical accident,
                a Haskell-ism, or actively worse for Ledgerkit's use case
                      → INTENTIONAL_DIVERGENCE, documented, with the
                        reason recorded in the compat register
```

`UNSUPPORTED` is not a failure state — it is any hledger feature Ledgerkit
has deliberately not built yet (most of Stage E–G). `UNEXPLAINED_MISMATCH`
is the only state that should never be committed as final; see
`09-compatibility-system.md` §4.

## 1.5 Python-native differentiation

Concretely, where this redefinition changes near-term priorities versus
"implement more of hledger":

- A typed query AST + Python API (`07-query-regex.md`) instead of growing
  the `Query` dataclass's field list every time a new filter is needed.
- Structured, typed report results usable directly as Python objects
  (already mostly true — `BalanceRow`, `RegisterRow`, `ReportSectionResult`
  — this becomes a stated design principle rather than an accident of
  incremental development).
- An explicit, opt-in Python `re` extension surface for queries
  (lookarounds, named groups, backreferences) that hledger's regex engine
  does not offer, clearly separated from the portable hledger-compatible
  subset (`07-query-regex.md`).
- A public Python API stable enough to be `ledgerkit-editor`'s (and future
  consumers') dependency contract, not a side effect of whatever the CLI
  currently needs (`06-core-architecture.md` §4).

## 1.6 Explicit non-goals

- **Not** a line-for-line Python port of hledger's Haskell implementation.
  Understanding hledger's source is for extracting *intended semantics*,
  not for transliterating Haskell control flow into Python
  (`10-source-assisted-development.md`, and the over-copying risk in
  `13-risks.md`).
- **Not** 100% hledger CLI-surface parity. Core 1.0 is not defined as
  "every hledger command exists" (per the task's explicit instruction) —
  see the Core 1.0 success criteria in `12-roadmap-migration.md` §4.
- **Not** MCP server, DuckDB adapter, pandas/Polars/Arrow analytics
  expansion, ML transaction classification, anomaly detection,
  natural-language query compilation, notebook tooling, bank integrations,
  or an AI finance copilot, during Core development. These are explicitly
  deferred consumers layered on top of a stable Core API
  (`06-core-architecture.md` §5) — building them now, or shaping Core
  around their hypothetical needs now, is out of scope.
- **Not** an immediate `ledgerkit-core` package split. A single package
  with an enforced internal boundary is the starting position; splitting
  is revisited only if real packaging/dependency evidence demands it
  (`06-core-architecture.md` §2).
- **Not** simultaneous hledger-1.52 and hledger-2 compatibility profiles
  right now (§1.3 above).
