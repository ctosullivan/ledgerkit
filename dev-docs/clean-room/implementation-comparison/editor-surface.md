---
role: domain-skeptic
mode: comparison
topic: editor-surface
dispatch-id: plan29-phase-comparison-editor-surface-20261114T161900Z
date: 2026-11-14
---

# Implementation comparison: `editor-surface` — snapshot `editor-surface-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/editor-surface-v1.md` +
  `editor-surface-v1.sidecar.json` (10 assertions, frozen
  2026-10-02T16:50:03Z, repository revision
  `51881415a204af8908834ec602a54f6e1f67dbdd`; external repository
  `ledgerkit-editor` pinned at `b03c203316a9f99593173feaeea7ba7dad91e060`).
- The 10 frozen assertion files under
  `dev-docs/clean-room/assertions/editor-surface/` (editor-surface-001
  through -010).
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/editor-surface.md`
  (dispatch `plan29-phase-implrecon-editor-surface-20261003T005502+0800`,
  model-blind, evidence basis: `ledgerkit/editor_model.py`,
  `tests/test_editor_model.py`, and the same pinned
  `ledgerkit-editor` clone commit, verified by the reconstructor itself
  via `git rev-parse HEAD` — no drift from the pin — with no access to
  the snapshot or assertions).

**Method.** Neither artefact was revised to force agreement. No source
or test file, and no file from the external clone, was read directly by
this dispatch — comparison mode compares the two clean-room artefacts
only; all findings below rest on what each artefact itself states. The
reconstruction's headline finding — that `EditorDocument` has zero real
usage anywhere in the `ledgerkit-editor` clone's code — is treated
throughout as a separate question from whether `EditorDocument` itself
behaves as asserted. "Unused" and "behaves as asserted" are classified
independently per assertion below, per this dispatch's instructions.

## Classification summary

| Assertion | Kind | Subject | Classification |
|---|---|---|---|
| editor-surface-001 | definition | `EditorDocument`'s public surface (ledgerkit-side) | aligned |
| editor-surface-002 | rule | `__init__` uses `parse_string`, not `loader.load_journal`; V1 include limitation | aligned |
| editor-surface-003 | state_transformation | mutation methods set `dirty`, conditionally shift spans | aligned |
| editor-surface-004 | definition | `validate_transaction` delegates solely to autobalanced check | aligned |
| editor-surface-005 | boundary | module docstring's stated intended-consumer / core-module boundary | aligned |
| editor-surface-006 | relationship | `ledgerkit-editor` pins `ledgerkit==1.0.0.dev1` | aligned |
| editor-surface-007 | boundary | `EditorDocument` never imported/instantiated in the clone | aligned |
| editor-surface-008 | relationship | six `src/` files import `ledgerkit` at runtime, never `EditorDocument` | aligned |
| editor-surface-009 | relationship | test suite imports a broader `ledgerkit` symbol set, never `EditorDocument` | aligned |
| editor-surface-010 | rule | `query_match.py` deliberately duplicates private matching logic | aligned |

**10 aligned / 0 partial / 0 conflicting / 0 not_implemented / 0
insufficiently_verified.**

No conflicting or not_implemented findings to report for this topic.
See "Verification caveat" below — several of these `aligned` results
concern a `rule`/`boundary`-kind claim, and alignment there is not the
same thing as that rule being the right one.

## Per-assertion notes

**editor-surface-001** (`EditorDocument`'s complete public surface — four
attributes, seven public methods, `_shift_spans_after` excluded as
private). Reconstruction §1.1 independently lists the same constructor,
the same private helper excluded on the same grounds, and the same six
further public methods (`add_transaction`, `update_transaction`,
`delete_transaction`, `save`, `reload`, `validate_transaction`) with
matching behavioural descriptions for each. This assertion is scoped
entirely to `EditorDocument`'s own shape within `ledgerkit` itself — the
reconstruction's "zero external usage" finding is orthogonal to it and
does not bear on whether the class's structure matches what's asserted.
Aligned.

**editor-surface-002** (`__init__` parses via `parse_string`, not
`loader.load_journal`; documented V1 include limitation). Reconstruction
§1.1 quotes the same docstring near-verbatim: "V1 limitation: include
directives in the file are not processed; the file is parsed as-is with
`parse_string()`. Use `loader.load_journal()` when full include support
is required," and independently restates this as limitation #3 in §7.
Aligned. This is a `rule`-kind assertion — see the verification caveat
below: aligned confirms the code currently follows this stated rule, not
that forgoing include-processing is the right scope for v1.

**editor-surface-003** (mutation methods set `dirty=True`; span shifts
are conditional on line-count delta, not unconditional). Reconstruction
§1.1 independently describes each of `add_transaction`,
`update_transaction`, and `delete_transaction` performing exactly this
sequence (splice lines, assign/update span, shift later spans, set
`dirty=True`), and §6.1's own test-by-test account (Update: "same
posting-count update causes no shift... adding a posting... does shift")
matches the assertion's own cited counterexample
(`test_update_transaction_same_size_no_shift`) describing the same
delta-conditional behaviour. Aligned.

**editor-surface-004** (`validate_transaction` delegates solely to
`check_transaction_autobalanced`, returns a possibly-empty list, never
raises). Reconstruction §1.1 states the identical delegation and
no-raise contract, and §6.1's "Validate" paragraph independently
reports the same three-case test behaviour (balanced → `[]`, unbalanced
→ one `CheckError` with `check_name == "autobalanced"`, elided posting →
`[]`, not flagged as unbalanced) that the assertion cites. Aligned.

**editor-surface-005** (module docstring states "Intended for use by
TUI/editor frontends. Not imported by any core module."). Reconstruction
§1.1 quotes this exact sentence. This assertion only claims what the
docstring itself says — a stated intended scope, not a verified claim
that any actual TUI frontend uses the class. The reconstruction's
headline "zero real usage" finding does not contradict this: a module
can truthfully state its own intended audience while that audience, in
practice, does not yet call it. Aligned on the documented-boundary claim
as stated; this is not evidence that the intended use is actually
realised (see editor-surface-007 below for that empirical question,
which the reconstruction answers separately and consistently).

**editor-surface-006** (`ledgerkit-editor`'s `pyproject.toml` pins
`ledgerkit==1.0.0.dev1` exactly). Reconstruction §2.3 independently
quotes the identical pin: `dependencies = ["textual==8.2.5",
"ledgerkit==1.0.0.dev1"]`. Aligned. (The reconstruction separately flags,
in the same section, a textual discrepancy between this pin and a test
docstring's "ledgerkit v0.2.0" claim — no assertion in this snapshot
makes a claim about that discrepancy, so it is not a comparison finding
against any assertion; noting it here only because it sits next to this
assertion's own cited evidence.)

**editor-surface-007** (`EditorDocument` is never imported or
instantiated anywhere in the clone's code or tests; the only two
occurrences of the string are a docstring line in `ledger_io.py` and a
`# TODO` comment in `commands/__init__.py`). This is the reconstruction's
own headline finding, stated almost word-for-word: "`EditorDocument` is
never imported or instantiated anywhere in the clone's actual code or
tests... It appears only in two comments: a docstring list in
`ledger_io.py`... and a `# TODO` in `commands/__init__.py`" (§2.2, §7
item 1), citing the identical two file/line locations
(`ledger_io.py` and `commands/__init__.py`) as the assertion's own
evidence paths. Aligned — and this is the strongest form of alignment in
this topic, since both artefacts independently arrived at an exhaustive,
negative result (absence of any call site) via the same search method
(unanchored/exhaustive grep over the whole clone).

