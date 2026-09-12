# 12. Migration of the current roadmap

**Gate G4 resolved 2026-09-12: executed.** `ROADMAP.md` has been rewritten
per this mapping — Milestones 0–4 retained verbatim, Milestone 5 marked
`[SUPERSEDED]`, the backlog table reclassified into Stages, and a new
Stages A–I summary table added. This document remains the authoritative
rationale for that rewrite.

## 12.1 Principle (historical — describes the process that was then followed)

`ROADMAP.md` was not rewritten by the original planning session — that was
Gate G4. This document was the **mapping** a human approved before that
rewrite happened, so the rewrite was mechanical once approved rather than
a fresh design exercise. That approval and rewrite have now both happened.

## 12.2 Completed work (Milestones 0–4) — retained as history, mapped forward

| Old milestone | Status | Disposition |
|---|---|---|
| Milestone 0 — Project Foundation | `[DONE]` | Retained as-is. Feeds Stage A directly: the project scaffold, doc structure, and dev tooling this milestone built are exactly what Stage A extends (agent roster, compat register, CodeCompass integration) rather than replaces. |
| Milestone 1 — Journal Parser | `[DONE]` | Retained as-is. Becomes the first wave of `COMPATIBLE`/`UNSUPPORTED` compat-register entries (§9.5) — no new parser work implied, just classification. |
| Milestone 2 — Core Reports | `[DONE]` | Retained. The `Query` dataclass this milestone introduced becomes Stage C's compatibility-shim starting point (`06-core-architecture.md` §6.5), not deprecated code to throw away. |
| Milestone 3 — Editor Readiness & Multi-Commodity | `[DONE]` | Retained. `EditorDocument`/`writer`/`parse_string_lenient` become the frozen v1 API surface (`06-core-architecture.md` §6.5) that Stage B/C must not break. |
| Milestone 4 — Comprehensive Format Compatibility | `[DONE]` | Retained. The explicit "Intentionally deferred" list at the bottom of this milestone (forecast, `--auto`, lot pricing, virtual postings, commodity conversion) becomes Stage E/F/G's starting backlog almost verbatim — this milestone already did the scoping work Stage E–G formalises. |

**No completed work is reclassified, reduced, or treated as not having
happened** — directly honouring the task's explicit instruction.

## 12.3 Planned/backlog work — reclassified, not discarded

| Old item | Old status | New disposition | Why |
|---|---|---|---|
| Milestone 5 — CLI Filter Flags | `[PLANNED]` | **Superseded by Stage C** (query engine), not implemented as originally scoped | Wiring raw CLI flags directly to today's `Query` dataclass, as Milestone 5 currently describes, would build exactly the "narrow ad-hoc filtering" the new goal explicitly wants replaced. Implementing it now would be rework the moment Stage C lands. The underlying user need (filter reports from the CLI) is fully preserved — it becomes `07-query-regex.md`'s `--query`-flag work, just routed through the AST instead of directly through `Query` fields. |
| Journal-comment `ReportSpec` parsing (`; report`/`; end report`) | `[BACKLOG]` | Stage D (Reporting) — natural fit once the report engine consolidation happens; not blocking Stage D's exit | Unchanged scope, just resequenced next to related reporting work instead of sitting as an orphaned backlog row |
| Full `stats` query support | `[BACKLOG]` | Stage C, immediately after the query engine lands (`stats` is exactly the kind of consumer the shared query engine is for) | Directly benefits from, and should not be built before, the query engine — building it against today's `Query` dataclass first would be the same rework risk as Milestone 5 |
| `EditorDocument` include-directive support | `[BACKLOG]` | Stage B (Core model) | Belongs with the journal/accounting model work, and is an Editor-compatibility concern (`06-core-architecture.md` §6.5) — sequenced early since it's a known gap in a component already declared "frozen API surface" |
| Account type inference | `[BACKLOG]` | Stage E (Accounting semantics) | Matches the task's own Stage E item list exactly |
| Periodic/auto postings | `[BACKLOG]` ("Out of scope for v1") | Stage G (Generated/transformative behaviour) | Unchanged scope; "out of scope for v1" becomes "scoped for Stage G", not silently promised sooner |
| `stats`: peak live memory (`psutil`) | `[BACKLOG]` | Deferred indefinitely, unchanged reasoning | Requires a third-party dependency (`psutil`) or platform syscall — stays blocked on the same "not without user approval of the dependency" condition already stated; the licence migration doesn't change this calculus |
| `stats`: peak allocated memory (`tracemalloc`) | `[BACKLOG]` | Low-priority Core-adjacent backlog, not blocking any Stage | Stdlib-only, genuinely small; sequence whenever convenient, no dependency chain forces it earlier or later |
| `stats`: per-reporting-interval output | `[BACKLOG]` | Stage D (Reporting) — depends on date-interval logic that's naturally part of report-engine consolidation | Matches the existing backlog note's own stated dependency |

