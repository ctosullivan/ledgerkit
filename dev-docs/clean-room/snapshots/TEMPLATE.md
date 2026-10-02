# Snapshot sidecar format

A snapshot is a **frozen, versioned bundle of reviewed assertions** for
one topic — the thing your documentation and your coding-context packets
both cite, instead of each re-reading the live, still-changing knowledge
base independently. Freezing it is what makes "the doc says X, and X was
true when this was written" a checkable claim later, even after the
underlying assertions have moved on.

Write it as a TOML sidecar next to your assertion records — nested,
per-assertion evidentiary structure doesn't fit a flat `key: value` file
well, and TOML needs no extra dependency if your toolchain already reads
it (Python's stdlib `tomllib`, for instance).

```toml
snapshot_id = "<topic-slug>@v1"
created = "<timestamp>"
repository_revision_at_freeze = "<the exact commit this snapshot was cut from>"
excluded_assertions = ["<any assertion id deliberately left out, e.g. still `proposed`>"]

[assertions."<assertion-id>"]
path = "<real relative path to that assertion's own record file>"
repository_revision = "<the commit that last touched this specific file>"
content_hash = "<sha256 of the exact historical file content at that revision>"

[assertions."<assertion-id>".supporting_evidence."<evidence-id>"]
path = "..."
repository_revision = "..."
content_hash = "..."
source_ref = "<file:line or command, if this evidence cites primary source>"
doc_ref = "<if it cites a doc instead>"
test_ref = "<if it cites a test instead>"

[assertions."<assertion-id>".derivation."<derivation-id>"]
path = "..."
repository_revision = "..."
content_hash = "..."
```

Store `path` explicitly per entry — don't assume it can be inferred from
the id later. File-naming conventions drift; the snapshot shouldn't.

## Two checks, not one, and why

A snapshot gets stale or corrupted in two genuinely different ways, and
conflating them produces false alarms:

**Historical integrity** — does the snapshot still match what actually
existed at freeze time? Check this by re-fetching the exact historical
revision (`git show <repository_revision>:<path>`, or your VCS's
equivalent) and re-hashing it — never the current live file. A mismatch
here means real corruption or a rewritten history, and should fail hard.

**Current divergence** — has the live record moved on since the
snapshot was frozen? Check this by comparing the historical content
against the current live file. A difference here is *expected and
healthy* the moment a record is legitimately superseded, corrected, or
withdrawn — it's informational, not a failure. Report it (so a stale
citation gets noticed), but never let it block anything the historical-
integrity check would otherwise pass.

Getting this backwards — treating any current-vs-snapshot difference as
"corruption" — means every legitimate update to your knowledge base
breaks every snapshot that ever cited it. That defeats the point of
freezing anything.

A third thing worth naming separately from both: **evidence or source
staleness** — the assertion's own record hasn' t changed, but something
it cites has (the evidence, or the evidence's own source). That's neither
tampering nor an ordinary status update — it's a signal the assertion
itself may need re-deriving, and it's worth surfacing distinctly rather
than folding into a generic "divergence" bucket.
