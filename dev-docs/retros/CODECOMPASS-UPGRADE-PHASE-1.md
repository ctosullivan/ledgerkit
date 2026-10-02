<!-- dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md -->

# CodeCompass upgrade + clean-room docs — Phase 1 retro

- **Date:** 2026-10-02
- **Commit(s):** (this response's commit)
- **Agents used:** none dispatched this phase — direct tooling work only
  (fetch/pin, `codecompass sync`/`index`/`check`, agent-brief diffing and
  hand-merging, guard-script authoring and testing).

## Where we are

This is Phase 1 of 6 in the governing plan (`dev-docs/planning/core-
redefinition/29-codecompass-upgrade-and-clean-room-docs.md`), twice
amended and approved to implement straight through to closeout. Stage C
closed 2026-09-27; Stage D not started. This phase is the tooling
foundation the remaining five phases depend on: a current, pinned
CodeCompass integration and a reconciled agent roster. Project state
after this phase: CodeCompass and `codecompass-template` are pinned and
the pin is mechanically enforced (not just recorded); `context-graph.db`
reflects Stage C's real source; all four existing CodeCompass-derived
agent briefs are reconciled against upstream; two new roles
(`implementation-reconstructor`, `domain-skeptic`) exist, adapted to
Ledgerkit's conventions; `CLAUDE.md`'s stale folder-structure diagram is
corrected. No `ledgerkit/`/`tests/` code touched; 935 tests still pass.

## Goal

Per the plan's §2: pin CodeCompass/`codecompass-template` and enforce the
pin mechanically; re-sync/index/check; prove Stage C source is
represented; reconcile the four existing agent briefs; add and adapt
`implementation-reconstructor`/`domain-skeptic`; fix the stale
`CLAUDE.md` folder-structure diagram; update CodeCompass integration
documentation; run tests; retro and normal project-state updates.

## Scope delivered vs planned

Matches the plan exactly, with one judgment call the plan left open:
**pin enforcement via a guard script, not a dedicated worktree** (plan
§2.0 explicitly permits either). Rationale, recorded in
`PINNED-REVISIONS.md`: `/home/cormac/projects/codecompass` is
CodeCompass's own active development repository (155+ commits since
Ledgerkit's original adoption, several dated the same day as this pin),
and the installed `codecompass` CLI is a single, global `pipx install -e`
shared with any other session actively developing CodeCompass itself.
Re-pointing that global install at a separate worktree would change
shared state outside this repository's own blast radius for no
isolation benefit the guard script doesn't already provide — the guard
was built and empirically tested in both directions (confirmed it passes
when the checkout matches the pin, and genuinely fails closed —
non-zero exit, clear message, no silent continuation — when it doesn't,
verified by temporarily corrupting a copy of the pinned SHA and
restoring it afterward).

One operational finding, not scoped by the plan but handled within it:
`codecompass sync`'s Phase B AI-enrichment step prompted for
confirmation (~$0.18 estimated spend) and then, when the prompt was
accepted, failed with `TypeError: Could not resolve authentication
method` — no `ANTHROPIC_API_KEY` is configured for the CodeCompass CLI
on this host. Declined the enrichment prompt instead (answered "n"),
which let `sync` complete cleanly and still correctly rebuilt
`context-graph.db` and regenerated `CLAUDE.md`'s routing table/
`SKILL.md` (confirmed by reading `cli.py`: the graph rebuild happens
before the enrichment trigger, and artifact regeneration runs in a
`finally` block regardless of enrichment's own outcome) — this phase's
goals (schema-current graph, regenerated artifacts) don't need AI
enrichment at all, and Ledgerkit has zero tracked vendor dependencies to
enrich in the first place.

## What was achieved

- `dev-docs/clean-room/PINNED-REVISIONS.md`: `codecompass` pinned at
  `96a1e4d53acf4acc6659dc233b1ca2eafae3d41a` (confirmed, via a fresh
  `git fetch`, not ahead of its own origin); `codecompass-template`
  freshly cloned to `/home/cormac/projects/codecompass-template` and
  pinned at `68bae8ec739aea413bbedac9f19078f6ab995aca`.
- `dev-docs/clean-room/check_codecompass_pin.sh`: resolves the installed
  `codecompass` executable's real source checkout via its editable
  install's own `direct_url.json`, compares `HEAD` against the pin,
  fails closed on mismatch. Tested both ways, not just asserted to work.
- `codecompass sync`/`index`/`check` re-run against the pinned revision:
  `check` clean (no severity findings); `context-graph.db`'s
  `last_deterministic_rebuild_at` now 2026-10-02; `query source-symbol`
  confirmed real entries for `ledgerkit/query/*`
  (`compile_hledger_regex`, `ledgerkit/query/regex.py:265`) and
  `ledgerkit/tags.py` (`_effective_tags`, line 210) — 107 of 322 total
  indexed symbols now come from Stage C's own code, proving the re-sync
  genuinely picked it up, not merely that the command exited 0.
- Four existing agent briefs (`docs-reconstructor`, `docs-maintainer`,
  `release-phase-auditor`, `roadmap-context-curator`) diffed line-by-line
  against the pinned upstream and hand-merged — not blind-copied.
  Adopted: `docs-reconstructor`'s hardened, topic-scoped MODE 2 (mapped
  onto Plan 29's own Phase 3/4/5 paths rather than copied verbatim);
  `docs-maintainer`'s generated-file caution, post-fix completeness-grep
  discipline, docstring-staleness side-scan, and full Legacy
  reconciliation mode (mapped onto Plan 29's own five-way scheme, which
  already matched upstream's exactly); `release-phase-auditor`'s
  single-question-per-verdict rule (directly load-bearing for Plan 29's
  own Phase 6 isolation reporting) and default persisted-audit-file
  requirement; `roadmap-context-curator`'s narrower terminal done-flip
  reconciliation rule. Declined to adopt: anything referencing
  CodeCompass's own internal `docs/domain/`, `decisions/*`, or
  `knowledge-curator`/`context-researcher` — no Ledgerkit equivalent,
  and adopting them would be scope creep per Plan 29 §9's own non-goals.
- `implementation-reconstructor.md`/`domain-skeptic.md`: adapted, not
  copied — CodeCompass's own heavier Observation/Evidence/Claim/Decision
  apparatus deliberately left out (Plan 29 §9), rewired onto Plan 29's
  own lighter assertion/snapshot/comparison artifact paths.
- `CLAUDE.md`'s folder-structure diagram: corrected from a 4-module,
  4-test-dir sketch to the real current layout (19 `ledgerkit/` modules
  including the whole `query/` subpackage, 11 real top-level `tests/`
  entries, `dev-docs/`'s real subdirectories including the new
  `clean-room/`, `.claude/`, `validation/`, and several root files the
  old diagram omitted entirely).

## What worked

- **Checking the tool's own recent commit history against the last-sync
  timestamp before assuming a breaking gap** (established in the
  original planning session, confirmed again here) kept this phase
  honestly small — a routine re-sync plus reconciliation, not a
  migration, exactly as planned.
- **Testing the guard script's failure path, not just its success path**,
  before trusting it for the rest of this initiative — the same
  discipline Plan 29 itself demands of the isolation preflight (§3.3)
  and the snapshot checker, applied here first to the simplest mechanism
  this phase introduces.
- **Reading `cli.py`'s own source to understand why `sync` crashed**,
  rather than guessing or retrying blindly, found the real cause (no API
  key) and the real safe path (decline the prompt) in one pass.

## What didn't work

The first two `codecompass sync` invocations wasted a round each: the
first used the *global* `--yes`/`--budget` flags (which belong to bare
`codecompass`, not `sync`), and the second crashed with a raw stack
trace because no API key is configured. Neither was a real blocker — the
fix (`sync`'s own `--yes`/`--budget`, then simply declining the prompt)
was found quickly by reading the actual CLI source — but it's worth
naming as the one piece of friction this phase had.

## Lessons learnt

- **A global, shared editable install (`pipx install -e`) is a real
  consideration when "enforcing a pin" — re-pointing it has a blast
  radius beyond the repository doing the pinning.** The guard-script
  alternative the plan explicitly allowed for this exact situation was
  the right call, not a corner cut; record the reasoning (as
  `PINNED-REVISIONS.md` does here), don't just silently pick the lighter
  option.
- **`codecompass`'s own CLI has subcommand-scoped flags that look
  identical to its global ones** (`--yes`/`--budget` exist both on bare
  `codecompass` and on `sync` specifically, with different semantics
  depending on position) — check `<command> --help` before assuming a
  flag's scope from its name alone.
- **A context-graph rebuild and an AI-enrichment trigger are two
  separable things inside one `sync` invocation** — declining enrichment
  (or it failing for lack of an API key) doesn't invalidate the
  mechanical rebuild that already happened first; verify this from the
  source (`cli.py`'s own `try/finally` structure) rather than assuming a
  non-zero exit means nothing useful happened.

## Process-improvement feedback

None — no agent dispatches occurred this phase, so no roster friction to
report. The two new roles (`implementation-reconstructor`,
`domain-skeptic`) get their first real exercise in Phase 3, not here.

## Learnings filed

None yet — per this initiative's own established pattern (see the
planning-phase retro's own addenda), learning-triage runs at the
initiative's eventual closeout, not piecemeal per phase, since several
of this phase's own lessons (the pipx blast-radius consideration
especially) may generalize beyond just this initiative and deserve a
`knowledge/DECISIONS.md` entry written with the full arc in view.

## Where we're going

Next: Phase 2 (isolation workflow adoption + snapshot checker
implementation, plan §3). Phase 1 confirmed the plan's own §1.1 finding
that "upgrading CodeCompass" would be small — it was, including the pin-
enforcement mechanism, which took one guard script and two test runs
rather than anything structural. Phase 2 is where the real new
tooling-build work starts (`check_snapshot.py` with historical-integrity
semantics), and where the first genuinely new artifact type
(`compliance-log.md`) gets created, ready for Phase 3 to start writing
to immediately.

## Time / cost note

One session. Mechanical work (fetch, sync, diff, merge, write, test) —
no agent dispatches, so no isolation/transcript-review overhead yet;
that starts in Phase 2's preflight probe and Phase 3's real dispatches.
