# 8. Accounting-semantics roadmap

## 8.1 Ordering rationale

The order below follows a genuine dependency chain, not just the task
prompt's suggested sequence (verified against it — they agree, because the
dependency chain is objectively real: you cannot value a balance without
prices, cannot compute a lot's gain without a cost basis, cannot compute a
cost basis without cost annotations already being retained rather than
discarded):

```
prices ──▶ costs ──▶ valuation ──▶ commodity conversion ──▶ account-type
   │                                                          semantics
   │
   └────────────────────────────────────────────────────▶ virtual posting
                                                             semantics
                                                                │
assertion/check semantics (extends existing, parallel track) ──┤
                                                                ▼
                                            lots ──▶ cost basis ──▶
                                            acquisition/disposal ──▶
                                            gains/losses
                                                    │
                                                    ▼
                                    generated transactions (periodic,
                                    auto-postings, forecasting) ──▶
                                    rewrite/close/transformation
```

## 8.2 Current-state prerequisites per item

| Item | Current Ledgerkit state | What must happen first |
|---|---|---|
| Prices | `P` directive parsed, stored in `Journal.prices`; **never applied** to any report | Nothing blocking — pure additive work: a valuation function consuming `Journal.prices` with "closest preceding date" semantics (already correctly stated as the rule in `knowledge/DOMAIN_RULES.md`) |
| Costs | `@`/`@@` cost annotations parsed, raw text stored in `Posting.cost_raw`, **never parsed into a structured `Amount`** | Parse `cost_raw` into a structured `Cost` type (unit vs total, per `models.py`'s existing dataclass conventions) |
| Valuation | Not implemented | Depends on Prices + Costs above |
| Commodity conversion | Explicitly "Not supported" (`hledger-compatibility.md`) | Depends on Valuation; hledger's `equity:conversion` convention needs its own compat-register entry either way (COMPATIBLE or INTENTIONAL_DIVERGENCE, decided with `hledger-researcher` + differential verification, not assumed here) |
| Account-type semantics | Not implemented (`Undecided/Future` in `hledger-compatibility.md`: "Account type inference from name prefixes") | No hard prerequisite — can start once `account` directive's `type:` tag is parsed (currently stripped/ignored) |
| Virtual postings | `ParseError` today (`()`/`[]` explicitly out of scope) | Parser change: recognise the syntax instead of rejecting it, before any semantics can apply |
| Assertion/check semantics | Substantial: `=`/`==`/`=*`/`==*` implemented and checked in date order; **balance assignments** (`= EXPECTED` implying the posting amount) parsed but not inferred (`knowledge/DECISIONS.md`, explicit known gap) | Balance-assignment inference is the concrete remaining gap; independent of the lots/valuation chain, can proceed in parallel |
| Lots | Lot annotations (`{cost}`, `[date]`, `(label)`) parsed and **discarded** today — explicit `dev-docs/hledger-compatibility.md` statement: "discarded (not stored v1)" | **Hard prerequisite:** parser must retain this data (`06-core-architecture.md` §6.3) before any lot semantics can exist at all |
| Cost basis | Depends on Lots + Costs | — |
| Acquisition/disposal | Depends on Cost basis | — |
| Gains/losses | Depends on Acquisition/disposal + Valuation | — |
| Generated transactions (periodic/auto) | Recognised and **skipped** today with a `ParseWarning` — explicitly deferred, not silently broken | Parser must retain the rule text (currently discarded along with skipping) before expansion logic can be built |
| Rewrite/close/transformation | Not implemented | No hard prerequisite beyond the model being stable; naturally sequenced last since it operates on the full accounting model |
| Import functionality "that belongs in Core" | Not implemented; task explicitly scopes this narrowly ("that belongs in Core" — most import/bank-integration work is an adapter, `01-product-goal.md` §1.6) | Needs its own scoping decision at Stage G time: which import concerns are Core (e.g. CSV-rules-directive parsing, since hledger treats `.rules` as part of its own format family) vs adapter (bank API integration, unambiguously out of Core) |

## 8.3 Staging (maps to `12-roadmap-migration.md`'s Stage E/F/G)

- **Stage E** — prices, costs, valuation, commodity conversion,
  account-type semantics, virtual posting semantics, assertion/check
  completion (balance assignments). All additive or parser-permissive
  changes; no existing behaviour changes.
- **Stage F** — lots, cost basis, acquisition/disposal, gains/losses,
  explicitly scoped to the hledger 1.52.x baseline's investment-accounting
  behaviour (hledger's own lot/investment semantics are one of its more
  intricate areas — `hledger-researcher` briefs are mandatory here before
  any implementation, not optional).
- **Stage G** — periodic transactions, auto postings, forecasting,
  rewrite/close/transformation, Core-scoped import functionality.

Each item above gets its own compat-register entry the moment it's
implemented (`09-compatibility-system.md`) — none of these ship as a bare
feature without a classification and executable-verified evidence trail.

## 8.4 What is explicitly not promised

Per `01-product-goal.md` §1.6, Core 1.0 does not require every item above
to be `COMPATIBLE` — an item can legitimately ship as `UNSUPPORTED`
(documented, deferred past 1.0) if Stage E/F/G evidence shows it's
disproportionate. The task's own Core 1.0 success criteria
(`12-roadmap-migration.md` §4) do not require exhaustive hledger parity.
