<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
# Assertion: current-state-004

## Statement
The `ledgerkit` CLI's top-level `--help` currently lists exactly six subcommands as the positional `{...}` choice set, named exactly: `balance`, `register`, `accounts`, `print`, `stats`, `check`.

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command: `cd /home/cormac/projects/ledgerkit && python -m ledgerkit --help`
Exact relevant output:
```
usage: ledgerkit [-h] [--version] [-v] [-1] [-o FILE] [-f FILE] [-s] [-I]
                 [-q TERMS] [-c STYLE]
                 {balance,register,accounts,print,stats,check} [journal ...]

Plain-text accounting (hledger-compatible)

positional arguments:
  {balance,register,accounts,print,stats,check}
                        Report to run: balance, register, accounts, print,
                        stats, check
  journal               Journal file (shorthand for -f; all commands except
                        check), or check names (check command only)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         Show more detailed output (stats: commodity names)
  -1                    Show a single tab-separated line of output (stats
                        only)
  -o, --output-file FILE
                        Write output to FILE instead of stdout
  -f, --file FILE       Read data from FILE, or stdin if -. May be specified
                        more than once.
  -s, --strict          Enable strict mode: also check that accounts and
                        commodities are declared
  -I, --ignore-assertions
                        Disable balance assertion checking
  -q, --query TERMS     Filter using a query string (see ledgerkit.query),
                        e.g. 'acct:food date:2024'. Applies to balance,
                        register, accounts, stats, and print.
  -c, --commodity-style STYLE
                        Override display style for a commodity, e.g.
                        '$1,000.00' or '1.000,00 EUR'. May be specified more
                        than once.
```

No Evidence-paths — purely from a live command run.

## Justification
This is argparse's literal rendering of the registered positional choices; the string inside `{}` is the exhaustive, exact set of accepted first-token report names.
## Examples
`python -m ledgerkit balance sample.journal` and `python -m ledgerkit check` are both accepted first tokens per this listing.
## Counterexamples
not applicable
## Depends on
none
## Open questions
none
## Evidence-support state
supported
## Status
verified
## Supersedes
