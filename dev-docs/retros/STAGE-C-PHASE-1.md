# Stage C Phase 1 retro — Query semantics research + standalone query engine

- **Date:** 2026-09-13
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** `hledger-researcher` (semantics brief)

## Where we are

Stage B (Core model) closed with two read-only phases — no `ledgerkit/`
code had changed since Milestone 4. This is Stage C's first phase, and
the first phase of this whole Core-redefinition arc to actually add new
`ledgerkit/` source. The user gave a standing "proceed with roadmap
until a natural stopping point, recommended options" directive; per
`ROADMAP.md`'s own process this still required scoping Stage C's first
phase explicitly rather than starting Stage C's full scope at once —
resolved by treating "research the initial term set, then build it
standalone" as the recommended, lowest-risk first slice. After this
phase: `ledgerkit/query/` exists (AST, regex-dialect validation, parser,
evaluator), fully tested, with 7 new compat-register entries — but not
yet reachable from any CLI flag, `reports.py`, or the existing `Query`
dataclass. That wiring is explicitly the next phase's concern, not this
one's.

## Goal

Implement Stage C's initial query-term set (`acct:`/desc:`/date:`(simple)/
`depth:`/`status:`/`not:`) as a standalone `ledgerkit/query/` subpackage,
grounded in a verified semantics brief rather than assumption, per
`07-query-regex.md`'s architecture plan.

## Scope delivered vs planned

Delivered: the semantics brief (`17-query-semantics-brief.md`), the full
`ledgerkit/query/` subpackage (`ast.py`, `regex.py`, `parser.py`,
`eval.py`), 81 new tests (656 total, all passing), `dev-docs/api-spec.md`'s
new section (approved explicitly — see below), `hledger-compatibility.md`'s
new Query Language section, and 7 compat-register entries.

Deliberately not delivered this phase, matching the brief's own scope
boundary and `07-query-regex.md`'s phasing note: `tag:`, `cur:`, hledger's
smart/period date expressions, and the `PythonRegex` extension syntax
(§7.4's dialect-marker question) are all out of scope — not started, not
half-built. Also deliberately not delivered: wiring into `reports.py`/
`cli.py`/`Query` — this phase is standalone by design, per the same
"verify before wiring" caution Stage B's phases used.

One scope decision made without re-asking, recorded here rather than
silently: the `date:` range separator support was narrowed to `-`, `..`,
and `' to '` with a **mandatory 4-digit year** (no year-inference from
journal context, since query-parse time has no such context) — the brief
flagged the open-ended-form and separator question as needing "the
lead's explicit decision," and this is that decision, not a deferral.

## What was achieved

A working, independently-grounded query engine slice: `parse("not:acct:a
not:acct:b")` correctly produces `And((Not(Acct("a")), Not(Acct("b"))))`
— the exact footgun the brief flagged, gotten right on the first
implementation rather than discovered later as a bug. `HledgerRegex`
validation rejects every construct the brief's construct-by-construct
table said to exclude (backreferences, `(?...)` forms, GNU `\<`/`\>`,
Perl shorthand classes, POSIX named classes, lazy quantifiers) with a
specific, named reason each. Date-span parsing correctly implements
exclusive-end-date semantics, which genuinely differs from the existing
`Query.date_to` — both documented side by side in `knowledge/
DOMAIN_RULES.md` so the divergence isn't accidentally "fixed" later by
someone assuming they should match.

## What worked

- **Dispatching `hledger-researcher` before writing any parser code.**
  The brief surfaced at least three things that would have been easy to
  get wrong by guessing: the exclusive-end-date rule, the
  negated-same-prefix-is-AND-not-OR rule, and the precise regex-construct
  exclusion list (with the specific insight that Python silently
  misinterprets `\<`/`\>` and `[[:alpha:]]` rather than erroring, which is
  the dangerous case worth excluding even where hledger's own behaviour
  wasn't fully confirmed).
- **A tight, reusable tokenizer bug feedback loop.** Writing real tests
  before declaring the implementation done caught two tokenizer bugs
  immediately (`desc:"quoted"` not respecting the quote, and one
  duplicate/confusing test) — both fixed in the same response, not left
  for a later phase to discover.
- **Pausing for explicit sign-off on the `api-spec.md` change**, per
  `CLAUDE.md`'s Unauthorised Change Rule, even under a broad "proceed
  with recommended options" mandate — the standing autonomy directive
  was about *which roadmap option to pursue*, not a blanket override of a
  file-specific protection rule stated in the same document.

## What didn't work

The initial tokenizer design (pure quote-vs-bare alternation) didn't
account for a prefix immediately followed by a quote (`desc:"whole
foods"`) — caught by tests, not by design review, meaning the first
implementation attempt was wrong on a case the brief's own examples
literally used. Not a large cost (one redesign, still same response),
but worth naming: the tokenizer needed the same "trace through the actual
hard case first" discipline the AST/eval logic got from the start.

## Lessons learnt

A regex-based tokenizer's "obviously correct" design deserves the same
by-hand trace-through against the *specific* example strings the source
material uses (here, `desc:"whole foods"`) before trusting it, not just
against the simple unquoted case. Separately: when a semantics brief
flags something as "needs the lead's explicit decision" (like the `date:`
separator/open-range question here), make that decision and record it
plainly in the same response — don't silently pick one without saying so,
and don't stall waiting to be asked when the brief itself invited the
implementer to decide.

## Process-improvement feedback

The `hledger-researcher` dispatch worked cleanly end-to-end (background
agent, no polling, correct completion notification) and the resulting
brief was directly implementable without needing a second round of
clarification — a good sign this agent's scoping/tools/mandate are right
for this kind of task, not just directionally useful. No friction to
report on the api-spec.md pause-and-ask either — one targeted question,
one clear answer, no back-and-forth.

## Learnings filed

- `knowledge/DOMAIN_RULES.md` — two new entries: the `date:` exclusive-end
  vs `Query.date_to`-inclusive divergence, and the negated-same-prefix
  AND-not-OR rule.
- `dev-docs/compat-register/` — 7 new `status: proposed` entries
  (`LK-COMPAT-QUERY-{ACCT,DESC,DATE}-001`, `LK-UNSUP-QUERY-DATE-002`,
  `LK-COMPAT-QUERY-{DEPTH,STATUS,BOOLCOMBINE}-001`).
- `dev-docs/compat-register/README.md` — corrected a stale claim that no
  hledger source clone exists in this environment (one does, used
  directly by this phase's research).

## Where we're going

Stage C's next phase is not yet scoped. Real candidates: (a) wiring
`ledgerkit/query/` into `reports.py` and/or a new CLI `--query` flag; (b)
extending the term set (`tag:`, `cur:`); (c) designing and implementing
the `PythonRegex`/`pyre:` extension syntax (`07-query-regex.md` §7.4,
still an open design question, not just an implementation one). This
phase confirmed the planned Stage C architecture (`07-query-regex.md`'s
AST/parser/eval split) works as designed and did not surface anything
that reshapes it — the one genuine surprise (the negated-same-prefix
rule) was anticipated as a risk by the plan's own task framing, not a new
finding that changes direction.

## Time / cost note

One `hledger-researcher` dispatch (~8 minutes background), then a single
implementation response covering 4 new source files, 3 new test files (81
tests), 2 doc updates, 7 register entries, and 2 domain-rules entries. No
step ran unusually long; the tokenizer bug fix was the only rework.
