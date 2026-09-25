# Decisions

Non-obvious judgment calls made during development. Each entry explains what was chosen, why, and what was rejected.

---

## 2026-09-16 — Stage C Phase 2's query/report integration is internal-only this phase; no new public API surface

**Decision:** `reports.py`'s `accounts`/`balance`/`register`/`stats`
gain a **private**, leading-underscore keyword parameter
(`_query_ast: ledgerkit.query.QueryNode | None = None`) rather than a
new public `query_ast=` parameter. `cli.py`'s new `-q`/`--query` flag
parses text to a `QueryNode` via `ledgerkit.query.parse` and passes it
through this private parameter. `dev-docs/api-spec.md` is **not**
updated this phase — the private parameter is explicitly not part of the
documented, stable contract those four functions carry.

**Why:** per `18-stage-c-phase-2-codecompass-adoption-plan.md` §6.1's own
decision criteria — prefer the option with the smallest committed public
surface absent a concrete reason otherwise. No known caller needs
`QueryNode` at the public `reports.py` level today: `ledgerkit-editor`'s
confirmed usage (Stage B Phase 1 finding) is `Query`-only, and no other
external consumer of `reports.py` is known to exist. Adding a new public
parameter (or widening `query`'s existing type) now would commit to an
API shape before any real caller has demonstrated needing it — exactly
the "temporary second public query interface" risk the plan's own
amendment (2026-09-16) was written to avoid. A leading-underscore keyword
avoids both the Journal-copying/elision-resolution risk a CLI-side pre-
filtering approach would have introduced (filtering postings out of a
transaction *before* `resolve_elision` runs would corrupt elided-amount
inference, since elision needs the full, unfiltered posting set) and the
premature-public-surface risk of a fully public new parameter — it
reuses each report's existing per-posting loop exactly where the
existing `Query`-based `_posting_matches` check already sits.

**What was rejected:**
- **A new public `query_ast=` parameter** (the original plan draft's
  default) — rejected per the amendment's own finding 1; no demonstrated
  caller need yet.
- **Overloading `query`'s existing type** to `Query | QueryNode` — same
  objection; still a public signature change committed without a
  demonstrated need, and risks `isinstance`-dispatch bugs for the sake of
  avoiding a second parameter name that isn't otherwise a real problem at
  private-parameter scope.
- **CLI-side pre-filtering of the Journal/transaction list** before
  calling the unchanged public report functions — rejected specifically
  because it would filter postings out of a transaction before
  `resolve_elision(txn)` runs, corrupting elided-amount inference for any
  query that excludes some but not all of a transaction's postings; the
  in-loop private-parameter approach avoids this because filtering still
  happens per-posting, after elision resolution, exactly where the
  existing `Query` check already happens.

**Follow-up:** if a real public, library-level need for `QueryNode`-based
filtering at the `reports.py` level surfaces (e.g. `ledgerkit-editor`
adopting the new query engine directly, or another consumer), promoting
`_query_ast` to a documented public parameter — or resolving §6.1's
options A/B properly — is a natural, evidence-backed follow-on, not a
reason to revisit this decision speculatively now.

---

## 2026-09-13 — Pinned hledger reference binary confirmed and formally recorded as the compat-differential-tester target

**Decision:** `/home/cormac/.local/bin/hledger` (`hledger
1.52.4-g33fa849e7-20260910, linux-aarch64`, sha256
`c212db5f25daddf82f5767011ae73d3b7329c244db617e010fafe481cd07d747`) is
the pinned `hledger` executable `compat-differential-tester` runs
against, matching `09-compatibility-system.md` §9.1's `1.52.4` baseline
exactly. Confirmed to build from the same commit
(`33fa849e7ae841968bd21c427094c4fb4a4ec38d`, tag `1.52.4`) as the local
source clone at `/home/cormac/projects/hledger` that `hledger-researcher`
already used for the Stage C Phase 1 semantics brief — binary and source
are the same pinned build, not two independently-tracked versions.

**Why:** prior sessions repeatedly recorded "no pinned hledger binary
exists in this environment" as an open blocker (Stage A closeout,
`CONTEXT.md` across Stage B and Stage C Phase 1) — that was checked
directly with `which hledger`/`hledger --version` and found to be no
longer true (or possibly never re-checked after the binary was installed
separately from this project's own sessions). Recording the exact
version/commit/hash here, rather than just noting "a binary exists,"
matches `10-source-assisted-development.md` §10.5's requirement that the
executable used for differential testing be recorded specifically, never
"whatever `hledger` resolves to on PATH" without pinning which version
that was.

**What this unblocks, and what it doesn't:** `compat-differential-tester`
can now actually perform executable verification — moving register
entries from `status: proposed` to `status: verified` by running real
comparisons, which was previously impossible in this environment. **This
decision does not itself run any differential test or change any register
entry's status** — it only confirms and pins the reference binary; the
verification work is a separate, not-yet-started task.

**What was rejected:** none — this is a confirmation of existing
environment state, not a choice among alternatives.

---

## 2026-09-13 — Standing pre-authorisation for commit/push at logical intervals and phase end

**Decision:** added a "Commit & Push Cadence" section to `CLAUDE.md`
(between Retro Reports and Commit Message Format) that pre-authorises
Claude to commit and push **without asking each time**, on this project
specifically. Two distinct triggers, deliberately not conflated: (1)
**commit** at a *logical interval* — any coherent, self-contained,
internally-consistent unit of change (tests passing, docs synced per the
same-response Documentation Sync Rules) — which may be more granular than
a whole phase; (2) **push** at the end of each *successful phase* (the
same granularity `dev-docs/retros/` already uses) — exit criteria met,
tests passing, retro written. A failed or incomplete phase gets neither.
Force-pushes, history rewrites, and branch deletion are explicitly carved
out as still requiring a per-instance ask.

**Why:** the user directed it explicitly, updating the durable project
instructions rather than asking case-by-case — this is precisely the
"authorised in advance in durable instructions like CLAUDE.md files"
exception the top-level tool guidance names for skipping a normally-required
confirmation on a hard-to-reverse, others-visible action (a push). Tying
the push trigger to the existing phase/retro granularity (rather than
inventing a separate cadence) means no new concept for future sessions to
learn, and keeps "was this phase pushed" checkable by the same
`release-phase-auditor` DoD pass that already checks the retro exists —
both are now audit items 8 and 9 on that checklist.

**What was rejected:**
- **A single "commit and push together" trigger** — rejected; commits are
  useful at a finer grain than pushes (several small commits within one
  phase are better version-control hygiene than one giant commit), while
  pushing every commit individually would spam the remote with
  intermediate, possibly-inconsistent states mid-phase.
- **Push at Stage/Milestone `[DONE]` instead of per-phase** — rejected;
  that event is coarser and still explicitly user-confirmed
  (`CLAUDE.md`'s existing Changelog & Roadmap Rules), and holding pushes
  back that long would mean long-lived unpushed local work, the opposite
  of what "logical intervals" was asked for.
- **Extending the standing pre-authorisation to force-push/rebase/branch
  deletion too** — explicitly rejected; those remain governed by the
  existing "Executing actions with care" guidance regardless of this
  change, since they're a different risk class (rewriting shared history
  vs. adding to it).

---

## 2026-09-13 — Account-type semantics (Stage E) must extend the model additively, never retype `declared_accounts`

**Decision:** when Stage E implements account-type semantics (parsing the
`account` directive's `type:` tag, currently stripped/ignored in
`parser.py`), the parsed type must be stored in a **new** field —
e.g. `Journal.account_types: dict[str, AccountType]` or a richer
`Journal.account_declarations: list[AccountDeclaration]` — kept alongside
the existing `Journal.declared_accounts: list[str]`, never by changing
that field's element type to something richer than a plain string.

**Why:** `Journal.declared_accounts` is documented in `dev-docs/api-spec.md`
as `list[str]`, and is a **confirmed real runtime dependency** of
`ledgerkit-editor`'s `utils/journal_index.py` (verified by reading its
actual source — `dev-docs/planning/core-redefinition/
15-editor-compat-inventory.md`, extended by the Stage B Phase 2 model
review, `16-model-review.md` §16.3). Retyping it would silently break that
consumer and violate the frozen-v1-API-surface commitment
`06-core-architecture.md` §6.5 already makes. Every other Stage E/F
model extension reviewed in the same phase (costs, lots, virtual postings,
valuation) is achievable as a pure new-field addition with no existing
field needing to change shape — `declared_accounts` was the one place a
naive implementation might reach for changing an existing field instead,
so it's recorded explicitly rather than left to be discovered the hard way
when Stage E actually starts.

