<!-- Verbatim independent-reviewer return preserved by the orchestrator per the report-preservation rule (ADR-005; transport decoding only). Reviewer: security-reviewer. Gate: G5. Task: M0-T020. Bound to task PR #60 head SHA 9da5449e02962c4ac75bf337e8fadefe827e75ab. Verdict: PASS (zero blocking). -->

# G5 SECURITY & PRIVACY GATE REPORT — M0-T020

| Field | Value |
|---|---|
| **Task ID** | M0-T020 — Python dependency-policy enforcement follow-up |
| **PR reviewed** | #60, branch `task/M0-T020-python-dependency-policy` |
| **Head SHA** | `9da5449e02962c4ac75bf337e8fadefe827e75ab` (verified: worktree HEAD == target SHA) |
| **Reviewer** | security-reviewer (independent; NOT the producer) |
| **Gate** | G5 (Security and privacy) |
| **Review location** | Clean worktree `.claude\worktrees\agent-ab14f31e8c53fac99` (read-only) |
| **Method** | Static inspection of the clean checkout + independent CI-log evidence on the exact SHA (`gh pr checks`, `gh run view --log`) |
| **VERDICT** | **PASS** |

Gate recording is delegated to the orchestrator per ADR-005 (I am read-only; I did not run `project_control.py`, git writes, or any write-producing command).

---

## Scope of change (all 12 changed files within `allowed_paths`; forbidden paths clean)

```
.github/workflows/ci.yml                 .github/workflows/scheduled-audit.yml
.gitignore                               services/api/pyproject.toml
services/api/requirements.in             services/api/requirements-tools.in
services/api/requirements-tools.lock     services/api/scripts/dependency_age_gate.py
services/api/scripts/lock_requirements.sh services/api/scripts/lock_tools.sh
services/api/scripts/tests/test_dependency_age_gate.py
project-control/reports/M0-T020-producer-report.md
```
Confirmed **NONE** of the forbidden paths appear in the diff: no `services/api/app/**`, no `generate-lockfile.yml`, no `secret-scan.yml`, no `apps/web/**`, no `M0-T018` task/report files. `requirements.txt` (production runtime lock) is **byte-identical to main** (no runtime dependency-surface change — the immutability constraint holds).

---

## Focus-area findings

### 1. Hash-pinning integrity — PASS
- Every audited Python tooling install path uses `pip install --require-hashes -r requirements-tools.lock` (ci.yml lines 123, 157, 183, 230, 269, 288, 317; scheduled-audit.yml line 66). The only non-hashed installs are `pip install --no-deps .` (the local app, which pulls no dependencies) and `pip install --require-hashes -r requirements.txt` (production runtime lock).
- `requirements-tools.lock` hash-pins **all 42 packages** (uv 0.11.28, pip 26.1.2, pip-audit 2.10.1, pytest 9.0.3, setuptools 83.0.0, wheel 0.46.2, httpx 0.28.1, ruff 0.13.0, pyyaml 6.0.3 + transitives) with **389 `--hash=sha256:` lines** — direct AND transitive.
- **No unlocked uv is ever downloaded before the lock.** `uv==` appears only in comments and the operator-hint `echo` inside `lock_requirements.sh`/`lock_tools.sh` (human error messages), never in a CI `run:` step. Both `api-lock-verify` and `api-tooling-lock-verify` bootstrap uv FROM the hash-pinned lock using the runner's existing pip, then run `lock_*.sh --check` for byte-identity.
- No unpinned `pip install --upgrade pip` remains (grep-confirmed removed from all affected jobs); pip is pinned in the tooling lock. No `pipx run --spec` remains; no `.[dev]`/`pytest>=`/`httpx>=` range resolution remains in audited paths.

