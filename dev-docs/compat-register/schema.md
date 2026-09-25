# Compatibility register — YAML schema

One file per entry, at `dev-docs/compat-register/LK-<KIND>-<AREA>-<NNN>.yaml`.
`dev-docs/compat-register/examples/` holds the two illustrative entries
drafted during Core-redefinition planning, kept as worked examples of the
schema — they are not part of the live register.

`KIND` ∈ `COMPAT` / `EXT` / `DIV` / `UNSUP` / `MISMATCH`.
`AREA` is a short slug matching the module/feature area, e.g. `QUERY`,
`PARSER`, `INCLUDE`, `LOTS`, `ASSERT`.

```yaml
id: LK-<KIND>-<AREA>-<NNN>          # stable, never reused, matches filename

area: <dotted path>                  # e.g. "query.regex", "parser.include"

kind: compatible | extension | intentional_divergence | unsupported
     | unexplained_mismatch

upstream:
  project: hledger
  compatibility_target: "<exact pinned version, e.g. 1.52.4>"
                                      # never "latest" — always the specific
                                      # version this entry was evaluated
                                      # against; re-verify and bump when the
                                      # baseline advances

ledgerkit:
  relationship: equivalent | superset | subset | incomparable
    # equivalent   — compatible: same behaviour
    # superset     — extension: does everything hledger does, plus more
    # subset       — unsupported/partial: intentionally does less
    # incomparable — divergence: genuinely different, not a superset/subset

compatibility:
  upstream_syntax_preserved: true | false
  extension_requires_explicit_syntax: true | false | n/a   # n/a unless kind: extension

reason: >
  Why this state was chosen. The engineering/product reason, not a
  restatement of the behaviour itself.

implementation:
  - <ledgerkit/module.py:function_or_class>

tests:
  - <tests/test_module.py::TestClass::test_name>

evidence:
  - kind: manual | source | executable | test
    ref: <URL, file:line, or exact command run>
    pinned_at: <version or commit — required for source/executable evidence>

status: proposed | self-verified | verified | final
  # proposed      — hledger-researcher's reading; not yet run against the real binary
  # self-verified — an actual hledger-vs-Ledgerkit comparison WAS run, with
  #                 real command output, but by the same identity/session
  #                 that implemented the feature under test — not yet
  #                 independently confirmed. Use this, never `verified`,
  #                 when independent review is deferred (dev-docs/
  #                 planning/core-redefinition/09-compatibility-system.md
  #                 §9.6). The lead may set this status directly.
  # verified      — compat-differential-tester, dispatched separately from
  #                 the implementing session, has executed the comparison
  #                 independently. The lead must NEVER write this status
  #                 into a register YAML directly — only a dispatched
  #                 compat-differential-tester agent's own output sets it.
  # final         — docs reconciled and cross-linked from hledger-compatibility.md
  # (unexplained_mismatch entries can only be `verified` — by definition
  #  they haven't resolved into a final classification yet)

verified_by: <agent or person>        # required once status != proposed
verified_date: <YYYY-MM-DD>           # required once status != proposed

resolved_into: LK-<KIND>-<AREA>-<NNN> # optional — set ONLY on a kind:
                                        # unexplained_mismatch entry, once a
                                        # fix has landed and been
                                        # independently verified. Points to
                                        # the NEW entry (a different id/
                                        # filename, kind: compatible/
                                        # extension/intentional_divergence/
                                        # unsupported) that now documents
                                        # current behaviour. See "Resolution
                                        # lifecycle" below.
resolved_date: <YYYY-MM-DD>           # required once resolved_into is set

resolves: LK-<KIND>-<AREA>-<NNN>      # optional — set on the NEW entry
                                        # created to resolve an old
                                        # unexplained_mismatch, pointing
                                        # back to it. Reciprocal to
                                        # resolved_into.

directly_translated: true | false     # optional, default false — set true only
                                        # for a near-line-for-line port of hledger's
                                        # own expression (not just its algorithm).
                                        # See 10-source-assisted-development.md §10.3:
                                        # requires a code comment citing the exact
                                        # hledger file/version/lines translated, and
                                        # a THIRD-PARTY-NOTICES.md entry, in addition
                                        # to setting this field.
```

