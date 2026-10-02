<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-005 | date: 2026-10-02 -->
# Assertion: reports-cli-005

## Statement
The `balance` CLI command's printed output format is: one line per (account, commodity) pair with the right-aligned formatted amount first and the account name second (only on the last row for that account), a dashed separator line sized to the widest amount/total string, then one line per nonzero commodity grand total (or a single bare "0" if every commodity nets to zero). Negative amounts are wrapped in ANSI red (`\033[31m...\033[0m`). Ordinary zero-net (account, commodity) rows are omitted — except a depth-0 `"..."` row, which is always shown unconditionally (`qty != 0 or acct == "..."`), regardless of its own net value. In an unfiltered, fully-balanced journal this collapsed total happens to be zero, but it is NOT "necessarily" zero in general: combined with an account-selecting `-q` filter, the depth-0 `"..."` row can net to a nonzero amount (the filtered subset need not itself balance) and is still shown via the same unconditional exception, not because of a zero-specific carve-out.
## Kind
state_transformation
## Basis
directly_stated
## Evidence
cli.py's balance branch builds `lines` filtering `qty != 0 or acct == "..."` (line 327), computes `col_w` from both amount strings and total strings, then for each row prints `f"{padded}  {acct}"` only on the last row index for that account (`acct_last_idx`), followed by `"-" * col_w` and either per-commodity totals or a bare `"0"`. Test evidence: `test_account_after_amount` (asserts `£` index < `assets` index), `test_separator_line_present` (`"----"` in output), `test_grand_total_zero_shown_bare` (bare `"0"` line present), `test_amount_format_negative` (`"£-5,000.00"` — commodity precedes the minus sign, not `-£5,000.00`).

Review note (2026-10-03): the original Statement claimed the depth-0 "..." row "necessarily nets to zero" as the stated reason hledger always shows it. This is false in general -- resolved by a live re-check, not just re-reading the cited test. `test_balance_query_depth_zero_shows_ellipsis_row` only exercises unfiltered `depth:0` against a fully-balanced journal, where the single collapsed bucket is trivially zero. Running `python -m ledgerkit balance -f tests/fixtures/filtered.journal -q "acct:food depth:0"` live produced a single nonzero `"..." = £159.00` row (the `acct:food` subset doesn't itself balance to zero), still printed under the exact same `qty != 0 or acct == "..."` condition -- confirming the real rule is "the `"..."` row is shown unconditionally, independent of its value," not "shown despite being zero." The Statement and this Evidence section have been corrected accordingly; Examples/Counterexamples below were checked and did not need correction (the `test_row_count`/`test_balance_query_depth_zero_shows_ellipsis_row` citations are both for the unfiltered case and remain accurate as narrow examples).
## Justification
Direct line-by-line correspondence between cli.py:305-394 and the TestBalanceOutput test class; the depth-0 unconditional-inclusion rule is directly readable from the `qty != 0 or acct == "..."` condition itself (line 327), independent of any particular journal's balance.
## Examples
Running `balance` on filtered.journal produces 6 account rows + separator + 1 bare "0" total line = 8 non-empty lines (`test_row_count`).
## Counterexamples
`-q depth:0` (unfiltered) collapses everything to a single `"..."` row that happens to net to zero but is still printed, unlike an ordinary zero-net account which is omitted (`test_balance_query_depth_zero_shows_ellipsis_row`). Additionally (live-confirmed this review, not covered by any cited test): `-q "acct:food depth:0"` against filtered.journal produces a single nonzero `"..." = £159.00` row -- proving the depth-0 exception is unconditional, not zero-specific.
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

Evidence-paths: [ledgerkit/cli.py:305-394, tests/test_cli/test_cli.py:198-229, tests/test_cli/test_cli.py:407-420]
