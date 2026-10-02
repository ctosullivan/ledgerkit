# Clean-room conceptual understanding + documentation workflow (imported from codecompass-template, pinned revision `68bae8ec739aea413bbedac9f19078f6ab995aca`)

**Adapted for Ledgerkit's own Plan 29**
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`). This is the upstream `codecompass-template` repository's
own README for this directory, kept largely verbatim per Plan 29 §3.1
("keep ... verbatim at first; adapt only path references") — the one
cross-reference below to that template's *other*, everyday-adoption
files (`CLAUDE.md`, `decisions/`, `planning/ROADMAP.md`, etc., which
Ledgerkit never copied — Ledgerkit already had its own equivalents years
before this import: `CLAUDE.md`, `knowledge/*.md`, `ROADMAP.md`,
`CONTEXT.md`, `dev-docs/retros/`) is not applicable here and is left as
historical context from the upstream template rather than rewritten,
since Plan 29's own governing document, not this file, is what actually
drives Ledgerkit's adoption.

## What this is, and when it earns its weight

A heavier, optional workflow for the specific moment when documentation
drift or onboarding cost has become a real, recurring problem — not a
general-purpose upgrade to "do more process." It builds evidence-backed
conceptual understanding of your own project independently of whatever
narrative documentation already exists, freezes that understanding into
a versioned, hash-checked snapshot, and checks it two ways: against an
independent, code-only reconstruction of what the system actually does,
and against real usefulness (a documentation reader test, a bounded
coding-context packet test) — rather than trusting either the existing
docs or a single unverified rewrite.

Reach for this when:

- A project has grown enough history that "why was it built this way"
  routinely costs more to rediscover than it would have cost to write
  down once, verified.
- Existing documentation and the real implementation have drifted apart
  enough that neither a new contributor nor a coding agent can fully
  trust it.
- You want a mechanical, citable trail from a published claim back to
  the specific evidence it rests on — not just "someone wrote this at
  some point."

Most projects, most of the time, don't need this yet. Adopting it
reflexively just because it exists re-creates exactly the clutter this
template's own everyday path is designed to avoid.

## How to adopt it, if you decide you need it

1. Copy this whole directory into your project as its own top-level
   folder (keep the name, or rename it — nothing elsewhere references
   the path).
2. Read `conceptual-documentation-guide.md` and `mechanical-isolation.md`
   first — they're the judgment-call guides, not format specs.
3. See `worked-example.md` for one short, concrete walkthrough of the
   whole loop (research → assertion → snapshot → independent
   reconstruction → comparison → documentation draft → reconciliation)
   against a trivial, invented function, before you try it on something
   real.
4. The seven `TEMPLATE.md` files (`assertions/`, `snapshots/`,
   `coding-context-selection/`, `implementation-comparison/`,
   `propagation/`, `legacy-reconciliation/`, `documentation-verification/`)
   are format skeletons for each stage's own output — fill in what each
   stage actually needs, not all seven at once; most topics won't need
   every stage on day one.

## What this deliberately does not include

Detailed evidence, drafts, and audit records produced by actually
*running* this workflow (a filled-in assertion, a frozen snapshot, a
comparison report) belong in your own project's own working directories
once you start — this directory ships only empty format skeletons and
guidance, never worked output of someone else's project, so there is
nothing here to accidentally treat as your own project's real evidence.
