# Decisions

Non-obvious judgment calls made during development. Each entry explains what was chosen, why, and what was rejected.

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
