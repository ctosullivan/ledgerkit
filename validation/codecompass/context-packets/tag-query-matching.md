# CodeCompass context packet — `tag:` query-term matching

Produced Stage C Phase 5A, Step 5 (`dev-docs/planning/core-redefinition/
22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md`). This is the
context packet for the genuine next Ledgerkit development task (G-CC-2,
resolved): implementing hledger's `tag:NAME[=REGEX]` query-matching
semantics. **This packet researches and prepares context for that task —
it does not implement it.** `tag:` matching itself remains a separate,
subsequent, separately-approved phase.

**Ledgerkit revision:** `eecb8a9`. **CodeCompass revision:** `4bc7c1d`
(local clone `/home/cormac/projects/codecompass`), CLI `codecompass-
context` `1.0.0` installed via `pipx install -e`, tag `v1.0.0`.

Every finding below carries one of four provenance categories, per the
amended plan's Step 5 requirement:

- **[SURFACED]** — surfaced by CodeCompass; would not plausibly have been
  reached without a CodeCompass query/Skill/`/discovery` result.
- **[INDEPENDENT]** — independently found from Ledgerkit sources; no
  material CodeCompass contribution.
- **[POINTED]** — CodeCompass pointed to relevant evidence, but the
  conclusion required direct investigation to understand what it meant.
- **[KNOWN]** — already known before CodeCompass consultation, from
  Ledgerkit's own docs/briefs/compat-register.

---

## 1. Research procedure actually followed (Step 4)

Per the amended plan's explicit sequencing requirement:

1. **Generated agent entry points first**: read `.claude/skills/
   codecompass/SKILL.md` (regenerated via `codecompass index`, this
   phase) and `.claude/commands/discovery.md` in full — the latter's own
   defined procedure (canned queries → SQL fallback → read persisted
   digests) is what §2-3 below actually follow, not an ad hoc departure
   from it.
2. **Then** direct `codecompass query`/`check` calls for deeper
   inspection, and one direct `sqlite3`-equivalent query (via Python's
   `sqlite3` module — the SKILL.md's own documented fallback names the
   `sqlite3` CLI specifically, which is **not installed in this
   environment**; noted as a real, minor environment-gap finding, §5).
3. Cross-referenced against Ledgerkit's own existing `tag:`-relevant
   documents (the two `hledger-researcher` briefs, `dev-docs/
   hledger-compatibility.md`, `ledgerkit/query/`).

## 2. What CodeCompass's own graph currently holds for this task

**[SURFACED]** `codecompass query vendors` → 0 rows. Ledgerkit has no
tracked runtime dependencies (matches its own known zero-dependency
design; `pandas` is an optional extra, not detected as "used" in this
environment). No vendor-side context exists for the `tag:` task at all —
there is no dependency whose docs/symbols could inform `tag:` matching
semantics, because the relevant reference material (hledger's own
manual/source) is not a package CodeCompass tracks.

**[SURFACED]** `codecompass query relations dev-docs/planning/
core-redefinition/19-tag-query-semantics-brief.md` → one real,
mechanically-detected `mentions_artifact` edge, target
`.claude/skills/codecompass/SKILL.md`.

**[POINTED → INDEPENDENT]** That edge's existence prompted checking *why*
— `grep -n -i codecompass` on the brief showed it cites CodeCompass's own
Phase 54 reference-experiment writeup and **corrects a specific
extraction error found there**: an earlier extraction of the hledger
manual's tag-inheritance section silently dropped the third of three
inheritance rules. This is a real, substantive cross-project finding —
CodeCompass's mechanical detection correctly flagged that the brief
*mentions* CodeCompass, but understanding *what the mention actually
means* (a documented accuracy correction, not a general tool reference)
required reading the brief directly. Enriched this edge via `codecompass
enrich apply` (agent-facing path, since no `ANTHROPIC_API_KEY` is
configured) with an accurate summary of this relationship — see
`validation/codecompass/findings/CC-LK-002.md` for the full write-up.

