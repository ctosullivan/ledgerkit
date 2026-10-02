<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-006

## Statement
Comment syntax distinguishes four cases: (1) a column-0 (non-indented) `;` or `#` line is always a silently-skipped top-level comment, never attached to any transaction; (2) an indented `;`-led line inside an open transaction block is a follow-on comment appended (newline-joined) to the last-seen posting's `inline_comment`, or to the transaction's `inline_comment` if no posting has been seen yet; (3) an indented `#`-led line inside a block extends the transaction's source span but its text is never attached to any comment field; (4) a same-line inline comment after `;` on a transaction header or posting is captured directly by the respective regex/split logic. `#`-led comments never contribute to tag extraction (only `;`-led comments are tag-scanned).

## Kind
rule

## Basis
directly_stated

## Evidence
The large comment block above the comment-handling branch in `_parse_string_impl`, and the branch body itself.

Evidence-paths: [ledgerkit/parser.py:1045-1109]

## Justification
The in-code comment explicitly describes both sub-cases (column-0 vs indented) and the `;`-vs-`#` distinction; the branch logic (checking `is_indented`, `stripped.startswith(";")` vs `"#"`) implements it, and it is heavily tested.

## Examples
Tests named with T/B/I/F/S prefixes in test_parser.py directly targeting this logic: `test_T09_bare_semicolon_at_top_level`, `test_F06_indented_hash_inside_txn_not_captured`, `test_F08_noindent_hash_inside_txn_not_captured_span_not_extended`, `test_F09_indented_semicolon_appended_to_existing_inline_comment`, `test_S02_noindent_semicolon_does_not_extend_span` (tests/test_parser/test_parser.py:848-1070). Also `test_hash_comment_never_yields_tags` (tests/test_parser/test_parser.py:1530).

## Counterexamples
A standalone column-0 `;` line with no blank line separating two transactions is explicitly NOT treated as a follow-on comment on the previous transaction's last posting — documented as a deliberate edge case in the same comment block (parser.py:1063-1066).

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes

