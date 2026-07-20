# M0-T020 Producer Report — Python dependency-policy enforcement follow-up

- **Task:** M0-T020 (infrastructure; post-acceptance follow-up to accepted, immutable M0-T018)
- **Producer:** cloud-architect
- **Requested status:** `awaiting_gate` (G3 code-reviewer, G4 integration, G5 security-reviewer; G0/G2 recorded by orchestrator)
- **Worktree branch:** control/session14-handoff-midwave worktree (agent-ab14f31e8c53fac99), branched from amended main
- **Verification date/time:** 2026-07-20, authoritative UTC now = 2026-07-20T18:1x–18:43Z (taken from live PyPI `Date` header; local clock matched)
- **Execution environment:** local Python 3.11.9 (bounded temp venvs, all cleaned up; disk 24.06→23.98 GB free, never below 4 GB floor). The suite/app target Python 3.12; the **authoritative full-suite + full-CI proof is GitHub Actions on Python 3.12** — local results are strong corroboration, noted per item.
- **OUTCOME: COMPLETED.** No STOP condition triggered. The production runtime lock is byte-identical (unchanged); pytest 9.0.3 runs the full suite with identical coverage and no test weakening; the whole tooling tree is age-clean and advisory-free.

---

## 1. Re-verification table (live PyPI + OSV, hash-aware where a lock exists)

`now` = 2026-07-20T18:1xZ from PyPI `Date` header. Threshold = 604800 s (7 days). "age" uses the **newest upload among lock-admitted sha256 artifacts** (for locked packages) or newest overall (for candidate screening). All advisory checks via OSV `api.osv.dev/v1/query` (PyPI ecosystem).

### 1a. DIRECT tooling — final admitted versions

| package | version | newest admitted-artifact upload (UTC) | age | yanked? | advisories | origin |
|---|---|---|---|---|---|---|
| uv | **0.11.28** | 2026-07-07T23:12:47Z | 12.80d | no (19 files) | NONE | pypi.org → github.com/astral-sh/uv (Astral) |
| pip | **26.1.2** | 2026-05-31T17:33:58Z | 50.04d | no | NONE | pypi.org (PyPA) |
| setuptools | **83.0.0** | 2026-07-04T15:31:22Z | 16.12d | no | NONE | pypi.org (PyPA) |
| wheel | **0.46.2** | 2026-01-21T23:55:25Z | 179.77d | no | NONE | pypi.org (PyPA) |
| pytest | **9.0.3** | 2026-04-07T17:16:18Z | 104.05d | no | NONE | pypi.org (pytest-dev) |
| httpx | **0.28.1** | 2024-12-06T15:37:23Z | 591.12d | no | NONE | pypi.org (encode) |
| ruff | **0.13.0** | 2025-09-10T16:25:37Z | 313.09d | no (19 files) | NONE | pypi.org (Astral) |
| pyyaml | **6.0.3** | 2025-09-29T20:27:46Z | 293.92d | no (73 files) | NONE | pypi.org (yaml) |
| pip-audit | **2.10.1** | 2026-06-10T22:17:01Z | 39.84d | no | NONE | pypi.org (pypa) |
| filelock | **3.29.7** | 2026-07-08T05:46:58Z | 12.53d | no | NONE | pypi.org (tox-dev) — age down-pin |
| platformdirs | **4.10.0** | 2026-05-28T03:32:53Z | 53.62d | no | NONE | pypi.org (platformdirs) — age down-pin |

### 1b. Key REJECTED candidates (why not admitted)

| package | version | reason rejected |
|---|---|---|
| uv | 0.11.29 | 2026-07-15T18:43:22Z → **4.98d < 7d** (fails age gate). Was wired at ci.yml:140 + lock_requirements.sh; **downgraded to 0.11.28**. |
| wheel | 0.46.0 | **YANKED (2/2)** + advisory GHSA-8rrh-rw8j-w5fx / PYSEC-2026-2047. |
| wheel | 0.46.1 | **YANKED (2/2)** + advisory GHSA-8rrh-rw8j-w5fx / PYSEC-2026-2047. |
| filelock | 3.31.1 | 2026-07-20T03:14:32Z → **0.63d < 7d** (unconstrained resolver pick; down-pinned to 3.29.7). |
| platformdirs | 4.10.1 | 2026-07-18T03:53:43Z → **2.60d < 7d** (unconstrained resolver pick; down-pinned to 4.10.0). |

