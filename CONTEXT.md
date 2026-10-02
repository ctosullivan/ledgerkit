# CONTEXT.md — Claude Session Working Memory

## Current Task
Implementing the twice-amended Plan 29
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`) straight through to closeout. **Phases 1 and 2 are
done. Phase 3 is in progress** — steps 1-4 of the 9-step per-topic
pipeline (§4.2) are complete and checker-valid for all 10 topics;
steps 5-8 (implementation-reconstructor + comparison) are next.

## Where We Are
Phase 3 (plan §4), per-topic pipeline:
1. ✅ Assertion research — all 10 topics, all compliant on final
   attempt (3 contamination/loss events logged, discarded, rerun —
   see `dev-docs/clean-room/compliance-log.md`).
2. ✅ `domain-skeptic` REVIEW mode — all 10 topics done. Found and
   fixed genuine defects by direct execution in every topic (not
   rubber-stamping): wrong specificity direction (query-engine-014),
   false "nets to zero" claim (reports-cli-005), anchored-grep false
   negative that missed 8 of 9 real import sites (editor-surface-008),
   and more. Surfaced 2 real **production bugs** as a byproduct
   (recorded, NOT fixed — out of scope for this phase): (a)
   `parse_string_lenient`'s "never raises" guarantee is false for a
   malformed `commodity` directive (parser.py:1324-1334 lacks the
   try/except guard every other directive handler has); (b) a
   containing directory named with a glob metacharacter (e.g. `inc[1]`)
   causes the loader's glob-vs-literal classification to diverge,
   silently misrouting a plain include into an uncaught `IndexError`.
   One lead-resolved escalation (editor-surface-006: `pyproject.toml`
   of an external clone is in-scope build/config evidence, same as for
   Ledgerkit's own).
3. ✅ Froze all 10 topics into `dev-docs/clean-room/snapshots/`
   (sidecar JSON + human-readable .md each).
4. ✅ Ran `check_snapshot.py` as a hard gate — caught 3 real citation
   defects before accepting anything: two off-by-one whole-file line
   counts (cli.py, ast.py each cited one line past their real end) and
   a literal unresolvable glob used as an Evidence-paths entry
   (`dev-docs/compat-register/*.yaml`, expanded to its 49 real files).
   Also extended the checker itself: editor-surface's evidence lives
   in an external `ledgerkit-editor` git clone (different repo
   entirely), which the checker couldn't resolve at all — added an
   `external_repositories` sidecar field + resolver, each
   absolute-path citation now checked against THAT repo's own pinned
   revision (recorded in `PINNED-REVISIONS.md`), never silently
   skipped. Added 2 new self-test cases (pass + fail) proving it works;
   all 9 self-test cases pass. **All 102 assertions across all 10
   topics now pass the checker.**
5. ⬜ Dispatch a fresh `implementation-reconstructor` per topic
   (never shown the assertions/snapshot) — NEXT STEP.
6. ⬜ Immediate transcript compliance check on each (§4.2a), same
   discipline already used for assertion-research.
7. ⬜ `domain-skeptic` COMPARISON mode per topic.
8. ⬜ Producer-metadata confirmation (already satisfied — every
   assertion file carries its producer header).

**This unit (steps 1-4, all 10 topics) was just committed** — see
Recent Git State below. The remaining unit (steps 5-7,
implementation-reconstructor + comparison ×10) is a separate,
equally-scoped commit to follow.

## Decisions In Flight
- **Operational finding, load-bearing for future dispatches**: a
  subagent's hand-back sometimes delivers only a summary, not full
  content, even when explicitly told to include it (observed 3 times
  in step 1). Fix: resume the *same* agent via `SendMessage`, never a
  fresh dispatch (which has no memory of content it never actually
  sent).
- **REVIEW-mode boundary-compliance standard, decided this session**:
  unlike assertion-research/implementation-reconstructor (named
  explicitly in plan §4.2a's mandatory discard-list), a domain-skeptic
  REVIEW dispatch's brief, self-disclosed, explicitly-unused peek
  outside its own topic's evidence list is logged as a compliance
  *note*, not treated as contamination requiring discard — because (a)
  the plan's own text doesn't name REVIEW mode in that list, (b)
  REVIEW's output is independently per-field traceable, so an unused
  aside doesn't propagate the way it would in the primary evidentiary
  record. Applied twice (reports-cli's `checks.py` peek, loader's
  `inspect.getsource` on `parser.py`), both explicitly confirmed unused
  in any edit.
- **Checker extended for external-repo evidence** (see step 4 above) —
  this is the kind of mechanical tooling gap Plan 29's own checker was
  always going to need once a topic's evidence wasn't exclusively
  Ledgerkit's own tree; treated as an expected extension, not scope
  creep.

## Files Currently Relevant
- `dev-docs/clean-room/assertions/<topic>/*.md` — all 102 files, all
  topics, frozen and checker-valid.
- `dev-docs/clean-room/snapshots/<topic>-v1.{md,sidecar.json}` — all 10
  topics, all passing `check_snapshot.py`.
- `dev-docs/clean-room/check_snapshot.py` — now also handles
  `external_repositories`; 9/9 self-test cases pass.
- `dev-docs/clean-room/compliance-log.md` — full per-dispatch record
  for every assertion-research and REVIEW dispatch so far; keep
  appending for the ×10 implementation-reconstructor dispatches next.
- `dev-docs/clean-room/PINNED-REVISIONS.md` — now also pins the
  ledgerkit-editor research clone's revision.
- `.claude/agents/domain-skeptic.md`, `.claude/agents/
  implementation-reconstructor.md` — both proven to work as real
  dispatchable `subagent_type` values.

## Blockers / Open Questions
None. Proceeding directly per explicit instruction to implement through
final closeout without another planning round-trip.

## What NOT To Revisit
- Don't re-run assertion-research or REVIEW for any of the 10 topics —
  both done, both checker-valid.
- Don't re-litigate the two production bugs found in step 2 (parser.py
  commodity-directive, loader.py glob-named-directory) — they are
  correctly out of scope for this documentation phase; flagged for a
  separate future fix, not silently dropped.
- Don't trust a subagent hand-back that says "see above"/"already
  posted" without the actual content present — resume the same agent.
- Don't let the main orchestrating session author assertions directly
  — keep honoring this for the comparison step too (domain-skeptic,
  not the orchestrator, classifies alignment).
- Don't begin Stage D as part of this task.

## Recent Git State (before this response's commit)
5188141 feat(codecompass-upgrade-phase-2): adopt clean-room workflow + snapshot checker
0c89ceb feat(codecompass-upgrade-phase-1): CodeCompass reconciliation + enforced revision pinning
4277036 docs: second amendment to CodeCompass/clean-room plan, approved to implement
e1b0144 docs: amend CodeCompass upgrade + clean-room docs plan per review
7032b3e docs: plan CodeCompass upgrade + clean-room docs reconstruction

**This response commits Phase 3 steps 1-4** (102 assertions across 10
topics, reviewed, frozen, checker-valid; checker itself extended for
external-repo evidence). Next unit: implementation-reconstructor ×10 +
comparison ×10, committed separately once done.
