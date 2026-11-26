# Legacy reconciliation: README.md

**Mode:** Plan 29 §6 Legacy Reconciliation (docs-maintainer, Phase 5)
**Date:** 2026-11-14
**Target:** `/home/cormac/projects/ledgerkit/README.md`
**Inputs:**
- Real legacy `README.md` (pre-reconciliation, committed state at dispatch time)
- Phase 4 clean-room draft: `dev-docs/clean-room/drafts/README.md.clean-room-draft`
  (dispatch `readme-clean-room-draft-20261114`)
- Phase 3 evidence for the 4 topics the draft cites: `current-state@v1`,
  `reports-cli@v1`, `journal-parsing@v1`, `compat-system@v1` — snapshots,
  sidecars, all assertion files (incl. `_review.md` domain-skeptic notes),
  `implementation-reconstruction/<topic>.md`, `implementation-comparison/<topic>.md`
- `knowledge/DECISIONS.md`, `knowledge/EDGE_CASES.md`, `knowledge/ANTIPATTERNS.md`,
  `knowledge/DOMAIN_RULES.md`
- Direct, independent re-verification performed this session (live `python -m
  unittest`, live `python -m ledgerkit ...` runs, direct reads of `pyproject.toml`,
  `.github/workflows/tests.yml`, `ledgerkit/*.py`, `dev-docs/compat-register/*.yaml`,
  `git show v1.0.0:LICENSE`) — used only to re-ground claims, never to replace a
  Phase 3 assertion citation where one exists.

**Important methodological note:** per the brief, agreement between the legacy
README and the Phase 4 draft is never treated as evidence on its own. Every
`supported` classification below traces either (a) to a specific Phase 3
assertion whose own cited evidence checked the claim directly (file:line, a
named test, or a live command transcript — most of these were additionally
re-run live this session, see per-item notes), or (b) where the claim falls
outside the four in-scope topics, to a direct primary-source check performed
independently this session (not to the legacy doc's or the draft's own prose).

---

## Classification breakdown

| Category | Count |
|---|---|
| `supported` | 25 |
| `stale_or_contradicted` | 2 |
| `rationale_requiring_verification` | 2 (both resolved below) |
| `useful_example` | 3 |
| `obsolete` | 0 |
| **Total legacy claims classified** | **32** |

Plus: 7 wholly new sections folded in from the Phase 4 draft (not a
reclassification of an existing legacy claim — these are additions). See
"New content merged from the draft" below.

---

## Claim-by-claim classification

### Title, badges, intro paragraph

1. **Tests/Licence badges** — `supported`. Workflow file
   `.github/workflows/tests.yml` and `LICENSE` (GPLv3) both exist and match
   the badge text. Direct file check, this session.
2. **"A deterministic, Python-native accounting and query engine with a
   documented hledger-compatible foundation"** — `supported`. Verbatim match
   to `pyproject.toml`'s `[project] description` field (same file
   `current-state-001` reads). Direct check, this session, same evidence
   file as `current-state@v1#current-state-001`.
