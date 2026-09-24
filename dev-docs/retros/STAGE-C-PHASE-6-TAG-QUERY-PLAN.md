# Stage C Phase 6 retro — Planning (`tag:` query-term matching: context curation + design document)

- **Date:** 2026-09-25
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** one fresh `context-curator` dispatch (Step 1) — a
  genuinely independent agent, no access to this conversation's prior
  turns, given only the existing Phase 5A context packet as a
  not-to-be-trusted starting point.

## Where we are

Stage C Phase 5A closed with a real CodeCompass workflow adopted and a
recommendation to reuse it routinely rather than run further dedicated
evaluation phases. The user directed a new, more rigorous process for
this phase — the first substantial Ledgerkit feature phase to use it:
roadmap objective → independent context curation → evidence-backed
context packet → formal design document → human approval → implementation
plan → fresh coding agent → independent verification → documentation
sync → retro → knowledge update. This retro covers the first checkpoint:
Steps 1-2 (context curation, design document). Steps 3 onward (human
approval gate, implementation planning, fresh-agent handoff,
implementation, verification, doc sync, full retro, knowledge feedback)
are explicitly **not started** — the user's own instruction is to stop
here for review.

## Goal

Produce a fresh, independently-verified body of context for `tag:NAME
[=REGEX]` query matching (not trusting the existing Phase 5A packet), then
a formal design document distinguishing verified external behaviour,
existing Ledgerkit decisions, proposed design, and unresolved questions
— explicit enough that a human can approve or redirect it without needing
this conversation's own history.

## Scope delivered vs planned

Both steps delivered exactly as specified. The `context-curator` dispatch
covered its full checklist: CodeCompass workflow first (Skill/
`/discovery`/`query`), direct Ledgerkit source inspection (`tags.py`,
`query/*.py`, `models.py`, `reports.py`, `cli.py`), Phase 4/5 architecture
inspection, existing briefs/compat-register/knowledge/tests, and direct
hledger manual/source/binary verification (nine live differential runs
on a scratch fixture, not a re-read of brief 19's own claims). The
design document covers all required sections (§14 of the doc: intended
syntax, verified behaviour, transaction/posting-level matching,
inheritance, exact/regex/value semantics, parser/AST/QueryPlan/evaluator
implications, affected CLI commands, Phase 4 data-model interaction,
combination-operator interaction, edge cases, error behaviour,
compatibility implications, Python-API backwards-compatibility, explicit
non-goals, documentation changes, proposed tests, unresolved questions),
each item tagged to one of the four required categories.

One deliberate, disclosed deviation from "just synthesise the curator's
report": the lead independently spot-checked the report's two most
architecturally significant claims (the `accounts`-command tag-stripping
mode; the missing-inheritance-layer finding) against source directly,
rather than passing them through untested — both confirmed exactly as
reported, but the check itself is the point, not the specific outcome.
The lead's own further verification also surfaced one architectural fact
the curator's report did not explicitly flag: `matches_transaction`/
`matches_posting` currently receive no `Journal` parameter at all, which
materially affects the cost comparison between the design's two
inheritance-scope options (§9.1 of the design doc).

## What was achieved

A context-curator report (§§1-7, preserved in the agent dispatch's own
output, cited by section from the design document rather than
duplicated) that: re-confirmed the existing packet's claims held, found
one genuinely new architectural fact (`accounts`' third matching mode,
never named in brief 19), corrected one framing gap (brief 19's "no tag
data model" framing predates Phase 4 shipping and needed updating, though
the underlying disclosure was already accurate in `dev-docs/
hledger-compatibility.md`), strengthened one piece of evidence from
source-only to executable (the AND-not-OR combination rule), and filed
zero new CodeCompass findings after checking CodeCompass's own gap
register directly (nothing was novel — everything reproduced already-
filed, already-diagnosed gaps). A 17-section design document
(`dev-docs/planning/core-redefinition/23-tag-query-matching-design.md`)
with three explicit unresolved questions, each with the lead's own
recommendation stated separately from the decision itself.

## What worked

- **Telling the curator explicitly not to trust the existing packet**,
  and the curator actually re-running the packet's own prior CodeCompass
  queries live rather than re-stating them — this is what caught that
  the `sqlite3` gap (`CC-LK-003`) and the `07↔17` non-relation (`CG-006`)
  both still reproduce unchanged, real re-confirmation rather than
  assumed persistence.
- **The curator checking CodeCompass's own gap register before
  concluding "nothing new to file."** Consistent with Phase 5A's own
  established discipline (`CC-LK-002`'s `CG-006` cross-reference) — this
  is now a repeatable pattern across two consecutive phases, not a
  one-off.
- **The lead's own follow-up spot-check surfacing a real, additional
  finding** (`journal`-parameter absence) the curator's report didn't
  explicitly name — confirms the "trust but verify, even a thorough
  report" discipline has genuine marginal value, not just process
  theatre, on the very first real use of this new multi-step process.
- **Presenting two named options with a stated recommendation, rather
  than a single silent choice**, for both unresolved questions (§9.1/
  §9.2 of the design doc) — mirrors Stage C Phase 5's own successful
  gate-based pattern (`G-DEPTH-1` through `G-CC-5`), reused here for a
  design-level decision rather than a process-level one.

## What didn't work

Nothing failed in this checkpoint. One thing worth naming honestly,
since the retro's later full version (post-implementation) will need to
judge whether this process is worth its ceremony: this checkpoint alone
(one agent dispatch, ~57 tool calls inside it, plus the lead's own
follow-up reads and this document) is substantially more expensive than
Stage C Phase 4's own original `tag:`-adjacent research (two
`hledger-researcher` briefs, no separate context-curation pass). Whether
the *added* rigour (independent re-verification, explicit provenance
tagging, a formal reviewable document before any code) is worth that
added cost is exactly the question Step 9's eventual process evaluation
needs to answer with evidence, not asserted here in advance either way.

## Lessons learnt

Re-verifying a prior research artifact's *central* claims — not just
skimming it for continuity — is what turned "the curator wrote a good
report" into "the lead can build on this report with confidence." This
is the same lesson Phase 5A's own retro drew from its `CG-004` correction,
now applied a second time, in a different role (the lead checking a
subagent's report, rather than a phase checking its own prior planning
pass) — suggesting it generalises across *who* is doing the trusting, not
just this one project's own planning-pass habit.

## Process-improvement feedback

The four-category discipline (verified-external / existing-decision /
proposed / unresolved) made the design document's own internal
consistency checkable in a way a normal prose design doc wouldn't be —
every claim's category is a testable assertion (is this really externally
verified? is this really already decided?), not just a section heading.
Worth carrying forward as the default shape for any future design
document, not just this one.

