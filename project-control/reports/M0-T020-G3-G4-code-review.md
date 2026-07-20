<!-- Verbatim independent-reviewer return preserved by the orchestrator per the report-preservation rule (ADR-005; transport decoding only). Reviewer: code-reviewer. Gates: G3 + G4. Task: M0-T020. Bound to task PR #60 head SHA 9da5449e02962c4ac75bf337e8fadefe827e75ab. Verdict: PASS (zero blocking). -->

# GATE REPORT — M0-T020 (G3 + G4)

**Task ID:** M0-T020 — Python dependency-policy enforcement follow-up
**Reviewed:** PR #60, branch `task/M0-T020-python-dependency-policy`, **head SHA `9da5449e02962c4ac75bf337e8fadefe827e75ab`**
**Reviewer:** code-reviewer (independent; NOT the producer, who was cloud-architect)
**Gates:** G3 (independent human-style walkthrough) + G4 (integration/regression)
**Review location:** clean worktree `.claude/worktrees/agent-ab14f31e8c53fac99` (verified `git rev-parse HEAD` = target SHA; `git status --porcelain` clean before and after review)
**Method:** started from the acceptance contract (`project-control/tasks/M0-T020.json`, TP-S1..TP-S14 + `age_gate_contract` + allowed/forbidden paths), inspected code, ran grep-provable checks, executed the age-gate logic locally (17 committed unit tests + an independent driver), locally corroborated pytest collection count, and verified live CI evidence bound to the exact SHA.

## CI evidence (bound to SHA 9da5449)
- `gh run view 29770040965` -> `event: push`, `sha: 9da5449...`, `conclusion: success`; `gh run view 29770069581` -> `event: pull_request`, `sha: 9da5449...`, `conclusion: success`.
- `gh pr checks 60`: **all 20 checks PASS** (each M0-T020-relevant job appears twice — push + PR triggers). Key jobs: `api` (35s), `api-lock-verify` (15s), `api-tooling-lock-verify` (14s, NEW), `exact-production-install` (53-55s), `pip-audit (production tree)` (scheduled-audit PR trigger, 31s), `contracts`, `contracts-typegen`, `web`, `web-e2e` (2m12s), `control-plane`, `secret-scan`.

## Per-scenario verdicts

**TP-S1 — requirements.in header fix: PASS.** `services/api/requirements.in:8-17` names `services/api/scripts/lock_requirements.sh` and the exact pinned command `uv pip compile --universal --python-version 3.12 --generate-hashes --no-header requirements.in --output-file requirements.txt` (uv 0.11.28). `grep -c "pip-compile" services/api/requirements.in` -> **0**. The incidental "pip-compile alone would pick" phrase was reworded to "the resolver alone would pick" (line 24).

**TP-S2 — uv downgrade + production-lock immutability: PASS.** `lock_requirements.sh:43` `UV_VERSION="0.11.28"`; ci.yml `api-lock-verify` installs uv from the tooling lock (`ci.yml:157`, `pip install --require-hashes -r requirements-tools.lock`), no bare `uv==` download. `services/api/requirements.txt` is **NOT in the diff** (`git diff --name-only main...HEAD -- services/api/requirements.txt` -> empty). Live CI `api-lock-verify` job: `OK: requirements.txt is byte-identical to a fresh uv 0.11.28 lock`. Producer report §1a records uv 0.11.28 published 2026-07-07T23:12:47Z (12.80d), advisory-free, from pypi.org->astral-sh; CI age gate independently confirms uv 0.11.28 age=12.82d PASS. uv 0.11.29 correctly rejected (4.98d < 7d).

**TP-S3 — tooling lock + source manifest: PASS.** `requirements-tools.in` = 11 direct pins (single authoritative source). `requirements-tools.lock` = 42 pinned packages; I independently verified **every one of the 42 pins carries >=1 sha256 hash (zero unhashed pins)**, 389 hash lines total, 35229 bytes. One documented generator `scripts/lock_tools.sh` (mirrors `lock_requirements.sh`; UV_VERSION=0.11.28; `--check` mode). Live CI `api-tooling-lock-verify`: `OK: requirements-tools.lock is byte-identical to a fresh uv 0.11.28 lock`. CI bootstraps via `pip install --require-hashes -r requirements-tools.lock` using the runner's stock pip (ci.yml:157,183; no unlocked uv first — the lock hash-pins uv itself, uv 0.11.28 has 19 hashed artifacts). No pin list duplicated across scripts (each script reads exactly one manifest).

**TP-S4 — pip pinned/removed: PASS.** Comprehensive scan of both workflows: **no `pip install --upgrade pip` in any actual run command**. The three residual `--upgrade pip` mentions (ci.yml:117,210 and requirements-tools.in) are all comment lines documenting the removal. pip is pinned in the tooling lock (`pip==26.1.2`, age 50.06d, CI-confirmed PASS).

