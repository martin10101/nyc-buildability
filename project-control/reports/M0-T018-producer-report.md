# M0-T018 — Producer Report (AOS section-6 return packet)

- **Task ID:** M0-T018 — Backend production dependency parity and Python supply-chain enforcement
- **Producer:** cloud-architect (isolated worktree `agent-a101d24e4a5be9404`)
- **Status requested:** `awaiting_gate` (G2 self-check complete; G3 code-reviewer + G5 security-reviewer required, both != producer)
- **Report path:** `project-control/reports/M0-T018-producer-report.md`
- **Verification date:** 2026-07-20
- **Contracts / schema changed:** NONE. No `services/api/app/**` behavior change; no connector/spatial/profile-contract/UI change. `packages/contracts/**` untouched (schema-bundle drift check still green).

---

## 1. Summary of what was done

The EXACT Render production install (`pip install -r requirements.txt`, `render.yaml` buildCommand) is now:

1. **Complete** — `jsonschema` (a RUNTIME dep of `app/profile/contract.py::validate_profile`) is installed by the Render path; the previous mislabel ("dev/test tools … NEVER installed on Render") is gone and grep-provably absent.
2. **Deterministic** — `services/api/requirements.txt` is a GENERATED, fully hash-pinned universal lock (direct AND transitive) produced from `services/api/requirements.in` by `uv pip compile --universal --python-version 3.12 --generate-hashes`. Byte-identical on regeneration, including `--no-cache`.
3. **Advisory-clean** — `pip-audit` against the exact resolved tree reports ZERO known vulnerabilities; the prior nine `starlette==0.46.2` advisories are cleared by `starlette==1.3.1`.
4. **Release-age-controlled** — every one of the 27 locked packages is ≥ 7 days old (two transitive deps, `websockets` and `numpy`, were explicitly pinned to age-clean versions because the newest in-range releases failed the age gate / were resolver-ambiguous).
5. **Tested through the deployment command path** — new CI job `exact-production-install` runs Render's exact install, `pip check`, creates the real app, runs `validate_profile` on a committed valid fixture (POSITIVE), proves the gate FAILS with `jsonschema` removed (NEGATIVE), audits the tree (blocking), and runs the full API suite against the production-installed tree.
6. **Continuously audited** — new `scheduled-python-audit` workflow re-audits the production tree daily, on dependency-artifact PRs, and on demand; any finding fails the run.

## 2. Files changed (all within `allowed_paths`)

| File | Change |
|---|---|
| `services/api/requirements.txt` | REPLACED with a generated, hash-pinned universal lock (849 lines, 27 packages, LF, no BOM). |
| `services/api/requirements.in` | NEW — exact-version SOURCE for the lock; documents every deliberate pin + the pyproject-range relationship. |
| `services/api/scripts/lock_requirements.sh` | NEW — deterministic lock generator/verifier (pins uv 0.11.29; `--check` mode used by CI). |
| `services/api/scripts/exact_install_smoke.py` | NEW — positive/negative smoke that exercises `create_app()` + `validate_profile`. |
| `.github/workflows/ci.yml` | ADDED jobs `api-lock-verify` and `exact-production-install`; existing jobs untouched. |
| `.github/workflows/scheduled-audit.yml` | NEW — scheduled + dependency-PR + manual production-tree audit. |
| `render.yaml` | Comment-only update on the `nycdf-api` buildCommand to describe the generated hash-pinned lock. Install command unchanged (`pip install -r requirements.txt`). |

`services/api/pyproject.toml` was in scope but required NO change: `[project.dependencies]` already declares `jsonschema>=4.21,<5` as runtime and its dev-extras comment already states jsonschema is runtime. requirements.in pins satisfy every pyproject range.

## 3. CRITICAL FIRST STEP — target-set verification (before any change)

### 3.1 Compatibility (fastapi ↔ starlette ↔ uvicorn)
`fastapi==0.139.0` `requires_dist` includes `starlette>=0.46.0` (OPEN upper bound) → `starlette==1.3.1` is PERMITTED. `uvicorn` does not depend on starlette. The full tree resolves cleanly (see §5 lock).

### 3.2 Publication age (≥ 7 complete days as of 2026-07-20) — official source: PyPI JSON API `https://pypi.org/pypi/<pkg>/<ver>/json` (`upload_time_iso_8601`)