**editor-surface-008** (six `src/` files — `ledger_io.py`,
`view_filter.py`, `transaction_table.py`, `filter_popup.py`,
`journal_index.py`, `commodity_format.py` — import `ledgerkit` at
runtime via deferred, function-local imports, never `EditorDocument`;
two of the six also carry `TYPE_CHECKING`-only imports). Reconstruction
§2.2 lists the identical six files with matching per-file call-site
detail (same functions named: `_snapshot_journal`/`_apply_view_filter`/
`_merge_filtered_edits` in `view_filter.py`; `action_save` in
`transaction_table.py`; `apply_filter` in `filter_popup.py`;
`build_journal_index` in `journal_index.py`; `load_journal`/
`save_journal` in `ledger_io.py`; `extract_commodity_styles` in
`commodity_format.py`), and separately confirms the same two
`TYPE_CHECKING`-only sites (`ledger_io.py`, `commodity_format.py`).
Aligned. Worth noting: this assertion's own file history (per its
Review note) records that an earlier draft missed these six sites
entirely due to a `^`-anchored grep blind to indented/deferred imports,
and was corrected before freezing — the reconstruction, produced
independently and later, did not reproduce that error, which is itself
corroborating evidence that the corrected six-file claim is right rather
than an artefact of how the correction was made.

**editor-surface-009** (test suite imports a broader `ledgerkit` symbol
set than production `src/` code — `Query`, `Posting`/`Transaction`,
`ParseError`/`ParseWarning`/`parse_string_lenient`, `CommodityStyle`,
plus direct `load()`/`parse_string_lenient()` calls — never
`EditorDocument`). Reconstruction §2.2's "Test-side runtime imports"
paragraph and §6.2 independently list the same imports from the same
three test files (`test_query_match.py`, `test_commodity_format.py`,
`test_comprehensive_hledger.py`), including the same `ledgerkit.Query`/
`Posting`/`Transaction` top-level forms and the same `ParseError`/
`ParseWarning`/`parse_string_lenient` set. Aligned.

