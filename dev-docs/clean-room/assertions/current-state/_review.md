<!-- producer: domain-skeptic | role: REVIEW | topic: current-state | review-dispatch: cs-review-01 | date: 2026-10-03 -->
# Review note: current-state assertions (001–008)

## Scope
Reviewed `current-state-001.md` through `current-state-008.md`. Permitted
evidence used: `pyproject.toml` content; live re-runs of `git tag --list`,
`git describe --tags --always`, `git log --oneline -1`, `python -m
unittest discover -s tests -t . -v`, `python -m ledgerkit --help`, `python
-m ledgerkit <subcommand> --help` for all six subcommands, `python -m
ledgerkit stats tests/fixtures/sample.journal`, `python -m ledgerkit check
-f tests/fixtures/sample.journal` (and the bare-positional variant to
confirm its documented failure mode), and `ls`/`grep -h`/`grep -l` counts
against `dev-docs/compat-register/*.yaml` filenames and `kind:` lines
only (no YAML content was opened). No legacy documentation, ROADMAP,
README, CHANGELOG, CONTEXT, `docs/`, `dev-docs/architecture.md`,
`dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md`,
`dev-docs/retros/`, `dev-docs/planning/`, `knowledge/`, individual
compat-register YAML content, or any `ledgerkit/*.py` source was read.

## Forward-looking-content check
Scanned all eight files for forward-looking language (`will`, `future`,
`propose`, `upcoming`, `TODO`, `roadmap`, etc.). None found. All eight
assertions are phrased as "right now" / "currently" observations, as
required for this factual-only topic. No escalation needed on this point.

## Checked and confirmed as-is (no changes needed)
- **001** (`pyproject.toml` metadata): re-read the file directly; `version
  = "1.0.0.dev1"`, `requires-python = ">=3.8"`, `dependencies = []`, and
  the `pandas` optional-dependency block are all verbatim as cited.
  Supported.
- **002** (git tags / describe): re-ran `git tag --list` and `git
  describe --tags --always`; output byte-for-byte matches
  (`v1.0.0`, `v1.0.0.dev1`, `v1.0.0.dev1-60-g5188141`), and `git log
  --oneline -1` confirms HEAD is `5188141`. Supported.
- **003** (test suite summary): re-ran `python -m unittest discover -s
  tests -t . -v`; confirmed `Ran 935 tests in 0.775s` / `OK (skipped=29)`
  / exit code `0`, matching the cited figures exactly. (Noted in passing,
  not a finding: the unittest summary line is written to stderr
  unbuffered while per-test stdout prints are buffered, so in a combined
  `2>&1` capture the "OK" line can appear before trailing buffered
  stdout from tests that exercise the CLI — this doesn't affect the
  truth of the asserted counts, which are read directly off the summary
  line itself.)
- **004** (top-level `--help` subcommand list): re-ran `python -m
  ledgerkit --help`; usage line and six-subcommand set
  (`balance,register,accounts,print,stats,check`) match verbatim.
  Supported.
- **005** (subcommand `--help` identical to top-level): re-ran all six
  `python -m ledgerkit <cmd> --help` invocations; hashed each output
  block and confirmed all six are byte-identical to each other and to
  the bare `--help` output from 004 (`diff` reported no differences).
  Supported, and this also cross-validates 004.
- **006** (compat-register `kind:` counts): re-ran `ls
  dev-docs/compat-register/*.yaml | wc -l` (49) and `grep -h "^kind:"
  ... | sort | uniq -c` (compatible=40, unsupported=6,
  unexplained_mismatch=2, intentional_divergence=1, summing to 49).
  Exact match. Supported.
- **007** (unanchored-grep discrepancy and overlap explanation): re-ran
  the unanchored `grep -l "kind: unexplained_mismatch"` (3), the
  per-kind unanchored counts (compatible=41, intentional_divergence=1,
  unsupported=6, unexplained_mismatch=3), and the overlap isolation via
  `uniq -d`, which reproduced the identical two filenames
  (`LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml`,
  `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml`). Exact match. Supported,
  and its "Open questions" field is honest about what it can't determine
  without reading file content (out of scope here too).

## Finding resolved: current-state-008
The draft statement claimed running `stats` **and** `check` against the
sample journal both "succeed... and produce[] non-empty, well-formed
tabular/report output," citing only `stats` output as the example. I
checked this directly:

- `python -m ledgerkit stats tests/fixtures/sample.journal` → exit `0`,
  non-empty tabular output (matches the draft's cited figures exactly).
- `python -m ledgerkit check -f tests/fixtures/sample.journal` → exit
  `0`, but **zero bytes of stdout** — a passing `check` run is silent by
  design. Re-confirmed with `-v` added; still empty.

So the draft's claim that `check` also "produces non-empty... output" on
success is false as written — it conflated `check`'s *successful exit*
with `stats`'s *non-empty report output*, when only `stats` has the
latter property. I also found, while isolating the correct invocation,
that `python -m ledgerkit check tests/fixtures/sample.journal` (passing
the path as a bare positional instead of via `-f`) does not validate that
file at all — per the CLI's own `--help` text, `check`'s positional
argument is read as a check *name*, not a file shorthand — so that
invocation instead fails with `no journal file specified`. This is a
real, non-obvious edge case the original (apparently incidental)
evidence-gathering for 008 didn't surface, since it never says how
`check` was actually invoked.

I resolved this myself (no escalation needed — fully researchable within
permitted evidence) and rewrote `current-state-008.md`: the `Statement`
now distinguishes `stats`'s non-empty output from `check`'s silent
success, the `Evidence` section cites both commands' exact-reproduced
output (and the bare-positional failure mode as a note), `Justification`
and `Examples` were updated to match, a `Counterexamples` entry was added
naming `check`'s silent success as the counterexample to the
"both produce non-empty output" reading, and the stale `Open questions`
entry (which said the invoking journal path "was not isolated") was
closed out since re-running directly against `tests/fixtures/sample.journal`
reproduced the cited figures, confirming that was the source file.
`Evidence-support state` remains `supported` (now on a corrected,
fully-evidenced claim) and `Status` remains `verified`.

## Contradictions search
Checked 004 vs. 005 (consistent, 005 explicitly depends on 004's
baseline and both are now independently confirmed), and 006 vs. 007
(007 explicitly reconciles its own apparent discrepancy against 006's
anchored counts, and I reproduced both counts and the named overlap
files, so the explanation holds). No other cross-assertion contradiction
found among the eight files.

## Escalations
None. Every finding was resolvable with the permitted evidence; nothing
is being escalated to the lead as a genuine unresolved ambiguity.

## Files touched
- Edited: `dev-docs/clean-room/assertions/current-state/current-state-008.md`
  (Statement, Evidence, Justification, Examples, Counterexamples, Open
  questions updated; Evidence-support state and Status unchanged at
  `supported`/`verified` since the corrected claim is fully evidenced).
- Added: this file,
  `dev-docs/clean-room/assertions/current-state/_review.md`.
- No other assertion files required changes.
