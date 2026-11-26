<!-- producer: domain-skeptic | mode: comparison | topic: current-state | dispatch: cs-comparison-01 | dispatch-timestamp: 2026-11-14T00:00:00Z | date: 2026-11-14 -->
# Implementation comparison: current-state

**Role:** domain-skeptic
**Mode:** comparison
**Topic:** current-state
**Dispatch id:** cs-comparison-01
**Date:** 2026-11-14

## Inputs

- Snapshot: `current-state@v1` (`dev-docs/clean-room/snapshots/current-state-v1.md` +
  `.sidecar.json`), frozen 2026-10-02T16:50:03Z at repository revision
  `51881415a204af8908834ec602a54f6e1f67dbdd`, containing 8 assertions
  (`current-state-001` … `current-state-008`).
- As-built reconstruction: `dev-docs/clean-room/implementation-reconstruction/current-state.md`,
  produced by `implementation-reconstructor`, dispatch timestamp
  2026-10-02T16:54:48Z, dated 2026-10-03. Evidence method: model-blind,
  source-code-blind — exclusively `pyproject.toml` reading plus live
  `python -m ledgerkit ...` CLI runs against `tests/fixtures/sample.journal`.
  No `ledgerkit/*.py` source, no git history, no `dev-docs/compat-register/`,
  and no test-suite execution are within this report's evidence base.

No source, tests, or legacy documentation were read directly by this
dispatch; this comparison is strictly between the two named artefacts.

## Per-assertion classification

| Assertion | Classification | Basis |
|---|---|---|
| current-state-001 (pyproject.toml metadata: version, requires-python, deps) | **aligned** | Reconstruction §1 quotes `name`, `version = "1.0.0.dev1"`, `requires-python = ">=3.8"`, `dependencies = []`, and `optional-dependencies.pandas = ["pandas>=1.3"]` verbatim — matches the assertion's claims exactly. |
| current-state-002 (two git tags; HEAD 60 commits ahead of `v1.0.0.dev1` per `git describe`) | **insufficiently_verified** | The reconstruction's evidence method is explicitly scoped to `pyproject.toml` + live CLI runs; it contains no git-history or tag inspection at all. There is nothing in the reconstruction to agree or disagree with this assertion. |
| current-state-003 (unittest discover: 935 tests, 29 skipped, 0 failed/errored, `OK (skipped=29)`) | **insufficiently_verified** | The reconstruction never runs the test suite — its own scope statement (§"Evidence method") and its closing scope-discipline section (§6) list only `pyproject.toml` reads and CLI invocations against the fixture. No comparison data exists. |
| current-state-004 (`--help` lists exactly six subcommands: balance, register, accounts, print, stats, check, with the full usage/options block) | **aligned** | Reconstruction §2 quotes the *exact same* `--help` output verbatim, word-for-word identical to the block quoted in the assertion, including the `{balance,register,accounts,print,stats,check}` choice set and every option line. |
| current-state-005 (all six `<cmd> --help` invocations print byte-identical top-level help; no per-subcommand help exists) | **aligned** | Reconstruction §2 and finding §5.10 independently reach the same conclusion ("there are no per-subcommand parsers... `check --help` prints the exact same top-level usage block"), and explicitly frames it as a general architectural fact (single flat `argparse` parser for all six commands), not limited to one command. Note on evidence breadth: the reconstruction's narrative explicitly demonstrates this only for `check --help` by name, whereas the assertion's own evidence is a for-loop over all six subcommands; the two are consistent in direction and conclusion, but the reconstruction's own evidence is narrower than the assertion's. This is noted for completeness, not as a divergence — no case of a subcommand producing a *different* help block appears in either artefact. |
| current-state-006 (49 YAML files in `dev-docs/compat-register/`; `kind:` counts 40/6/2/1) | **insufficiently_verified** | The reconstruction never touches `dev-docs/compat-register/` — it is out of its stated evidence scope (pyproject.toml + CLI runs only). No comparison data exists. |
| current-state-007 (unanchored `grep -l "kind: unexplained_mismatch"` returns 3, one more than the anchored count, due to substring overlap in two specific files) | **insufficiently_verified** | Same as current-state-006 — `dev-docs/compat-register/` is entirely outside the reconstruction's evidence base. No comparison data exists. |
| current-state-008 (`stats` succeeds with non-empty tabular output; `check -f ...` succeeds silently with zero stdout; bare positional for `check` is treated as a check name, not a file, and fails without `-f`/`$LEDGER_FILE`) | **aligned** | Reconstruction §3 ("stats", "check") independently reproduces every specific claim: the same `stats` field set and values for this fixture (`Txns : 5 (0.2 per day)`, `Accounts : 6 (depth 3)`, `Commodities : 1`, and even the same `(987 days ago)` figure for `Last txn`); `check -f tests/fixtures/sample.journal` exits `0` with zero stdout/stderr ("fully silent success"); and the bare-positional case for `check` fails with the identical error string `ledgerkit: no journal file specified; use -f FILE or set $LEDGER_FILE`, exit `1`, because the positional is consumed as a check name rather than a file path. No divergence found between the two artefacts on any of these points. |

