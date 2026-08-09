---
name: python-supply-chain-audit-review
description: G5 review method for Python dependency-lock hardening (M0-T018) — pip-audit blocking, release-age, hash-pinning, scheduled audit
metadata:
  type: project
---

M0-T018 established the backend Python supply-chain enforcement baseline for services/api. Review method for any future dependency-lock/audit change:

**Independent pip-audit replay:** bounded temp venv in `$TEMP` (Git-Bash `df -k c:/Users/MLFLL` first; keep >=4GB free), `pip install pip-audit==<pinned>`, then the EXACT CI command `python -m pip_audit -r services/api/requirements.txt --no-deps --strict`. Expect `No known vulnerabilities found` / exit 0. Prove prior findings existed by auditing the OLD pin (e.g. `starlette==0.46.2` -> 9 findings incl PYSEC-2026-249 fixed in 1.3.1, exit 1). Delete venv; re-check disk.

**Release-age spot-check:** PyPI JSON `https://pypi.org/pypi/<pkg>/<ver>/json`, field `urls[0].upload_time_iso_8601`. Verify pinned versions are >=7d AND that the REJECTED too-new siblings really are <7d (fastapi 0.139.1 = 2026-07-16/4d rejected; websockets 16.1.1 = 2026-07-17/3d rejected; pins fastapi 0.139.0, websockets 16.1, numpy 2.4.6, uvicorn 0.51.0, starlette 1.3.1, jsonschema 4.26.0 all confirmed >=7d as of 2026-07-20).

**No-suppression grep:** `ignore-vuln|allowlist|--ignore|continue-on-error|\|\| true|no-strict` across yml/yaml/sh/in/txt/py. In M0-T018 the ONLY hits in pip-audit context were comments asserting NONE are used; the `allowlist` term is otherwise heavily used for CORS/connector field allowlists (unrelated).

**Blocking + hash + scheduled invariants:** CI `exact-production-install` uses `pip install --require-hashes` (explicit) though Render's `buildCommand` is bare `pip install -r requirements.txt` (render.yaml) — pip auto-enters hash-checking mode because every lock line carries `--hash`, so Render is hash-verified in practice. Lock is `uv pip compile --universal --python-version 3.12 --generate-hashes --no-header` (scripts/lock_requirements.sh, uv pinned 0.11.29), byte-identity enforced by `api-lock-verify`. scheduled-audit.yml runs the same `--strict` command on daily cron + dependency-artifact PRs + workflow_dispatch, blocking (red run = signal).

**Known low/observation residuals (non-blocking):** requirements.in header comment line 9 still says `pip-compile --generate-hashes` while the real generator is `uv pip compile` (stale doc only, not a security defect). `*.egg-info/` under services/api not gitignored (producer flagged follow-up). Related: [[supply-chain-action-pinning-review]], [[g5-gate-recording-protocol]].
