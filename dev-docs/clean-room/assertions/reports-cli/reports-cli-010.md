<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-010 | date: 2026-10-02 -->
# Assertion: reports-cli-010

## Statement
The CLI's `print` command does NOT serialize inline comments (neither transaction-header nor posting-level `inline_comment` fields are ever printed) -- this is a real divergence from `ledgerkit/writer.py`'s `transaction_to_text()`, which does emit `"  ; {inline_comment}"` for both header and posting lines. This is a confirmed behavioural fact (live-checked this review), though whether the omission is an intentional `print`-scope decision or an unnoted gap remains unresolved from the permitted evidence.
## Kind
boundary
## Basis
directly_stated
## Evidence
cli.py's print branch (lines 427-449) only ever prints `txn.date`, `flag`, `txn.description`, and per-posting `posting.account`/formatted amount -- there is no reference to `txn.inline_comment` or `posting.inline_comment` anywhere in that branch. By contrast, `writer.py`'s `transaction_to_text()` explicitly does: `if txn.inline_comment is not None: header += f"  ; {txn.inline_comment}"` and the same for each posting's `inline_comment`.

Review note (2026-10-03): the static-read-only inference has been upgraded to a directly-confirmed behavioural fact. Live re-check performed this review: a journal with `2024-01-01 Coffee  ; business meeting` and a posting-level `; latte` comment was run through `python -m ledgerkit print -f <file>`; the output omitted both comments entirely (`2024-01-01 Coffee` with no `; business meeting` suffix, and no `; latte` on the posting line), confirming the Statement is not merely a plausible inference from reading two files side by side but an observed fact about current CLI behaviour. The remaining Open question (design intent) is NOT resolved by this check -- intent cannot be determined from behaviour alone, and no test, docstring, or comment in the permitted evidence paths states whether this is deliberate scope or an unnoted gap. That narrower question is escalated below rather than guessed at.
## Justification
Directly confirmed by live CLI execution (see Evidence), corroborated by the side-by-side code read of cli.py's print branch versus writer.py's `transaction_to_text()`. Grep of tests/test_cli/test_cli.py confirms no test exercises `inline_comment`/comment-bearing transactions through `print` -- the CLI-behaviour gap in test coverage (not in the behaviour itself) stands as previously noted.
## Examples
A transaction with `inline_comment="business meeting"` printed via `ledgerkit print` shows only `DATE DESCRIPTION` with no `; business meeting` suffix (live-confirmed), whereas `writer.transaction_to_text()` on the same object would include it (confirmed by tests/test_writer.py's `test_inline_comment_header`/`test_inline_comment_posting`).
## Counterexamples
None found in the permitted evidence, and none found via live re-check either -- `print` drops inline comments unconditionally in every case checked.
## Depends on
None
## Open questions
ESCALATED (unresolved, not decidable from permitted evidence): whether `print`'s omission of inline comments is an intentional scope decision or an unnoted gap. Behaviour is now confirmed (see Evidence); only the design-intent question remains open. No docstring, comment, or test in ledgerkit/cli.py, ledgerkit/writer.py, tests/test_cli/, or tests/test_reports.py/test_writer.py addresses this, and legacy documentation is out of bounds for this dispatch. Needs a decision from the lead/user, not a guess.
## Evidence-support state
supported
## Status
verified
## Supersedes
None

Evidence-paths: [ledgerkit/cli.py:427-449, ledgerkit/writer.py:29-83, tests/test_writer.py:79-108]
