<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-003 | date: 2026-10-03 -->
# Assertion: compat-system-003

## Statement
As of this survey, the live compat-register directory contains exactly 49 YAML entry files. Their `kind` distribution is: 40 `compatible`, 6 `unsupported`, 2 `unexplained_mismatch`, 1 `intentional_divergence`, 0 `extension`. This matches the id-prefix distribution exactly: 40 files prefixed `LK-COMPAT-`, 6 prefixed `LK-UNSUP-`, 2 prefixed `LK-MISMATCH-`, 1 prefixed `LK-DIV-`.

## Kind
state_transformation
## Basis
observed_behaviour
## Evidence
`ls *.yaml | wc -l` → 49. `grep -h "^kind:" *.yaml | sort | uniq -c` → "40 kind: compatible", "1 kind: intentional_divergence", "2 kind: unexplained_mismatch", "6 kind: unsupported". `grep -h "^id:" *.yaml | sed -E 's/^id: (LK-[A-Z]+)-.*/\1/' | sort | uniq -c` → "40 LK-COMPAT", "1 LK-DIV", "2 LK-MISMATCH", "6 LK-UNSUP".

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-ACCOUNTDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-ALIAS-001.yaml, dev-docs/compat-register/LK-COMPAT-APPLYACCOUNT-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKACCOUNTS-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKASSERTIONS-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKAUTOBALANCED-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKCOMMODITIES-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKORDEREDDATES-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKPARSEABLE-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKPAYEES-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKUNIQUELEAFNAMES-001.yaml, dev-docs/compat-register/LK-COMPAT-COMMODITYDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-DDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-DECIMALMARK-001.yaml, dev-docs/compat-register/LK-COMPAT-DIRECTIVE-TAG-001.yaml, dev-docs/compat-register/LK-COMPAT-INCLUDE-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-POSTINGDATE-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-SCOPE-001.yaml, dev-docs/compat-register/LK-COMPAT-PAYEEDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-PDIRECTIVE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-ACCT-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-BOOLCOMBINE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DATE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-STATS-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DESC-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-PRINT-INTEGRATION-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-STATUS-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-ACCOUNTS-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-COMBINE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-COMMODITY-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-INHERIT-001.yaml, dev-docs/compat-register/LK-COMPAT-TAGDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-YDIR-001.yaml, dev-docs/compat-register/LK-DIV-INCLUDE-002.yaml, dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml, dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml, dev-docs/compat-register/LK-UNSUP-AUTOPOSTING-001.yaml, dev-docs/compat-register/LK-UNSUP-MULTICURRENCY-001.yaml, dev-docs/compat-register/LK-UNSUP-PERIODIC-001.yaml, dev-docs/compat-register/LK-UNSUP-QUERY-DATE-002.yaml, dev-docs/compat-register/LK-UNSUP-TIMECLOCK-001.yaml, dev-docs/compat-register/LK-UNSUP-VIRTUALPOSTING-001.yaml]

(Review note, lead, 2026-10-03: the original citation used a glob,
`dev-docs/compat-register/*.yaml`, which check_snapshot.py's evidence
resolver cannot resolve as a git object path -- a glob is not a path.
Expanded to the 49 actual filenames it denoted at freeze time, so the
citation remains exactly as meaningful -- "the full live register" --
while becoming machine-checkable.)

## Justification
Raw counts produced by shell commands scoped only to the permitted *.yaml glob in dev-docs/compat-register/ (no subdirectories, no README.md/UNEXPLAINED.md). The id-prefix/kind-field cross-check confirms internal consistency of the register's own naming convention.
## Examples
The 6 unsupported entries: LK-UNSUP-AUTOPOSTING-001, LK-UNSUP-MULTICURRENCY-001, LK-UNSUP-PERIODIC-001, LK-UNSUP-QUERY-DATE-002, LK-UNSUP-TIMECLOCK-001, LK-UNSUP-VIRTUALPOSTING-001.
## Counterexamples
None — the two count methods (by `kind:` field vs. by id prefix) agreed exactly, with no file where the two disagreed.
## Depends on
None.
## Open questions
The `examples/` subdirectory (excluded from this survey per task scope) may contain additional illustrative (non-live) entries per schema.md's own note that it holds illustrative entries "not part of the live register" — these are correctly excluded from the above counts, but were not inspected.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)