**What was rejected:** changing `declared_accounts` to carry richer
per-account data directly (e.g. `list[AccountDeclaration]` in place of
`list[str]`) — rejected because it's an avoidable breaking change to a
verified-live consumer, when an additive alternative exists at no real
cost.

---

## 2026-09-12 — Adopted a per-phase retro report process, modelled on the sibling codecompass project

**Decision:** added `dev-docs/retros/` (README + TEMPLATE) and a "Retro
Reports" section in `CLAUDE.md`: at the end of every **phase** (a discrete
unit of implementation work with its own `ROADMAP.md`-relevant scope —
sometimes a whole small Milestone/Stage, sometimes one of several phases
within a larger one, per the existing `Milestone 4 Phase 1`…`Phase 5`
precedent in `dev-docs/changelog/MILESTONE-4.md`), Claude authors
`dev-docs/retros/<STAGE-OR-MILESTONE>[-PHASE-K].md` in that same response,
using the template's fixed sections (where we are, goal, scope delivered
vs planned, what worked/didn't, lessons learnt, process-improvement
feedback, learnings filed, where we're going, time/cost). This is **not**
tied only to a Milestone/Stage reaching `[DONE]` — it fires at the same
per-phase cadence `release-phase-auditor` and `docs-reconstructor` already
use (`dev-docs/planning/core-redefinition/03-agent-led-development.md`
§3.4's fresh-session workflow). `release-phase-auditor` now checks the
retro exists and is substantive for that phase as part of its
Definition-of-Done audit; `roadmap-context-curator` authors retros at
phase-end and reads them during its existing learning-triage job.

**Why:** the sibling `codecompass` project (`/home/cormac/projects/
codecompass`) runs this exact convention per-phase
(`decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md`,
`planning/retros/`), for two reasons that apply equally here: process
friction (unclear agent boundaries, a step that added nothing, a dropped
handoff) previously had nowhere to go except ad hoc mention in
conversation, and nothing accumulates evidence for later questions like
"is this agent roster still earning its keep" without dated records to
review in bulk. Ledgerkit already had the other half of codecompass's
ADR 0050 independently (a dual-mode `docs-reconstructor` doing per-phase
drift audits, and a `roadmap-context-curator`/`release-phase-auditor` pair
already operating per-phase) — the retro report itself was the one piece
missing, and it belongs at the same per-phase granularity those roles
already use, not a coarser one. (A first draft of this decision scoped
retros to Milestone/Stage completion only — corrected within the same
session, before anything was committed, once it was noticed that this
undershot the cadence the rest of the roster already runs at.)

**What was rejected:**
- **Folding retro content into `CONTEXT.md`** — rejected because
  `CONTEXT.md` is overwritten each session (`CLAUDE.md`'s Context File
  rule); retros need to accumulate as a running, reviewable narrative.
- **Scoping retros to Milestone/Stage completion only** — rejected (see
  above); it would fire far less often than `release-phase-auditor`'s own
  per-phase Definition-of-Done audits, leaving most phases' process
  friction uncaptured.
- **Retroactively writing retros for Milestones 0–4** — rejected as
  unnecessary busywork; their full detail, including their own internal
  phase breakdown, already lives in `dev-docs/changelog/MILESTONE-{0..4}.md`.
  The convention starts with the phase(s) that made up Stage A, the most
  recently completed work at adoption time (mirroring codecompass's own
  "not retroactive before the phase it was adopted in" precedent).
- **A new dedicated agent for this** — rejected; `roadmap-context-curator`
  already owns learning triage and `ROADMAP.md`/`CONTEXT.md` reconciliation
  at phase boundaries, so authoring the retro is the same concern at the
  same trigger point, not a new role.

**Follow-up:** Stage A's retro (`dev-docs/retros/STAGE-A.md`) was written
in this same response as a single file covering the whole stage — Stage A
had already completed by the time this process was adopted, so it wasn't
practical to reconstruct separate per-sub-phase retros after the fact.

---

## 2026-09-12 — Stage A compat-register migration scoped to a representative first wave, not full transcription

**Decision:** when closing out the rest of Stage A (agent-role files +
compatibility harness), the register migration described in
`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.5
("every In-Scope/Out-of-Scope row becomes an entry") was scoped down, on
the user's explicit choice among three offered options, to: directive
entries (11 + 1 newly identified divergence), validation-check entries
(8), and the genuinely-unsupported-feature entries (5) — 25 entries total.
The finer-grained rows (date formats, amount formats, comment forms,
account-name rules) were **not** migrated in this pass.

**Why:** a full mechanical migration would have been ~57 individual YAML
entries, each needing a real `implementation:`/`tests:` citation grepped
from the code — a large batch with real per-entry effort, not pure
transcription. Rather than either quietly doing a fraction of the literal
instruction or unilaterally expanding scope to all 57, the choice was put
to the user directly (three options: full migration, representative first
wave, harness-only). This is not a re-scoping of the underlying plan —
§9.5 already anticipated migration happening incrementally ("verified as
Stage A's compatibility-harness work runs through them"), so remaining
rows are still fully in scope, just not yet done.

**What was rejected:** doing all ~57 entries in this session (rejected by
the user for cost/thoroughness tradeoff reasons) and doing harness-
scaffolding-only with zero new entries (rejected in favour of getting real,
citable content into the register now).

**Follow-up:** the remaining In-Scope-table rows (Transactions, Account
Names, Amounts, Comments sections of `dev-docs/hledger-compatibility.md`)
are still unmigrated — this is tracked in `ROADMAP.md`'s Stage A row and
`CONTEXT.md`, not silently dropped.

## 2026-09-12 — Relicensed MIT → GPL-3.0-or-later

**Decision:** ledgerkit moves from the MIT License to GPL-3.0-or-later,
effective from the first release after this date. Already-published
releases (through `1.0.0`/`1.0.0.dev1`) remain MIT.

**Why:** hledger itself is GPL-3.0-or-later (confirmed from `license:`
fields in `hledger.cabal`/`hledger-lib.cabal`, not inferred from the
`LICENSE` file text alone). Matching it allows Ledgerkit development to use
hledger's documentation, source, and test suite directly as compatibility
evidence, with recorded provenance, instead of maintaining a self-imposed
clean-room separation. See
`dev-docs/planning/core-redefinition/02-licence-migration.md` and
`10-source-assisted-development.md` for the full reasoning, including the
important nuance that *reading* GPL source was never restricted by
licence mismatch — what actually changes is that Ledgerkit can now
lawfully host directly-translated hledger expression, should that ever
occur, which it could not under MIT.

**Known consequence, accepted deliberately:** `ledgerkit-editor` imports
`ledgerkit` in-process (not via subprocess) — confirmed by inspecting its
actual source (`ledgerkit.Query`, `ledgerkit.EditorDocument`,
`ledgerkit.parse_string_lenient`, `ledgerkit.{models,reports,checks,parser,
commodity_style}`, `ledgerkit.{load,journal_to_text,transaction_to_text}`
are all used directly, most substantially in `filter_popup.py` and
`query_match.py`) — so a GPL library embedded in-process inside an MIT
application is not a stable long-term combination. **`ledgerkit-editor`'s
own relicensing is an explicit separate decision, made in that
repository, on its own timeline — not bundled into this change.** Any
*other* third party embedding `ledgerkit` in-process faces the same
constraint going forward; this was weighed explicitly (see the licence
migration doc's options table) and accepted in favour of exactly matching
hledger's licence family, rather than choosing LGPL for library-friendliness.

**Rejected alternatives:** LGPL-3.0-or-later (library-friendly, but doesn't
literally match hledger's licence); restructuring `ledgerkit-editor` to a
subprocess boundary instead of relicensing it (disproportionate rewrite of
its editor-integration layer, which exists specifically for in-process
access); dual-licensing (ongoing administrative overhead not justified for
a single-maintainer project).

**Applies to:** `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`,
`pyproject.toml`, `README.md`, `CONTRIBUTING.md`, `dev-docs/versioning.md`,
`ledgerkit/__init__.py`, and (separately) the `ledgerkit-editor` repository.

**Addendum, 2026-09-12 (same day, CI-driven correction):** the initial
commit used a PEP 639 `license = "GPL-3.0-or-later"` SPDX string, verified
only locally, which broke CI's Python 3.8 job. Reverted to the classic
`license = {text = "GPL-3.0-or-later"}` form (kept alongside the `License ::`
classifier), which is exactly the pattern the prior MIT declaration used
successfully across the full 3.8–3.12 matrix. See
`knowledge/ANTIPATTERNS.md` — "PEP 639 `license` string-expression while
still supporting Python 3.8".

---

## 2026-04-15 — Parser silently accepts unbalanced transactions

**Decision:** `parse_string` does not validate that postings sum to zero. Unbalanced transactions are stored as-is and only rejected later by `checks.py`.

**Why:** The parser's job is to produce a structural model from text. Balance validation is a semantic check that belongs at the reports/checks layer, where the caller can decide whether to enforce it.

**Rejected alternative:** Raising `ParseError` in the parser when postings don't balance.

**Applies to:** `ledgerkit/parser.py`, `ledgerkit/checks.py`

---

## 2026-04-15 — Posting indentation is conventional, not required

**Decision:** The parser does not enforce 2-space or tab indentation on posting lines. Any non-header line inside an open transaction block is treated as a posting.

**Why:** hledger 1.52 documents indentation as conventional. Enforcing it would reject valid journals and contradict the compatibility spec.

**Rejected alternative:** Strict `line.startswith("  ") or line.startswith("\t")` gate (was the original implementation; removed).

**Applies to:** `ledgerkit/parser.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-04-17 — Only `.journal` and `.ledger` file formats supported

**Decision:** `load_journal()` and the `include` directive only accept `.journal` and `.ledger` extensions. All other hledger format families (`.csv`, `.timeclock`, `.timedot`, `.rules`, `.prices`, `.ledger-json`) raise `ParseError`.

**Why:** The other formats require fundamentally different parsers. Supporting them is a future milestone, not v1.

**Rejected alternative:** Silently ignoring unsupported formats or accepting any extension.

**Applies to:** `ledgerkit/loader.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-04-17 — File I/O extracted to `loader.py`; `parser.py` is pure text-only

**Decision:** `parse_file()` was removed from `parser.py`. All file reading, include resolution, and glob expansion live in `loader.py`. `parse_string()` is the only public entry point in `parser.py`.

**Why:** Separates concerns cleanly. The parser is a pure function (text → Journal); the loader handles I/O, paths, and multi-file merging. Easier to test each in isolation.

**Rejected alternative:** Keeping `parse_file()` in `parser.py` alongside `parse_string()`.

**Applies to:** `ledgerkit/parser.py`, `ledgerkit/loader.py`

---

## 2026-04-xx — `alias` directive is file-scoped at parse time

**Decision:** Aliases apply to account names within the file they are declared in, processing them at parse time. They are not propagated to including files.

**Why:** Matches hledger 1.52 semantics. Applying aliases globally would cause surprising account rewrites in unrelated included files.

**Rejected alternative:** Accumulating aliases across all included files and applying them in a post-processing pass.

**Applies to:** `ledgerkit/parser.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-04-xx — `decimal-mark` directive only applies forward, not retroactively

**Decision:** A `decimal-mark` directive only affects amount parsing for postings that appear *after* it in the file. Postings before the directive use the previous decimal mark (default: period).

**Why:** This matches hledger's streaming-parse model. Retroactive application would require a two-pass parser.

**Rejected alternative:** Applying the decimal mark to all transactions in the file regardless of position.

**Applies to:** `ledgerkit/parser.py`

---

## 2026-04-27 — `assert amt is not None` over `self.assertIsNotNone()` for type narrowing

**Decision:** In tests, bare `assert x is not None` is used (not `self.assertIsNotNone(x)`) immediately after extracting a `Posting.amount` field.

**Why:** Pylance recognises bare `assert` as a type-narrowing guard and eliminates `reportOptionalMemberAccess` warnings. `self.assertIsNotNone()` does not narrow the type in Pylance's analysis.

**Rejected alternatives:** `cast()`, `# type: ignore`, `if x is None: self.fail(...)`.

**Applies to:** `tests/test_parser/test_parser.py`, `tests/test_directives/test_directives.py`

---

## 2026-04-27 — Minor version bump (0.2.0) for new milestone

**Decision:** Version bumped from `0.1.2` → `0.2.0` when starting Milestone 2.

**Why:** Minor version increments mark the start of a new milestone (new user-visible feature area). Patch versions are used for fixes and admin changes within a milestone.

**Rejected alternative:** Continuing to bump patch version (0.1.3, 0.1.4, …) indefinitely.

**Applies to:** `ledgerkit/__init__.py`, `pyproject.toml`

---

## 2026-04-27 — Test subdirectories require `__init__.py`

**Decision:** Every test subdirectory (`test_parser/`, `test_directives/`, etc.) has an explicit `__init__.py`.

**Why:** Python 3.13's `unittest discover` silently skips namespace-package subdirectories (those without `__init__.py`). Without the file the tests are simply not found, with no warning.

**Rejected alternative:** Using namespace packages (no `__init__.py`).

**Applies to:** `tests/` subdirectories

---

## 2026-05-03 — `assertions` added to `BASIC_CHECK_NAMES` (not `OTHER_CHECK_NAMES`)

**Decision:** The `assertions` check runs automatically (basic tier) on every CLI command, not as an opt-in named check.

**Why:** hledger treats balance assertions as automatic — they are enforced at journal-load time rather than requiring explicit invocation. Adding them to `OTHER_CHECK_NAMES` would mean users could silently ignore assertion failures unless they explicitly ran `check assertions`, which defeats the purpose.

**Rejected alternative:** `OTHER_CHECK_NAMES` placement, which would match the existing pattern for `payees`, `ordereddates`, etc.

**Applies to:** `ledgerkit/checks.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-05-03 — Balance assignments deferred (not validated in Milestone 2)

**Decision:** The parser accepts `= AMOUNT` syntax with no preceding posting amount (balance assignment — where the assertion implies the posting amount). It stores `posting.amount = None` and `posting.balance_assertion` as normal, but `check_assertions` does not infer the elided amount from the assertion.

**Why:** Balance assignments are a distinct feature from balance assertions. Implementing them correctly requires inferring the posting amount (affecting `check_autobalanced`) and potentially the order of check evaluation. Scoped out to keep Milestone 2 focused.

**Rejected alternative:** Raising a `ParseError` when a balance assignment is encountered (too strict — valid hledger files should load without error even if the assignment isn't validated).

**Applies to:** `ledgerkit/parser.py`, `ledgerkit/checks.py`

---

## 2026-09-17 — Tag/date-override resolution as pure functions, not a `Posting.transaction` back-reference

**Decision:** `Posting.date_override`/`date2_override` resolve against their
owning `Transaction`'s dates via free functions, `tags.effective_date(txn,
posting)` and `tags.effective_date2(txn, posting)`, taking both objects as
arguments. No `Posting.transaction` back-reference field was added.

**Why:** Ledgerkit's existing model design has no back-references anywhere
(`Posting` doesn't point to its `Transaction`; `Journal` doesn't get
pointed to by anything it contains). Adding one back-reference for this
one feature would be an inconsistent one-off, would break `Posting`
equality/hashing (a cycle, or a field that would need `compare=False` and
`repr=False` special-casing), and isn't needed — every call site that has
a `Posting` also has the `Transaction` it came from (transactions are
always iterated as `(txn, posting)` pairs in `parser.py`, `checks.py`,
`reports.py`).

**Rejected alternative:** `Posting.transaction: Transaction` back-reference
field, proposed in `dev-docs/planning/core-redefinition/
20-tag-parsing-syntax-brief.md` §7 as an open question for the lead to
decide; rejected by the user via `AskUserQuestion` in favour of the
pure-function form.

**Applies to:** `ledgerkit/tags.py`, `ledgerkit/models.py`

---

## 2026-09-17 — New `ledgerkit/tags.py` module rather than adding to `parser.py`

**Decision:** Tag-extraction logic (`parse_tags`, `_parse_comment_line_tags`,
`_tag_name_before_colon`) and date-override resolution
(`effective_date`/`effective_date2`) live in a new `ledgerkit/tags.py`
module. `parser.py` imports and calls into it; it contains no
tag-extraction logic of its own beyond wiring the results onto model
fields at the point a comment is fully assembled.

**Why:** `parser.py` was already 1547+ lines, over the 300–500 line
module-size signal in `CLAUDE.md`. Adding a self-contained, independently
testable unit of logic (pure functions, no shared state with the parser's
state machine) as a new module avoids growing the already-oversized file
further, without requiring the user-approval-gated "split `parser.py`"
refactor that the size signal would otherwise call for.

**Rejected alternative:** Adding the functions directly to `parser.py` as
private helpers (would have pushed the file further over threshold for no
structural benefit, since the logic doesn't share state with the parser's
line-by-line state machine).

**Applies to:** `ledgerkit/tags.py`, `ledgerkit/parser.py`

---

## 2026-09-17 — `tags.parse_tags` is an adapted implementation, not directly translated material

**Decision:** `ledgerkit/tags.py`'s `parse_tags`/`_parse_comment_line_tags`
is recorded as an **adapted implementation** of hledger's tag-extraction
grammar (`commentlinetagsp`/`commenttagsanddatesp` in
`hledger-lib/Hledger/Read/Common.hs`), not directly translated material,
per the categories in `dev-docs/planning/core-redefinition/
10-source-assisted-development.md` §10.3.

**Why:** The Python implementation is an independent iterative
scan-and-split loop over a comment line, verified against hledger's
*observable* grammar (its manual, doctests, and `check-tags.test`) rather
than transcribed from the Haskell parser-combinator source. It does not
mirror `commentlinetagsp`'s recursive combinator structure, uses no
Haskell-specific idioms, and was written by reasoning about output
behaviour on test cases (e.g. the `Data.Text.split isSpace` vs Python
`str.split()` trailing-empty-token difference was reasoned through
explicitly, not copied). This determination was required by the brief
itself (`20-tag-parsing-syntax-brief.md`, "directly-translated-material
assessment"), which flagged the risk and asked the lead to make and record
the call rather than leaving it implicit.

**Rejected alternative:** Recording it as directly translated material
(would require a `THIRD-PARTY-NOTICES.md` entry and `directly_translated:
true` in the relevant compat-register entries) — rejected because the
implementation shape genuinely differs, per the reasoning above.

**Applies to:** `ledgerkit/tags.py`, `dev-docs/compat-register/
LK-COMPAT-PARSER-TAG-001.yaml`

---

## 2026-09-17 — `depth:` modelled as a `DepthSpec` report option, never a `QueryNode`

**Decision:** `ledgerkit.query.ast.Depth` (Stage C Phase 1's pure boolean
exclusion predicate) is removed from the selection-predicate AST
entirely. `depth:N`/`depth:REGEX=N` in a `-q` query string produce a
`ledgerkit.query.depth.DepthSpec` on `QueryPlan.depth` instead — a
report-display clipping/aggregation option consumed by `reports.py`, not
something `ledgerkit.query.eval.matches_posting`/`matches_transaction`
ever sees.

**Why:** a full trace of every hledger command that consumes a `Query`
(`MultiBalanceReport.hs`, `PostingsReport.hs`, `EntriesReport.hs`,
`Accounts.hs`, `AccountTransactionsReport.hs`) found every one strips
`Depth`/`DepthAcct` out of the query used to select postings *before*
selection happens, and re-derives a `DepthSpec` purely for display
truncation/aggregation. `depth:` is never a real selection predicate in
any hledger command's actual behaviour, despite the `Depth` constructor's
own `matchesAccount` function existing and being real — Phase 1 mistook
"this function exists and is unit-tested" for "this function is what a
user's `depth:` query actually does." See `dev-docs/planning/
core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md` §1.3
for the full source citations and live-binary confirmation.

**Rejected alternative:** keeping `Depth` as the string-grammar's
`depth:` handler and accepting the divergence as `intentional_divergence`
(the Phase 2-4 status quo) — rejected because a real fix was available
and the divergence provided no offsetting value; nothing depended on the
old exclusion behaviour (shipped only days earlier, no external users).

**Applies to:** `ledgerkit/query/ast.py`, `ledgerkit/query/parser.py`,
`ledgerkit/query/eval.py`, `ledgerkit/query/depth.py`, `ledgerkit/reports.py`

---

## 2026-09-17 — `Query.depth`/`ReportSection.depth` stay flat-only; the richer `DepthSpec` is not retrofitted onto them

**Decision:** the pre-existing public `models.Query.depth: int | None`
and `models.ReportSection.depth: int | None` fields are **not** retyped
to `DepthSpec`. The richer custom-`REGEX=N`/multi-term form is reachable
only via the `-q` CLI string grammar and `ledgerkit.query.depth`
directly, not through the older Python-API `Query`/`ReportSection`
dataclasses.

**Why:** retyping a currently-shipped public field is a breaking change
to existing callers for no demonstrated need — nothing in this phase's
scope required `Query.depth` to grow regex support, and the two
mechanisms (legacy flat `Query.depth`, newer `-q`-driven `DepthSpec`) can
coexist: `reports._effective_depth_spec` already reconciles them (prefers
`_query_depth` when supplied and non-empty, else wraps `query.depth` as
`DepthSpec(flat=query.depth)`).

**Rejected alternative:** retyping `Query.depth`/`ReportSection.depth`
to `DepthSpec` directly, unifying the two representations — rejected as
unnecessary API churn; can be revisited if a real need for regex-depth
via the Python `Query` API surfaces.

**Applies to:** `ledgerkit/models.py`, `ledgerkit/reports.py`

---

## 2026-09-17 — Old exclusion-predicate `Depth` kept as `MaxAccountLevel`, Python-API-only, no `-q` string syntax

**Decision:** the removed `ast.Depth` node is not deleted outright — it's
renamed to `MaxAccountLevel` and kept as a disclosed, Ledgerkit-native
boolean predicate, reachable only by constructing the `QueryNode` object
directly in Python. `ledgerkit.query.parser.parse()` never produces one —
there is no `-q` string spelling for it at all, `depth:` included.

**Why:** the underlying predicate ("is this posting at or shallower than
depth N") is a real, independently useful primitive with no other
spelling in the AST, and deleting working, tested code purely because its
name collided with hledger's own token would be needlessly destructive.
But keeping it reachable under the literal `depth:` string — even as a
documented divergence — was rejected: reusing hledger's own exact token
for different semantics is a durable trap for anyone who reasonably
assumes `depth:` means what it means everywhere else, and fails the
register schema's own `extension_requires_explicit_syntax` bar
structurally (an extension must be reachable only via syntax that
doesn't collide with upstream).

**Rejected alternatives:** (a) delete `Depth` entirely — rejected, see
above; (b) give it a new non-colliding string token (e.g. `levelmax:N`)
reachable from `-q` — rejected as unnecessary complexity for a primitive
that, so far, has no demonstrated Python-API caller at all; can be
revisited if one appears.

**Applies to:** `ledgerkit/query/ast.py`, `ledgerkit/query/eval.py`

---

## 2026-09-17 — No standalone `--depth`/`-N` CLI flag this phase

**Decision:** Stage C Phase 5 fixes `-q "depth:N"`'s semantics but does
not add a standalone `--depth`/`-N` CLI flag independent of `-q` (which
hledger itself treats as equivalent: `depth:2` ≡ `--depth=2` ≡ `-2`).

**Why:** the phase's approved scope was correcting `depth:`'s semantics,
not expanding CLI surface area; `-q "depth:N"` already gives full access
to the corrected behaviour (general and custom-regex forms alike) without
a new flag. Keeps this phase's diff focused on the actual defect.

**Rejected alternative:** adding `--depth`/`-N` in the same phase —
deferred as a named, explicitly-scoped follow-on instead
(`21-stage-c-phase-5-depth-and-verification-plan.md` §9, gate G-DEPTH-4).

**Applies to:** `ledgerkit/cli.py`

---

## 2026-09-17 — `stats`'s depth-exclusion quirk replicated exactly, not treated as a divergence

**Decision:** `reports.stats()`'s `account_count`/`account_depth` fields
use `ledgerkit.query.depth.account_excluded_by_depth` — a genuine
EXCLUSION rule — rather than `clip_account_name` (the clipping rule every
other depth-aware report function here uses).

**Why:** hledger's own `Ledger.hs:ledgerFromJournal`, which `stats`
alone (of the commands Ledgerkit tracks) builds its account list from,
has a doc-comment stating plainly: "If the query includes a depth limit,
the ledger's journal will be depth limited [excluded], but the ledger's
account tree will not [clipped]." This is a real, narrow, source-
confirmed exception specific to `stats` — verified live against the
pinned 1.52.4 binary on two independent scenarios (a single custom-regex
depth, and a mixed custom+general combination), both reproducing
hledger's exact `Accounts: N (depth D)` output. Choosing NOT to replicate
this quirk (i.e. clipping `stats`' counts too, for internal Ledgerkit
consistency) was considered and rejected: the whole point of this phase
was matching hledger's actual observable behaviour, and this is
observable, real, and now verified — treating it as "too weird to bother
matching" would have been arbitrary.

**Rejected alternative:** clipping `stats`' account_count/account_depth
like every other depth-aware function, for internal consistency across
Ledgerkit's own reports — rejected in favour of hledger-accuracy, given
the exception is real and now confirmed, not speculative.

**Applies to:** `ledgerkit/query/depth.py`, `ledgerkit/reports.py`

---

## 2026-09-25 — `tag:` matches hledger's complete four-source effective-tag semantics (Option A), not a disclosed own-tags-only subset (Option B)

**Decision:** Stage C Phase 6's `tag:NAME[=REGEX]` implements hledger's
full, verified effective-tag semantics: a posting's own literal comment
tags, its transaction's own tags, its account's declared-and-inherited
tags (walking every ancestor, not just the exact declared account), and
its main amount's commodity's declared tags — unioned with **no
shadowing/exclusion logic**, per `23-tag-query-matching-design.md` §2.7's
executable finding that hledger's manual "posting tags override account
tags override commodity tags" wording does not mean exclusion for
query-matching: same-named, differently-valued tags from every source
remain simultaneously, independently matchable. This required building a
genuinely new commodity-tag substrate (`Journal.declared_commodity_tags`,
mirroring `declared_account_tags`'s shape; `commodity` directive comment
capture in `parser.py`, mirroring the existing `account`-directive
tag-capture code path) alongside the account-inheritance computation.

**Why:** Option B (own-tags-only, no account inheritance, no commodity
propagation) would have shipped faster but left a real, disclosed gap
covering **two** of the four sources real hledger journals commonly use
— materially bigger than a single-source gap, with no evidence either
missing source was individually more tractable to defer. The commodity-
tag substrate work is structurally a close parallel to Phase 4's own
already-successful `account`-directive tag-capture work (same shape:
capture same-line + follow-on comment tags, store in a
`dict[str, list[tuple[str, str]]]`), not novel risk. See design §9.1's
own recommendation, unchanged in direction from its original framing.

**Rejected alternative:** Option B — a disclosed Ledgerkit-native subset
(own tags only), mirroring the `MaxAccountLevel` precedent. Rejected
because the resulting gap (two missing sources, not one) was judged too
large relative to the marginal implementation cost of doing it properly,
and the commodity substrate work was not genuinely separable risk.

**Applies to:** `ledgerkit/models.py`, `ledgerkit/parser.py`,
`ledgerkit/tags.py`, `ledgerkit/query/ast.py`, `ledgerkit/query/eval.py`

---

## 2026-09-25 — Evaluator API shape: `journal: Journal | None = None`, not a context object or pre-materialised storage

**Decision:** `matches_transaction`/`matches_posting` (`ledgerkit/query/
eval.py`) each gained one new parameter, `journal: Journal | None = None`
— a real default, so every existing caller that never constructs a `Tag`
node keeps compiling and running unchanged. A `Tag` node evaluated with
`journal=None` raises `ValueError` (not `TypeError` — deliberately
distinguishing "caller's fault, journal context was available and should
have been passed" from a genuine internal correctness bug), never
silently narrowing to own-tags-only.

**Why:** all four existing call sites (`reports.py`'s
`balance`/`register`/`accounts`/`stats`, `cli.py`'s `print`) already had
`journal` in their own enclosing scope, so a plain optional parameter is
the least invasive of the three candidates design §9.1 raised (a
`journal` parameter; a bundling context object; pre-materialised
effective-tag storage computed before evaluation runs). A context object
would have been justified only if more cross-cutting evaluator needs were
anticipated beyond this one; none are. Pre-materialising into new storage
was considered (it would avoid touching `matches_transaction`/
`matches_posting`'s signatures at all) but rejected as needless indirection
for a computation (`ledgerkit.tags._effective_tags`) that is already cheap
and pure — there is no performance or architectural reason to precompute
and cache it separately.

**Rejected alternatives:** a context-object parameter (deferred — no
second cross-cutting need exists yet to justify the extra abstraction);
pre-materialised effective-tag storage computed once before query
evaluation (rejected — needless indirection over an already-cheap pure
computation, and would have broken the on-demand-computation style
`ledgerkit/tags.py` already established for `effective_date`/
`effective_date2`).

**Applies to:** `ledgerkit/query/eval.py`, `ledgerkit/reports.py`,
`ledgerkit/cli.py`

---

## 2026-09-25 — `accounts -q "tag:X"` replicates hledger's narrower visibility, not uniform matching

**Decision:** `ledgerkit.reports.accounts` dispatches `Tag` nodes through
a private `ledgerkit.query.eval._matches_posting_for_accounts` wrapper
instead of the ordinary `matches_posting` — using
`ledgerkit.tags._accounts_effective_tags` (transaction-own +
account-inherited tags only, excluding posting-own and
commodity-propagated tags) rather than the full four-source
`_effective_tags` every other command uses. Every other `QueryNode` type
behaves identically either way; `balance`/`register`/`print`/`stats` are
completely unaffected by this wrapper's existence.

**Why:** design §2.5/§9.2 found this is a real, source-confirmed hledger
quirk (`journalPostingsKeepAccountTagsOnly` composed with
`postingAllTags`'s unconditional `++ ttags`), now four-way executable-
confirmed, and narrow to implement — one command, one matching-mode
substitution, no `DepthSpec`-style side-channel needed (unlike `depth:`'s
own Phase 5 redesign). The design's original recommendation favoured
uniform matching for internal consistency; that recommendation was
explicitly reconsidered and reversed before implementation planning,
on the grounds that "avoid a second special case" is not, by itself, a
strong enough reason to choose a disclosed, easily-avoidable divergence
from real hledger behaviour over a small, well-understood amount of extra
matching logic that directly reuses machinery (`_inherited_account_tags`)
the full computation already needs.

**Rejected alternative:** uniform matching — `accounts` using the same
`_effective_tags` as every other command, disclosed as an
`intentional_divergence`. Rejected once the design's own re-assessment
found the divergence avoidable at low, well-understood cost.

**Applies to:** `ledgerkit/reports.py`, `ledgerkit/query/eval.py`,
`ledgerkit/tags.py`

---

## 2026-09-25 — `effective_tags` implemented as private `_effective_tags` (small judgment call resolving a naming inconsistency between design and plan)

**Decision:** the fourth new `ledgerkit/tags.py` helper is named
`_effective_tags` (leading underscore), not the unprefixed `effective_tags`
that both `23-tag-query-matching-design.md` §9.3's own illustrative naming
and `24-tag-query-matching-implementation-plan.md`'s file-by-file section
literally wrote.

**Why:** design §9.3's own resolution text is explicit and unambiguous —
"keep **all** new inheritance/commodity helpers **private** initially
(leading-underscore...)" — and separately names `effective_tags` itself
as one of the three helpers that resolution covers. The implementation
plan's file-by-file section lists four functions under a header reading
"All three new helpers **private**," with three of the four
(`_inherited_account_tags`, `_commodity_tags`, `_accounts_effective_tags`)
already spelled with a leading underscore and the fourth
(`effective_tags`) spelled without one — read most plausibly as the
plan simply carrying forward the design's own illustrative (pre-decision)
spelling for that one name rather than a deliberate reversal of §9.3's
express "all new helpers" resolution, since the plan states no rationale
for singling out exactly this one helper as the sole public exception,
and doing so would contradict the plan's own stated Unauthorised-Change-
Rule discipline against adding undisclosed public API surface. Treated
as the smallest reasonable resolution of a naming inconsistency between
two already-approved documents, not a new design decision — flagged in
the Stage C Phase 6 implementation retro per this project's standing
ambiguity-handling instruction.

**Applies to:** `ledgerkit/tags.py`, `ledgerkit/query/eval.py`

## 2026-09-25 — Empty-regex-pattern rejection is a breaking change, not backward-compatible, made pre-1.0

**Decision:** `ledgerkit.query.regex.validate_hledger_regex("")`/
`compile_hledger_regex("")` now raise `UnsupportedRegexConstructError`
instead of validating/compiling successfully. Documented explicitly as
an **intentional, behaviourally breaking compatibility/correctness
correction** made while Ledgerkit is still at `1.0.0.dev1` (pre-`1.0.0`),
not as "no public API change" or "backward-compatible" — both framings
were used in an earlier draft of the design document and corrected on
review before implementation (`dev-docs/planning/core-redefinition/
26-query-regex-empty-pattern-design.md`).

**Why:** real hledger 1.52.4 rejects an empty regex pattern at parse
time for every prefix that accepts one (`acct:`, `desc:`, `tag:`'s
name/value halves, `depth:`'s REGEX half); Ledgerkit previously accepted
an empty pattern as "matches anything, including empty" — a real,
independently-verified divergence (`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-
001`). The function signatures and `UnsupportedRegexConstructError`
itself are genuinely unchanged (so this is not a protected-surface
change under the Unauthorised Change Rule's signature-based definition),
but the documented *accepted-input behaviour* of two public functions
is changing — a call that used to succeed now raises. Calling that "no
API change" would be inaccurate; calling it "backward-compatible" would
be actively misleading, since existing code passing `""` intentionally
will now get an error where it previously got a match-everything
pattern. No version bump was made for this change — `dev-docs/
versioning.md`'s new "Breaking changes during the `1.0.0.dev1`
pre-release" section explains why: no stable `1.0.0` contract has
shipped yet for a MAJOR bump to signal against; the eventual `1.0.0`
release absorbs every pre-release breaking correction into one settled
contract. The rejection is scoped narrowly — only the literal empty
pattern **string** is rejected, not any pattern whose semantics merely
admit an empty match (`.*`/`a*`/`^$`/`()` all remain accepted) — a
broader "semantically admits empty" check was considered and explicitly
rejected as wrong, since real hledger accepts all four of those.

**Rejected alternative:** describing this as backward-compatible because
no released version ever depended on the old behaviour. Rejected because
"nothing has shipped yet" is not the same claim as "this doesn't change
documented behaviour" — the two are orthogonal, and conflating them
would set a bad precedent for how future pre-1.0 breaking changes get
described in `api-spec.md`/`CHANGELOG.md`.

**Applies to:** `ledgerkit/query/regex.py`, `dev-docs/api-spec.md`,
`dev-docs/versioning.md`

## 2026-09-25 — Compatibility-register mismatch resolution: rename-and-link, never an in-place `kind:` flip

**Decision:** resolving a `kind: unexplained_mismatch` compat-register
entry (once a fix lands and is independently verified) creates a **new**
entry under the settled `kind`/`KIND`-prefixed id it resolved into,
rather than editing the mismatch entry's own `kind:` field in place. The
original mismatch entry is retained untouched (never deleted or
overwritten) with a new `resolved_into`/`resolved_date` pair added, and
cross-linked from the new entry's `resolves:` field. Schema and process
documented generally in `dev-docs/compat-register/schema.md`'s
"Resolution lifecycle" section and `09-compatibility-system.md` §9.7 —
not specific to any one entry.

**Why:** the register's own filename/id convention
(`LK-<KIND>-<AREA>-<NNN>`, `KIND` tracking the `kind:` field directly,
`09-compatibility-system.md` §9.3) means a `MISMATCH`-prefixed id
classified `compatible` (or any other settled state) would contradict
itself — the id claims "still open," the field claims "resolved." An
earlier draft of the Stage C Phase 7 design proposed exactly this
in-place flip; caught and corrected on review before implementation.
Retaining the original entry (rather than deleting it) preserves the
historical record of what was actually observed, when, and by whom —
useful evidence if the same area ever regresses, and consistent with
this project's general "never rewrite history, only add" discipline
(already applied to retros).

**Also corrected in the same pass**: `implementation`/`tests` may be
empty for `kind: unexplained_mismatch` entries too (previously the
schema said "only for `kind: unsupported`," which didn't reflect that a
fresh mismatch, by definition, has no fix yet to cite). Never fabricate
a reference to satisfy the schema — an honest empty list is correct.

**Applies to:** `dev-docs/compat-register/schema.md`,
`dev-docs/compat-register/UNEXPLAINED.md`,
`dev-docs/planning/core-redefinition/09-compatibility-system.md`
