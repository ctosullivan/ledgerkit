"""Repository-root and register-location discovery.

Implements `planning/phase-02-stage-2.2-plan.md` SS2a.2 (correction B): an
explicit --repo-root argument, validated against the presence of
knowledge/README.md, with a current-working-directory walk-up default — no
configuration framework, no second marker file.

Register-location discovery is the one BUILD-time decision
`planning/phase-02-adoption-design.md` SS2 explicitly left open ("the
simplest adequate mechanism ... is chosen then, against the real
requirement -- not pre-decided here"): a single optional `register:` line
inside the same knowledge/README.md marker file, naming the register
directory relative to the repository root. Absent that line, the generic
default `knowledge/claims/` location is assumed (its *implementation* is
still deferred per the plan's SS2a.1 -- this module only resolves the path,
it does not parse that schema).
"""
from __future__ import annotations

from pathlib import Path

from .errors import RegisterNotFoundError, RepositoryNotFoundError

MARKER_RELATIVE_PATH = "knowledge/README.md"
DEFAULT_REGISTER_RELATIVE_PATH = "knowledge/claims"
_REGISTER_DIRECTIVE_PREFIX = "register:"


def _has_marker(candidate: Path) -> bool:
    return (candidate / MARKER_RELATIVE_PATH).is_file()


def discover_repo_root(repo_root: str | None = None, start: str | None = None) -> Path:
    """Resolve the repository root per SS2a.2's three governing rules.

    - If `repo_root` is given, it is used exactly as given: no walk-up, only
      a check that it actually contains the marker file.
    - Otherwise, walk up from `start` (defaulting to the current working
      directory) looking for the marker file.

    Raises RepositoryNotFoundError, naming what was checked, in both failure
    cases -- never a silent fallback to the wrong directory.
    """
    if repo_root is not None:
        candidate = Path(repo_root).resolve()
        if not _has_marker(candidate):
            raise RepositoryNotFoundError(
                f"--repo-root {candidate} does not contain {MARKER_RELATIVE_PATH}; "
                "not an Axiom-adopted repository, or the path is wrong."
            )
        return candidate

    current = Path(start).resolve() if start is not None else Path.cwd()
    for candidate in (current, *current.parents):
        if _has_marker(candidate):
            return candidate

    raise RepositoryNotFoundError(
        f"No {MARKER_RELATIVE_PATH} found in {current} or any parent directory; "
        "this does not look like an Axiom-adopted repository. Pass --repo-root "
        "explicitly if it is adopted at a different location."
    )


def _read_register_directive(repo_root: Path) -> str | None:
    marker_path = repo_root / MARKER_RELATIVE_PATH
    text = marker_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(_REGISTER_DIRECTIVE_PREFIX):
            value = stripped[len(_REGISTER_DIRECTIVE_PREFIX):].strip()
            return value or None
    return None


def discover_register_root(repo_root: Path) -> Path:
    """Resolve the claim-register directory for an already-discovered repo.

    Reads one optional `register: <relative-path>` line from
    knowledge/README.md; falls back to the generic default location if the
    directive is absent. Raises RegisterNotFoundError, naming the exact
    path that was expected, if the resolved directory does not exist --
    never a silent empty register.
    """
    directive = _read_register_directive(repo_root)
    relative = directive if directive is not None else DEFAULT_REGISTER_RELATIVE_PATH
    register_root = (repo_root / relative).resolve()

    if not register_root.is_dir():
        source = "knowledge/README.md's register: directive" if directive else "the generic default location"
        raise RegisterNotFoundError(
            f"Register directory {register_root} does not exist "
            f"(resolved from {source}: '{relative}'). This repository is "
            "Axiom-adopted but has no claim register at the expected path."
        )
    return register_root