### 1c. FULL tooling closure (42 pkgs) — every DIRECT + TRANSITIVE, hash-aware age + advisory

All 42 packages in `requirements-tools.lock` were verified with every lock-admitted sha256 matched to a live PyPI artifact, age ≥ 7d, unyanked, zero OSV advisories. Closest-to-boundary transitive: **anyio 4.14.2 = 7.92d** (2026-07-12). Representative transitives (all PASS): boolean-py 5.0, cachecontrol 0.14.4, certifi 2026.6.17, charset-normalizer 3.4.9 (93/93 hashes matched), colorama 0.4.6, cyclonedx-python-lib 11.11.0, defusedxml 0.7.1, h11 0.16.0, httpcore 1.0.9, idna 3.18, iniconfig 2.3.0, license-expression 30.4.4, markdown-it-py 4.2.0, mdurl 0.1.2, msgpack 1.2.1 (66/66), packageurl-python 0.17.6, packaging 26.2, pip-api 0.0.34, pip-requirements-parser 32.0.1, pluggy 1.6.0, py-serializable 2.1.0, pygments 2.20.0, pyparsing 3.3.2, requests 2.34.2, rich 15.0.0, sortedcontainers 2.4.0, tomli 2.4.1 (47/47), tomli-w 1.2.0, typing-extensions 4.16.0, urllib3 2.7.0. **Result: FAILURES = NONE.**

The production runtime lock (`requirements.txt`, 27 pkgs incl. direct+transitive) was likewise age-verified end-to-end (closest: websockets 16.1 = 10.50d) and pip-audits to zero — see §4.

---

## 2. pyproject.toml diff (exact — proves ONLY the pytest specifier + comment changed)

```diff
 [project.optional-dependencies]
 dev = [
-    "pytest>=8,<9",
+    # M0-T020: pytest floored at 9.0.3 to admit the advisory-free fix for
+    # CVE-2025-71176 / PYSEC-2026-1845 (the <9 cap held 8.x); the tooling lock
+    # (services/api/requirements-tools.lock) hash-pins pytest==9.0.3 exactly and
+    # every audited CI job installs pytest from that lock, not from this range.
+    "pytest>=9.0.3,<10",
     "httpx>=0.27,<1",
     "ruff>=0.6,<1",
```

`git diff HEAD -- services/api/pyproject.toml` shows exactly this hunk and nothing else. No other dependency, no version cap, **no `[tool.*]` / `[tool.pytest.ini_options]`** change. Old cap `pytest>=8,<9` is grep-absent; new range begins at fixed 9.0.3. **(TP-S14)**

---

## 3. Tooling source manifest + lock

- **`services/api/requirements-tools.in`** — 11 DIRECT pins: uv 0.11.28, pip 26.1.2, setuptools 83.0.0, wheel 0.46.2, pytest 9.0.3, httpx 0.28.1, ruff 0.13.0, pyyaml 6.0.3, pip-audit 2.10.1, **+ 2 age-control down-pins** filelock 3.29.7 and platformdirs 4.10.0.
- **`services/api/requirements-tools.lock`** — full DIRECT+TRANSITIVE closure: **42 packages**, SHA-256 hashes on every line, 35229 bytes, LF, sha256 `803e90f9cf4a1ac5e2b4c86e79db491c67924453cab9c6950bb8754094185228`.
- **Generated by ONE documented script:** `services/api/scripts/lock_tools.sh` (mirrors `lock_requirements.sh`; UV_VERSION=0.11.28; `uv pip compile --universal --python-version 3.12 --generate-hashes --no-header`; `--check` mode).
- **Byte-identical regeneration:** two independent regenerations produced identical sha256 `803e90f9…`. `bash scripts/lock_tools.sh --check` → `OK: requirements-tools.lock is byte-identical to a fresh uv 0.11.28 lock.` (exit 0).
- **No duplicated pin list:** the two manifests (`requirements.in`, `requirements-tools.in`) are the only authoritative pin sources; `lock_tools.sh` and `lock_requirements.sh` each read one and share no embedded list.
- **CI bootstraps uv FROM the lock:** every job installs tooling via `pip install --require-hashes -r requirements-tools.lock` using the runner's existing pip; **no unlocked `uv==…` download precedes lock generation/verification**. (Verified: the `-r lock uv` single-package form fails require-hashes; installing the full hash-pinned lock puts the `uv` console script on PATH — `uv --version` → 0.11.28.) **(TP-S3)**

