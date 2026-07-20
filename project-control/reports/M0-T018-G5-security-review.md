<!-- Preserved VERBATIM by the orchestrator from the security-reviewer G5 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

# G5 Security & Supply-Chain Gate Report — M0-T018

**Task:** Backend production dependency parity and Python supply-chain enforcement
**Reviewed commit:** 7ffd542 (Merge PR #55) — confirmed == HEAD of main, working tree is the merged state
**Reviewer:** security-reviewer (independent; != producer cloud-architect)
**Mode:** READ-ONLY (ADR-005). All evidence reproduced independently.

## VERDICT: PASS

All six focus areas verified independently against the merged tree. No advisory suppression, no allowlist, audit is genuinely blocking, release-age gate holds, lock is fully hash-pinned, scheduled audit is present and blocking. Two non-blocking observations recorded.

---

## Evidence I ran (not producer's claims)

### 1. pip-audit — EXACT resolved production tree (DP-S6) — PASS
Bounded temp venv in `$TEMP` (30.1 GB free before/after; venv deleted; low-storage honored), `pip-audit==2.10.1` (the pinned CI version). Exact CI command:
```
python -m pip_audit -r services/api/requirements.txt --no-deps --strict
  -> No known vulnerabilities found
  -> EXIT CODE: 0
```
Old-pin proof (findings now cleared):
```
python -m pip_audit -r <starlette==0.46.2> --no-deps
  -> Found 9 known vulnerabilities in 1 package
    PYSEC-2026-161/248/249/1941/1942/2280/2281  (PYSEC-2026-249 Fix: 1.3.1 = the target)
  -> EXIT CODE: 1
```
CI enforcement (ci.yml:186-187): `pipx run --spec "pip-audit==2.10.1" pip-audit -r requirements.txt --no-deps --strict`. No `|| true`, no `continue-on-error`, no print-only, no `--ignore-vuln`. Non-zero exit fails the build. `--no-deps` is correct here because the lock is the full transitive closure (auditing the active env would trip `--strict` on the local non-PyPI app package).

### 2. Release-age >= 7 days (DP-S7) — PASS
PyPI JSON `upload_time_iso_8601`, verified as of 2026-07-20:

| Package | Published | Age | Status |
|---|---|---|---|
| fastapi 0.139.0 | 2026-07-01 | 19d | admitted |
| starlette 1.3.1 | 2026-06-12 | 38d | admitted |
| jsonschema 4.26.0 | 2026-01-07 | 194d | admitted |
| numpy 2.4.6 | 2026-05-18 | 63d | admitted |
| uvicorn 0.51.0 | 2026-07-08 | 12d | admitted |
| websockets 16.1 | 2026-07-10 | 10d | admitted |
| **fastapi 0.139.1** | 2026-07-16 | **4d** | correctly REJECTED |
| **websockets 16.1.1** | 2026-07-17 | **3d** | correctly REJECTED |

Producer did NOT silently substitute too-new versions: it kept fastapi 0.139.0 over 0.139.1, and deliberately pinned websockets 16.1 (open `>=10.4` upper bound would otherwise pull the 3-day-old 16.1.1) and numpy 2.4.6 (resolver-ambiguity + age). Reasoning holds. requirements.in documents both age-pins with rationale (lines 48-64).

### 3. No advisory suppression / allowlist — CONFIRMED NONE
Grep for `ignore-vuln|allowlist|--ignore|continue-on-error|\|\| true|no-strict` across yml/yaml/sh/in/txt/py. The only pip-audit-context hits are comments explicitly asserting NONE are used (ci.yml:183, scheduled-audit.yml:16). Every other `allowlist` hit is unrelated (CORS origin allowlist, connector field/value allowlists). CI is green because the tree is genuinely clean, not because findings are hidden.

### 4. Hash verification — PASS
Lock is fully hash-pinned: 27 pinned packages, 774 `--hash=sha256:` lines, every pin carries a continuation backslash (no bare/unhashed requirement line). CI `exact-production-install` uses explicit `pip install --require-hashes -r requirements.txt` (ci.yml:166, 198). Render's `buildCommand` is bare `pip install -r requirements.txt` (render.yaml:98) — pip auto-enters hash-checking mode when any line has a hash and all do, so Render is hash-verified in practice; render.yaml:92-95 documents this correctly. `referencing==0.37.0` (needed by contract.py) is present in the lock.

### 5. Scheduled audit (DP-S8) — PASS
`.github/workflows/scheduled-audit.yml`: daily cron `17 6 * * *`, `pull_request` on requirements.txt/requirements.in/pyproject.toml, and `workflow_dispatch`. Runs the identical blocking command `python -m pip_audit -r requirements.txt --no-deps --strict` (line 58). A finding turns the run red (visible/actionable); no suppression. `permissions: contents: read` (least privilege).

### 6. Secrets / provenance / lifecycle — PASS
No secrets in lock/scripts/workflows. requirements.in contains only clean pinned specifiers — no `-e`, `git+`, URLs, or `file://` (no lifecycle-script injection surface). Negative-smoke proof (ci.yml:193-196) genuinely exercises the lazy `import jsonschema` at contract.py:231 inside validate_profile (confirmed the import is function-local at that exact line), so the gate catches the real production defect that /health would miss. `render.yaml` secrets all `sync: false`; service-role key backend-only.

---

## Findings

**No BLOCKING findings.**

- **OBSERVATION-1 (LOW, doc-only):** `services/api/requirements.in:9,19` header comment still references `pip-compile --generate-hashes` while the actual generator is `uv pip compile --universal` (scripts/lock_requirements.sh). Stale documentation, not a security defect; the CI byte-identity check (`api-lock-verify`) enforces the real `uv` output regardless. Recommend a one-line comment fix in a future dependency-touch commit.
- **OBSERVATION-2 (LOW):** `services/api/**/*.egg-info/` not gitignored (producer self-disclosed §7). Outside this task's allowed_paths; recommend follow-up. No security impact.

---

## Gate recording note (ADR-005)
I am read-only and did NOT run project_control.py, git write, or gh. Orchestrator should record **G5 = PASS** for M0-T018. The two LOW observations are non-blocking and may be tracked as follow-ups; they do not gate acceptance.

Relevant files: `services/api/requirements.txt`, `services/api/requirements.in`, `services/api/scripts/lock_requirements.sh`, `services/api/scripts/exact_install_smoke.py`, `.github/workflows/ci.yml`, `.github/workflows/scheduled-audit.yml`, `render.yaml`.
