---
role: domain-skeptic
mode: comparison
topic: tags
dispatch-id: plan29-phase-comparison-tags-20261114
date: 2026-11-14
---

# Implementation comparison: `tags` — snapshot `tags-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/tags-v1.md` +
  `tags-v1.sidecar.json` (9 assertions, frozen 2026-10-02, repository
  revision `51881415a204af8908834ec602a54f6e1f67dbdd`).
- The 9 frozen assertion files under `dev-docs/clean-room/assertions/tags/`.
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/tags.md`
  (dispatch `plan29-phase-reconstruction-tags-20261003`, model-blind,
  evidence basis: `ledgerkit/tags.py`, `ledgerkit/models.py`,
  `tests/test_tags.py`, plus live execution — no access to the snapshot
  or assertions).

**Method.** Neither artefact was revised to force agreement. No source
or test file was read directly by this dispatch (comparison mode
compares the two clean-room artefacts only); all findings below rest on
what each artefact itself states.

## Classification summary

| Assertion | Kind | Classification |
|---|---|---|
| tags-001 | definition | aligned |
| tags-002 | rule | aligned |
| tags-003 | rule | aligned |
| tags-004 | rule | aligned |
| tags-005 | rule | aligned |
| tags-006 | rule | aligned |
| tags-007 | invariant | aligned |
| tags-008 | rule | aligned |
| tags-009 | boundary | aligned |

**9 aligned / 0 partial / 0 conflicting / 0 not_implemented / 0
insufficiently_verified.**

No conflicting or not_implemented findings to report for this topic.

## Per-assertion notes

**tags-001** (four-source union feeding `_effective_tags`). Reconstruction
§5.3 independently states the same return expression — `posting.tags +
txn.tags + _inherited_account_tags(journal, posting.account) +
_commodity_tags(journal, _posting_commodities(posting))` — as the
assertion's cited evidence. Aligned.

**tags-002** (no shadowing/dedup across the four sources, including exact
`(name, value)` duplicates). Reconstruction §5.3 independently concludes
"No deduplication of any kind... confirmed by reading the code (a flat
`+` of four lists)" and cites the same
`test_unions_all_four_sources_with_no_dedup_by_name` result. The
reconstruction did not itself construct the exact-duplicate-pair case
the assertion's review step added (it reasons from the general "plain
`+`, no union/set/dict" structure rather than a dedicated probe), but it
does not contradict the claim either. Aligned — alignment here is
structural-code-reading agreement, not independent duplicate-pair
confirmation from the reconstruction side.

**tags-003** (`_accounts_effective_tags`'s narrower two-source union).
Reconstruction §5.3 states the identical return expression (`txn.tags +
_inherited_account_tags(...)`, explicitly excluding posting tags and
commodity tags) and independently cites
`test_excludes_posting_own_and_commodity_tags`. Both artefacts
independently flag the same unverifiable sub-claim — that this function
is actually wired up to `ledgerkit.reports.accounts` /
`ledgerkit.query.eval`'s accounts-mode dispatch — as outside their
respective permitted evidence paths (assertion's own "Open questions";
reconstruction §7's "actual caller could not be verified"). This
agreement-on-the-limits-of-verification is itself a form of alignment,
not a gap between the two artefacts: neither claims more than the
function's own behaviour in isolation, which both confirm. Aligned.

**tags-004** (`_inherited_account_tags` ancestor-prefix walk,
sibling-does-not-inherit). Reconstruction §5.3 independently describes
the identical mechanism: "splits `account` on `:`... builds every
progressively longer prefix... concatenates... for each — so an account
inherits from itself and every ancestor, in least-specific-first order,
not deduplicated." Aligned.

**tags-005** (space-before-colon voids the whole candidate; scanning
resumes after the voided colon). Reconstruction §5.1 independently
states and live-confirms the identical behaviour, including the same
illustrative case (`parse_tags("a b : c:d") → [('c', 'd')]`,
functionally equivalent to the assertion's cited
`test_space_before_colon_then_a_real_tag_later`). Aligned.

**tags-006** (comma/end-of-line terminates a value; colon inside a value
does not; no comma-escaping). Reconstruction §5.1 point 5 and §7
("No comma-escaping in tag values... real, permanent limitation") state
the same mechanism and the same "not an oversight" framing. Aligned.

**tags-007** (ordered list, never collapsed by name; no character-class
restriction on tag names, contra the hledger manual's prose). 
Reconstruction §5.1 point 6 and §7 state the identical ordered-list/no-
collapse claim, and independently live-tests a non-ASCII tag name
(`日本語:value`) to confirm the no-character-class-restriction claim —
the same category of evidence the assertion cites via
`test_no_character_class_restriction_on_name`. Aligned.

**tags-008** (`effective_date`/`effective_date2` four-level fallback
chain, including primary override reused as secondary fallback).
Reconstruction §5.2 states the identical chain in the identical order —
`posting.date2_override → txn.date2 → posting.date_override → txn.date`
— and explicitly confirms "This reuse-of-primary-as-secondary-fallback
step is real code, not just a docstring claim." Aligned.

**tags-009** (`_posting_commodities` is always 0/1-element;
`_commodity_tags` is plural/list-shaped for forward-compatibility only).
Reconstruction §5.3 and §7 state the identical structural claim —
"Always 0 or 1 elements, since `Posting.amount` is a single `Amount`...
the docstring explicitly flags this as a deliberate single-item special
case" — and independently frames the plural `_commodity_tags` signature
as describing "a capability the current data model does not actually
have yet," matching the assertion's own framing and its "structural
impossibility, not an outstanding ambiguity" resolution of its open
question. Aligned.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification**. For
every `rule`/`invariant`-kind assertion above (tags-002 through
tags-008, and tags-007), the "aligned" classification means only that
the independently-reconstructed as-built behaviour currently matches
what the snapshot asserts — it does not, by itself, establish that the
asserted rule (e.g. "no dedup is correct design," "the sibling/ancestor
boundary is the right boundary," "the four-level date fallback is the
right fallback") is itself the *right* behaviour relative to hledger's
own semantics. Both artefacts are explicit, in their own text, that
questions of "is this the correct choice relative to hledger" are out of
scope for their respective evidence (tags-002's "Open questions";
tags-009's "structural impossibility... not an outstanding ambiguity").
This comparison report preserves that distinction rather than
collapsing "matches the code" into "is correct."

## What was checked

- All 9 assertion `Statement`/`Evidence`/`Examples` fields against the
  reconstruction report's §2–§7 content, assertion-by-assertion.
- Whether either artefact's stated uncertainties (tags-003's and
  tags-009's "open questions") were silently resolved one way or the
  other by the other artefact — they were not; both independently land
  on the same unresolved boundary in each case, which is recorded above
  as part of the alignment rather than suppressed.
- No contradiction, partial divergence, or not-implemented claim was
  found between the frozen snapshot's 9 assertions and the independent
  reconstruction for this topic.

## Escalations

None. No genuine conflicting or not_implemented classification arose
for this topic; nothing is escalated to the lead.
