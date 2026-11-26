<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
# Assertion: current-state-006

## Statement
There are exactly 49 YAML files in `dev-docs/compat-register/` right now, and counting each file's `kind:` field line gives: `compatible` = 40, `unsupported` = 6, `unexplained_mismatch` = 2, `intentional_divergence` = 1 (sum = 49, matching the total file count).

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command 1: `cd /home/cormac/projects/ledgerkit && ls dev-docs/compat-register/*.yaml | wc -l` → `49`
Command 2: `cd /home/cormac/projects/ledgerkit && grep -h "^kind:" dev-docs/compat-register/*.yaml | sort | uniq -c`
Exact output:
```
     40 kind: compatible
      1 kind: intentional_divergence
      2 kind: unexplained_mismatch
      6 kind: unsupported
```

No Evidence-paths — these are grep/count commands against the register directory, not a content read of any individual file (per the task's restriction).

## Justification
`grep -h "^kind:"` matches only lines that begin with the literal field `kind:` (anchored at line start), so each matched line is one file's actual `kind:` field value, not an incidental substring elsewhere in the file; the counts sum to exactly the total file count (49), which cross-validates that each file contributes exactly one such anchored line.
## Examples
40 files' first/only `^kind:` line reads `kind: compatible`; 6 files' reads `kind: unsupported`; etc.
## Counterexamples
not applicable
## Depends on
none
## Open questions
none
## Evidence-support state
supported
## Status
verified
## Supersedes