Target direct set:
```
fastapi==0.139.0            2026-07-01  age=18d   OK
starlette==1.3.1            2026-06-12  age=37d   OK
uvicorn==0.51.0             2026-07-08  age=11d   OK
jsonschema==4.26.0          2026-01-07  age=193d  OK
shapely==2.0.7              2025-01-31  age=534d  OK  (GEOS-digest pin, unchanged)
```

**STOP-condition findings that FORCED deliberate transitive pins (documented, not silent):**
```
fastapi==0.139.1/0.139.2    2026-07-16  age=4d    <7d  -> NOT used; 0.139.0 is the age-clean target
websockets==16.1.1          2026-07-17  age=2d    <7d  -> pinned websockets==16.1 (2026-07-10, 9d) instead
numpy (unpinned)            resolver-ambiguous     -> pinned numpy==2.4.6 (2026-05-18, 62d) for determinism
```
`websockets` (uvicorn[standard], constraint `>=10.4`) and `numpy` (shapely, constraint `>=1.14`) have OPEN upper bounds; letting the resolver pick the newest admitted `websockets==16.1.1` (2 days old, fails age gate) and produced non-deterministic numpy selection. Both are pinned to age-clean, advisory-free predecessors in `requirements.in` with rationale.

### 3.3 Final locked tree — every package ≥ 7 days (DP-S7)
Age sweep over all 27 locked packages (command: PyPI JSON per package): **packages < 7 days: NONE** (minimum is `anyio==4.14.2` at exactly 7d). Full table:
```
annotated-doc==0.0.4 251d   annotated-types==0.7.0 790d   anyio==4.14.2 7d
attrs==26.1.0 122d          click==8.4.2 25d              colorama==0.4.6 1363d
fastapi==0.139.0 18d        h11==0.16.0 451d              httptools==0.8.0 55d
idna==3.18 47d              jsonschema==4.26.0 193d        jsonschema-specifications==2025.9.1 314d
numpy==2.4.6 62d            pydantic==2.13.4 74d           pydantic-core==2.46.4 74d
python-dotenv==1.2.2 140d   pyyaml==6.0.3 297d             referencing==0.37.0 279d
rpds-py==2026.6.3 19d       shapely==2.0.7 534d            starlette==1.3.1 37d
typing-extensions==4.16.0 17d  typing-inspection==0.4.2 291d  uvicorn==0.51.0 11d
uvloop==0.22.1 276d         watchfiles==1.2.0 62d          websockets==16.1 9d
```

## 4. Acceptance scenarios DP-S1 .. DP-S9

Local runs used bounded temp venvs on Python 3.11/pip 25.2 (all cleaned up; disk stayed ~32 GB free). Where a check requires the Render/CI Python-3.12 exact-install environment, the BINDING evidence is the CI job wired in this task; that is marked **CI-AUTHORITATIVE**.

### DP-S1 — parity (PASS)
```
$ grep -rniE "jsonschema" requirements.txt requirements.in pyproject.toml | grep -iE "dev|test|never"
(no matches; grep exit 1)          # no runtime dep mislabeled dev/test-only
$ grep -nE "^jsonschema==" requirements.txt
93:jsonschema==4.26.0 \            # jsonschema IS installed by the Render path
```
requirements.in direct pins all satisfy pyproject ranges: fastapi 0.139.0∈[0.115,1); uvicorn 0.51.0∈[0.30,1); jsonschema 4.26.0∈[4.21,5); shapely 2.0.7==2.0.7.

### DP-S2 — determinism (PASS)
- Lock is fully hash-pinned (every line carries `--hash=sha256:…`), direct + transitive.
- Idempotent: `uv pip compile … --output-file` re-run is **byte-identical** (`cmp` clean) on warm cache AND `--no-cache`:
```
RUN2 byte-identical
RUN3(no-cache) byte-identical
```
- Render install is hash-verified automatically: pip enters hash-checking mode whenever any requirement has a hash, and every line does.
- CI-AUTHORITATIVE: `api-lock-verify` runs `scripts/lock_requirements.sh --check` (pinned uv 0.11.29) and fails on any drift.

