<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-014 | date: 2026-10-02 -->
# Assertion: reports-cli-014

## Statement
`writer.transaction_to_text()` serializes a single Transaction to hledger journal-format text that is guaranteed to round-trip through `parse_string()` to an equivalent Transaction (same date, flag, description, postings, amounts, comments — `source_span`/`raw_text` excluded from the guarantee). Amount columns are right-aligned to a shared column computed from the widest account name (among postings that carry an explicit amount) plus a minimum 2-space gap; elided postings (no amount) are printed as bare `"    {account}"`. `writer.journal_to_text()` serializes all transactions in `journal.transactions`, separated by exactly one blank line, but explicitly does NOT serialize directives (account/commodity/payee/P) in v1 — callers needing full round-trip fidelity for directives must use the raw source file.
## Kind
state_transformation
## Basis
directly_stated
## Evidence
`transaction_to_text()` docstring: "The returned string ends with a single newline. When parsed by parse_string(), the result round-trips to an equivalent Transaction (same date, flag, description, postings, amounts, comments; source_span and raw_text are not checked)." `journal_to_text()` docstring: "Directives (account, commodity, payee, P) are not serialised in v1 — callers that need full round-trip fidelity should work with the raw source file rather than re-serialising the Journal." Tests `test_roundtrip_simple`, `test_roundtrip_with_flags_and_comments`, and `test_journal_to_text_roundtrip` confirm the round-trip guarantee at both the transaction and journal level; `test_journal_to_text_separator` confirms exactly one blank line (`\n\n`, never `\n\n\n`) between transaction blocks; `test_journal_to_text_empty` confirms an empty journal serializes to a lone `"\n"`.
## Justification
Docstrings, implementation (writer.py:29-97), and the full TestTransactionToText/TestJournalToText test classes all agree.
## Examples
A transaction with a £2000.00 and a -£2000.00 posting serializes with both amounts right-aligned to the same column; an elided posting line has no trailing amount; a cleared transaction's header starts with `"DATE *"`.
## Counterexamples
None
## Depends on
None
## Open questions
None
## Evidence-support state
supported
## Status
verified
## Supersedes
None

Evidence-paths: [ledgerkit/writer.py:1-97, tests/test_writer.py:30-203]
