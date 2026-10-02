# Coding-context packet: <bounded task name>

A packet assembled from a frozen knowledge snapshot for one **specific,
bounded coding task** — not a topic overview, not "everything about this
subsystem." The test for whether this packet is well-scoped: could
someone unfamiliar with the codebase pick up the actual task using only
what's in here, without it being padded with assertions the task doesn't
touch?

## The task

State the concrete task this packet supports — a real change, a real
question with a code-level answer, a real bug. Bound it enough that
"what's relevant" has a clear edge.

## Snapshot cited

`<topic-slug>@v<N>` — the exact frozen version this packet was assembled
from. If the live knowledge base has moved past this version since, that
divergence is expected and informational (see
`optional-clean-room-workflow/snapshots/TEMPLATE.md`) — it doesn't invalidate this
packet, but note the version explicitly so staleness is checkable later.

## Assertions included, and why each one

List each assertion id pulled into this packet, with one line on why the
task actually needs it. An assertion that doesn't earn its place here
should be left out, even if it's topically related — a packet's value
comes from precision, not coverage.

## What was deliberately left out

Anything adjacent that a less careful assembly might have included, and
why it isn't needed for *this* task specifically. This is often the most
useful section for whoever reviews the packet's quality later.

## Independent assessment

This packet should be assessed the same way documentation-only context
is: an evaluator who inspects the real target code directly (never by
running your own tooling against itself) rates whether the packet gave a
genuine advantage over having no packet at all — LOW / MODERATE / HIGH —
and whether anything material was missing. Record that verdict here once
it exists; a packet that hasn't been independently checked isn't yet a
finished deliverable, just a draft.