**TP-S5 — CI installs from the locks only: PASS.** Every actual `pip install` run-command across ci.yml + scheduled-audit.yml is one of: `--require-hashes -r requirements.txt`, `--require-hashes -r requirements-tools.lock`, or `--no-deps .`. Grep for `.[dev]`, `pytest>=`, `httpx>=` in workflows -> matches are **comment-only** (ci.yml:117,263,314). No dynamically-resolved setuptools. The `api` job replaced `.[dev]` with tooling-lock + production-lock + `--no-deps .` (ci.yml:122-127).

**TP-S6 — pipx + scheduled-audit replaced: PASS.** Only `pipx` occurrence is a comment (ci.yml:223). `exact-production-install` builds an isolated venv and installs pip-audit from the tooling lock (ci.yml:227-230). `scheduled-audit.yml:66` installs pip-audit via `--require-hashes -r requirements-tools.lock` (no pip-resolved transitives). Live CI log shows the isolated audit venv collecting pip-audit's full transitive tree from the hash-pinned lock (filelock==3.29.7, cyclonedx, msgpack, etc.).

**TP-S7 — dual audit zero: PASS.** `exact-production-install` runs `pip-audit -r requirements.txt --no-deps --strict` AND `pip-audit -r requirements-tools.lock --no-deps --strict` (ci.yml:239,242); scheduled-audit runs both (lines 71,73). Live CI log: **"No known vulnerabilities found" appears 2x** (both locks, zero at every severity). No `--ignore-vuln`/allowlist/waiver anywhere (grep confirmed only docstring negations).

**TP-S8 — machine age-gate (positive + artifact semantics): PASS.** `scripts/dependency_age_gate.py` uses live UTC from PyPI `Date` header (`utc_now`), live PyPI JSON per version, newest **lock-admitted-sha256** artifact timestamp (`decide`), full-second `>=604800` compare, covers both locks direct+transitive, prints name/version/timestamp/age/PASS-FAIL (`format_result`). Live CI (`exact-production-install`) ran it: `now=2026-07-20T18:59:02+00:00, min_age=604800s`, evaluated **27 production + 42 tooling packages**, all PASS, `RESULT: PASS — every admitted artifact is >= 7 days old`. Tightest observed: `anyio==4.14.2 age=7.94d` PASS. No date-only/truncated-day math (verified in source; my driver confirmed `age_s=604799.0` and `604800.0`).

**TP-S9 — machine age-gate (negative + fail-closed): PASS.** `test_dependency_age_gate.py` — I ran it locally offline: **17 passed**; CI `api-tooling-lock-verify` also **17 passed**. Proves 604800->PASS, 604799->FAIL, and every fail-closed branch FAILS (not skip/pass): unmatched hash, unhashed pin, malformed timestamp, missing timestamp, registry outage (via `evaluate_lock`), missing `urls`, missing `Date` header, hash-before-pin corruption. My independent driver reproduced: boundary, unmatched-hash->FAIL, malformed->AgeGateError, outage->FAIL result, and the "new artifact not in lock ignored"->PASS bypass defense.

**TP-S10 — no agent waiver: PASS.** The gate has no allowlist/exception/ignore input; grep for suppression tokens returns only the docstring lines stating "There is NO agent-created exception path... this module never reads an allowlist or suppression file." pip-audit remains the separate blocking advisory gate with no waiver.

**TP-S11 — egg-info hygiene: PASS.** `.gitignore:16` `services/api/**/*.egg-info/` (with explanatory comment at :13). Producer removed the stray egg-info; worktree has none.

**TP-S12 — regression + immutability: PASS.** `requirements.txt` unchanged (not in diff; CI `api-lock-verify` byte-identical with uv 0.11.28). No `project-control/tasks/M0-T018.json` or `M0-T018-*` report changes (`git diff --name-only` empty). No `services/api/app/**` changes (empty). Ruff (from tooling lock): CI `api` job "All checks passed". Full suite: CI `api` job + `exact-production-install` both **538 passed** on Python 3.12.13. `exact-production-install` + `api-lock-verify` green.

**TP-S13 — full Python-CI-download reconciliation: PASS.** Producer report §8 tabulates every Python download path. My comprehensive independent grep of both workflows enumerated **every** `pip install`/`pip-audit` command — all map to the production lock, the tooling lock, `--no-deps .`, or a `--no-deps --strict` audit. No unlisted Python download remains; no STOP-condition exception was required. `contracts`->pyyaml, `contracts-typegen`->pytest, `web-e2e`->production lock, `api-lock-verify`->uv all install from a lock (CI-confirmed).