## Learnings filed

Deferred to the full phase retro (Step 9) rather than filed piecemeal
here — this checkpoint's findings are all provisional pending the
design's own approval (§9.1/§9.2 aren't decided yet, so nothing durable
to write to `knowledge/*.md` follows from them until they are).

## Where we're going

**Stopped, as directed, for human review.** The design document's §17
lists exactly what needs explicit approval: §9.1 (inheritance scope,
lead recommends Option A), §9.2 (`accounts` command mode, lead recommends
uniform/no special case), and general approval to proceed to Step 4
(implementation planning) once those are resolved. No implementation
work of any kind has begun.

## Time / cost note

Single response: one `context-curator` dispatch (~473s wall time, 57
tool uses, per its own reported usage), the lead's own three follow-up
verification greps/reads, then the 17-section design document itself.
The dispatch's own cost dwarfs everything else in this checkpoint — see
"What didn't work" above for the open question of whether that's
proportionate for a phase of this size, to be judged with evidence once
the full phase (including implementation) is complete.

---

## Addendum (2026-09-25, same day) — design-review correction, caught before implementation

The user reviewed the design document and found it **not yet ready for
approval**: its claim that the four A-D propagation rules constituted
*complete* hledger 1.52.4 effective-tag semantics was incomplete — it
omitted commodity-directive tag propagation entirely, a real, separately-
documented (`hledger.1:3550-3556`, "Commodity tags") fifth source. This
is recorded explicitly, per the user's own instruction, as **a
design-review correction caught before any code was written — not an
implementation defect**. No `ledgerkit/`/`tests/` code existed to have a
defect in; what was wrong was the design document's own claim of
completeness, caught by review at exactly the stage this process's own
mandatory gate (Step 3) exists to catch it.

