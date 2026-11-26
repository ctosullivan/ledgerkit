<!-- producer: assertion-research | topic: checks | dispatch: ck-strictfmt-05 | date: 2026-10-02 -->
# Assertion: checks-005

## Statement
Strict-tier check failures (`accounts`, `commodities`) produce a multi-line `CheckError.message` built by `_build_strict_context`: an "Error: {source_file}:{line}:" header, a reconstructed transaction header line, each posting line reconstructed via `_fmt_posting`/`_fmt_amount`, a caret (`^`) underline positioned under the offending account name (for `accounts`) or the offending amount text (for `commodities`), followed by an explanation ("Strict account/commodity checking is enabled, and ...") and example `account`/`commodity` directive suggestions. This is distinct from all other checks, whose `message` is a single-line plain string.

## Kind
rule
## Basis
directly_stated
## Evidence
`_build_strict_context` (checks.py:181-215) constructs the `{pad} | ...` / caret-line block; `check_accounts` (244-257) computes `caret_offset = 4` (the posting indent) and `caret_len = len(posting.account)`; `check_commodities` (290-306) computes `caret_offset = 4 + len(posting.account) + 2` and `caret_len = max(len(amt_str), 1)`, then both append tier-specific explanatory text and example directive lines.

Evidence-paths: [ledgerkit/checks.py:181-312, tests/test_checks/test_checks.py:677-721]

## Justification
`test_strict_fails_without_declarations` (CLI-level, 677-689) and `test_strict_fails_missing_account_declarations` (702-710) assert the stderr output contains the literal substring "has not been declared" together with the specific account name — consistent with the explanation text appended at checks.py:251-252 ('account "{posting.account}" has not been declared.'). `test_strict_fails_missing_commodity_declarations` (712-720) confirms the analogous commodity wording and that the symbol "£" appears in output.

## Examples
For an undeclared account "assets:bank", the appended explanation lines read exactly: `Strict account checking is enabled, and`, then `account "assets:bank" has not been declared.`, then `Consider adding an account directive. Examples:`, then blank, then `account assets:bank`, then `account assets:bank    ; type:A  ; (L,E,R,X,C,V)` (checks.py:249-257).

## Counterexamples
None found; no strict check test shows a different message shape.

## Depends on
checks-003, checks-004 (the two check functions that invoke this formatting).

## Open questions
The CLI-level tests confirm substrings appear in stderr output but (being outside permitted evidence for cli.py) do not establish whether cli.py reformats/wraps this message further before printing — only that `checks.py`'s own `CheckError.message` contains this exact structure per its source code.

## Evidence-support state
supported
## Status
verified
## Supersedes
None
