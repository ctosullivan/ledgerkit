<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
<!-- reviewed-by: domain-skeptic | review-dispatch: cs-review-01 | review-date: 2026-10-03 -->
# Assertion: current-state-008

## Statement
Right now, running `python -m ledgerkit stats tests/fixtures/sample.journal` succeeds (exit code `0`, no traceback) and produces non-empty, well-formed tabular report output (e.g. `Txns : 5 (0.2 per day)`, `Accounts : 6 (depth 3)`, `Commodities : 1`). Running `python -m ledgerkit check -f tests/fixtures/sample.journal` also succeeds (exit code `0`, no traceback), but — unlike `stats` — it produces **no stdout output at all** on success; a passing `check` run is silent. Both facts together demonstrate the CLI's reporting/validation path is currently functional end-to-end for this journal, not merely that `--help` parses, but "non-empty output" is only true of `stats`, not of `check`.

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command 1: `cd /home/cormac/projects/ledgerkit && python -m ledgerkit stats tests/fixtures/sample.journal`
Exact output:
```
Main file           : /home/cormac/projects/ledgerkit/tests/fixtures/sample.journal
Included files      : 0
Txns span           : 2024-01-01 to 2024-01-20 (20 days)
Last txn            : 2024-01-20 (987 days ago)
Txns                : 5 (0.2 per day)
Txns last 30 days   : 0 (0.0 per day)
Txns last 7 days    : 0 (0.0 per day)
Payees/descriptions : 5
Accounts            : 6 (depth 3)
Commodities         : 1
Market prices       : 0
Runtime stats       : 0.02 s elapsed, 211 txns/s
```
Exit code: `0`

Command 2: `cd /home/cormac/projects/ledgerkit && python -m ledgerkit check -f tests/fixtures/sample.journal; echo "EXIT:$?"`
Exact output:
```
EXIT:0
```
(zero bytes of stdout before the `EXIT:0` echo — confirmed again with `-v` added, same empty-stdout/exit-0 result)

Note on invocation: `python -m ledgerkit check tests/fixtures/sample.journal` (journal path as a bare positional, no `-f`) does **not** run `check` against that file — per the top-level help text, the positional `journal` argument is read as a check name for the `check` subcommand specifically, not a file shorthand. That invocation instead fails with `ledgerkit: no journal file specified; use -f FILE or set $LEDGER_FILE` (exit `1`), because no journal was supplied via `-f`/`$LEDGER_FILE` and "tests/fixtures/sample.journal" was consumed as an (unmatched) check name. The file must be passed via `-f` for `check` to actually validate it.

No Evidence-paths — purely from live command runs against the repository's own `tests/fixtures/sample.journal`.

## Justification
The printed figures (txn counts, account counts, elapsed time, throughput) for `stats` are runtime-computed values that only appear if the loader, parser, and report-formatting code paths all executed without raising; their presence is direct evidence the `stats` reporting pipeline currently runs successfully. For `check`, exit code `0` with no exception is the only observable success signal — ledgerkit's `check` command, like a typical lint/validator, reports nothing on success and only produces output when a check fails; this was confirmed directly rather than assumed.
## Examples
`Accounts : 6 (depth 3)` and `Txns : 5 (0.2 per day)` are concrete computed values from the `stats` run above. `check -f tests/fixtures/sample.journal` exiting `0` with empty stdout is the concrete example of `check`'s silent-success behaviour.
## Counterexamples
`check`'s own success case is the counterexample to any reading of this assertion that would claim *both* subcommands "produce non-empty, well-formed tabular/report output" — only `stats` does; `check`'s successful output is empty by design.
## Depends on
none
## Open questions
none — the original open question ("which journal file produced this output... the exact invoking file path was not isolated") is resolved: re-running directly against `tests/fixtures/sample.journal` reproduces the same `stats` figures (txn/account/commodity counts), confirming that was the source journal; the "Runtime stats" line's elapsed-time/throughput values are expected to vary run-to-run since they measure wall-clock execution and are not claimed to be reproducible.
## Evidence-support state
supported
## Status
verified
## Supersedes