### DP-S3 — exact-production-install (positive) (PASS locally on the runtime deps; CI-AUTHORITATIVE for the full 3.12 install)
`validate_profile(full_example.json)` executed with the EXACT locked engine `jsonschema==4.26.0` + `referencing==0.37.0`:
```
validate_profile(full_example.json) -> SUCCESS (no exception)
=== EXIT 0 ===
```
CI job `exact-production-install`: clean 3.12 env → `pip install --require-hashes -r requirements.txt` → `pip install --no-deps .` → `pip check` → `python scripts/exact_install_smoke.py` (create_app + validate_profile on the committed valid fixture).

### DP-S4 — exact-production-install (negative, the key proof) (PASS)
With `jsonschema` uninstalled, `validate_profile` on the same fixture raised loudly:
```
Uninstalling jsonschema-4.26.0: Successfully uninstalled jsonschema-4.26.0
EXPECTED NEGATIVE: validate_profile raised ModuleNotFoundError -> ModuleNotFoundError("No module named 'jsonschema'")
=== EXIT 0 ===
```
This is the exact production defect (missing runtime jsonschema on Render) made visible; the health endpoint would NOT catch it because the import is function-local at `contract.py:231`. CI wires this as the `NEGATIVE smoke` step (`--expect-missing-jsonschema`).

### DP-S5 — API suite on production tree (CI-AUTHORITATIVE)
CI job installs the production tree, then adds ONLY the test-RUNNER deps (`pytest>=8,<9`, `httpx>=0.27,<1` for `TestClient`) and runs `pytest -q`. Production runtime deps still come from the locked tree, not from dev extras. Expected count ≥ 538 (repo has 435 base `def test_` functions plus parametrize expansions; the existing `api` job passes at that count). Disclosed limitation: pytest/httpx are dev-only test tools and are legitimately NOT in the production lock — they are added on top solely to execute the suite.

### DP-S6 — pip-audit zero (PASS)
Against the exact resolved production tree:
```
$ pip-audit -r requirements.txt --no-deps --strict
No known vulnerabilities found
=== EXIT 0 ===
```
Proof the starlette bump resolved the advisories — auditing the OLD pin:
```
$ pip-audit -r <(echo starlette==0.46.2) --no-deps
Found 9 known vulnerabilities in 1 package
starlette 0.46.2  PYSEC-2026-161 / 248 / 249 / 1941 / 1942 / 2280 / 2281   Fix: 1.0.1 / 1.3.0 / 1.3.1 / 0.47.2 / 0.49.1 / 1.1.0
=== EXIT 1 ===
```
`PYSEC-2026-249` lists Fix Version **1.3.1** — the exact target. CI step is BLOCKING (`pip-audit … --strict`, no `--ignore-vuln`/allowlist/print-only; non-zero exit fails the build), run via `pipx run` so pip-audit's own deps do not perturb the production tree.

### DP-S7 — release-age (PASS)
See §3.3: all 27 locked packages ≥ 7 days; deliberate age pins for `websockets`/`numpy` documented in `requirements.in`.

### DP-S8 — scheduled audit (PASS)
`.github/workflows/scheduled-audit.yml`: `schedule` (daily `17 6 * * *`), `pull_request` on `requirements.txt`/`requirements.in`/`pyproject.toml`, and `workflow_dispatch`. Failure is a red run (blocking; not silent). Simulated-failing-advisory path already demonstrated by the `starlette==0.46.2` audit above (exit 1 + advisory table) — the same `pip-audit … --strict` command the scheduled job runs.

### DP-S9 — regression (PASS locally where runnable; remainder CI-AUTHORITATIVE)
```
ruff check .                                   -> All checks passed!
services/api/scripts/sync_contract_schemas.py --check -> OK: byte-identical (contract drift)
pip-audit (locked tree)                        -> No known vulnerabilities found
lock idempotency                               -> byte-identical (warm + --no-cache)
```
Full pytest ≥ 538 and the exact 3.12 install smoke run in the new CI jobs (`api`, `exact-production-install`).

