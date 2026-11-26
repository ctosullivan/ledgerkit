<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-007 | date: 2026-10-02 -->
# Assertion: reports-cli-007

## Statement
The `register` CLI command prints one fixed-width line per RegisterRow: `DATE(10) DESC(21)  ACCOUNT(abbreviated,22)  AMOUNT(right 12)  RUNNING_BALANCE(right 13)`. Date and description columns are blanked (empty string) on every row after the first posting of a given (date, description) pair — i.e. only the first posting of each transaction shows the date/description. Account names longer than 20 chars are abbreviated by progressively shortening leading (non-last) colon-components to 2 then 1 character(s) (e.g. "equity:opening-balances" → "eq:opening-balances"). A zero running balance is shown as bare "0" with no commodity symbol.
## Kind
state_transformation
## Basis
directly_stated
## Evidence
cli.py register branch: `cur_key = (row.date, row.description); is_first = cur_key != prev_key; date_str = str(row.date) if is_first else ""`, format string `f"{date_str:10} {desc_str:21}  {acct_str:<22}  {amt_str}  {bal_str}"`; `_abbreviate_account()` shortens leading parts to 2 then 1 char if still over `max_width=20`. Confirmed by tests: `test_date_blank_on_continuation_rows` (6 of 12 lines start with a date, 6 are blank), `test_long_account_abbreviated` (`"eq:opening-balances"` present, `"equity:opening-balances"` absent), `test_running_balance_zero_shown_bare` (bare "0" trailing lines present).
## Justification
Direct line-by-line match between cli.py:52-62/396-421 and TestRegisterOutput.
## Examples
Two postings of the same "Rent" transaction on the same date print the date/description only on the first line.
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

Evidence-paths: [ledgerkit/cli.py:52-62, ledgerkit/cli.py:396-421, tests/test_cli/test_cli.py:260-288]
