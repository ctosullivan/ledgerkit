# Knowledge wiki

Human-readable comparison/explanation pages. These pages **link to**
the real, authoritative compatibility-register entries at
`dev-docs/compat-register/` — they never restate or duplicate a
claim's own evidence. If this page and the linked register entry ever
disagree, the register entry is authoritative.

## `LK-COMPAT-CHECKASSERTIONS-001` — balance assertions

See `dev-docs/compat-register/LK-COMPAT-CHECKASSERTIONS-001.yaml`.

Covers hledger's four balance-assertion variants (`=`, `==`, `=*`,
`==*`). The register entry's own `reason` field already draws the
relevant boundary: balance *assignments* (implied-amount inference from
a bare assertion) are explicitly deferred and **not** claimed compatible
by this entry — a distinct, separate behaviour from the assertions this
entry does cover. Native `status: proposed` — not yet executable-verified
against a real hledger binary.

## `LK-COMPAT-DECIMALMARK-001` — `decimal-mark` directive

See `dev-docs/compat-register/LK-COMPAT-DECIMALMARK-001.yaml`.

Covers the `decimal-mark .` / `decimal-mark ,` directive and Ledgerkit's
matching restriction to exactly those two characters. Native
`status: proposed` — not yet executable-verified against a real hledger
binary.

## `LK-COMPAT-PARSER-TAG-COMMODITY-001` — commodity-directive comment tags

See `dev-docs/compat-register/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml`.

Native `status: verified`, with a real `verified_by`
(`compat-differential-tester`, a dispatch independent of the
implementing session) and `verified_date`. This is the one claim in
this register that also has an independently reviewed Axiom scope
manifest (`knowledge/scope-manifests/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml`)
— the combination of both is what lets Axiom's `get()` report
`derived.status: VERIFIED` with a non-null scope, rather than
`UNCERTAIN`, for this claim specifically.

## `LK-COMPAT-QUERY-TAG-001` — `tag:NAME[=REGEX]` query matching

See `dev-docs/compat-register/LK-COMPAT-QUERY-TAG-001.yaml`.

Also native `status: verified` with a real `verified_by`/`verified_date`
— but this claim **deliberately has no scope manifest**. It exists
alongside `LK-COMPAT-PARSER-TAG-COMMODITY-001` specifically to
demonstrate the contrast: a native `verified` claim with no
independently reviewed scope evidence stays `derived.status: UNCERTAIN`
(with `derived.scope: null`) under Axiom, never `VERIFIED` — the
presence or absence of a scope manifest is the only thing that differs
between the two claims' Axiom-derived outcomes.
