<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-001 | date: 2026-10-03 -->
# Assertion: compat-system-001

## Statement
The compat-register schema (dev-docs/compat-register/schema.md) defines a closed `kind` taxonomy of exactly five values for a compatibility-register entry: `compatible`, `extension`, `intentional_divergence`, `unsupported`, `unexplained_mismatch`. Each `kind` corresponds to a fixed `ledgerkit.relationship` value: compatible→equivalent, extension→superset, unsupported→subset, intentional_divergence→incomparable (unexplained_mismatch has no fixed relationship stated).

## Kind
definition
## Basis
directly_stated
## Evidence
schema.md lines 17-19 state: "kind: compatible | extension | intentional_divergence | unsupported | unexplained_mismatch". Lines 29-33 give the relationship mapping as inline comments under `ledgerkit.relationship`.

Evidence-paths: [dev-docs/compat-register/schema.md:17-19, dev-docs/compat-register/schema.md:29-33]

## Justification
This is a direct transcription of the schema file's own enumerated field definition; no inference was required.
## Examples
LK-COMPAT-ACCOUNTDIR-001.yaml uses `kind: compatible` + `relationship: equivalent`; LK-UNSUP-AUTOPOSTING-001.yaml uses `kind: unsupported` + `relationship: subset`; LK-DIV-INCLUDE-002.yaml uses `kind: intentional_divergence` + `relationship: incomparable` — all three observed pairings match the schema's stated mapping exactly.
## Counterexamples
None found — every one of the 49 entries' kind/relationship pairs observed during this survey matched the schema's stated mapping (see compat-system-003 for the full kind-count breakdown).
## Depends on
None.
## Open questions
No live entry uses `kind: extension` (see compat-system-003) — the superset/`relationship: extension` pairing is defined in schema but currently unexercised in the register; whether this is because no extension behaviour exists yet, or because such entries live elsewhere, was not investigated (out of scope: would require reading non-permitted docs).
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)
