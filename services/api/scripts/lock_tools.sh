#!/usr/bin/env bash
# =============================================================================
# services/api — deterministic Python TOOLING lock generator (M0-T020)
# =============================================================================
# Regenerates services/api/requirements-tools.lock (the fully hash-pinned
# DIRECT+TRANSITIVE closure that every audited Python CI job installs its
# test/build/lock/audit tools from) out of services/api/requirements-tools.in.
#
# This is the ONE documented tooling-lock generation script. It mirrors the
# production lock generator services/api/scripts/lock_requirements.sh exactly
# (same uv, same flags, same determinism contract) but operates on the TOOLING
# manifest instead of the runtime manifest. The two manifests are the only
# authoritative pin lists; nothing here is duplicated in another script.
#
# DETERMINISM CONTRACT (identical to lock_requirements.sh)
# -------------------------------------------------------
# The lock is generated with `uv pip compile --universal` so the SAME bytes are
# produced regardless of host OS/interpreter:
#   * --universal            -> cross-platform resolution with environment
#                               markers (e.g. colorama ; sys_platform=='win32');
#                               a Windows dev and the Linux CI runner produce
#                               identical output.
#   * --python-version 3.12  -> resolves for the CI target interpreter
#                               regardless of the local Python.
#   * --generate-hashes      -> every direct AND transitive tool is pinned to an
#                               exact version with sha256 hashes, so CI installs
#                               with `pip install --require-hashes` are verified.
#   * --no-header            -> omit uv's header (it embeds the absolute
#                               --output-file path, which would differ between
#                               environments and break the byte-identical check).
#                               Provenance lives in requirements-tools.in and
#                               this script instead.
#
# The uv version is PINNED (UV_VERSION below, matching the production lock) so
# resolver output cannot drift across uv releases; the tooling-lock-verify CI
# step installs this exact uv FROM the committed lock (pip install
# --require-hashes -r requirements-tools.lock) using the runner's existing pip —
# it never downloads an unlocked uv to build or verify the tool lock — and then
# fails if a fresh regeneration is not byte-identical to the committed lock.
#
# Usage (Linux/macOS/Git-Bash):
#   services/api/scripts/lock_tools.sh            # regenerate in place
#   services/api/scripts/lock_tools.sh --check    # verify only (CI)
# =============================================================================
set -euo pipefail

# Keep in lockstep with services/api/scripts/lock_requirements.sh.
UV_VERSION="0.11.28"
PYTHON_TARGET="3.12"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
IN_FILE="${API_DIR}/requirements-tools.in"
OUT_FILE="${API_DIR}/requirements-tools.lock"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv not found. Install the pinned tooling lock first:" >&2
  echo "       pip install --require-hashes -r ${OUT_FILE}" >&2
  exit 2
fi

INSTALLED_UV="$(uv --version | awk '{print $2}')"
if [ "${INSTALLED_UV}" != "${UV_VERSION}" ]; then
  echo "ERROR: uv ${INSTALLED_UV} found but the tooling lock is pinned to uv ${UV_VERSION}." >&2
  echo "       Install the exact tooling lock: pip install --require-hashes -r ${OUT_FILE}" >&2
  exit 2
fi

COMPILE=(uv pip compile --universal --python-version "${PYTHON_TARGET}"
         --generate-hashes --no-header "${IN_FILE}")

MODE="${1:-generate}"
if [ "${MODE}" = "--check" ]; then
  TMP="$(mktemp)"
  trap 'rm -f "${TMP}"' EXIT
  "${COMPILE[@]}" --output-file "${TMP}" >/dev/null
  if ! diff -u "${OUT_FILE}" "${TMP}"; then
    echo "ERROR: requirements-tools.lock is NOT byte-identical to a fresh lock." >&2
    echo "       Run services/api/scripts/lock_tools.sh and commit." >&2
    exit 1
  fi
  echo "OK: requirements-tools.lock is byte-identical to a fresh uv ${UV_VERSION} lock."
else
  "${COMPILE[@]}" --output-file "${OUT_FILE}"
  echo "Wrote ${OUT_FILE}"
fi