---

## 4. Audit results (both ZERO, blocking)

Installed `requirements-tools.lock` hash-verified into a clean venv, then:

- **PRODUCTION lock:** `pip_audit -r requirements.txt --no-deps --strict` → `No known vulnerabilities found` (exit 0).
- **TOOLING lock:** `pip_audit -r requirements-tools.lock --no-deps --strict` → `No known vulnerabilities found` (exit 0).

No `--ignore-vuln`, no allowlist, no waiver anywhere. The two `--no-deps` INFO warnings from pip-audit are informational (each lock is already the full transitive closure, so `-r <lock> --no-deps` audits exactly the pinned tree — the accepted M0-T018 pattern). **(TP-S7)**

---

## 5. Production-lock byte-identity vs git blob (immutability — TP-S2 / TP-S12)

- Git blob `HEAD:services/api/requirements.txt`: sha256 **`a75dc743df533568bd38c1b70b3bee1b82f64c77cb5ae771cd5a32053f956c37`**, 67325 bytes, LF.
- Regenerated with **uv 0.11.28** (exact `lock_requirements.sh` flags): raw sha256 **`a75dc743…` = git blob exactly** (67325 bytes, LF). **BYTE-IDENTICAL → no runtime-lock change committed.**
- `git diff HEAD -- services/api/requirements.txt` = empty (git sees no change).
- **CRLF note (documented, not a real diff):** the Windows working-copy `requirements.txt` on disk has CRLF, so a raw `diff`/sha of the working copy vs a fresh LF uv output differs on *every line* — this is purely line endings. LF-normalized, the working copy, the fresh regen, and the git blob **all** hash to `a75dc743…`. `core.autocrlf=true`; on Linux CI git checks out LF and uv writes LF, so `lock_requirements.sh --check` passes there (as in accepted M0-T018 CI). The uv 0.11.29→0.11.28 downgrade does **not** perturb the production lock.

---

## 6. Age-gate: positive + boundary + fail-closed (TP-S8 / TP-S9 / TP-S10)

New tool: **`services/api/scripts/dependency_age_gate.py`** (stdlib-only; live UTC from PyPI `Date` header; live PyPI JSON per version; newest **lock-admitted-hash** artifact timestamp; ≥604800s full-second compare; covers BOTH locks direct+transitive; per-package name/version/timestamp/age/PASS-FAIL; **fails closed** on outage/missing-metadata/malformed-timestamp/unmatched-hash/unhashed-pin/ambiguous; **no agent exception path** — never reads any allowlist/suppression).

- **LIVE gate over both real locks:** `python scripts/dependency_age_gate.py requirements.txt requirements-tools.lock` → per-package PASS lines for all 27 production + 42 tooling packages → `RESULT: PASS — every admitted artifact is >= 7 days old` (exit 0).
- **Deterministic unit tests** (`services/api/scripts/tests/test_dependency_age_gate.py`, injected fixed UTC now, offline): **17 passed** under pytest 9.0.3. Covers:
  - **604800 s → PASS**, **604799 s → FAIL** (both boundary tests).
  - Multi-artifact: keys on the **newest lock-admitted** artifact (a too-new admitted artifact FAILS; a too-new artifact **not** in the lock is ignored — the "old version number, new artifact" bypass defence).
  - Fail-closed: unmatched hash, unhashed pin, malformed timestamp, missing timestamp, registry outage (raising provider → FAIL not skip), missing `urls`, missing `Date` header, hash-before-pin lock corruption.
  - `utc_now` reads the server `Date` header (not the local clock).
