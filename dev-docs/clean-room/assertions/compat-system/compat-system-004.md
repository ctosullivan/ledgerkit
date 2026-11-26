<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-004 | date: 2026-10-03 -->
# Assertion: compat-system-004

## Statement
The live register's `status` distribution is: 26 `proposed`, 9 `self-verified`, 14 `verified`, 0 `final` (26+9+14=49, matching the total file count exactly). The majority of entries (26/49, ~53%) have not yet had any executable comparison run against them by an independently-dispatched verifier.

## Kind
state_transformation
## Basis
observed_behaviour
## Evidence
`grep -h "^status:" *.yaml | sort | uniq -c` → "26 status: proposed", "9 status: self-verified", "14 status: verified".

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-ACCOUNTDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-ALIAS-001.yaml, dev-docs/compat-register/LK-COMPAT-APPLYACCOUNT-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKACCOUNTS-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKASSERTIONS-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKAUTOBALANCED-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKCOMMODITIES-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKORDEREDDATES-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKPARSEABLE-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKPAYEES-001.yaml, dev-docs/compat-register/LK-COMPAT-CHECKUNIQUELEAFNAMES-001.yaml, dev-docs/compat-register/LK-COMPAT-COMMODITYDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-DDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-DECIMALMARK-001.yaml, dev-docs/compat-register/LK-COMPAT-DIRECTIVE-TAG-001.yaml, dev-docs/compat-register/LK-COMPAT-INCLUDE-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-POSTINGDATE-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-SCOPE-001.yaml, dev-docs/compat-register/LK-COMPAT-PAYEEDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-PDIRECTIVE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-ACCT-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-BOOLCOMBINE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DATE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-STATS-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DESC-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-PRINT-INTEGRATION-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-STATUS-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-ACCOUNTS-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-COMBINE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-COMMODITY-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-INHERIT-001.yaml, dev-docs/compat-register/LK-COMPAT-TAGDIR-001.yaml, dev-docs/compat-register/LK-COMPAT-YDIR-001.yaml, dev-docs/compat-register/LK-DIV-INCLUDE-002.yaml, dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml, dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml, dev-docs/compat-register/LK-UNSUP-AUTOPOSTING-001.yaml, dev-docs/compat-register/LK-UNSUP-MULTICURRENCY-001.yaml, dev-docs/compat-register/LK-UNSUP-PERIODIC-001.yaml, dev-docs/compat-register/LK-UNSUP-QUERY-DATE-002.yaml, dev-docs/compat-register/LK-UNSUP-TIMECLOCK-001.yaml, dev-docs/compat-register/LK-UNSUP-VIRTUALPOSTING-001.yaml]

(Review note, lead, 2026-10-03: same glob-to-enumeration fix as
compat-system-003 -- see that file's note.)

## Justification
Direct count from the permitted yaml files; no `final`-status entries exist to inspect for that tier's own practice.
## Examples
Most of the pre-existing "migrated from hledger-compatibility.md" batch (e.g. LK-COMPAT-ACCOUNTDIR-001, LK-COMPAT-ALIAS-001, LK-COMPAT-APPLYACCOUNT-001, the LK-COMPAT-CHECK*-001 entries, LK-COMPAT-COMMODITYDIR-001, LK-COMPAT-DDIR-001, LK-COMPAT-DECIMALMARK-001, LK-COMPAT-INCLUDE-001, LK-COMPAT-PAYEEDIR-001, LK-COMPAT-PDIRECTIVE-001) remain `status: proposed` — these carry only `evidence: kind: manual` (a doc-link citation), consistent with schema.md's note that executable evidence is expected before status moves past `proposed`.
## Counterexamples
None.
## Depends on
compat-system-002 (the authorship rule each status tier is gated by).
## Open questions
Whether the 26 `proposed` entries represent a backlog actively being worked through by compat-differential-tester dispatches, or a stalled/lower-priority batch, cannot be determined from the register files alone (would require dev-docs/retros/ or ROADMAP.md, both out of scope).
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)
