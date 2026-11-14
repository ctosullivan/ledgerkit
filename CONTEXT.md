# CONTEXT.md — Claude Session Working Memory

## Current Task
Implementing the twice-amended Plan 29
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`) straight through to closeout. **Phases 1 and 2 are
done. Phase 3 is in progress** — steps 1-6 of the 9-step per-topic
pipeline (§4.2) are complete for all 10 topics; step 7 (domain-skeptic
COMPARISON mode) is next.

## Where We Are
Phase 3 (plan §4), per-topic pipeline:
1. ✅ Assertion research — all 10 topics.
2. ✅ `domain-skeptic` REVIEW mode — all 10 topics. Found genuine
   defects + 2 real production bugs (parser.py commodity-directive
   never-raise violation; loader.py glob-named-directory IndexError).
3. ✅ Froze all 10 topics into `dev-docs/clean-room/snapshots/`.
4. ✅ `check_snapshot.py` hard gate — all 102 assertions pass (caught
   and fixed 3 real citation defects first; checker itself extended
   with an `external_repositories` resolver for editor-surface's
   external-clone evidence).
   **Steps 1-4 committed as `7224bb5`.**
5. ✅ Dispatched a fresh `implementation-reconstructor` per topic (all
   10, never shown the assertions/snapshot). Two dispatches
   (journal-parsing, commodity-styling) were interrupted mid-task by
   the account's weekly rate limit on a trailing, inessential
   verification step — their reports had already been fully written to
   disk beforehand, recovered by reading the files directly rather than
   redispatching.
6. ✅ Immediate transcript compliance check on each (§4.2a) — all 10
   compliant, logged in `dev-docs/clean-room/compliance-log.md`.
   Independent reconstruction surfaced **3 more real production bugs**
   beyond the 2 found in step 2 (now 7 total + 1 compat-register data
   defect — full tally in the compliance log's own summary section):
   an `alias` directive with an out-of-range backreference crashing
   with an uncaught `re.PatternError`; a directive encountered
   mid-open-transaction-block silently discarding subsequent posting
   lines; and hledger's balance-assignment elision syntax silently
   corrupting data for suffix-commodity/comma-decimal input. Also: the
   editor-surface reconstruction found **zero real usage of
   `EditorDocument`** by its intended external consumer (dead code from
   that consumer's perspective) — highly relevant for the comparison
   step and for Phase 4's eventual drafting.
   **This unit (step 5-6, all 10 topics) was just committed** — see
   Recent Git State below.
7. ⬜ `domain-skeptic` COMPARISON mode per topic (×10) — NEXT STEP. Each
   dispatch classifies alignment between a topic's frozen snapshot and
   its implementation-reconstruction report; never forces either side
   to match, never auto-promotes an assertion's status from alignment
   alone.
8. ⬜ Producer-metadata confirmation (already satisfied — every
   assertion and reconstruction file carries a producer header).

## Decisions In Flight
- **REVIEW/reconstructor-mode boundary-compliance standard** (carried
  from prior unit): a dispatch's brief, self-disclosed, explicitly-
  unused peek outside its own evidence list is logged as a compliance
  *note*, not treated as contamination requiring discard, for any
  dispatch type OTHER than assertion-research/implementation-
  reconstructor's *primary* evidence-gathering act itself (plan §4.2a's
  own mandatory-discard list names only those two). Not triggered this
  unit — all 10 reconstructor dispatches were clean.
- **Recovering a report from disk after a rate-limit interruption,
  rather than redispatching**: when a dispatch's final hand-back is cut
  off by the account's own weekly limit, check whether the report file
  it was writing already exists and looks complete (consistent size/
  timestamp with sibling dispatches) before spending a fresh dispatch
  re-doing the work. Applied twice this unit (journal-parsing,
  commodity-styling), both times correctly — the interrupted step in
  both cases was a trailing, inessential "let me also check one more
  edge case," not the main report-writing act.
- **Real production bugs found as a byproduct of this clean-room
  phase are recorded, never fixed** — out of scope for a documentation-
  reconstruction phase; the full, cumulative tally lives in
  `dev-docs/clean-room/compliance-log.md`'s own dedicated section,
  flagged for a future tracked-fix task.

## Files Currently Relevant
- `dev-docs/clean-room/implementation-reconstruction/<topic>.md` — all
  10 topics, all compliant, ready for COMPARISON mode next.
- `dev-docs/clean-room/snapshots/<topic>-v1.{md,sidecar.json}` — all 10
  topics, all checker-valid (from the prior unit).
- `dev-docs/clean-room/implementation-comparison/` — empty so far; next
  mechanical home for COMPARISON mode's ×10 outputs.
- `dev-docs/clean-room/compliance-log.md` — full per-dispatch record
  for every dispatch so far across both units; keep appending for the
  ×10 COMPARISON dispatches next.

## Blockers / Open Questions
None. Proceeding directly per explicit instruction to implement through
final closeout without another planning round-trip.

## What NOT To Revisit
- Don't re-run assertion-research, REVIEW, freezing, or
  implementation-reconstruction for any of the 10 topics — all done,
  all compliant.
- Don't re-litigate any of the 7 production bugs or 1 compat-register
  data defect found so far — correctly out of scope for this
  documentation phase; flagged for a separate future fix, not silently
  dropped, not fixed now either.
- Don't trust a subagent hand-back that says "see above"/"already
  posted" without the actual content present — resume the same agent.
  Distinct from the rate-limit case: if a dispatch is cut off by a
  rate-limit error (not a summary-only hand-back), check disk for an
  already-complete report first before redispatching.
- Don't let the main orchestrating session author assertions or
  classify alignment directly — domain-skeptic does the comparison
  classification next, not the orchestrator.
- Don't begin Stage D as part of this task.

## Recent Git State (before this response's commit)
7224bb5 feat(codecompass-upgrade-phase-3): clean-room assertion research, review, and freeze for all 10 topics
5188141 feat(codecompass-upgrade-phase-2): adopt clean-room workflow + snapshot checker
0c89ceb feat(codecompass-upgrade-phase-1): CodeCompass reconciliation + enforced revision pinning
4277036 docs: second amendment to CodeCompass/clean-room plan, approved to implement
e1b0144 docs: amend CodeCompass upgrade + clean-room docs plan per review

**This response commits Phase 3 steps 5-6** (10 implementation-
reconstruction reports, all compliant, 3 more real production bugs
found). Next unit: domain-skeptic COMPARISON mode ×10, committed
separately once done.
