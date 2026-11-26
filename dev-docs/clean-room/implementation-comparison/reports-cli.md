---
role: domain-skeptic
mode: comparison
topic: reports-cli
dispatch-id: plan29-phase-comparison-reports-cli-20261114
dispatch-timestamp: 2026-11-14T00:00:00Z
date: 2026-11-14
---

# Implementation comparison: `reports-cli` — snapshot `reports-cli-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/reports-cli-v1.md` +
  `reports-cli-v1.sidecar.json` (15 assertions, frozen
  2026-10-02T16:50:03Z, repository revision
  `51881415a204af8908834ec602a54f6e1f67dbdd`).
- The 15 frozen assertion files under `dev-docs/clean-room/assertions/
  reports-cli/` (reports-cli-001 through reports-cli-015; -005, -010, and
  -011 each carry a prior domain-skeptic REVIEW-mode correction dated
  2026-10-03, already folded into their frozen `Statement`/`Evidence`/
  `Evidence-support state` fields — see that directory's own
  `_review.md`).
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/reports-cli.md`
  (dispatch `plan29-phase-reports-cli-20261003`, 2026-10-03T00:00Z,
  model-blind, evidence basis: `ledgerkit/cli.py` full file,
  `ledgerkit/reports.py` full file, `ledgerkit/writer.py` full file,
  `tests/test_cli/test_cli.py`, `tests/test_reports.py`,
  `tests/test_writer.py`, plus live `python -m ledgerkit ...` CLI runs
  against fixtures and two constructed scratch journals — no access to
  the snapshot or assertions).

**Method.** Neither artefact was revised to force agreement. No source
or test file was read directly by this dispatch — comparison mode
compares the two clean-room artefacts only; all findings below rest on
what each artefact itself states. No live command was run by this
dispatch either; where the reconstruction's own live-output transcripts
are cited below, they are quoted from that report, not re-executed here.

## Classification summary

| Assertion | Kind | Classification |
|---|---|---|
| reports-cli-001 | definition | aligned |
| reports-cli-002 | definition | aligned |
| reports-cli-003 | rule | aligned |
| reports-cli-004 | state_transformation | aligned |
| reports-cli-005 | state_transformation | aligned |
| reports-cli-006 | invariant | insufficiently_verified |
| reports-cli-007 | state_transformation | aligned |
| reports-cli-008 | definition | aligned |
| reports-cli-009 | rule | aligned |
| reports-cli-010 | boundary | aligned |
| reports-cli-011 | definition | aligned |
| reports-cli-012 | rule | aligned |
| reports-cli-013 | boundary | aligned |
| reports-cli-014 | state_transformation | partial |
| reports-cli-015 | state_transformation | aligned |

**13 aligned / 1 partial / 1 insufficiently_verified / 0 conflicting /
0 not_implemented.**

No conflicting or not_implemented findings — nothing in the independent
reconstruction contradicts an assertion, and nothing an assertion claims
exists was found by the reconstruction to be absent. The one `partial`
(reports-cli-014) and the one `insufficiently_verified`
(reports-cli-006) are both reach gaps — the reconstruction's own
evidence simply does not extend far enough to independently confirm one
specific, named sub-claim in each — not disagreements.

## Per-assertion notes

**reports-cli-001** (six subcommands via a flat positional `choices=
COMMANDS`, no argparse subparsers tree). Reconstruction §2 independently
quotes the identical `--help` usage line (`{balance,register,accounts,
print,stats,check} [journal ...]`) and independently states `COMMANDS =
("balance", "register", "accounts", "print", "stats", "check")` is "a
module-level tuple in `cli.py`, used both as argparse `choices` and as
the dispatch switch in `main()`." It also independently confirms the
no-subparsers structure from a different angle than the assertion's own
evidence (`-h` on `balance` producing the identical top-level usage,
per the assertion): the reconstruction instead live-confirms an
unrecognised command (`ledgerkit frobnicate`) is rejected by argparse's
own `choices` validation with exit code 2, before `main()` ever runs —
a different experiment reaching the same underlying fact (no
per-subcommand parser exists). Aligned.

**reports-cli-002** (the nine global flags, uniform across all
commands). Reconstruction §2's verbatim `--help` transcript matches the
assertion's own quoted flag list token-for-token, including the exact
help strings for `-q`/`-c`. Aligned.

**reports-cli-003** (four-tier file-resolution precedence; `-f`+
positional is a hard error; `check`'s positional arguments are check
names, never a journal path). Reconstruction §2 independently quotes
the `--help` positional-argument help text verbatim — "journal: Journal
file (shorthand for `-f`; all commands except check), or check names
(check command only)" — matching the third clause of the assertion
exactly, and §6 independently names "`_resolve_files`'s four-tier
precedence (`-f` > positional > `$LEDGER_FILE` > `~/.hledger.journal`)
and its two `SystemExit(1)` error paths," matching the first two
clauses exactly. Aligned.

**reports-cli-004** (`balance()`'s two return modes: flat dict by
default, `list[BalanceRow]` with implicit parent accounts and
`is_subtotal` when `tree=True`). Reconstruction §5.2 independently
confirms the default-mode shape ("Flattens `reports.balance()`'s
`dict[account, dict[commodity, Decimal]]`..." — this is what the CLI's
`balance` command consumes). Reconstruction §3 independently confirms,
from direct reading of `_build_balance_tree`'s construction site, that
`BalanceRow` carries exactly the fields the assertion names
(`account`, `depth` as colon-count, `amounts`, `is_subtotal: bool`) and
that `_build_balance_tree` is reports.py's sole tree-mode builder. The
reconstruction does not independently re-exercise the specific semantic
claims that `is_subtotal` is `True` only for *pure*-parent rows, that
amounts are aggregated self+descendants, or that rows are sorted
alphabetically — these are elaborations the reconstruction's evidence
doesn't retest, not claims it contradicts. Aligned, with that reach
caveat noted.

**reports-cli-005** (`balance` CLI output format: right-aligned amount
then account on the account's last row; dashed separator sized to the
widest string; zero-net rows omitted except the depth-0 `"..."` row,
shown unconditionally regardless of its own value; negative amounts
ANSI-red-wrapped after padding). Reconstruction §5.2 independently
reproduces essentially the same analysis, including a live transcript
of `-q "depth:0" balance` showing the bare `"0"` ellipsis-and-total
lines, an independent restatement of the in-code rationale for padding
before colouring ("padding must happen first because escape codes have
non-zero string length but zero display width"), and an independent
restatement of the `max([20] + ...)` list-literal rationale for
avoiding a `TypeError` on an all-zero-match `-q` filter — live-confirmed
there too (`-q "acct:doesnotexist" balance` exits 0 with a bare `"0"`
total, not a crash). The reconstruction's live checks do not include the
specific nonzero-`"..."` scenario the assertion's own REVIEW-mode
correction added (`-q "acct:food depth:0"` on `filtered.journal`
producing a nonzero `"..." = £159.00"` row) — it stops at the unfiltered
`depth:0` case, which nets to zero. This is an unretested extension of
the same rule, not a contradiction of it (the underlying code condition
the reconstruction cites, `qty != 0 or acct == "..."`, is literally the
same unconditional-inclusion rule the assertion's correction rests on).
Aligned.

**reports-cli-006** (`register()`'s `running_balance` is a single
cumulative sum across every row in output order, never grouped or
re-aggregated by account, even when `depth` clips several postings'
account names to the same displayed string). **Insufficiently
verified.** The reconstruction's only touch on `RegisterRow` is a
field-level inventory from its construction site (§3: "constructed in
`register()` as `RegisterRow(date=..., description=..., account=...,
amount=..., running_balance=...)`"), which confirms the field exists but
says nothing about its accumulation mechanics. §5.3's live-traced
`register` CLI behaviour covers date/description blanking, account
abbreviation, and amount/running-balance formatting widths — it does
not exercise or discuss depth clipping's interaction with
`running_balance` at all (no `-q "depth:N" register"` scenario is
mentioned anywhere in the reconstruction). Nothing in the reconstruction
contradicts the assertion's invariant, but nothing in it independently
confirms the specific claim either — the two artefacts simply do not
overlap on this point, which is the reconstruction's reach, not a
disagreement. Honestly flagged as insufficiently verified rather than
forced into `aligned`.

**reports-cli-007** (`register` CLI line format: fixed-width date(10)/
description(21)/abbreviated-account(22)/amount(12)/running-balance(13);
date/description blanked on continuation rows of the same (date,
description) pair; account abbreviation via progressive colon-component
shortening, never the last component; zero running balance as bare
`"0"`). Reconstruction §5.3 independently restates every one of these
mechanics, including the identical worked example
(`equity:opening-balances` → `eq:opening-balances`, confirmed live) that
the assertion itself uses as its own Example. Aligned.

**reports-cli-008** (`accounts` prints a bare sorted list with no
separator/zero-total convention; a non-matching query produces genuinely
empty output, unlike `balance`). Reconstruction §5.6 independently
states the identical conclusion, citing the identical test
(`TestQueryFlag.test_multi_term_query`) and its identical in-test
comment ("accounts' CLI output has no separator/zero-total convention
(unlike balance) -- genuinely empty here"). Aligned.

**reports-cli-009** (`print`'s header/posting line format; `-q`
matching is whole-transaction, not per-posting; `print` ignores `depth:`
entirely). Reconstruction §5.4 independently quotes the identical
in-code comment ("print deliberately uses only query_ast, never
query_depth, matching hledger's own print (which ignores depth: entirely
..."), cites the same two tests
(`test_print_query_filters_whole_transactions`,
`test_print_ignores_depth_entirely`), and live-reproduces both: a
query-filtered `print` still shows a matched transaction's non-matching
posting in full, and `-q "depth:1" print` is identical to unfiltered
`print` with full unclipped account names. The reconstruction's own
limitation #3 independently uses the phrase "just the account name on
its own line" for an elided posting under `print`, matching the
assertion's own "or just the account if elided" clause verbatim in
substance. Aligned.

**reports-cli-010** (`print` drops every inline comment, header- and
posting-level, unlike `writer.transaction_to_text()`'s lossless
round-trip; design intent is an open, unresolved question). Reconstruction
§5.4 independently runs essentially the same experiment the assertion's
own REVIEW-mode correction used — a constructed journal with both a
header-level and a posting-level inline comment, run through `print` and
through `writer.journal_to_text()` — and reaches the identical
behavioural conclusion (both comments vanish under `print`, both survive
under `writer.py`). Its own limitation #1 independently states "There is
no in-code comment in `cli.py` acknowledging this as a deliberate
simplification," landing on the same unresolved-intent boundary the
assertion's own "Open questions" field escalates, without either
artefact resolving it. Aligned on the behavioural claim; the intent
question remains open in both, independently, which reinforces rather
than resolves the assertion's own escalation.

**reports-cli-011** (`JournalStats` holds only deterministic fields;
elapsed time/txns-per-second are CLI-layer-only; `-v` only affects the
`Commodities` line; `-1` prints one tab-separated line). Reconstruction
§5.5 independently restates the deterministic/CLI-computed split, and
live-confirms both flag behaviours with its own transcripts (`-v stats`
→ `"Commodities : 1 (£)"` vs. plain `stats` → `"Commodities : 1"`; `-1`
→ `"1.0.0.dev1\t/path/.../filtered.journal\t0.02 s elapsed\t247
txns/s"`), matching the assertion's own field-order claim. The
reconstruction does not independently re-verify the exact "12 labeled
lines" count the assertion's own REVIEW-mode note corrected (an internal
arithmetic fix to that assertion's `Evidence` field, not a claim in its
`Statement`); this narrower point is simply untouched, not contradicted.
Aligned.

**reports-cli-012** (`stats` is the sole report function where
`_query_depth` *excludes* accounts deeper than the limit from
`account_count`/`account_depth`, via `account_excluded_by_depth`, rather
than clip-and-aggregate like `balance`/`register`/`accounts`).
Reconstruction §5.5 independently states the identical contrast
(`account_excluded_by_depth` vs. `clip_account_name`), independently
cites the docstring's claim that this is a "genuine, source-confirmed
exception" tied to a comment in hledger's own `Ledger.hs`, independently
flags that it did not itself verify that upstream citation (matching the
assertion's own caveat precisely), and live-reproduces the identical
scenario (`-q "depth:2" stats -f filtered.journal` → `"Accounts : 2
(depth 2)"`). Aligned.

**reports-cli-013** (`balance_from_spec`/`ReportSpec`/`ReportSection`
are Python-API-only; no CLI command wires to them). Reconstruction §1
describes `main()`'s dispatch as routing to "one of six command
branches (`balance`, `register`, `accounts`, `print`, `stats`,
`check`)" based on a full 509-line read of `cli.py`, and §2 independently
lists `balance_from_spec` only among `reports.py`'s public functions
with no CLI-wiring commentary attached. The reconstruction never states
the negative claim ("`balance_from_spec` is not called from `cli.py`")
in so many words — it is an inference from the exhaustiveness of the
six-branch dispatch description it does give, not a directly quoted
grep-style statement the way reports-cli-013's own Justification phrases
it. Given the reconstruction's evidence basis was a full-file read of
`cli.py` with no caveat about any additional, unlisted call sites, this
inference is reach-complete rather than reach-limited; aligned, noted as
indirect rather than a verbatim match.

**reports-cli-014** (`writer.transaction_to_text()`/`journal_to_text()`
round-trip guarantee; right-aligned amount columns; elided postings as
bare `"    {account}"`; exactly one blank line between transactions;
directives are explicitly NOT serialised in v1). **Partial.** The
round-trip, column-alignment, and blank-line-separation claims are
strongly and specifically corroborated: reconstruction §1 and §6
independently cite the same docstring guarantee ("same date, flag,
description, postings, amounts, comments"), and independently state that
`journal_to_text` tests confirm an empty journal serialises to a lone
`"\n"` and exactly one blank line separates transaction blocks — matching
the assertion's own cited tests' effect precisely. Where the two
artefacts diverge in reach, not content: the assertion's Statement
contains a distinct, separately-stated clause that `journal_to_text()`
"explicitly does NOT serialize directives (account/commodity/payee/P) in
v1." Nothing in the reconstruction's seven sections or its eleven named
limitations mentions directives, journal-level declarations, or that
exclusion at all — `writer.py`'s scope is discussed only in terms of
transaction/posting serialisation. This is a reach gap on a distinctly
named sub-claim (the kind the comparison report for `checks` classified
as `partial` for an analogous reason), not a disagreement — classified
`partial` rather than `aligned` for that reason alone.

**reports-cli-015** (`check` has a distinct control-flow path in
`main()`; the unconditional basic-check gate runs before `check`'s own
named-check pass; `-I` suppresses only the "assertions" basic check via
a shared `skip` frozenset passed to both the gate and `check` itself;
`-s` additionally runs `run_strict_checks` for non-`check` commands and
is forwarded into `check` via `strict=args.strict`). Reconstruction §5.1
independently states the identical control-flow ordering (file
resolution → load/merge → commodity-style map → `-q` parse →
unconditional `run_basic_checks(journal, skip=...)` → optional
`run_strict_checks` if `-s`) and live-reproduces the exact scenario the
assertion's own Examples field uses: `check -f assertions_fail.journal`
with no check names still exits 1 because the unconditional gate runs
before `check`'s own `run_checks(names=[])` call, and `-I`/
`--ignore-assertions` suppresses that same gate. The reconstruction's
own limitation #9 independently restates this exact two-layer structure
("`check` with zero explicit check names still exits 0... but the
unconditional basic-check gate... still applies unless `-I` is passed")
and independently warns it "could easily be misread as 'the `check`
command controls all checking,' which it does not" — the same
distinction the assertion's own Statement makes. The reconstruction does
not independently re-verify the more granular mechanics of `-s` (that
`run_strict_checks` is filtered to exclude names already in
`BASIC_CHECK_NAMES`, or the precise `strict=args.strict` forwarding
signature into `check`); it only confirms `-s`'s existence and general
effect at the `--help`/dispatch level. This is a minor elaboration gap
on the same already-confirmed claim, not a separately-named sub-claim
the way reports-cli-014's directive exclusion is — aligned.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification.** Every
`aligned`/`partial` classification above means only that the
independently-reconstructed as-built behaviour currently matches (or
partially matches) what the snapshot asserts — it does not establish
that the asserted rule or invariant is itself the *right* behaviour
relative to hledger's own semantics. This matters most for the
`rule`/`invariant`-kind assertions here: reports-cli-003's file-
resolution precedence, reports-cli-009's/-012's depth semantics, and
reports-cli-015's two-layer check structure are all confirmed as
*currently implemented*, not confirmed as the behaviour hledger itself
specifies — both artefacts independently decline to re-verify the cited
upstream `Ledger.hs` claim behind reports-cli-012, and neither artefact
in this comparison attempts to. Treat every `aligned` above as "the code
matches the claim," not as "the claim is correct."

## Gaps in the knowledge base (found by the reconstruction, not covered by any assertion)

The reconstruction surfaced several real, specific behaviours that none
of the 15 frozen assertions address at all. These are knowledge-base
gaps, not comparison failures — flagged per this mode's "both
directions" instruction, not classified against any assertion:

1. **Two independently-defined, differently-behaving `_fmt_amount`
   helpers** (reconstruction §5.4, limitation #2): `cli.py`'s version
   (shared by `balance`/`register`/`print`) renders a negative amount as
   `"£-4.50"` (symbol then minus sign); `writer.py`'s version renders the
   same value as `"-£4.50"` (minus sign then symbol). No assertion in
   this topic's set discusses amount-formatting parity (or the lack of
   it) between `print`'s on-screen output and `writer.py`'s serialised
   text, beyond the inline-comment divergence reports-cli-010 names.
2. **`print` does not resolve elided postings** (limitation #3): it
   iterates raw `txn.postings`, never `ledgerkit.parser.resolve_elision`,
   so an elided posting prints with no amount at all under `print`,
   while `balance`/`register` (which do call `resolve_elision`) show its
   inferred amount for the same journal. Not covered by any assertion.
3. **`print` never colourises negative amounts** (limitation #4), unlike
   `balance`/`register`. Not covered by any assertion.
4. **Two parallel filter mechanisms coexist in every `reports.py`
   function** — the legacy `Query` dataclass and the internal-only
   `_query_ast`/`_query_depth` pair, AND-combined when both are supplied,
   plus `accounts()`'s own narrower tag-visibility carve-out
   (`_matches_posting_for_accounts`) that applies only to `_query_ast`
   `Tag` nodes (limitation #7). No assertion in this set describes this
   dual-mechanism structure as such.
5. **`balance_from_spec`'s per-section `accounts=`/`exclude=` patterns
   remain on a separate, older `_matches_pattern`/`compile_hledger_regex`
   path**, never converged with the same `Query`→AST translation the
   function's own *outer* query argument now uses (limitation #8).
   reports-cli-013 covers `balance_from_spec`'s CLI-unreachability but
   not this internal architectural asymmetry.
6. **An unrecognised CLI command exits with code 2, not 1** (limitation
   #11), inconsistent with every other documented error path in the
   reconstruction (and in this topic's assertions), which uniformly use
   exit code 1. reports-cli-001 confirms the *rejection* of an
   unrecognised command but no assertion states its exit code.

## What was checked

- All 15 assertions' `Statement`/`Evidence`/`Examples`/`Counterexamples`
  fields against the reconstruction's §1–§7 content, assertion-by-
  assertion, including cross-checking cited test names and quoted code
  comments for literal correspondence rather than just topical overlap.
- Whether the reconstruction's eleven named limitations (its §7)
  contradicted, narrowed, or were silent on any assertion's claim. None
  contradicted. Four (limitations #1/#5/#6/#9) directly corroborate
  reports-cli-010/-009/-012/-015 respectively; the remainder
  (limitations #2/#3/#4/#7/#8/#11) are real findings outside any
  assertion's scope, listed above as knowledge-base gaps; limitation #10
  is the reconstruction's own evidence-boundary disclosure
  (`ledgerkit/models.py` unread), not a behavioural claim to compare
  against anything.
- Whether either artefact's own escalated/open items were silently
  resolved by the other. reports-cli-010's escalated "design intent"
  open question is not resolved by the reconstruction either — it
  independently lands on the same "no code comment/docstring/test
  addresses this" boundary, reinforcing rather than closing the
  escalation.
- Searched specifically for a case where an assertion's own stated
  claim predicted a counterexample the reconstruction might have
  surfaced (the brief's "actively search for contradictions" charge,
  carried into this comparison as "did the independent artefact ever
  catch the assertion in a mistake"). None found: the two places where
  the original assertion-research draft *had* been mistaken
  (reports-cli-005's "necessarily zero" claim, reports-cli-011's
  line-count arithmetic) were already caught and fixed in this topic's
  own prior REVIEW-mode pass, before this comparison; the reconstruction
  does not surface any further such case.

## Escalations

None raised by this comparison. reports-cli-010's own "ESCALATED" open
question (whether `print`'s comment-dropping is deliberate scope or an
unnoted gap) remains open from the snapshot's own prior REVIEW-mode
pass; this comparison does not resolve it, and notes only that the
independent reconstruction reaches the identical unresolved boundary on
its own, which is corroborating evidence that the question is a genuine
ambiguity rather than something either artefact failed to look for.
