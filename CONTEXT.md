# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 6 (`tag:NAME[=REGEX]` query-term matching) — **implementation
complete**, by a fresh coding agent (Step 6 of the design → plan →
implement → verify process), per the already-approved design
(`23-tag-query-matching-design.md`, §17: Option A, `accounts`-mode
replication) and implementation plan
(`24-tag-query-matching-implementation-plan.md`, evaluator-API shape
`journal: Journal | None = None`). **Next required step is independent
verification** — a genuinely separate `compat-differential-tester`
dispatch (Stage C Phase 5's own verification-independence process,
`09-compatibility-system.md` §9.6) — **not performed by this session**.

## Where We Are
Both implementation commits are made, about to be pushed (end of this
phase, per the project's standing Commit & Push Cadence rule):
`0523426` (core: commodity-tag substrate, `ledgerkit/tags.py` private
helpers, `Tag` AST node, parser rule, evaluator branches + `journal`
param, `accounts`-mode dispatch, doc sync) and `fa05bbc` (integration:
`tests/fixtures/tags.journal`, `TestQueryAstTagIntegration`,
`TestTagQueryFlag`, 6 compat-register entries at `status: proposed`,
this phase's implementation retro). Full test suite: 827 tests, all
passing (746 before this phase, 81 new). Awaiting the next agent
dispatch (`compat-differential-tester`) to run a real differential
comparison against the pinned hledger 1.52.4 binary and promote the six
`status: proposed` entries to `verified` (or file a mismatch) — do NOT
self-promote any of them in a future session either; that promotion may
only come from that agent's own separately-dispatched output.

## Decisions In Flight
All resolved this session, recorded in `knowledge/DECISIONS.md`
(2026-09-25 entries):
- **Option A** (complete four-source effective-tag semantics) implemented
  in full, not Option B (own-tags-only subset).
- **Evaluator API shape**: `journal: Journal | None = None` on
  `matches_transaction`/`matches_posting` — a real default; `Tag`
  evaluated with `journal=None` raises `ValueError`.
- **`accounts` command mode**: replicates hledger's own narrower
  visibility (transaction-level + account-inherited visible; posting-own
  + commodity-propagated not) via a private
  `_matches_posting_for_accounts` dispatch — not uniform matching.
- **Judgment call** (not pre-resolved by either document): the fourth new
  `ledgerkit/tags.py` helper is named `_effective_tags` (private, leading
  underscore), not the unprefixed `effective_tags` the implementation
  plan's own code sample literally showed — resolved per the design's
  own §9.3 text ("keep ALL new helpers private"), which the plan's
  header text agrees with even though its code sample didn't. Flagged in
  the phase retro, not silently decided.

## Files Currently Relevant
- `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md` — this
  phase's full retro (what shipped, what worked, the one judgment call).
- `dev-docs/compat-register/LK-COMPAT-QUERY-TAG-001.yaml`,
  `-COMBINE-001`, `-INHERIT-001`, `-COMMODITY-001`,
  `LK-COMPAT-PARSER-TAG-COMMODITY-001`, `-ACCOUNTS-001` — all
  `status: proposed`; the next agent's actual work list.
- `tests/fixtures/tags.journal` — the precedence-matrix fixture a
  `compat-differential-tester` dispatch should extend or reuse directly
  against the real hledger binary, per its own header comment.
- `ledgerkit/tags.py` (`_inherited_account_tags`, `_commodity_tags`,
  `_posting_commodities`, `_effective_tags`, `_accounts_effective_tags`),
  `ledgerkit/query/eval.py` (`journal` param, `_matches_posting_impl`,
  `_matches_posting_for_accounts`), `ledgerkit/query/ast.py` (`Tag`),
  `ledgerkit/query/parser.py` (`_build_tag`), `ledgerkit/parser.py`
  (`commodity_comment_target`), `ledgerkit/models.py`
  (`declared_commodity_tags`) — the real implementation, for whoever
  reviews it next.

## Blockers / Open Questions
None blocking further Ledgerkit work in general. The one open item is
process-sequential, not a decision: independent `compat-differential-
tester` verification of the six new `status: proposed` entries has not
happened yet. Until it does, `tag:` should be treated as "implemented,
not yet independently confirmed compatible" — accurate per
`dev-docs/hledger-compatibility.md`'s own wording, which already says
exactly this.

## What NOT To Revisit
- Don't re-litigate Option A vs. B, the evaluator-API shape, or the
  `accounts`-mode decision — all three are closed, implemented, and
  recorded in `knowledge/DECISIONS.md`.
- Don't implement shadowing/exclusion logic into `_effective_tags` "to
  match the manual's override wording more literally" — this was
  deliberately rejected; the manual's prose is not the compatibility
  basis here, the pinned binary's executable behaviour is (design §2.7,
  `knowledge/DOMAIN_RULES.md`'s tag: entry). A future "simplification"
  that adds name-only dedup would be a real regression, not a cleanup.
- Don't self-promote any of the six `status: proposed` compat-register
  entries to `verified` (or even `self-verified`) without an actual
  differential run against the real pinned hledger binary — this
  session's own "executable" evidence citations in those entries are
  honestly sourced from the design's own prior findings and this
  session's own Ledgerkit-only checks, not a real differential run this
  session performed.
- Don't unilaterally split `ledgerkit/reports.py` (~720 lines) or
  `ledgerkit/cli.py` (~510 lines) — both were already over CLAUDE.md's
  300-500 line guidance before this phase; this phase added modestly to
  both without pushing either past a threshold it hadn't already crossed.
  Flagged in the retro for a human decision, not acted on.

## Recent Git State
fa05bbc test: add tag: integration tests, compat-register entries, retro
0523426 feat: implement tag:NAME[=REGEX] query matching (Stage C Phase 6)
0849690 docs: small final correction pass on Stage C Phase 6 tag: design
2d2ebf6 docs: amend Stage C Phase 6 tag: design -- add commodity-tag semantics
7a74056 docs: Stage C Phase 6 -- tag: query-matching context curation + design
