# M0-T021 — Producer report

Task: **M0-T021 — Repair lock-verifier reproducibility check (blank-temp → seeded committed lock).**
Producer: cloud-architect (dispatched); integrated by the orchestrator. Frozen submit SHA **`bd80e72`**
(branch `task/M0-T021-lock-verifier`, off main `f5ab631`, pushed). Requested status: **`awaiting_gate`**.
Not accepted; no merge.

## Root cause (see `M0-T021-diagnosis.md`)
`lock_tools.sh --check` and `lock_requirements.sh --check` compiled the fresh resolution into a **blank
`mktemp`** output file. `uv pip compile` uses the versions already in `--output-file` as resolution
**preferences** (pip-tools-compatible) and keeps them unless `--upgrade` is passed or the inputs no
longer permit them. With a blank output there were no preferences, so uv resolved every package to its
**latest** upstream release — the check reduced to "is anything newer upstream?" and turned red on every
unrelated PR the moment any transitive dep published (certifi 2026.7.22, 2026-07-22).

## Fix (both mirror scripts, identical)
In `--check` mode, seed the temp output with the committed lock before the identical **non-`--upgrade`**
compile:
```bash
TMP="$(mktemp)"; trap 'rm -f "${TMP}"' EXIT
cp "${OUT_FILE}" "${TMP}"                        # seed → existing-output preferences
"${COMPILE[@]}" --output-file "${TMP}" >/dev/null
diff -u "${OUT_FILE}" "${TMP}" || { echo "... NOT byte-identical ..."; exit 1; }
```
No `--upgrade`/`--upgrade-package`; the COMPILE command, uv-version pin check, flags, and IN_FILE are
otherwise unchanged.

## Security properties preserved
- **Exact pins + hashes** retained (no re-lock; both lock files byte-identical to f5ab631).
- **Separate** production (`requirements.txt`) and tooling (`requirements-tools.lock`) locks — both
  verifiers fixed identically.
- **Genuine manifest↔lock drift still FAILS**: uv re-resolves any pin the changed inputs no longer
  permit → diff (AS-3).
- **Tampered / missing hashes still FAIL**: `--generate-hashes` rewrites the true hash, so a hand-edited
  hash cannot survive (AS-4).
- **7-day age gate untouched**: `dependency_age_gate.py` byte-identical; 604800 s PASS / 604799 s FAIL
  asserted (AS-5). No silent updates.

## Scope
Changed only: `services/api/scripts/lock_tools.sh` (+11), `services/api/scripts/lock_requirements.sh`
(+11), new `services/api/scripts/tests/test_lock_verify_reproducibility.py`. **No** change to
`dependency_age_gate.py`, either `.in` manifest, either lock, `app/**`, `packages/**`, `ci.yml`, or any
M4 path. `ci.yml` already runs `pytest scripts/tests` in the `api-tooling-lock-verify` job, so the new
tests auto-collect with no workflow change.

## Acceptance scenarios (evidence — `test_lock_verify_reproducibility.py`, both mirrors parametrized)
- **AS-1** consistent lock → `--check` PASSES.
- **AS-2** (core fix) newer upstream exists but seeded pin still satisfies inputs → PASSES; sub-assertion
  proves an unseeded/blank resolve would have pulled the newer version (the pre-fix deadlock).
- **AS-3** genuine input drift → FAILS with a diff.
- **AS-4** tampered hash → FAILS.
- **AS-5** age gate unchanged; 604800/604799 boundary holds.
- **AS-6** both scripts seed before compile; no `--upgrade` in executable code.

## Evidence
- Local: `bash -n` clean on both scripts; `pytest scripts/tests -q` → **28 passed** (17 age-gate + 11 new).
- The tests run WITHOUT real uv (thin-client) via a faithful fake-uv stub modeling uv's output-file
  preference behavior. **Real-uv proof is CI**: at frozen `bd80e72` **all 12 CI checks are green**,
  including `api-tooling-lock-verify` (`lock_tools.sh --check` under hash-pinned uv 0.11.28) and
  `api-lock-verify` (`lock_requirements.sh --check`) — the same jobs that were RED at the identical
  certifi-2026.7.22 upstream state. This confirms real uv honors the seeded output file.

## uv behavior relied upon
`uv pip compile` reads an existing `--output-file` and uses its versions as preferences (no upgrade
unless `--upgrade`), mirroring pip-tools; with `--generate-hashes` it rewrites the resolved version's
hashes. Confirmed empirically by the green `api-tooling-lock-verify` at `bd80e72` (a blank-temp resolve
would have pulled certifi 2026.7.22 and failed, as it did pre-fix).

## Gate status
Required gates G0 (PASS) / G3 (code) / G4 (qa) / G5 (security, dependency-security). Submitting to the
independent gates at frozen `bd80e72`. Not accepted; no merge.
