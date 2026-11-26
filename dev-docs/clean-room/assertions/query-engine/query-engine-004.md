<!-- producer: assertion-research | topic: query-engine | dispatch: qe-tagjournal-004 | date: 2026-10-02 -->
# Assertion: query-engine-004

## Statement
Both `matches_transaction` and `matches_posting` (and the internal `_matches_posting_impl`/`_matches_posting_for_accounts`) raise `ValueError` if a `Tag` node is evaluated while `journal` is `None`. Every other node type (`Acct`, `Desc`, `DateSpan`, `MaxAccountLevel`, `Status`, and the `And`/`Or`/`Not` combinators) is unaffected by `journal` being `None` — only `Tag` evaluation consults it.

## Kind
invariant
## Basis
directly_stated
## Evidence
`eval.py` lines 128-130 (`matches_transaction`): `if journal is None: raise ValueError("tag: matching requires journal context")`; identical guard at lines 166-167 inside `_matches_posting_impl`. `test_eval.py::TestTag::test_journal_none_raises_on_matches_posting` and `test_journal_none_raises_on_matches_transaction` (lines 189-195) both call with no `journal` kwarg and assert `ValueError`.

Evidence-paths: [ledgerkit/query/eval.py:100-140, ledgerkit/query/eval.py:166-168, tests/test_query/test_eval.py:189-195]

## Justification
The module docstring (eval.py lines 20-22) states this is a deliberate, "binding loud-failure constraint": a `Tag` node must never silently narrow to own-tags-only when no journal is supplied, so correctness depends on this raising rather than degrading quietly.

## Examples
`matches_posting(Tag("rate", "1"), txn, posting)` (no `journal=`) raises `ValueError`; the same call with `journal=some_journal` succeeds.

## Counterexamples
None — every other node type's dispatch branch in both functions ignores `journal` entirely (e.g. the `Acct`/`Desc`/`DateSpan`/`Status`/`MaxAccountLevel` branches reference only `node`/`txn`/`posting`).

## Depends on
query-engine-001, query-engine-010 (what "effective tags" actually means).

## Open questions
None.

## Evidence-support state
supported
## Status
verified
## Supersedes
