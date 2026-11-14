---
role: domain-skeptic
mode: comparison
topic: loader
dispatch_id: plan29-phase-domainskeptic-comparison-loader-20261114
dispatch_timestamp: 2026-11-14T00:00:00Z
date: 2026-11-14
inputs:
  snapshot: dev-docs/clean-room/snapshots/loader-v1.md (+ loader-v1.sidecar.json)
  assertions: dev-docs/clean-room/assertions/loader/loader-00[1-8].md (8, as named by snapshot)
  reconstruction: dev-docs/clean-room/implementation-reconstruction/loader.md
---

# Implementation Comparison: `loader` (snapshot v1 vs. independent as-built reconstruction)

Per the hard rule for this mode: an `aligned` finding below means the
snapshot's assertion and the as-built evidence currently agree — it does
**not**, by itself, mean the underlying rule/invariant is the *correct*
design choice. Neither artefact is edited to force agreement; any
divergence is recorded here only.

## Classification summary

| Assertion | Classification | One-line reason |
|---|---|---|
| loader-001 | **aligned** | Regex detection, whitespace-only-path error, bare-`include` pass-through, indented-`include` non-match all independently reproduced. |
| loader-002 | **partial** | Resolution precedence (tilde/absolute/relative) and resolved-path-based glob classification fully corroborated; the specific "glob-metacharacter-in-*containing-directory-name*" sub-claim is not independently re-tested in the reconstruction (see note below). |
| loader-003 | **partial** | Self-filter + self-include misleading-`FileNotFoundError` sub-claim is aligned; the bracketed-containing-directory `IndexError` sub-claim is not independently re-tested in the reconstruction. |
| loader-004 | **aligned** | Ancestor-stack (not global) cycle detection, mutual-cycle `ParseError`, and diamond-pattern silent duplication (same `included_files` unique-file-count semantics) independently reproduced with a structurally equivalent fixture. |
| loader-005 | **aligned** | Textual splicing (one flattened blob, one `parse_string` call) vs. `merge_journals`'s post-parse list concatenation independently confirmed as architecturally distinct. |
| loader-006 | **aligned** | `merge_journals` identity fast path, `ValueError` on empty list, first-wins `source_file`, summed `included_files`, order-preserving concatenation all independently confirmed. |
| loader-007 | **partial** | The `is_glob`-based `ParseError`/`FileNotFoundError` dichotomy is corroborated (via the self-include repro, which exercises the non-glob/`FileNotFoundError` branch, plus the existing glob/`ParseError` tests); the claimed third outcome (uncaught `IndexError` from the directory-name-bracket scenario) is not independently re-tested in the reconstruction. |
| loader-008 | **aligned** | `line_map` 1:1-per-retained-line accounting, error re-attribution with corrected file/line, and stripping of the pre-existing `" (line N)"` suffix all independently confirmed; the untested fallback branch (`line_number is None`/out of range) is an open gap shared by both artefacts, not a divergence between them. |

No assertion classifies as `conflicting`, `not_implemented`, or wholly
`insufficiently_verified`; three (loader-002/003/007) are `partial`
because one specific sub-claim in each goes beyond what the
reconstruction's permitted-evidence-paths execution actually probed.

## Detail

### loader-001 — aligned
Reconstruction §5.1 independently executes all three cases the
assertion names: `"include   "` (whitespace-only path) raises
`ParseError: include: missing file path`; a bare `"include"` line with
no trailing whitespace is not matched and passes through inert; an
indented `"    include leaf.journal"` line is never matched (`^`
anchor) and is picked up downstream as ordinary content. These match
loader-001's Statement, Examples, and Counterexamples exactly, with
independently-constructed repros (not the same fixture names), which
strengthens rather than merely repeats the original reviewer
verification.