- **No agent waiver path exists** (TP-S10): the gate has no allowlist/exception input; pip-audit remains the separate blocking advisory gate; any emergency age-only exception is an owner action outside the tool and can never waive an advisory.

---

## 7. pytest 9.0.3 compatibility (PYTEST 9 STOP — cleared)

- **Collection parity:** `pytest --collect-only` node-ID sets under **pytest 8.4.2** and **pytest 9.0.3** are **byte-identical** (`diff` empty, exit 0). **538 tests collected** in both. No collection-format change, no lost/added tests.
- **Full suite:** under **pytest 9.0.3** → **538 passed, 1 warning** (6.29s, Python 3.11 local). Baseline pytest 8.4.2 → **538 passed, 1 warning**. The single warning is the pre-existing `StarletteDeprecationWarning` about httpx/starlette TestClient — unrelated to pytest 9, identical in both. **No new pytest-9 warnings.**
- **No test weakened/deleted/skipped/xfailed/bypassed** to accommodate pytest 9; the same test files/assertions pass. **(TP-S14, PYTEST 9 STOP satisfied)**
- **Authoritative note:** local run is Python 3.11 (my PC); the suite targets 3.12. The definitive full-suite pass on Python 3.12 is **CI (`api`, `exact-production-install`)** — I could not run the app package locally because it declares `requires-python = ">=3.12"` (documented; I collected/ran via PYTHONPATH with runtime deps + pytest, which is why 538/538 was reproducible locally).
- The `contracts-typegen` generator tests (stdlib-only) also pass under pytest 9.0.3: **14 passed**.

---

## 8. Full Python-CI-download → lock mapping (TP-S13)

Every Python package download path in CI, reconciled. **No unlisted Python download remains; no STOP-condition exception was required.** (npm/Playwright in web/web-e2e untouched — M0-T019.)

| Workflow / job | Python step | Before | After (→ lock) |
|---|---|---|---|
| ci.yml **web-e2e** | serve real app | `pip install --upgrade pip` + `pip install ./services/api` | `pip install --require-hashes -r requirements.txt` (PRODUCTION) + `pip install --no-deps .` |
| ci.yml **api** | ruff + pytest | `pip install --upgrade pip` + `pip install .[dev]` | `--require-hashes -r requirements-tools.lock` (TOOLING) + `--require-hashes -r requirements.txt` (PRODUCTION) + `pip install --no-deps .` |
| ci.yml **api-lock-verify** | pinned uv | `pip install "uv==0.11.29"` | `pip install --require-hashes -r requirements-tools.lock` (TOOLING; uv 0.11.28 on PATH) |
| ci.yml **api-tooling-lock-verify** (NEW) | lock check + age unit tests | — | `--require-hashes -r requirements-tools.lock` (TOOLING) |
| ci.yml **exact-production-install** | prod install | `pip install --upgrade pip` + `--require-hashes -r requirements.txt` | `--require-hashes -r requirements.txt` (PRODUCTION; pip upgrade removed) |
| ci.yml **exact-production-install** | app | `pip install --no-deps .` | unchanged (`--no-deps .`) |
| ci.yml **exact-production-install** | audit | `pipx run --spec "pip-audit==2.10.1" …` | isolated venv `--require-hashes -r requirements-tools.lock` (TOOLING) → dual audit prod+tooling |
| ci.yml **exact-production-install** | age gate (NEW) | — | isolated-venv python runs `dependency_age_gate.py` over both locks |
| ci.yml **exact-production-install** | restore | `--require-hashes -r requirements.txt` | unchanged (PRODUCTION) |
| ci.yml **exact-production-install** | test runner deps | `pip install "pytest>=8,<9" "httpx>=0.27,<1"` | `--require-hashes -r requirements-tools.lock` (TOOLING; shares 6 identical transitives with prod so prod pins preserved — re-`pip check` step added) |
| ci.yml **contracts** | render.yaml yaml check | `pip install --quiet pyyaml` | `python3 -m pip install --require-hashes -r services/api/requirements-tools.lock` (TOOLING → pyyaml) |
| ci.yml **contracts-typegen** | generator tests | `pip install --quiet "pytest>=8,<9"` | `python3 -m pip install --require-hashes -r services/api/requirements-tools.lock` (TOOLING → pytest) |
| ci.yml **contracts-schema-bundle** | drift check | stdlib-only (no install) | unchanged |
| ci.yml **control-plane** | control tests | stdlib-only (no install) | unchanged |
| scheduled-audit.yml **audit** | pip-audit | `pip install "pip-audit==2.10.1"` (pip-resolved transitives) | `--require-hashes -r requirements-tools.lock` (TOOLING) → dual audit prod+tooling + age gate |

