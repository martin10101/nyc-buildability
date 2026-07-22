# M0-T021 — G5 (security & dependency-security) verbatim return

_Verbatim independent security-reviewer return (transport decoding only). Orchestrator-recorded._

- Gate ID: G5 (security & dependency-security)
- Task ID: M0-T021 — Repair lock-verifier reproducibility check (blank-temp → seeded committed lock)
- Reviewer: security-reviewer (read-only, independent). Producer: cloud-architect.
- Frozen reviewed code SHA: `bd80e72` (branch tip `eded402` carries only ledger/reports on top).
- Result: PASS

## Steps independently executed
- `git diff f5ab631 bd80e72 -- services/api/scripts/dependency_age_gate.py` → EMPTY.
- `git diff f5ab631 bd80e72 -- services/api/requirements.txt requirements-tools.lock requirements.in requirements-tools.in` → EMPTY.
- `git diff f5ab631 bd80e72 -- .github/workflows/ci.yml` → EMPTY.
- `git diff --name-only f5ab631 bd80e72` → only `lock_requirements.sh`, `lock_tools.sh`, `tests/test_lock_verify_reproducibility.py` (rest are project-control ledger files).
- `bash -n` both scripts → clean. `pytest scripts/tests -q` → 28 passed (11 new).

## Expected vs actual (7 mandated items)
1. `dependency_age_gate.py` byte-identical; 604800 gate intact — EMPTY diff; AS-5 asserts `MIN_AGE_SECONDS == 604800`, 604800→PASS / 604799→FAIL. **PASS**
2. No lock/manifest content change (no certifi upgrade, no re-lock) — EMPTY on all 4 files. **PASS**
3. No `--upgrade`/`--upgrade-package` in executable code — only added executable line is `cp "${OUT_FILE}" "${TMP}"`; COMPILE array unchanged; AS-6 asserts no `--upgrade` on non-comment lines. **PASS**
4. Still FAILS on drift + tamper; non-tautological — AS-3 asserts rc==1 + "NOT byte-identical" + both pins in diff; AS-4 flips a hash hex digit, asserts rc==1. Both drive the real `--check` path. **PASS**
5. Prod/tooling locks stay separate; both mirrors fixed identically — distinct IN/OUT; identical seed line; AS-6 asserts both. **PASS**
6. Test never mutates real locks; stub faithful — every scenario copies the script into `tmp_path`; stub models preference/hash behavior faithfully; stub deliberately omits transitive/marker resolution (covered by real-uv CI). **PASS**
7. No new dependency/network/secret/write-outside-tmp/privilege — only added op is `cp OUT_FILE → mktemp`; test writes only under `tmp_path`. **PASS**

## Conclusion
Correctly scoped repair of the lock verifier, byte-limited to the two mirror `--check` branches (a single `cp` seed line + comment) plus one offline regression test. `dependency_age_gate.py`, both `.in` manifests, both lock files, and `ci.yml` byte-identical to `f5ab631`. No `--upgrade` in executable code, no certifi upgrade, no re-lock, no silent update. 7-day (604800s) age gate untouched and asserted. Reproducibility still fails closed on genuine drift and tampered hashes (rc=1, non-tautological). Fail-closed `set -euo pipefail` + trap cleanup preserved. No dependency-security regression.

Non-blocking notes: **L1** — record the live `api-tooling-lock-verify` + `api-lock-verify` green at `bd80e72` with the gate (orchestrator-captured in `M0-T021-ci-evidence.md`). **L2** — AS-4 covers a tampered hash; missing-hash / package-removed are caught by the same regenerate-diff mechanism (minor completeness note, not a gap).

## VERDICT: PASS
