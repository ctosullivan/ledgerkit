#!/usr/bin/env bash
# Pin-enforcement guard for the CodeCompass upgrade + clean-room docs
# initiative (dev-docs/planning/core-redefinition/29-codecompass-upgrade-
# and-clean-room-docs.md, §2.0 steps 5-6, §8 Finding C2).
#
# Run this before every codecompass-dependent command for the duration of
# this initiative. It resolves the checkout the installed `codecompass`
# executable actually imports from, compares its HEAD against the SHA
# recorded in PINNED-REVISIONS.md, and fails loudly on any mismatch
# rather than letting a moved checkout silently stand in for the pin.
#
# Exit 0: pin confirmed, safe to proceed.
# Exit 1: pin violated, or the check itself could not be completed --
#         either way, stop; do not run the codecompass command that
#         prompted this check.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PINNED_FILE="${REPO_ROOT}/dev-docs/clean-room/PINNED-REVISIONS.md"

if [[ ! -f "${PINNED_FILE}" ]]; then
    echo "PIN GUARD FAIL: ${PINNED_FILE} does not exist -- nothing to enforce against." >&2
    exit 1
fi

# Extract the pinned codecompass SHA from PINNED-REVISIONS.md's own
# "**Pinned SHA:**" line under the "## codecompass" heading (the first
# such line in the file -- the codecompass-template section's own line
# comes second).
PINNED_SHA="$(awk '
    /^## codecompass$/ { in_section = 1 }
    in_section && /\*\*Pinned SHA:\*\*/ {
        match($0, /`[0-9a-f]+`/)
        sha = substr($0, RSTART+1, RLENGTH-2)
        print sha
        exit
    }
' "${PINNED_FILE}")"

if [[ -z "${PINNED_SHA}" ]]; then
    echo "PIN GUARD FAIL: could not extract a pinned codecompass SHA from ${PINNED_FILE}." >&2
    exit 1
fi

# Resolve the checkout the installed `codecompass` executable actually
# imports from, via pip's own editable-install metadata.
EXECUTABLE_PATH="$(command -v codecompass 2>/dev/null)"
if [[ -z "${EXECUTABLE_PATH}" ]]; then
    echo "PIN GUARD FAIL: no 'codecompass' executable found on PATH." >&2
    exit 1
fi

# pipx installs each tool into its own isolated venv; find that venv's
# site-packages and read the editable install's direct_url.json, which
# names the real source checkout pip -e installed from.
VENV_DIR="$(dirname "$(dirname "${EXECUTABLE_PATH}")")"
DIRECT_URL_JSON="$(find "${VENV_DIR}" -path '*codecompass_context*.dist-info/direct_url.json' 2>/dev/null | head -1)"

if [[ -z "${DIRECT_URL_JSON}" || ! -f "${DIRECT_URL_JSON}" ]]; then
    echo "PIN GUARD FAIL: could not locate direct_url.json for the installed codecompass-context package under ${VENV_DIR}." >&2
    exit 1
fi

RESOLVED_PATH="$(python3 -c "
import json, sys, urllib.parse
with open('${DIRECT_URL_JSON}') as f:
    data = json.load(f)
url = data.get('url', '')
if url.startswith('file://'):
    print(urllib.parse.unquote(url[len('file://'):]))
else:
    print(url)
")"

if [[ -z "${RESOLVED_PATH}" || ! -d "${RESOLVED_PATH}" ]]; then
    echo "PIN GUARD FAIL: resolved checkout path '${RESOLVED_PATH}' from ${DIRECT_URL_JSON} does not exist or is empty." >&2
    exit 1
fi

ACTUAL_SHA="$(git -C "${RESOLVED_PATH}" rev-parse HEAD 2>/dev/null)"
if [[ -z "${ACTUAL_SHA}" ]]; then
    echo "PIN GUARD FAIL: could not resolve HEAD of '${RESOLVED_PATH}' as a git repository." >&2
    exit 1
fi

if [[ "${ACTUAL_SHA}" != "${PINNED_SHA}" ]]; then
    echo "PIN GUARD FAIL: codecompass checkout at '${RESOLVED_PATH}' is at ${ACTUAL_SHA}," >&2
    echo "but PINNED-REVISIONS.md pins ${PINNED_SHA}. The checkout has moved since this" >&2
    echo "initiative pinned it. Stopping -- do not run the codecompass command that" >&2
    echo "prompted this check. Either restore the checkout to the pinned SHA, or record" >&2
    echo "an explicit, new pin decision in PINNED-REVISIONS.md (plan §2.0 step 4) before" >&2
    echo "continuing." >&2
    exit 1
fi

echo "PIN GUARD OK: codecompass checkout at '${RESOLVED_PATH}' matches pinned SHA ${PINNED_SHA}."
exit 0
