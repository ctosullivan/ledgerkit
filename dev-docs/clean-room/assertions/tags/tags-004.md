<!-- producer: assertion-research | topic: tags | dispatch: tags-r4 | date: 2026-10-02 -->
# Assertion: tags-004

## Statement
`_inherited_account_tags` computes an account's effective declared-tag set by walking every ancestor in its `:`-separated hierarchy from the root segment down to the account itself (inclusive), concatenating each level's declared tags in least-specific-to-most-specific order. A sibling account branch does NOT inherit tags declared on a different sibling at a deeper level — only tags declared on a true ancestor (a strict prefix of the account's own `:`-joined path) apply.

## Kind
rule

## Basis
directly_stated

## Evidence
`_inherited_account_tags` (tags.py:157-176) builds all prefixes of `account.split(":")` from length 1 up to full length and looks up each in `journal.declared_account_tags`, concatenating results — "own tags first come from the least-specific ancestor, most-specific last." The docstring states it "mirrors hledger's `journalInheritedAccountTags`: inherited tags apply to the declaring account itself and all of its descendants, not just strict descendants."

Evidence-paths: [ledgerkit/tags.py:157-176]

## Justification
The loop `for i in range(1, len(segments) + 1)` constructs exactly the chain of prefixes "assets", "assets:bank", "assets:bank:savings" for account "assets:bank:savings" — each is looked up independently, so an account only picks up tags declared on itself or a literal ancestor prefix, never on a cousin/sibling subtree.

## Examples
`test_deep_descendant_inherits_from_every_ancestor` (test_tags.py:201-205): "assets:bank:savings" inherits both "assets"'s `type:A` and "assets:bank"'s `rate:3`. `test_sibling_branch_does_not_inherit` (test_tags.py:213-216): "assets:savings" (a sibling of "assets:bank", not a descendant) inherits "assets"'s `type:A` but NOT "assets:bank"'s `rate:3`. `test_root_level_declared_tag_applies_to_itself_too` (test_tags.py:210-211): "assets" itself gets its own declared tag, confirming self-inclusion. `test_unrelated_account_gets_nothing` (test_tags.py:207-208): "expenses:food" (no shared prefix at all) returns [].

## Counterexamples
None found.

## Depends on
`Journal.declared_account_tags` (a dict keyed by exact account-path string, per the setUp fixtures).

## Open questions
None within permitted evidence — the sibling/ancestor distinction and self-inclusion are both directly tested.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)
