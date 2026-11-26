<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a10 | date: 2026-10-02 -->
# Assertion: editor-surface-010

## Statement
`ledgerkit-editor`'s `src/ledgerkit_editor/utils/query_match.py` deliberately does NOT import `ledgerkit.reports._matches_pattern` / `_posting_matches` (private, underscore-prefixed, never exported from `ledgerkit.__init__`), instead duplicating the matching logic locally. The module's own docstring attributes this to an accepted planning decision to avoid depending on unreleased/private upstream surface.

## Kind
rule

## Basis
directly_stated

## Evidence
From the ledgerkit-editor clone: the module docstring states the policy and reasoning verbatim, and the corresponding test file explains the same rationale.

Evidence-paths: [/tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/query_match.py:1-14, /tmp/ledgerkit-editor-research-clone-2/tests/test_query_match.py:1-7]

## Justification
Direct quotation from query_match.py's docstring: "Deliberately duplicated from ledgerkit.reports._matches_pattern and _posting_matches, which are private (underscore-prefixed, never exported from ledgerkit.__init__). Importing private members of a pinned dependency is fragile." The test file's docstring independently corroborates: "Uses real ledgerkit Query/Transaction/Posting objects... to catch any drift between our locally-duplicated matching semantics and the real ledgerkit.Query contract."

## Examples
test_query_match.py imports the real `ledgerkit.Query`, `Posting`, `Transaction` specifically to cross-check the locally duplicated logic in `query_match.py` against real ledgerkit behaviour, rather than importing the private helpers directly.

## Counterexamples
None found.

## Depends on
editor-surface-009 (the real `ledgerkit.Query` import used for the cross-check).

## Open questions
This references an unnamed project-level API convention belonging to the ledgerkit-editor project's own governance (not ledgerkit's) — that file was not read (out of scope: narrative/root documentation, not source or test code), so the rule's exact wording in that project is unconfirmed beyond this paraphrase.

## Evidence-support state
partially_supported

## Status
proposed

## Supersedes
(none)
