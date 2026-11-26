<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-009 | date: 2026-10-02 -->
# Assertion: reports-cli-009

## Statement
The `print` CLI command prints each matching transaction as: a header line `DATE flag DESCRIPTION` (flag is `" * "` cleared, `" ! "` pending, else a single space) followed by one indented line per posting (`"    "` + account left-padded to 40 chars + formatted amount, or just the account if elided), then a blank line. `-q`/`--query` filtering on `print` matches whole transactions (if ANY posting matches, the WHOLE transaction — all its postings — is printed, not just the matching posting), and `print` deliberately ignores `depth:` entirely (neither filters nor clips), matching hledger's own print behaviour exactly.
## Kind
rule
## Basis
directly_stated
## Evidence
cli.py: `flag = " * " if txn.cleared else " ! " if txn.pending else " "`; posting line `f"    {posting.account:<40}  {amt_txt}"`. The `-q` wiring in `main()` explicitly comments: "print deliberately uses only query_ast, never query_depth, matching hledger's own print (which ignores depth: entirely...)". Test `test_print_query_filters_whole_transactions` filters on `acct:food` and asserts the OTHER posting on the matching transaction (`assets:bank:checking`) is also present; `test_print_ignores_depth_entirely` asserts `-q "depth:1" print` output is byte-identical to unfiltered print output, with full unclipped account names still present.
## Justification
Direct line-by-line match between cli.py:233-239/427-449 and the TestQueryFlag print-related tests.
## Examples
`-q "acct:food" print` on filtered.journal shows "Supermarket" and "Coffee" transactions in full (including their non-food posting), excludes "Opening balance" and "Rent".
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

Evidence-paths: [ledgerkit/cli.py:233-239, ledgerkit/cli.py:427-449, tests/test_cli/test_cli.py:496-554]
