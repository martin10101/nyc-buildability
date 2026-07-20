#!/usr/bin/env bash
# =============================================================================
# services/api — deterministic production-dependency lock generator (M0-T018)
# =============================================================================
# Regenerates services/api/requirements.txt (the fully hash-pinned lock that
# render.yaml installs) from services/api/requirements.in.
#
# DETERMINISM CONTRACT
# --------------------
# The lock is generated with `uv pip compile --universal` so the SAME bytes are
# produced regardless of the host OS/interpreter:
#   * --universal            -> cross-platform resolution with environment
#                               markers (e.g. colorama ; sys_platform=='win32',
#                               uvloop ; sys_platform!='win32'); a Windows dev
#                               and the Linux Render/CI runner produce identical
#                               output.
#   * --python-version 3.12  -> resolves for the Render/CI target interpreter
#                               regardless of the local Python.
#   * --generate-hashes      -> every direct AND transitive package is pinned to
#                               an exact version with sha256 hashes, so the
#                               Render `pip install -r requirements.txt` is
#                               hash-verified.
#   * --no-header            -> omit uv's header (it embeds the absolute
#                               --output-file path, which would otherwise differ
#                               between environments and break the byte-identical
#                               CI check). Provenance lives in requirements.in
#                               and this script instead.
#
# The uv version is PINNED (UV_VERSION below) because resolver output can change
# across uv releases; the api-lock-verify CI job installs this exact uv and
# fails if a fresh regeneration is not byte-identical to the committed lock.
#
# Usage (Linux/macOS/Git-Bash):
#   services/api/scripts/lock_requirements.sh            # regenerate in place
#   services/api/scripts/lock_requirements.sh --check    # verify only (CI)
# =============================================================================
set -euo pipefail

UV_VERSION="0.11.29"
PYTHON_TARGET="3.12"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
IN_FILE="${API_DIR}/requirements.in"
OUT_FILE="${API_DIR}/requirements.txt"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv not found. Install the pinned version: pip install uv==${UV_VERSION}" >&2
  exit 2
fi

INSTALLED_UV="$(uv --version | awk '{print $2}')"
if [ "${INSTALLED_UV}" != "${UV_VERSION}" ]; then
  echo "ERROR: uv ${INSTALLED_UV} found but lock is pinned to uv ${UV_VERSION}." >&2
  echo "       Install it: pip install uv==${UV_VERSION}" >&2
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
    echo "ERROR: requirements.txt is NOT byte-identical to a fresh lock." >&2
    echo "       Run services/api/scripts/lock_requirements.sh and commit." >&2
    exit 1
  fi
  echo "OK: requirements.txt is byte-identical to a fresh uv ${UV_VERSION} lock."
else
  "${COMPILE[@]}" --output-file "${OUT_FILE}"
  echo "Wrote ${OUT_FILE}"
fi
