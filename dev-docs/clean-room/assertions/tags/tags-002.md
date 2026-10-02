<!-- producer: assertion-research | topic: tags | dispatch: tags-r2 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | dispatch: tags-r2-review | date: 2026-10-03 -->
# Assertion: tags-002

## Statement
`_effective_tags` performs no shadowing, precedence, or deduplication across its four sources, under ANY circumstance — not only when a tag name is declared with a different value by more than one source (e.g. posting, transaction, and account all declaring a tag named "rate" with different values, where ALL of those (name, value) pairs appear independently in the returned list, not just the "winning" one), but also when two sources declare the exact same (name, value) pair: `_effective_tags`'s implementation is plain `+` concatenation of four lists (`posting.tags + txn.tags + _inherited_account_tags(...) + _commodity_tags(...)`), with no `set`/`dict`/union-style call anywhere in it, so an exact-duplicate `(name, value)` pair from two sources is preserved twice in the output, not collapsed to one.

## Kind
rule

## Basis
directly_stated

## Evidence
The `_effective_tags` docstring (tags.py:218-230) states: "Deliberately **no shadowing/exclusion logic**... This is not an oversight; it is the design's own executable-verified finding... A naive 'highest-priority wins' implementation here would be wrong, not merely a simplification." It further notes hledger's own manual prose ("posting tags override account tags override commodity tags") is contradicted by hledger's actual `Data.List.union` behaviour, which dedups only on the full `(name, value)` tuple, not by name alone — this part of the docstring describes *hledger's* mechanism as background/rationale, not a claim that `_effective_tags` itself replicates that exact-tuple dedup.

The return statement itself (tags.py:232-237) is the dispositive evidence for ledgerkit's own behaviour: `posting.tags + txn.tags + _inherited_account_tags(...) + _commodity_tags(...)` — plain list concatenation via `+`, with no `union`, `set`, or `dict`-keyed collapsing anywhere in the function. This was independently re-verified during review by invoking `_effective_tags` directly with an identical `("rate", "1")` pair declared on all four sources (posting, transaction, account, commodity): the result was `[("rate","1"), ("rate","1"), ("rate","1"), ("rate","1")]` — all four copies retained, none deduplicated. Resolvable entirely from the already-cited source (tags.py:232-237) without needing hledger-binary access; the original "open question" below was answerable from the permitted evidence all along.

Evidence-paths: [ledgerkit/tags.py:210-237]

## Justification
This is an explicit, called-out design decision in the code's own docstring, directly contradicting the human-facing hledger manual's description of override semantics. The plain-`+` return expression contains no de-duplication mechanism of any kind, so the "no dedup" behaviour holds unconditionally — for differently-valued same-name tags (the originally-tested case) and for exact-duplicate `(name, value)` pairs alike (confirmed by direct invocation during review, not merely inferred).

## Examples
`test_unions_all_four_sources_with_no_dedup_by_name` (test_tags.py:245-263) sets posting tag `rate:1`, txn tag `rate:4`, account tag `rate:3`, commodity tag `rate:2`, and asserts the result is `[("rate","1"), ("rate","4"), ("rate","3"), ("rate","2")]` — all four preserved in source order (posting, txn, account, commodity). No test in test_tags.py exercises the exact-duplicate-pair case; that case was confirmed by the reviewer running `_effective_tags` directly against hand-built fixtures with an identical `("rate","1")` pair on all four sources (see Evidence above and `_review.md`), not by a persisted test in test_tags.py.

## Counterexamples
None — no test, nor the reviewer's direct invocation, shows deduplication occurring under any circumstance in `_effective_tags`, including the exact-duplicate-pair case.

## Depends on
tags-001 (the four-source union itself).

## Open questions
None remaining within permitted evidence. The original open question ("would an exact (name,value) duplicate from two sources be deduplicated") has been resolved by review: it is not — `_effective_tags` never deduplicates, by construction (plain `+`, no union/set/dict). This is ledgerkit's own implementation behaviour, confirmed directly from tags.py and by direct invocation; whether this is the *correct* choice relative to hledger's own `Data.List.union` behaviour on exact duplicates is a separate design question this assertion does not adjudicate (out of scope for REVIEW mode and for this module's permitted evidence).

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)
