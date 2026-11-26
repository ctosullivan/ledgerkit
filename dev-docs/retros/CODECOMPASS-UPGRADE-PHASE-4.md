# CodeCompass upgrade + clean-room docs — Phase 4 retro — clean-room documentation drafting

- **Date:** 2026-11-14
- **Commit(s):** this response's commit (immediately following)
- **Agents used:** 7 fresh `general-purpose` drafting dispatches (never `fork`), one per target document

## Where we are

This is Phase 4 of Plan 29's six-phase initiative, immediately following
Phase 3's closeout (`dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-3.md`),
which produced 102 checker-valid assertions, 10 implementation-
reconstruction reports, and 10 comparison reports across all 10 bounded
topics — the entire evidentiary basis this phase draws on. This phase
is the first one that produces something a human will actually read:
six replacement documents plus one internal factual artifact, drafted
entirely from Phase 3's output, with zero legacy documentation consulted
anywhere. This commit is Plan 29's hard boundary — the last point before
Phase 5 reintroduces any existing prose at all.

## Goal

Draft the six clean-room-redraft documents (`README.md`,
`dev-docs/architecture.md`, `docs/getting-started.md`, `docs/usage.md`,
`docs/journal-format.md`, `docs/python-api.md`) plus the
current-shipped-state factual artifact, via fresh isolated dispatches,
each sentence traceable to a Phase 3 snapshot citation, with zero
forward-looking content and confidence language calibrated to each
cited assertion's comparison classification.

## Scope delivered vs planned

Delivered exactly what §5.2 specified: 6 documents + 1 internal
artifact, 7 dispatches total (matching §5.4's "six drafting dispatches
... and the current-shipped-state dispatch" exactly — `docs/getting-
started.md` and `docs/usage.md` were kept as two separate documents/
dispatches rather than merged, since §5.1's table lists them as
distinct rows and nothing in the material suggested merging was the
better fit). One unplanned but necessary detour: Phase 4's own
precondition check (§5.3, re-confirming the checker before any drafting
dispatch) found the editor-surface snapshot had gone from passing to
failing since Phase 3 closed — its external-repository clone under
`/tmp` had been cleaned up during the six-week gap between phases,
exactly the risk `PINNED-REVISIONS.md` had flagged at freeze time.
Re-cloned from the recorded origin URL at the exact pinned SHA, checker
re-passed, drafting proceeded. Not a scope change — a precondition that
needed restoring before the precondition check could pass.

## What was achieved

- Seven drafts on disk under `dev-docs/clean-room/drafts/`, none
  overwriting the real documents they will eventually replace.
- Every factual sentence across all seven drafts traces to a specific
  `<topic>@v1#<assertion-id>` citation; zero genuine forward-looking
  language found on spot-check (two string matches were both
  self-referential disclaimers stating the document contains no
  roadmap content, not actual forward-looking claims).
- Confidence language consistently calibrated to each cited assertion's
  Phase 3 comparison classification across all seven drafts — `aligned`
  stated as current fact, `partial`/`insufficiently_verified` hedged
  explicitly, with several dispatches naming the exact classification
  inline rather than just silently softening the tone.
- Confirmed, unflattering current-behaviour facts (the production bugs
  Phase 3 found) were included where a document's own scope called for
  them — most notably `docs/journal-format.md`'s explicit sections on
  `parse_string_lenient`'s broken never-raise guarantee, the directive-
  mid-transaction silent data loss, and the balance-assignment silent
  corruption — rather than omitted for being surprising, per explicit
  instruction in that dispatch's brief.
- A consistent, disclosed citation-discipline nuance surfaced
  independently in two dispatches (`architecture.md`, `python-api.md`):
  exact function-signature detail is sourced from each topic's bundled
  reconstruction report, not a dedicated assertion ID, since no Phase 3
  assertion was written at that granularity. Flagged as a known gap, not
  silently papered over.

## What worked

- **The explicit instruction to include confirmed-but-unflattering
  findings, rather than quietly dropping them, worked exactly as
  intended** — multiple dispatches (journal-format.md most visibly,
  but also usage.md for `check`'s silent-success behaviour and `print`'s
  dropped comments) wrote the surprising, honest fact plainly instead of
  softening it into vaguer language.
- **Scoping each dispatch to only the topics its target document
  naturally needs** (3-5 topics for most documents, all 10 only for the
  two genuinely cross-cutting ones, architecture.md and python-api.md)
  kept each dispatch's evidence load proportionate to its actual job,
  without starving any dispatch of evidence it needed.
- **The citation rule caught itself working**: multiple dispatches
  independently declined to state a real, interesting finding (the
  pyproject.toml version/classifier mismatch, print's further
  divergences from writer.py, the editor-surface EditorDocument's own
  zero-usage framing recurring correctly across both README and python-
  api) specifically because no frozen assertion backed it at the right
  granularity — exactly the discipline §5.4's "a sentence that doesn't
  trace to anything is a drafting defect" rule is meant to enforce, and
  every dispatch applied it without being told to re-check itself.
- **Re-confirming the checker immediately before dispatching (§5.3),
  not assuming Phase 3's pass still held**, caught the editor-surface
  clone's disappearance before any drafting dispatch could have silently
  produced a draft against invalid evidence.

## What didn't work

- No misfires this phase. All 7 dispatches returned compliant, with
  disclosed (not contamination-level) notes only.

## Lessons learnt

- An external, non-Ledgerkit-repo evidence source living in `/tmp` will
  not survive an inter-phase gap measured in weeks. The recorded
  origin-URL-plus-pinned-SHA recovery path (written into
  `PINNED-REVISIONS.md` specifically anticipating this) worked exactly
  as designed the one time it was actually needed — validating that the
  extra recording discipline at freeze time was worth the effort, not
  theoretical caution.
- Giving a drafting dispatch explicit permission (and instruction) to
  state an unflattering, confirmed fact plainly removes the temptation
  to omit it "to be safe" — worth carrying this exact phrasing forward
  into any future documentation-drafting brief, not just this initiative.

## Process-improvement feedback

- Two independent dispatches surfacing the identical citation-
  granularity gap (signature-level facts living only in reconstruction
  reports, not assertions) suggests this is a real, systematic gap in
  Phase 3's own assertion coverage, not an isolated oversight. Worth
  considering a narrow, signature-focused assertion-research addendum
  pass before Phase 6's audit, rather than treating it as acceptable
  residue — flagged for the lead's decision, not resolved here.

## Learnings filed

None yet — same as Phase 3's retro, recommend a single `roadmap-
context-curator` learning-triage pass across the whole initiative's
compliance log once Phase 6 closes it out, rather than triaging
piecemeal mid-initiative.

## Where we're going

Phase 5 (legacy reconciliation) is next: reintroduce the existing
documents these seven drafts are meant to replace or inform, classify
every old-doc claim against the drafts/snapshots per §5.1's inventory,
reconcile `dev-docs/api-spec.md`/`dev-docs/hledger-compatibility.md`/
`ROADMAP.md` (reconciliation-only, not blindly overwritten), and run the
deferred api-spec coverage comparison. This phase's citation-granularity
gap (noted above) and the 8 production bugs/defects Phase 3 found both
feed Phase 5 as inputs, not blockers. This phase confirmed the planned
trajectory; it did not change it.

## Time / cost note

Comparatively fast relative to Phase 3 — seven dispatches, one
precondition-recovery detour (the external clone re-clone), all in a
single session continuation. No contamination events, no rate-limit
interruptions this phase.