Lock-only invariant verified by grep: no actual `run:` command contains `pip install --upgrade pip`, `.[dev]`, `pytest>=`, `httpx>=`, `pipx`, or unpinned `pyyaml`/`pip-audit` — every such string that remains is in an explanatory comment. Every `pip install` command uses `--require-hashes -r <lock>` or `--no-deps .`. **(TP-S4, TP-S5, TP-S6, TP-S13)**

Shared packages across the two locks (anyio, colorama, h11, idna, pyyaml, typing-extensions) are at **identical** versions — no conflict — so layering tooling on top of the production tree preserves every production pin (verified: `pip check` → "No broken requirements found"; production pins fastapi 0.139.0 / starlette 1.3.1 / uvicorn 0.51.0 / shapely 2.0.7 / numpy 2.4.6 / jsonschema 4.26.0 unchanged after adding tooling).

---

## 9. requirements.in header fix (TP-S1)

Replaced the wrong `pip-compile … --output-file=requirements.txt requirements.in` regeneration instruction with the real command:
```
uv pip compile --universal --python-version 3.12 --generate-hashes --no-header requirements.in --output-file requirements.txt
```
naming `services/api/scripts/lock_requirements.sh` (regenerate) and `… --check` (CI), pinned uv 0.11.28. The incidental "pip-compile alone would pick…" phrase was reworded to "the resolver alone would pick…". `grep 'pip-compile' services/api/requirements.in` → **0 matches**. Comment-only edits; production lock re-verified byte-identical after them (§5).

---

## 10. uv downgrade sites (TP-S2)

- `services/api/scripts/lock_requirements.sh`: `UV_VERSION="0.11.29"` → `"0.11.28"` (+ explanatory comment; kept in lockstep with `lock_tools.sh`).
- `.github/workflows/ci.yml` **api-lock-verify**: `pip install "uv==0.11.29"` → `pip install --require-hashes -r requirements-tools.lock` (uv installed FROM the lock, hash-verified, on PATH).

---

## 11. ruff (from tooling lock)

`ruff 0.13.0` (installed from the tooling lock) `check .` over `services/api` → **All checks passed!** (exit 0), including the two new scripts. (Ruff selects E/F/I/UP/B; new files were brought to compliance — `collections.abc` imports, `datetime.UTC`, line length.)

---

## 12. egg-info hygiene (TP-S11)

`.gitignore` gains `services/api/**/*.egg-info/`. Verified: a stray `services/api/nyc_buildability_api.egg-info` is matched by `git check-ignore` (`.gitignore:16`) and does not appear in `git status`. Stray directory removed to leave a clean tree.

---

## 13. Complete list of files created / modified

**Modified:**
- `services/api/requirements.in` — header now names `lock_requirements.sh` + the exact pinned uv 0.11.28 command; `pip-compile` removed (comments only; lock unchanged).
- `services/api/pyproject.toml` — ONLY the `[dev]` pytest specifier `>=8,<9` → `>=9.0.3,<10` (+ adjacent comment).
- `services/api/scripts/lock_requirements.sh` — `UV_VERSION` 0.11.29 → 0.11.28.
- `.github/workflows/ci.yml` — Python jobs install from the two hash-pinned locks; unpinned pip/`.[dev]`/`pipx`/ranged-tool installs removed; dual pip-audit + live age gate added to `exact-production-install`; new `api-tooling-lock-verify` job (tooling-lock byte-identity + age-gate unit tests).
- `.github/workflows/scheduled-audit.yml` — pip-audit installed from the tooling lock; dual audit (prod+tooling) + daily age gate; PR paths extended to the tooling artifacts + age gate.
- `.gitignore` — `services/api/**/*.egg-info/`.

