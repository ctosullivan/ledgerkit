# Unexplained mismatches — running punch-list

This file lists every open `kind: unexplained_mismatch` entry in the
compatibility register. It is the register's north-star metric dashboard
(`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.2):
**the goal is to drive this list to zero**, not to drive
`intentional_divergence`/`extension`/`unsupported` counts to zero — those
are legitimate, permanent product decisions.

An entry appears here, in "Open entries", only while its `kind` is
`unexplained_mismatch` **and** it has no `resolved_into` field.
**Corrected Stage C Phase 7** (`dev-docs/compat-register/schema.md`'s
"Resolution lifecycle" section, `09-compatibility-system.md` §9.7):
resolving a mismatch does **not** mean flipping its `kind` field in
place. Once `compat-differential-tester` independently confirms a fix,
a **new** entry is created (new id, `kind:` matching the settled state
it resolved into — `compatible`, `extension`, `intentional_divergence`,
or `unsupported`), the **original** `unexplained_mismatch` entry is
retained untouched as historical evidence with a new `resolved_into`/
`resolved_date` pair added, and the row moves from "Open entries" below
to "Resolved entries" — it is never simply deleted from this file. This
file is never edited to "explain away" an entry without the register
files themselves changing first; the two must always agree.

## Open entries

| ID | Area | Opened | Summary | Owner |
|---|---|---|---|---|
| `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` | query.regex.emptyalternation | 2026-09-25 | Empty-alternation-branch regex syntax — confirmed on BOTH sides for the full family as of 2026-09-27 re-verification: `(|)`, `a\|`, `\|a`, `(a\|)`, `(\|a)`, plus generalised cases (`a\|\|b`, `(a\|)\|b`, `\|\|`, `(\|\|)`, `a\|(\|b)`, `(a)\|`, `\|(a)`, `a(\|)b`, `(a\|)(b)`) all error on real hledger 1.52.4 (regex-tdfa rejects any branch of `\|` with zero atoms) but are ALL accepted by Ledgerkit's `ledgerkit.query.regex.validate_hledger_regex` (no `\|`-aware check exists); found as a related-but-separate observation while scoping `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`; still not resolved into a fix — a fix must be escape-aware (`a\|\|b`-style escaped literal pipes must stay accepted) and must not affect `()`, `(a)`, `a\|b`, `(a\|b)`, `()\|a`, `a\|()` which hledger and Ledgerkit both already accept correctly | unassigned |

## Resolved entries

Moved here (not deleted) once independently verified and superseded by
a new, settled-state entry — see the paragraph above.

| Original ID | Resolved into | Resolved | Summary |
|---|---|---|---|
| `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` | `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` | 2026-09-25 | Stage C Phase 7: `ledgerkit.query.regex.validate_hledger_regex` now rejects an empty pattern (`pattern == ""`), matching real hledger's own parse-time rejection for `acct:`/`desc:`/`tag:NAME=`/`depth:=N` alike — independently verified by a genuinely separate `compat-differential-tester` dispatch |

## Format, once entries exist

**Open entries:**

| ID | Area | Opened | Summary | Owner |
|---|---|---|---|---|
| `LK-MISMATCH-<AREA>-NNN` | dotted area path | YYYY-MM-DD | one-line description of the observed disagreement | agent/person investigating, or "unassigned" |

**Resolved entries:**

| Original ID | Resolved into | Resolved | Summary |
|---|---|---|---|
| `LK-MISMATCH-<AREA>-NNN` | `LK-<KIND>-<AREA>-NNN` | YYYY-MM-DD | one-line description of how it resolved |
