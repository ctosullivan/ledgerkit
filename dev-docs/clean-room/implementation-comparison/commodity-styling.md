---
role: domain-skeptic
mode: comparison
topic: commodity-styling
dispatch-id: plan29-phase-comparison-commodity-styling-20261114T000000Z
date: 2026-11-14
---

# Implementation comparison: `commodity-styling` — snapshot `commodity-styling-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/commodity-styling-v1.md` +
  `commodity-styling-v1.sidecar.json` (8 assertions, frozen
  2026-10-02T16:50:03Z, repository revision
  `51881415a204af8908834ec602a54f6e1f67dbdd`).
- The 8 frozen assertion files under
  `dev-docs/clean-room/assertions/commodity-styling/`.
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/commodity-styling.md`
  (dispatch `session_014zQZ8FHzgy8VTjoy79bmYm` @ 2026-10-03T00:55:47+08:00,
  model-blind, evidence basis: `ledgerkit/commodity_style.py`,
  `ledgerkit/models.py`, `tests/test_commodity_style.py`, partial reads of
  `tests/test_parser/test_parser.py`, plus live execution — no access to
  the snapshot or assertions).

**Method.** Neither artefact was revised to force agreement. No source or
test file was read directly by this dispatch (comparison mode compares
the two clean-room artefacts only); all findings below rest on what each
artefact itself states.

## Classification summary

| Assertion | Kind | Classification |
|---|---|---|
| commodity-styling-001 | rule | aligned |
| commodity-styling-002 | rule | aligned |
| commodity-styling-003 | rule | aligned |
| commodity-styling-004 | rule | aligned |
| commodity-styling-005 | rule | aligned |
| commodity-styling-006 | rule | aligned |
| commodity-styling-007 | state_transformation | aligned (one sub-claim not corroborated, not contradicted) |
| commodity-styling-008 | boundary | aligned |

**8 aligned / 0 partial / 0 conflicting / 0 not_implemented / 0
insufficiently_verified.**

No conflicting or not_implemented findings to report for this topic.

## Per-assertion notes

**commodity-styling-001** (prefix/suffix detection via
`startswith`/`elif endswith`, degenerate-both-match resolves to prefix,
no-match fallback silently treats the whole stripped string as numeric).
Reconstruction §5 independently describes the identical mechanism: "Checks
`s.startswith(commodity)` → prefix; else `s.endswith(commodity)` → suffix;
else neither... the *entire* stripped string... is treated as 'numeric'".
The reconstruction's own live probes (`infer('X','abc')`, `infer('X','')`,
and the quoted-commodity gap) independently confirm the assertion's
claim that this fallback never raises and silently degrades rather than
erroring — matching the assertion's Counterexamples section, which
reports the same "silent corruption, no test coverage" finding from its
own live execution. Aligned.

**commodity-styling-002** (single-separator heuristic: exactly one
occurrence, not at position 0, exactly 3 digits after → group separator;
otherwise decimal mark). Reconstruction §5 states the identical rule for
both the dot-only and comma-only branches, in the same words structurally
("exactly one dot, with exactly 3 digits after it, and the dot isn't at
position 0... otherwise `.` is the decimal mark"). The reconstruction's
independent live probe of the 4-digit case (`_infer_separators("1,2345")
→ (',', '', 4)`) exercises exactly the boundary condition the assertion's
Counterexamples section reasons about (3-digit vs. non-3-digit) from code
reading alone. Aligned.

**commodity-styling-003** (both separators present → rightmost wins as
decimal mark, regardless of repeat counts). Reconstruction §5 states the
identical rule and independently live-verifies it against a *multi-group*
string (`"1.234.567,89"` → `(',', '.', 2)`), a stronger case than any
example cited in the assertion itself (whose examples are all
single-group). Both artefacts separately flag that the rule does not
validate earlier groups' digit-width — the assertion does not make this
observation itself (it belongs to commodity-styling-002's Counterexamples
and the reconstruction's own gap list, §7 item 5), but neither artefact's
treatment of 003's actual stated rule disagrees. Aligned.

**commodity-styling-004** (negative-sign placement: prefix drops the
`space` gap entirely when negative; suffix preserves the gap). Reconstruction
§5 states this with the same structural detail — noting the prefix-negative
f-string has no `{gap}` token at all, so `space` is "structurally
irrelevant to that branch" — and independently live-verifies the
`space=True` + prefix + negative combination the assertion itself flags as
previously untested-by-suite (`CommodityStyle("$", prefix=True,
space=True,...).format(Decimal("-1234.56"))` → `"$-1,234.56"`, no space,
vs. `"$ 1,234.56"` for the positive case on the same style object). Both
artefacts independently reach the same live-execution conclusion by the
same method. Aligned.

**commodity-styling-005** (`Journal.commodity_styles` three-pass priority:
posting-amount first-seen, then price-directive first-seen, then
`commodity`-directive entries unconditionally overwriting both). Reconstruction
§5 states the identical three passes in the identical order and priority
outcome: "`_commodity_directive_raws` entries unconditionally overwrite
whatever passes 1/2 set for that commodity... matching the property's own
docstring." Neither artefact backs this with a dedicated test exercising
the priority-override case directly (the assertion's own Evidence-support
state is `partially_supported` for exactly this reason; the reconstruction
likewise derives this purely from reading `models.py`, not from live
execution or an existing test). This is a case where **alignment is not
verification**: both artefacts agree on what the code does, from the same
kind of evidence (direct code reading), but neither establishes it with a
test — a limitation both already say about themselves, not a gap this
comparison is surfacing for the first time. Aligned.

**commodity-styling-006** (`parse_style_override` tries suffix-regex
before prefix-regex; raises `ValueError` on empty/no-digit/matches-neither;
override is scoped per-commodity, not global). Reconstruction §2 and §5
state the identical regex-ordering and both raise conditions, and
independently exercises the per-commodity scoping via the same CLI test
(`TestCLIIntegration`'s "different commodity has no effect" case).
Reconstruction additionally live-confirms the assertion's own
previously-untested third raise branch would behave consistently were a
bare-numeric override attempted (both artefacts independently ran
`parse_style_override` against a numeric-only string and got the same
`ValueError` outcome — the assertion against `"123.45"`, the reconstruction
against `"1,234.56"`). Aligned.

**commodity-styling-007** (`resolve_elision` produces one inferred,
negated posting per distinct commodity, alphabetically sorted by
commodity symbol, inferred=True, spliced in at the original elided
posting's position). Reconstruction §6 independently states the
alphabetical-sort-by-commodity-symbol claim in the same terms, citing the
same `sorted(["EUR", "$", "£"])` ordering example, and independently
notes (consistent with the assertion's own "Depends on"/"Open questions")
that `resolve_elision`'s own implementation lives outside the permitted
evidence paths (not in `commodity_style.py` or `models.py`), so both
artefacts evidence this purely via the test file's observed behaviour.
The reconstruction's summary does not explicitly restate the
position-preservation sub-claim (splicing in-place rather than appending)
— it is silent on that specific point rather than contradicting it, most
likely because its read range for `test_parser/test_parser.py` (up to
line 480) falls just short of the assertion's own self-corrected citation
range (432-483, which the assertion's review note says originally missed
lines 480-483 too). This is a reporting-completeness gap in the
reconstruction, not a disagreement between the two artefacts — nothing in
the reconstruction contradicts position preservation. Aligned, with that
one sub-claim noted as not independently corroborated by the
reconstruction (also not contradicted).

**commodity-styling-008** (`ReportSectionResult.to_dataframe()`'s
single-commodity limitation: dead first assignment to `commodity` from
account-name keys, immediately overwritten by
`next(iter(self._commodity_styles), "")`, applied uniformly to every row
regardless of the row's actual commodity). Reconstruction §5 quotes the
identical code fragment near-verbatim, including the same in-code comment
text ("Actually rows are account names, not commodities...") and reaches
the identical conclusion that the first assignment is dead code with "no
observable effect." Both artefacts independently flag that no test in
scope exercises this method. Aligned.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification**. For
every `rule`-kind assertion above (001-006), and the `boundary`/
`state_transformation`-kind assertions (007, 008), "aligned" means only
that the independently-reconstructed as-built behaviour currently matches
what the snapshot asserts — it does not establish that the asserted rule
is the *correct* one relative to hledger's own semantics, nor that the
underlying implementation is bug-free. The reconstruction report itself
is explicit that several of these "aligned" mechanisms are, in its own
assessment, real limitations or inconsistencies in the implementation
(e.g. `format()`'s rounding at `precision > 0` vs. truncation at
`precision == 0`; `infer()`'s mishandling of quoted/multi-word
commodities if `Amount.raw` retains quote characters; the complete
inability of `parse_style_override()` to express a quoted-commodity
override) — none of which any of the 8 frozen assertions makes a claim
about, so none of these is classified above (there is no corresponding
assertion to compare against). They are recorded here as reconstruction-only
observations that fall outside this topic's current assertion coverage,
not as a conflicting or not_implemented finding, and not as an invitation
to treat "aligned" as "correct."

## What was checked

- All 8 assertion `Statement`/`Evidence`/`Examples`/`Counterexamples`
  fields against the reconstruction report's §2-§7 content,
  assertion-by-assertion.
- Whether either artefact's stated uncertainties (001's unresolved
  reachability-via-`_commodity_directive_raws` open question, 005's
  untested-priority-override claim, 006's out-of-scope CLI-wiring open
  question, 007's out-of-scope `resolve_elision` implementation, 008's
  out-of-scope `balance_from_spec` producer) were silently resolved one
  way or the other by the other artefact — they were not; both
  independently land on the same unresolved boundary in each case.
- Whether the reconstruction surfaced anything that directly contradicts
  a frozen assertion's stated rule — none found.
- Whether the reconstruction surfaced behaviour/limitations with no
  corresponding assertion at all (a knowledge-base gap, not a comparison
  failure) — yes: see Verification caveat above (rounding/truncation
  inconsistency in `format()`; quoted/multi-word-commodity gaps in both
  `infer()` and `parse_style_override()`). These are not classified
  against any of the 8 assertions because none of the 8 makes a claim
  these could agree or disagree with.

## Escalations

None. No genuine conflicting or not_implemented classification arose for
this topic; nothing is escalated to the lead. The reconstruction-only
gaps noted under "Verification caveat" are flagged for whoever scopes the
*next* assertion-research pass for this topic (they are not ambiguities
for this comparison to resolve, since there is nothing in the frozen
snapshot to compare them against).
