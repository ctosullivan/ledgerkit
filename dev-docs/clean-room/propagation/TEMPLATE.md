# Propagation demonstration: <what changed>

Demonstrates that a change to a real **source** actually propagates all
the way through your knowledge base to every dependent artifact — not
just that an assertion, edited directly, updates its own file. Editing an
assertion by hand and confirming the checker notices doesn't exercise
discovery: it skips the step where a source change gets *found* in the
first place.

Do this with a **disposable fixture**, never in real canonical knowledge
or published documentation:

1. Build a small fixture outside your real project tree: a fake source
   file, an Evidence record that cites it (`source_ref`), a couple of
   assertions derived from that evidence, and — if your workflow supports
   transitive dependency tracking — a small dependency chain between
   assertions, ideally including a genuine **cycle** (assertion A depends
   on B depends on A) so you can confirm your traversal terminates rather
   than looping forever.
2. Change the fixture's **source file** — not the assertion directly.
3. Walk the real chain: source → the evidence citing it → the
   assertion(s) that evidence supports → every transitive dependent of
   those assertions (cycle-safe) → any frozen snapshot citing any of
   them → both a documentation page and a coding-context packet that
   cite that snapshot.
4. Confirm each hop actually surfaces the change — a stale-evidence flag,
   a divergence report, a re-derivation prompt, whatever your workflow's
   real mechanism is. If a hop silently doesn't propagate, that's the
   finding.
5. Record what happened at each hop in this file.
6. **Delete the fixture.** Nothing from this demonstration belongs in
   real canonical knowledge or real published output once you're done —
   the report in this file is what's kept, not the fixture itself.

## Fixture description

What you built, and where (outside the real tree).

## Change made

The exact change to the fixture's source file.

## Propagation trace

Hop by hop: what was supposed to notice the change, and what actually
happened.

## Cycle handling

If your fixture included a dependency cycle: confirm the traversal
visited each node once and terminated, rather than looping.

## Fixture deleted

Confirm here, once done.