### loader-002 — partial
**Aligned part:** reconstruction §5.2 independently confirms the
three-branch precedence (tilde-prefix → `expanduser()`; absolute →
as-is; else → relative to the *containing* file's directory), that the
glob-vs-literal test is applied to the already-joined resolved path
string (not the raw target in isolation — reconstruction's own wording,
"if the resulting string contains any of `*`, `?`, `[`... it is treated
as a glob pattern", matches "resulting string" = resolved path), `**`
recursive glob support, and deterministic sorting of glob matches.

**Not independently re-tested:** loader-002's specific counterexample —
a *containing directory's own name* containing a bracket (e.g.
`inc[1]/`) silently reclassifying an otherwise-plain raw target as a
glob and returning `[]` instead of the documented single-element list —
is not reproduced with that exact construction in the reconstruction
report. The reconstruction's closest analogous finding (§5.3) is a
*file name* (not directory name) containing a bracket, e.g.
`data[1].journal`, which is classified as a glob because the bracket is
present in the *raw target string itself* (so `is_glob` is correctly
`True` by the Statement's own definition) and fails with
`ParseError: include: no files matched '...'` — a different code path
and a different symptom than the empty-list-then-later-`IndexError`
chain loader-002/003/007 describe for the directory-name case. The two
findings share a root cause (no escaping of glob metacharacters
anywhere in a resolved path) but are not the same reproduction, so I am
not crediting the directory-name-specific sub-claim as independently
corroborated. I verified this by re-reading the reconstruction report's
§5.2/§5.3 text directly rather than taking the dispatch-note framing (that
this was already "independently reproduced") at face value — resolving
this myself from the evidence in hand, per the review discipline this
role applies in both modes, rather than deferring to that framing or
escalating it as an ambiguity.

### loader-003 — partial
**Aligned part:** reconstruction §5.4 independently confirms the
self-filter (`targets = [t for t in targets if t != file_path]`) and
that a literal self-include (`A` containing `include A`) lands in the
non-glob/no-targets branch and raises `FileNotFoundError: include: file
not found: ...` for a path that demonstrably exists — the exact
misleading-error-message behaviour loader-003's Counterexamples
describe, independently reproduced (per the dispatch note, correctly
flagged as not a fresh finding).

**Not independently re-tested:** the second, more severe counterexample
loader-003 adds (the `is_glob`-computed-from-raw-target vs.
glob-actually-taken-on-resolved-path mismatch, for a bracketed
*containing directory name*, producing an uncaught `IndexError` rather
than `FileNotFoundError`/`ParseError`) is not reproduced in the
reconstruction report with that construction — same gap as noted under
loader-002 above, carried through consistently.

### loader-004 — aligned
Reconstruction §5.4 (mutual two-file cycle → `ParseError: circular
include detected`; diamond pattern `A` → {`B`,`C`} → both → `D`) and
§5.4's cycle-via-glob sub-case are independently reproduced. Critically,
the reconstruction's diamond repro yields the same qualitative result
loader-004's Counterexamples describe: content duplication with **no**
error raised, and `included_files` reporting the count of *distinct*
files touched (3: `B`/`C`/`D` in the reconstruction's naming, matching
`Shared`/`B`/`C` = 3 in the assertion's own earlier-reviewer repro) —
not the number of times content was actually expanded. Both artefacts
independently land on "ancestor-stack, not global, cycle detection" as
the mechanism and name it as the direct cause of silent
diamond-duplication (reconstruction Limitations #3/#5 vs. assertion's
Counterexamples/Open-questions) — the dispatch note's framing of this
as already-known, not a fresh finding, holds up under my own reading.

### loader-005 — aligned
Reconstruction §1/§3/§5.6 independently confirms the textual-splicing
mechanism (`line_map`, single `parse_string` call over one concatenated
blob) and explicitly separates it from `merge_journals`'s pure
list-concatenation-over-already-parsed-objects mechanism (§2), matching
loader-005's Statement and Counterexamples without divergence.

### loader-006 — aligned
Reconstruction §2's description of `merge_journals` — identity
fast-path return (`assertIs`-confirmed), `ValueError` on empty input,
`source_file` from the first journal only, `included_files` summed, and
order-preserving concatenation of transactions/prices/all four
`declared_*` lists — matches loader-006 field-for-field.

### loader-007 — partial
**Aligned part:** the `is_glob`/`ParseError` vs.
non-`is_glob`/`FileNotFoundError` dichotomy is corroborated across two
independent angles in the reconstruction: the existing glob-no-match
case (`ParseError: ... no files matched`, §5.3/§6) and the self-include
repro (§5.4), which exercises the non-glob/empty-targets branch and
independently confirms it raises `FileNotFoundError` rather than
`ParseError`.

**Not independently re-tested:** the third-outcome claim (uncaught
`IndexError` from the directory-name-bracket mismatch between
raw-target-based and resolved-path-based glob classification) is not
reproduced in the reconstruction, for the same reason noted under
loader-002/003 — this is one underlying open point appearing in three
assertions, not three separate gaps.

### loader-008 — aligned
Reconstruction §5.6 independently confirms the full chain: `line_map`
accumulates exactly one entry per retained output line (include
directive lines consume none), a caught `ParseError` is re-raised with
the corrected originating file and local line number, and any
pre-existing `" (line N)"` suffix is stripped before re-wrapping to
avoid a doubled annotation — verified by the reconstruction via direct
inspection of `_expand_includes`'s return value on a two-file fixture,
independent of the assertion's own test-based verification. The
fallback branch (`exc.line_number is None` or out of `line_map`
bounds) remains untested by both the assertion (which notes this
explicitly under Counterexamples/Open questions) and the
reconstruction (which does not address it at all) — this is a shared
blind spot in both artefacts, not a point of disagreement between them,
so it does not pull the classification off `aligned`.

## What was and wasn't independently checked by me in this comparison

I read both artefacts' full text directly (snapshot, sidecar, all 8
assertion files, and the full reconstruction report) rather than
relying on assertion-file citations or the dispatch note's framing at
face value. Per this mode's constraints, I did not read
`ledgerkit/loader.py` or `tests/test_loader/test_loader.py` directly and
did not execute any code — classification above rests entirely on
comparing the two clean-room artefacts' own stated evidence and
reasoning against each other.

One correction to the dispatch note that prompted this run: the note
characterized the reconstruction as having "independently reproduced
the glob-metacharacter-named-directory IndexError bug already
documented in loader-002/003/007." On direct reading, the
reconstruction reproduces a related but distinct bug (a literal
bracketed *filename*, not a bracketed *containing directory name*,
misclassified as a glob — yielding a `ParseError`, not an `IndexError`).
I have classified loader-002/003/007 as `partial` rather than `aligned`
on this specific point for that reason, while crediting the aligned
portions of each (confirmed above) fully. This is not an escalation —
it is independently resolvable from the two texts in hand, and I am
recording the resolution here rather than passing along the
dispatch-note's framing unexamined.

## Escalations

None. All classification questions in this comparison were resolvable
directly from the snapshot/assertions and the reconstruction report's
own text; no genuine unresolved ambiguity between the two artefacts
remains open.
