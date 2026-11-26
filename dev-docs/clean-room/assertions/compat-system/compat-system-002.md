<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-002 | date: 2026-10-03 -->
# Assertion: compat-system-002

## Statement
The schema defines a four-tier `status` field (`proposed`, `self-verified`, `verified`, `final`) with an explicit, enforced authorship rule: `status: verified` may **only** be written by a separately-dispatched `compat-differential-tester` agent's own output — "The lead must NEVER write this status into a register YAML directly" — whereas `self-verified` is for the same identity/session that implemented the feature confirming it with real command output. This rule is a written policy, and it was found to hold in every single one of the 23 entries carrying either status.

## Kind
rule
## Basis
directly_stated
## Evidence
schema.md lines 54-67 (the `status` field's enum and per-value comments) state the tiering and the authorship restriction verbatim. A grep of `verified_by:` across every yaml whose `status:` is `verified` (14 files) shows all 14 name "compat-differential-tester" as the verifier; a grep of the 9 files whose `status:` is `self-verified` shows all 9 name "Claude (lead session, ...)" as the verifier.

Evidence-paths: [dev-docs/compat-register/schema.md:54-67, dev-docs/compat-register/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml, dev-docs/compat-register/LK-COMPAT-QUERY-ACCT-001.yaml, dev-docs/compat-register/LK-COMPAT-DIRECTIVE-TAG-001.yaml]

## Justification
The policy statement is directly quoted from schema.md. The compliance claim (that the rule is actually followed, not just written) is an observed_behaviour finding from a full-register grep, not an inference — every verified_by string in both tiers was read and categorized.
## Examples
LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml: `verified_by: "compat-differential-tester (independent dispatch, Stage C Phase 9 verification)"`. LK-COMPAT-QUERY-ACCT-001.yaml: `verified_by: "Claude (lead session, Stage C Phase 2 implementation — not a separately-dispatched compat-differential-tester agent...)"`.
## Counterexamples
None found in the 23 proposed/self-verified/verified entries checked for this specific authorship rule.
## Depends on
compat-system-004 (status counts).
## Open questions
No entry in the register currently carries `status: final`, so the fourth tier's own practice (docs reconciled and cross-linked from hledger-compatibility.md) was not observable from the register files alone.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)
