<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
# Assertion: current-state-005

## Statement
Right now, running `python -m ledgerkit <subcommand> --help` for each of the six listed subcommands (`balance`, `register`, `accounts`, `print`, `stats`, `check`) prints byte-for-byte the same top-level usage/help text shown by `python -m ledgerkit --help` alone — there is no subcommand-specific `--help` output distinguishable from the top-level one.

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command: `cd /home/cormac/projects/ledgerkit && for cmd in balance register accounts print stats check; do echo "=== $cmd ==="; python -m ledgerkit $cmd --help; done`
Observed: all six `=== <cmd> ===` sections produced identical text, each matching exactly the usage block quoted in current-state-004 (same `usage:`, same positional-arguments block, same options block, word-for-word).

No Evidence-paths — purely from a live command run.

## Justification
Direct side-by-side comparison of the six captured blocks shows no textual difference between them or against the bare `--help` invocation, which is the directly observable current CLI surface (argparse evidently treats the report name as an ordinary positional value, not a registered subparser with its own help).
## Examples
`python -m ledgerkit balance --help` and `python -m ledgerkit check --help` both print the identical six-command usage line and the identical `options:` block.
## Counterexamples
not applicable
## Depends on
current-state-004 (establishes the baseline top-level help text being compared against)
## Open questions
none
## Evidence-support state
supported
## Status
verified
## Supersedes
