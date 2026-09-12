# Changelog — Stage B: Core Model

Archived on: 2026-09-13
GitHub commits: (uncommitted at time of archiving)

---

### [Stage B Phase 1 — Editor-compatibility inventory] — 2026-09-13

Full detail: [dev-docs/planning/core-redefinition/15-editor-compat-inventory.md](../planning/core-redefinition/15-editor-compat-inventory.md)

**Human:** directed implementing "the next phase"; when asked to confirm
Stage B's scope (not yet approved for implementation per `ROADMAP.md`'s
process and `14-human-decision-gates.md` G5), chose the Editor-compat
inventory as this phase's scope, then supplied the `ledgerkit-editor` git
URL when asked.

**Claude:** cloned `https://github.com/ctosullivan/ledgerkit-editor`
(read-only, scratch directory) and independently verified its actual
`import ledgerkit` usage against the real source, correcting three
inaccuracies in `14-human-decision-gates.md` G8's earlier inventory:
`EditorDocument` is not actually used anywhere in its shipped code (only a
stale docstring mention); `ledgerkit.reports`'s matching helpers are
deliberately *not* imported (duplicated locally instead, to avoid depending
on private members); `ledgerkit.models` types are `TYPE_CHECKING`-only in
shipped code, not a runtime dependency there. Confirmed accurate:
`Query` (used with only 4 constructor kwargs, never passed to a `ledgerkit`
report function), `parse_string_lenient`, `checks.run_basic_checks`,
`commodity_style.CommodityStyle`, `parser.{ParseError,ParseWarning}`,
`load`, `writer.{transaction_to_text,journal_to_text}`. Updated
`06-core-architecture.md` §6.5's frozen-API-surface list and
`14-human-decision-gates.md` G8 accordingly. `ROADMAP.md`'s Stage B row
moved to `[IN PROGRESS]`. Retro: `dev-docs/retros/STAGE-B-PHASE-1.md`. No
`ledgerkit/`/`tests/` code touched.

---

### [Stage B Phase 2 — Journal/accounting model review] — 2026-09-13

Full detail: [dev-docs/planning/core-redefinition/16-model-review.md](../planning/core-redefinition/16-model-review.md)

**Human:** directed scoping Stage B's next phase; chose the
journal/accounting model review as this phase's scope.

**Claude:** independently reviewed whether `models.py` needs structural
change to later carry Stage E/F's `Cost`/`Lot`/`PriceGraph`/valuation
types, per `06-core-architecture.md` §6.3's claim that it doesn't.
Confirmed for costs, lots, virtual postings, and valuation (all achievable
as pure additive dataclass fields). Found one real exception: Stage E's
planned account-type semantics must store the `account` directive's
`type:` tag in a **new** field, never by changing
`Journal.declared_accounts`'s `list[str]` shape — `ledgerkit-editor`'s
`journal_index.py` depends on that exact shape (confirmed in Stage B
Phase 1's inventory). Also recorded a second guardrail: new
`Posting`/`Transaction` fields must make a deliberate `compare=` choice,
matching the existing `source_line`/`raw_text`/`inline_comment` precedent.
Threaded both guardrails through `06-core-architecture.md`,
`08-accounting-semantics-roadmap.md`, `dev-docs/architecture.md`'s Design
Principles, and a new `knowledge/DECISIONS.md` entry. `ROADMAP.md`'s Stage
B row updated. Retro: `dev-docs/retros/STAGE-B-PHASE-2.md`. No
`ledgerkit/`/`tests/` code touched.

---

### Stage B closed — user-confirmed 2026-09-13

Both phases were read-only investigation/review; no `ledgerkit/` or
`tests/` code changed across all of Stage B. Retro bulk-review (per
`dev-docs/retros/README.md`'s lifecycle, checked at Stage completion):
both phase retros (`dev-docs/retros/STAGE-B-PHASE-{1,2}.md`) report no
process friction and no agent-roster gap — neither phase needed a
specialist agent dispatch, and that was the right call rather than a
missed opportunity. No process change indicated. Stage C (query system)
is next; not yet scoped.