## 5. The exact resolved production tree (versions)
```
annotated-doc==0.0.4  annotated-types==0.7.0  anyio==4.14.2  attrs==26.1.0  click==8.4.2
colorama==0.4.6 (; sys_platform=='win32')  fastapi==0.139.0  h11==0.16.0  httptools==0.8.0
idna==3.18  jsonschema==4.26.0  jsonschema-specifications==2025.9.1  numpy==2.4.6
pydantic==2.13.4  pydantic-core==2.46.4  python-dotenv==1.2.2  pyyaml==6.0.3
referencing==0.37.0  rpds-py==2026.6.3  shapely==2.0.7  starlette==1.3.1
typing-extensions==4.16.0  typing-inspection==0.4.2  uvicorn==0.51.0
uvloop==0.22.1 (; sys_platform!='win32')  watchfiles==1.2.0  websockets==16.1
```
The universal lock carries environment markers so the SAME file is byte-reproducible on Windows (dev) and Linux (Render/CI): `colorama` win32-only; `uvloop` non-win32 — the earlier plain `pip-compile` (Windows) lock had MISSED uvloop entirely, which would have broken hash-verified install on Render. `referencing==0.37.0` is present (required by `contract.py`'s `from referencing import Registry`).

## 6. Assumptions and defaults
- **Lock tooling: `uv` (pinned 0.11.29).** Chosen over pip-tools because pip-tools 7.x strips environment markers and resolves for the local platform only, yielding a Windows-specific, non-cross-platform lock (missing Linux `uvloop`). `uv pip compile --universal --python-version 3.12` produces a marker-preserving, target-python lock reproducible on any host. If the reviewer prefers a different pinned tool, the `requirements.in` source is tool-agnostic.
- **`--no-header`** on the lock: uv's default header embeds the absolute `--output-file` path, which differs between environments and would break the byte-identical CI check; provenance instead lives in `requirements.in` + `lock_requirements.sh`.
- **numpy pinned to 2.4.6** (not the newest 2.5.1) to remove resolver ambiguity AND keep age ≥ 7d; both are advisory-free, 2.4.6 is the more-established (62d).
- **"7 complete days"** interpreted as age ≥ 7 (anyio at exactly 7d admitted).

## 7. Known limitations
- The full 3.12 exact-install proof, `pip check`, and full pytest ≥ 538 are CI-AUTHORITATIVE — local Windows Python is 3.11 (pyproject requires ≥3.12) and the universal lock's Linux-only `uvloop` cannot install on Windows, so local runs exercised the runtime deps and script logic but not the complete Linux/3.12 install. The wired CI jobs provide the binding evidence.
- `services/api/*.egg-info/` is not currently gitignored (a stray one from a local test install was deleted; nothing tracked). `.gitignore` is outside this task's `allowed_paths`; recommend a follow-up to ignore `*.egg-info/` under `services/api`.
- pip-audit's advisory DB is point-in-time (2026-07-20); the scheduled workflow exists precisely to catch advisories disclosed later against these pinned versions.

## 8. Security / provenance impact
- Removes a live production defect: the deployed Render tree omitted a runtime dependency (`jsonschema`), so the first validated property request would have raised `ModuleNotFoundError` — now installed and gate-proven.
- Eliminates nine `starlette==0.46.2` advisories via `starlette==1.3.1`; production tree is advisory-clean and blocking-audited on every push, PR, and schedule.
- Supply-chain hardening: fully hash-pinned install (hash-verified by pip), release-age control (≥7d) on every direct+transitive package, deterministic reproducible lock, no advisory suppression/allowlist anywhere.
- No secrets touched; no app behavior changed; no production provisioning/deploy performed.

## 9. New risks / dependencies
- Adds a build-time tool dependency on `uv==0.11.29` for lock regeneration (CI-installed via pip; not a runtime dep). Bumping uv requires re-verifying byte-identity.
- `websockets`/`numpy` age pins will need deliberate refresh once newer releases clear the 7-day window (documented in `requirements.in`).

## 10. Recommended next tasks
1. Follow-up: add `services/api/**/*.egg-info/` (and any build artifacts) to `.gitignore` (outside this task's scope).
2. Wire a notification (e.g., issue/Slack) on `scheduled-python-audit` failure so a newly disclosed advisory is actionable without watching the Actions tab.
3. On the M0-T019 DEPENDENCY_SECURITY_POLICY landing, reconcile the shared age/audit rules with this task's implementation (both should reference one policy).
