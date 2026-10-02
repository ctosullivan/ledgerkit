<!-- producer: assertion-research | topic: query-engine | dispatch: qe-tokenizer-006 | date: 2026-10-02 -->
# Assertion: query-engine-006

## Statement
The tokenizer (`_TOKEN` regex, `parser.py` lines 82-89, applied via `_tokenize`) splits a query string on whitespace while keeping a `prefix:"quoted phrase"` together as a single token, with the surrounding quote characters stripped. It accepts both single and double quotes, does not support escaping a quote character inside a quoted token, and degrades to treating an unterminated quote's remainder as plain literal text (e.g. `don't` tokenizes as the single literal token `don't`) rather than raising.

## Kind
rule
## Basis
directly_stated
## Evidence
`_TOKEN`'s accompanying comment (parser.py lines 45-81) documents exactly this behavior, including "An unterminated quote ... makes the quoted-group alternative fail; `rest` ... then consumes the stray quote character and everything after it as plain literal text." `test_parser.py::TestQuoting` (lines 120-128) confirms `_pred('"expenses dining"') == Acct("expenses dining")`, `_pred('desc:"whole foods"') == Desc("whole foods")`, and that an *unquoted* two-word input (`"expenses:dining out"`) tokenizes into two separate terms producing `Or((Acct("expenses:dining"), Acct("out")))`.

Evidence-paths: [ledgerkit/query/parser.py:45-97, tests/test_query/test_parser.py:120-128]

## Justification
This explains a subtle but consequential behavior: forgetting to quote a multi-word `acct:`/`desc:` pattern silently produces two separate, OR-combined terms rather than a parse error — worth documenting since it's an easy correctness trap for callers constructing query strings programmatically.

## Examples
`desc:"whole foods"` → one token → `Desc("whole foods")`. `desc:whole foods` (unquoted) → two tokens (`desc:whole`, `foods`) → `Desc("whole")` and `Acct("foods")` (the second token has no recognized prefix and defaults to `acct:`); confirmed by direct execution: `parse("desc:whole foods").predicate == And((Acct("foods"), Desc("whole")))` — these two tokens AND together, they do NOT OR together, because they are two *different* prefix types (`Desc` vs `Acct`), and per query-engine-005's bucketing rule only *same*-prefix unnegated terms OR together. The genuine OR-producing unquoted-two-word example is `"expenses:dining out"` (both tokens default to `acct:`, so they share a prefix type): `parse("expenses:dining out").predicate == Or((Acct("expenses:dining"), Acct("out")))` — this is the example actually confirmed by the cited test (`test_unquoted_two_words_are_two_terms`).

(Reviewed 2026-10-03: the original draft asserted `desc:whole foods` (unquoted) → `Or((Desc("whole"), Acct("foods")))`. This was checked by directly running `ledgerkit.query.parser.parse` and is **incorrect** — it also directly contradicts this same topic's own query-engine-005 bucketing rule, which this assertion's author apparently forgot applies across different prefix types, not just within one. Corrected above; the test-confirmed `"expenses:dining out"` example from this assertion's own Evidence section was substituted as the genuine OR-producing illustration.)

## Counterexamples
None found for the documented tokenizer behavior itself; the module explicitly says escaped quotes are unsupported, matching (per the comment) hledger's own tokenizer limitation rather than a gap introduced here — that comparison itself was not independently re-verified.

## Depends on
query-engine-001, query-engine-005 (the bucketing/combination rule that determines whether two tokenized terms OR or AND together).

## Open questions
The claim that this "mirrors hledger's own tokenizer" is a compatibility claim sourced from the code's own comment, not independently verified against the real hledger binary in this pass.

## Evidence-support state
partially_supported
## Status
verified
## Supersedes
