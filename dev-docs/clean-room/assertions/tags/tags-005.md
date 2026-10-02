<!-- producer: assertion-research | topic: tags | dispatch: tags-r5 | date: 2026-10-02 -->
# Assertion: tags-005

## Statement
`parse_tags`'s underlying grammar treats a space immediately before a colon as voiding that entire tag candidate (not merely producing an empty-string name) — e.g. "foo : bar" yields zero tags, not a tag named "foo" nor one named "" — and scanning resumes immediately after the voided colon, so a genuine tag appearing later on the same line after a voided candidate is still correctly found.

## Kind
rule

## Basis
directly_stated

## Evidence
`_tag_name_before_colon` (tags.py:141-154): "if `candidate` is empty or its *last character* is whitespace, the name is empty (voided)." The `parse_tags` docstring (tags.py:50-55) states: "a space right before the colon voids that tag entirely (the text is discarded, scanning continues after the colon for a further tag), it does not merely produce an empty-string name." `_parse_comment_line_tags` (tags.py:93-100) implements the "resume right after this colon" behavior via `pos = colon + 1; continue`.

Evidence-paths: [ledgerkit/tags.py:50-55, ledgerkit/tags.py:93-100, ledgerkit/tags.py:141-154]

## Justification
The code explicitly distinguishes Python's own `str.split()` (which would discard trailing whitespace and still find "foo" as the last word) from hledger's actual `last (T.split isSpace candidate)` semantics, and implements the latter specifically to void the tag rather than silently clean up the name.

## Examples
`test_space_before_colon_voids_the_tag` (test_tags.py:64-69): `parse_tags("foo : bar")` returns `[]`. `test_space_before_colon_then_a_real_tag_later` (test_tags.py:71-75): `parse_tags("foo : bar, real:tag")` returns `[("real", "tag")]`, confirming scanning resumes and finds the later genuine tag rather than aborting the whole line.

## Counterexamples
None found — both tests confirm the stated voiding/resume behavior consistently.

## Depends on
`_tag_name_before_colon` (the whitespace-at-end check).

## Open questions
None within permitted evidence.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)
