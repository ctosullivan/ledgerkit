<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-013 | date: 2026-10-02 -->
# Assertion: reports-cli-013

## Statement
`reports.balance_from_spec(journal, spec, query=None)` computes a structured, multi-section balance report (e.g. an income statement with an "Income" section marked `invert=True` and an "Expenses" section) driven by `ReportSpec`/`ReportSection` dataclasses, returning one `ReportSectionResult` per section (rows: dict[account, Decimal], subtotal: Decimal). This function is reachable from the Python API (`ledgerkit.balance_from_spec`, `ledgerkit.ReportSpec`, `ledgerkit.ReportSection`) but is NOT wired to any CLI subcommand — none of the six `COMMANDS` in cli.py invoke it.
## Kind
boundary
## Basis
directly_stated
## Evidence
reports.py defines `balance_from_spec()` (lines 600-696) with a full docstring describing the 7-step per-section algorithm (outer query → account include/exclude via OR logic → depth → aggregate → invert → ReportSectionResult). Tests exercise it purely via `ledgerkit.ReportSpec`/`ledgerkit.ReportSection`/`balance_from_spec` imports (test_reports.py:664-672, "All new public symbols must be importable from the top-level package"), never via `main()`/CLI argv. cli.py's `main()` dispatch only branches on `args.command in {"balance","register","accounts","print","stats"}` plus the separate `check` early-return — `balance_from_spec` is never imported or called in cli.py.
## Justification
Grep-equivalent manual read of cli.py confirms zero references to `balance_from_spec`, `ReportSpec`, or `ReportSection`; it is a Python-API-only, not CLI-exposed, report path.
## Examples
`ledgerkit.balance_from_spec(journal, ledgerkit.ReportSpec(name="Income Statement", sections=(ReportSection("Income", accounts=("income",), invert=True), ReportSection("Expenses", accounts=("expenses",)))))`
## Counterexamples
None
## Depends on
None
## Open questions
None
## Evidence-support state
supported
## Status
verified
## Supersedes
None

Evidence-paths: [ledgerkit/reports.py:600-696, ledgerkit/cli.py:1-508, tests/test_reports.py:664-672]
