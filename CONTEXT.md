# CONTEXT.md — Claude Session Working Memory

## Current Task
Implementing the twice-amended Plan 29
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`) straight through to closeout. **Phases 1-4 are done.**
Phase 5 (legacy reconciliation) is next.

## Where We Are
Phase 4 is fully complete: 6 clean-room-redraft documents + the
current-shipped-state factual artifact, all drafted via isolated
dispatches, all compliant, all living under
`dev-docs/clean-room/drafts/` (not overwriting any real document yet).
Retro written: `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-4.md`. Plan
29 §13's implementation log updated to mark Phase 4 done. **This
response's commit is Plan 29's hard boundary** — the last point before
any legacy documentation is reintroduced.

**Next: Phase 5 — legacy reconciliation** (plan §6). Per §5.1's
disposition table:
- **Clean-room redraft** (6 docs, drafted this phase): `README.md`,
  `docs/getting-started.md`, `docs/usage.md`, `docs/journal-format.md`,
  `docs/python-api.md`, `dev-docs/architecture.md` — Phase 5 reconciles
  each existing document's claims against its own fresh draft + the
  underlying snapshots.
- **Reconciliation-only** (no blind draft exists, never will):
  `dev-docs/api-spec.md` (protected, Unauthorised Change Rule applies),
  `dev-docs/hledger-compatibility.md`, `ROADMAP.md`.
- **Intentionally retained, out of scope**: `CHANGELOG.md`, `CONTEXT.md`,
  retros, planning docs, `knowledge/*.md`, `dev-docs/compat-register/**`,
  and several other process files — never claim-classified, never
  reconciled, per §5.1a's explicit distinction from ordinary workflow
  bookkeeping (which continues normally throughout, as it already has
  every phase).

Immediate next steps for Phase 5:
1. Re-read plan §6 closely (classification scheme, acceptance criteria,
   the git-history-restricted-to-tree/content rule) before proceeding.
2. For each clean-room-redraft document: classify every existing claim
   against the draft + snapshots (the five-way scheme referenced in
   §5.1/§6.1), reconcile — correcting what's unsupported, preserving
   what's independently confirmed.
3. For each reconciliation-only document: same claim-by-claim
   reconciliation directly against snapshots/evidence, no parallel
   blind draft to compare against.
4. Separate ROADMAP.md's current-state content from forward-looking
   intent explicitly (§5.1, §6.1) — the current-shipped-state artifact
   from Phase 4 is exactly the factual input for this.
5. Run the deferred `docs/python-api.md` vs. `dev-docs/api-spec.md`
   coverage comparison (api-spec.md is protected — any actual change
   goes through the Unauthorised Change Rule's confirm-first step
   regardless of what reconciliation finds).
6. Replace live documents only where the inventory permits (clean-room
   redraft + reconciliation-only rows); never touch anything
   dispositioned `intentionally retained`.
7. Do CHANGELOG/CONTEXT/retro updates as ordinary bookkeeping, separate
   from the reconciliation reports themselves.

## Decisions In Flight
- **Citation-granularity gap, flagged by two Phase 4 dispatches**:
  several exact function-signature details in `architecture.md`/
  `python-api.md` trace only to a topic's bundled reconstruction report,
  not a dedicated assertion ID, since no Phase 3 assertion was written
  at signature-level granularity. Not yet resolved — flagged as a
  candidate for a narrow signature-focused assertion-research addendum
  before Phase 6's audit, or to carry forward as a disclosed limitation.
  Decide before Phase 6, not silently.
- **External-repo evidence under `/tmp` does not survive inter-phase
  gaps** — confirmed twice now (once discovered mid-Phase-4's own
  precondition check). The recorded origin-URL-plus-pinned-SHA recovery
  path in `PINNED-REVISIONS.md` works reliably; re-check it before any
  future phase that touches editor-surface's evidence again.
- **8 real production bugs/defects found in Phase 3 remain recorded,
  never fixed** — out of scope for this entire documentation
  initiative. Full tally in `dev-docs/clean-room/compliance-log.md`.
  Several were deliberately included as confirmed current-behaviour
  facts in the Phase 4 drafts (journal-format.md especially) — this is
  appropriate (they're true facts about current behaviour) and distinct
  from fixing them, which remains a separate future task.

## Files Currently Relevant
- `dev-docs/clean-room/drafts/*.clean-room-draft` + `current-shipped-
  state.md` — the 7 Phase 4 outputs, now the primary input for Phase 5
  alongside the real documents they inform/replace.
- `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md`
  §6 — Phase 5's own charter, to re-read closely before proceeding.
- `README.md`, `docs/getting-started.md`, `docs/usage.md`,
  `docs/journal-format.md`, `docs/python-api.md`,
  `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
  `dev-docs/hledger-compatibility.md`, `ROADMAP.md` — the real documents
  Phase 5 reconciles (now finally in scope to read).
- `dev-docs/clean-room/compliance-log.md` — keep appending for every
  Phase 5 dispatch.

## Blockers / Open Questions
None. Proceeding directly per explicit instruction to implement through
final closeout without another planning round-trip.

**Separate, non-blocking note for the user**: `git push` failed earlier
this session — the local SSH agent has no identities loaded
(`ssh-add -l` → "The agent has no identities"). All work is safely
committed locally; pushing needs the user's own `ssh-add` with their
key. Not a blocker to continuing the implementation work itself.

## What NOT To Revisit
- Don't re-run any Phase 3 or Phase 4 step — both fully done, all
  compliant, all checker-valid where applicable.
- Don't re-litigate the 8 production bugs/defects — correctly out of
  scope for this initiative; flagged, not fixed, not silently dropped.
- Don't let Phase 5 read any document dispositioned `intentionally
  retained` as a reconciliation target (it's fine to touch for ordinary
  bookkeeping, per §5.1a — just never claim-classified).
- Don't overwrite `dev-docs/api-spec.md` without going through the
  Unauthorised Change Rule's confirm-first step, regardless of what
  Phase 5's reconciliation finds.
- Don't begin Stage D as part of this task.

## Recent Git State (before this response's commit)
c2cb98f feat(codecompass-upgrade-phase-3): comparison mode + phase 3 closeout for all 10 topics
f55294f feat(codecompass-upgrade-phase-3): model-blind implementation reconstruction for all 10 topics
7224bb5 feat(codecompass-upgrade-phase-3): clean-room assertion research, review, and freeze for all 10 topics
5188141 feat(codecompass-upgrade-phase-2): adopt clean-room workflow + snapshot checker
0c89ceb feat(codecompass-upgrade-phase-1): CodeCompass reconciliation + enforced revision pinning

**This response commits Phase 4's closeout** (7 drafts, retro, plan log
update) — this is Plan 29's explicit hard boundary commit. Push was
attempted automatically per the Commit & Push Cadence rule but failed on
an SSH auth issue (see above) — commit stands locally regardless; retry
push once the user's SSH agent has an identity loaded. Next unit: Phase
5 legacy reconciliation, a fresh phase.
