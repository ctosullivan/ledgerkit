# Antipatterns

Approaches that were tried and abandoned — do not revisit without addressing the underlying problem.

---

## Strict indentation gate for posting detection

**Tried:** Original `parse_string` used `line.startswith("  ") or line.startswith("\t")` to distinguish posting lines from directives/headers.

**Problem:** hledger 1.52 documents posting indentation as conventional, not mandatory. The strict gate would reject valid journals and contradicted the compatibility spec.

**Lesson:** Posting detection must be position-based (inside an open transaction block), not indentation-based.

**Do not revisit unless:** hledger changes the spec to require indentation (currently documented as conventional).

**See also:** `knowledge/DECISIONS.md` — "Posting indentation is conventional"

---

## `parse_file()` in `parser.py`

**Tried:** An early version of `parser.py` contained both `parse_string()` and `parse_file()`, mixing pure text parsing with file I/O in the same module.

**Problem:** Made the parser impure and harder to test. File resolution logic (relative paths, tilde expansion, format checks) accumulated in the wrong module.

**Lesson:** `parser.py` must remain a pure text-to-model function. All I/O belongs in `loader.py`.

**Do not revisit unless:** There's a compelling reason to collapse loader and parser (there isn't — they serve distinct responsibilities).

---

## `self.assertIsNotNone()` as a Pylance type guard

**Tried:** Using `self.assertIsNotNone(posting.amount)` before accessing `.quantity`/`.commodity` on `Posting.amount` (typed `Amount | None`).

**Problem:** Pylance does not treat `self.assertIsNotNone()` as a type-narrowing operation. `reportOptionalMemberAccess` warnings persist even after the assertion.

**Lesson:** Use bare `assert x is not None` immediately after extracting the field to a local variable. Pylance recognises this as a type guard.

**Do not revisit unless:** A future Pylance version adds support for `assertIsNotNone` narrowing (track microsoft/pylance-release).

---

## PEP 639 `license` string-expression while still supporting Python 3.8

**Tried:** Setting `pyproject.toml`'s `[project] license` to a bare PEP 639
SPDX string (`license = "GPL-3.0-or-later"`), during the 2026-09-12
MIT→GPL relicensing, in place of the classic `{text = "..."}` dict form.

**Problem:** Verified locally against a single environment
(`setuptools 82.0.1`) — build and `twine check` passed. Pushed to CI, and
the Python 3.8 job failed: `setuptools` dropped Python 3.8 support before
it accepted `license` as a plain string, so no single `setuptools` release
satisfies both constraints. `pip`'s build isolation on that job resolved
an older `setuptools` that still validates `project.license` against the
pre-PEP-639 schema (`{file: ...}` or `{text: ...}` only) and rejected the
string outright.

**Lesson:** Verifying packaging metadata against one local Python/setuptools
combination does not verify it against a project's whole supported-version
matrix. For a project that still declares `requires-python = ">=3.8"`, any
packaging-metadata syntax change needs checking against the *oldest*
supported Python's dependency-resolution behaviour, not just the
newest/local one — CI's actual matrix run is the real oracle here, exactly
as `dev-docs/planning/core-redefinition/10-source-assisted-development.md`
already establishes for behavioural compatibility claims generally.

**Do not revisit unless:** Python 3.8 support is explicitly dropped first
(a separate, `pyproject.toml`-metadata decision requiring its own
approval per `CLAUDE.md`'s Unauthorised Change Rule), or a `setuptools`
release ships that supports both Python 3.8 and the PEP 639 string form.

**See also:** `knowledge/DECISIONS.md` — "Relicensed MIT → GPL-3.0-or-later".

---

## Accumulating aliases across included files

**Tried:** (Design consideration during alias implementation) — applying aliases globally across all files loaded via `include`.

**Problem:** Would silently rewrite account names in unrelated included files, producing surprising and hard-to-debug behaviour.

**Lesson:** Aliases are file-scoped at parse time. Each file's alias list is independent.

**Do not revisit unless:** A user explicitly requests cross-file alias propagation and we document it as a deliberate deviation from hledger.
