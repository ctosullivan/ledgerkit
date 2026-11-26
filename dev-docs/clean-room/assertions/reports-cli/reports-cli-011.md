<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-011 | date: 2026-10-02 -->
# Assertion: reports-cli-011

## Statement
`reports.stats()` returns a `JournalStats` dataclass containing only deterministic journal data (transaction_count, date_range, txns_per_day, payee_count, account_count, account_depth, commodity_count, commodities, price_count, etc.); runtime stats (elapsed time, txns/s) are measured and formatted only by the CLI layer (`cli.py`), not stored in `JournalStats`. The CLI prints a multi-line labeled report by default, or -- with `-1` -- a single tab-separated line: `VERSION\tSOURCE_FILE\tELAPSED_s elapsed\tTXNS_PER_S txns/s`. With `-v`/`--verbose`, the "Commodities" line additionally lists commodity names in parentheses.
## Kind
definition
## Basis
directly_stated
## Evidence
`JournalStats` docstring: "Contains only deterministic journal data. Runtime stats (elapsed time, txns/s) are measured and formatted by the CLI layer, not stored here." cli.py's stats branch computes `elapsed = time.perf_counter() - _PROGRAM_START` and `txns_per_s` locally, then branches on `args.one_line` to print `"\t".join([__version__, s.source_file or "(none)", f"{elapsed_str} s elapsed", f"{txns_per_s:.0f} txns/s"])` versus 12 labeled lines (`Main file`, `Included files`, `Txns span`, `Last txn`, `Txns`, `Txns last 30 days`, `Txns last 7 days`, `Payees/descriptions`, `Accounts`, `Commodities`, `Market prices`, `Runtime stats`). `commodity_str` only lists names when `args.verbose and s.commodities`.

Review note (2026-10-03): the original Evidence text itemised the same 12 labeled lines but then miscounted them as "10 labeled lines" -- an internal arithmetic inconsistency within the assertion's own Evidence field (the list enumerated has 12 entries, not 10). Resolved by a live re-check: `python -m ledgerkit stats -f tests/fixtures/sample.journal` was run and produces exactly 12 printed lines in the non-`-1` branch, matching cli.py:478-489's 12 `print(...)` calls one-for-one. Corrected "10" to "12" above; no other field required a matching fix (Statement/Examples/Counterexamples never repeated the wrong count).
## Justification
Direct correspondence between JournalStats dataclass fields (reports.py:181-206), cli.py's stats branch (451-489), and the `--help` text for `-v`/`-1` ("stats: commodity names" / "stats only").
## Examples
`ledgerkit stats -1 -f sample.journal` -> e.g. `0.1.0\t/path/sample.journal\t0.003 s elapsed\t1667 txns/s`
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

Evidence-paths: [ledgerkit/reports.py:181-206, ledgerkit/cli.py:451-489, ledgerkit/cli.py:72-82]
