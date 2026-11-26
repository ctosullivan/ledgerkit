# Legacy reconciliation: docs/usage.md

Reconciling the real, pre-existing `docs/usage.md` against the already-committed
Phase 4 clean-room draft `dev-docs/clean-room/drafts/usage.md.clean-room-draft`
(built from the `reports-cli`, `checks`, and `current-state` topic snapshots @ v1,
repo revision `51881415a204af8908834ec602a54f6e1f67dbdd`).

Per Plan 29 §6.1: agreement between the legacy doc and the draft is not itself
evidence of truth. Every `supported` claim below is traced to a specific,
`verified`/`supported` Phase 3 assertion whose own Evidence section was checked
directly (code citation, named test, or a live-reproduced CLI run) — not merely to
the draft's prose. Claims outside the evidence this dispatch was given (the `-q`
query-language deep dive, `-c`/`--commodity-style` validation rules — these trace
to the `query-engine`/`tags`/`commodity-styling` topics, not `reports-cli`/
`checks`/`current-state`) are left unclassified-by-this-dispatch and unchanged,
since nothing in the permitted evidence contradicts them and re-deriving them
blind would be `docs-reconstructor`'s MODE 2, not this role's.

## Classification

### `supported` (kept, now cited)

1. **CLI invocable as `ledgerkit ...` or `python -m ledgerkit ...`, equivalently.**
   Traces to reports-cli-001 (`ledgerkit/cli.py:23`, `:126-130` — single flat
   `argparse.ArgumentParser`, `COMMANDS` tuple as `choices=`). Kept.
2. **`-f`/`--file` repeatable, merges multiple journals in order.**
   reports-cli-002 (`action="append"` on `-f`, cli.py:66-139) + reports-cli-003
   (`_resolve_files()`, cli.py:142-184, cross-checked against
   `tests/test_cli/test_cli.py:108-162`). Kept.
3. **Positional journal argument is a shorthand for a single `-f`; combining the
   two is a hard error; `$LEDGER_FILE` then `~/.hledger.journal` fallback.**
   reports-cli-003, directly — code and
   `test_f_flag_and_positional_errors`/`test_env_fallback_ledger_file`/
   `test_no_file_no_env_exits_with_message` all agree. Kept, cited.
4. **`-s`/`--strict` adds two checks (`accounts`, `commodities`) beyond what runs
   by default.** checks-001 (`STRICT_CHECK_NAMES`, checks.py:28) + reports-cli-015
   (strict forwarded to `check` via `strict=args.strict`). Kept, but see
   `stale_or_contradicted` #1 below — the *default* set this adds to was wrong.
5. **`check` check-names table: `parseable`, `autobalanced`, `accounts`,
   `commodities`, `payees`, `ordereddates`, `uniqueleafnames` and their one-line
   descriptions.** checks-001 through checks-007, each description verified
   against the cited function and test (e.g. `uniqueleafnames` against
   checks-007/`test_duplicate_leaf_fails`). Kept — but see
   `stale_or_contradicted` #2 (missing the eighth, `assertions`).
6. **`check`: silent success (no stdout), errors to stderr + exit 1 on failure.**
   reports-cli-015 (cli.py:253-291, directly: no stdout write in the success
   path) + current-state-008 (live-reproduced: `check -f sample.journal` exits 0
   with zero bytes of stdout, re-confirmed with `-v`). Kept, cited.
7. **`print` supports `-q`; a matching transaction is printed whole (every
   posting, not just the matching one).** reports-cli-009, directly —
   `test_print_query_filters_whole_transactions` asserts the *other* posting on
   a matched transaction is also present. Kept.
