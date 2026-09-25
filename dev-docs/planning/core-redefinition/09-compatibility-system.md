# 9. Compatibility and extension system

## 9.1 Baseline

**hledger 1.52.x** is the compatibility target, pinned to a specific patch
release per evaluation (recorded per-entry, never "latest"), currently
`1.52.4` (published 2026-09-10, `prerelease: false` — verified via
`gh api repos/hledgerorg/hledger/releases`). hledger's `1.99.x` line
(`1.99.4`, 2026-09-11, `prerelease: true`) is pre-2.0 development and is
**monitored, not targeted** — see `06-core-architecture.md` §1.3 for the
architectural separation that keeps a future `hledger-2` profile possible
without rewriting Core.

This is not a new decision — `dev-docs/hledger-compatibility.md` already
says "Reference: https://hledger.org/1.52/hledger.html" throughout. This
plan formalises what was already the implicit target and gives it a
machine-readable form.

**Pinned binary confirmed (2026-09-13):** a real `hledger` executable
exists in this environment at `/home/cormac/.local/bin/hledger`,
reporting `hledger 1.52.4-g33fa849e7-20260910, linux-aarch64` —
confirmed to build from the exact same commit
(`33fa849e7ae841968bd21c427094c4fb4a4ec38d`, tag `1.52.4`) as the local
source clone at `/home/cormac/projects/hledger` that `hledger-researcher`
already used for the Stage C Phase 1 semantics brief. This is the pinned
reference `compat-differential-tester` runs against; its actual
executable-verification work (moving register entries from `proposed` to
`verified`) can now start — that work itself has not started yet, only
the binary's availability has been confirmed and recorded here.

## 9.2 The five states

| State | Meaning | Who can assign it |
|---|---|---|
| `COMPATIBLE` | Ledgerkit's behaviour matches hledger 1.52.x's, verified by running both against the same input | `compat-differential-tester` only, after executable verification |
| `EXTENDED` | Ledgerkit behaviour is a documented superset — the portable/hledger-compatible core still works, plus an additional Ledgerkit-only capability reachable only through explicit syntax | `compat-differential-tester` verifies the compatible core still holds; the extension itself is documented by `hledger-researcher`/lead, not "verified against hledger" (there is nothing in hledger to verify an extension against by definition) |
| `INTENTIONAL_DIVERGENCE` | Ledgerkit deliberately behaves differently from hledger, for a stated reason | Proposed by `hledger-researcher` or the lead with a written reason; confirmed by `compat-differential-tester` demonstrating the actual hledger behaviour it diverges from (so the divergence is precise, not vague) |
| `UNSUPPORTED` | hledger has this behaviour; Ledgerkit deliberately does not implement it (yet or ever) | Lead, recorded at the point a feature is scoped out (already partially done informally in `hledger-compatibility.md`'s "Out of Scope" table — this migrates that table into the register) |
| `UNEXPLAINED_MISMATCH` | A differential test found Ledgerkit and hledger disagreeing, and nobody has yet determined which of the four states above it should become | `compat-differential-tester` only — this is the **only** state a test failure produces automatically; it is never a resting state, only a to-do marker |

**North star metric:** drive `UNEXPLAINED_MISMATCH` count toward zero.
There is no metric or target for driving `INTENTIONAL_DIVERGENCE`,
`EXTENDED`, or `UNSUPPORTED` toward zero — those are legitimate, permanent
product decisions, not defects (directly restating the task's central
instruction, because it is easy for a compatibility-tracking system to
accidentally start optimising for the wrong number).

## 9.3 Register schema and storage

```
dev-docs/compat-register/
    README.md                 schema documentation (this section, expanded)
    schema.md                 the YAML schema itself, annotated
    examples/
        LK-EXT-QUERY-001.yaml       (extension — Python regex, drafted below)
        LK-DIV-INCLUDE-001.yaml     (intentional divergence — alias scoping
                                     across includes, backfilled from an
                                     already-known, already-documented
                                     deviation)
    UNEXPLAINED.md             running punch-list of open
                               UNEXPLAINED_MISMATCH entries — the metric
                               dashboard, kept short by construction
```

One file per entry, `LK-<KIND>-<AREA>-<NNN>.yaml` (`KIND` ∈
`COMPAT`/`EXT`/`DIV`/`UNSUP`/`MISMATCH`; `AREA` a short slug like `QUERY`,
`PARSER`, `INCLUDE`, `LOTS`). This mirrors CodeCompass's own numbered-file
convention for `decisions/` — a pattern already proven to scale for exactly
this "many small, individually-citable records" shape.

### Schema (matches the task's own example structure, filled in with real fields)

```yaml
id: LK-<KIND>-<AREA>-<NNN>
area: <dotted path, e.g. "query.regex", "parser.include", "accounting.lots">
kind: compatible | extension | intentional_divergence | unsupported | unexplained_mismatch

upstream:
  project: hledger
  compatibility_target: "1.52.4"   # exact pinned version this entry was
                                     # evaluated against — never "latest"

ledgerkit:
  relationship: equivalent | superset | subset | incomparable
  # equivalent   — same behaviour (compatible)
  # superset     — Ledgerkit does everything hledger does, plus more (extension)
  # subset       — Ledgerkit intentionally implements less (unsupported/partial)
  # incomparable — behaviour genuinely differs, neither a superset nor subset (divergence)

compatibility:
  upstream_syntax_preserved: true | false
  extension_requires_explicit_syntax: true | false | n/a

reason: >
  Why this state was chosen — the actual engineering or product reason,
  not a restatement of what the behaviour is.

implementation:
  - <ledgerkit file:function or module>

tests:
  - <test file::test_name>

evidence:
  - kind: manual | source | executable | test
    ref: <URL, file:line, or command run>
    pinned_at: <version/commit, for source/executable evidence>

status: proposed | self-verified | verified | final
verified_by: <agent/person>
verified_date: <YYYY-MM-DD>
```

`status` tracks the register entry's own lifecycle (separate from `kind`,
which is the compatibility classification itself): `proposed` (by
`hledger-researcher`, not yet executable-verified), `self-verified` (an
actual hledger-vs-Ledgerkit comparison was run, with real command output,
but by the same identity/session that implemented the feature under test
— see §9.6), `verified` (`compat-differential-tester`, dispatched
separately from the implementing session, has run the comparison
independently), `final` (docs reconciled, register entry cross-linked
from `hledger-compatibility.md`). An entry with `kind:
unexplained_mismatch` can only be `status: verified` — by definition it
hasn't been resolved into a final classification yet.

