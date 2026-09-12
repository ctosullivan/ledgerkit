# 11. Documentation lifecycle

## 11.1 Ledgerkit's current state is already healthy — extend, don't replace

Unlike CodeCompass's own starting point (`architecture/overview.md` at
1,954 lines with visible accretion — CodeCompass's own documented reason
for building this lifecycle), Ledgerkit's current docs are small and
current: `dev-docs/architecture.md` (156 lines), `dev-docs/api-spec.md`
(comprehensive but tightly scoped), `dev-docs/hledger-compatibility.md`
(the single largest doc, already well-organised into In/Out-of-scope
tables). The existing same-commit doc-sync rule (`CLAUDE.md`) has
evidently worked — there is no current accretion problem to fix. This
section's job is to **add the milestone-renewal half that doesn't exist
yet**, not to fix an incremental-maintenance half that's already working.

## 11.2 Three documentation roles (adopted from CodeCompass unchanged — this distinction is domain-independent)

1. **Current truth** — `README.md`, `docs/`, `dev-docs/{architecture,
   api-spec,hledger-compatibility}.md`. Describes Ledgerkit as it exists
   now. May be rewritten, consolidated, or have material deleted.
2. **Decision history** — `knowledge/DECISIONS.md` (+ `ANTIPATTERNS.md`,
   `EDGE_CASES.md`, `DOMAIN_RULES.md`). Already append-only in practice
   (dated entries, never rewritten) — formalise this as an explicit rule
   rather than an implicit convention, since Stage A's larger agent roster
   makes it more likely someone edits a historical entry by accident.
   **Recommendation (not executed here):** consider migrating to numbered,
   one-file-per-decision ADRs (`knowledge/decisions/NNNN-slug.md`) once
   volume grows enough that a single growing file becomes unwieldy —
   CodeCompass's own `decisions/` directory is the precedent, but
   Ledgerkit's current `DECISIONS.md` size doesn't yet justify the
   migration cost. Revisit at Stage D or when the file exceeds roughly the
   same 300–500-line threshold `CLAUDE.md` already applies to source
   modules.
3. **Historical milestone state** — git tags/releases (`v1.0.0` already
   exists) + `dev-docs/changelog/MILESTONE-N.md` archives (already a
   working pattern — Milestones 0–4 are archived this way). No change
   needed; the new Stage-based roadmap continues this exact pattern
   (`12-roadmap-migration.md`).

## 11.3 Incremental maintenance (unchanged mechanism, now agent-operationalised)

`docs-maintainer` (`03-agent-led-development.md`) is the agent form of
`CLAUDE.md`'s existing same-response doc-sync rule and
`dev-docs/SYNC.md`'s existing audit checklist. `docs-reconstructor` adds
the missing independent counterweight: `docs-maintainer` both edits and
would otherwise self-certify — every phase gets a read-only drift audit
from `docs-reconstructor` against the phase's actual diff (not
`docs-maintainer`'s summary of it), verdict `NO DRIFT` / `DRIFT — n
findings`, looped back until clean.

## 11.4 Blank-slate reconstruction (the new half)

At **Core 1.0** (Stage I) and at any Stage boundary the lead judges
significant (e.g. completing Stage F's investment-accounting work, given
how much new conceptual surface that adds), `docs-reconstructor`:

- Approaches Ledgerkit as though `README.md`/`docs/`/`dev-docs/architecture.md`
  did not exist.
- Derives documentation from authoritative reality only: `ledgerkit/`
  source, `tests/`, the CLI's actual `--help` output, the compatibility
  register, `knowledge/*.md`, current `ROADMAP.md`.
- Output: a shadow proposal at
  `dev-docs/planning/blank-slate/<milestone>/` — proposed `README.md`,
  proposed `docs/`, proposed `dev-docs/architecture.md`, and an explicit
  "concepts the current docs spend words on that the current system no
  longer justifies" list.
- **Does not overwrite anything itself.**

Then a **reconciliation** step (lead + `docs-maintainer`): for each current
doc and each proposed doc, a recorded decision — retain / rewrite /
consolidate / split / replace / remove / preserve only in historical state
— with a one-line rationale, at
`dev-docs/planning/blank-slate/<milestone>/reconciliation.md`.

## 11.5 Milestone documentation closeout

Extends Ledgerkit's existing milestone-archiving practice
(`CLAUDE.md`'s "Milestone archiving" section, already working for
Milestones 0–4) with the blank-slate step:

1. Deterministic doc checks pass (extend `dev-docs/SYNC.md`'s existing
   checklist mechanically — every public function documented, every
   compat-register `final` entry cross-linked, internal links resolve).
2. Blank-slate reconstruction done (§11.4).
3. Reconciliation done, actioned.
4. Obsolete current documentation deleted, not annotated with "note: since
   Stage N this also..." caveats — if a paragraph is wrong, the paragraph
   is fixed, not appended to (directly restating CodeCompass's own hard-won
   rule for exactly this failure mode).
5. `knowledge/` entries reviewed — any decision made during the milestone
   lacking a `knowledge/DECISIONS.md` entry gets one; superseded entries
   get a short addendum pointing at what replaced them (never rewritten).
6. Existing milestone-archive mechanism (`dev-docs/changelog/MILESTONE-N.md`)
   continues unchanged, extended with a compatibility-register summary
   (how many entries in each of the five states, at milestone close).
7. Git tag preserving complete historical state (already standard
   practice — `v1.0.0` exists).

## 11.6 Learning lifecycle

Reuses `knowledge/` as the promotion target rather than introducing a
parallel `planning/learnings/` tree (§3.2's `roadmap-context-curator`
rationale) — Ledgerkit's four `knowledge/*.md` files already **are** its
promoted-knowledge store, unlike CodeCompass, which didn't have an
equivalent before building `planning/learnings/`.

```
observation                 an agent notices something during a phase
    ↓
candidate                   roadmap-context-curator does a lightweight
                             accept — specific, not necessarily yet true
    ↓
evidence / recurrence       tracked informally in CONTEXT.md's
                             "Decisions In Flight" section (already exists,
                             already the right shape) until it either
                             recurs or gets resolved
    ↓
promote / retain / discard  → the artifact that owns it:
```

| Classification | Promoted to |
|---|---|
| behavioural rule | a regression test |
| compatibility behaviour | a compat-register entry + test |
| extension | a compat-register entry (`kind: extension`) + test |
| architecture rationale | `knowledge/DECISIONS.md` |
| current architecture | `dev-docs/architecture.md` |
| recurring project-wide agent rule | a proposed `CLAUDE.md` change — **requires explicit user approval**, mirroring CodeCompass's own §0 protection of its `CLAUDE.md`; Ledgerkit's current `CLAUDE.md` doesn't yet state this meta-rule about itself — recommend adding it as part of Stage A (a one-line addition, analogous to CodeCompass's own) |
| scoped/repeatable workflow | a `.claude/skill` or agent-brief tweak |
| future work | a `ROADMAP.md` row |
| unresolved current work | `CONTEXT.md` |
| user-visible shipped change | a `CHANGELOG.md` entry |
| unsupported/irrelevant | discarded, with a one-line reason (not silently dropped — a discard is itself a small recorded decision) |

`roadmap-context-curator` owns this triage (`03-agent-led-development.md`
§3.2), same as it owns `ROADMAP.md`/`CONTEXT.md` reconciliation generally —
no separate `knowledge-curator` agent is created for this at Ledgerkit's
current scale (explicit deviation from CodeCompass, justified in
`03-agent-led-development.md` §3.1).
