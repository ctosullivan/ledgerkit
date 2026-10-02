<!-- producer: assertion-research | topic: query-engine | dispatch: qe-depthspec-014 | date: 2026-10-02 -->
# Assertion: query-engine-014

## Statement
`DepthSpec` (`depth.py`) is explicitly never a selection filter — it is a report-display clipping/aggregation option, deliberately separate from the predicate AST. It has two fields: `flat: int | None` (a general clip) and `by_pattern: tuple[tuple[str, int], ...]` (ordered `(regex, depth)` pairs from `depth:REGEX=N` terms). `merge_depth_specs` combines two specs by taking the MINIMUM of their `flat` values (None-tolerant) and concatenating `by_pattern`. `clipped_depth_for_account` resolves one account's effective clip depth using a counterintuitive specificity rule: among `by_pattern` entries matching the account (or any strict ancestor), the one whose matched ancestor is *deepest* (highest index) wins — equivalently, a pattern that only starts matching once you climb further up the ancestor chain (or that matches no strict ancestor at all) is treated as MORE specific, not less; a pattern matching the account itself but no strict ancestor is the single most-specific case of all (its specificity value is a sentinel strictly greater than any real ancestor index). Ties go to the later-declared `by_pattern` entry. If no `by_pattern` entry matches, `flat` is the fallback; if that's also `None`, the account isn't clipped. `clip_account_name` renders depth 0 as the literal string `"..."` — never an empty string, never exclusion.

(Reviewed 2026-10-03: the original draft stated the opposite direction — "the one whose matched ancestor is *shallowest* (lowest index) wins" — which directly contradicted its own next clause ("no strict ancestor" = "maximally specific"), since the code assigns the sentinel its *highest*, not lowest, specificity value. Corrected after directly executing `clipped_depth_for_account`; see Evidence.)

## Kind
rule
## Basis
directly_stated
## Evidence
`DepthSpec`'s docstring (depth.py lines 26-45) states the specificity rule and tie-breaking explicitly, and — on its own, careful re-reading — is actually consistent with the corrected direction above ("the one with the **greatest** specificity wins ... a pattern that only matches deep/specific text is *more* specific, not less"); the error identified in this review was in the assertion's own prior paraphrase, not in the source docstring. `merge_depth_specs` (lines 59-76): `flat = min(a.flat, b.flat)` when both are set, with None-passthrough otherwise, and `by_pattern=a.by_pattern + b.by_pattern`. `clipped_depth_for_account` (lines 89-117) implements the rule via `specificity = len(ancestors) + 1` as the no-ancestor-match sentinel (strictly greater than any real 1-based ancestor index `i`), selecting the entry with `specificity >= best_specificity` (so ties go to the later-declared entry, since `>=` always overwrites on a tie). `clip_account_name` (lines 159-171): `if depth == 0: return "..."`.

Test confirmation (pre-existing): `test_parser.py::test_multiple_flat_depth_terms_take_the_minimum` (lines 84-91) confirms `depth:3 depth:1` and `depth:1 depth:3` both yield `DepthSpec(flat=1)`, order-independent — but this only exercises `merge_depth_specs`'s flat-min rule.

**Gap found in this review**: no test anywhere in `tests/test_query/` exercises `clipped_depth_for_account`, `clip_account_name`, or `account_excluded_by_depth` directly (confirmed by grepping the whole directory for their names — zero hits outside `depth.py` itself). The specificity-direction claim above was therefore unverifiable from the assertion's own cited test evidence; it is resolved here instead by directly executing the function in this review pass:
```
DepthSpec(by_pattern=(('assets', 1), ('savings', 2)))  on 'assets:bank:savings' -> 2   # "savings" (no ancestor match) beats "assets" (shallow-ancestor match)
DepthSpec(by_pattern=(('assets', 10), ('bank', 20)))   on 'assets:bank:savings' -> 20  # "bank" (matches deeper ancestor, i=2) beats "assets" (matches shallower ancestor, i=1)
DepthSpec(by_pattern=(('savings', 2), ('ving', 5)))    on 'assets:bank:savings' -> 5   # tie (both no-ancestor-match) -> later-declared entry wins
DepthSpec(by_pattern=(('ving', 5), ('savings', 2)))    on 'assets:bank:savings' -> 2   # same tie, reversed declaration order -> later-declared entry wins again
```
These confirm both the corrected specificity direction and the later-entry tie-break rule, and match the module's own worked example (`assets=1` vs `savings=2` on `assets:bank:savings`) cited in `clipped_depth_for_account`'s docstring.

Evidence-paths: [ledgerkit/query/depth.py:1-171, tests/test_query/test_parser.py:84-102]

## Justification
`account_excluded_by_depth` (depth.py lines 120-156) is a third, distinct depth function in this module — documented as the ONE genuine exception to "depth never excludes," used only by `reports.stats()`. It implements real boolean exclusion, unlike `clipped_depth_for_account`/`clip_account_name`'s pure display-truncation semantics — conflating these three functions would be a real correctness bug for anyone extending `stats()`-adjacent code.

## Examples
`clip_account_name(DepthSpec(flat=0), "assets:bank")` → `"..."`. `clipped_depth_for_account(DepthSpec(by_pattern=(("assets", 1), ("savings", 2))), "assets:bank:savings")` → `2` (confirmed by direct execution in this review).

## Counterexamples
None found for `merge_depth_specs` (directly tested, `test_parser.py` lines 84-91/93-102). For `clipped_depth_for_account`/`clip_account_name`/`account_excluded_by_depth`, there is no test-suite counterexample search possible at all, because **no test exercises these three functions** — this review closed that gap for the specificity-direction claim specifically via direct execution (see Evidence), but the underlying absence of unit-test coverage for `clipped_depth_for_account`/`clip_account_name`/`account_excluded_by_depth` in `tests/test_query/` remains and is flagged below.

## Depends on
query-engine-003.

## Open questions
1. (Pre-existing) `account_excluded_by_depth`'s docstring claims its exclusion decisions were verified to reproduce hledger's exact `stats` output on real scenarios against a pinned binary — this specific fidelity claim was not independently re-checked in this research pass (it would normally be grounded in a compat-register entry, out of scope here).
2. (New, found in this review) `tests/test_query/` has no dedicated unit tests for `clipped_depth_for_account`, `clip_account_name`, or `account_excluded_by_depth` — only `merge_depth_specs` and the parser-level `DepthSpec` construction are tested. This review resolved the one specific behavioral claim this assertion makes about `clipped_depth_for_account` via direct execution, but the broader test-coverage gap itself is a process/quality finding, not something REVIEW mode can fix (no write access to `tests/`) — flagged to the lead for a follow-up test-addition task.

## Evidence-support state
partially_supported
## Status
verified
## Supersedes