## 9.4 Relationship between documentation, source, executable, implementation, tests

```
hledger manual section  ──┐
hledger source           ──┼──▶  hledger-researcher's brief  ──▶  proposed
hledger test suite       ──┘        (documents intended            register
                                      semantics)                    entry
                                                                       │
                                                                       ▼
                                                          Ledgerkit implementation
                                                                       │
                                                                       ▼
                                                    compat-differential-tester runs
                                                    both the real hledger binary and
                                                    Ledgerkit against the same fixture
                                                                       │
                                                                       ▼
                                                        register entry finalised:
                                                    COMPATIBLE / EXTENDED /
                                                    INTENTIONAL_DIVERGENCE /
                                                    UNSUPPORTED / UNEXPLAINED_MISMATCH
                                                                       │
                                                                       ▼
                                                    Ledgerkit test(s) added, cited in
                                                    the entry's `tests:` field — the
                                                    test is what prevents regression;
                                                    the register entry is what explains
                                                    *why* the test asserts what it does
```

Documentation and source explain **intent**; the executable is the only
thing that verifies **actual observable compatibility** — this is the
task's own instruction restated precisely, and it's why `status: verified`
requires `compat-differential-tester`'s executable run specifically, never
just a citation of the manual.

## 9.5 Migration of currently-implicit classifications

`dev-docs/hledger-compatibility.md`'s existing "In Scope" / "Out of Scope"
/ "Undecided" tables are the raw material for the first wave of register
entries — this is transcription-with-verification, not new analysis:

- Every "Out of Scope (v1)" row → an `UNSUPPORTED` entry.
- The two already-known deviations (alias-scoping-across-includes,
  dot-file glob behaviour) → `INTENTIONAL_DIVERGENCE` entries (one drafted
  as an example, §9.3).
- Everything in "In Scope (v1)" → a `COMPATIBLE` entry, **pending actual
  executable verification** — this planning session did not run the real
  `hledger` binary against Ledgerkit's fixtures, so these should be created
  as `status: proposed` initially and verified as Stage A's compatibility-
  harness work runs through them, not asserted `verified` from the
  existing manual-only documentation.

## 9.6 Verification independence (amended Stage C Phase 5, 2026-09-17)

An audit of every register entry ever moved past `status: proposed`
across Stage C Phases 2-4 (`dev-docs/planning/core-redefinition/
21-stage-c-phase-5-depth-and-verification-plan.md` §1.1) found all 11 of
them were marked `verified` by the same session that implemented the
feature being classified — never by a separately-dispatched
`compat-differential-tester`, despite that role's own charter ("the only
role authorised to move a compat-register entry out of status:proposed")
already saying otherwise. This section makes that independence
structurally checkable rather than a convention to remember.

