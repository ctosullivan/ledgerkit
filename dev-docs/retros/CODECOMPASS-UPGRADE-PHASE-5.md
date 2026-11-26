# CodeCompass upgrade + clean-room docs — Phase 5 retro — legacy reconciliation

- **Date:** 2026-11-14
- **Commit(s):** this response's commit (immediately following)
- **Agents used:** 8 `docs-maintainer` Legacy Reconciliation Mode dispatches (one `python-api.md`+`api-spec.md` pair, 7 single-document)

## Where we are

This is Phase 5 of Plan 29's six-phase initiative, the first phase where
existing legacy narrative documentation is read at all, per the hard
invariant that governed every phase before it. Phase 4's six clean-room
drafts plus the current-shipped-state factual artifact (committed as the
hard boundary) are now reconciled against all 9 documents in §5.1's
inventory — README.md, docs/getting-started.md, docs/usage.md,
docs/journal-format.md, docs/python-api.md, dev-docs/architecture.md
(all clean-room-redraft) and dev-docs/api-spec.md,
dev-docs/hledger-compatibility.md, ROADMAP.md (all reconciliation-only).
Every live human-facing document in the project now traces its factual
claims to Phase 3 evidence, a targeted re-check, or an explicit
historical/intent label — closing the loop this entire six-phase
initiative was built to close.

## Goal

For every claim in the 9 inventoried documents, classify it against the
Phase 4 drafts/Phase 3 evidence using the five-way scheme, fix what's
wrong (not merely log it), separate ROADMAP.md's fact from its intent,
run the deferred §6.4 api-spec.md coverage check, and replace the live
documents — all without touching anything outside the inventory, and
with `dev-docs/api-spec.md` gated behind the Unauthorised Change Rule's
confirm-first step.

## Scope delivered vs planned

Delivered exactly what §6 specified, with one unplanned interruption and
recovery: all 8 dispatches were cut off mid-research by the account's
own session rate limit simultaneously (a shared resource exhaustion
event, not individual failures) before any had written a report or
touched a live document. All 8 were resumed via `SendMessage` once the
limit reset — not redispatched fresh — preserving the research each had
already done. All 8 then completed fully. No scope was dropped or
deferred.

## What was achieved

- All 9 documents reconciled: 8 replaced live, 1 (`dev-docs/api-spec.md`)
  held pending the user's explicit confirmation, then applied after
  approval.
- The §6.4 coverage check ran with a real, named number: **67 of 72**
  public symbols listed in `dev-docs/api-spec.md` have a corresponding
  Phase 3 assertion; the 5 gaps are named, not glossed over.
- Several genuine cross-cutting findings surfaced and were correctly
  routed rather than fixed outside each dispatch's own write boundary:
  a stale `knowledge/EDGE_CASES.md` entry (EC-006, contradicted by
  test-confirmed current behaviour), a false `knowledge/DECISIONS.md`
  entry (claimed balance-assignments were gracefully deferred; as-built
  code actually crashes or corrupts), and 2 compat-register entries
  flagged for a future `compat-differential-tester` re-check.
  None of these are `knowledge/`/`compat-register/` edits this
  initiative is authorised to make directly — correctly left as
  flagged findings for their respective owning roles.
  `dev-docs/api-spec.md` itself got 3 additive, user-confirmed
  disclosures of confirmed current bugs (the two `checks-008` skip/
  names/strict asymmetries, the two `loader` glob-escaping gaps) —
  these ARE within this initiative's own write boundary and were
  applied after confirmation.
