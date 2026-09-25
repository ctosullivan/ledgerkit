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

| ID | Area | Opened | Summary | Owner |
|---|---|---|---|---|
| `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` | query.tag.emptyvalue | 2026-09-25 | `tag:NAME=` (and any other empty-regex query value, e.g. `acct:`/`desc:`) errors (exit 1) on real hledger 1.52.4 but is accepted and matches "any value" on ledgerkit — found while independently re-verifying `LK-COMPAT-QUERY-TAG-001`, which incorrectly claimed the two were equivalent for this case | unassigned |

## Format, once entries exist

| ID | Area | Opened | Summary | Owner |
|---|---|---|---|---|
| `LK-MISMATCH-<AREA>-NNN` | dotted area path | YYYY-MM-DD | one-line description of the observed disagreement | agent/person investigating, or "unassigned" |
