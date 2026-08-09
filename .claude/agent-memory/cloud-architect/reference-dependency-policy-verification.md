---
name: reference-dependency-policy-verification
description: Reusable technique for verifying the owner's dependency-admission rule (>=7d age on admitted artifacts, advisory-free, hash-pinned) against live PyPI + OSV, and the pytest<9 advisory trap
metadata:
  type: reference
---

Technique for M0-T018/M0-T019/M0-T020-class dependency-policy work (age >=7 days, advisory-free, exact hash-pinned, no waiver):

1. **Resolve first, age-check after.** Pin direct tools in a `*.in`, then `uv pip compile --universal --python-version 3.12 --generate-hashes --no-header` (the repo's `lock_requirements.sh` method) to get the FULL transitive closure. You cannot age-check transitives until you resolve them.
2. **Age = newest admitted artifact.** For each `name==version`, collect the lock's admitted SHA-256 set, GET `https://pypi.org/pypi/<name>/json`, match those hashes to `releases[version]` files, take the NEWEST `upload_time_iso_8601` among matched files, require `(now_utc - newest) >= 604800 s`. Compare full UTC instants in seconds. FAIL CLOSED if no admitted hash matches PyPI (prevents an old version number with a freshly re-uploaded artifact bypassing the wait).
3. **Down-pin too-new transitives** the same way M0-T018 pinned websockets/numpy: add an explicit age-clean predecessor to the `*.in` and re-resolve (e.g. 2026-07-20: filelock 3.31.1→3.29.7, platformdirs 4.10.1→4.10.0).
4. **Advisories via live pip-audit AND OSV.** `pip-audit -r <lock> --no-deps --strict` (blocking) for the finding; then OSV `POST https://api.osv.dev/v1/query {"package":{"name","ecosystem":"PyPI"},"version"}` to get exact `introduced`/`fixed` ranges so you know the minimum clean version.
5. **The pytest<9 trap (as of 2026-07-20):** pytest CVE-2025-71176 / PYSEC-2026-1845 (`introduced=0, fixed=9.0.3`) affects EVERY pytest 8.x. `services/api/pyproject.toml [dev]` caps `pytest>=8,<9`, so no admissible pytest is advisory-free — reaching zero findings needs pytest 9.0.3, i.e. a pyproject amendment (a forbidden path in M0-T020) → this is a legitimate owner-decision STOP, not something an agent may waive. Same-day fixed-and-age-clean bumps that ARE in scope: pip 25.2→26.1.2, setuptools 80.9.0→83.0.0 (satisfies build `>=69`), wheel 0.45.1→0.46.2 (0.46.0/0.46.1 are yanked).
6. **Prove the residual blocker is isolated:** build a hypothetical fully-fixed manifest and re-audit → "No known vulnerabilities found" pinpoints exactly which pin is the sole blocker for the owner.

Local Windows PC ran uv, pip, venv, live PyPI and OSV without denial (2026-07-20); keep it bounded in one `mktemp -d` venv and delete after. Related: [[tooling-lock-byte-identity-crlf]].
