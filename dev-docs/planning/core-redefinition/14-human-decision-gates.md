# 14. Human decision gates

Nothing in this package authorises implementation. Each gate below is a
specific, answerable question; work gated behind it does not start until
it's answered. Gates are independent of each other except where noted —
resolving G1 doesn't require resolving G3 first, etc.

## G1 — Licence transition: which option, exactly? — RESOLVED: Option A

**Resolved 2026-09-12: Option A** — GPL-3.0-or-later for `ledgerkit`
Core. Executed this session: `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`,
`pyproject.toml` (`license = {text = "GPL-3.0-or-later"}`, classic form,
plus a matching `License ::` classifier), `README.md`, `CONTRIBUTING.md`,
`dev-docs/versioning.md`, `ledgerkit/__init__.py`, and
`knowledge/DECISIONS.md` (2026-09-12 entry). Build and full test suite
(575 tests) verified passing after the change.

**Correction (same day):** a PEP 639 SPDX license-expression string was
tried first, verified only against one local environment, and broke CI's
Python 3.8 job (`setuptools` has no release supporting both Python 3.8 and
that syntax). Reverted to the classic dict form, which is what's described
above and is what's actually deployed — see
`knowledge/ANTIPATTERNS.md`. This is exactly the "verify locally ≠ verify
across the matrix" mistake `10-source-assisted-development.md` §10.4
warns against for compatibility claims generally, now demonstrated on
packaging metadata rather than accounting behaviour.

**`ledgerkit-editor`'s own relicensing is explicitly out of scope for this
resolution — see G8.** Option A originally assumed both repos move
together; that assumption was overridden: Core's licence change proceeds
independently, and Editor's own repository decides its own response and
timing.

**Blocked and now unblocked:** `09-compatibility-system.md`'s
compat-register work can now describe entries as living under a
GPL-compatible licence; directly-translated hledger material
(`10-source-assisted-development.md` §10.3) can now be lawfully hosted, if
and when any is added — none has been yet.

**Was never blocked:** Stages B–G's technical design and implementation,
which are licence-neutral — only the wholesale-copying provenance category
actually depended on G1's outcome; source inspection, algorithm
understanding, and adapted implementation were always fine (§10.1).

## G2 — Public product positioning — RESOLVED: adopted

**Resolved 2026-09-12.** Executed: `README.md` intro and Acknowledgements
section rewritten; `pyproject.toml` `description` field changed to "A
deterministic, Python-native accounting and query engine with a documented
hledger-compatible foundation"; `ledgerkit/__init__.py` module docstring
updated to match. PyPI's listing picks this up on the next publish.

## G3 — Compatibility baseline confirmation — RESOLVED: hledger 1.52.4

**Resolved 2026-09-12: hledger 1.52.4**, per `09-compatibility-system.md`
§9.1. No file changes required beyond what's already in the compat-register
scaffolding (`dev-docs/compat-register/examples/*.yaml`, already stamped
`compatibility_target: "1.52.4"`). Re-verify and re-stamp affected entries
if the baseline advances to a later `1.52.x` patch release.

## G4 — Roadmap restructuring

**Question:** Approve the Stage A–I structure and the specific
reclassifications in `12-roadmap-migration.md` §12.3 — most notably,
Milestone 5 ("CLI Filter Flags") becoming "superseded by Stage C" rather
than implemented as originally scoped. Does this require rewriting
`ROADMAP.md` now, or should the existing Milestone 0–5 structure stay
in place until Stage A actually begins and `roadmap-context-curator`
performs the rewrite as its first act?

**Blocks:** any edit to the live `ROADMAP.md`.

## G5 — Major architecture/schema changes — RESOLVED IN PRINCIPLE (not executed)

**Resolved 2026-09-12, in principle only.** Both changes approved as
direction: (a) the parser retaining lot/cost annotation data instead of
discarding it (`06-core-architecture.md` §6.3, prerequisite for Stage F);
(b) introducing `ledgerkit/query/` as a new subpackage with `Query`
becoming a compatibility shim over it (`06-core-architecture.md` §6.5,
`07-query-regex.md`) — the second now additionally justified by G8's
confirmation that `ledgerkit-editor` genuinely depends on `Query` today.