8. **`balance`/`register`/`accounts`/`stats`: one-line descriptions.** Broadly
   supported by reports-cli-004/006/008/011 but each was *too* terse to surface
   now-documented, user-relevant behaviour (see `stale_or_contradicted` #3-6) —
   kept as the opening sentence of each section, expanded underneath.
9. **`depth:N`/`depth:REGEX=N` truncates/aggregates for `balance`/`register`/
   `accounts`, never excludes; `print` ignores `depth:` entirely; `stats`
   uniquely *excludes* rather than aggregates.** This is the one already-present
   claim in the legacy doc's `-q` section that *is* inside this dispatch's
   evidence (overlaps reports-cli-004/006/008/012, and matches
   `knowledge/EDGE_CASES.md` EC-017's "RESOLVED Stage C Phase 5" note exactly —
   the legacy doc already reflects the fixed, current behaviour, not the old
   exclusion bug). Kept verbatim; this is a case where the legacy doc was
   already right and the draft doesn't restate it in this much detail, so it's
   folded in as-is rather than replaced.
10. **Python library snippet: `ledgerkit.load()`, `journal.transactions`,
    `journal.accounts()`/`.stats()` exist and return data (not formatted
    strings).** Supported by reports-cli-004/006/011 and corroborated by the
    already-hand-authored `docs/python-api.md` (read for cross-check only, not
    treated as primary evidence for this dispatch's three topics). Kept, but see
    `stale_or_contradicted` #7 for the specific type annotations.

### `stale_or_contradicted` (fixed in the published doc)

1. **"By default ledgerkit checks that every transaction balances (the
   `autobalanced` check)."** False by omission: the default (basic) tier is
   *three* checks — `parseable`, `autobalanced`, **and `assertions`**
   (checks-001, `BASIC_CHECK_NAMES = ("parseable", "autobalanced",
   "assertions")`, checks.py:27) — run on *every* command, not `check` alone.
   The doc never mentioned `assertions` or `-I`/`--ignore-assertions` anywhere.
   Fixed: rewrote the `-s`/`--strict` section to name all three default checks
   and document `-I`.
2. **Check-names table omitted `assertions` entirely**, even though it is a
   real, nameable check (`ledgerkit check assertions -f file.journal` is used
   as the canonical example in both reports-cli-015 and checks-006) and is one
   of only eight entries in `_CHECK_FN`'s registry (checks-008). Fixed: added
   the row, with a `Tier` column added to the table (basic/strict/other) since
   checks-001 makes the tier structure load-bearing (which checks run when).
3. **"Specifying the journal file" never mentioned the `check`-command
   exception.** reports-cli-003 states this explicitly as "the one exception
   to this rule" and current-state-008 reproduces the concrete failure mode
   live: `ledgerkit check sample.journal` (no `-f`) does *not* check that file —
   the positional is read as an unrecognised check name, and the command fails
   with "no journal file specified." The legacy doc's own `check` examples all
   happened to use `-f` correctly, so no example was wrong, but the rule itself
   was never stated and a user following the general "positional = file"
   pattern from earlier in the doc would be misled. Fixed: added an explicit
   callout paragraph.
4. **`balance`/`register`/`accounts`/`print`/`stats` sections were one-line
   stubs that omitted verified, user-relevant behaviour**: `balance`'s
   ANSI-red negatives, zero-row omission, and the unconditional depth-0 `"..."`
   row (reports-cli-005); `register`'s fixed-width columns, date/description
   blanking, account abbreviation algorithm, and the "running balance is never
   re-grouped per account" invariant (reports-cli-006/007); `accounts`'
   genuinely-empty-output-on-no-match behaviour, contrasted with `balance`
   (reports-cli-008); `print`'s exact output format and — materially — that it
   **drops inline `;` comments entirely**, unlike ledgerkit's own round-trip
   serialiser (reports-cli-009/010); `stats`' `-1`/`-v` modes and the
   depth-*exclusion* (not aggregation) quirk unique to `stats`
   (reports-cli-011/012). Fixed: expanded each section with the verified detail,
   cited.
5. **Top-level `Syntax` block (`ledgerkit [-f FILE]... [-s] <command>
   [args...]`) and the whole document never mentioned `--version`, `-v`/
   `--verbose`, `-1`, `-o`/`--output-file`, or `-I`/`--ignore-assertions`** —
   all five are real, current, documented-in-`--help` global flags
   (current-state-004, reports-cli-002). Fixed: updated the synopsis and added
   an "Other options" table for the five previously-undocumented flags.
6. **No mention that subcommand-level `--help` doesn't exist** (e.g.
   `ledgerkit balance --help` prints the identical top-level help, not a
   balance-specific one) — current-state-005/reports-cli-001, directly
   reproduced by a live for-loop over all six subcommands. Fixed: added a note
   under "Getting Help."