**TP-S14 — bounded pyproject pytest amendment: PASS.** `git diff main...HEAD -- services/api/pyproject.toml` shows **only** `"pytest>=8,<9"` -> `"pytest>=9.0.3,<10"` plus a 4-line adjacent comment; no other dependency/cap/`[tool.*]`/`[tool.pytest.ini_options]` change (`testpaths=["tests"]` unchanged). `requirements-tools.in:71` pins `pytest==9.0.3`; lock resolves pytest==9.0.3 with 2 hashes. Full suite passes under pytest 9.0.3 (CI: pytest-9.0.3 installed, 538 passed). Collection parity independently corroborated: my local **pytest 8.4.2 collect-only -> 538 tests collected**, matching the CI pytest-9 run of 538 passed and the report's byte-identical node-ID claim. No test weakened/deleted/skipped/xfailed. pytest 9.0.3 and the whole tooling tree report ZERO advisories (dual audit + age gate green).

## Required case classes (G3)
- **Normal:** live age gate over both real locks -> all 69 packages PASS; full suite 538 passed. My driver: 30-day-old artifact -> PASS.
- **Boundary:** exactly 604800s -> PASS; 604799s -> FAIL (committed test + my driver; `age_s` shows exact-second arithmetic, no day-truncation). Tightest live package anyio 7.94d PASS.
- **Missing/ambiguous:** unmatched lock hash -> FAIL closed; unhashed pin -> FAIL closed; a too-new artifact not admitted by the lock -> correctly ignored (bypass defense).
- **Failure:** malformed/missing timestamp -> AgeGateError; registry outage -> FAIL result via `evaluate_lock` (not skipped); missing Date header -> fail closed; negative jsonschema smoke -> `validate_profile` raised ModuleNotFoundError (M0-T018 regression proof intact).

## Regressions / collateral
None found. Diff = exactly 12 files, all within `allowed_paths`. Forbidden paths all clean: `services/api/app/**`, `project-control/tasks/M0-T018.json` + `M0-T018-*`, `.github/workflows/generate-lockfile.yml`, `.github/workflows/secret-scan.yml`, `apps/web/**` — none modified. `requirements.txt` byte-identical. `merge-base(main,HEAD) == main tip` (branch current, mergeable). Age gate is timezone-aware (`datetime.UTC`, no deprecated `utcnow`).

## Low-storage / thin-client (G4)
Compliant. All heavy execution is GitHub Actions (Python 3.12.13, ubuntu-24.04). Producer local runs were bounded temp venvs, cleaned. My review created only tiny temp files (all removed) and transient `__pycache__` (gitignored; I removed them). Worktree left pristine. C: has 23 GB free (>4 GB floor). No large/persistent local artifacts written.

## Findings
- **Blocking:** none.
- **Non-blocking (informational, no action required for this gate):**
  1. Producer report §14.4 — the full tooling lock is installed where a single tool (pyyaml / pytest / uv) would suffice. This is a deliberate, documented design choice: `pip --require-hashes` rejects the `-r <lock> <singlepkg>` form, and a third hash-pinned subset would duplicate an authoritative pin list (forbidden). The extra packages are inert for those stdlib-only steps, hash-verified, age-gated, and advisory-clean. Correct, not an oversight.
  2. Producer report §14.7 — the `api` job's pip cache key still points at `pyproject.toml`; installs are hash-verified from the locks regardless, so this is correctness-neutral. Candidate for a future tidy-up; not required by this packet.
  3. Local producer verification ran on Python 3.11 (owner PC), but the authoritative full-suite + full-CI proof is GitHub Actions on Python 3.12 — which I verified green on the exact SHA. The `datetime.UTC` usage requires >=3.11, satisfied on the 3.12 target.

## VERDICT: **PASS**

All 14 acceptance scenarios (TP-S1..TP-S14) and the full `age_gate_contract` are satisfied with reproducible evidence. The production runtime lock is provably immutable (byte-identical, not in the diff); the tooling lock is a complete, hash-pinned, byte-identically-regenerable 42-package closure with a single documented generator; every audited Python CI path installs only from the two locks; dual pip-audit is zero and blocking; the machine age gate enforces >=604800 full seconds over both locks' direct+transitive packages with live PyPI/UTC and fails closed on every ambiguous condition with no agent waiver; and the bounded pytest 9.0.3 amendment is the only pyproject change, with the full 538-test suite passing under pytest 9 with no weakened tests. Live CI (20/20) is bound to head SHA 9da5449. No forbidden path was touched and no regression was introduced.

*(Read-only reviewer per ADR-005: I did not run `tools/project_control.py` or any write command. The orchestrator should save this report to `project-control/reports/` and record the G3+G4 gate result.)*