**Not executed.** "In principle" approval unblocks Stage B/C *implementation
work* when those stages actually begin — it is not authorisation to start
writing `ledgerkit/query/` or changing the parser's lot-annotation handling
in this session. No source file under `ledgerkit/` was touched by this
gate's resolution.

## G6 — Intentional compatibility breaks — RESOLVED: recommendation adopted

**Question:** As each Stage C–G phase surfaces a candidate
`INTENTIONAL_DIVERGENCE` (starting with the two backfilled examples in
`dev-docs/compat-register/examples/`), does it need per-instance human
sign-off, or does `hledger-researcher` + `compat-differential-tester`'s
process (propose → executable-verify) constitute sufficient authority on
its own once G1–G5 are resolved?

**Resolved 2026-09-12:** per-instance sign-off for the *first few* entries
(to calibrate whether the process is working as intended — not yet
exercised, since no Stage C/D/E work has started), then delegate to the
agent process once `release-phase-auditor` has independently confirmed a
few cycles are sound. Nothing to execute now — this governs behaviour once
Stage C produces its first real divergence candidate.

## G7 — Core 1.0 boundary confirmation — RESOLVED: confirmed as written

**Resolved 2026-09-12.** The Core 1.0 success criteria in
`12-roadmap-migration.md` §12.5 stand as the final Definition of Done —
"every hledger command exists" is explicitly **not** a criterion. Nothing
to execute now; this governs Stage I, years away at current pace — recorded
now specifically so scope-creep pressure across Stages E–G has a fixed
reference point to be checked against.

## G8 — `ledgerkit-editor`'s own response to G1 — RESOLVED: handled separately

**Resolved 2026-09-12:** `ledgerkit-editor`'s relicensing is an
**independent decision made in that repository, on its own timeline** —
explicitly not bundled into Ledgerkit Core's licence migration, and not
executed by this session. Its actual `ledgerkit` usage *was* inspected
(superseding this gate's earlier note that it hadn't been): it imports
`ledgerkit` in-process and uses `ledgerkit.Query`, `ledgerkit.EditorDocument`,
`ledgerkit.parse_string_lenient`, `ledgerkit.{models,reports,checks,parser,
commodity_style}`, and `ledgerkit.{load,journal_to_text,transaction_to_text}`
directly — most substantially in `filter_popup.py` and `query_match.py`
(its transaction-filter feature, which uses `ledgerkit.Query` heavily).
This confirms the Query-compatibility-shim requirement in
`06-core-architecture.md` §6.5 is a real, not speculative, constraint.

The underlying tension described in `02-licence-migration.md` §2.2 (a GPL
library embedded in-process inside an MIT application is not a stable
long-term combination) still stands and is unaffected by this
sequencing choice — it simply means `ledgerkit-editor`'s own repository
makes and executes that decision itself, at whatever pace it chooses,
rather than Ledgerkit Core's session making it on Editor's behalf.

**No longer blocks anything in Ledgerkit Core.**

## Summary table

| Gate | Status | Executed this session? |
|---|---|---|
| G1 | **RESOLVED** — Option A, Core only | Yes — LICENSE/NOTICE/pyproject.toml/README/CONTRIBUTING/versioning.md/`__init__.py`/DECISIONS.md; build + 575 tests verified |
| G2 | **RESOLVED** — new positioning adopted | Yes — README/pyproject.toml description/`__init__.py` |
| G3 | **RESOLVED** — hledger 1.52.4 | Yes — reflected in compat-register examples |
| G4 | **RESOLVED** — rewrite now | In progress — `ROADMAP.md` rewrite next |
| G5 | **RESOLVED in principle** | No — Stage B/C implementation not started |
| G6 | **RESOLVED** — process defined | No — nothing to execute until Stage C's first divergence |
| G7 | **RESOLVED** — criteria confirmed | No — Stage I is not imminent |
| G8 | **RESOLVED** — handled separately, not by this session | No — explicitly deferred to `ledgerkit-editor`'s own repository/timeline |