- A lead-level consolidation pass caught two things the dispatches'
  own parallel execution didn't: a stale "each entry there is
  `status: proposed`" framing sentence in `dev-docs/hledger-
  compatibility.md`'s own opening paragraph (missed by that
  document's own reconciliation dispatch despite an otherwise
  thorough pass), and a stray one-space formatting slip the
  `api-spec.md` dispatch introduced in an unrelated, unchanged
  `Commands:` summary block while producing its proposed revision —
  both fixed before anything was finalized.
- 935 tests still pass throughout; no `ledgerkit/` source touched.

## What worked

- **Resuming all 8 rate-limited dispatches via `SendMessage` rather
  than redispatching fresh** preserved a large amount of already-done
  research (each dispatch had read most or all of its permitted
  evidence before being cut off) — a meaningfully cheaper recovery than
  starting over, and the pattern held at 8-way concurrency just as
  reliably as it had at smaller scale earlier in this initiative.
- **The "agreement between legacy and clean-room draft is not itself
  evidence" rule, carried explicitly into every dispatch's brief,
  worked as intended** — multiple dispatches independently re-opened
  and directly re-read cited assertions rather than trusting draft/
  legacy agreement at face value, and at least one (`architecture.md`)
  mechanically verified 100% citation survival through the merge via a
  literal citation-set diff, not just an assertion that nothing was
  dropped.
- **Giving `dev-docs/api-spec.md`'s dispatch the explicit instruction
  to never touch the live file, only a proposed-revision file,**
  combined with the lead's own consolidation pass catching the one
  real defect in that proposal before presenting it, meant the
  Unauthorised Change Rule's confirm-first step actually worked as a
  real gate — the user saw a clean, exactly-scoped diff, not something
  requiring them to spot an unrelated formatting regression themselves.
- **A lead-level consolidation pass after all dispatches return is
  genuinely load-bearing, not redundant** — it caught two real defects
  (the stale framing sentence, the formatting slip) that 8 individually
  careful, independently-reasoning dispatches collectively missed.
  Worth keeping as a standing step whenever several reconciliation
  dispatches run in parallel against documents that reference each
  other.

## What didn't work

- The shared session rate limit cutting off all 8 dispatches
  simultaneously (rather than staggered) suggests dispatching this many
  heavyweight reconciliation passes in one batch pushes close to a real
  resource ceiling. Recovered cleanly this time, but a future phase
  with an even larger document set might want to batch dispatches in
  smaller groups rather than all-at-once, to reduce the chance of a
  simultaneous cutoff turning into something harder to recover from.
- Two dispatches (`README.md`, implicitly; `ROADMAP.md`, explicitly)
  didn't add their own `CHANGELOG.md` entry despite their own agent
  brief's normal duty to do so — not a defect in their actual
  reconciliation work, but it meant the lead had to notice and backfill
  2 of 8 entries during consolidation rather than everything being
  self-consistent on the first pass.

## Lessons learnt

- A fleet of independently-reasoning agents reconciling documents that
  reference each other (README.md citing hledger-compatibility.md's own
  framing, api-spec.md needing to match docs/python-api.md) will
  produce a few genuine cross-references that fall through the cracks
  of per-document scoping, even when each individual pass is careful.
  This isn't a flaw in any one dispatch — it's a structural property of
  parallel, scoped work — and the fix is a deliberate, separate
  consolidation pass, not tighter individual briefs.
- "Produce a proposed revision, never touch the live protected file"
  is a clean, auditable pattern for the Unauthorised Change Rule — but
  the proposal itself still needs the same scrutiny as any other
  dispatch output before it reaches the user. Confirm-first protects
  against an unauthorized *change*; it doesn't by itself protect
  against an *imprecise* proposed change reaching the confirmation step
  with an unrelated defect riding along.

## Process-improvement feedback

- Consider having a Legacy Reconciliation dispatch explicitly verify,
  as a final self-check step before returning, that every section of
  the document it rewrote still reads coherently end-to-end (not just
  that each individual claim was correctly classified) — this might
  have caught the hledger-compatibility.md framing-sentence staleness
  without needing the lead's separate pass. Flagged as a possible brief
  addition, not applied retroactively here.

## Learnings filed

None yet — consistent with Phases 3 and 4's retros, recommend a single
`roadmap-context-curator` learning-triage pass across the whole
initiative's compliance log once Phase 6 closes it out. The stale
`knowledge/EDGE_CASES.md` and `knowledge/DECISIONS.md` entries found
this phase are exactly the kind of finding that triage pass should
surface and route to an actual fix.

## Where we're going

Phase 6 (independent final validation) is next: an explicit,
separately-reported audit against all 8 criteria named in the plan's
§7.1 — CodeCompass pin success, workflow fidelity, actual isolation
tier, transcript compliance via this compliance log, contamination/
discard/rerun events (3, all in Phase 3, all correctly handled),
full topic/document coverage, snapshot/provenance integrity, and
documentation consistency + test results. This phase's own findings
(the knowledge/ staleness, the 2 flagged compat-register entries, the
5 api-spec.md coverage gaps) are Phase 6 audit inputs, not blockers —
they were correctly surfaced and routed, which is itself evidence the
process is working, not a sign of incompleteness. This phase confirmed
the planned trajectory; it did not change it.

## Time / cost note

Comparable to Phase 3 in dispatch count (8) but completed in roughly one
continuation after a single shared rate-limit interruption, recovered
in one resume round rather than requiring redispatch. The lead's own
consolidation pass (api-spec.md diff review + 2 cross-dispatch fixes)
added meaningful value for comparatively little additional cost.
