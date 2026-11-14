# CodeCompass upgrade + clean-room documentation reconstruction — closeout retro

- **Date:** 2026-11-14
- **Commit(s):** `0c89ceb` (Phase 1) through this retro's own commit; the
  full initiative spans `4277036`/`e1b0144`/`7032b3e` (the twice-amended
  governing plan itself) through `63d310f` (Phase 5's closeout) and this
  response's Phase 6/final commit.
- **Agents used this closeout task specifically:** `release-phase-auditor`
  (the Phase 6 independent audit), `roadmap-context-curator` (the
  deferred learning-triage pass). Individual phases' own retros
  (`dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md` through `-5.md`)
  document each phase's own agent usage in full (`implementation-
  reconstructor`, `domain-skeptic` in both modes, `docs-maintainer` in
  Legacy Reconciliation Mode, dozens of fresh `general-purpose`
  assertion-research dispatches); this retro is the initiative-level
  synthesis, not a re-narration of each phase.

## Where we are

This initiative is now complete across all six planned phases,
independently audited, and fully reconciled at both the per-document and
initiative-wide level. It is tracked in `ROADMAP.md`'s new "Tooling &
Process Initiatives" section (added this phase, per the plan's own §8
item 1 resolution) rather than consuming a Stage letter — it ran before
Stage D specifically so that Stage D onward doesn't keep compounding
documentation drift against a stale baseline. This retro closes out the
initiative as a whole, distinct from, and synthesising across, every
individual phase's own retro — none of which are rewritten or superseded,
per this project's "never rewrite a past retro, only add" rule.

## Goal

Two governing objectives, stated at the top of the (twice-amended)
plan: (1) reconcile and mechanically re-pin CodeCompass and
`codecompass-template` against this project's own CLAUDE.md state; (2)
reconstruct Ledgerkit's human-facing documentation from scratch, via a
genuinely evidence-backed, legacy-blind clean-room process — never
copying forward an existing claim without independently re-deriving it
— then reconcile that clean-room result against the documents it
replaces, closing the loop with an independent, separately-reported
final audit.

## Scope delivered vs planned

Delivered exactly the twice-amended plan's six phases, with zero scope
dropped and one deliberate, recorded addition (the `check_snapshot.py`
`external_repositories` resolver, needed once a topic's evidence spanned
more than one git repository — a mechanical tooling extension within
the checker's own stated spirit, not a plan deviation). Every phase's
own acceptance criteria were met and independently verified at Phase 6,
not merely self-reported:

- **Phase 1** — CodeCompass/`codecompass-template` reconciled and
  mechanically pinned (not merely recorded); four existing agent briefs
  hand-merged; two new roles (`implementation-reconstructor`,
  `domain-skeptic`) added, reconciled from upstream rather than
  blind-copied.
- **Phase 2** — the isolation workflow adopted; `check_snapshot.py`
  built with all six fail-closed conditions and proven via a
  self-test battery; the real isolation tier (`best-effort`) determined
  empirically, never assumed.
- **Phase 3** — the full per-topic evidence-backed reconstruction
  pipeline run for all 10 bounded topics: 102 assertions, each
  independently reviewed, mechanically frozen, checker-validated, then
  independently (model-blind) reconstructed and compared for alignment.
  3 contamination/content-loss events, all correctly discarded and
  rerun per the plan's own mechanical rule — including once where the
  dispatch's own output looked completely clean, applied anyway. 97
  aligned / 9 partial / 5 insufficiently_verified / 0 conflicting / 0
  not_implemented across the final comparison tally.
- **Phase 4** — 6 clean-room-redraft documents plus a current-shipped-
  state factual artifact drafted from Phase 3 evidence alone, zero
  legacy documentation consulted, committed as the plan's own explicit
  hard boundary.
- **Phase 5** — all 9 documents in the plan's own inventory reconciled:
  8 replaced live, `dev-docs/api-spec.md` held pending explicit user
  confirmation (given, then applied — 3 additive bug disclosures,
  verified to be exactly those 3 and nothing else). The §6.4 coverage
  check ran with a real, named number: 67 of 72 `api-spec.md` symbols
  have a corresponding Phase 3 assertion.
- **Phase 6** — an independent `release-phase-auditor` audit, verdict
  **PASS WITH NON-BLOCKING OBSERVATIONS**, re-verifying every claim
  itself (re-running tests, re-running `check_snapshot.py`, independently
  spot-checking provenance, independently confirming no contaminated
  output survived) rather than trusting any phase's own self-report. A
  deferred learning-triage pass, run immediately after, closed out every
  accumulated finding.

## What was achieved

- A from-scratch, independently cross-validated record of what
  Ledgerkit's code actually does, now reconciled into every human-facing
  document in the project (`README.md`, `docs/getting-started.md`,
  `docs/usage.md`, `docs/journal-format.md`, `docs/python-api.md`,
  `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
  `dev-docs/hledger-compatibility.md`, `ROADMAP.md`).
