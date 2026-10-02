<!-- producer: assertion-research | topic: loader | dispatch: ldr-f5r1 | date: 2026-10-02 -->
# Assertion: loader-006

## Statement
`merge_journals(journals: list[Journal]) -> Journal` is a separate public function from the include mechanism; it merges already-parsed `Journal` objects by order-preserving concatenation of `transactions`, `prices`, `declared_accounts`, `declared_commodities`, `declared_payees`, and `declared_tags` across all inputs. `source_file` on the result is taken from `journals[0]` only; `included_files` on the result is the arithmetic sum of each input's `included_files`. A single-element input list is a fast path that returns the original object unchanged (`is` identity, not a copy). An empty input list raises `ValueError`.

## Kind
definition

## Basis
directly_stated

## Evidence
Function body matches docstring exactly; this is the most heavily test-covered behavior in the file, with dedicated tests for every field and the identity fast path.

Evidence-paths: [ledgerkit/loader.py:216-248, tests/test_loader/test_loader.py:351-437, tests/test_loader/test_loader.py:481-536]

## Justification
`test_merge_single_journal` asserts `self.assertIs(result, j)`, directly confirming the identity fast path rather than a copy; `test_merge_source_file_is_first` and `test_merge_included_files_summed` directly confirm the stated first-wins / sum-all semantics respectively.

## Examples
- `merge_journals([j1, j2, j3])` where each has one transaction (A, B, C) → result has 3 transactions in order `["A", "B", "C"]` (test-confirmed, `test_merge_three_journals`).
- `merge_journals([j1])` → returns `j1` itself, not a new object (test-confirmed).
- `merge_journals([])` → raises `ValueError` (test-confirmed, `test_merge_empty_raises`).

## Counterexamples
None found; behavior matches docstring and tests in every case examined.

## Depends on
None (independent of the include/`_expand_includes` mechanism).

## Open questions
None.

## Evidence-support state
supported

## Status
verified

## Supersedes
None.
