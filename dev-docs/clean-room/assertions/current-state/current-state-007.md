<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
# Assertion: current-state-007

## Statement
Running `grep -l "kind: unexplained_mismatch" dev-docs/compat-register/*.yaml | wc -l` right now returns `3` — one higher than the `2` obtained by the line-anchored `^kind:` count in current-state-006 — because the unanchored substring `"kind: unexplained_mismatch"` additionally matches inside a third file (`dev-docs/compat-register/LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml`) that contains that text somewhere other than its own `kind:` field (its own `kind:` field is `compatible`, per the file-list overlap check below).

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command 1: `cd /home/cormac/projects/ledgerkit && grep -l "kind: unexplained_mismatch" dev-docs/compat-register/*.yaml 2>/dev/null | wc -l` → `3`
Command 2 (per-kind `grep -l | wc -l`, run together): `compatible` → `41`, `intentional_divergence` → `1`, `unsupported` → `6` (unchanged from current-state-006), `unexplained_mismatch` → `3`. Sum = 51, exceeding the 49 total files.
Command 3 (overlap isolation): `grep -l "kind: compatible" dev-docs/compat-register/*.yaml | sort > f1; grep -l "kind: unexplained_mismatch" dev-docs/compat-register/*.yaml | sort >> f1; sort f1 | uniq -d`
Exact output:
```
dev-docs/compat-register/LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml
dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml
```

No Evidence-paths — these are grep/count commands against filenames and line-presence only, no file content was opened or read with the Read tool.

## Justification
The two filenames found by `uniq -d` are the files simultaneously matched by both the `"kind: compatible"` and `"kind: unexplained_mismatch"` unanchored greps, which explains the +2 discrepancy between the unanchored `grep -l` totals (41 + 3 = 44 for just these two kinds) and the anchored `^kind:` totals (40 + 2 = 42) for the same two kinds — each of these two files contains both substrings somewhere in its body, not just in its own `kind:` field.
## Examples
`LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml` and `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml` are the two filenames each matched by both unanchored substring searches.
## Counterexamples
not applicable
## Depends on
current-state-006 (the anchored baseline this discrepancy is measured against)
## Open questions
This record does not determine what field or prose inside those two files contains the cross-matching substring (e.g. a cross-reference to a related entry's kind, a cover-field, history note) — establishing that would require reading file content, which is outside this dispatch's permitted evidence.
## Evidence-support state
supported
## Status
verified
## Supersedes