7. **Python snippet's type comments were inaccurate**: `balances =
   journal.balance()  # dict[str, Decimal]` is wrong — reports-cli-004 states
   the actual shape is a `BalanceResult` keyed *account → commodity → Decimal*
   (a nested nested mapping, not a flat one), and `docs/python-api.md` (already
   hand-authored, cross-checked) already calls it `BalanceResult (behaves like
   dict)` rather than a bare `dict[str, Decimal]`. Fixed: corrected the type
   comments for `accounts()`/`balance()`/`register()` to match
   `python-api.md`'s and reports-cli-004's actual shapes.
8. **No "Exit codes" section**, despite reports-cli-003/-008/-015 and
   current-state-008 jointly fully specifying this. Added as new content (not a
   correction of a wrong claim, but a gap directly closed by this dispatch's own
   evidence).

### `rationale_requiring_verification`

None found that required escalation. The one candidate — *why* `print` omits
inline comments (deliberate v1 scope vs. an unnoted gap) — is reports-cli-010's
own escalated open question: the **behavioural fact** (comments are dropped) is
`verified`/`supported` and is documented in the published doc as a plain fact;
the **design-intent** question behind it is explicitly left open by the
domain-skeptic review and is not something `knowledge/*.md` resolves either (no
`DECISIONS.md`/`ANTIPATTERNS.md` entry addresses `print` and inline comments).
Not asserted either way in `docs/usage.md` — stated as a confirmed limitation
only, intent left unstated. This is the one explicit open question carried
through from Phase 3/4.

### `useful_example`

- The existing `print` worked example (`Opening balance` / `Supermarket`
  transactions with aligned amounts) illustrates the described format
  correctly and was kept verbatim — not independently re-verified byte-for-byte
  against a live run (that would require re-deriving the exact padding), but it
  is consistent with reports-cli-009's stated algorithm and was not contradicted
  by anything in the permitted evidence, so it stays as an illustration rather
  than as a cited fact.
- The new `stats` sample output block is **not** a legacy artefact — it's
  current-state-008's literally-reproduced live output, substituted in as a
  grounded example (the legacy doc had no example output for `stats` at all).

### `obsolete`

None found — no claim in the legacy `docs/usage.md` described functionality
that has been removed outright; every stale claim above was an *omission* or an
*inaccuracy* about still-existing functionality, not a description of something
gone.

## Citations dropped from the clean-room draft during merge — checked

The draft's own citation style (`(topic@v1#id)`) was carried into the published
`docs/usage.md` verbatim wherever draft prose or draft-derived facts were
folded in, per this mode's "preserve structure, not only facts" requirement.
Every citation the draft attaches to a fact used in this merge survives into
`docs/usage.md`; sections of the draft not used here (the full `--help` block
reproduction, the `balance_from_spec`/Python-API-only reports-cli-013,
`journal_to_text`'s directive-exclusion caveat reports-cli-014, which belong to
`python-api.md`/`architecture.md` rather than the CLI usage guide) were left
for whichever future dispatch reconciles those documents, not silently dropped
from this one as if they'd been considered and rejected here.

## Result

`docs/usage.md` was rewritten in place (not restructured — the original section
order and headings are preserved) with the fixes listed above. Net effect:
eight omissions/inaccuracies corrected, one new "Exit codes" section added, all
newly-added or corrected factual claims cited to a specific `reports-cli@v1`/
`checks@v1`/`current-state@v1` assertion ID. The `-q`/`--query` deep-dive and
`-c`/`--commodity-style` sections were left unchanged — they fall outside this
dispatch's permitted evidence (`query-engine`/`tags`/`commodity-styling`
topics) and nothing in the evidence given here contradicts them.
