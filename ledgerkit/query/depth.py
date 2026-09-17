"""DepthSpec — report-display depth clipping/aggregation.

Never a selection filter (see `ledgerkit.query.ast`/`eval` for the actual
predicate AST). This mirrors hledger's own architecture, where every real
command (`balance`, `register`, `print`, `accounts`, `aregister`) strips
`depth:`/`--depth` out of the query used to select postings *before*
selection happens, then reapplies it purely as a display-name transform
(truncation + aggregation, never exclusion). Grounded in
`dev-docs/planning/core-redefinition/
21-stage-c-phase-5-depth-and-verification-plan.md` §1.3/§3, itself sourced
from hledger 1.52.4's `hledger-lib/Hledger/Data/AccountName.hs`
(`getAccountNameClippedDepth`/`clipAccountName`/`clipOrEllipsifyAccountName`)
and `Hledger/Data/Types.hs` (`DepthSpec`'s own `Semigroup` instance) — an
independent Python reimplementation of the same precedence rule, not a
translated port; see `knowledge/DECISIONS.md`.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass

from ledgerkit.query.regex import compile_hledger_regex


@dataclass(frozen=True)
class DepthSpec:
    """A report's depth-clipping configuration.

    flat: general depth (`depth:N` / a future `--depth N`), or None for
        "no general clip."
    by_pattern: (regex, depth) pairs from `depth:REGEX=N`, in the order
        supplied. Resolution for one account: among patterns matching the
        account (or any strict ancestor of it), the one with the greatest
        specificity wins — "specificity" is the 1-based index of the
        shallowest strict ancestor the pattern also matches, or a value
        greater than any real ancestor index if the pattern matches the
        account itself but no strict ancestor (this is hledger's own
        "starts matching the latest as you progress up the parents" rule
        — a pattern that only matches deep/specific text is *more*
        specific, not less). Ties (including two patterns matching at the
        same ancestor depth) go to the later-declared entry. If no
        pattern matches, `flat` is the fallback; if `flat` is also None,
        the account is not clipped at all.
    """

    flat: int | None = None
    by_pattern: tuple[tuple[str, int], ...] = ()

    def is_empty(self) -> bool:
        return self.flat is None and not self.by_pattern


@functools.lru_cache(maxsize=None)
def _compiled(pattern: str):
    return compile_hledger_regex(pattern)


def merge_depth_specs(a: DepthSpec, b: DepthSpec) -> DepthSpec:
    """Combine two DepthSpecs as hledger does when multiple `depth:` terms
    appear within one query (its `DepthSpec` `Semigroup` instance) — NOT
    the same rule as multiple `--depth` CLI flags (which is "last wins";
    out of scope here, no standalone `--depth` flag exists yet). Confirmed
    live against the pinned 1.52.4 binary: `depth:3 depth:1` and
    `depth:1 depth:3` (as two query terms, not one `--depth` flag each)
    both clip to depth 1 regardless of order — the smaller (more
    restrictive) flat depth wins, matching AND-query intersection
    semantics; `by_pattern` entries simply accumulate from both sides.
    """
    if a.flat is None:
        flat = b.flat
    elif b.flat is None:
        flat = a.flat
    else:
        flat = min(a.flat, b.flat)
    return DepthSpec(flat=flat, by_pattern=a.by_pattern + b.by_pattern)


def _account_ancestors(account: str) -> list[str]:
    """Strict ancestors only, shallowest first — excludes `account` itself.

    "assets:bank:savings" -> ["assets", "assets:bank"]. A single-segment
    account (no ':') has no strict ancestors -> [].
    """
    parts = account.split(":")
    return [":".join(parts[:i]) for i in range(1, len(parts))]


def clipped_depth_for_account(spec: DepthSpec, account: str) -> int | None:
    """Resolve the depth to clip `account` to, or None for "don't clip."

    Mirrors hledger's `getAccountNameClippedDepth` exactly, including the
    counterintuitive specificity direction: a pattern that matches the
    account but none of its strict ancestors is *more* specific (wins
    over one matching a shallow ancestor), not less — confirmed against
    the manual's own worked example (`assets=1` vs `savings=2` on
    `assets:bank:savings`: "savings" matches no strict ancestor of that
    account at all, and wins).
    """
    ancestors = _account_ancestors(account)
    best_specificity: int | None = None
    best_depth: int | None = None
    for pattern, depth in spec.by_pattern:
        regex = _compiled(pattern)
        if not regex.search(account):
            continue
        specificity = len(ancestors) + 1  # sentinel: matches no strict ancestor
        for i, ancestor in enumerate(ancestors, start=1):
            if regex.search(ancestor):
                specificity = i
                break
        if best_specificity is None or specificity >= best_specificity:
            best_specificity = specificity
            best_depth = depth
    if best_depth is not None:
        return best_depth
    return spec.flat


def account_excluded_by_depth(spec: DepthSpec, account: str) -> bool:
    """hledger's own RAW `Depth`/`DepthAcct` boolean-EXCLUSION semantics —
    NOT the clipping rule every other depth-aware function in this module
    implements or that `clipped_depth_for_account`/`clip_account_name`
    apply. Used ONLY by `reports.stats()`.

    hledger's `stats` command is a genuine, source-confirmed exception to
    "depth: never excludes" (dev-docs/planning/core-redefinition/
    21-stage-c-phase-5-depth-and-verification-plan.md §1.3's own headline
    finding): `Ledger.hs`'s `ledgerFromJournal`, which `stats` alone (of
    the commands Ledgerkit tracks) builds its account list from, has its
    own doc-comment stating plainly — "If the query includes a depth
    limit, the ledger's journal will be depth limited, but the ledger's
    account tree will not" — i.e. `stats`' own account_count/account_depth
    fields are computed from an EXCLUSION-filtered posting set, while
    every other command (`balance`/`register`/`print`/`accounts`) clips
    display names and never excludes. Confirmed live against the pinned
    1.52.4 binary on two independent scenarios (a single custom-regex
    depth, and a mixed custom+general combination) — this function's
    exclusion decisions were verified to reproduce hledger's exact
    `stats` "Accounts: N (depth D)" counts in both cases.

    A general (flat) term excludes when the account's level exceeds it. A
    `REGEX=N` term excludes only when BOTH the regex matches the account
    AND its level exceeds N — hledger's own `matchesAccount (DepthAcct r
    d) a = accountNameLevel a <= d || not (regexMatchText r a)`: a
    non-matching regex term never excludes on its own. Multiple terms
    combine via AND (hledger's own multi-term `Query` combination) —
    excluded overall if ANY one term's own exclusion condition holds.
    """
    level = account.count(":") + 1 if account else 0
    if spec.flat is not None and level > spec.flat:
        return True
    for pattern, depth in spec.by_pattern:
        if _compiled(pattern).search(account) and level > depth:
            return True
    return False


def clip_account_name(spec: DepthSpec, account: str) -> str:
    """Apply `clipped_depth_for_account`'s result to `account`'s display name.

    Depth 0 clips to the literal string "..." (confirmed live against the
    pinned binary: `hledger balance --depth 0` shows one "..." row, never
    an empty/excluded result) — never an empty string, never exclusion.
    """
    depth = clipped_depth_for_account(spec, account)
    if depth is None:
        return account
    if depth == 0:
        return "..."
    return ":".join(account.split(":")[:depth])
