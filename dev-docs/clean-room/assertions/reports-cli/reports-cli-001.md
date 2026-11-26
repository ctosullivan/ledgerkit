<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-001 | date: 2026-10-02 -->
# Assertion: reports-cli-001

## Statement
The ledgerkit CLI exposes exactly six subcommands, selected via a single required positional `command` argument: `balance`, `register`, `accounts`, `print`, `stats`, `check`. There are no argparse subparsers — all six share one flat flag set.
## Kind
definition
## Basis
directly_stated
## Evidence
`python -m ledgerkit --help` printed: `{balance,register,accounts,print,stats,check} [journal ...]` and `-h`/`--help` on `balance` produced the identical top-level usage text (not a per-subcommand help page), confirming `command` is an `argparse.ArgumentParser` positional with `choices=COMMANDS`, not a subparsers tree.

Evidence-paths: [ledgerkit/cli.py:23, ledgerkit/cli.py:126-130]

## Justification
`COMMANDS = ("balance", "register", "accounts", "print", "stats", "check")` (cli.py:23) is used directly as `choices=COMMANDS` on the `command` positional (cli.py:128); there is no `add_subparsers()` call anywhere in `_build_parser()`.
## Examples
`ledgerkit balance -f x.journal`, `ledgerkit check assertions -f x.journal`
## Counterexamples
None found — `python -m ledgerkit balance --help` does not produce balance-specific flag help, confirming no subcommand-level parser exists.
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