## 12.4 New Stage structure (as approved, becomes the new `ROADMAP.md` — Gate G4)

Stages A–I as specified in the task, reconciled above with zero
unaccounted-for existing roadmap rows. Per-stage documents already written
in this package: Stage A → this whole planning package + §3–§5; Stage B →
`06-core-architecture.md`; Stage C → `07-query-regex.md`; Stage D →
(reporting consolidation — not separately documented in this package since
it has no open design question beyond "route through the query engine",
already stated in `06-core-architecture.md` §6.1's pipeline diagram); Stage
E/F/G → `08-accounting-semantics-roadmap.md`; Stage H → `09-compatibility-system.md`;
Stage I → §12.5 below (Core 1.0 criteria) + `11-documentation-lifecycle.md`
§11.5.

Every stage keeps the existing `ROADMAP.md` convention: `[DONE]` only on
explicit user confirmation, exit criteria stated up front, a
`dev-docs/planning/<stage>.md` plan file before implementation begins
(already `CLAUDE.md`'s convention for milestones — carried forward
unchanged, per §3's "operationalise, don't duplicate" principle).

## 12.5 Core 1.0 success criteria (the actual Definition of Done for Stage I)

Restating the task's own explicit instruction, made concrete and checkable
rather than aspirational:

Core 1.0 means Ledgerkit can, **with evidence, not assertion**:

1. Represent the target accounting model (transactions, postings,
   multi-commodity amounts, prices, costs, valuation, lots where in scope,
   generated-transaction rules) — checked against `models.py`'s actual
   type coverage.
2. Execute a stable, extensible query language — checked against
   `07-query-regex.md`'s AST having shipped and being the sole filtering
   path for every report and the CLI (no report function with its own
   bespoke filter logic).
3. Calculate the accounting semantics Stage E/F actually shipped (not
   "all of them" — whatever Stage E/F evidence showed was worth building,
   per `08-accounting-semantics-roadmap.md` §8.4).
4. Produce reports through the reusable report engine — checked: zero
   report-specific filtering code outside `reports.py` consuming
   `query/`.
5. Have a documented hledger compatibility profile — checked: every
   in-scope hledger 1.52.x feature has a `status: final` compat-register
   entry, whichever of the five `kind`s it resolved to.
6. Have documented Ledgerkit extensions/divergences — checked: every
   `EXTENDED`/`INTENTIONAL_DIVERGENCE` entry exists and is cross-linked
   from `dev-docs/hledger-compatibility.md`.
7. Expose all of the above through a stable Python API — checked:
   `dev-docs/api-spec.md` marks the full surface `[STABLE]`, and
   `ledgerkit-editor` (or an equivalent lightweight-dependency test) can
   consume it without a heavy optional dependency being pulled in.

**Explicitly not a Core 1.0 criterion:** "every hledger command/feature
exists." A feature legitimately shipping as `UNSUPPORTED` with a clear
compat-register entry satisfies criterion 5 just as well as one shipping
`COMPATIBLE` — the register's completeness is the bar, not hledger's
feature count.
