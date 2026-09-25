# Stage C Phase 6 retro — Implementation (`tag:` query-term matching)

- **Date:** 2026-09-25
- **Commit(s):** `0523426` (core implementation, unit tests, doc sync),
  plus one further commit for compat-register entries and integration
  tests (fixture + `reports.py`/CLI wiring) landed in this same session —
  see `git log` for the exact hash once pushed.
- **Agents used:** none — a single fresh coding-agent dispatch (Step 6 of
  this project's design → plan → implement → verify process), per the
  task's own explicit instruction not to spawn sub-agents for an
  already-fully-specified implementation task.

## Where we are

This is the implementation checkpoint of Stage C Phase 6, following
directly from `STAGE-C-PHASE-6-TAG-QUERY-PLAN.md` (Steps 1-2: context
curation, design document — including its own review-driven amendment and
small-correction passes) and the subsequent, separately-authored
implementation plan (`24-tag-query-matching-implementation-plan.md`,
Step 5 — resolved the one thing the design left open, the evaluator-API
shape). This retro covers Step 6: a fresh coding agent (no access to the
planning conversation's own history — only the two approved documents)
turning that plan into real `ledgerkit/`/`tests/` code. After this phase,
Ledgerkit implements every query term Stage C originally scoped except
`cur:`/`PythonRegex`/the `Query`-as-shim migration — `tag:NAME[=REGEX]`
was the last major gap in the query engine's own term set.

## Goal

Implement `tag:NAME[=REGEX]` end to end per the approved design/plan:
Option A (complete, four-source effective-tag semantics — posting-own,
transaction-own, account-inherited, commodity-propagated, unioned with no
shadowing), `accounts`-mode replication of hledger's own narrower
visibility, and the resolved evaluator-API shape
(`journal: Journal | None = None`) — plus all required tests, doc sync,
and compat-register entries at `status: proposed` only.

## Scope delivered vs planned

Everything in the implementation plan's file-by-file section shipped, in
the order it was written, with no scope cut: `Journal.
declared_commodity_tags`; `parser.py`'s `commodity`-directive same-line +
follow-on comment-tag capture (a new `commodity_comment_target` variable,
deliberately mirroring the existing `account_comment_target` mechanism
rather than inventing a second one); four new private `ledgerkit/tags.py`
helpers (`_inherited_account_tags`, `_commodity_tags`,
`_posting_commodities`, `_effective_tags`, `_accounts_effective_tags` —
five, not four; `_posting_commodities` was a small extraction the plan
flagged as needed "if one doesn't already exist," and none did); the
`Tag` AST node and `_build_tag` parser rule; `matches_transaction`/
`matches_posting`'s new `journal` parameter and `Tag` branches; the
`accounts`-mode dispatch (implemented as a private
`_matches_posting_for_accounts` wrapper sharing one recursive dispatch
via a `tag_source` parameter, rather than a duplicated copy of the
And/Or/Not walk — the plan explicitly left this structural choice to the
implementer's judgment); all four report call sites plus `cli.py`'s
`print` updated to pass `journal=journal`. All six named compat-register
entries created at `status: proposed`, none promoted further. Every test
category the plan's "Tests" section named was implemented (unit:
bare/valued/malformed-regex/empty-value/`not:`/multiple-AND/`==`-split/
`.`-name-pattern/`journal=None` cases; integration: a new
`tests/fixtures/tags.journal` fixture covering all five required
same-name precedence pairs individually, commodity propagation, parent-
account+commodity composition on one posting, all four `accounts`
visibility cells as four separate test methods, and `-q` wiring for all
five commands). Nothing from the plan's "Explicitly out of scope" list
was touched (`cur:`, `payee:`/`note:`, `PythonRegex`, the `Query`-shim
migration, a standalone `--depth`/`-N` flag).

One genuine ambiguity required a judgment call, not resolved by either
the design or the plan explicitly: whether `_effective_tags` (the fourth
new `tags.py` helper) should be private. The design's own §9.3 resolution
text says "keep ALL new inheritance/commodity helpers private" and names
`effective_tags` as one of the three it means — but the plan's file-by-
file section spells it without a leading underscore in the same breath as
three siblings that do have one, under a header literally reading "All
three new helpers **private**." Read most plausibly as the plan simply
carrying the design's own pre-decision illustrative spelling forward by
accident rather than a deliberate reversal of §9.3 (which states no
rationale for singling out exactly one helper as a public exception, and
doing so would contradict the plan's own stated Unauthorised-Change-Rule
discipline). Resolved as `_effective_tags` (private) — the smallest
reasonable reading consistent with both documents' own stated rationale.
Recorded as its own dated entry in `knowledge/DECISIONS.md` per this
project's ambiguity-handling instruction, not silently decided.

## What was achieved

`tag:NAME[=REGEX]` now works identically across `balance`/`register`/
`accounts`/`stats`/`print`, matching hledger's real, executable-verified
effective-tag semantics rather than a disclosed subset — the harder,
more valuable of the two design-approved options. The account-tag
inheritance gap Stage C Phase 4 had knowingly left open (`Journal.
declared_account_tags` parsed but never consumed anywhere) is now closed.
A genuinely new capability, commodity-tag propagation, exists in
Ledgerkit for the first time, built on a substrate (`declared_commodity_
tags`) that didn't exist before this phase at all. The single most
counter-intuitive rule this feature turned on — same-named,
differently-valued tags from different sources are never shadowed, only
unioned, despite the manual's own "override" wording reading the opposite
way — is now both correctly implemented (a plain concatenation, no
dedup-by-name anywhere in the pipeline) and regression-tested explicitly
(`test_no_shadowing_regression_naive_dedup_by_name_would_fail_this`, named
so a future "simplification" that adds shadowing logic fails loudly). The
`accounts` command's own narrower visibility mode is replicated exactly,
via a mechanism (`_matches_posting_for_accounts`) that provably cannot
affect any other command's behaviour, since it's a separate function
`balance`/`register`/`print`/`stats` never call.

Full test suite: 746 tests before this phase, 827 after (81 new), all
passing, including the pre-existing suite unmodified except for the two
files (`test_directives.py`, `test_reports.py`, `test_cli.py`,
`test_tags.py`, `test_query/test_{parser,eval}.py`) this phase added
tests to.

## What worked

- **Mirroring an existing code path instead of inventing a new one**, per
  the plan's own explicit instruction, paid off directly: the commodity-
  directive tag-capture mechanism (`commodity_comment_target`) is a
  near-exact structural copy of the account-directive one
  (`account_comment_target`), which meant the risk of a subtle new
  parser-state bug was much lower than a from-scratch design would have
  carried — and it was fast to implement and test correctly on the first
  pass.
- **Writing manual sanity-check scripts before writing formal tests**
  (e.g. constructing the precedence fixture in a scratch Python script
  and printing `_effective_tags`'/`matches_posting`'s output directly)
  caught the exact shape of `accounts`'s four-way split and the `not:tag:
  rate=3` account-wide-exclusion behaviour *before* committing to
  specific test assertions — one assertion in the CLI test suite
  (`test_not_tag_negation`) was written wrong on the first pass (assuming
  only `assets:bank:savings` would be excluded) and caught this way
  rather than as a test failure discovered later.
- **The design/plan's own extremely thorough, dated, amendment-tracked
  history** made this phase genuinely low-ambiguity — only one real
  judgment call was needed across the whole implementation (the
  `_effective_tags` naming question above), and even that had a strong
  textual basis to resolve from, not a coin flip.

## What didn't work

No misfires this phase. The one place effort was spent that didn't
directly ship a feature was re-deriving, by hand, the exact expected
`balance()`/`accounts()` output for several precedence-matrix scenarios
before writing assertions — necessary given the feature's own
counter-intuitiveness, not wasted, but worth noting as real time spent
that a less novel feature wouldn't have needed.

## Lessons learnt

- When a design document's own resolved text and its downstream
  implementation plan's illustrative code samples disagree on a small,
  easily-overlooked detail (here: one identifier's leading underscore),
  the design's own *prose resolution* — not the plan's *code sample* —
  is the more authoritative source, especially when the plan states no
  independent rationale for the apparent reversal. Treat a plan's code
  samples as illustrative shorthand unless the plan explicitly says it is
  deciding something the design left open.
- A private, `accounts`-only dispatch variant that shares its recursive
  tree-walk with the public function via one extra parameter (here:
  `tag_source` threaded through `_matches_posting_impl`) is a small,
  reusable pattern worth remembering for the next time a report function
  needs a narrower semantics for exactly one predicate node type without
  touching a documented public signature at all.

## Process-improvement feedback

No process notes this phase — the design → plan → implement handoff
worked cleanly with a fresh agent that had zero access to the planning
conversation, which is exactly what this process is meant to prove out.
One observation for whoever runs the next verification step: this
session's own "executable evidence" citations in the six new
compat-register entries are honestly labelled as NOT a real differential
run against the pinned hledger binary this session (no binary access was
exercised by this implementing agent) — they cite the design's own prior
executable findings plus this session's own Ledgerkit-only checks. The
`compat-differential-tester` dispatch that comes next should treat these
entries' `evidence` sections as a starting point for what to re-run, not
as already-independent confirmation.

## Learnings filed

- `knowledge/DECISIONS.md`: four new dated entries — Option A over
  Option B (why); evaluator-API shape (`journal: Journal | None = None`
  over a context object or pre-materialised storage); `accounts` mode
  replication over uniform matching; and the `_effective_tags`
  private-naming judgment call.
- `knowledge/DOMAIN_RULES.md`: one new entry covering the four
  inheritance rules, the always-AND-never-OR combination rule, commodity-
  tag propagation, the `accounts` visibility split, and the union-not-
  shadowing precedence finding — flagged as the single most
  counter-intuitive rule in the entry, matching the design's own framing.

## Where we're going

Independent verification (a genuinely separate `compat-differential-
tester` dispatch, per Stage C Phase 5's own verification-independence
process, `09-compatibility-system.md` §9.6) is the mandatory next step —
**not performed by this session**, and no compat-register entry here was
promoted past `status: proposed`. Once that verification lands (or finds
a mismatch), the six new entries move to `verified` (or a filed
mismatch), `dev-docs/hledger-compatibility.md`'s `tag:`-related rows get
their final cross-links, and this phase can be considered for `[DONE]` —
which remains the user's own call to make, not inferred here. `cur:`,
`PythonRegex`, and the `Query`-as-compatibility-shim migration remain
Stage C's own unscoped follow-on work, untouched by this phase.

## Time / cost note

One continuous session, no sub-agent dispatches. The bulk of the effort
was the commodity-tag substrate (new parser state, new Journal field, new
tags.py helpers) and the precedence-matrix test fixture construction —
both directly scoped by the plan, neither a surprise. Roughly in line
with the plan's own implied scope (five file-by-file sections, six
compat-register entries, a full new test matrix); no rework was needed
once the fixture's expected values were manually verified before the
first test assertion was written.
