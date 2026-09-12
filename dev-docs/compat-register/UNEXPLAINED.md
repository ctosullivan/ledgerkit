# Unexplained mismatches — running punch-list

This file lists every open `kind: unexplained_mismatch` entry in the
compatibility register. It is the register's north-star metric dashboard
(`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.2):
**the goal is to drive this list to zero**, not to drive
`intentional_divergence`/`extension`/`unsupported` counts to zero — those
are legitimate, permanent product decisions.

An entry appears here only while its `kind` is `unexplained_mismatch`. Once
`compat-differential-tester` (or the lead, with `compat-differential-tester`
confirming) resolves it into one of the four settled states —
`compatible`, `extension`, `intentional_divergence`, or `unsupported` — its
`kind` changes in the register file itself and it is removed from this
list. This file is never edited to "explain away" an entry without the
register file itself changing first; the two must always agree.

## Open entries

_None currently open._ No `compat-differential-tester` differential run has
taken place yet (Stage A closeout has produced `status: proposed` register
entries only — see `README.md`) — this list will populate once Stage C
onward starts running real fixtures against a pinned `hledger` binary.

## Format, once entries exist

| ID | Area | Opened | Summary | Owner |
|---|---|---|---|---|
| `LK-MISMATCH-<AREA>-NNN` | dotted area path | YYYY-MM-DD | one-line description of the observed disagreement | agent/person investigating, or "unassigned" |
