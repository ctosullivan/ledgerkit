<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-002 | date: 2026-10-02 -->
# Assertion: reports-cli-002

## Statement
The CLI's global flags are: `--version`, `-v`/`--verbose`, `-1` (one-line, stats only), `-o`/`--output-file FILE`, `-f`/`--file FILE` (repeatable), `-s`/`--strict`, `-I`/`--ignore-assertions`, `-q`/`--query TERMS`, `-c`/`--commodity-style STYLE` (repeatable). These apply uniformly regardless of which `command` is chosen (argparse does not scope them per-subcommand).
## Kind
definition
## Basis
directly_stated
## Evidence
`python -m ledgerkit --help` output: `-v, --verbose  Show more detailed output (stats: commodity names)`, `-1  Show a single tab-separated line of output (stats only)`, `-o, --output-file FILE  Write output to FILE instead of stdout`, `-f, --file FILE  Read data from FILE, or stdin if -. May be specified more than once.`, `-s, --strict  Enable strict mode...`, `-I, --ignore-assertions  Disable balance assertion checking`, `-q, --query TERMS  Filter using a query string...Applies to balance, register, accounts, stats, and print.`, `-c, --commodity-style STYLE  Override display style for a commodity...May be specified more than once.`
## Justification
Each flag is defined once on the top-level `ArgumentParser` in `_build_parser()` (cli.py:66-139); `-f`/`-c` use `action="append"`, confirming repeatability.
## Examples
`ledgerkit -f a.journal -f b.journal stats`; `ledgerkit -c '$1,000.00' -c '1.000,00 EUR' balance`
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