- **11 real findings surfaced as a byproduct of this process**, none
  fixed (correctly out of scope for a documentation-reconstruction
  initiative), all now triaged into durable, dated records rather than
  left floating: 6 confirmed production bugs in `ledgerkit/` (new
  `knowledge/EDGE_CASES.md` entries EC-018 through EC-023, plus a new
  `ROADMAP.md` "Plan 29 bug-fix backlog" row), 1 real code-cleanliness
  defect (`ReportSectionResult.to_dataframe()`'s dead assignment, folded
  into the same backlog row), 2 compat-register entries needing a
  targeted `compat-differential-tester` re-check (a new `ROADMAP.md`
  row), and 2 pre-existing, independently-discovered-stale
  `knowledge/*.md` entries corrected via dated addenda (`EDGE_CASES.md`
  EC-006, `DECISIONS.md`'s balance-assignments entry) — plus a 13th,
  unprompted bonus finding (the identical EC-006 staleness duplicated in
  `DOMAIN_RULES.md`) caught proactively during triage.
- Mechanical tooling that now exists and is proven, not merely
  described: `check_codecompass_pin.sh` (tested both pass/fail paths),
  `check_snapshot.py` (9/9 self-test cases, including the
  `external_repositories` extension built mid-initiative), and the
  `dev-docs/clean-room/compliance-log.md` audit trail itself — now a
  single, continuous record spanning all 6 phases and dozens of
  dispatches, re-verified independently at Phase 6 rather than trusted.
- A real, demonstrated instance of the clean-room process catching its
  own mistakes rather than rubber-stamping: REVIEW mode found and fixed
  genuine draft errors (a backwards specificity rule, a false "nets to
  zero" claim, an anchored-grep false negative); independent
  reconstruction then re-derived several of those exact same corrected
  facts from scratch with zero access to the correction — real
  cross-validation, not assumed.

## What worked

- **Discarding and rerunning on contamination, mechanically, even when
  inconvenient** (compat-system attempt 2, Phase 3) — proved the rule
  is genuinely mechanical, applied by its own letter, not a judgment
  call waived when the output happens to look clean anyway.
- **Recovering a rate-limited dispatch via `SendMessage` resume rather
  than blind redispatch** — validated repeatedly, at increasing scale
  (a pair of dispatches in Phase 3, then all 8 of Phase 5's dispatches
  simultaneously) — preserved substantial already-completed research
  each time rather than discarding it.
- **A lead-level consolidation pass after a batch of parallel
  dispatches is genuinely load-bearing**, not redundant with each
  dispatch's own care — caught two real cross-document defects in
  Phase 5 that 8 individually-careful dispatches collectively missed.
- **Treating the Unauthorised Change Rule's confirm-first step as a real
  gate, not a formality** — the `dev-docs/api-spec.md` proposal was
  scrutinized and had a real defect fixed before ever reaching the user,
  so the diff the user actually confirmed was exactly what it claimed
  to be.
- **An independent final audit that re-runs everything itself** rather
  than trusting the phases' own self-reports — Phase 6 re-ran the test
  suite, re-ran the checker, and independently picked its own
  provenance samples rather than reusing anyone else's examples. This
  is what made the `PASS WITH NON-BLOCKING OBSERVATIONS` verdict
  actually mean something, including catching two things (CodeCompass's
  pin drift, the missing `ROADMAP.md` section) that no phase retro had
  surfaced.

## What didn't work

- Three contamination/content-loss events (Phase 3) and two separate
  rate-limit interruptions (Phase 3's reconstruction step; Phase 5's
  entire 8-dispatch batch, hit simultaneously by a shared session
  limit) were real costs, not free safety margin — correctly handled
  every time, but each one meant extra dispatch rounds beyond the
  planned count.
- `git push` has been blocked all session on a local SSH-agent auth
  issue unrelated to the work itself — flagged repeatedly, never
  resolved within this session, correctly treated throughout as an
  environment issue rather than a completion criterion, but it means
  this initiative's five phase commits (and this closeout) remain
  un-pushed as of this retro.
- CodeCompass's own live checkout drifted past this initiative's Phase
  1 pin partway through (confirmed harmless — no `codecompass`-dependent
  command ran under this initiative's name after Phase 1 — but only
  caught by Phase 6's independent audit, not by any earlier phase
  noticing).

## Lessons learnt

- A mechanical gate only proves its value when it's applied even when
  inconvenient. This initiative validated that principle at least
  three separate times (the compat-system discard, the `api-spec.md`
  confirm-first gate catching a real defect, the Phase 6 audit's
  independent re-runs), and each time the "inconvenient" path was the
  one that actually caught something.
- Parallel, scoped dispatches reconciling documents that reference each
  other will reliably produce a few cross-references that fall through
  individual scoping cracks, no matter how careful each dispatch is.
  The fix is a deliberate, separate consolidation pass built into the
  process, not tighter individual briefs.
- Findings that are genuinely out of an initiative's own scope (a
  production bug found while reconstructing documentation, a stale
  knowledge-base entry found while reconciling a doc against it) are
  not distractions from the initiative's goal — correctly finding them,
  disclosing them honestly, and routing them to a durable record without
  attempting to fix them outside the initiative's own boundary is
  itself evidence the process is working as designed.

## Process-improvement feedback

- Consider having a Legacy Reconciliation dispatch (or any multi-
  document reconciliation dispatch) perform a final end-to-end
  coherence self-check before returning, not just per-claim
  classification — flagged in Phase 5's own retro, not yet acted on,
  carried forward here as a standing suggestion for any future
  initiative with a similar structure.
- The plan's own §4.2a boundary-compliance rule named only two dispatch
  roles in its mandatory-discard list; this initiative needed to extend
  that reasoning (by the lead, recorded in the compliance log, not
  invented unilaterally) to REVIEW/COMPARISON-mode scope slips. Worth
  stating this distinction explicitly in any future plan of this shape
  from the start, rather than deriving it mid-initiative.

## Learnings filed

This phase's own learning-triage pass (dispatched to
`roadmap-context-curator`, reported above and in `dev-docs/clean-room/
compliance-log.md`) closed out all 12 named findings plus one bonus
finding: 6 new `knowledge/EDGE_CASES.md` entries (EC-018–EC-023), 1
corrected in place (EC-006, dated addendum, original preserved), 1
`knowledge/DECISIONS.md` addendum (balance-assignments), 1
`knowledge/DOMAIN_RULES.md` correction (the bonus finding), and 2 new
`ROADMAP.md` backlog rows (the Plan 29 bug-fix backlog; compat-register
corrections, routed to `compat-differential-tester`). Nothing left
untriaged.

