# 2. Licence migration plan: MIT → GPL-3.0-or-later

## 2.1 Current state (verified)

| Item | Finding |
|---|---|
| `ledgerkit` LICENSE | MIT, `Copyright (c) 2026 Cormac O' Sullivan` |
| `ledgerkit` contributors | `ctosullivan` only (`gh api .../contributors`) — **sole copyright holder**, no CLA needed, no third party to ask |
| `ledgerkit` third-party code | None. Zero mandatory runtime deps; `pandas` is an optional, separately-licensed dependency the user installs themselves (BSD-3, not bundled) |
| `ledgerkit-editor` LICENSE | MIT, same sole author, same copyright holder |
| `ledgerkit-editor` → `ledgerkit` coupling | **In-process Python `import`** of `ledgerkit` (`EditorDocument`, `parse_string_lenient`, `writer`, `check_transaction_autobalanced`) — not a CLI subprocess call. Currently pinned `ledgerkit==1.0.0.dev1`, `textual==8.2.5` (MIT) |
| hledger LICENSE | `GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007` (root `LICENSE`, `hledger-lib/LICENSE`) |
| hledger's own SPDX declaration | `license: GPL-3.0-or-later` in **both** `hledger/hledger.cabal` and `hledger-lib/hledger-lib.cabal` (confirmed directly, not inferred from the `LICENSE` file's boilerplate text) |

**Conclusion:** the target identifier is exactly right — hledger itself is
`GPL-3.0-or-later`, not `GPL-3.0-only`, so aligning Ledgerkit to
`GPL-3.0-or-later` genuinely matches "the same licence family" rather than
a stricter or looser sibling of it.

## 2.2 The licensing problem this migration creates — must be resolved before it proceeds

GPL-3.0 is a **strong copyleft licence for a combined/derivative work**.
Ledgerkit is not just an end-user application (like hledger itself,
distributed as a compiled binary) — it is **also a Python *library***
imported in-process by at least one other program (`ledgerkit-editor`) that
is not itself GPL. Under the FSF's own interpretation, dynamically
importing a GPL library into the same process as a non-GPL program creates
a combined work whose distribution as a whole must be under GPL-compatible
terms. (Invoking a GPL program as an arm's-length *subprocess* — e.g.
shelling out to the `hledger` binary — is not the same thing and is not
restricted this way; this is exactly the distinction §10 relies on for why
"the hledger executable remains an independent behavioural oracle" doesn't
itself raise a licensing question.)

Concretely, relicensing `ledgerkit` to GPL-3.0-or-later as written today
would mean:

- `ledgerkit-editor`, as currently architected (in-process import), could
  no longer be lawfully distributed under MIT terms as a whole — its
  distributable combination with `ledgerkit` would need to be
  GPL-compatible.
- Any **third-party** application that `pip install`s `ledgerkit` and
  imports it in-process — the exact "lightweight dependency for
  applications" use case the new product goal explicitly wants to keep
  serving — faces the same constraint. This is a real tension inside the
  prompt's own goals: "match hledger's licence family" and "remain a
  lightweight dependency other Python applications can embed freely" pull
  in opposite directions once the dependency is a *library*, not an
  application. (This is precisely the gap LGPL exists to close — GPL is
  the right choice for an application; LGPL is the conventional choice for
  a library meant to be linked into non-copyleft programs.)

This is **not a reason to silently deviate from the instruction**. It is
the specific, concrete consequence the instruction's own "human approval
requirements" and "public product positioning" decision gates exist to
catch, and it is surfaced as **Gate G1** in `14-human-decision-gates.md`
rather than resolved unilaterally here.

Because `ctosullivan` is the sole copyright holder of **both** repositories,
every option below is legally available without needing anyone else's
consent — this is a product-direction decision, not a rights-clearance
problem.

### Options for Gate G1 (presented, not decided, here)

| Option | Effect | Trade-off |
|---|---|---|
| **A. GPL-3.0-or-later exactly as specified**, and relicense `ledgerkit-editor` to GPL-3.0-or-later too | Fully matches the instruction; both first-party repos consistent | Any *other* third party embedding `ledgerkit` in-process must also be GPL-compatible — narrows "lightweight dependency for applications" to GPL-compatible applications only |
| **B. GPL-3.0-or-later for Core, and restructure `ledgerkit-editor` to talk to Core only via CLI subprocess / IPC** | Keeps `ledgerkit-editor` MIT; keeps third-party embedding legally open via subprocess use | Non-trivial `ledgerkit-editor` architecture change (loses direct access to `EditorDocument`, `parse_string_lenient`, in-process typed objects — its entire editor-integration layer exists *because* in-process access was wanted); likely disproportionate cost for one consumer |
| **C. LGPL-3.0-or-later** (same GNU family, library-appropriate copyleft) | Preserves free in-process embedding by any licence (GPL or not), consistent with hledger's project *ethos* if not its exact identifier | Does not literally match "the same licence family used by hledger" as specified (hledger itself is GPL, not LGPL) — a deliberate, disclosed departure from the instruction's letter, in service of its "lightweight dependency" goal |
| **D. Dual-license** (GPL-3.0-or-later OR a commercial/permissive licence available on request) | Maximum flexibility | Adds ongoing licensing-administration overhead disproportionate to a single-maintainer open-source project |

**Resolved 2026-09-12: Option A, for `ledgerkit` Core only.** Executed:
see §2.3. `ledgerkit-editor`'s own relicensing is **explicitly out of
scope for this decision** — it is a separate decision made in that
repository, on its own timeline, not bundled into Core's migration (see
`14-human-decision-gates.md` G8). The tension described in §2.2 above
still applies and is not resolved by this choice — it simply means
`ledgerkit-editor`'s repository, not Ledgerkit Core's, decides how and
when to respond to it. §2.3's "if Gate G1 = Option A" subsection for
`ledgerkit-editor` below is retained as **reference for whenever that
repository takes up the decision itself**, not as work this session
performed or scheduled.

## 2.3 Migration steps (once Gate G1 is resolved)

### `ledgerkit` (Core)

1. Replace `LICENSE` with the full GPLv3 legal text (identical to hledger's
   `LICENSE` file — the legal text itself is standard and not
   project-specific).
2. Add the FSF-recommended short notice — the part that actually carries
   the "or later" grant — to a canonical location. hledger expresses this
   entirely through its Cabal `license:` metadata field rather than a
   per-file header; Ledgerkit should do the Python equivalent **plus** a
   short top-of-package notice, since Python packaging doesn't have a
   single authoritative metadata field the way Cabal does until a project
   fully adopts PEP 639:
   - `ledgerkit/__init__.py` docstring: short SPDX + copyright + "or later"
     notice.
   - `NOTICE` file at repo root (new): the full FSF "how to apply" notice
     with `Copyright (C) 2026 Cormac O'Sullivan` and the actual project
     name substituted in.
   - Per-file headers are **not** required by GPL itself and are not
     hledger's own practice (confirmed — hledger's per-file Haddock
     comments carry no licence header; licensing is declared once, at the
     package/cabal level). Ledgerkit should follow the same
     once-per-package pattern rather than inventing a heavier convention
     hledger itself doesn't use.
3. `pyproject.toml`:
   - **Executed as `license = {text = "GPL-3.0-or-later"}`** — the classic
     dict form, not a PEP 639 SPDX expression string. A string-expression
     form was tried first and reverted: it passed under a locally-installed
     recent `setuptools`, but broke CI's Python 3.8 job, because no
     `setuptools` release supports both Python 3.8 and the PEP 639 string
     schema, and `ledgerkit` still declares `requires-python = ">=3.8"`.
     Revisit the PEP 639 form only alongside an explicit, separately
     approved decision to drop Python 3.8 support — see
     `knowledge/ANTIPATTERNS.md`.
   - `License :: OSI Approved :: GNU General Public License v3 or later
     (GPLv3+)` classifier added alongside the dict-form field — the two
     coexist without conflict (only the newer string-expression form
     conflicts with a classifier under recent setuptools, confirmed by
     this same incident).
   - `description` and `keywords` are unaffected.
4. `README.md`: update the "Acknowledgements" section (already credits
   Ledger/hledger authors — extend it to state the licence relationship
   explicitly, since the acknowledgement previously only credited
   *inspiration*, not a shared licence family) and add a licence badge
   consistent with hledger's own README convention.
5. `CHANGELOG.md`: a dedicated, prominent `[Unreleased]` entry stating the
   relicensing as a **breaking change for consumers**, even though
   Ledgerkit's own `dev-docs/versioning.md` SemVer rules (API/CLI
   compatibility only) don't technically classify a licence change as
   MAJOR — recommend bundling the licence change with whatever version bump
   accompanies the Core redefinition's first shipped milestone, precisely
   so it's not a silent patch-level surprise for consumers pinning
   `ledgerkit`.
