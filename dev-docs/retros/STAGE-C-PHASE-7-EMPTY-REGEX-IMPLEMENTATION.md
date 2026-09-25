# Stage C Phase 7 retro — Implementation (empty-regex-pattern rejection)

- **Date:** 2026-09-25
- **Commit(s):** see `git log` for this retro's own commit (implementation
  landed in the same response as this retro).
- **Agents used:** none for implementation itself — the fix's small,
  fully-characterised size meant no fresh coding-agent dispatch was
  needed (design §11 item 5 left this to the implementer's judgment).
  Independent verification (Step 7) is a separate, genuinely-dispatched
  `compat-differential-tester` — see "Where we're going" below; not yet
  run as this retro is written.

## Where we are

Following directly from `STAGE-C-PHASE-7-EMPTY-REGEX-PLAN.md` (design
document, amended twice on review) — this retro covers turning the
amended, approved design into real `ledgerkit/`/`tests/` code. Stage C
Phase 6 closed `[DONE]` with this fix named as backlog item 1; this
phase resolves it.

## Goal

Implement the approved fix: `validate_hledger_regex("")` raises
`UnsupportedRegexConstructError`, with a generic (not `tag:`-specific)
message; treat this accurately as a breaking, not backward-compatible,
change made pre-1.0; keep the empty-alternation-branch family out of
scope; fix the compat-register lifecycle so a resolved mismatch is
renamed-and-linked, not edited in place; cover the full test matrix; and
stop before any compat-register promotion until independent verification
runs.

## Scope delivered vs planned

Everything in the amended design's §5/§9/§10/§11 shipped, plus the two
register-schema/process amendments the implementation task itself asked
for (not originally in the design document, added as explicit
implementation-time instructions): the resolution-lifecycle mechanism
(`resolved_into`/`resolved_date`/`resolves` fields, `schema.md`'s new
"Resolution lifecycle" section, `09-compatibility-system.md` §9.7) and
the `implementation`/`tests`-may-be-empty-for-`unexplained_mismatch`
schema correction. Both fixed as general-purpose register mechanisms,
not phase-7-specific, per explicit instruction.

No scope cuts. Deliberately not done here, per explicit instruction:
`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`'s actual resolution (creating
`LK-COMPAT-QUERY-TAG-EMPTYVALUE-001`, moving the row in `UNEXPLAINED.md`)
is deferred to after independent verification — applying the new
lifecycle mechanism to this specific entry before that verification
lands would violate the same verification-independence rule the
mechanism itself is meant to support.

## What was achieved

`ledgerkit/query/regex.py`'s `validate_hledger_regex` gained one check
(`pattern == ""`, raising the existing `UnsupportedRegexConstructError`
with a fully generic message) — the single shared chokepoint every
regex-taking query term already routed through meant zero changes were
needed to `_build_acct`/`_build_desc`/`_build_depth_spec`/`_build_tag`,
`ledgerkit/query/depth.py`, or `ledgerkit/query/eval.py`, exactly as the
design predicted.

17 new tests: `tests/test_query/test_regex.py` (`TestEmptyPattern`,
`TestEmptyMatchingPatternsRemainAccepted` — explicit regression guards
for `.*`/`a*`/`^$`/`()` staying accepted, and for the message containing
no `tag:`-specific text), `tests/test_query/test_parser.py`
(`TestEmptyPatternRejected` covering `acct:`/`desc:`/bare `tag:`/
`tag:NAME=`/`depth:=N`/`not:acct:`, plus the existing
`test_empty_value_pattern_is_not_none` rewritten to
`test_empty_value_pattern_rejected`), `tests/test_cli/test_cli.py` (two
new tests confirming the CLI's existing `QueryParseError`-to-exit-1/
`"invalid query"` convention is reused unchanged, no new error-handling
path invented). 844 tests total (up from 827), all passing.

Documentation: `dev-docs/api-spec.md` (both functions' docstrings plus a
"Breaking change from Stage C Phase 6" note, mirroring the project's own
existing precedent for this exact phrasing from Milestone 2→3);
`dev-docs/versioning.md` (a new "Breaking changes during the
`1.0.0.dev1` pre-release" section — general policy, not phase-specific:
breaking changes get recorded accurately, but don't themselves trigger a
version bump before the first stable `1.0.0` ships); `dev-docs/hledger-
compatibility.md` (`acct:`/`desc:`/`depth:`/`tag:` rows updated);
`docs/usage.md` (the bare-`tag:NAME`-vs-`tag:NAME=` guidance the shared
validator's own message deliberately excludes); `knowledge/DECISIONS.md`
(two new entries — the breaking-change framing, and the register
resolution mechanism); `knowledge/DOMAIN_RULES.md` (one new entry — the
narrow-vs-broad empty-pattern scoping rule).

## What worked

- **Checking the actual chokepoint before writing any code** confirmed
  the design's own prediction exactly — one function, one check, zero
  call-site changes. No implementation surprises.
- **The api-spec.md "Breaking change from Milestone N" precedent**
  (found by grep before writing new prose) meant this phase didn't
  invent a new way to describe a breaking pre-1.0 change — it reused an
  established, already-legible convention.

## What didn't work

No misfires this phase. The one area needing real care rather than
mechanical execution was the compat-register schema amendment (the
resolution-lifecycle mechanism) — getting the general-vs-phase-specific
framing right (the schema/process docs describe a mechanism, not just
this one entry's resolution) took more drafting attention than the code
fix itself.

## Lessons learnt

- A design document's own careful framing (§5.1's "backward-compatible
  compatibility/correctness fix") can still be wrong in a way that only
  surfaces once someone asks the sharper question ("is this actually
  backward-compatible, or does it just not matter yet because nothing's
  shipped?") — pre-1.0 status doesn't make a breaking change not
  breaking, it just changes the version-bump consequence. Worth
  remembering for any future pre-1.0 behaviour-narrowing fix.
- When a compat-register lifecycle gap is found while resolving one
  specific entry, fix the *mechanism* generally rather than special-
  casing that one entry — the schema/process documents are the right
  place for the fix, not a one-off note on the entry itself.

## Process-improvement feedback

No process notes this phase — implementation, at this fix's scale,
didn't need a fresh coding-agent dispatch, and the design/plan handoff
(such as it was, folded into one document per §11 item 5's own
allowance) worked cleanly.

## Learnings filed

- `knowledge/DECISIONS.md`: two new dated entries (breaking-change
  framing; register resolution mechanism).
- `knowledge/DOMAIN_RULES.md`: one new entry (narrow empty-string-only
  scoping, contrasted with the rejected broader "admits empty match"
  rule).

## Where we're going

Independent verification (Step 6 of the implementation task, a
genuinely separate `compat-differential-tester` dispatch per
`09-compatibility-system.md` §9.6) is the mandatory next step — **not
performed by this session**. Until it lands: no compat-register entry
is promoted, `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` stays exactly as
filed (open, unresolved, in `UNEXPLAINED.md`'s "Open entries" table),
and Phase 7 is not proposed for `[DONE]`. `LK-MISMATCH-QUERY-REGEX-
EMPTYALT-001` remains untouched and out of scope, as it was throughout
this phase.

## Time / cost note

One continuous implementation session, no sub-agent dispatches for the
code itself. Proportionate to the fix's small size — the bulk of the
effort was the compat-register schema/process amendment (general-
purpose, not phase-specific) rather than the one-check code fix.