## Where we're going

This initiative does not begin Stage D — it was explicitly designed to
run *before* Stage D starts, not as part of it, so that Stage D onward
builds on a reconciled baseline rather than compounding drift against a
stale one. Per the plan's own §7.3 and the standing "never infer
completion" rule, `ROADMAP.md`'s new "Tooling & Process Initiatives" row
is **not** flipped to `[DONE]` by this retro — that happens only on the
user's own explicit confirmation, separately. The 3 non-blocking
follow-ups the Phase 6 audit named (CodeCompass re-pin before further
use, the `git push` retry, the now-completed learning-triage) are
recorded in that row's own text for whoever picks them up next. Stage D
itself remains `[PLANNED]`, unaffected and unblocked by anything in this
initiative's own scope.

## Time / cost note

The longest-running initiative-level effort in this project's history by
calendar time — spanned roughly six weeks (2026-10-02 through
2026-11-14) across multiple session continuations, interrupted several
times by account-level usage/rate limits (each time correctly resumed,
never abandoned or silently restarted from scratch). Total dispatch
count across all six phases: approximately 60 (10 assertion-research
attempts + 3 reruns, 10 REVIEW, 10 implementation-reconstruction, 10
COMPARISON for Phase 3; 7 drafting dispatches for Phase 4; 8 Legacy
Reconciliation dispatches for Phase 5; 1 audit + 1 learning-triage for
Phase 6), each with its own immediate compliance check logged to a
single continuous audit trail.