### 2. No advisory suppression — PASS
- Repo-wide grep for `ignore-vuln | --ignore | allowlist | nosec | continue-on-error | \|\| true | no-strict | skip.*audit` across `*.yml/*.yaml/*.sh/*.in/*.lock/*.toml/*.py`: **every hit in an audit context is a comment asserting NONE are used** (ci.yml:234, scheduled-audit.yml:16/69). All other `allowlist` hits are unrelated (CORS origins, connector field/value allowlists, secret-scan path allowlist).
- Dual pip-audit runs `-r <lock> --no-deps --strict` on BOTH locks, BLOCKING at every severity, in an isolated `$RUNNER_TEMP/auditenv` (ci.yml `exact-production-install` lines 239, 242; scheduled-audit.yml lines 71, 73). `--strict` also fails on any un-auditable pin. No print-only downgrade.
- **Independent CI-log confirmation on this SHA:** PRODUCTION lock -> `No known vulnerabilities found`; TOOLING lock -> `No known vulnerabilities found`. Every admitted version the task named (uv 0.11.28, pip 26.1.2, setuptools 83.0.0, wheel 0.46.2, pytest 9.0.3, httpx 0.28.1, ruff 0.13.0, pyyaml 6.0.3, pip-audit 2.10.1 + transitives) is advisory-free.

### 3. Age gate cannot be bypassed — PASS
`services/api/scripts/dependency_age_gate.py` reviewed in full:
- **No agent-usable exception/allowlist/skip flag.** The CLI has exactly one argument (`locks` positional). No env var, no `--skip/--force/--allow/--ignore`, no allowlist/suppression file read (module docstring explicitly states it "never reads an allowlist or suppression file").
- **Fails closed** (exit 1, package marked FAIL, never skip/pass) on: registry outage/network error, missing metadata, missing/malformed timestamp, an unhashed lock line, a hash-line-before-pin (malformed lock), and a lock sha256 that matches no official PyPI artifact. Verified by 10 of the 17 unit tests plus the `AgeGateError`-everywhere design.
- **Newest admitted-hash artifact timestamp:** `decide()` selects the newest `upload_time_iso_8601` among ONLY artifacts whose sha256 is admitted by the lock — defends the "old version number, freshly re-uploaded artifact" bypass (tests `test_multi_artifact_uses_newest_admitted_timestamp`, `test_newer_artifact_not_in_lock_is_ignored`).
- **Boundary:** `age >= MIN_AGE_SECONDS` where `MIN_AGE_SECONDS = 604_800`; full-instant seconds arithmetic. Exactly 604800 PASSES, 604799 FAILS — both proven by deterministic offline tests (`test_exactly_seven_days_passes`, `test_one_second_under_seven_days_fails`).
- `now` is taken from PyPI's own `Date` response header (not the local clock, `test_utc_now_reads_server_date_header`; fails closed if absent, `test_utc_now_missing_date_header_fails_closed`).
- **Independent CI-log confirmation on this SHA:** live run `now=2026-07-20T18:59:02+00:00`, 27 production + 42 tooling artifacts, **RESULT: PASS — every admitted artifact is >= 7 days old**. Tight-but-passing entries (anyio 7.94d, websockets 10.52d, uvicorn 12.33d) prove it measures real ages. The deliberately down-pinned `filelock 3.29.7` (newest 3.31.1 was 0.63d) and `platformdirs 4.10.0` (newest 4.10.1 was 2.60d) confirm the gate genuinely rejects too-new resolver picks. Age-gate unit tests: `17 passed`.

### 4. SSRF / injection / egress — PASS (with one non-blocking defense-in-depth note)
- Fetch targets the **fixed official host** `https://pypi.org` (hardcoded `PYPI_JSON_URL`, `PYPI_TIME_URL`). No attacker-controlled URL, no Location/redirect URL is ever consumed (only JSON body + `Date` header). HTTP timeout set (`_HTTP_TIMEOUT = 30`). JSON parsed with `json.load` (no eval).
- **No command injection / unsafe subprocess:** the age gate is pure `urllib` + stdlib — grep-confirmed NO `subprocess/os.system/os.popen/eval/exec/shell=True`. `lock_tools.sh` and `lock_requirements.sh` use `set -euo pipefail`, an array-form `COMPILE=(...)` command (no word-split injection), `mktemp` for temp files, pin+assert the uv version before use, and read only the local `.in` manifest — NO `curl/wget/eval`, no untrusted interpolation.
- **Non-blocking observation (defense-in-depth):** `name`/`version` are interpolated into the fixed URL via `.format()`. These values come exclusively from the committed lock files, whose byte-identity is enforced by `api-lock-verify` + `api-tooling-lock-verify` *before* this gate runs (a hand-poisoned lock fails those jobs first). The name regex `[A-Za-z0-9._-]+` is PEP 503-safe and the version regex `[^\s;\\]+` stops at whitespace/`;`/backslash; the hardcoded scheme+host cannot be crossed by a path segment. `urllib.parse.quote()` on the version segment would harden further, but the realistic threat is fully mitigated. **Not a defect.**

