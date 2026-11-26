---
role: domain-skeptic
mode: comparison
topic: journal-parsing
dispatch-id: plan29-phase-domainskeptic-comparison-journal-parsing-20261114T081914Z
date: 2026-11-14
---

# Implementation Comparison: journal-parsing

Inputs compared:
- Frozen snapshot: `dev-docs/clean-room/snapshots/journal-parsing-v1.md` +
  `journal-parsing-v1.sidecar.json` (repo revision `51881415a204af8908834ec602a54f6e1f67dbdd`)
- 10 frozen assertion files: `dev-docs/clean-room/assertions/journal-parsing/journal-parsing-00{1..9}.md`,
  `journal-parsing-010.md`
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/journal-parsing.md`
  (model-blind, no access to the snapshot/assertions)

Per this role's write boundary, no `ledgerkit/*.py`/`tests/*` source was read or
executed by me; all code-level claims below are read off the two artefacts
being compared. Neither artefact was revised to force agreement — this report
records disagreement and gaps as found.

**Reminder embedded in every classification below: `aligned` records that the
snapshot's assertion and the as-built evidence currently agree, not that the
underlying claim is correct.** This matters most for `journal-parsing-005`
and `journal-parsing-010`, both `kind: rule`/`invariant` assertions where
"aligned" means "the code currently implements the stated rule," not "the rule
is the right one."

## Classification summary

| Assertion | Classification | One-line reason |
|---|---|---|
| journal-parsing-001 | aligned | `_TXN_HEADER` structure/date-form claims match reconstruction's regex inventory; no contradiction found |
| journal-parsing-002 | aligned | `_SIMPLE_DATE`/default-year/invalid-date behaviour matches; reconstruction confirms full test suite (233 tests) passes |
| journal-parsing-003 | aligned | two-space account/amount split and elision fallback match reconstruction's `_parse_posting` description |
| journal-parsing-004 | aligned | amount-form coverage (prefix/suffix/negative/comma-thousands/decimal-mark/space-groups/E-notation) matches regex inventory in reconstruction §1 |
| journal-parsing-005 | aligned | reconstruction independently live-confirms `resolve_elision` is a pure, parser-decoupled post-processing step with exactly the 0/1/2+ behaviour asserted |
| journal-parsing-006 | aligned | reconstruction reads the same T/B/I/F/S-series tests in full and confirms the column-0-vs-indented, `;`-vs-`#` distinctions as stated |
| journal-parsing-007 | **partial** | directive inventory matches, but omits a reconstructor-found failure mode: `account`/`commodity`/`payee`/`tag` directives silently discard subsequent posting lines of a still-open transaction block |
| journal-parsing-008 | **partial** | correctly identifies the commodity-directive "never raises" exception, but its "except one" count is contradicted by a second, independently-typed exception the reconstructor found (alias replacement backreference escapes as uncaught `re.PatternError`, not even `ParseError`) |
| journal-parsing-009 | **partial** | composability claim holds, and the already-documented bare-leading-`=` prefix-commodity failure is confirmed; but the assertion's resolved open question generalizes to "it simply fails amount parsing," which the reconstructor shows is false for the suffix-commodity + comma-decimal-mode case (silent corruption, not an error) |
| journal-parsing-010 | aligned | posting-only, first-occurrence-wins, no-transaction-level-effect claims all independently corroborated, including the specific "no override effect" `models.py` comment |

No assertion was classified `conflicting`, `not_implemented`, or
`insufficiently_verified`.

## Detail: the three reconstructor-found bugs, mapped to assertions

The reconstruction report (§7) found three production bugs not described by
any of the 10 assertions as their own distinct failure mode. None is a
mutual, irreconcilable disagreement between the two artefacts (so none is
`conflicting`) — in each case the relevant assertion's core claim remains
true as far as it goes, but is incomplete once the specific failure mode is
known. Per the dispatch's own guidance, I classified each as `partial` on the
assertion covering its general area, rather than inventing a new,
unaddressed-topic category.

1. **Alias-directive backreference crash** (`alias /(foo)/ = \2` → uncaught
   `re.PatternError` from both `parse_string` and `parse_string_lenient`).
   Mapped to **journal-parsing-008** (the strict-vs-lenient error-handling
   policy assertion). That assertion already names one exception to "never
   raises" (the malformed `commodity` directive, itself a finding from a
   prior REVIEW-mode pass dated 2026-10-03) and phrases its claim as "for
   every directive handler except one." The reconstructor's independent,
   live-executed finding is a *second* exception, of a different kind
   entirely (a bare `re.error` subclass escaping `_apply_aliases`'s
   unconditional `re.sub`, not a `ParseError` at all, and not raised from the
   directive-parsing branch but later from the posting-line/`account`-directive
   branch that applies the alias). This falsifies the "except one" count
   without disputing the assertion's underlying thesis (lenient mode's
   "never raises" guarantee is not actually universal). Classified `partial`
   rather than `conflicting` because the two artefacts agree on the general
   claim and disagree only on its completeness/scope, not on a single fact
   both assert in contradictory ways.

2. **Directive-mid-open-transaction silent data loss** (`account`, and by the
   reconstructor's structural read also `commodity`/`payee`/`tag`, directives
   appearing between two posting lines of a still-open transaction block
   silently discard every subsequent posting line of that block — no error,
   no warning). Mapped to **journal-parsing-007** (the directive-inventory
   assertion). That assertion correctly enumerates every directive and its
   handler, and its own Counterexamples section already corrects a prior
   evidence-path error about `comment`/`apply account` structure, but it says
   nothing about what happens when any of these directives appears while a
   transaction block is still open — the specific failure mode the
   reconstructor traced to a missing `current_txn is not None` guard shared
   by these four (but not by the `~`, `=`, `comment`, or transaction-header
   branches, which do flush/guard correctly). No assertion in the set
   addresses transaction-vs-directive interleaving at all, so this is
   classified as a gap in journal-parsing-007's coverage (`partial`) rather
   than a contradiction of anything it states.

3. **Balance-assignment-elision silent corruption for suffix-commodity amounts
   under comma-decimal mode** (`a  = 100,00 EUR` → `Amount(quantity=Decimal
   ('100.00'), commodity='=')` with `balance_assertion=None`, silently, vs.
   the clean `ParseError` the same unimplemented feature produces for a
   prefix-commodity amount). Mapped to **journal-parsing-009**, whose already-
   resolved Open Questions section (from a prior REVIEW-mode pass) states
   generally that "ledgerkit does not currently implement hledger's
   balance-assignment-elision posting syntax... it simply fails amount
   parsing" — but that resolution's own reproduction only tested the
   prefix-commodity case (`= $500`). The reconstructor's independent
   construction of the suffix-commodity + comma-decimal-mode variant shows
   the generalization is false: that variant does not fail at all, it
   silently produces a wrong `Amount` and silently drops the balance
   assertion. This is a real omission in 009's generalized claim (not every
   attempt "simply fails amount parsing" — one attempt succeeds with wrong,
   uncaught output), so classified `partial`.

## Why no `conflicting`, `not_implemented`, or `insufficiently_verified`

- **`conflicting`** would require the two artefacts to make genuinely
  irreconcilable claims about the same specific fact, with neither
  preferable. I found none: every divergence above is the reconstruction
  supplying a failure mode the relevant assertion's broader claim did not
  anticipate or address, not the two sources asserting opposite things about
  the identical case.
- **`not_implemented`** would require an assertion describing
  intended/proposed behaviour the as-built evidence shows does not exist at
  all. All 10 assertions describe behaviour the reconstruction confirms does
  exist and run (the deliberately-deferred `~`/`=` rule-body parsing,
  mentioned only in the reconstruction's §7 point 4, is explicitly out of
  scope by design per in-code comments and is not claimed as implemented by
  any of the 10 assertions, so there is no assertion to classify this way
  against).
- **`insufficiently_verified`** would require neither artefact to have enough
  evidence to classify confidently. Every assertion here has either a
  reconstructor-confirmed structural match, a reconstructor-run full test
  suite (233/233 passing, read in full across both test files) backing it,
  or (for the three partials) a specific, reconstructor-live-executed
  counter-input — none were left as an open evidentiary gap on both sides.

## Escalations

None. All findings above are recorded as `partial` with a named, specific
divergence; no genuine unresolved ambiguity requiring lead/user adjudication
was identified in this comparison pass.
