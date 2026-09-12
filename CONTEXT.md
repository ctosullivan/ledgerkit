# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 1 (query semantics research + standalone query engine) is
done, committed, and pushed (`f86dd28`). Since then: confirmed and
formally pinned a real `hledger` executable
(`/home/cormac/.local/bin/hledger`, `1.52.4-g33fa849e7-20260910`, sha256
`c212db5f...d07d747`) as `compat-differential-tester`'s reference binary
— resolving a blocker noted repeatedly since Stage A. Confirmed it builds
from the exact same commit (`33fa849e7...`, tag `1.52.4`) as the local
source clone `hledger-researcher` already used. This does not itself run
any differential verification; that's still separate, not-yet-started
work.

## Where We Are
`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.1 and
`dev-docs/compat-register/README.md` both updated with the pinned
binary's exact version/commit/hash. `knowledge/DECISIONS.md` has the
recording entry. This is a small, complete, self-contained addition —
ready to commit and push under `CLAUDE.md`'s Commit & Push Cadence rule
once `CONTEXT.md`/`CHANGELOG.md` are current (this response).

## Decisions In Flight
- None beyond what's now in `knowledge/DECISIONS.md` (the pinned-binary
  recording entry, 2026-09-13).

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.1 —
  pinned-binary confirmation added.
- `dev-docs/compat-register/README.md` — corrected again (binary now
  confirmed, superseding the same-day "still no binary" note).
- `knowledge/DECISIONS.md` — new entry.

## Blockers / Open Questions
- Stage C's next phase (after Phase 1) is still unscoped — candidates:
  wire `ledgerkit/query/` into `reports.py`/a CLI `--query` flag; extend
  the term set (`tag:`, `cur:`); design the `PythonRegex`/`pyre:`
  extension syntax (`07-query-regex.md` §7.4). Needs explicit scoping
  before starting.
- **Newly unblocked, not yet acted on:** `compat-differential-tester` can
  now actually run executable verification against the pinned binary —
  no entry has been moved from `proposed` to `verified` yet; that's a
  separate task from today's pin-and-confirm.
- `EditorDocument`'s include-directive backlog item is still open and
  unscoped (Stage B finding: lower priority than assumed).
- The finer-grained `hledger-compatibility.md` rows from Stage A are still
  unmigrated into the compat-register — open follow-up, not a blocker.

## What NOT To Revisit
- Stage A, Stage B, and Stage C Phase 1 are all closed/committed and
  settled.
- The per-phase retro process and the commit/push cadence rule are both
  adopted and demonstrated across multiple real phases — don't re-ask.
- Don't re-litigate Stage C Phase 1's query semantics (exclusive-end
  dates, negated-same-prefix-AND, the HledgerRegex construct exclusion
  list) — sourced from `hledger-researcher`'s brief, cross-checked by
  real tests.
- Don't re-ask whether a pinned hledger binary exists — confirmed
  directly via `which`/`--version` this response; it does, at the path
  and version recorded above.
- Milestones 0–4 do not get retroactive retros.

## Recent Git State (before this response's commit, if any)
f86dd28 feat: Stage C Phase 1 — query semantics research + standalone query engine
9c33e37 chore: add standing commit/push cadence; scope Stage C Phase 1
f51a18b feat: close out Stage B — editor-compat inventory, model review
a3cf2a7 feat: close out Stage A — agent roster and compatibility-register harness
e702497 fix: revert pyproject.toml license to classic form for Python 3.8 CI
