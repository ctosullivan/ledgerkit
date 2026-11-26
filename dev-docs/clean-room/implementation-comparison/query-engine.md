---
role: domain-skeptic
mode: comparison
topic: query-engine
dispatch-id: plan29-phase-comparison-query-engine-20261114
date: 2026-11-14
---

# Implementation comparison: `query-engine` — snapshot `query-engine-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/query-engine-v1.md` +
  `query-engine-v1.sidecar.json` (15 assertions, frozen
  2026-10-02T16:50:03Z, repository revision
  `51881415a204af8908834ec602a54f6e1f67dbdd`).
- The 15 frozen assertion files under
  `dev-docs/clean-room/assertions/query-engine/`.
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/query-engine.md`
  (dispatch timestamp 2026-10-02T16:55:18Z, model-blind, evidence basis:
  `ledgerkit/query/*.py` + `tests/test_query/test_{parser,eval,regex,compat}.py`
  plus live execution of `ledgerkit.query` functions in-checkout — no
  access to the snapshot or assertions).

**Method.** Neither artefact was revised to force agreement. No source
or test file was read directly by this dispatch (comparison mode
compares the two clean-room artefacts only); all findings below rest on
what each artefact itself states. Several of the frozen assertions
(002, 006, 014) carry an inline "(Reviewed 2026-10-03: ...)" note from
an earlier `domain-skeptic` REVIEW-mode pass that already corrected a
draft error before freezing — those corrected statements are what is
compared here, not the pre-correction drafts.

## Classification summary

| Assertion | Kind | Classification |
|---|---|---|
| query-engine-001 | definition | aligned |
| query-engine-002 | boundary | aligned |
| query-engine-003 | invariant | aligned |
| query-engine-004 | invariant | aligned |
| query-engine-005 | rule | aligned |
| query-engine-006 | rule | aligned |
| query-engine-007 | rule | aligned |
| query-engine-008 | rule | aligned |
| query-engine-009 | rule | aligned |
| query-engine-010 | rule | aligned |
| query-engine-011 | relationship | aligned |
| query-engine-012 | rule | aligned |
| query-engine-013 | rule | aligned |
| query-engine-014 | rule | aligned |
| query-engine-015 | rule | aligned |

**15 aligned / 0 partial / 0 conflicting / 0 not_implemented / 0
insufficiently_verified.**

No conflicting or not_implemented findings to report for this topic.
That said, the 15 assertions differ in *how strongly* the
reconstruction corroborates them — see per-assertion notes below; a
genuine methodological distinction, not a disguised partial/conflict.

## Per-assertion notes

**query-engine-001** (nine frozen AST node types + `QueryPlan`, no
shared superclass). Reconstruction §1–§2 independently confirms the
same nine-type enumeration, `frozen=True` on each, and explicitly notes
`QueryNode` is "a `typing.Union`... not a base class — no shared
superclass, no shared method; dispatch everywhere is `isinstance`
chains" — matching the assertion's "none of them perform validation or
evaluation themselves." Aligned.

**query-engine-002** (`MaxAccountLevel` unreachable from the string
parser; Python-construction only). Reconstruction §2 independently
live-tested this exact boundary: `parse("level:2")` and
`parse("depth:2")` "never produce a `MaxAccountLevel` node," and states
the node is "reachable only by constructing it directly in Python."
This is a direct, independent live-execution match to the assertion's
core claim (the assertion's own evidence was code-reading plus an
existing test; the reconstruction adds an independent execution of the
exact same boundary without having seen the assertion). Aligned.

**query-engine-003** (`depth:` terms never enter the predicate tree; a
depth-only query yields `predicate == And(())`). Reconstruction §5
independently ran `parse("depth:2")` and got
`QueryPlan(predicate=And(()), depth=DepthSpec(flat=2))` — an exact,
independent live-execution match. Aligned.

**query-engine-004** (`Tag` evaluation requires `journal`; every other
node type is unaffected by `journal=None`). Reconstruction §5 states,
from direct reading of `eval.py`, that both `matches_transaction` and
`_matches_posting_impl` "raise `ValueError("tag: matching requires
journal context")` the moment a `Tag` node is reached with
`journal=None`," and cites the same two named tests the assertion does.
Aligned.

**query-engine-005** (same-type unnegated terms OR together; any
`Not`-wrapped term, regardless of inner prefix, always lands in the AND
list rather than the OR bucket). Reconstruction §5 independently ran
`parse("acct:a desc:b acct:c")` and got
`And((Or((Acct('a'), Acct('c'))), Desc('b')))` — an exact match to the
assertion's own stated example, confirming the unnegated-same-prefix-OR
half directly. The negated-same-prefix-AND half is not independently
re-executed in the reconstruction's §5, but §6 confirms (from reading
the test body, not just its name) that `test_parser.py` contains "the
full depth-term matrix... same-prefix OR vs. negated-same-prefix AND
(the "central footgun" test explicitly named as such)," and the
reconstruction's own full-suite run (200/200 passing) covers that test.
Aligned, with the OR-half independently live-verified and the AND-half
corroborated by test-body reading plus a passing full-suite run rather
than a fresh independent execution.

**query-engine-006** (tokenizer quoting: `prefix:"phrase"` collapses to
one token; unterminated quote degrades to literal text rather than
raising; trailing text after a closed quote is absorbed). This
assertion was itself corrected in an earlier REVIEW pass (the
`desc:whole foods` unquoted example was wrong and was replaced with the
`"expenses:dining out"` example). Reconstruction §5 independently ran
the *exact* set of `_tokenize` probes the corrected assertion relies on
(`'acct:"expenses dining" out'`, `"don't"`, `'a"b'`,
`'desc:"foo"bar'`) and got identical outputs, and separately confirms
`parse("expenses:dining out").predicate ==
Or((Acct("expenses:dining"), Acct("out")))`. This is a strong,
independent live-execution match to the corrected (not the original
draft) assertion text. Aligned.

**query-engine-007** (`date:` accepts exactly four shapes; a bare date
becomes `[D, D+1day)`; a written range's end is the literal bound, not
auto-incremented; year must be 4 digits). Reconstruction does not
re-execute `date:` parsing directly in its own live-execution section,
but §6 states (from reading the test bodies, not just names) that
`test_parser.py` asserts "the full depth-term matrix... the four
date-span shapes plus the "written range bound is not auto-incremented
but a bare single date is" distinction," and the full 200-test suite
passed. Aligned — via test-body reading and a passing full-suite run
rather than independent re-execution of this specific behaviour.

**query-engine-008** (`depth:`/`tag:` both split on the *first* `=`
only; `not:depth:...` rejected at parse time regardless of wrap count).
Reconstruction §6 independently names "the full `tag:` grammar including
the `tag:rate==0.05` first-`=`-only split" as a test body it read
directly, and §5/§7 item 10 independently confirms (live, and by
reading `_wraps_depth`'s loop) that `not:depth:...` is rejected at parse
time and that the rejection logic "by inspection... handles an
arbitrary wrap count," while also noting — consistent with the
assertion's own Evidence section, which cites only one- and two-wrap
tests — that three-or-more-wrap rejection is confirmed by code reading
in both artefacts, not by execution in either. Aligned, with both
artefacts independently landing on the identical "tested to two wraps,
confirmed-by-reading beyond that" boundary rather than one silently
resolving what the other left open.

**query-engine-009** (`Acct`/`MaxAccountLevel` use an any-posting rule
at the transaction level vs. single-posting at the posting level;
`Desc`/`DateSpan`/`Status` are identical at both levels; matching is
always case-insensitive infix `.search()`, never `.match()`/
`.fullmatch()`). Reconstruction §6 states it read `test_eval.py`
directly and confirms it "asserts `matches_transaction`'s "any posting
matches" rule for `Acct`/`MaxAccountLevel`, `Desc`/`Status`
posting-inheritance." Aligned — via test-body reading and a passing
full-suite run; the case-insensitive-`.search()`-only claim specifically
is not independently re-executed by the reconstruction, but nothing in
it contradicts that claim either.

**query-engine-010** (`Tag` matching uses the full four-source
"effective tags" union with no shadowing/dedup by name; transaction-level
match is an explicit two-part OR). Reconstruction §6 independently
describes reading "a 20+ test `Tag` suite built around a single fixture
with a *different* `"rate"` value at each of the four effective-tag
sources... explicitly designed... to catch a "highest-priority-wins"
bug," which is the same test and the same framing the assertion cites.
Both artefacts independently disclose the identical scope boundary: the
underlying `_effective_tags`/`_accounts_effective_tags` computation
itself lives in `ledgerkit/tags.py`, outside both dispatches' permitted
evidence paths (assertion's own "Open questions"; reconstruction §4's
"I did not read [`ledgerkit/tags.py`]... and cannot independently
confirm those symbols' own behavior"). This is itself a form of
alignment — neither artefact claims more than `eval.py`'s own
consumption of that result, which both confirm. Aligned.

**query-engine-011** (`_matches_posting_for_accounts` is a second,
private posting-matcher sharing one dispatch body with `matches_posting`
via a `tag_source` parameter, differing only in which effective-tags
function it calls for `Tag` nodes). Reconstruction §2 independently
states `_matches_posting_for_accounts` exists in `eval.py` and is, "per
its own docstring, used only by `ledgerkit.reports.accounts`" — the same
caller-side claim the assertion makes, and both artefacts independently
flag that caller as unverified (outside permitted evidence paths in
both dispatches). The reconstruction does not independently re-execute
the specific accounts-mode tag-visibility narrowing (no equivalent to
its depth.py live-execution probes for this function), relying instead
on reading the module structure and test-body names in §6 ("the
separate narrower `_matches_posting_for_accounts` visibility mode").
Aligned, with the shared-dispatch-body structural claim confirmed
directly and the specific tag-narrowing behaviour corroborated more
lightly (reading, not execution).

**query-engine-012** (six excluded `HledgerRegex` construct families:
inline-flag/group/lookaround constructs, numeric backreferences, GNU
`\<`/`\>` word boundaries, Perl shorthand classes, POSIX named classes,
lazy quantifiers). Reconstruction §6 independently enumerates, from
reading `test_regex.py` directly, "a construct-by-construct accept/reject
matrix (inline flags, named/non-capturing groups, lookahead,
backreferences, GNU word boundaries accepted as `\b` but a separate
`\<`/`\>` form rejected, Perl classes, POSIX classes, lazy
quantifiers)" — a near-verbatim match to the assertion's six-family
list, including the specific `\b`-accepted-but-`\<`/`\>`-rejected
detail. Aligned.

**query-engine-013** (empty-string pattern rejected but
empty-match-admitting patterns like `.*` remain valid; empty-alternation
branches rejected via an escape-aware scan, not a single compiled
regex; 18 named reject cases / 13 named accept cases). Reconstruction
§6 independently reports reading `test_regex.py` and finding "the
empty-pattern-string rejection (distinguished explicitly from patterns
that merely *admit* an empty match, e.g. `.*`, `a*`, `()`, which remain
accepted), and an 18-pattern reject-list / 13-pattern accept-list for
the empty-alternation-branch rule, each as its own named test" — an
exact match, including the 18/13 counts. Aligned.

**query-engine-014** (`DepthSpec` specificity rule: the `by_pattern`
entry whose matched ancestor is *deepest*, or that matches no strict
ancestor at all — the sentinel case — wins; ties go to the
later-declared entry; `clip_account_name` renders depth 0 as the
literal string `"..."`). This is the one assertion the earlier REVIEW
pass had to actively correct (the draft had the specificity direction
backwards) and flagged a gap: no test in `tests/test_query/` exercises
`clipped_depth_for_account`/`clip_account_name`/`account_excluded_by_depth`
directly, so the corrected direction was verified by direct execution
in that REVIEW pass rather than by a pre-existing test. The
reconstruction — with no access to the assertion, the review note, or
the correction — independently ran the *same* worked example
(`DepthSpec(by_pattern=(("assets", 1), ("savings", 2)))` on
`"assets:bank:savings"`) and got the identical result (`2`, "savings"
wins), independently ran an additional tie-break probe
(`DepthSpec(by_pattern=(("assets", 1), ("assets", 5)))` → `5`, later
entry wins) matching the corrected assertion's own tie-break claim, and
independently confirmed `clip_account_name(DepthSpec(flat=0), ...)` →
`"..."`. The reconstruction also independently found the identical
test-coverage gap: "No dedicated unit tests, among the four permitted
test files, for `depth.py`'s three core clipping/exclusion functions"
(§6–§7), confirmed by grepping the test directory for the three function
names. This is the strongest corroboration among all 15 assertions —
two independently-dispatched, model-blind processes reached the
identical corrected numeric result and the identical coverage-gap
finding by two different routes (a REVIEW-mode correction vs. a
from-scratch reconstruction). Aligned.

**query-engine-015** (`compat._query_to_ast` field mapping;
`query.depth` never translated; eager per-field validation via
`_validated`; `date_to` inclusive→exclusive conversion with a
`date.max`→`None` special case to avoid `OverflowError`).
Reconstruction §6 independently reports reading `test_compat.py` and
finding "`_query_to_ast` translation of every `Query` field alone and in
combination, the inclusive→exclusive date translation (including the
`date.max` overflow-avoidance case), and eager (translation-time, not
evaluation-time) validation failures for excluded regex constructs and
empty patterns" — matching the assertion's claims field-for-field.
§1/§4 additionally independently confirm `compat.py`'s import structure
(`TYPE_CHECKING`-only reference to `Query`, no runtime import, to avoid
a circular import with `eval.py`), consistent with but not itself part
of the assertion's own Statement. Aligned.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification**. All
15 classifications above are `rule`/`invariant`/`boundary`/`relationship`
kind except query-engine-001 (`definition`); for every one of them,
"aligned" means only that the independently-reconstructed as-built
behaviour currently matches what the snapshot asserts — it does not, by
itself, establish that the asserted rule is the *right* one relative to
real hledger's own query semantics. Both artefacts are explicit, in
their own text, about this boundary: query-engine-002, -005, -006, -007,
-009, -012, -013, and -014's own "Open questions" sections each
separately flag that the underlying hledger-fidelity claim for their
respective design decision was sourced from an out-of-scope planning
document and not independently re-verified against the real hledger
binary; the reconstruction report independently never claims such
fidelity either (its evidence basis is explicitly limited to
`ledgerkit/query/*.py`, the four permitted test modules, and live
execution of this checkout's own code). This comparison report
preserves that distinction rather than collapsing "matches the code"
into "is correct relative to hledger."

A second, narrower caveat specific to this topic: several "aligned"
classifications above (007, 008's three-plus-`not:`-wrap case, 009, 010,
011, 012) rest on the reconstruction having read test bodies directly
and run the full permitted test suite (200/200 passing) rather than
having independently re-executed that specific behaviour live, the way
it did for 002, 003, 004, 005 (OR-half), 006, and 014. This is disclosed
above per assertion rather than folded uniformly into "aligned" — it is
a real difference in verification strength, not a difference in
classification outcome, and no assertion's classification changes as a
result.

## What was checked

- All 15 assertion `Statement`/`Evidence`/`Examples`/`Counterexamples`
  fields (including the two inline post-REVIEW corrections already
  present in query-engine-002, -006, and -014's own files) against the
  reconstruction report's §1–§8 content, assertion-by-assertion.
- Whether either artefact's stated open questions or caveats (the
  hledger-fidelity sourcing disclaimers common to most assertions; the
  caller-side-unverified disclaimers in query-engine-010, -011, -014,
  -015; the no-test-coverage-for-depth-functions gap in query-engine-014)
  were silently resolved one way or the other by the other artefact —
  they were not; in every case both artefacts independently land on the
  same unresolved boundary, which is recorded above as part of the
  alignment rather than suppressed.
- Specifically cross-checked query-engine-014's corrected specificity
  direction and tie-break rule against the reconstruction's independent
  live-execution results — identical outputs, strengthening (not merely
  not-contradicting) the correction made in the earlier REVIEW pass.
- No contradiction, partial divergence, or not-implemented claim was
  found between the frozen snapshot's 15 assertions and the independent
  reconstruction for this topic.

## Escalations

None. No genuine conflicting or not_implemented classification arose
for this topic; nothing is escalated to the lead.
