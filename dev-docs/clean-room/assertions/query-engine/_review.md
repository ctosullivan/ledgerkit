<!-- producer: domain-skeptic (REVIEW mode) | topic: query-engine | date: 2026-10-03 -->
# Review note: query-engine assertions (001-015)

## Scope
Reviewed all 15 draft assertions (`query-engine-001.md` through `query-engine-015.md`)
against their cited evidence, restricted to the same permitted-evidence-paths
list the assertion-research dispatch used:
- `ledgerkit/query/` (ast.py, parser.py, eval.py, depth.py, regex.py, compat.py, __init__.py)
- `tests/test_query/` (test_parser.py, test_eval.py, test_regex.py, test_compat.py)

No legacy documentation, compat-register, planning docs, or other out-of-scope
paths were opened. Where an assertion's own Open Questions already correctly
scoped an external hledger-fidelity claim as unverified from this pass, that
scoping was left as-is (it is correct, not a finding).

## What I checked
For every assertion: re-read the cited source line ranges directly and
confirmed they say what the assertion claims they say; re-read every cited
test and confirmed it asserts what the assertion claims it asserts;
cross-checked line-number citations against the actual files; looked for
contradictions between assertions in the same topic (especially 001 vs
__init__.py, 005 vs 006, 010 vs 011, 003 vs the parser's actual loop); and,
for every "X always does Y" claim, tried to construct a counterexample within
the permitted evidence paths, including by directly executing the permitted
source code (not just reading it) where the test suite's own coverage was
thin or silent.

Line-number citations were, overall, unusually precise — most test-file
citations I checked matched exactly or within one line, including non-trivial
ones like 013's "18 individually named rejection cases" / "13 ... acceptance
regression-guards" counts, which I counted by hand and both matched exactly.

## What I found and fixed

1. **query-engine-001 (AST node set), Counterexamples field** — the draft
   claimed `ledgerkit/query/__init__.py`'s `__all__` list "matches this same
   set exactly" (the nine node types). Checked directly against
   `ledgerkit/query/__init__.py:22-46`: false — `__all__` is a strict
   superset, also exporting `TxnStatus`, `QueryNode`, `QueryPlan`,
   `DepthSpec`, and eight functions/exceptions. The assertion's core
   Statement (nine node types, no tenth) is unaffected and remains correct;
   fixed the over-claimed sub-point in place.

2. **query-engine-006 (tokenizer), Examples field** — the draft asserted
   `desc:whole foods` (unquoted) parses to
   `Or((Desc("whole"), Acct("foods")))`. This is wrong, and it directly
   contradicts this same topic's own query-engine-005 bucketing rule (only
   *same*-prefix unnegated terms OR together; different prefix types AND).
   Confirmed by running `ledgerkit.query.parser.parse("desc:whole foods")`
   directly: the real result is
   `And((Acct("foods"), Desc("whole")))`. Fixed the example and substituted
   the already-test-confirmed genuine OR-producing case
   (`"expenses:dining out"` → `Or((Acct("expenses:dining"), Acct("out")))`,
   both tokens defaulting to `acct:`) as the correct illustration.

3. **query-engine-014 (DepthSpec specificity rule), Statement + Evidence +
   Counterexamples** — the draft stated the specificity tie-break backward:
   "the one whose matched ancestor is *shallowest* (lowest index) wins,"
   which directly contradicts its own next clause ("no strict ancestor" =
   "maximally specific") — a no-ancestor-match is assigned the *highest*
   specificity value in the code, not the lowest. Also found, while
   resolving this: **no test anywhere in `tests/test_query/` exercises
   `clipped_depth_for_account`, `clip_account_name`, or
   `account_excluded_by_depth` at all** (confirmed by grep) — the only cited
   test evidence (`test_multiple_flat_depth_terms_take_the_minimum`) covers
   only `merge_depth_specs`'s flat-min rule, nothing about the
   specificity/tie-break/clip-rendering claims the bulk of the Statement
   makes. Resolved both by directly executing `clipped_depth_for_account`
   with several inputs (documented in the file's Evidence section) —
   confirmed the correct direction (deepest-ancestor-or-no-ancestor-match
   wins) and the later-entry tie-break rule. Fixed the Statement, Evidence,
   and Counterexamples fields; left Evidence-support state at
   `partially_supported` (the pre-existing hledger-fidelity open question for
   `account_excluded_by_depth` is unrelated and still stands) but added a
   second, new Open Question naming the test-coverage gap explicitly.

## What I did not find
No other line-citation errors, no other wrong code-behavior claims. Specific
things I actively tried to break and could not:
- Re-ran `parse()` on a three-date `date:` string to confirm query-engine-007's
  claimed `QueryParseError` counterexample really raises (it does).
- Re-ran `clipped_depth_for_account` on tie cases in both declaration orders
  to confirm the "later entry wins" tie-break (confirmed both directions).
- Checked eval.py's `And`/`Or` short-circuiting against query-engine-004's
  "Tag raises ValueError if evaluated with journal=None" claim — the wording
  ("if evaluated") already correctly allows for short-circuit avoidance, so
  no fix needed.
- Checked query-engine-010/011's reliance on `ledgerkit.tags` (outside the
  permitted paths) — both assertions already correctly scope their Open
  Questions to "this documents only how eval.py's Tag branch *consumes* that
  function's result, not its internal algorithm," and the behavioral claims
  they do make (four independently-matchable sources, no shadowing, the
  narrower accounts-mode view) are fully confirmed by `test_eval.py`'s own
  fixtures, which are in-scope. No fix needed.

## Flagged, not escalated (no genuine ambiguity)
The query-engine-014 test-coverage gap (point 3 above) is a definite finding,
not an ambiguity — I was able to resolve the specific claim at issue by direct
execution. But the broader absence of unit tests for
`clipped_depth_for_account`/`clip_account_name`/`account_excluded_by_depth`
in `tests/test_query/` is outside REVIEW mode's write permissions (read-only
toward `tests/`) and should be handed to whoever owns follow-up test work.

## Escalating to the lead
Nothing. Every finding in this pass was resolvable from within the permitted
evidence paths by reading the cited lines directly, reading/counting the
cited tests directly, or executing the permitted source code directly — no
genuine unresolved ambiguity remains.
