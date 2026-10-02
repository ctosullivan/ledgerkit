<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-003

## Statement
A posting line is split into account and amount on the first run of two-or-more whitespace characters (`\s{2,}`, maxsplit=1); this lets account names containing a single internal space (e.g. "expenses:fun money") survive intact, while a posting with no amount token after the split is treated as an elided amount (`amount=None`), to be resolved later via `resolve_elision`.

## Kind
rule

## Basis
directly_stated

## Evidence
`_parse_posting` function, specifically the `re.split(r"\s{2,}", line, maxsplit=1)` call and its accompanying comment block.

Evidence-paths: [ledgerkit/parser.py:676-716]

## Justification
The code and its mandated regex-documentation comment explicitly state the two-space account/amount delimiter rule and the elided-amount fallback; `test_elided_amount_is_none` exercises it directly.

## Examples
`"expenses:fun money  £5"` splits into account="expenses:fun money", amount="£5"; `"    assets:bank\n"` (posting with no amount) → `Posting(amount=None)` (tests/test_parser/test_parser.py:75-83).

## Counterexamples
A posting line with only a single space between account and amount is NOT split there — the whole line including the would-be amount becomes part of `account`, which would then fail commodity/amount parsing expectations; not separately unit-tested in the excerpts read, but implied by the regex (`\s{2,}` strictly requires 2+).

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes

