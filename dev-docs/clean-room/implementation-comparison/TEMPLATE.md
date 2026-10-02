# Implementation comparison: <topic-slug>

Compares a frozen knowledge snapshot against an independent,
implementation-only reconstruction of the same topic (see
`optional-clean-room-workflow/mechanical-isolation.md` for how that reconstruction should have
been produced — model-blind, no access to this snapshot at the time it
was written). This comparison happens strictly *after* both sides exist,
performed by whoever (or whatever) did neither the original research nor
the reconstruction.

## Inputs

- Snapshot: `<topic-slug>@v<N>`
- As-built reconstruction report: `<path, and when/how it was produced>`

## Per-assertion classification

For each assertion in the snapshot, one of:

- **`aligned`** — the reconstruction's own findings support this
  assertion as currently true of the implementation.
- **`partial`** — some part holds, some doesn't; say which.
- **`conflicting`** — the reconstruction directly contradicts this
  assertion; say how.
- **`not_implemented`** — the assertion describes something the
  reconstruction found no evidence of in the actual code.
- **`insufficiently_verified`** — the reconstruction didn't cover enough
  ground to classify this one either way; this is a real, useful
  finding, not a placeholder to avoid picking a harder category.

Do this in both directions where it matters: also flag anything the
reconstruction found that no assertion covers at all — that's a gap in
the knowledge base, not a comparison failure.

## The one rule that matters more than the classification scheme

**An `aligned` finding never, by itself, promotes an assertion's own
status to `verified`.** Alignment tells you the current implementation
matches what was claimed. It does not independently establish that the
claim itself is correct — that needs a separate, assertion-specific
check against primary evidence. This distinction matters most for a
`rule`, an `invariant`, or a `proposed_policy`: code that currently
behaves as described proves the code's current behavior, not that the
rule is the right one. Treat a directly `observed_behaviour` assertion
differently only in that alignment there is closer to (but still not
identical to) the check itself — even there, write the assertion-
specific verification separately rather than inferring it from this
comparison.

## Findings requiring action

Anything `conflicting` or `not_implemented` needs a decision: is the
assertion wrong (fix the knowledge base), is the implementation wrong
(a real bug, file it as such), or is this a legitimate divergence the
documentation should describe honestly rather than paper over? Record
which, and why.