**What the correction pass found, verified executable rather than
resolved by interpretation** (the review's own explicit instruction,
since the manual's "posting tags override account tags override
commodity tags" wording is ambiguous between "shadowing" and "union"
readings): built a five-transaction fixture and ran it directly against
the pinned hledger 1.52.4 binary. Result: **no shadowing occurs at all**
for `tag:` query matching — a posting with its own `rate:1`, whose
account declares `rate:3` and whose commodity declares `rate:2`, matches
`tag:rate=1`, `tag:rate=2`, **and** `tag:rate=3` simultaneously. The
manual's "override" language, taken literally, would have predicted
exclusion; the source (`Tag = (TagName, TagValue)`, a plain tuple with
structural equality, combined via `Data.List.union`) predicted no
exclusion for differently-valued same-named tags; the executable result
confirmed the source's prediction over the manual's prose — exactly the
resolution order the review instructed ("make the executable result the
basis... where they differ"). This also resolved, precisely, *why* the
original document's own live tests had already observed account-tag
inheritance working "by default" without the correction pass needing to
re-derive it from scratch: `auto_posting_tags_` (the flag gating both
account- and commodity-tag materialization) defaults to `False` in the
bare library, but is set `True` for every CLI command except `print
--output-format=beancount` (`hledger/Hledger/Cli/CliOptions.hs:642`) —
found by tracing the actual value used, not assumed from the library
default alone.

**Substantive amendments made** (full detail in the design document's
own body, not restated here): §2 gained two new subsections (§2.6
commodity-tag propagation, §2.7 the executable precedence matrix); §2.5's
`accounts`-mode finding was corrected to be broader (commodity tags are
stripped too, not just the posting's own); §3/§4 now name a second,
distinct substrate gap (Ledgerkit's `commodity` directive parsing
actively discards its own comment text, confirmed by direct read of
`ledgerkit/parser.py:1290`, `body = _strip_directive_comment(rest)`); §9.1
was rewritten to define Option A as genuinely complete (four sources, not
three) and to soften the evaluator-API recommendation away from a
required positional `Journal` parameter toward backward-compatible
alternatives, per explicit instruction not to assume that shape; §9.2's
`accounts`-mode recommendation was **reversed** (from "diverge, uniform
matching" to "replicate hledger's mode") after re-weighing the review's
own point that the wrinkle is real, confirmed, and narrow enough to
implement cheaply — general internal-consistency preference alone was
not, on reflection, a strong enough reason to prefer a known, avoidable
divergence; §9.3's default changed to keeping new helpers private; §10/
§12/§16/§17 were updated throughout to match.

**Process observation**: this is the second time in two consecutive
checkpoints (the original design document's own §1 already recorded one
lead-vs-curator-report cross-check; this is now a lead-vs-user-review
cross-check) that an explicit "verify, don't assume completeness" pass
caught something a prior pass had stated with more confidence than the
evidence supported. Both corrections were caught by the same discipline
— checking a specific, falsifiable claim against primary sources rather
than accepting a well-organised document's own internal consistency as
proof of external accuracy.

Still stopped for human review, as before — the amended design's §17 is
the updated approval list. No implementation started.

---

## Addendum 2 (2026-09-25, same day) — small final correction pass

A third review pass, explicitly scoped as "a small final correction
pass only, not a redesign, not a curator re-run, not implementation."
Four corrections, each verified before being written down rather than
taken on the review's own restatement alone:

1. **Plain `accounts tag:X` visibility was still wrong after the prior
   amendment.** That amendment correctly added that commodity-propagated
   tags are stripped alongside posting-own ones, but stated the result
   as "shows only account-inherited tags" — missing that
   `postingAllTags` (the function query matching actually reads)
   unconditionally re-adds the transaction's own tags on top of whatever
   `journalPostingsKeepAccountTagsOnly` did to a posting's own tags.
   **Verified live before writing this correction down**: `accounts
   tag:rate=4` (a transaction-header-only tag) matches, confirming
   transaction-level tags survive the stripping. The correct rule is a
   four-way split (transaction-level and account-inherited visible;
   posting-own and commodity-propagated not), not the three-way split
   the prior amendment stated.
2. **Transaction-level matching's conceptual rule was stated too
   narrowly.** Corrected to "a transaction's own tags match directly, OR
   any posting's effective tags match" — sourced precisely to
   `transactionAllTags t = ttags t ++ concatMap ptags (tpostings t)`
   (`Posting.hs:443-444`), which unions the transaction's own tags in
   directly rather than solely via its postings.
3. **The evaluator-API recommendation contained a real Python error.**
   "A keyword-only `journal` parameter with no default... existing
   callers unaffected" is not correct — a keyword-only parameter with no
   default is still mandatory on every call. Corrected to name
   `journal: Journal | None = None` (a genuine default) as the leading
   backward-compatible candidate, with explicit-failure-not-silent-
   degradation restated as the binding constraint regardless of which
   shape implementation planning ultimately picks.
4. **The commodity-tag substrate's scope question is now resolved** (not
   left open): in scope for this same Phase 6, not split into a
   prerequisite sub-phase, on the reasoning that — unlike Phase 4's own
   account-tag work, a genuinely separate parsing/storage feature — the
   commodity substrate is a bounded completion of this phase's own
   `tag:` semantics, not a separate capability. Design-approved scope
   only; nothing implemented.

**Process observation, worth naming plainly**: this is the third
successive pass in which a stated finding needed correcting on review —
first the curator-report-vs-lead cross-check (original document), then
the manual-vs-executable-evidence correction (first amendment, which
also *introduced* the incomplete `accounts` claim this pass fixes), now
this. None of the three corrections were caught by the pass that
introduced them; each was caught by the *next* pass's fresh scrutiny.
That pattern is itself a data point worth carrying into Step 9's
eventual process evaluation: multiple review passes on the same
artifact are finding real, distinct, materially-different errors each
time — not diminishing returns yet, three passes in.

Still stopped for human review. Amended §17 is the current, and
materially shorter, approval list (two open items instead of the
previous five, three having been resolved with recommendations
implementation planning may still override).
