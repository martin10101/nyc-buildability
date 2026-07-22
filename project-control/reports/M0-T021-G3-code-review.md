# M0-T021 — G3 (code review) verbatim return

_Verbatim independent code-reviewer return (transport decoding only). Orchestrator-recorded._

**Task:** M0-T021 — Repair lock-verifier reproducibility check (blank-temp → seeded committed lock)
**Reviewed SHA (code):** `bd80e72` (branch tip `eded402` is ledger/reports-only; `services/**` == `bd80e72`)
**Reviewer:** code-reviewer (independent, read-only). **Gate:** G3. **Verdict: PASS**

## Scope reviewed
Diff `f5ab631..bd80e72` under `services/`: `lock_tools.sh` (+11), `lock_requirements.sh` (+11), new `tests/test_lock_verify_reproducibility.py` (405 lines). Remaining commit-range files are project-control ledger artifacts. No other code paths changed.

## Commands run
- `bash -n` both scripts → clean.
- `python -m pytest services/api/scripts/tests -q` → **28 passed** (17 age-gate + 11 new) on Windows Git-Bash; no flakiness; `FAKE_UV_PYTHON` interpreter forwarding works.
- `git diff --name-only f5ab631 bd80e72 -- .github/` → empty (no ci.yml change).
- Age gate + both `.in` + both locks → untouched.
- `--upgrade`: only in comments and the test's guard assertion — never in executable code.

## Findings
**Shell fix (both mirrors) — CORRECT.** `cp "${OUT_FILE}" "${TMP}"` sits inside `--check`, after `TMP="$(mktemp)"`+`trap`, immediately before the compile. Trap cleanup still owns `TMP`. `set -euo pipefail` safe (both files exist; a missing lock fails closed — desirable). Diff/exit-code logic byte-for-byte unchanged; only the `cp` is added. Applied identically to both scripts. No `--upgrade` introduced.

**Test quality — SOUND.** Fake-uv stub is a faithful, non-circular model (existing `--output-file` pins are preferences kept while they satisfy inputs; exact input pins dictate version; `--generate-hashes` rewrites the canonical hash). AS-2 (core) is meaningful — asserts the seeded check keeps `demo==1.5.0` AND that a blank resolve pulls `2.0.0`. AS-3/AS-4 assert rc==1 with correct diagnostics. AS-5 imports the REAL `dependency_age_gate.py` unmodified and asserts the 604800/604799 boundary. AS-6 asserts both scripts seed and no `--upgrade`. Windows/Git-Bash portability handled; non-flaky.

**CI — CORRECT and unchanged.** `ci.yml` already runs `pytest scripts/tests` in `api-tooling-lock-verify`; the new test auto-collects with no workflow edit.

**Scope — CONFIRMED.** Only the two scripts + one test changed; age gate, `.in` manifests, and locks untouched.

## Minor observation (non-blocking)
`test_as6_...` names a local `check_idx` after the `MODE=` index rather than the `--check` branch entry; the ordering assertion still holds (the sole `--output-file "${TMP}"` occurrence lives only in `--check`). Cosmetic only.

## VERDICT: PASS