6. `CONTRIBUTING.md`: state that all future contributions are accepted
   under GPL-3.0-or-later (relevant the moment a second contributor shows
   up — currently moot with a sole author, but should be stated before it
   isn't moot).
7. **Already-published PyPI artifacts (`0.1.x`–`1.0.0`, `1.0.0.dev1`) stay
   MIT** — relicensing is not retroactive to bytes already shipped. Only
   the next release carries the new licence. State this explicitly in
   `dev-docs/versioning.md`.
8. Add a `THIRD-PARTY-NOTICES.md` (currently would be empty/near-empty —
   zero mandatory deps — but establishes the location before Stage
   E–G work potentially adds one, and before any directly-translated
   hledger material exists per `10-source-assisted-development.md`).

### `ledgerkit-editor` — reference only; a decision for that repository, not executed here

1. Same LICENSE/NOTICE/pyproject.toml/classifier treatment, `GPL-3.0-or-later`.
2. Its own third-party dependency review: `textual` (MIT — GPL-compatible
   one-directionally, no issue), `pytest`/`pytest-asyncio` (dev-only, not
   distributed, no issue).
3. `README.md` / `CHANGELOG.md` equivalent entries, cross-referencing the
   Ledgerkit relicensing as the reason.

### If Gate G1 selects Option B or C instead

- Option B: no `ledgerkit-editor` licence change; instead
  `docs/python-api.md` (Ledgerkit) and `ledgerkit-editor`'s own
  architecture docs get a new "Consuming Ledgerkit from a non-GPL
  application" section describing the subprocess/CLI boundary, and
  `06-core-architecture.md`'s CLI surface becomes a first-class contract
  rather than a convenience wrapper.
- Option C: identical steps to §2.3 above with `LGPL-3.0-or-later`
  substituted throughout; no `ledgerkit-editor` change needed at all.

## 2.4 Third-party licence review

- **Zero mandatory runtime dependencies today** — nothing to review for
  Core itself.
- **`pandas` (optional extra)**: BSD-3-Clause. GPL-compatible in the
  permitted direction (a GPL program may depend on a BSD library); no
  action needed regardless of which Gate G1 option is chosen.
- **Future Stage E–G work** may pull in nothing new by default (the
  "Core must not directly include DuckDB/pandas/ML as mandatory
  dependencies" boundary in `06-core-architecture.md` already prevents
  this) — flag that any *new* mandatory dependency proposed during Core
  development gets a licence-compatibility check against
  GPL-3.0-or-later before being accepted, added as a standing item in
  `CLAUDE.md`'s existing "Unauthorised Change Rule" (which already gates
  `pyproject.toml` dependency changes on explicit approval — this migration
  adds a licence-compatibility criterion to that existing approval step,
  not a new process).
- **hledger's own doc/manual licensing** is a separate question from its
  code licence and was **not** resolved in this planning session (the
  `hledger.org` manual pages and `doc/` tree may carry different terms,
  e.g. some plain-text-accounting documentation uses CC licences) — flagged
  as an open item in `10-source-assisted-development.md` §4, to be checked
  *before* any hledger manual text (example journals, worked examples) is
  copied verbatim into Ledgerkit's own docs or test fixtures. Independent
ly-authored Ledgerkit examples describing the same behaviour are unaffected
  regardless of the manual's licence.

## 2.5 Attribution and provenance (summary — full policy in §10)

- hledger / Simon Michael: acknowledged today in `README.md`; extended
  with the licence-family statement (§2.3.4).
- Ledger (John Wiegley): acknowledged today; unaffected by this migration
  (Ledgerkit does not use Ledger's source, only its documented format
  concepts, and Ledger itself is a separate, differently-licensed project
  not implicated by aligning with hledger's licence).
- Any future directly-translated hledger material gets its own
  per-instance provenance record in the compatibility register
  (`09-compatibility-system.md`) — this migration's job is only to make
  Ledgerkit's own licence *capable* of hosting that material lawfully, not
  to pre-authorise copying anything specific.

## 2.6 Human approval required for

Everything in this document is gated behind **Gate G1**
(`14-human-decision-gates.md`) before any file listed in §2.3 is touched.