3. **"ledgerkit uses hledger as its primary accounting and compatibility
   reference... does not aim to be a line-for-line Python clone"** —
   originally `rationale_requiring_verification` (a stated reason for a
   design stance). **Resolved: `supported`.** Traces to
   `dev-docs/planning/core-redefinition/01-product-goal.md` line 148
   ("**Not** a line-for-line Python port of hledger's Haskell
   implementation") — a dedicated product-goal planning document, not the
   README's or draft's own say-so — corroborated by the live compat-register
   distribution (`compat-system@v1#compat-system-003`/`-004`, re-verified
   live this session: 49 entries, 40 `compatible`, 1 `intentional_divergence`,
   6 `unsupported`, 2 `unexplained_mismatch`/resolved, 0 `extension`), which
   is the register actually enacting a "compatible-but-not-a-clone" posture
   rather than merely asserting one. No entry in `knowledge/*.md` contradicts
   this stance.
4. **"Where Python or modern tooling offers a materially better design,
   ledgerkit says so explicitly rather than copying a limitation for its own
   sake"** — originally `rationale_requiring_verification`. **Resolved:
   `supported`**, same grounding as item 3 — `01-product-goal.md`'s explicit
   non-clone stance plus the register's `intentional_divergence` kind
   existing as a real, populated category (1 entry) is the mechanism by
   which this stated behaviour is actually exercised, not merely claimed.
5. **compat-register description ("record of exactly which behaviours match
   hledger, which are deliberate extensions, and which are documented,
   intentional divergences")** — `supported` against
   `compat-system@v1#compat-system-001` (the schema's closed five-value
   `kind` taxonomy). Noted but not a defect: the `extension` kind currently
   has zero populated entries (`compat-system-003`/`-004`, re-verified live);
   the README describes an available *category*, not a claim that an example
   currently exists, so this is not contradicted.

### Features bullets

6. **"Parse `.journal` files compatible with the hledger 1.52 format"** —
   `supported`. The hledger 1.52 pin is consistent across every current-truth
   doc that states a version (`dev-docs/hledger-compatibility.md`,
   `dev-docs/api-spec.md`, and the relevant planning docs), and
   `journal-parsing@v1`'s ten assertions (all `verified`, several
   independently re-confirmed by the domain-skeptic review and by me live
   this session) describe exactly this parsing surface.
7. **"Comprehensive directive support: `include`, `account`, `commodity`,
   `payee`, `alias`, `P`, `Y`, `D`, `apply account`"** — `stale_or_contradicted`
   (incomplete, not false). `journal-parsing-007` (verified; evidence:
   `ledgerkit/parser.py:966-1011,1111-1575`, a dedicated test class per
   directive) documents three additional supported directives this bullet
   omitted: `tag`, `decimal-mark`, and `comment`/`end comment` (block
   comment). `include` itself is real but is handled by `ledgerkit/loader.py`
   (confirmed by direct read this session, `_INCLUDE_LINE` regex and
   `_expand_includes`), not by `parser.py` — the bullet's inclusion of
   `include` is accurate, just drawn from a different module than the rest
   of the list. **Fixed**: the bullet now lists all twelve supported
   directives.
8. **"Core CLI commands: `balance`, `register`, `print`, `accounts`, `stats`,
   `check`"** — `stale_or_contradicted` (cosmetic only: wrong order).
   `current-state-004` and `reports-cli-001` both give the canonical,
   source-verified order as `balance, register, accounts, print, stats,
   check` (the literal `COMMANDS` tuple and the `argparse` `--help` choices
   string). **Fixed**: reordered to match.
9. **"Strict mode (`-s`) and balance assertions"** — `supported`
   (`reports-cli-002` for the flag's existence; `reports-cli-015` for
   strict-mode's actual effect, forwarded into `check` too). Live-reconfirmed
   this session (`check -f ...` silent-success, `commodity` directive bug
   reproduced — see item 20 below).
10. **"Multi-commodity balances with tree rollup"** — `supported`
    (`reports-cli-004`, `tree=True` behaviour, implicit-parent accounts,
    `is_subtotal`).
11. **"Commodity display style inference and `-c` override flag"** —
    `supported`. The `-c` flag half is `reports-cli-002` (in-scope,
    `verified`). The "inference" half concerns `ledgerkit/commodity_style.py`
    (the `commodity-styling` topic, **not** one of this dispatch's four
    in-scope topics). Per the brief's re-grounding rule, I did not accept
    this on the legacy doc's or draft's say-so; I independently confirmed
    `CommodityStyle` and `_infer_separators` exist in that module by direct
    read this session. Flagged here as verified by direct inspection rather
    than by a Phase 3 assertion citation, since none was in scope.
12. **"Optional pandas DataFrame export (`pip install ledgerkit[pandas]`)"**
    — `supported` (`current-state-001`: `pandas>=1.3` optional-dependency
    block in `pyproject.toml`), plus direct confirmation this session that
    `to_dataframe` methods exist on `Journal` and on the three report-result
    classes (`ledgerkit/models.py:252,479`, `ledgerkit/reports.py:65,116,171`).
13. **"Editor-integration layer: lenient parser, round-trip writer,
    `EditorDocument`"** — `supported`. "Lenient parser" is
    `journal-parsing-008` (in-scope, `verified`, and I live-reproduced its one
    confirmed exception this session). "Round-trip writer" is
    `reports-cli-014` (in-scope, `verified`). `EditorDocument` itself belongs
    to the `editor-surface` topic (out of this dispatch's four-topic scope);
    confirmed to exist by direct read of `ledgerkit/editor_model.py` this
    session rather than accepted on the legacy doc's authority.
14. **"Pure Python — no third-party runtime dependencies"** — `supported`
    (`current-state-001`: `dependencies = []`).
15. **"Python 3.8–3.12"** — `supported`. `current-state-001` establishes the
    `>=3.8` floor; the `3.12` ceiling is confirmed by direct read of
    `pyproject.toml`'s `classifiers` block and `.github/workflows/tests.yml`'s
    CI matrix (`["3.8","3.9","3.10","3.11","3.12"]`) this session, not by a
    Phase 3 assertion (out of the four-topic scope).

### Requirements / Installation / Usage / Python library

16. **"Python 3.8+"** (Requirements) — `supported`, same grounding as item 15.
17. **Installation commands** (`pip install ledgerkit`, `[pandas]` extra, dev
    install via `pip install -e ".[pandas]"`) — `useful_example`, re-grounded
    this session against `pyproject.toml`'s actual `name`/`optional-dependencies`
    fields (`current-state-001`'s evidence file) rather than kept on the
    strength of having previously existed.
18. **CLI quick-start examples** (`ledgerkit balance myfile.journal`, etc.,
    and `python -m ledgerkit balance myfile.journal`) — `useful_example`,
    re-grounded against `current-state-004`/`-005`'s live `--help` transcript
    and `reports-cli-003`'s file-resolution rule (a bare positional *is* a
    valid journal shorthand for every non-`check` command).
19. **Python library example** (`ledgerkit.load(...)`, `.accounts()`,
    `.balance()`) — `useful_example`, re-grounded this session by directly
    importing `ledgerkit`, calling `ledgerkit.load("tests/fixtures/sample.journal")`,
    and confirming the returned `Journal` has both methods. Not a Phase 3
    assertion in the four-topic scope; directly re-run instead of trusted.

### Documentation table, pandas ecosystem, Development

20. **Documentation table** (links to `docs/getting-started.md`, `usage.md`,
    `journal-format.md`, `python-api.md`) — `supported`, all four files
    confirmed to exist this session.
21. **pandas ecosystem code example** (`journal.to_dataframe()`,
    `journal.balance().to_dataframe()`, etc.) — `useful_example`, re-grounded
    against the direct `to_dataframe` method-existence check in item 12.
22. **Development section test command**
    (`python -m unittest discover -s tests -t . -v`) — `supported`,
    live-re-run this session: `Ran 935 tests in 0.755s` / `OK (skipped=29)`,
    matching `current-state-003` (`verified`, itself independently
    re-confirmed by the domain-skeptic review on 2026-10-03) exactly, with
    zero drift between the 2026-10-02 freeze and today (2026-11-14).

### Hledger Compatibility / Contributing / Acknowledgements / Licence

23. **"See `dev-docs/hledger-compatibility.md` for which hledger journal
    features are supported"** — `supported`, file exists; superseded in
    structure (not in truth) by the richer register-tracking summary now
    folded in from the draft — see "New content merged from the draft" below.
24. **Contributing section + CONTRIBUTING.md description** ("pull request
    guidelines, commit message format, and branch naming") — `supported`,
    confirmed this session that `CONTRIBUTING.md` has exactly those three
    `##`/`###` sections (`Pull Requests`, `Branch Naming`, `Commit Messages`),
    plus `CODE_OF_CONDUCT.md` exists.
25. **AI-tooling / sparse-checkout clone instructions** — `supported`
    (structural; the named sparse-checkout set — `ledgerkit tests docs
    README.md LICENSE pyproject.toml` — matches the actual top-level layout
    confirmed via `ls` this session).
26. **Acknowledgements: Ledger / John Wiegley** — `supported`. External
    historical attribution, outside this project's own verifiable surface;
    left as a stable, non-controversial attribution (not independently
    re-derivable from this repository's evidence, and not contradicted by
    anything in scope).
27. **Acknowledgements: hledger / Simon Michael, licence-compatibility
    rationale, link to `10-source-assisted-development.md`** — originally
    `rationale_requiring_verification`. **Resolved: `supported`.**
    `dev-docs/planning/core-redefinition/10-source-assisted-development.md`
    exists and its line 64 (`directly_translated` table row) is specifically
    about this exact mechanism (translated hledger material requiring a
    citing comment + `THIRD-PARTY-NOTICES.md` entry + register `kind`) — the
    README's claim is a direct, accurate summary of that document, not an
    unverified assertion resting on its own say-so.
28. **Licence section** (GPL-3.0-or-later; matches hledger's own licence;
    pre-GPL releases 0.1.0–1.0.0 and 1.0.0.dev1 remain MIT) — `supported`.
    `LICENSE` is GPLv3 text, `NOTICE` states GPL-3.0-or-later,
    `02-licence-migration.md` exists, and — the one claim here that's
    independently falsifiable rather than just "the file says so" — I ran
    `git show v1.0.0:LICENSE` this session and confirmed that tagged
    revision's `LICENSE` file is in fact MIT-licensed, directly confirming
    the "not retroactive" claim rather than trusting the current `NOTICE`
    file's own prose about history.

### `obsolete`

None found. Nothing in the legacy README describes a feature, command, or
behaviour that has been removed or renamed.

---

## New content merged from the draft (not a legacy-claim reclassification)

The Phase 4 draft (`readme-clean-room-draft-20261114`) contributes seven
sections with no prior equivalent in README.md, each kept with its original
`<topic>@v1#<assertion-id>` citations intact:

1. **Status** — version/Python-floor/zero-deps/pandas-extra
   (`current-state-001`) and the test-suite snapshot (`current-state-003`).
2. **Command-line interface** — the flat six-subcommand `argparse` surface
   and shared global flags (`reports-cli-001`, `-002`), and journal-file
   resolution precedence including `check`'s positional-as-name quirk
   (`reports-cli-003`).
3. **Reports** — per-command behavioural detail for `balance`, `register`,
   `accounts`, `print`, `stats`, `check`, and the unwired `balance_from_spec`
   Python-API-only report path (`reports-cli-004` through `-013`, `-015`).
4. **Journal text serialization** — `writer.transaction_to_text()`/
   `journal_to_text()`'s round-trip guarantee and directive-exclusion
   caveat (`reports-cli-014`).
5. **Journal format support** — dates, postings/amounts, comments,
   directives, and strict-vs-lenient parsing (`journal-parsing-001`
   through `-010`).
6. **hledger compatibility tracking** — the register's schema, `kind`
   taxonomy, four-tier `status` lifecycle, the authorship-restriction
   finding, and current entry counts (`compat-system-001` through `-005`).
   I re-ran the register's own `kind:`/`status:` counts live this session
   (see item 22's sibling check) and they are **unchanged** from the
   2026-10-02 freeze: 49 entries, 40/6/2/1 by kind, 26/9/14/0 by status. No
   drift to reconcile.
7. **Known current limitations** — the five limitations the draft's
   assertions name explicitly (print drops inline comments;
   `parse_string_lenient` doesn't actually catch a malformed `commodity`
   directive; `check`'s positional reads as a check name, not a file;
   `balance_from_spec` isn't CLI-wired; most compat-register entries are
   still at `proposed`). I live-reproduced three of these five directly this
   session (the `print`/inline-comment drop, the `commodity`-directive
   lenient-parsing bug, and the register's current status counts) rather
   than accepting the draft's citations on faith.

I did **not** bulk-merge the draft's full per-command CLI examples or the
complete journal-format syntax reference as duplicate prose, since
equivalent (and already-correct, separately maintained) detail already
lives in `docs/usage.md` and `docs/journal-format.md`; duplicating it
verbatim in README would create a second copy to keep in sync. The merged
sections above are the behavioural/precision content that has no
pre-existing home elsewhere in the hand-authored docs.

---

## Explicit open questions (left unresolved, not silently decided)

1. **Whether `print`'s omission of inline comments is deliberate v1 scope or
   an unnoted gap** (`reports-cli-010`). The *behaviour* is fully confirmed
   (live-reproduced again this session). The *design intent* is not
   decidable from any evidence in scope — no docstring, comment, or test
   addresses it, and nothing in `knowledge/*.md` resolves it either (grepped
   this session, no match). Kept as an explicit open question in both the
   new "Reports" → `print` paragraph and the "Known current limitations"
   list, exactly as the domain-skeptic review escalated it on 2026-10-03.
   This needs a decision from the lead/user, not a guess.
2. **A named count disagreement between the `compat-system` assertion set
   and its independent implementation-reconstruction**, over whether
   `LK-COMPAT-QUERY-DEPTH-001` cites ten or eleven test identifiers
   (`implementation-comparison/compat-system.md`, classified `partial`
   there). This is too granular for README and isn't surfaced there; noting
   it here so the lead is aware it exists. I did not touch any
   compat-register entry's `kind`/`status` field — not my role.
3. **`dev-docs/hledger-compatibility.md` line 11** currently reads "each
   entry there is `status: proposed` pending executable verification,"
   which is now stale (live counts this session: 26 `proposed`, 9
   `self-verified`, 14 `verified`, 0 `final` — the majority is no longer
   universally `proposed`). This is a real current-truth defect, but it is
   in a file outside this specific dispatch's declared target (README.md
   only, per the task's framing). Flagging it to the lead rather than
   fixing it here or silently leaving it unflagged.
4. **journal-parsing-008's "one named exception" framing**: the
   implementation-comparison for `journal-parsing` found a *second*,
   differently-typed uncaught exception (an alias-replacement backreference
   escaping as `re.PatternError`, not even `ParseError`) beyond the
   `commodity`-directive bug the assertion names. The draft's own prose
   already hedges this correctly ("This is the one exception the available
   evidence names explicitly; it should not be read as a guarantee that no
   other case can break the 'never raises' contract"), and that hedge is
   carried into the merged README unchanged — no further action needed, but
   noting the comparison finding here for traceability.
