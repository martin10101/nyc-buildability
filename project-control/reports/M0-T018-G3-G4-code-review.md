<!-- Preserved VERBATIM by the orchestrator from the code-reviewer G3+G4 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

# G3 + G4 GATE REPORT — M0-T018 (Backend production dependency parity + Python supply-chain enforcement)

## VERDICT: PASS

Independently verified against acceptance scenarios DP-S1..DP-S9 (not the producer's conclusions), on the merged tree at 7ffd542. Local runs on Python 3.11 (thin client; pyproject requires 3.12 → the Linux/3.12 full-install pieces are CI-authoritative, and PR CI runs 29755375638/29755409641 show `exact-production-install` PASS). Zero BLOCKING defects.

---

## Scenario-by-scenario findings

**DP-S1 parity — PASS.** `jsonschema==4.26.0` is present in requirements.txt (line 93) and installed by Render's exact command. `grep -riE "dev|test|never" requirements.txt` → no matches (the old mislabel is gone). pyproject `[project.dependencies]` declares `jsonschema>=4.21,<5` as runtime (line 20) and its dev-extras comment (lines 38-40) explicitly states jsonschema is runtime, not dev. All direct pins satisfy pyproject ranges: fastapi 0.139.0∈[0.115,1); uvicorn 0.51.0∈[0.30,1); jsonschema 4.26.0∈[4.21,5); shapely 2.0.7==2.0.7. No runtime dep is labeled dev/test-only anywhere.

**DP-S2 determinism — PASS.** requirements.txt is a fully hash-pinned lock: 851 lines, 27 packages, 774 `--hash=sha256:` lines; every requirement carries hashes (verified fastapi/starlette blocks). Direct AND transitive deps pinned exact. `lock_requirements.sh` pins `UV_VERSION="0.11.29"` and `--python-version 3.12`; the `api-lock-verify` CI job installs that exact uv and runs `--check` (fails on any drift). Byte-identical regeneration is uv-tool dependent — not locally reproducible on this thin client (no uv), so idempotency is CI-authoritative via `api-lock-verify`; the mechanism (pinned uv + `--no-header` + `--universal`) is sound and enforced. `--require-hashes` used in CI install.

**DP-S3 positive smoke — PASS.** Ran `exact_install_smoke.py` locally (PYTHONPATH=services/api): `SMOKE OK (positive): create_app() built the app and validate_profile() accepted the valid fixture (full_example.json)`. It genuinely calls `create_app()` then `validate_profile()` on the committed fixture `packages/contracts/fixtures/valid/property_profile/full_example.json` (exists, 2506 bytes). CI mirrors this after `pip install --require-hashes -r requirements.txt` + `pip install --no-deps .` + `pip check`.

**DP-S4 negative proof — PASS, GENUINE (the key proof).** Confirmed the lazy import at `app/profile/contract.py:231` (`import jsonschema` inside `_validator()`), so a health endpoint cannot catch a missing jsonschema. I independently validated BOTH branches locally:
- With jsonschema blocked (sys.meta_path finder, no env mutation): `SMOKE OK (negative): validate_profile() raised ModuleNotFoundError("No module named 'jsonschema'") ... proves the exact-install gate genuinely exercises validate_profile` → exit 0.
- With jsonschema PRESENT (the misconfiguration the gate must catch): `SMOKE FAIL (negative): jsonschema is importable ...` → **exit 1**.

This proves the negative smoke is NOT a no-op: it fails CI unless jsonschema is actually absent and validate_profile actually raises. CI wires the real path (`pip uninstall -y jsonschema` → `--expect-missing-jsonschema` → restore). The negative proof would genuinely fail CI if validate_profile stopped exercising the runtime import.

**DP-S5 API suite on production tree — PASS (disclosed).** `pytest --co` collects exactly **538 tests** on this checkout (meets ≥538 precisely). CI runs the suite against the locked production tree plus ONLY test-runner deps (pytest, httpx for TestClient), added on top — production runtime deps still come from the lock, not dev extras. The pytest/httpx exception is legitimately disclosed (producer report §DP-S5). Full run on 3.12 is CI-authoritative.

**DP-S6 pip-audit zero — PASS.** CI step: `pipx run --spec "pip-audit==2.10.1" pip-audit -r requirements.txt --no-deps --strict` (ci.yml:187) — blocking, run via pipx isolation so audit deps don't perturb the pinned tree. No `--ignore-vuln`/allowlist/`continue-on-error`/`|| true`/print-only anywhere (grep confirmed only comment references describing their absence). starlette 0.46.2 → 1.3.1 clears the advisories.

**DP-S7 release-age — PASS.** Producer recorded ≥7-day publication ages for all 27 packages with PyPI `upload_time_iso_8601` evidence; deliberate age pins (websockets==16.1, numpy==2.4.6) documented in requirements.in with rationale. Age data is point-in-time (2026-07-20) and not re-verifiable read-only here, but the STOP-condition handling (no silent substitution; fastapi 0.139.1/2 and websockets 16.1.1 rejected for <7d) is disclosed and consistent with the contract.

**DP-S8 scheduled audit — PASS.** `.github/workflows/scheduled-audit.yml`: daily cron `17 6 * * *`, PR trigger on requirements.txt/.in/pyproject.toml, and workflow_dispatch. Same blocking `--no-deps --strict` audit; a finding → red run (not silent).

**DP-S9 regression — PASS.** Local: `ruff check .` → All checks passed; 538 tests collected; app importable with jsonschema 4.26.0 + referencing 0.37.0. Contract drift (`sync_contract_schemas.py --check`, `generate_ts_types.py --check`) covered by existing CI jobs, unaffected. Exact-install smoke + full pytest on 3.12 are CI-authoritative and shown green on the PR.

---

## Scope confirmation — PASS
`git show --stat 7ffd542`: exactly 8 files — ci.yml, scheduled-audit.yml, producer report, render.yaml, requirements.in, requirements.txt, exact_install_smoke.py, lock_requirements.sh. **No `app/**` change, no pyproject change, no connector/spatial/profile-contract/UI change, no forbidden path.** render.yaml diff is comment-only; `buildCommand: "pip install -r requirements.txt"` line neither added nor removed (unchanged).

---

## Observations (non-blocking; no rework required for acceptance)

1. **LOW — requirements.in header names the wrong tool.** `services/api/requirements.in` lines 9 and 11 describe the lock as produced by `pip-compile` / `pip-tools`, but the actual generator (`lock_requirements.sh`) and CI use `uv pip compile`. Producer report §6 documents the deliberate choice of uv over pip-tools; the requirements.in header comment just wasn't updated to match. Cosmetic/provenance-doc only — the real generator is correct and CI-enforced. Recommend fixing at the M0-T019 DEPENDENCY_SECURITY_POLICY landing.

2. **OBSERVATION — `--require-hashes` (CI) vs plain (render.yaml).** CI uses `pip install --require-hashes -r requirements.txt`; Render uses `pip install -r requirements.txt`. This is an intentional, documented equivalence (render.yaml:92-96: pip auto-enters hash-checking mode when any line is hashed; the flag just makes CI fail loudly on an unhashed line). Not a divergence.

3. **OBSERVATION — egg-info gitignore.** Producer flagged `services/api/**/*.egg-info/` not gitignored (.gitignore outside this task's allowed_paths). Follow-up recommended, correctly deferred.

4. **OBSERVATION — age-pin refresh debt.** websockets==16.1 / numpy==2.4.6 age pins will need deliberate refresh once successors clear the 7-day window (documented in requirements.in).

---

## Reproduction evidence (tails)
```
$ python -m pytest tests/ -q --co        -> 538 tests collected in 7.26s
$ ruff check .                           -> All checks passed!
$ grep -c hash=sha256 requirements.txt   -> 774   (851 lines, 27 pkgs)
$ grep -riE "dev|test|never" requirements.txt -> (no matches)
$ python scripts/exact_install_smoke.py (PYTHONPATH set)
    -> SMOKE OK (positive) ... validate_profile() accepted the valid fixture ... exit 0
$ python scripts/exact_install_smoke.py --expect-missing-jsonschema   [jsonschema present]
    -> SMOKE FAIL (negative): jsonschema is importable ...   exit 1   (proves not a no-op)
$ [jsonschema blocked via meta_path] scripts/exact_install_smoke.py --expect-missing-jsonschema
    -> SMOKE OK (negative): validate_profile() raised ModuleNotFoundError("No module named 'jsonschema'")  exit 0
$ grep -riE "ignore-vuln|allowlist|continue-on-error|\|\| true" workflows -> only comment refs (none active)
```

**DP-S4 negative jsonschema proof is confirmed GENUINE and would actually fail CI** if validate_profile ceased exercising the runtime import.

Relevant paths: `services/api/requirements.txt`, `services/api/requirements.in`, `services/api/scripts/exact_install_smoke.py`, `services/api/scripts/lock_requirements.sh`, `.github/workflows/ci.yml`, `.github/workflows/scheduled-audit.yml`, `render.yaml`, `services/api/app/profile/contract.py:231`.

**VERDICT: PASS** (LOW-1 requirements.in header tool-name is a documentation nit to fold into M0-T019; not blocking acceptance).
