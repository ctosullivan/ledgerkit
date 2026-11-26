<!-- producer: assertion-research | topic: loader | dispatch: ldr-e2p6 | date: 2026-10-02 -->
# Assertion: loader-005

## Statement
`load_journal()` merges multiple files' content by textual substitution, not AST-level merge: `_expand_includes` recursively replaces each include directive line with the fully expanded text of the referenced file(s), producing one single combined text string that is parsed exactly once via `parse_string()`. As a direct consequence, directive scope active before an include (the docstring's own example: an `alias` directive) propagates naturally into the included content, because the included text is spliced in at the exact textual position of the `include` line within one continuous parse.

## Kind
state_transformation

## Basis
directly_stated

## Evidence
`load_journal`'s docstring states this rationale explicitly ("Included files are expanded recursively at the point of the directive before parsing, so directive scope ... propagates naturally through included content"); `_expand_includes` implements this via string concatenation (`output.append(...)` / `"".join(output)`) rather than merging parsed objects.

Evidence-paths: [ledgerkit/loader.py:254-258, ledgerkit/loader.py:145-191, ledgerkit/loader.py:289, ledgerkit/loader.py:294]

## Justification
`test_ordering_preserved` (nested three-level include) demonstrates that included content appears at the exact point of substitution — innermost-included transaction (C) appears before its including file's transaction (B), which appears before the root's own transaction (A) — matching pure textual splicing rather than any append-at-end or alphabetical merge.

## Examples
- `nested_a.journal` includes `nested_b.journal` which includes `nested_c.journal`; resulting transaction order is `["Nested C transaction", "Nested B transaction", "Nested A transaction"]` (test-confirmed, `test_ordering_preserved`, lines 153-162).
- `test_include_at_top_of_file` / `test_include_at_end_of_file` confirm transactions appear in document order relative to where the `include` line sits in the root file.

## Counterexamples
`merge_journals()` is architecturally distinct and does NOT do textual splicing — it operates on already-parsed `Journal` objects and concatenates their lists after independent parsing, so any directive scoping captured within one journal's parse does not and cannot propagate into another journal being merged via `merge_journals`. The two merge mechanisms (include-based text splicing vs. post-parse list concatenation) are not interchangeable.

## Depends on
loader-001

## Open questions
None beyond what's noted under Counterexamples.

## Evidence-support state
supported

## Status
verified

## Supersedes
None.
