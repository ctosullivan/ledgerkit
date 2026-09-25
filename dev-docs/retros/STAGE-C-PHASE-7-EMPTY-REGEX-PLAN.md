# Stage C Phase 7 retro — Planning (empty-regex-pattern rejection)

- **Date:** 2026-09-25
- **Commit(s):** see `git log` for this retro's own commit; the design
  document itself is `dev-docs/planning/core-redefinition/26-query-
  regex-empty-pattern-design.md`.
- **Agents used:** `context-curator` (misdirected dispatch, correctly
  self-refused — see below), `compat-differential-tester` (live-binary
  matrix, Step 1's actual research work).

## Where we are

Stage C Phase 6 (`tag:` query matching) closed out `[DONE]` with one
named backlog item recommended as the next phase to scope: a real,
pre-existing, cross-cutting divergence where Ledgerkit accepts an empty
regex pattern (`acct:`, `desc:`, `tag:NAME=`, `depth:REGEX=N`'s REGEX
half) that real hledger rejects at parse time. This retro covers Steps
1-3 of this project's standing process for that fix: context
curation, live-binary verification, and the design document. Following
directly from `STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md`'s own
Addendum 2, which named this as backlog item 1 and the recommended next
phase.

## Goal

Scope a fix for `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`: determine
exactly what hledger rejects (literal empty string vs. any
empty-matching pattern), determine the minimal correct Ledgerkit change,
and produce a design document for human approval — not implement
anything.

## Scope delivered vs planned

Design document produced, fully scoped, no implementation. One real
process correction along the way (see "What didn't work").

## What was achieved

The scoping question that mattered most — does hledger reject the
literal empty string, or any pattern capable of matching one — is now
answered precisely and executably: **only the literal empty string**
(`.*`, `a*`, `^$`, `()` are all accepted). This turned what could have
been an open-ended regex-semantics audit into a one-line, fully
characterised fix: a `pattern == ""` check in `ledgerkit/query/regex.py`'s
`validate_hledger_regex`, reusing the already-public `Unsupported
RegexConstructError` — no new exception class, no `api-spec.md`
signature change, no per-call-site changes needed at all, since every
regex-taking query term already routes through this one shared
function. A second, unrelated hledger rejection family (empty
alternation branches, `(|)` etc.) was found and explicitly scoped
**out** rather than folded in, keeping the fix narrow as the prior
retro's own recommendation asked for.

## What worked

- **Live-binary testing settled the scope question decisively** — the
  design phase could have spent real effort deriving "does regex-tdfa's
  own semantics reject empty-admitting patterns" from source/manual
  reasoning alone; instead, a systematic table (`.*`, `a*`, `x*`, `^$`,
  `()`, `(|)`, `a|`, `|a`, `(a|)`, `(|a)`, `a**`) against the pinned
  binary answered it directly and found the message-text-vs-pattern-
  echo signal that distinguishes the two rejection causes externally —
  a level of precision unlikely from reasoning alone.
- **Checking the existing parser code before assuming a design fork
  existed** avoided real wasted design effort: the misdirected
  `context-curator` dispatch's own final report flagged "does
  Ledgerkit need to distinguish bare `tag:NAME` from `tag:NAME=`
  internally" as an open question for the design phase — direct
  reading of `_build_tag`'s existing `partition("=")` logic showed this
  was already resolved by existing code, not a new problem to solve.

## What didn't work

The initial `context-curator` dispatch was mis-scoped by the lead: it
was asked to do general hledger/Ledgerkit-source research (five broad
areas, including live-binary testing) rather than its actual, narrower
charter (judging whether CodeCompass context was useful for this task).
This mirrors how Stage C Phase 6's own design document used
"context-curator" informally to mean "a fresh research dispatch with no
conversation history" — a role-name conflation that worked out
harmlessly there but was caught explicitly this time when the dispatched
agent read its own `.claude/agents/context-curator.md` directly and
refused the mismatched assignment rather than silently overstepping.
Cost: one extra round-trip (the misdirected dispatch's own turnaround
time) before the correctly-scoped `compat-differential-tester` dispatch
could start. Not a wasted dispatch, though — it did do its actual job
correctly (checked CodeCompass, found the expected LOW-advantage
baseline, filed nothing) and its recommendation section correctly named
which real roles owned the work instead.

## Lessons learnt

- **"context-curator" is not a synonym for "fresh agent with no
  conversation history and CodeCompass access" — it is a specific role
  with a specific, narrow deliverable** (rate CodeCompass's usefulness
  for a task). When a phase needs general hledger-behaviour research or
  Ledgerkit-source auditing with no prior context, the correct dispatch
  is `compat-differential-tester` (for anything requiring the live
  binary), `hledger-researcher` (for manual/source-only research, no
  binary), or the lead doing it directly — not `context-curator`
  stretched to cover ground its own charter doesn't include. Check the
  role's actual `.claude/agents/*.md` file before writing its brief,
  not just the label used for it in a prior phase's retro.
- **A single shared chokepoint function is worth confirming explicitly
  before assuming a fix needs per-call-site changes** — this fix's
  entire footprint is one function, `validate_hledger_regex`, precisely
  because Ledgerkit's Phase 1 architecture already centralised regex
  validation there; a less careful design pass might have proposed
  changes to `_build_acct`/`_build_desc`/`_build_tag`/`_build_depth_
  spec` individually before checking whether the shared function alone
  was sufficient.

## Process-improvement feedback

Worth stating plainly for whoever next writes a dispatch brief: verify
which specialised agent role actually owns a piece of research before
briefing it, especially when a prior phase's retro used a role name
informally. The self-correcting agent this time caught its own
mis-scoping cleanly and cheaply — but a differently-behaved agent might
have silently done the work anyway outside its stated charter, which
would be worse than the one extra round-trip this cost.

## Learnings filed

None yet — deferred to implementation time (per this project's own
convention: `knowledge/DECISIONS.md`/`DOMAIN_RULES.md` entries land
with the code they document, not the design document alone, matching
Phase 6's own sequencing).

## Where we're going

Design document (`26-query-regex-empty-pattern-design.md`) is complete
and awaiting explicit human approval (§11's four-item gate) — the
same "stop and wait" point Phase 6's design used. No implementation
begins until that approval lands. Given the fix's small, fully
characterised size, the design document itself may double as the
implementation plan (§11 item 4 explicitly flags this as the
implementer's own call to confirm or dispute) rather than requiring a
separate `24-...-implementation-plan.md`-style document, unlike Phase
6's larger scope.

## Time / cost note

One continuous planning session: one misdirected dispatch (cheap,
self-corrected), one correctly-scoped `compat-differential-tester`
dispatch (the real research), and direct lead-performed source auditing
in parallel with it. Substantially smaller than Phase 6's own planning
effort, proportionate to this fix's much narrower scope.

## Addendum (2026-09-25, same day) — design-review correction pass

The user reviewed the design document and found it not yet ready for
approval on four specific points, none of which changed the fix's
actual scope or mechanism — a design-review correction, exactly the
same category as Phase 6's own two amendment rounds, not an
implementation defect (no `ledgerkit/`/`tests/*.py` code existed yet).

1. **The proposed exception message was `tag:`-specific advice inside
   a prefix-agnostic shared function.** `validate_hledger_regex` serves
   `acct:`/`desc:`/`depth:`/`tag:` alike and has no way to know which
   one called it — the original message's "use a bare `tag:NAME`..."
   advice was simply wrong for a caller reached via `acct:`. Corrected
   to fully generic wording; tag-specific guidance relocated to
   user-facing docs instead.
2. **"No public API change" was an inaccurate framing.** Signatures and
   the exception type genuinely are unchanged, so the Unauthorised
   Change Rule's protected-surface sense doesn't trigger — but
   documented *accepted-input behaviour* is changing (a call that used
   to succeed now raises), which is a real `api-spec.md`-relevant fact.
   Corrected to "backward-compatible compatibility/correctness change
   to documented behaviour," with `api-spec.md` update now explicitly
   listed as required, not skippable.
3. **A separately-discovered divergence (empty-alternation-branch
   regex syntax, `(|)` etc.) was left as an informal note in a research
   document rather than actually filed.** Corrected by filing
   `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`, deliberately scoped to only
   what's independently verified on both sides (`(|)` confirmed
   divergent; four sibling patterns confirmed only on hledger's side,
   explicitly not asserted as divergences) — the same "don't claim more
   than what's verified" discipline this project has applied
   consistently since Phase 6.
4. **The planned resolution mechanics for `LK-MISMATCH-QUERY-TAG-
   EMPTYVALUE-001` would have left a contradiction**: the original
   design said this entry "resolves from `unexplained_mismatch` to
   `compatible`" in place, but the register's own filename convention
   (`LK-<KIND>-<AREA>-<NNN>`, `KIND` tracking the `kind:` field) means a
   `MISMATCH`-prefixed ID classified `compatible` would contradict
   itself. Corrected to a rename-and-reclassify closeout process (new
   `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` entry, old one retired and
   removed from `UNEXPLAINED.md`) — a real process gap this phase's own
   design would otherwise have introduced into the register.

**Process observation**: this is the fourth successive instance across
this project's last two phases (Phase 6's two amendment rounds, this
phase's own correction) where a design document's stated claim needed a
review pass to catch — three of the four points here were framing/
process-mechanics errors rather than technical ones, a different flavor
from Phase 6's substantive semantic corrections but the same underlying
value: the human-approval gate keeps doing real work, not rubber-
stamping.

Approval list grew from four items to five (§11) — not because scope
grew, but because item 4 (mismatch-entry closeout mechanics) is now an
explicit, separate confirmation rather than folded silently into the
original item 1.
