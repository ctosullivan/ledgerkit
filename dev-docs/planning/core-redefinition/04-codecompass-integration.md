# 4. CodeCompass integration plan

## 4.1 Ground truth about CodeCompass today (verified, not assumed)

CodeCompass (`https://github.com/ctosullivan/codecompass`, MIT, pre-release)
is, as of this planning session:

- A tool that discovers **package-manifest dependencies** (npm/PyPI/Cargo),
  clones each vendor's upstream source, generates per-vendor `CLAUDE.md`
  digests, extracts public API surface, and builds a SQLite
  `context-graph.db` of vendors/symbols/usage — plus **mechanical
  mention-detection** linking a project's own hand-authored docs
  (`decisions/0037`–`0043`) to the vendors/Skills they mention.
- Explicitly **not** an agent orchestrator (`README.md` §1.9 there) and
  explicitly **not** an hledger black-box experiment runner — CodeCompass's
  own `planning/v1-redefinition/ledgerkit-plan.md` states this as a hard
  boundary.
- **Already planning to use Ledgerkit as its own "harder second" reference
  project** — CodeCompass's Stage D (phases 52–55) is scoped almost
  exactly around the question this document also has to answer: can a
  generalised "technical dependency" concept (executable / manual /
  spec / behavioural-contract, not just "package") represent what
  Ledgerkit actually depends on? CodeCompass's own plan explicitly treats
  this as **undecided** — Phase 55's decision could be "not justified for
  v1." This integration plan must not assume CodeCompass already has that
  capability; it has to work whether or not Stage D ships it.

This matters directly: **Ledgerkit's real technical dependencies are
almost entirely not packages.** In CodeCompass's own ranked list (from its
Ledgerkit reference-project plan): the `hledger` executable, hledger's
manuals, hledger's journal-format grammar, hledger's query semantics,
general plain-text-accounting reference material, and observed black-box
hledger behaviour — all *before* "the local Ledgerkit implementation"
itself. None of these are things `codecompass`'s current PyPI-manifest
discovery would ever find.

## 4.2 What Ledgerkit can honestly use today

Given §4.1, Ledgerkit's CodeCompass usage in the near term is narrow and
should be described that way rather than aspirationally:

- **Entry point:** CodeCompass's generated root `CLAUDE.md` routing table
  and `/discovery` command, exactly as it works for any project — useful
  for whatever real PyPI dependencies Ledgerkit does have (currently just
  `pandas`, optional). Low value today given zero mandatory deps, but
  free and non-invasive to run.
