<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-008 | date: 2026-10-02 -->
# Assertion: reports-cli-008

## Statement
The `accounts` CLI command prints the sorted, deduplicated list of account names, one per line, with no separator/zero-total convention — a query that matches nothing produces genuinely empty output (unlike `balance`, which always prints a separator and a total line even for zero matches).
## Kind
definition
## Basis
directly_stated
## Evidence
cli.py: `elif args.command == "accounts": for name in reports.accounts(...): print(name)` — a bare loop with no extra formatting. Test `test_multi_term_query` explicitly contrasts this with balance: "accounts' CLI output has no separator/zero-total convention (unlike balance) -- genuinely empty here" and asserts `out.strip() == ""`.
## Justification
Implementation is a trivial print loop (cli.py:423-425); the contrast with `balance`'s always-present separator/total is explicitly called out in the test comment and corroborated by reports-cli-005.
## Examples
`-q "acct:expenses status:*"` against filtered.journal (no expense postings on cleared transactions) → empty stdout, exit code 0.
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

Evidence-paths: [ledgerkit/cli.py:423-425, tests/test_cli/test_cli.py:431-440]
