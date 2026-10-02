# Writing conceptual documentation from a knowledge snapshot

This guide is for the step where you turn a frozen snapshot of
reviewed assertions (`optional-clean-room-workflow/snapshots/TEMPLATE.md`) into
documentation a person will actually read. It's not a format spec — it's
the judgment calls that matter when you make that jump.

## Understanding lives in the documentation directly

Don't build a separate "reviewed understanding" artifact that sits
between your knowledge base and your published docs, waiting on a human
sign-off before the docs can be written. The snapshot itself — already
evidence-backed, already reviewed — *is* the reviewed understanding.
Write the documentation straight from it. A staging artifact whose only
job is to be approved before the real writing starts is a step that adds
delay without adding rigor the snapshot didn't already provide.

## Pick an architecture from the material, not a template

Don't force every topic into the same fixed doc skeleton. Read what the
snapshot actually contains and let its own shape suggest the
documentation's shape — a topic that's mostly definitions and
relationships wants a different structure than one that's mostly rules
and invariants with edge cases. A fresh, isolated pass at this (no
memory of how the last topic was organized) tends to produce a more
honest fit than reusing whatever structure worked last time.

## Draft before reconciling

Write the complete first version from the snapshot alone, and commit
it, before touching whatever legacy documentation already existed on
this topic. Reconciliation is a separate, deliberate step (see
`optional-clean-room-workflow/legacy-reconciliation/TEMPLATE.md`) — folding it into
the first draft risks quietly re-importing an old framing the evidence
no longer supports, just because it was sitting there already.

## Every claim in the doc traces to something citable

A sentence in the published doc that doesn't trace back to a specific
assertion (and that assertion to specific evidence) is either an
unsupported claim that shouldn't be there, or evidence that didn't make
it into the snapshot and should have. If you notice one while writing,
that's a signal to go back and fix the snapshot's own coverage — not to
write around it with vaguer language.

## Cite the snapshot, not the live knowledge base

When a piece of documentation needs to point back to where a claim comes
from, cite the frozen snapshot version (`<topic-slug>@v<N>#<assertion-id>`),
not "the knowledge base" generically. That's what makes "this doc was
accurate as of what it cites" a claim you can actually check later, even
after the live assertions have moved on.

## Alignment with the real implementation isn't automatic verification

If your workflow includes an independent, code-only reconstruction of
what the system actually does (compared afterward against the snapshot),
remember: agreement between the two means the *current* implementation
matches what you asserted — it does not mean the assertion itself was
correct, especially for a rule or an invariant rather than a directly
observable behavior. Don't let a documentation page quietly upgrade its
own confidence language ("this is guaranteed") off the back of an
alignment finding that only checked "this is what currently happens."
