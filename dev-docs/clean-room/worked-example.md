# Worked example: one topic through the whole loop

A short, invented, deliberately trivial walkthrough — a toy
`next_id(items)` function that computes `max(id for id in items) + 1` (or
`1` if `items` is empty) — to show the shape of each stage's real output,
not the full rigor a real topic deserves. Use this to pattern-match
against, not to copy verbatim.

## 1. Assertion (`assertions/TEMPLATE.md`'s shape, filled in)

```
Statement: next_id computes max(current ids) + 1, or 1 if empty — a
function of the CURRENTLY PRESENT ids only, with no memory of ids used
in the past. Consequence: deleting the item holding the current maximum
id, then calling next_id again, reuses that id — even while other,
older items are still present.

Evidence: direct execution against the real function, three sequences
(delete a non-max id; delete the current-max id; empty the list
entirely).

Status: verified.
```

## 2. Snapshot (`snapshots/TEMPLATE.md`'s shape, filled in)

A frozen, versioned citation of the assertion above plus its evidence,
each entry recording the exact file path, commit/revision, and a content
hash — so the snapshot can later be checked against tampering (did the
cited file's content at that revision really say this) versus legitimate
drift (has the live file moved on since). `next-id-behavior@v1`.

## 3. Independent reconstruction (no access to the assertion above)

A fresh pass, given only the real source and tests — never the
assertion or snapshot — reconstructs what `next_id` actually does,
purely from running it and reading it. If it has no access to steps 1-2
at all, its own account of the function's behavior is an independent
check, not a restatement.

## 4. Comparison

Does the independent reconstruction's account agree with what the
snapshot asserts? Here: yes — both land on "one more than the current
max, or 1." Agreement confirms the *current implementation* matches the
assertion; it does not, by itself, upgrade the assertion's own
confidence as a general rule (see `mechanical-isolation.md` and
`conceptual-documentation-guide.md`'s own point about this).

## 5. Documentation draft (written from the snapshot, before looking at any existing docs on this topic)

> `next_id` is not a stable, never-reused identifier. It computes one
> more than the current maximum id present in the list. Deleting the
> item that holds the current maximum id, then adding a new one, reuses
> that id — this isn't limited to the case where the list becomes
> completely empty.

## 6. Reconciliation (now compare against whatever existing docs already said)

If an existing doc claimed "ids are never reused" — this is where that
gets corrected, with the old claim's own text preserved and a dated
correction added, not silently rewritten.

## What this example deliberately skips

Real adversarial review, a genuine isolation check (was the
reconstruction pass in step 3 actually unable to see steps 1-2, or just
instructed not to look), and the coding-context-packet usefulness check
— all real, necessary parts of doing this for real, left out here only
because this example's job is to show the *shape* of the six stages in
one page, not to be a complete specification.