**[SURFACED]** `codecompass query relations dev-docs/planning/
core-redefinition/20-tag-parsing-syntax-brief.md` → zero relations, an
**honest empty result** (the brief doesn't contain another tracked
doc-artifact's exact title string). Confirmed this is not a false
negative — no other spec doc's title appears verbatim in brief 20's
prose.

**[SURFACED, materially corrects the phase's own planning-pass claim]**
`context-graph.db`'s `doc_artifacts` table has real, non-`NULL` `name`
values for `spec_doc`-kind rows (e.g. `dev-docs/hledger-compatibility.md`
→ `"Hledger Compatibility"`), and 18 real `mentions_artifact` edges exist
project-wide. **This directly contradicts this phase's own original
plan's §1.4 claim that `CG-004` ("`doc_artifacts.name` never populated
for `spec_doc` rows") was "still open, not fixed in v1.0.0."** Checking
CodeCompass's own `CHANGELOG.md`/`planning/retros/phase-55b-...md`
directly: `CG-004` was closed in **Phase 55b, dated 2026-09-17** — before
this phase's original planning pass was even written. The original
plan's source check was simply wrong (a research error in the planning
pass, not a change in CodeCompass between then and now — recorded
plainly per the amended plan's own "don't anchor, verify independently"
instruction; see §6 for how this feeds the evaluation).

## 3. What CodeCompass's graph does *not* cover for this task

**[SURFACED]** `codecompass query symbol MaxAccountLevel` / `query symbol
parse` → both "no symbol named ... found." Confirmed: CodeCompass indexes
*vendor* (dependency package) symbols and their usage, not Ledgerkit's
own source code. `ledgerkit/query/`'s actual AST nodes, parser structure,
and `ledgerkit/tags.py`'s tag data model are **not queryable through
CodeCompass at all** — they require direct reading, exactly as every
prior evaluation in this project's history has also found. This is a
structural scope boundary, not a defect.

**[SURFACED]** `codecompass check` → "Spec docs with no detected
relations" lists 42 of Ledgerkit's own docs, including both tag briefs'
sibling planning documents and most retros/compat-register entries.
Mechanical mention-detection only catches exact doc-title string matches
— it cannot detect that, say, `17-query-semantics-brief.md` and
`19-tag-query-semantics-brief.md` are thematically related (both about
Stage C's query language) unless one literally names the other's title.

## 4. What was already known, independent of CodeCompass

**[KNOWN]** `tag:NAME[=REGEX]` matching is not implemented
(`dev-docs/hledger-compatibility.md` lines 165, 247, 276, confirmed
current this session). Its prerequisite — tag parsing/storage
(`Transaction.tags`/`Posting.tags`/`Journal.declared_account_tags`) —
shipped in Stage C Phase 4.

**[KNOWN]** Brief 19 (`19-tag-query-semantics-brief.md`) already
documents the target semantics in detail: bare name/value matching via
`patternsMatchTags`; **four** propagation/inheritance rules (account←
parent, posting←own account, posting←its transaction, transaction←all
postings) — not three, correcting the CodeCompass Phase 54 error found
independently (§2); `tag:` terms never OR-combine even when unnegated,
unlike `acct:`/`desc:`/`status:`; `payee:`/`note:` share the same `Tag`
AST node as a case-sensitive literal-string dispatch trap; account-level
`tag:` matching is a separate, narrower, declared-tags-only mechanism.
Proposed compat-register entries already drafted there:
`LK-COMPAT-QUERY-TAG-001`, `LK-COMPAT-QUERY-TAG-INHERIT-001` (blocked),
`LK-COMPAT-QUERY-TAG-COMBINE-001`.

**[KNOWN]** Brief 20 (`20-tag-parsing-syntax-brief.md`) covers the
parsing grammar this phase's own Stage C Phase 4 already implemented
(`ledgerkit/tags.py`) — relevant to `tag:` matching only as the data
model matching will read from, not as remaining work.

**[INDEPENDENT]** `ledgerkit/query/parser.py`'s `_PREFIX_BUILDERS` dict
(confirmed this session, `grep`) has no `"tag:"` entry — matching the
docs exactly, no drift between documentation and implementation.

## 5. Environment/workflow observations (feed Step 6/CC-LK findings)

- `sqlite3` CLI is not installed in this environment; `.claude/skills/
  codecompass/SKILL.md`'s own fallback instructions name it specifically
  ("query `context-graph.db` directly with `sqlite3`"). Worked around via
  Python's `sqlite3` module for this phase's own investigation, but a
  fresh agent following the Skill's literal instructions in an
  environment without `sqlite3` would hit a dead end without the same
  workaround occurring to it. Filed as `CC-LK-003` (§6 of the plan, Step
  6).
- Bare `codecompass sync` (whole-project) prompted for enrichment
  confirmation and aborted cleanly (no partial/corrupt state) when no
  input was available — `context-graph.db` was already fully written by
  the deterministic portion before the prompt. Confirms deterministic
  sync and enrichment are genuinely separable steps, matching the amended
  plan's Step 2 sequencing requirement structurally, not just by
  convention.

## 6. Unresolved questions for whoever implements `tag:` matching next

1. Should the four inheritance rules (brief 19) be implemented as a
   single combined predicate or four composable primitives? Not resolved
   by this packet — an implementation-phase design question.
2. `payee:`/`note:`'s shared-AST-node dispatch trap (brief 19) needs a
   decision on whether Ledgerkit's own `Payee`/`Note` (if/when
   implemented) share a node the same way, or diverge deliberately —
   also not resolved here.
3. None of CodeCompass's tracked context bears on either question —
   both are pure hledger-semantics/Ledgerkit-architecture questions, for
   `hledger-researcher`/the lead, not something a richer CodeCompass
   graph would help resolve even if Ledgerkit had tracked dependencies.

## Summary: does this change the historical LOW-advantage finding?

Per the amended plan's explicit instruction not to assume either way:
this task's own evidence shows a **mixed, more nuanced picture than a
flat repeat of the baseline**. The vendor-tracking/symbol-query axis
(§3) reproduces the historical LOW result exactly — 0 vendors, no
project-source indexing, unchanged. But the doc-relation axis (§2) shows
a genuine capability that did not exist in every prior Ledgerkit
evaluation this project's own history recorded (`CG-004` was open through
Phase 54's own experiment) and is now real, working, and produced one
concrete, correct, non-trivial finding (the Phase 54 extraction-error
citation) that a fresh agent glancing at `check`'s coverage report would
plausibly have found faster via CodeCompass than via cold-reading every
brief. Whether that's enough to move the *overall* verdict is the
retro's call (§6 of the plan) — this packet reports the evidence, not a
pre-decided verdict.