**Process overhead scales with claim strength, not change size:**

| Tier | Trigger | Requirement |
|---|---|---|
| 0 — no compatibility claim change | Ordinary implementation/refactor/bugfix touching no register entry's `kind`/`relationship`/`status` | Normal lead verification (tests + judgment). No dispatch. |
| 1 — proposed classification | A new entry drafted, or an existing entry's `reason`/`kind` proposed to change, not yet promoted past `proposed` | `hledger-researcher` (or the lead reading source/manual directly) proposes freely — already the correctly-followed process. |
| 2 — promotion to independently-verified truth | An entry's `status` is set to `verified` for the **first time**, or an already-`verified`/`final` entry's `kind`/`relationship` changes | MUST come from an actual `compat-differential-tester` Agent dispatch's own returned output. The lead never writes `status: verified` into a register YAML directly — see §9.3's `self-verified` value for what to use instead when independent review is deferred. |
| 3 — finalisation | `status: final` | Requires doc reconciliation (unchanged) AND the Tier 2 evidence packet (below) referenced from the entry, not just asserted to exist. |

Tier 0 is deliberately unchanged from today — the overwhelming majority
of day-to-day work never touches a register entry's `status`/`kind` at
all and is completely unaffected by this section.

**Making Tier 2 checkable, not just a convention:** a phase's retro
(`dev-docs/retros/`, already mandatory) must name, for every register
entry it touches, whether the entry ended the phase at `self-verified` or
`verified` — and if `verified`, cite the specific `compat-differential-
tester` dispatch that produced it. `release-phase-auditor` checks, for
any entry newly at `status: verified`/`final` in a phase's diff, that the
retro names an actual dispatch for it — a non-blocking observation if
not (it never repairs what it audits; it surfaces, the user decides).

**Evidence packet** — a fixed, compact shape the lead hands a Tier 2
dispatch so it never has to reconstruct context from scratch:

```
Ledgerkit revision:      <commit hash>
Upstream revision:       hledger <version>, commit <hash>, binary <exact version string>
Register entry:          <LK-...-NNN id(s) affected>
Fixture(s):              <path(s) under tests/fixtures/, or fixture text to create>
Commands to run:         <exact hledger command> vs <exact ledgerkit command>, per scenario
Proposed interpretation: <kind + relationship the lead believes applies, and why>
Prior evidence:          <what the lead already observed, explicitly labelled
                          self-verified / not yet independent>
```

`compat-differential-tester.md` already has the correct hard rules for
what happens once it receives this packet (never edit `ledgerkit/` to
make a mismatch disappear; report findings back, don't silently fix
them) — this section changes when it must be invoked, not what it does
once invoked.

## 9.7 Resolving an `unexplained_mismatch` entry (added Stage C Phase 7, 2026-09-25)

Two gaps found while resolving `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`
(empty-regex-pattern rejection, `dev-docs/planning/core-redefinition/
26-query-regex-empty-pattern-design.md`):

1. §9.3's schema said `implementation`/`tests` "may be empty only for
   `kind: unsupported` entries" — but a fresh `unexplained_mismatch`
   entry, by definition, describes an observed disagreement nobody has
   built a fix for yet, so it legitimately has nothing real to cite for
   either field either. **Corrected**: both fields may be empty for
   `unexplained_mismatch` entries too. Never fabricate a reference to
   satisfy the schema — an honest empty list beats an invented one.
2. There was no documented process for what happens to a mismatch
   entry's **identity** once it's actually resolved. Simply flipping its
   `kind:` field to the settled state it resolved into (e.g.
   `compatible`) would leave a `MISMATCH`-prefixed `id`/filename
   contradicting its own `kind:` field, since §9.3's filename convention
   ties `KIND` directly to `kind:`.

**Resolution mechanism** (full detail: `dev-docs/compat-register/
schema.md`'s "Resolution lifecycle" section — this is the design
rationale, that file is the operational reference): resolving a mismatch
creates a **new** entry (new id, `kind:` matching the settled state,
`resolves: <old id>`) rather than mutating the old one in place. The
original `unexplained_mismatch` entry is retained, untouched except for
a new `resolved_into: <new id>`/`resolved_date:` pair — it stays as
honest historical evidence of what was observed and when, not deleted or
overwritten. `UNEXPLAINED.md` moves the entry from its "Open entries"
table to a new "Resolved" table, cross-linking both ids, instead of
simply dropping the row. This mechanism is general-purpose — it applies
to any future `unexplained_mismatch` resolution, not only this one.
