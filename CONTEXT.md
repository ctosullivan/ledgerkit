# Context — 2026-05-09

## Current Task
Milestone 3 released as v0.5.0 — committed.

## Where We Are
All work committed. Next milestone scope not yet defined.
Next: user specifies Milestone 4 scope when ready.

## Decisions In Flight
None.

## Files Currently Relevant
None — awaiting next task.

## Blockers / Open Questions
None.

## What NOT To Revisit
- `Transaction.comment` kept as `str = ""` alongside `inline_comment: str | None` — backward compat.
- `journal_to_text` omits directives — documented decision.
- `EditorDocument` does not use `load_journal` — correct for single-file editor use case.
- All new metadata fields use `compare=False` — correct, deliberate.

## Recent Git State
```
(see git log)
```
