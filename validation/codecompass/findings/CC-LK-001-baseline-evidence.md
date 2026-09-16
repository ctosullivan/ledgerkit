# CC-LK-001 — raw baseline evidence

Captured per `dev-docs/planning/core-redefinition/
18-stage-c-phase-2-codecompass-adoption-plan.md` §4, phase step 2, before
any `ledgerkit/`/`cli.py` code was touched. This is raw transcript
evidence backing `CC-LK-001.{yaml,md}`; the finding's own analysis and
verdict live there, not here.

- **Ledgerkit revision:** `d86f9b4`
- **CodeCompass revision:** `e40d8d1`
- **Run from:** `/home/cormac/projects/ledgerkit` (the real repo, not a
  copy — the first time `codecompass` has ever been run against it)
- **CodeCompass binary:** `/home/cormac/projects/codecompass/.venv/bin/codecompass`

## Command 1 — `codecompass --budget 0` (bare, first run)

```
$ codecompass --budget 0
bootstrapped /home/cormac/projects/ledgerkit/vendor.toml — 0 vendor(s) tracked, 0 newly discovered
```
Exit code: 0.

**Side effects on the working tree:**
- `vendor.toml` created (0 bytes — empty).
- `context-graph.db` created (245,760 bytes; already covered by
  Ledgerkit's existing `.gitignore`, confirmed via `git status --ignored`).
- `.claude/skills/codecompass/SKILL.md` and `.claude/commands/discovery.md`
  created — both already covered by Ledgerkit's existing `.claude/*` +
  `!.claude/agents/` gitignore rule (Stage A decision), so neither would
  ever be accidentally committed regardless of this phase's own choices.
- **`CLAUDE.md` was modified directly**, without being asked to be:

```diff
+
+
+<!-- codecompass:start -->
+The table below lists dependencies with a generated reference digest under `vendor/<name>/`. Consult the linked digest before relying on training knowledge for these libraries.
+
+| Vendor | Path | Version | Enriched | Deps | Consult when |
+|---|---|---|---|---|---|
+<!-- codecompass:end -->
```

Reviewed per the plan's explicit instruction not to apply this without
review. Content is an empty table (0 vendors) — zero current value.
**Reverted** (`git checkout -- CLAUDE.md`) rather than committed; this is
a documented decision, not an oversight — see the finding's own writeup
for the reasoning (CodeCompass stays development tooling, not something
that silently accretes an unused, upkeep-requiring block into Ledgerkit's
own governance file for no current benefit).

## Command 2 — `codecompass query vendors --json`

```json
[]
```
Predicted by `18-...md` §1.9/§8 before running — confirmed exactly.
Ledgerkit has 0 mandatory PyPI/npm/Cargo dependencies; structural, not a
defect.

## Command 3 — `codecompass query skills --json` (immediately after command 1, before any `sync`)

```json
[]
```
**Empty even though the Skill/discovery files it had just generated
already existed on disk** — see Command 4 below for what changed this.

## Command 4 — `codecompass --budget 0 sync` (whole-project)

```
$ codecompass --budget 0 sync
enrichment will make ~1 AI call(s) (~$0.02) using claude-haiku-4-5-20251001 to describe 0 vendor(s): (none), and 11 relationship(s)
Proceed? [y/N]: 
Aborted.
```
Exit code: 1. **No AI call was made, no cost incurred** — the
confirmation prompt defaulted to No non-interactively, matching the
plan's explicit constraint (§4: "do not run `codecompass sync`'s Phase B
enrichment... Phase A is explicitly opt-in/cost-disclosed"). One process
observation: `--budget 0` did not silently no-op the attempt or auto-
decline without a prompt — it still printed the cost estimate and asked
before aborting on the declined confirmation. Whether that's intended
(matches "discloses estimated cost and asks" from the README) or should
auto-abort at `--budget 0` specifically without prompting is left as an
open observation, not chased further — out of scope for this baseline
capture.

**Despite aborting before Phase B, the abort happened *after* Phase A's
scan/registration step had already run and persisted** — re-running the
skills query afterward shows the change:

## Command 5 — `codecompass query skills --json` (after the aborted `sync` attempt)

```json
[
  {
    "id": 2,
    "path": ".claude/commands/discovery.md",
    "name": null,
    "kind": "slash_command",
    "origin": "codecompass_tool",
    "mentions_vendors": [],
    "mentions_source_files": []
  },
  {
    "id": 1,
    "path": ".claude/skills/codecompass/SKILL.md",
    "name": "codecompass",
    "kind": "skill",
    "origin": "codecompass_tool",
    "mentions_vendors": [],
    "mentions_source_files": []
  }
]
```
Both rows: `mentions_vendors: []`, `mentions_source_files: []` — the
Skill/discovery command mention nothing Ledgerkit-specific, matching
their generic boilerplate content (see below).

## Command 6-8 — `codecompass query relations <path>` on real, load-bearing Ledgerkit docs

```
$ codecompass query relations dev-docs/hledger-compatibility.md
Relation: (none)
Package code: (none)

$ codecompass query relations dev-docs/planning/core-redefinition/07-query-regex.md
Relation: (none)
Package code: (none)

$ codecompass query relations dev-docs/planning/core-redefinition/17-query-semantics-brief.md
Relation: (none)
Package code: (none)
```
All three: **tracked, zero relations** — not the pre-Phase-49 "not found"
error. Confirms `CG-002`/`L-016`'s fix (already known from CodeCompass's
own Phase 51 re-run against a pinned commit) generalises correctly to the
live repo, for files that didn't even exist at Phase 51's own pin
(`17-query-semantics-brief.md` postdates it).

## Command 9 — `codecompass query relations ledgerkit/reports.py` (a `.py` source file, not a spec doc)

```
$ codecompass query relations ledgerkit/reports.py
error: 'ledgerkit/reports.py' exists as a file but was not detected as a
spec/vendor doc, so it has no relations recorded — check whether it's
covered by spec_docs's glob coverage, then re-run sync
```
A **new, not-previously-tested case type**: a real source file (not a
markdown spec doc). The message is accurate and correctly disambiguated —
"exists as a file but was not detected as a spec/vendor doc" is a true,
non-misleading statement (`.py` files are outside `query relations`'
documented scope, which is spec-doc paths / vendor / Skill names), not a
false "not found." This is the disambiguation Phase 49's `L-016` fix
targeted, now independently confirmed on a case shape Phase 51's own
re-run didn't cover.

## Generated artifact content (for reference — not Ledgerkit-specific)

`SKILL.md` and `.claude/commands/discovery.md`'s content matched
CodeCompass's own `tests/fixtures/ledgerkit_lifecycle_demo/` fixture
templates near-verbatim (generic boilerplate, "Vendors (0 tracked, 0
enriched)" table empty) — confirmed by direct comparison, not assumed.

## Cleanup

After capturing the above, the working tree was restored to its
pre-baseline state: `CLAUDE.md` reverted (`git checkout --`), `vendor.toml`,
`context-graph.db`, `.claude/skills/codecompass/`, and
`.claude/commands/discovery.md` deleted. Nothing CodeCompass-generated
was committed to the Ledgerkit repository — consistent with "CodeCompass
remains development tooling, never a Ledgerkit runtime dependency"
(`18-...md` §10/Development-tool separation).
