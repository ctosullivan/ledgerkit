<!--
producer: phase-4-drafting
document: current-shipped-state (internal, feeds Phase 5)
dispatch: phase4-draft-current-shipped-state-01
dispatch-timestamp: 2026-11-14T00:00:00Z
date: 2026-11-14
topics covered: current-state, compat-system
permitted evidence: dev-docs/clean-room/snapshots/{current-state,compat-system}-v1.md(+.sidecar.json),
  dev-docs/clean-room/assertions/{current-state,compat-system}/*.md,
  dev-docs/clean-room/implementation-reconstruction/{current-state,compat-system}.md,
  dev-docs/clean-room/implementation-comparison/{current-state,compat-system}.md
-->

# Current Shipped State (Internal Draft — Factual, Present-Tense Only)

This draft records only what currently exists and works in ledgerkit, as
established by Plan 29's clean-room snapshot/assertion/reconstruction/
comparison artefacts for the `current-state` and `compat-system` topics
(both frozen 2026-10-02T16:50:03Z at repository revision
`51881415a204af8908834ec602a54f6e1f67dbdd`). It contains no roadmap or
intent language. Every fact below is cited to the assertion that
establishes it, in the form `<topic>@v1#<assertion-id>`. Confidence
language matches each cited assertion's classification in its topic's
`implementation-comparison` report (`aligned`, `partial`, or
`insufficiently_verified`); per the comparison reports' own stated rule,
an `aligned` classification confirms that two independently-gathered
evidence sets currently agree — it does not itself certify that the
underlying fact is desirable design, only that it is current fact.

## Package identity and metadata

The package's declared version in `pyproject.toml` is `1.0.0.dev1`, with
`requires-python = ">=3.8"` and zero runtime `dependencies` declared; an
optional `pandas` extra (`pandas>=1.3`) exists under
`[project.optional-dependencies]`. (current-state@v1#current-state-001,
classification: aligned — the independent reconstruction's direct read of
`pyproject.toml` reproduces these same fields verbatim.)

Two git tags currently exist in the repository, `v1.0.0` and
`v1.0.0.dev1`, and `git describe --tags --always` reports the current
`HEAD` as 60 commits ahead of `v1.0.0.dev1` (commit `5188141`), i.e.
`v1.0.0.dev1-60-g5188141`. This is asserted but was not independently
cross-checked against a second artefact: the topic's own
implementation-reconstruction report scoped its evidence to
`pyproject.toml` plus live CLI runs only and contains no git-history
inspection, so its comparison classifies this fact as
insufficiently_verified rather than aligned. (current-state@v1#current-state-002,
classification: insufficiently_verified.)

## CLI surface

The installed `ledgerkit` CLI's top-level `--help` lists exactly six
subcommands as the positional choice set: `balance`, `register`,
`accounts`, `print`, `stats`, `check`, under one flat `argparse` parser
with options `-h/--help`, `--version`, `-v/--verbose`, `-1`,
`-o/--output-file`, `-f/--file`, `-s/--strict`, `-I/--ignore-assertions`,
`-q/--query`, and `-c/--commodity-style`. (current-state@v1#current-state-004,
classification: aligned — the reconstruction's own `--help` run reproduces
this exact usage/options block word-for-word.)

Running `python -m ledgerkit <subcommand> --help` for each of the six
subcommands currently prints byte-for-byte the same top-level usage/help
text as the bare `--help` invocation; there is no subcommand-specific help
text, confirming a single flat argument parser shared by all six commands
rather than true subparsers with their own option sets.
(current-state@v1#current-state-005, classification: aligned.)

Running `stats` against the project's own `tests/fixtures/sample.journal`
currently succeeds (exit code `0`, no traceback) and produces non-empty,
well-formed tabular output (e.g. `Txns : 5 (0.2 per day)`, `Accounts : 6
(depth 3)`, `Commodities : 1`). Running `check -f tests/fixtures/sample.journal`
against the same fixture also currently succeeds (exit code `0`, no
traceback), but — unlike `stats` — produces no stdout output at all on
success; a passing `check` run is silent by design.
(current-state@v1#current-state-008, classification: aligned — the
reconstruction's independent run reproduces the identical `stats` field
values for this fixture and the identical silent, exit-0 `check` result.)

## Test suite

As of the frozen revision, running the full test suite via
`python -m unittest discover -s tests -t . -v` collects and runs 935
tests, of which 29 are skipped and 0 fail or error, with the run reporting
overall result `OK (skipped=29)` and exit code `0`. This figure is
asserted but was not independently cross-checked against a second
artefact: the topic's implementation-reconstruction report never executes
the test suite (its evidence method is scoped to `pyproject.toml` reads
and live CLI invocations only), so its comparison classifies this fact as
insufficiently_verified rather than aligned. (current-state@v1#current-state-003,
classification: insufficiently_verified.)

## Compat-register: current census

There are currently exactly 49 YAML entry files in
`dev-docs/compat-register/` (the live register directory itself, not its
`examples/` subdirectory). This count is independently corroborated by
both topics: within the `current-state` topic alone, the count is
asserted but not independently cross-checked against a second artefact —
the `current-state` reconstruction's evidence method never touches
`dev-docs/compat-register/` at all, so its own comparison classifies this
as insufficiently_verified. (current-state@v1#current-state-006,
classification: insufficiently_verified.) The same count and distribution
are separately asserted, with independent corroboration, under the
`compat-system` topic (compat-system@v1#compat-system-003, classification:
aligned — see below), which this draft treats as the stronger-evidenced
source for the distribution figures that follow.

Counting each file's `kind:` field (anchored, one value per file) gives:
`compatible` = 40, `unsupported` = 6, `unexplained_mismatch` = 2,
`intentional_divergence` = 1, `extension` = 0 (sum = 49, matching the
total file count exactly). This distribution matches the register's own
id-prefix naming convention exactly (40 `LK-COMPAT-`, 6 `LK-UNSUP-`, 2
`LK-MISMATCH-`, 1 `LK-DIV-`, 0 `LK-EXT-` among the live files).
(compat-system@v1#compat-system-003, classification: aligned — the
independent reconstruction's own filename-prefix and `kind:`-field tables
give identical counts and independently states the two distributions
match 1:1 in every file.)

An unanchored substring search, `grep -l "kind: unexplained_mismatch"`,
currently returns 3 files rather than the anchored-field count of 2,
because the substring additionally appears somewhere other than the
`kind:` field itself in a third file
(`dev-docs/compat-register/LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml`, whose
own `kind:` field is `compatible`). This discrepancy is asserted but was
not independently cross-checked against a second artefact within the
`current-state` topic itself (out of that reconstruction's evidence
scope), so that topic's comparison classifies it as insufficiently_verified.
(current-state@v1#current-state-007, classification: insufficiently_verified.)
The underlying mechanism this discrepancy traces to — the register's
resolution lifecycle for `unexplained_mismatch` entries — is independently
and more strongly evidenced under the `compat-system` topic: resolving a
mismatch creates a new entry (carrying `resolves: <old-id>`) rather than
editing the original `kind:` field in place, and the original mismatch
entry is retained with only `resolved_into:`/`resolved_date:` added. This
mechanism has currently been exercised exactly twice, and both of the
register's two `unexplained_mismatch` entries
(`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`,
`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`) are currently resolved, with 0
presently open by this mechanism. (compat-system@v1#compat-system-005,
classification: aligned — the independent reconstruction confirms both
resolution pairs end-to-end: the old entries' `kind:` fields and original
evidence are unmodified, and the new entries carry fresh `resolves:`,
`status`, and verification fields.)

## Compat-register: schema and status lifecycle

The compat-register schema currently defines a closed `kind` taxonomy of
exactly five values — `compatible`, `extension`, `intentional_divergence`,
`unsupported`, `unexplained_mismatch` — each mapped to a fixed
`ledgerkit.relationship` value (`compatible`→`equivalent`,
`extension`→`superset`, `unsupported`→`subset`,
`intentional_divergence`→`incomparable`; `unexplained_mismatch` has no
fixed relationship stated in the schema). No live entry in the current
49-file register uses `kind: extension`/`relationship: superset`; this
pairing currently exists only in the schema's own documentation and in an
illustrative example file outside the live register.
(compat-system@v1#compat-system-001, classification: aligned — the
independent reconstruction's own cross-check of `relationship:` against
`kind:` across all 49 files confirms the identical mapping holding with
zero exceptions, and independently flags the same "no live `extension`
entry" gap.)

The schema currently defines a four-tier `status` field (`proposed`,
`self-verified`, `verified`, `final`) with an enforced authorship rule:
`status: verified` may currently only be written following a
separately-dispatched `compat-differential-tester` agent's own output,
never directly by the lead session, whereas `self-verified` records the
same session that implemented the feature confirming it with its own
command output. This rule currently holds in every one of the register's
23 non-`proposed` entries (14 carrying `status: verified` with a
`compat-differential-tester` verifier, 9 carrying `status: self-verified`
with a lead-session verifier). No entry in the current register carries
`status: final`. (compat-system@v1#compat-system-002, classification:
aligned — the independent reconstruction's own `verified_by:` text
analysis across all 23 entries confirms the identical authorship split
and count.)

The register's current `status` distribution is 26 `proposed`, 9
`self-verified`, 14 `verified`, 0 `final` (26+9+14=49, matching the total
file count exactly); the majority of entries (26/49, roughly 53%) have
not yet had an executable comparison run against them by an
independently-dispatched verifier — these 26 entries currently carry only
non-executable (`manual`/doc-link) evidence, consistent with the schema's
own gating expectation that executable evidence precede any status move
past `proposed`. (compat-system@v1#compat-system-004, classification:
aligned — the independent reconstruction reproduces the identical 26/9/14/0
counts and independently confirms that all 26 `proposed` entries currently
have zero `kind: executable` evidence items while all 23 non-`proposed`
entries have at least one.)

## Compat-register: entry-level test citations (sampled)

A sample of individual compat-register entries' cited test
identifiers has been checked against the live test suite for existence
(not for whether the cited test bodies actually assert the specific
behaviour each entry narrates — that question remains unchecked by this
evidence). Entries confirmed, with their cited test class(es) existing
exactly as named: `LK-COMPAT-ACCOUNTDIR-001` →
`tests/test_directives/test_directives.py::TestAccountDirective`
(compat-system@v1#compat-system-006, classification: aligned);
`LK-COMPAT-PARSER-TAG-COMMODITY-001` →
`tests/test_directives/test_directives.py::TestCommodityDirectiveTags`
(compat-system@v1#compat-system-007, classification: aligned);
`LK-COMPAT-QUERY-REGEX-EMPTYALT-001` → four test identifiers across
`tests/test_query/test_regex.py`, `tests/test_query/test_parser.py`, and
`tests/test_cli/test_cli.py` (compat-system@v1#compat-system-009,
classification: aligned); `LK-UNSUP-QUERY-DATE-002` →
`tests/test_query/test_parser.py::TestDateSpans::test_malformed_date_rejected`,
with its `implementation:` field currently an empty list, which the
schema currently permits for `kind: unsupported` entries describing
something not yet built (compat-system@v1#compat-system-010,
classification: aligned); `LK-COMPAT-PARSER-POSTINGDATE-001` →
`tests/test_tags.py::TestEffectiveDate` and `::TestEffectiveDate2`
(compat-system@v1#compat-system-011, classification: aligned).

One entry's citation count is currently disputed between the two
independent artefacts for this topic and is not resolved by either: for
`LK-COMPAT-QUERY-DEPTH-001` (ten distinct cited test identifiers across
four test files, per the assertion), the independent reconstruction's own
count of methods it attributes to this entry under
`TestQueryAstIntegration` is five rather than the assertion's four,
leaving the total at eleven rather than ten by the reconstruction's
reading. Neither figure has been adjudicated, since doing so would
require reading `tests/test_reports.py` directly, which was out of scope
for the comparison dispatch. (compat-system@v1#compat-system-008,
classification: partial.)

## Scope note

This draft deliberately excludes any fact outside the two topics'
permitted evidence (snapshots, assertions, implementation-reconstruction,
and implementation-comparison files for `current-state` and
`compat-system` only). It does not draw on ROADMAP.md, dev-docs/api-spec.md,
dev-docs/hledger-compatibility.md, any other dev-docs/*.md or docs/*.md
file, knowledge/*.md, CHANGELOG.md, CONTEXT.md, this governing plan
document, any other clean-room topic's artefacts, or any `ledgerkit/*.py`
source file. Findings surfaced only in a reconstruction or comparison
report with no corresponding frozen assertion (e.g. a reconstruction-only
observation lacking an assertion id to cite) are not included here, per
this draft's citation requirement that every fact trace to a
`<topic>@v1#<assertion-id>` reference.
