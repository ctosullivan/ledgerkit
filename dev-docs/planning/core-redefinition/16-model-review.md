# 16. Journal/accounting model review (Stage B Phase 2)

Independent review of `06-core-architecture.md` §6.3's claim that
`models.py` needs "no structural change now" to later accommodate Stage
E/F's `Cost`/`Lot`/`PriceGraph`/valuation types
(`08-accounting-semantics-roadmap.md`). Read-only: `ledgerkit/models.py`,
`ledgerkit/parser.py`'s `account` directive handling, `dev-docs/api-spec.md`,
and `15-editor-compat-inventory.md`'s confirmed `ledgerkit-editor`
dependencies were all read directly; no `ledgerkit/`/`tests/` code changed.

## 16.1 Verdict

**Confirmed, with two guardrails** for whoever implements Stage E/F — the
claim isn't wrong, but it's only true if these two constraints are
followed rather than assumed:

## 16.2 Confirmed additive: Cost, Lot, virtual postings, valuation

- **Costs:** `Posting.cost_raw: Optional[str]` already exists (raw text
  only). Parsing it into a structured `Cost` type is a pure addition — a
  new `Posting.cost: Optional[Cost] = None` field alongside the existing
  one (or replacing it — either way, additive to the dataclass shape, no
  existing field needs to change type).
- **Lots:** `{cost}`/`[date]`/`(label)` annotations are currently parsed
  and fully discarded — `Posting` has no field for them at all today.
  Adding one (a single `Posting.lot: Optional[Lot] = None`, or several
  scalar fields) is a clean addition with zero existing-field conflict.
- **Virtual postings:** currently rejected outright with `ParseError`
  (`()`/`[]` syntax). Recognising them needs a new field (e.g.
  `Posting.posting_type: Literal["real","virtual","virtual_balanced"]` or
  an equivalent) — additive; nothing existing needs restructuring since
  the syntax isn't accepted at all today.
- **PriceGraph/valuation:** `PriceDirective` already exists
  (`Journal.prices`); valuation is new function/type surface consuming it,
  not a change to the existing dataclass.

None of these require touching `Transaction`'s or `Journal`'s existing
field shapes, and none require a breaking change to anything in
`dev-docs/api-spec.md`.

## 16.3 Guardrail 1 — account-type semantics must not retype `declared_accounts`

`08-accounting-semantics-roadmap.md` §8.2 says account-type semantics "can
start once `account` directive's `type:` tag is parsed (currently
stripped/ignored)" — true (`ledgerkit/parser.py` around the `account`
directive block just appends the bare name string,
`declared_accounts.append(_apply_aliases(account_name, aliases))`, line
~1147; any `type:` tag is silently dropped before that point). But
`Journal.declared_accounts: list[str]` is a **confirmed real dependency**
of `ledgerkit-editor` — `utils/journal_index.py` reads
`journal.declared_accounts` directly as a flat list of strings
(`15-editor-compat-inventory.md`, extended by this review's own grep of
the same source). `dev-docs/api-spec.md` documents it as exactly
`list[str]` too.

**Implication:** when Stage E parses and stores account types, it must do
so via a **new, separate field** — e.g. `Journal.account_types:
dict[str, AccountType]`, or a richer `Journal.account_declarations:
list[AccountDeclaration]` kept *alongside* the unchanged
`declared_accounts: list[str]` — never by changing `declared_accounts`'s
element type from plain strings to something richer. Retyping it would
silently break `ledgerkit-editor`'s `journal_index.py` and violate the
frozen-v1-API-surface commitment `06-core-architecture.md` §6.5 already
makes. This is the one point in the whole review where "no structural
change" could plausibly be read as license to change an *existing*
field's shape — it explicitly is not.

## 16.4 Guardrail 2 — new fields must make a deliberate `compare=` choice

`Posting`/`Transaction` already carry several fields marked
`compare=False` specifically to keep dataclass equality (relied on
throughout the 575-test suite) stable across metadata that varies by
parse context but not by accounting meaning: `Posting.source_line`,
`Posting.inline_comment`, `Transaction.source_span`, `Transaction.raw_text`,
`Transaction.inline_comment`. `Amount.raw` follows the same pattern.

Every new field Stage E/F adds (`cost`, `lot`, `posting_type`, etc.) needs
the same deliberate choice made explicitly, not left to the dataclass
default (`compare=True`): a field that changes the *accounting meaning* of
a posting (e.g. `cost`, `lot`, `posting_type`) should almost certainly
compare `True` — two postings with a different lot or virtual-posting
status are not equal — while a field that's purely provenance/formatting
metadata should follow the existing `compare=False` precedent. Getting
this wrong in either direction either silently breaks existing
equality-based tests (`compare=True` on pure metadata) or lets two
semantically different postings compare equal (`compare=False` on
accounting-meaningful data). Recorded as a design principle in
`dev-docs/architecture.md`, not left implicit.

## 16.5 Not reviewed / out of scope for this phase

`Query`, `ReportSpec`, `ReportSection` also live in `models.py` but are
Stage C's concern (`07-query-regex.md`), not this Stage B model review —
not touched here beyond confirming they're unaffected by anything above.