- **Spec-doc relation detection**, generalised: CodeCompass already
  mechanically links a project's own docs (`README.md`,
  `architecture/**/*.md`, `decisions/**/*.md`) to the vendors/Skills they
  mention (`decisions/0037`). CodeCompass's own precedent for treating
  *non-package* reference text as a first-class artifact is
  `decisions/0041` ("vendor upstream docs are a new doc-artifacts kind,
  root-level only"). **If** Ledgerkit vendors a local snapshot of relevant
  hledger manual sections as text (which it should do anyway for
  `hledger-researcher`'s use, §10), it becomes a candidate input to this
  *existing* mechanism — worth trying, but as an experiment
  (`context-curator` logs the result), not a designed-in dependency.
- **What does not exist yet and must not be assumed:** any edge type
  representing "hledger source implements this", "this manual section
  documents that Ledgerkit behaviour", "this executable run verified that
  compatibility claim". The task's suggested edge vocabulary
  (`DOCUMENTED_BY`, `IMPLEMENTED_UPSTREAM_BY`, `COMPATIBILITY_TARGET_FOR`,
  `IMPLEMENTED_BY`, `EXTENDED_BY`, `VERIFIED_BY`, `CONSTRAINS`,
  `EXPLAINED_BY`, `SUPERSEDES`) is a **hypothesis to validate through use**,
  matching the task's own instruction not to assume these are correct.
  Ledgerkit's compatibility register (`09-compatibility-system.md`)
  already captures every one of these relationships **in its own YAML
  schema**, independent of whether CodeCompass ever models them — the
  register is Ledgerkit's source of truth regardless of what CodeCompass
  can or can't represent. CodeCompass consuming/relating the register
  later is upside, not a dependency.

## 4.3 Agent-suggested edges

Because the edge types above don't exist in CodeCompass yet, "agent-
suggested edges" for Ledgerkit's purposes means, concretely: when
`context-curator` or `hledger-researcher` notices a relationship CodeCompass
*could* usefully represent (e.g. "this compat-register entry is
`VERIFIED_BY` this specific `hledger` invocation"), it is recorded as a
**suggestion**, not written into `context-graph.db` directly (Ledgerkit has
no write access to CodeCompass's graph schema and shouldn't invent one) —
it becomes:

1. A candidate note in the relevant compat-register entry itself
   (`dev-docs/compat-register/*.yaml` already has `evidence:` /
   `implementation:` / `tests:` fields that *are* this relationship,
   expressed in Ledgerkit's own format), and
2. If it recurs or looks generalisable, an input to a `context-curator`
   report (`05-context-curator.md`) proposing CodeCompass gain the
   capability — which CodeCompass's own review decides whether to accept,
   exactly per the task's "a suggested edge must not silently become
   authoritative" instruction and CodeCompass's own
   suggested/verified/rejected edge-state discipline
   (`decisions/0051` there).

Ledgerkit never writes directly into CodeCompass's `context-graph.db` or
`vendor.toml`. This mirrors CodeCompass's own reference-project working-
copy discipline in reverse: just as CodeCompass never mutates a reference
project's tree, Ledgerkit never mutates CodeCompass's.

## 4.4 Evidence / relationship states

Reused directly from CodeCompass's own model, since it's already exactly
the right shape and re-inventing a parallel taxonomy would be pure
duplication:

- **deterministic** — CodeCompass's mechanical mention-detection, or
  Ledgerkit's own register entries derived directly from a test result.
- **agent-suggested** — a relationship an agent noticed but hasn't been
  independently checked.
- **verified/accepted** — checked by an independent role
  (`compat-differential-tester` for compatibility claims; a CodeCompass
  reviewer for graph-edge proposals) and promoted.
- **rejected** — considered and explicitly not promoted, kept as a record
  so it isn't proposed again without new evidence.

## 4.5 Context-evaluation process

Ledgerkit reuses CodeCompass's own `context-quality-evaluation.md` report
shape wholesale (`05-context-curator.md` §2) rather than designing a new
one — the task's own required report fields (Setup / Criteria / Verdict /
Context advantage / Material gaps / "would this have misled the agent")
match CodeCompass's template near-exactly, which is itself a useful
cross-check: it means the human's ask and CodeCompass's own existing
design converged independently, and there's no reason for Ledgerkit's copy
to diverge cosmetically.

## 4.6 Coordination with CodeCompass's own Stage D

CodeCompass's Stage D (phases 52–55) is **CodeCompass's roadmap decision,
not Ledgerkit's to schedule** — Ledgerkit's `context-curator` process
(§4.2–§4.5) must work whether or not CodeCompass ever runs Stage D. When it
does run, the two sides line up by construction:

- CodeCompass's `reference-project-tester` performs genuine Ledgerkit
  development tasks using CodeCompass and files friction as CodeCompass
  candidate learnings.
- Ledgerkit's `context-curator` is the same activity from the other side —
  and its output format (`05-context-curator.md`) is deliberately written
  to be directly consumable as input to CodeCompass's own
  `planning/reference-projects/ledgerkit/<NN>-<task-slug>.md` and
  `planning/learnings/inbox.md`, so a finding never needs to be
  transcribed twice.
- Neither side adds a feature to make the other easier to evaluate — this
  is stated as a hard rule on both sides already (CodeCompass's
  `reference-project-protocol.md` §2.3; restated for Ledgerkit in
  `05-context-curator.md` §1).
