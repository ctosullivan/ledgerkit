# Documentation verification: <what was checked>

A dedicated check of whether your **published** documentation (not the
knowledge base behind it — that's covered elsewhere) actually holds up,
run independently of whoever wrote it.

Two things worth checking separately, since they catch different
failures:

## Documentation-only Q&A

Freeze a set of real questions a reader might plausibly have. Dispatch a
fresh reader — someone or something with no other context, no access to
the underlying knowledge base or source code, only the published
documentation itself — to answer them using only what's published.
Independently check those answers against the real system (source,
tests, actual behavior), not against the documentation that produced
them — checking the doc against itself just confirms it's internally
consistent, not that it's true.

Any answer that turns out to be wrong or unsupported is a doc defect:
fix the actual published documentation, don't just log the finding.

## Coding-context advantage

Separately, if this documentation is meant to help with real
implementation work (not just to explain the system to a reader), check
whether it actually helps with a real coding task — see
`optional-clean-room-workflow/coding-context-selection/TEMPLATE.md` for how that
packet is assembled and independently rated.

## Record

- Questions asked / task attempted:
- Answers or attempt produced, from the frozen documentation alone:
- Independent check against the real system:
- Findings, and which of them were fixed in the actual published
  documentation (not just noted here):
