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

**Correction (2026-09-13):** the note above about "no pinned hledger
binary or clone exists" was only half right and is superseded — a full
`hledger` **source** clone exists locally (used directly by
`hledger-researcher` for the Stage C query-semantics entries below,
pinned at tag `1.52.4`); there is still no pinned `hledger` **binary**, so
`status: proposed` remains accurate until `compat-differential-tester`
has one to run against.

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