**editor-surface-010** (`query_match.py` deliberately avoids importing
private `ledgerkit.reports._matches_pattern`/`_posting_matches`,
duplicating the logic locally instead, per a stated policy in its own
docstring). Reconstruction §4 and §7 item 7 independently reach the same
conclusion from the same kind of evidence (reading the module's own
docstring and the duplicated implementation): "those names are
underscore-prefixed/private and 'never exported from
ledgerkit.__init__'... the editor project's own policy... is to
duplicate private-looking logic locally rather than depend on unstable
internals," and separately frames this as "an intentional, documented
fork, not a shared implementation," noting the sync obligation is manual
rather than mechanically enforced. Aligned — and notably stronger than
the assertion's own self-rating suggests: this assertion is the one
item in the snapshot marked `Evidence-support state: partially_supported`
and `Status: proposed` (not `verified`), because its own "Open
questions" field could not confirm the exact wording of what it called
an "unnamed project-level API convention... (not ledgerkit's)," since
the assertion's dispatch was barred from reading the clone's README.
The reconstruction, operating under the same README exclusion, resolves
this independently in the corroborating direction: it quotes a *named*
convention directly from the `query_match.py` docstring itself ("this
project's ledgerkit API Rule"), which is source code, not narrative
documentation — so the assertion's residual uncertainty is not, in
fact, un-researchable within the permitted evidence paths; it was simply
not run down at the time. I am not editing the frozen assertion file to
upgrade its own status (that revision, if warranted, is the lead's call
via re-running assertion-research for a new version, not mine in
comparison mode) — flagging it here as a resolvable-looking gap for the
lead's attention rather than silently treating it as settled.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification**. For
the `rule`-kind assertions above (editor-surface-002,
editor-surface-010) and the `boundary`-kind assertions
(editor-surface-005, editor-surface-007), "aligned" means only that the
independently-reconstructed as-built evidence currently matches what the
snapshot asserts — it does not establish that forgoing include
processing in v1 (editor-surface-002), that duplicating private matching
logic rather than exporting it (editor-surface-010), or that
`EditorDocument` remaining both "intended for TUI/editor frontends"
(editor-surface-005) and, as of this pinned revision, entirely unused by
the one such frontend built against it (editor-surface-007), are the
*right* design choices. Both artefacts describe current fact; neither
artefact, nor this comparison, rules on whether that fact reflects good
design. In particular, `EditorDocument`'s own behaviour (structure,
docstring claims, mutation/validation semantics — editor-surface-001
through -005) is fully aligned with the reconstruction's evidence
*independently of* the separate, also-aligned finding that no consumer
currently calls it (editor-surface-006 through -010); these are not in
tension and neither is weakened by the other.

## What was checked

- All 10 assertion `Statement`/`Evidence`/`Examples`/`Counterexamples`
  fields against the reconstruction report's §1–§7 content,
  assertion-by-assertion.
- Whether the reconstruction's headline "`EditorDocument` has zero real
  usage" finding contradicts any assertion describing `EditorDocument`'s
  own behaviour (editor-surface-001 through -005) — it does not; those
  assertions describe the class's internal shape and documented intent,
  not external uptake, and the reconstruction's own "zero usage" finding
  is itself the direct subject of, and fully corroborates,
  editor-surface-007.
- Each assertion's own in-file Review notes (editor-surface-001's method
  miscount fix, editor-surface-006's clone-`pyproject.toml`-scope
  escalation and resolution, editor-surface-008's six-file correction,
  editor-surface-009's line-number off-by-one fix) against the
  reconstruction's independent findings, to see whether the
  reconstruction reproduced any of the same errors or independently
  landed on the corrected claim — in every case the reconstruction
  matches the corrected (not the original, erroneous) version, which is
  additional corroborating signal for those corrections rather than a
  coincidence.
- Whether the reconstruction surfaced anything no assertion covers at
  all. It does, in §7: the `run_basic_checks` attribute-access-without-
  explicit-import question (item 6), the `ledgerkit==1.0.0.dev1` vs.
  `v0.2.0` docstring version-string mismatch (item 2), and the
  `split_journal_segments` date-sort block-reassociation risk (item 5).
  None of these are contradicted by any assertion — they are simply
  outside this snapshot's 10-assertion scope entirely, which is a gap in
  the knowledge base's coverage of this topic, not a comparison failure
  against any existing assertion. Recorded here per the per-topic
  comparison brief's instruction to flag such gaps explicitly.

## Escalations

None. No genuine conflicting or not_implemented classification arose
for this topic. The one item worth the lead's attention is not an
escalation of an ambiguity (per this mode's hard rule, I do not rule on
genuine ambiguities, and there is no unresolved ambiguity here) but a
pointer: editor-surface-010's own `partially_supported`/`proposed`
self-rating appears, per the reconstruction's independent evidence, to
be resolvable to `supported`/`verified` by re-reading
`query_match.py`'s docstring for its named convention — a candidate for
a future assertion-research re-pass, not a finding I am empowered or
positioned to resolve by editing the frozen snapshot myself in
comparison mode.
