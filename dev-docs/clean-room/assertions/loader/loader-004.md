<!-- producer: assertion-research | topic: loader | dispatch: ldr-d9m4 | date: 2026-10-02 -->
# Assertion: loader-004

## Statement
Circular includes are detected via a `visited: set[Path]` of absolute paths threaded through recursive `_expand_includes` calls, representing the set of files currently "in progress" along the active include chain (an ancestor stack, not a global "already processed" record): a path is added to `visited` immediately before recursing into it and removed immediately after that recursive call returns. If a target path is already in `visited` when about to be processed, `ParseError("circular include detected: ...")` is raised. `load_journal` seeds this set with the root file itself (`visited = {abs_path}`) before the first call.

## Kind
invariant

## Basis
directly_stated

## Evidence
The add-before/remove-after pattern and seeding of the root path are explicit in code; a dedicated fixture-driven test confirms a ParseError mentioning "circular" is raised for a known circular fixture (fixture contents were out of scope for this research and were not read).

Evidence-paths: [ledgerkit/loader.py:117-134, ledgerkit/loader.py:179-190, ledgerkit/loader.py:288, tests/test_loader/test_loader.py:286-289]

## Justification
Because `visited.remove(target)` runs after each recursive call returns (not only on success), the set tracks only the current chain of ancestors, not every file ever included — this is the standard DFS cycle-detection pattern and is explicitly what the docstring describes ("Mutated (add before recurse, remove after) for cycle detection").

## Examples
- `circular_a.journal` (fixture, not read directly) → `load_journal` raises ParseError whose message contains "circular" (case-insensitive check in test).

## Counterexamples
A "diamond" include graph — e.g. root includes both `b.journal` and `c.journal`, and both `b.journal` and `c.journal` independently include the same `shared.journal` — would NOT trigger circular-include detection under this ancestor-stack design, because `shared.journal` is removed from `visited` after the first inclusion completes, before the second (sibling) inclusion begins. No test in `tests/test_loader/test_loader.py` exercises this diamond scenario. **Reviewer verification (2026-10-03):** confirmed by direct execution — a root file including both `b.journal` and `c.journal`, each of which independently includes a shared `shared.journal`, loads successfully with 5 transactions in order `["Shared", "B", "Shared", "C", "Root"]` and `included_files == 3`; `shared.journal`'s transaction is duplicated, and no `ParseError` is raised. This is no longer an inference from the add/remove pattern; it is a confirmed, reproducible behaviour.

## Depends on
loader-001, loader-002

## Open questions
Is repeated-but-non-circular inclusion of the same file from independent branches (the diamond case) intended to succeed (producing duplicate transactions), or should it also be flagged? Not addressed by any docstring, comment, or test in the permitted evidence. The behaviour itself is now reviewer-confirmed as fact (see Counterexamples); what remains unresolved is the design intent. **Escalating to lead.**

## Evidence-support state
partially_supported

## Status
supported

## Supersedes
None.
