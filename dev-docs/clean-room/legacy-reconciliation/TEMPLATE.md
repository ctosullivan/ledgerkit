# Legacy reconciliation: <topic-slug>

Once a fresh documentation draft has been written from a knowledge
snapshot and **committed on its own**, reconcile it against whatever
narrative documentation already existed on this topic before the
reconstruction. Do this as a genuinely separate, later step — not folded
into the first draft (see `optional-clean-room-workflow/conceptual-documentation-guide.md`) —
so the fresh draft's own framing isn't quietly displaced by the old
narrative's framing before anyone's had a chance to compare them
deliberately.

This is **re-grounding**, not restoration: the goal isn't to preserve as
much of the old text as possible, it's to decide, claim by claim,
whether the old text still holds up against the new evidence-backed
draft.

## For each claim the legacy documentation made, classify it

- **`supported`** — the new evidence backs this; keep it, ideally now
  cited to a specific assertion.
- **`stale_or_contradicted`** — the new evidence contradicts this, or it
  describes a state that's no longer current; remove or correct it, and
  say what changed.
- **`rationale_requiring_verification`** — this claims a *reason why*
  something is true, and the reason itself hasn't been independently
  checked (only the surface fact has). Flag it for a real check before
  treating it as settled.
- **`useful_example`** — not itself an assertion, but a concrete,
  correct illustration worth keeping alongside the new draft.
- **`obsolete`** — no longer relevant to the current system at all; drop
  it, and note why here so nobody re-adds it from memory later.

## A documentation-verification finding gets fixed, not just logged

If reconciling surfaces a documentation-verification finding — the old
docs claimed something the evidence doesn't support — the fix belongs in
this same pass, in the actual published documentation. Recording it here
without also correcting the live doc leaves the false claim live for
whoever reads it next.

## Result

What changed in the published documentation as a result of this pass,
and what from the legacy version was deliberately dropped or kept, with
the classification that justified each call.
