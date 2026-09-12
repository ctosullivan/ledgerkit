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

status: proposed | verified | final
  # proposed — hledger-researcher's reading; not yet run against the real binary
  # verified — compat-differential-tester has executed the comparison
  # final    — docs reconciled and cross-linked from hledger-compatibility.md
  # (unexplained_mismatch entries can only be `verified` — by definition
  #  they haven't resolved into a final classification yet)

verified_by: <agent or person>        # required once status != proposed
verified_date: <YYYY-MM-DD>           # required once status != proposed

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
- `implementation` and `tests` may be empty only for `kind: unsupported`
  entries describing something not yet built.
- `directly_translated: true` is rare and should be rare — most Ledgerkit
  code is an independent Python-native reimplementation informed by
  reading hledger (`10-source-assisted-development.md`'s "adapted
  implementation" category), which does not set this field.
