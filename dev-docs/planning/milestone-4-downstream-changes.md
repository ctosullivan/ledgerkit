# Milestone 4 — Downstream API Changes

Audience: package consumers (e.g. a ledger editor) upgrading from v0.1.x to v0.2.0.

---

## New model fields

### `Transaction.date2: datetime.date | None`

Secondary / auxiliary date, parsed from the `=DATE2` syntax in the transaction header.

```python
# journal source:  2024-02-20=2024-02-22 * Payroll
txn.date   # datetime.date(2024, 2, 20)  — primary date (unchanged)
txn.date2  # datetime.date(2024, 2, 22)  — new; None when absent
```

`date2` is `None` for every transaction that has no secondary date. No existing
field is renamed or reordered; `date2` is inserted between `date` and `description`
in the dataclass definition with `default=None`, so positional construction still
works if you only pass the required arguments.

### `Posting.cost_raw: str | None`

Raw cost-annotation text stripped from the amount, e.g. `"$180.00"` from
`10 AAPL @ $180.00`. The amount itself (`posting.amount`) contains only the
primary quantity and commodity (`10 AAPL`). `cost_raw` is `None` when no
annotation was present.

```python
# journal source:  assets:brokerage  10 AAPL @ $180.00
posting.amount.quantity   # Decimal("10")
posting.amount.commodity  # "AAPL"
posting.cost_raw          # "$180.00"
```

---

## New class: `ParseWarning`

```python
from ledgerkit.parser import ParseWarning
```

`ParseWarning` is a subclass of `ParseError`. It is appended to the `errors_out`
list in `parse_string_lenient` for constructs that are skipped rather than
hard-failed:

| Construct | Warning message |
|---|---|
| `~ monthly …` (periodic rule block) | `periodic transaction rule (~) skipped (not supported in v1)` |
| `= expenses:food` (auto-posting rule block) | `auto-posting rule (=) skipped (not supported in v1)` |
| Second `apply account` with no intervening `end apply account` | `nested apply account: previous prefix replaced (nesting not supported)` |

**The transaction journal still loads successfully** when these warnings appear.
No transaction data is lost; the unsupported blocks are simply skipped.

### Distinguishing warnings from hard errors

```python
journal, errors = parse_string_lenient(text)

hard_errors = [e for e in errors if not isinstance(e, ParseWarning)]
warnings    = [e for e in errors if isinstance(e, ParseWarning)]

if hard_errors:
    # one or more transactions failed to parse
    ...
if warnings:
    # unsupported directives were silently skipped; journal is otherwise complete
    ...
```

If your editor previously treated any non-empty `errors` list as a load failure,
add the `isinstance` check so that `ParseWarning` items do not trigger false
error states.

---

## Newly supported amount formats

The following amount forms previously raised `ParseError` and now parse correctly.
No API changes are required to use them; the results appear in `Amount.quantity`
and `Amount.commodity` as before.

| Format | Example | Result |
|---|---|---|
| Sign after prefix symbol | `$-300` | `quantity=-300, commodity="$"` |
| Space digit-group separators | `1 000 000 JPY` | `quantity=1000000, commodity="JPY"` |
| Scientific notation | `1E3 EUR` | `quantity=1000, commodity="EUR"` |
| Quoted commodity suffix | `3 "Chocolate Frogs"` | `quantity=3, commodity="Chocolate Frogs"` |
| Cost annotation (`@` / `@@`) | `10 AAPL @ $180.00` | amount=`10 AAPL`; `cost_raw="$180.00"` |
| Lot annotations (`{}`, `[]`, `()`) | `10 AAPL {$182} [2023-01-01]` | annotation stripped; amount=`10 AAPL` |

---

## Newly supported directives

These directives are now parsed and applied. They were previously silently ignored
or would cause downstream parse errors.

### `Y YEAR` — default year

Sets the default year for all year-omitted dates that follow it in the file.

```
Y 2024
1/15 Salary         ; parsed as 2024-01-15
```

No API surface change — the effect is on `Transaction.date` values only.

### `D AMOUNT` — default commodity

Sets the fallback commodity symbol for amounts that carry no symbol.

```
D $1,000.00
2024-01-01 Transfer
    expenses:misc  300     ; parsed as $300
    assets:bank
```

No API surface change — the effect is on `Amount.commodity` values only.

### `apply account PREFIX` / `end apply account`

Prepends `PREFIX:` to every account name in postings within the block.
Account aliases (if any) are applied to the base name before the prefix is added.

```
apply account company
2024-01-01 T
    expenses:food  $10    ; account stored as "company:expenses:food"
    assets:bank   -$10    ; account stored as "company:assets:bank"
end apply account
```

No API surface change — the effect is on `Posting.account` string values only.

---

## Previously out-of-scope constructs that are now handled

| Construct | Old behaviour | New behaviour |
|---|---|---|
| `~ monthly …` block | `ParseError` | Skipped; `ParseWarning` appended; journal loads |
| `= QUERY` block | `ParseError` | Skipped; `ParseWarning` appended; journal loads |
| `2024-01-15=2024-01-20` | secondary date ignored | stored in `Transaction.date2` |
| `10 AAPL @ $180`, `{$182}`, etc. | `ParseError` | annotation stripped; `cost_raw` populated |

---

## Recommended upgrade checklist

- [ ] Add `ParseWarning` to your import: `from ledgerkit.parser import ParseWarning`
- [ ] Update any `if errors:` guard to `if [e for e in errors if not isinstance(e, ParseWarning)]:`
- [ ] If your editor displays error markers, suppress or style `ParseWarning` items differently from hard `ParseError` items
- [ ] If you display transaction metadata, consider surfacing `Transaction.date2` (e.g. "effective date" column or tooltip)
- [ ] If you display posting detail, consider surfacing `Posting.cost_raw` (e.g. in a cost-basis panel)