### 5. Secrets & logging — PASS
- No tokens/secrets committed or logged in any changed file. The only "secret"-adjacent grep hits are the fixed `pypi.org` URLs and a comment ("No secrets are referenced anywhere in this workflow").
- No fake token was introduced, so **no `# secretscan:allow` marker is required** (the age-gate tests use synthetic sha256 digests like `"a"*64`, which are hashes, not credentials). Secret-scan CI ("Scan repository for credentials") is **green** on this SHA.
- The age-gate output contains only package name, version, upload timestamp, elapsed age, PASS/FAIL — no sensitive data.

### 6. Least privilege / blast radius — PASS
- The only new external egress is **read-only PyPI metadata fetches** (age gate) — no new privileged calls. Both workflows declare `permissions: contents: read`.
- Production runtime lock unchanged (byte-identical) -> **no runtime dependency surface change**. No `services/api/app/**` behavior change (forbidden path untouched). The bounded pyproject amendment is exactly the single `[dev]` pytest specifier `pytest>=8,<9` -> `pytest>=9.0.3,<10` (+ adjacent comment); `httpx>=0.27,<1` and `ruff>=0.6,<1` ranges are unchanged (contract-permitted — CI installs exact from the lock). Full suite **538 passed** under pytest 9.0.3 in both the `api` job and `exact-production-install` (no weakened/skipped tests). `.gitignore` adds `services/api/**/*.egg-info/` (bounded hygiene).

### 7. Prompt injection — N/A
This change introduces no AI/LLM invocation and no source/document ingestion. There is no untrusted-content-to-tool-instruction surface. **Not applicable**, as stated.

---

## CI evidence (independently retrieved on head SHA 9da5449)
All **12 distinct checks PASS**, zero non-pass:
`web`, `web-e2e`, `api (ruff + pytest)`, `api-lock-verify`, `api-tooling-lock-verify`, `contracts`, `contracts-schema-bundle`, `contracts-typegen`, `control-plane`, `exact-production-install (dual pip-audit + validate_profile + age-gate)`, `pip-audit (scheduled, production tree)`, `Scan repository for credentials`. Log excerpts independently confirm: dual audit `No known vulnerabilities found`, age gate `RESULT: PASS`, age-gate unit tests `17 passed`, full suite `538 passed`.

---

## Findings summary

**Blocking findings: NONE.**

**Non-blocking observations (defense-in-depth / informational only — no action required for this gate):**
1. `dependency_age_gate.py` could `urllib.parse.quote()` the `version` path segment for belt-and-suspenders hardening. Current risk is fully mitigated by lock byte-identity enforcement + fixed scheme/host; not a defect.
2. Two M0-T018-era residuals I previously flagged are now **fixed** in this PR: the stale `pip-compile` reference in `requirements.in` (now names `lock_requirements.sh` + the exact pinned uv command) and the missing `services/api/**/*.egg-info/` gitignore rule.

---

## VERDICT: **PASS**

The change is a well-constructed supply-chain hardening: fully hash-pinned tooling lock installed via `--require-hashes` on every audited Python path (no unlocked uv, no unpinned pip, no ranged/`pipx` tool resolution), a fail-closed machine release-age gate with no agent-usable bypass and correct 604800/604799 boundary + newest-admitted-artifact semantics, dual blocking pip-audit reporting zero on both locks, a fixed-host injection-safe PyPI fetch with no subprocess/eval, no secrets or sensitive log output, least-privilege `contents: read` workflows, an unchanged production runtime lock, and untouched forbidden paths. All acceptance-relevant security invariants are independently verified in both source and CI logs on the exact head SHA.

Recommend the orchestrator record **G5 = PASS** for M0-T020 at SHA `9da5449e02962c4ac75bf337e8fadefe827e75ab`.
