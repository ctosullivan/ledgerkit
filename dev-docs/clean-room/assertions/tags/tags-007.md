<!-- producer: assertion-research | topic: tags | dispatch: tags-r7 | date: 2026-10-02 -->
# Assertion: tags-007

## Statement
The same tag name may legitimately appear multiple times within a single `parse_tags` result (and, by extension, within `_effective_tags`'s combined output) with different values; results are always an ORDERED LIST of (name, value) pairs, never collapsed into a dict keyed by name. Additionally, tag names have no character-class restriction beyond "not a colon, not a line break, no internal whitespace" — digits, punctuation, and non-ASCII characters are all accepted, despite the hledger manual's prose describing tags as "a single word or hyphenated word."

## Kind
invariant

## Basis
directly_stated

## Evidence
`parse_tags` docstring (tags.py:56-60, 70-72): "Tag names have no character-class restriction beyond... despite the manual's prose... the actual parser is more permissive... The same tag name may legitimately repeat with different values on one line — the result is an ordered list of pairs, never collapsed into a dict." Return type annotation is `list[tuple[str, str]]` (tags.py:41), not a dict.

Evidence-paths: [ledgerkit/tags.py:41, ledgerkit/tags.py:56-60, ledgerkit/tags.py:70-72]

## Justification
The function signature itself (`-> list[tuple[str, str]]`) structurally rules out silent collapsing by name, and the docstring explicitly calls out that this is a deliberate choice following hledger's own grammar rather than a more "dict-like" tag model.

## Examples
`test_repeated_tag_name_kept_as_list_not_collapsed` (test_tags.py:112-117): `parse_tags("tag1:value 1, tag1:value 2")` → `[("tag1", "value 1"), ("tag1", "value 2")]`, both entries preserved. `test_no_character_class_restriction_on_name` (test_tags.py:77-80): `parse_tags("tag_with.punct123:x")` → `[("tag_with.punct123", "x")]`, confirming punctuation/digits accepted in a name.

## Counterexamples
None found.

## Depends on
None beyond `parse_tags` itself.

## Open questions
None within permitted evidence.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)