### Classification breakdown

- **aligned:** 4 (001, 004, 005, 008)
- **partial:** 0
- **conflicting:** 0
- **not_implemented:** 0
- **insufficiently_verified:** 4 (002, 003, 006, 007)

No assertion in this snapshot was found to directly conflict with the
reconstruction's findings, and none describes behaviour the
reconstruction shows to be absent. The four `insufficiently_verified`
findings are not close calls — they are topics (git tag/commit state,
test-suite results, compat-register file census) that the
reconstruction's evidence method structurally never touches, since its
scope was deliberately narrowed to package metadata plus live CLI
behaviour. This is a genuine coverage gap between the two artefacts, not
a sign of disagreement.

## Reconstruction findings with no corresponding assertion

Per the comparison template's "do this in both directions" instruction,
the following reconstruction findings describe real, directly-observed
behaviour that none of the 8 frozen assertions address at all. These are
not classified above (there is no assertion to compare them against) but
are named here as a knowledge-base coverage gap for the lead to act on,
not resolved or adjudicated by this report:

- `check`'s positional-argument/file-shorthand inconsistency relative to
  every other command (reconstruction §5.1) — partially adjacent to
  current-state-008's note about the bare-positional failure mode, but
  current-state-008 doesn't generalize it as a cross-command
  inconsistency the way the reconstruction does.
- `-c` (commodity-style override) silently no-ops when its symbol
  doesn't match any commodity in the file, with no warning (§5.3).
- `print` drops header-line inline comments on round-trip — a real
  data-loss gap (§5.4).
- ANSI color codes (red, for negative amounts in `balance`/`register`)
  are emitted unconditionally, including to non-TTY output, with no
  observed `--color`/`--no-color` flag (§5.5).
- `register`'s account-name abbreviation behaviour (e.g.
  `equity:opening-balances` → `eq:opening-balances`) was observed but its
  trigger condition was not characterized (§5.6, explicitly left open by
  the reconstructor as unresolved from permitted evidence).
- Strict-mode (`-s`) error-reporting completeness across multiple
  violations in a single file was not established (§5.7).
- `-I` (ignore-assertions) was never actually exercised against
  assertion-bearing data, since the fixture contains none (§5.8).
- The `pyproject.toml` classifiers claim `Development Status :: 5 -
  Production/Stable` despite the `1.0.0.dev1` pre-release version string
  — a direct internal metadata inconsistency (§1, §5.9).

None of these are adjudicated here — per this mode's hard rule, neither
artefact is revised to force agreement, and a real correction (adding
assertions to cover these, if warranted) means re-running the
assertion-research step for a new snapshot version, not editing the
frozen v1 snapshot or this comparison report.

## Hard-rule note: alignment is not verification

The four `aligned` classifications above (001, 004, 005, 008) establish
only that the reconstruction's independently-gathered, live evidence
currently matches what the snapshot asserts — not that the underlying
claims are the "right" ones in any normative sense. All eight assertions
in this topic are `observed_behaviour`/`observed_behaviour` kind (not
`rule`/`invariant`/`proposed_policy`), so this distinction is narrower
here than it would be for a policy-type assertion, but it still holds:
e.g., `aligned` on current-state-005 confirms that *today*, no
subcommand has its own help text — it does not certify that this is
desirable CLI design, only that both artefacts observed the same current
fact independently.

## Findings requiring action

None of the four `insufficiently_verified` findings (002, 003, 006, 007)
rise to the level of a `conflicting` or `not_implemented` finding
requiring a correctness decision — they are coverage gaps in the
reconstruction's evidence method (by design, per its stated scope), not
disagreements. No action is required on the snapshot itself. The
reconstruction-findings-with-no-assertion list above is a candidate
input for a future assertion-research dispatch on this topic, but that
is a recommendation for the lead, not something this report resolves.