**Created:**
- `services/api/requirements-tools.in` — 11 direct tooling pins (source manifest).
- `services/api/requirements-tools.lock` — 42-package hash-pinned closure (sha256 `803e90f9…`).
- `services/api/scripts/lock_tools.sh` — the one documented tooling-lock generator (`--check` mode; uv 0.11.28).
- `services/api/scripts/dependency_age_gate.py` — machine-enforced release-age gate.
- `services/api/scripts/tests/test_dependency_age_gate.py` — 17 deterministic offline unit tests.

**Unchanged (verified):** `services/api/requirements.txt` (byte-identical git blob `a75dc743…`); all `project-control/tasks/M0-T018.json` + `M0-T018-*` reports; no `services/api/app/**`; no npm/Playwright/`generate-lockfile.yml`/`secret-scan.yml`.

---

## 14. Assumptions, uncertainties, nonblocking concerns for reviewers

1. **Local Python is 3.11; suite targets 3.12.** I ran collection + the full suite (538/538) + age-gate unit tests via PYTHONPATH with runtime deps + pytest 9.0.3 locally, and installed/audited/age-gated both locks hash-verified. I could **not** `pip install ./services/api` locally (declares `requires-python>=3.12`). **CI on Python 3.12 (`api`, `web-e2e`, `exact-production-install`, `api-lock-verify`, `api-tooling-lock-verify`, `contracts`, `contracts-typegen`, scheduled-audit) is the authoritative proof** and should be confirmed green by the gate.
2. **`datetime.UTC`** (used in the age gate after ruff UP017 autofix) requires Python ≥3.11 — satisfied on the 3.12 CI target and my 3.11 local. Not a concern for CI.
3. **`$RUNNER_TEMP` / venv `bin/`** paths in `exact-production-install`'s isolated audit venv are Linux-runner conventions (`ubuntu-latest`); `RUNNER_TEMP` is a default Actions env var and Linux venvs use `bin/`. Reviewers should confirm the isolated-audit steps run green in CI (I validated the YAML parses and the install/audit/age-gate logic locally, but the exact `$RUNNER_TEMP/auditenv/bin/...` invocation only executes on the runner).
4. **Full tooling lock installed where a single tool would suffice** (contracts→pyyaml, contracts-typegen→pytest, api-lock-verify→uv). Rationale: pip's `--require-hashes` rejects the `-r lock <singlepkg>` form (the bare package is treated as unpinned), and maintaining a third hash-pinned subset would duplicate an authoritative pin list (forbidden). Installing the full hash-pinned, audited, age-gated lock is correct and conflict-free; the extra packages are inert for those stdlib-only/py-only steps. Flagging as a deliberate design choice, not an oversight.
5. **`exact-production-install` final pytest step** now installs the full tooling lock on top of the production tree. The two locks share 6 transitives at identical versions, so all production runtime pins are preserved (a second `pip check` step guards this). The proof "the production tree runs the whole suite" holds: the app's runtime imports come from the production lock; pytest/httpx come from the tooling lock. pip-audit's extra transitives in that env are test-only and never change what the app imports.
6. **No live-network flake handling in CI for the age gate beyond fail-closed.** By contract the gate fails closed on registry outage. If PyPI/OSV is transiently unreachable during a CI run, the age-gate step will fail the build (by design). This is the intended safe behavior; reviewers should note a transient PyPI outage would require a re-run, not a waiver.
7. **`api` job pip cache key** still points at `pyproject.toml`. Installs are hash-verified from the locks regardless, so this is correctness-neutral; I left it to avoid cache-key churn and to keep the diff within the tightest scope. Reviewers may wish to note it for a future tidy-up (not required by this packet).