## Field notes

- `reason` is the single most important field for the register's actual
  purpose (distinguishing intentional decisions from accidents) — an entry
  with a thin or missing `reason` should be treated as not yet ready for
  `status: final`, regardless of what `kind` it claims.
- `evidence` should normally include **at least one** `executable` item
  before `status` moves past `proposed`, per
  `09-compatibility-system.md` §9.4 — documentation/source evidence alone
  explains intent, not observed compatibility.
- `status: verified` is reserved for a separately-dispatched
  `compat-differential-tester` agent's own output — never write it into
  an entry directly from the implementing session, even with real
  executable evidence in hand. Use `status: self-verified` for that case
  instead. See `09-compatibility-system.md` §9.6 (added Stage C Phase 5)
  for the full tiered rule and why it exists.
- `implementation` and `tests` may be empty for `kind: unsupported`
  entries describing something not yet built, **and for `kind:
  unexplained_mismatch` entries** (corrected Stage C Phase 7,
  `26-query-regex-empty-pattern-design.md`) — a mismatch is, by
  definition, an observed disagreement nobody has resolved into a fix
  yet, so there is nothing real to cite for either field until a fix
  exists. **Never fabricate an `implementation`/`tests` reference on an
  `unexplained_mismatch` entry merely to satisfy this schema** — an
  empty list is the honest, correct value; a fabricated one is worse
  than an empty one. Every other `kind` is expected to have real,
  non-empty `implementation`/`tests` entries.
- `directly_translated: true` is rare and should be rare — most Ledgerkit
  code is an independent Python-native reimplementation informed by
  reading hledger (`10-source-assisted-development.md`'s "adapted
  implementation" category), which does not set this field.

## Resolution lifecycle (`kind: unexplained_mismatch` → a settled state)

Added Stage C Phase 7, generalised from a concrete case (`LK-MISMATCH-
QUERY-TAG-EMPTYVALUE-001`) but written to apply to **any** mismatch
entry, not just that one. `unexplained_mismatch` is never a resting
state (§9.2) — but resolving one does **not** mean editing its `kind:`
field in place. The register's own filename/id convention
(`LK-<KIND>-<AREA>-<NNN>`, `KIND` tracking `kind:` directly) means a
`MISMATCH`-prefixed id classified, say, `compatible` would contradict
itself — the id would claim "still open" while the `kind:` field claims
"resolved."

Instead, once a fix lands and is independently re-verified (a
genuinely separate `compat-differential-tester` dispatch, same rule as
any other first-time `status: verified` promotion, §9.6):

1. **Create a new entry** — a new `LK-<KIND>-<AREA>-<NNN>.yaml`, `KIND`
   matching whichever settled state the fix actually produced
   (`COMPAT`/`EXT`/`DIV`/`UNSUP`), with its own fresh `status: verified`/
   `verified_by`/`verified_date` and `resolves: <old id>` pointing back
   to the mismatch entry it resolves.
2. **Retain the original entry file — never delete or overwrite it.**
   Its `id`, `kind: unexplained_mismatch`, and original evidence stay
   exactly as filed — it remains the honest historical record of what
   was observed, when, and by whom. Add `resolved_into: <new id>` and
   `resolved_date:` to it, and nothing else; do not change its `kind`.
3. **Update `UNEXPLAINED.md`**: remove the resolved entry from the open
   "Open entries" table (its own stated rule already requires this —
   an entry appears there only while genuinely open) and add a row to
   a "Resolved" table instead, linking both ids, so the resolution
   stays discoverable rather than silently vanishing.
4. **Update every cross-reference** to the old id (other compat-register
   entries' `reason:`/evidence text, `hledger-compatibility.md`,
   design/planning documents) to point readers to the new id going
   forward, while leaving the old file itself untouched as history.

This mechanism is deliberately general-purpose — any future
`unexplained_mismatch` entry resolves the same way, not just this one.
