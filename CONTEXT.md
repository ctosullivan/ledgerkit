# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 7 (empty-regex-pattern rejection, resolving `LK-MISMATCH-
QUERY-TAG-EMPTYVALUE-001`) — design document amended after a targeted
review-correction pass (four points, none re-scoping the fix). **Still
stopped for explicit human approval** — no `ledgerkit/`/`tests/*.py`
code touched.

## Where We Are
Design document: `dev-docs/planning/core-redefinition/26-query-regex-
empty-pattern-design.md`, now amended (§5/§5.1, §7, §8, §11 corrected).
New compat-register entry filed this pass: `dev-docs/compat-register/
LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml` (the empty-alternation-
branch divergence, `(|)` etc. — separate from this phase's own fix,
explicitly not implemented). Retro addendum, `ROADMAP.md`, `CHANGELOG.md`
updated. About to commit + push, then wait — do NOT proceed to
implementation until explicit approval arrives.

## Decisions In Flight
Design §11's five-item approval gate (grew from four after this pass),
all open:
1. Approve the fix: `pattern == ""` check in `validate_hledger_regex`,
   raising the existing `UnsupportedRegexConstructError` — no new
   exception class, no signature change. (Now correctly framed as a
   real, documented-behaviour change requiring an `api-spec.md`
   update, not "no API change.")
2. Approve the corrected, fully generic error message: *"pattern must
   not be empty (hledger rejects an empty regex at parse time)"* — no
   `tag:`-specific advice in the shared validator.
3. Confirm the empty-alternation-branch family stays filed
   (`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`) but unimplemented this
   phase.
4. Confirm the `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` closeout
   mechanics: rename-and-reclassify to a new `LK-COMPAT-QUERY-TAG-
   EMPTYVALUE-001` entry once independently verified, not an in-place
   `kind:` flip.
5. General approval to proceed — likely no separate implementation-plan
   document needed given the fix's small size.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/26-query-regex-empty-pattern-
  design.md` — the amended design document awaiting approval.
- `dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`
  — newly filed this pass; `(|)` confirmed divergent both sides,
  `a|`/`|a`/`(a|)`/`(|a)` hledger-side-only confirmed.
- `dev-docs/compat-register/UNEXPLAINED.md` — now lists both open
  entries.
- `ledgerkit/query/regex.py` — `validate_hledger_regex`, the single
  proposed change site (unchanged from before this correction pass).
- `docs/usage.md` — will need the tag-specific escape-hatch guidance
  (bare `tag:NAME`) once implemented; not the shared validator message.

## Blockers / Open Questions
The five-item approval gate above. Nothing else blocking.

## What NOT To Revisit
- Don't re-derive the empty-string-vs-empty-matching scoping question —
  settled executably in the prior planning pass, unchanged by this
  correction pass.
- Don't put `tag:`-specific advice back into `validate_hledger_regex`'s
  exception message — it's a shared, prefix-agnostic chokepoint;
  `acct:`/`desc:`/`depth:` callers would get wrong advice.
- Don't describe this fix as "no public API change" — signatures are
  unchanged but documented accepted-input behaviour changes; frame as
  a backward-compatible compatibility/correctness fix, and update
  `api-spec.md` accordingly at implementation time.
- Don't fold the empty-alternation-branch family into this fix's
  implementation — it's filed (`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`)
  but explicitly out of scope. Don't add unverified patterns to that
  entry's confirmed-divergence claims either — only `(|)` has both
  sides checked so far.
- Don't resolve `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` by flipping its
  `kind:` field in place — the register's own filename convention
  requires a rename to a new `LK-COMPAT-*` ID when it's reclassified.
- Don't use `context-curator` for general hledger/source research —
  established in the prior planning pass, still holds.

## Recent Git State (before this response's commit)
c4feb1d docs: Stage C Phase 7 -- empty-regex-pattern rejection design
a49ac50 docs: close out Stage C Phase 6, mark [DONE]
5887ea8 docs: close out Stage C Phase 6 independent verification
fe9dfe5 test: independently verify Stage C Phase 6 tag: compat-register entries
cb06d1f docs: update CONTEXT.md for Stage C Phase 6 implementation end state
