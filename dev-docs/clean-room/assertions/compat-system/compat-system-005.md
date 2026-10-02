<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-005 | date: 2026-10-03 -->
# Assertion: compat-system-005

## Statement
The register implements a documented "resolution lifecycle" for `kind: unexplained_mismatch` entries: a mismatch is never a resting state; resolving one requires creating a brand-new entry (new id/kind/status) carrying `resolves: <old-id>`, while the original mismatch file is retained unmodified except for an added `resolved_into: <new-id>` / `resolved_date:` pair — the mismatch's own `kind` field is never edited in place. As of this survey, this mechanism has been exercised exactly twice, and both of the register's two `unexplained_mismatch` entries have been resolved (0 currently open).

## Kind
relationship
## Basis
directly_stated
## Evidence
schema.md lines 75-91 define `resolved_into`/`resolved_date`/`resolves` fields; lines 135-172 ("Resolution lifecycle" section) spell out the four-step procedure. Grep confirms both pairings exist: LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml:149 `resolved_into: LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` / :150 `resolved_date: "2026-09-25"`, reciprocally LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml:26 `resolves: LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`; and LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml:271 `resolved_into: LK-COMPAT-QUERY-REGEX-EMPTYALT-001` / :272 `resolved_date: "2026-09-27"`, reciprocally LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml:24 `resolves: LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`.

Evidence-paths: [dev-docs/compat-register/schema.md:75-91, dev-docs/compat-register/schema.md:135-172, dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml:149-150, dev-docs/compat-register/LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml:26, dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml:271-272, dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml:24]

## Justification
Both the mechanism's written definition and its only two real invocations are directly observable in the permitted yaml files; since `kind: unexplained_mismatch` count is exactly 2 (compat-system-003) and both carry `resolved_into`, 100% of currently-filed mismatches are resolved — this is a count fact, not an inference.
## Examples
LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml also documents, in its own header comment, that it followed "the same precedent as LK-COMPAT-QUERY-TAG-EMPTYVALUE-001's own resolution" — i.e. the second use of the mechanism explicitly cites the first as precedent, suggesting the lifecycle is being used consistently rather than reinvented each time.
## Counterexamples
None — no entry was found where `kind: unexplained_mismatch` was edited in place to a different kind (which the schema explicitly forbids), and no orphaned `resolves`/`resolved_into` reference (pointing to a nonexistent id) was found.
## Depends on
compat-system-003 (kind counts, establishing there are exactly 2 unexplained_mismatch entries).
## Open questions
This task's hard-rule scope forbade reading UNEXPLAINED.md, so step 3 of the documented lifecycle ("Update UNEXPLAINED.md: remove from Open entries, add to Resolved") could not be independently checked — whether that bookkeeping step was actually completed for either resolution is unverified by this survey.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)
