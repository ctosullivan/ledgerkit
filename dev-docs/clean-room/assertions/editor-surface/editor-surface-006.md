<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a6 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | review-dispatch: edsurf-review-1 | date: 2026-10-03 -->
# Assertion: editor-surface-006

## Statement
The `ledgerkit-editor` project (cloned from https://github.com/ctosullivan/ledgerkit-editor) pins its `ledgerkit` dependency to an exact pre-release version, `"ledgerkit==1.0.0.dev1"`, in its `pyproject.toml`.

## Kind
relationship

## Basis
directly_stated

## Evidence
From the ledgerkit-editor clone: the dependency pin is a literal string in the dependencies list of pyproject.toml.

Evidence-paths: [/tmp/ledgerkit-editor-research-clone-2/pyproject.toml:16]

## Justification
Exact-pin dependency strings are unambiguous evidence of the declared coupling version between the two projects.

## Examples
Line 16 reads exactly: `"ledgerkit==1.0.0.dev1",`

## Counterexamples
None.

## Depends on
None.

## Open questions
Whether this pin matches what's actually installed in the editor's test/dev environment was not checked (no test suite was run, per task constraints).

RESOLVED BY LEAD (2026-10-03), per domain-skeptic's escalation above: this
assertion's citation to the ledgerkit-editor clone's own `pyproject.toml:16`
is in scope. The review dispatch's instruction to restrict the clone to
"source and test files only, never its README/docs" was aimed at excluding
that project's *narrative* documentation, not its build/config files — the
governing clean-room plan's own evidence rule explicitly lists "package/
build/configuration files" as legitimate primary evidence, for an inspected
external repository exactly as much as for Ledgerkit's own. Reading an
external dependency's own pin file to establish the coupling version
between two projects is squarely that category, not docs-adjacent prose.
The imprecision was in how narrowly the dispatch instruction was worded,
not a boundary violation by either dispatch. Restored to its original state
below.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

## Review note
REVIEW (domain-skeptic, 2026-10-03): escalated whether `pyproject.toml` was
in scope for the ledgerkit-editor clone, since it's neither a `.py` source
nor test file. RESOLVED BY LEAD: yes, in scope — build/config files are
primary evidence for an inspected external repo, same as for Ledgerkit's
own; the instruction's "source and test files only" wording was meant to
exclude narrative docs, not config. No re-derivation needed; the original
citation and claim stand.
