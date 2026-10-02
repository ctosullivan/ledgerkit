# Getting real independence between research and implementation review

Some workflows depend on one pass of work genuinely not having seen
another — an independent understanding of what a system *should* do,
checked later against an independent reconstruction of what it *actually*
does, without either one having quietly absorbed the other's framing
first. That independence has to be real, not assumed. This is what to
actually check, and how to report honestly when you can't get all of it.

## Test the isolation you're relying on — don't assume it from a tool's own description

Whatever mechanism you're using to run an "isolated" pass — a fresh
agent context, a separate sandboxed environment, a different machine —
its documentation telling you it's isolated is not the same as it
*being* isolated in your actual environment. Run a real preflight probe
before trusting it with anything sensitive:

1. **Filesystem** — can the isolated pass read a file you intended to
   exclude, at its real path?
2. **Search** — can it find that excluded content some other way (a
   filename search, a directory listing) even without being told where
   to look?
3. **Command execution** — does it have a shell, and if so, what can
   that shell reach?
4. **Network** — can it reach the outside world at all? If your project
   has a public mirror (a public GitHub repo, a public package registry
   entry), assume anything excluded locally may still be reachable
   there over the network, and check it directly rather than assuming
   the local exclusion is the whole story.
5. **Environment identity** — is this actually a different machine or
   filesystem, or a worktree/subdirectory of the same one? Check
   `hostname`, `pwd`, and whether the excluded content's real absolute
   path exists from inside the isolated pass.

Run the actual probe, capture the actual transcript, and base your label
on what happened — not on what the tool's own description says should
happen. A probe that *fails* (the isolated pass reaches something it
shouldn't) is a genuinely useful, honest result — it tells you which
tier of isolation you actually have available this time, in this
environment.

## Report the tier you actually achieved, not the tier you were aiming for

Two honest labels, not one aspirational one:

- **`verified`** — every probe you ran actually failed to reach excluded
  content, using the strongest isolation mechanism genuinely available
  to you (a real separate environment, not just a fresh context in the
  same one).
- **`best-effort`** — the isolation is a matter of scoped inputs and
  instructed compliance (a curated export, an instruction not to look
  elsewhere) rather than something mechanically enforced; the pass
  technically *could* reach more than it was given, and you're relying
  on it not doing so.

Never round `best-effort` up to `verified` because the pass behaved
correctly in a given run. Correct behavior under `best-effort` isolation
tells you the pass complied — it doesn't tell you it *couldn't* have done
otherwise, which is the actual distinction between the two labels.

## Keep "did the workflow get built" separate from "was isolation actually achieved"

These are two different questions with two different, independently
reportable answers. A workflow can be fully built, fully functional, and
genuinely useful, while its isolation claim honestly remains
`best-effort` rather than `verified` — that's not a failure of the
workflow, it's an accurate account of what your actual environment could
support. Don't let a single overall "done" verdict quietly launder a
known, disclosed limitation on one axis into an unqualified success on
both.
