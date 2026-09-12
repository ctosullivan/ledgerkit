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

status: proposed | verified | final
verified_by: <agent/person>
verified_date: <YYYY-MM-DD>
```

`status` tracks the register entry's own lifecycle (separate from `kind`,
which is the compatibility classification itself): `proposed` (by
`hledger-researcher`, not yet executable-verified), `verified`
(`compat-differential-tester` has run the comparison), `final` (docs
reconciled, register entry cross-linked from `hledger-compatibility.md`).
An entry with `kind: unexplained_mismatch` can only be `status: verified`
— by definition it hasn't been resolved into a final classification yet.

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
