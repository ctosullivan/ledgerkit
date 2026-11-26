<!-- producer: assertion-research | topic: tags | dispatch: tags-r6 | date: 2026-10-02 -->
# Assertion: tags-006

## Statement
Within a single tag value, only a literal comma (`,`) or end-of-line terminates the value — a colon inside the value text does NOT terminate it (e.g. `url: http://example.com` parses as one tag named "url" with value "http://example.com"). There is no escaping mechanism for a comma inside a value, so a value can never contain a literal comma; this is treated as a genuine hledger limitation, not a ledgerkit omission.

## Kind
rule

## Basis
directly_stated

## Evidence
`parse_tags` docstring (tags.py:63-69): "A value runs from just after the colon... to the next `,` or end of line... **A value cannot contain a literal comma** — there is no escaping mechanism; hledger documents this as a real limitation, not an omission. A colon *can* appear inside a value." Implementation in `_parse_comment_line_tags` (tags.py:101-107) searches only for the next comma (`rest.find(",")`) within `rest = line[colon + 1:]`, never re-scanning for a colon to end the value.

Evidence-paths: [ledgerkit/tags.py:63-69, ledgerkit/tags.py:101-107]

## Justification
The code's comma-search logic (`rest.find(",")`) is the sole terminator check for a value; nothing in `_parse_comment_line_tags` treats a colon within `rest` specially, so a colon is always absorbed into the current value rather than starting a new tag-name scan until the next top-level colon search begins after the comma.

## Examples
`test_colon_inside_value_is_fine` (test_tags.py:84-89): `parse_tags("url: http://example.com, other: x")` → `[("url", "http://example.com"), ("other", "x")]`. `test_comma_is_a_hard_separator_no_escaping` (test_tags.py:103-108): `parse_tags("tag:before,after:stuff")` → `[("tag", "before"), ("after", "stuff")]`, i.e. the comma always splits even with no space, and "after" becomes a new tag name rather than part of the value.

## Counterexamples
None found — no test shows a colon ending a value early, nor any comma-escaping syntax.

## Depends on
`_parse_comment_line_tags`'s single-pass colon/comma scanning loop.

## Open questions
None within permitted evidence.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)
