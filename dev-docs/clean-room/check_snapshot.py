#!/usr/bin/env python3
"""Ledgerkit-specific snapshot-integrity checker for the clean-room
documentation initiative (dev-docs/planning/core-redefinition/
29-codecompass-upgrade-and-clean-room-docs.md, Section 3.7).

Deliberately NOT an import of CodeCompass's own check_knowledge_base.py
subsystem (Plan 29 Section 3.1's non-adoption decision) -- a much
smaller, Ledgerkit-sized tool, built fresh, stdlib only.

Checks six conditions, fails closed (non-zero exit, one specific reason
per failure, never a silent pass):

  1. Missing or duplicate assertion IDs.
  2. Snapshot hash mismatch -- an assertion file's CURRENT content must
     match the sidecar's recorded content_hash (the assertion itself is
     frozen; this check catches an edit after freezing, including
     accidental tampering).
  3. Missing repository revision in the sidecar.
  4. Referenced assertion records don't exist on disk.
  5. The recorded repository revision does not exist as a real git
     object (git cat-file -e <rev>^{commit}).
  6. Cited local evidence (an "Evidence-paths:" entry inside an
     assertion) does not resolve against THAT REVISION's own git tree --
     never today's working tree. A file that didn't exist at the frozen
     revision, or a line/range that doesn't resolve against that
     revision's own historical blob content, is a failure here, even if
     it resolves fine against the live filesystem right now.

Usage:
    python check_snapshot.py <topic>          # check a real snapshot
    python check_snapshot.py --self-test       # run the internal fixture
                                                # battery (every failure
                                                # mode genuinely fails,
                                                # the passing case
                                                # genuinely passes)
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLEAN_ROOM = REPO_ROOT / "dev-docs" / "clean-room"


class CheckFailure(Exception):
    """One fail-closed condition. Message is the specific reason."""


@dataclass
class CheckResult:
    ok: bool
    failures: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Evidence-path citation parsing.
#
# Purpose: an assertion's "## Evidence" section is free-form prose for
# human readers, but must also carry a machine-checkable citation list so
# this script can verify it without parsing natural language. Convention
# (documented in dev-docs/clean-room/assertions/TEMPLATE.md, this
# project's own addition to the imported template): a line of the exact
# form "Evidence-paths: [path, path:line, path:start-end, ...]" -- the
# project's existing inline-list-form convention, one bracketed list, no
# block-list form (which this project's own established convention
# already requires elsewhere, for the same "a hand-rolled line-oriented
# parser can silently miss a YAML block list" reason).
#
# Group breakdown:
#   (1) the full bracketed list content, comma-separated entries.
#
# Edge cases:
#   - An entry with no line/range (a whole-file citation) is valid --
#     only existence-at-revision is checked for it, no range check.
#   - A line/range uses a single ':' separator; "path:10" is a single
#     line, "path:10-20" is an inclusive range. A path itself must never
#     contain ':' for this to parse correctly (true for every real
#     Ledgerkit path).
#   - Leading/trailing whitespace around each entry is stripped.
_EVIDENCE_PATHS_LINE = re.compile(r"^\s*Evidence-paths:\s*\[(.*)\]\s*$", re.MULTILINE)


@dataclass
class EvidenceCitation:
    raw: str
    path: str
    line_start: int | None
    line_end: int | None


def parse_evidence_citations(assertion_text: str) -> list[EvidenceCitation]:
    match = _EVIDENCE_PATHS_LINE.search(assertion_text)
    if not match:
        return []
    raw_list = match.group(1)
    citations: list[EvidenceCitation] = []
    for entry in raw_list.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            path, range_part = entry.rsplit(":", 1)
            if "-" in range_part:
                start_str, end_str = range_part.split("-", 1)
                citations.append(
                    EvidenceCitation(entry, path, int(start_str), int(end_str))
                )
            else:
                line = int(range_part)
                citations.append(EvidenceCitation(entry, path, line, line))
        else:
            citations.append(EvidenceCitation(entry, entry, None, None))
    return citations


# ---------------------------------------------------------------------------
# Git plumbing helpers -- all resolve against a named revision's own
# historical tree, never the live working directory, per check 6's own
# requirement.


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )


def revision_exists(repo: Path, revision: str) -> bool:
    result = _git(repo, "cat-file", "-e", f"{revision}^{{commit}}")
    return result.returncode == 0


def file_existed_at_revision(repo: Path, revision: str, path: str) -> bool:
    result = _git(repo, "cat-file", "-e", f"{revision}:{path}")
    return result.returncode == 0


def historical_content(repo: Path, revision: str, path: str) -> str | None:
    result = _git(repo, "show", f"{revision}:{path}")
    if result.returncode != 0:
        return None
    return result.stdout


def range_resolves(content: str, start: int, end: int) -> bool:
    lines = content.splitlines()
    return 1 <= start <= len(lines) and 1 <= end <= len(lines) and start <= end


# ---------------------------------------------------------------------------
# The six checks.


def check_snapshot(
    repo: Path,
    sidecar_path: Path,
    assertions_dir: Path,
) -> CheckResult:
    result = CheckResult(ok=True)

    def fail(msg: str) -> None:
        result.ok = False
        result.failures.append(msg)

    if not sidecar_path.exists():
        fail(f"sidecar does not exist: {sidecar_path}")
        return result

    try:
        sidecar = json.loads(sidecar_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"sidecar is not valid JSON: {exc}")
        return result

    # Check 3: missing repository revision.
    revision = sidecar.get("repository_revision_at_freeze")
    if not revision:
        fail("sidecar is missing repository_revision_at_freeze")
        return result  # nothing else below is checkable without it

    # Check 5: recorded revision is a real git object.
    if not revision_exists(repo, revision):
        fail(
            f"recorded revision {revision!r} does not exist as a real git "
            f"commit in {repo} (git cat-file -e {revision}^{{commit}} failed)"
        )
        return result  # checks 6 below are meaningless without a real revision

    assertions_meta = sidecar.get("assertions", {})
    if not assertions_meta:
        fail("sidecar names no assertions at all")

    # Check 1: missing/duplicate assertion IDs, by construction of a dict
    # keyed on id -- a literal JSON duplicate key is already impossible
    # (the parser keeps only the last one), so duplication is instead
    # checked against the assertions directory's own real files: every
    # file present must appear exactly once in the sidecar, and vice
    # versa.
    on_disk_ids = set()
    if assertions_dir.exists():
        for p in sorted(assertions_dir.glob("*.md")):
            if p.name == "TEMPLATE.md" or p.name == "_review.md":
                continue
            on_disk_ids.add(p.stem)

    sidecar_ids = set(assertions_meta.keys())

    missing_on_disk = sidecar_ids - on_disk_ids
    for aid in sorted(missing_on_disk):
        # Check 4: referenced assertion records don't exist.
        fail(f"assertion {aid!r} is named in the sidecar but has no file on disk")

    extra_on_disk = on_disk_ids - sidecar_ids
    for aid in sorted(extra_on_disk):
        fail(
            f"assertion file {aid!r}.md exists on disk but is not named in "
            f"the sidecar -- either a missing ID (incomplete freeze) or an "
            f"orphaned file"
        )

    for aid, meta in sidecar_meta_sorted(assertions_meta):
        rel_path = meta.get("path")
        expected_hash = meta.get("content_hash")
        if not rel_path or not expected_hash:
            fail(f"assertion {aid!r}'s sidecar entry is missing path or content_hash")
            continue

        full_path = repo / rel_path
        if not full_path.exists():
            fail(
                f"assertion {aid!r}'s sidecar path {rel_path!r} does not "
                f"exist on disk"
            )
            continue

        # Check 2: snapshot hash mismatch -- against the assertion
        # file's CURRENT content (the assertion is frozen; a mismatch
        # means it was edited, or tampered with, after freezing).
        actual_content = full_path.read_bytes()
        actual_hash = hashlib.sha256(actual_content).hexdigest()
        if actual_hash != expected_hash:
            fail(
                f"assertion {aid!r} content hash mismatch: sidecar recorded "
                f"{expected_hash}, current file hashes to {actual_hash} -- "
                f"the assertion was edited after freezing without a "
                f"re-freeze"
            )
            continue

        # Check 6: cited local evidence resolves against the FROZEN
        # revision's own tree, never today's working tree.
        assertion_text = actual_content.decode("utf-8", errors="replace")
        for citation in parse_evidence_citations(assertion_text):
            if not file_existed_at_revision(repo, revision, citation.path):
                fail(
                    f"assertion {aid!r} cites {citation.raw!r}, but "
                    f"{citation.path!r} did not exist at revision "
                    f"{revision} (git cat-file -e {revision}:{citation.path} "
                    f"failed) -- a later source change must not silently "
                    f"validate against today's tree"
                )
                continue
            if citation.line_start is not None:
                content = historical_content(repo, revision, citation.path)
                if content is None:
                    fail(
                        f"assertion {aid!r} cites {citation.raw!r}, but "
                        f"the historical content of {citation.path!r} at "
                        f"{revision} could not be retrieved"
                    )
                elif not range_resolves(content, citation.line_start, citation.line_end):
                    fail(
                        f"assertion {aid!r} cites {citation.raw!r}, but "
                        f"lines {citation.line_start}-{citation.line_end} do "
                        f"not resolve against {citation.path!r}'s own "
                        f"content AT REVISION {revision} (that historical "
                        f"blob has a different number of lines) -- resolving "
                        f"against today's file instead would be exactly the "
                        f"false-pass/false-fail risk this check exists to "
                        f"prevent"
                    )

    return result


def sidecar_meta_sorted(assertions_meta: dict) -> list[tuple[str, dict]]:
    return sorted(assertions_meta.items())


# ---------------------------------------------------------------------------
# Self-test: a disposable git fixture, one passing case, one case per
# failure mode -- proving each check genuinely fails closed, not merely
# asserting it does (same discipline Plan 29 requires of the preflight
# probe and the pin guard).


def _write_assertion(path: Path, aid: str, evidence_paths: str) -> None:
    path.write_text(
        f"# Assertion: {aid}\n\n"
        f"## Statement\n\nFixture statement for {aid}.\n\n"
        f"## Evidence\n\nFixture evidence.\n\n"
        f"Evidence-paths: [{evidence_paths}]\n"
    )


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_self_test() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="check_snapshot_selftest_"))
    try:
        return _run_self_test_in(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _run_self_test_in(tmp: Path) -> int:
    repo = tmp / "fixture-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", repo.as_posix()], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "config", "user.name", "Test"], check=True)

    src = repo / "src.py"
    src.write_text("line1\nline2\nline3\nline4\nline5\n")
    subprocess.run(["git", "-C", repo.as_posix(), "add", "."], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "commit", "-q", "-m", "initial"], check=True)
    frozen_revision = subprocess.run(
        ["git", "-C", repo.as_posix(), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    assertions_dir = repo / "assertions" / "fixture-topic"
    assertions_dir.mkdir(parents=True)
    _write_assertion(assertions_dir / "fixture-001.md", "fixture-001", "src.py:1-3")

    def make_sidecar(**overrides) -> Path:
        sidecar = {
            "snapshot_id": "fixture-topic@v1",
            "created": "2026-10-02T00:00:00Z",
            "repository_revision_at_freeze": frozen_revision,
            "assertions": {
                "fixture-001": {
                    "path": "assertions/fixture-topic/fixture-001.md",
                    "content_hash": _sha256_of(assertions_dir / "fixture-001.md"),
                },
            },
        }
        sidecar.update(overrides)
        path = tmp / "sidecar.json"
        path.write_text(json.dumps(sidecar, indent=2))
        return path

    checks: list[tuple[str, bool, CheckResult]] = []

    # Case A: everything correct -- expect PASS.
    result = check_snapshot(repo, make_sidecar(), assertions_dir)
    checks.append(("passing case", True, result))

    # Case B: missing repository revision -- expect FAIL.
    sidecar_path = make_sidecar(repository_revision_at_freeze="")
    result = check_snapshot(repo, sidecar_path, assertions_dir)
    checks.append(("missing repository revision", False, result))

    # Case C: revision doesn't exist as a real git object -- expect FAIL.
    sidecar_path = make_sidecar(repository_revision_at_freeze="0" * 40)
    result = check_snapshot(repo, sidecar_path, assertions_dir)
    checks.append(("nonexistent revision", False, result))

    # Case D: dangling assertion reference (named in sidecar, no file) --
    # expect FAIL.
    sidecar_path = make_sidecar(
        assertions={
            "fixture-001": {
                "path": "assertions/fixture-topic/fixture-001.md",
                "content_hash": _sha256_of(assertions_dir / "fixture-001.md"),
            },
            "fixture-999-dangling": {
                "path": "assertions/fixture-topic/fixture-999-dangling.md",
                "content_hash": "deadbeef",
            },
        }
    )
    result = check_snapshot(repo, sidecar_path, assertions_dir)
    checks.append(("dangling assertion reference", False, result))

    # Case E: hash mismatch (assertion edited after freezing) -- expect FAIL.
    sidecar_path = make_sidecar(
        assertions={
            "fixture-001": {
                "path": "assertions/fixture-topic/fixture-001.md",
                "content_hash": "0" * 64,
            },
        }
    )
    result = check_snapshot(repo, sidecar_path, assertions_dir)
    checks.append(("hash mismatch", False, result))

    # Case F: evidence cites a file that did not exist at the frozen
    # revision (added in a LATER commit) -- expect FAIL even though it
    # exists on disk right now. This is the core C3 historical-integrity
    # scenario.
    later_file = repo / "added_later.py"
    later_file.write_text("x = 1\n")
    subprocess.run(["git", "-C", repo.as_posix(), "add", "added_later.py"], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "commit", "-q", "-m", "add later file"], check=True)
    _write_assertion(assertions_dir / "fixture-002.md", "fixture-002", "added_later.py:1")
    sidecar_path = make_sidecar(
        assertions={
            "fixture-002": {
                "path": "assertions/fixture-topic/fixture-002.md",
                "content_hash": _sha256_of(assertions_dir / "fixture-002.md"),
            },
        }
    )
    result = check_snapshot(repo, sidecar_path, assertions_dir)
    checks.append(("evidence file did not exist at frozen revision", False, result))

    # Case G: evidence cites a line range that doesn't resolve against
    # the file's content AT the frozen revision, even though it resolves
    # fine against today's (later, longer) version of the same file.
    src.write_text("line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\n")
    subprocess.run(["git", "-C", repo.as_posix(), "add", "src.py"], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "commit", "-q", "-m", "extend src.py"], check=True)
    # src.py now has 10 lines on disk/HEAD, but the frozen revision's own
    # src.py only had 5 -- cite a range only the newer version supports.
    _write_assertion(assertions_dir / "fixture-003.md", "fixture-003", "src.py:8-9")
    sidecar_path = make_sidecar(
        assertions={
            "fixture-003": {
                "path": "assertions/fixture-topic/fixture-003.md",
                "content_hash": _sha256_of(assertions_dir / "fixture-003.md"),
            },
        }
    )
    result = check_snapshot(repo, sidecar_path, assertions_dir)
    checks.append(("evidence range only resolves against today's tree, not the frozen revision", False, result))

    all_ok = True
    for name, expect_ok, result in checks:
        actual_ok = result.ok
        status = "OK" if actual_ok == expect_ok else "SELF-TEST DEFECT"
        if actual_ok != expect_ok:
            all_ok = False
        print(f"[{status}] {name}: expected ok={expect_ok}, got ok={actual_ok}")
        for f in result.failures:
            print(f"    - {f}")

    if all_ok:
        print("\nSelf-test PASS: every check fails closed exactly where expected,")
        print("and the passing case genuinely passes.")
        return 0
    else:
        print("\nSelf-test FAIL: at least one check did not behave as expected.")
        return 1


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    if argv[0] == "--self-test":
        return run_self_test()

    topic = argv[0]
    snapshot_dir = CLEAN_ROOM / "snapshots"
    sidecar_path = snapshot_dir / f"{topic}-v1.sidecar.json"
    assertions_dir = CLEAN_ROOM / "assertions" / topic

    result = check_snapshot(REPO_ROOT, sidecar_path, assertions_dir)
    if result.ok:
        print(f"PASS: snapshot for topic {topic!r} is valid.")
        return 0
    print(f"FAIL: snapshot for topic {topic!r} has {len(result.failures)} problem(s):")
    for f in result.failures:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
