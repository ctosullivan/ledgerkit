# Compatibility register

Machine-readable record of every classified behaviour distinguishing
Ledgerkit from hledger (or confirming they match). Full design rationale:
[`dev-docs/planning/core-redefinition/09-compatibility-system.md`](../planning/core-redefinition/09-compatibility-system.md).

See [`schema.md`](schema.md) for the field-by-field schema,
[`examples/`](examples/) for two illustrative entries drafted during
Core-redefinition planning (kept as worked examples, not part of the live
register), and [`UNEXPLAINED.md`](UNEXPLAINED.md) for the running
punch-list of open `unexplained_mismatch` entries.

**Status as of Stage A closeout (2026-09-12):** the harness itself —
schema, directory structure, and a first wave of real entries — is built.
25 entries have been migrated from `dev-docs/hledger-compatibility.md`'s
In Scope / Out of Scope tables (12 directive entries incl. one newly
drafted `intentional_divergence`, 8 validation-check entries, 5
`unsupported` entries), per the migration process in
`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.5.
**Every entry is `status: proposed`** — none has been executable-verified
against a real `hledger` binary yet. Moving any entry to `status: verified`
is `compat-differential-tester`'s job, from Stage C onward, and requires
an actual comparison run, not a citation of the manual.

**Amended Stage C Phase 5 (2026-09-17):** an audit found every entry this
project had actually moved past `proposed` so far (11, across Phases 2-4)
was marked `verified` by the same session that implemented the feature —
never by a separately-dispatched `compat-differential-tester`, contrary
to the paragraph above. See `09-compatibility-system.md` §9.6 for the
resulting tiered process and the new `status: self-verified` value
(`schema.md`), which records real-but-non-independent evidence honestly
instead of overclaiming `verified`.

**Correction (2026-09-13, superseded same day):** the original note above
about "no pinned hledger binary or clone exists" was only half right — a
full `hledger` **source** clone exists locally (used directly by
`hledger-researcher` for the Stage C query-semantics entries below,
pinned at tag `1.52.4`). It was then confirmed that a pinned `hledger`
**binary** also exists (`/home/cormac/.local/bin/hledger`, `hledger
1.52.4-g33fa849e7-20260910`), built from the exact same commit as the
source clone — see `09-compatibility-system.md` §9.1. `status: proposed`
remains accurate for every entry below regardless — the binary's
existence unblocks `compat-differential-tester`'s executable verification
work, it doesn't itself perform any verification. No entry has been
re-run against the binary yet.

**Stage C Phase 1 addition (2026-09-13):** 7 entries added for the initial
query-term set (`query.acct`, `query.desc`, `query.date` x2, `query.depth`,
`query.status`, `query.combinators`), proposed by `hledger-researcher`'s
semantics brief (`dev-docs/planning/core-redefinition/
17-query-semantics-brief.md`) and implemented in `ledgerkit/query/`. All
`status: proposed` — same caveat as above.

Not yet migrated: the finer-grained amount/comment/transaction-field-level
rows in the In Scope tables (dates, amount formats, comment forms, account
name rules) — a deliberate scope decision at Stage A closeout, recorded in
`knowledge/DECISIONS.md`, to prioritise the directive/check/unsupported
categories first. Migrating the remainder is follow-up work, not
abandoned scope.

## The five classification states

| State | Meaning |
|---|---|
| `compatible` | Matches hledger, executable-verified |
| `extension` | Ledgerkit does everything hledger does here, plus more, reachable only via explicit syntax |
| `intentional_divergence` | Deliberately different, for a stated and verified reason |
| `unsupported` | hledger has it; Ledgerkit deliberately doesn't (yet, or ever) |
| `unexplained_mismatch` | A differential test found disagreement nobody has explained yet — never a resting state |

**The goal is zero `unexplained_mismatch`, not zero difference from
hledger.**
