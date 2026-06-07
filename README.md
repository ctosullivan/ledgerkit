# ledgerkit

[![Tests](https://github.com/ctosullivan/ledgerkit/actions/workflows/tests.yml/badge.svg)](https://github.com/ctosullivan/ledgerkit/actions/workflows/tests.yml)

A Python implementation of the [hledger](https://hledger.org) plain-text accounting tool.

## Features (planned for v1)

- Parse `.journal` files compatible with the hledger format
- Core commands: `balance`, `register`, `print`, `accounts`, `stats`
- Pure Python — no third-party runtime dependencies
- Modular, testable architecture
- Use as a CLI tool or as a Python library

## Requirements

- Python 3.8+

## Installation

```bash
pip install ledgerkit
```

With optional pandas support:

```bash
pip install ledgerkit[pandas]
```

### Development install

```bash
git clone https://github.com/ctosullivan/ledgerkit.git
cd ledgerkit
pip install -e ".[pandas]"
```

## Usage

### CLI

```bash
ledgerkit balance myfile.journal
ledgerkit register myfile.journal
ledgerkit accounts myfile.journal
ledgerkit print myfile.journal
ledgerkit stats myfile.journal
```

You can also invoke ledgerkit as a Python module:

```bash
python -m ledgerkit balance myfile.journal
```

### Python library

```python
import ledgerkit

journal = ledgerkit.load("myfile.journal")
accounts = journal.accounts()
balance  = journal.balance()
```

See [docs/python-api.md](docs/python-api.md) for the full library reference.

## Documentation

| Guide | Description |
|---|---|
| [docs/getting-started.md](docs/getting-started.md) | Installation, first run, verification |
| [docs/usage.md](docs/usage.md) | CLI commands with examples |
| [docs/journal-format.md](docs/journal-format.md) | Supported journal syntax with annotated examples |
| [docs/python-api.md](docs/python-api.md) | Python library reference |

## Python ecosystem (pandas)

Install the optional pandas extra for DataFrame export:

```bash
pip install ledgerkit[pandas]
```

Then:

```python
import ledgerkit

journal = ledgerkit.load("myfile.journal")

# Export all postings to a DataFrame
df = journal.to_dataframe()
print(df.groupby("account")["amount"].sum())

# Or export directly from a report object
balance_df = journal.balance().to_dataframe()
register_df = journal.register().to_dataframe()
accounts_df = journal.accounts().to_dataframe()
```

## Development

```bash
# Run all tests
python -m unittest discover -s tests -t . -v
```

See [dev-docs/architecture.md](dev-docs/architecture.md) for module design and
[dev-docs/api-spec.md](dev-docs/api-spec.md) for the full API specification.

## Hledger Compatibility

See [dev-docs/hledger-compatibility.md](dev-docs/hledger-compatibility.md) for which
hledger journal features are supported in v1.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for pull request guidelines, commit
message format, and branch naming. This project follows the
[Contributor Code of Conduct](CODE_OF_CONDUCT.md).

### With AI tooling (Claude Code)

Clone the full repository including AI-workflow files:

```bash
git clone https://github.com/ctosullivan/ledgerkit.git
```

### Without AI tooling

Use sparse checkout to clone only the source code, tests, and human docs
(excludes `CLAUDE.md`, `dev-docs/`, `CHANGELOG.md`, `ROADMAP.md`):

```bash
git clone --filter=blob:none --sparse https://github.com/ctosullivan/ledgerkit.git
cd ledgerkit
git sparse-checkout set ledgerkit tests docs README.md LICENSE pyproject.toml
```

## Acknowledgements

ledgerkit is a Python implementation inspired by two pioneering plain-text
accounting projects. We gratefully acknowledge their authors and contributors.

### Ledger

**John Wiegley** created Ledger, the original plain-text double-entry accounting
tool, which established the journal file format and accounting model that this
ecosystem is built upon.

  https://github.com/ledger/ledger

### hledger

**Simon Michael** created hledger, a Haskell implementation of Ledger's concepts,
which has since evolved its own rich feature set and extensive documentation.
ledgerkit's journal format support is modelled primarily on the hledger 1.52
specification.

  https://github.com/simonmichael/hledger

A full list of hledger contributors can be found at:

  https://github.com/simonmichael/hledger/blob/main/doc/CREDITS.md

Their work — and the broader plain-text accounting community — makes ledgerkit
possible.
