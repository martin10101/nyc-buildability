# Dependency admission — pip 26.2 (G5 specialist review, verbatim reviewer return)

Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
(report-preservation rule; transport entity-decoding only). Tier B dependency change,
dedicated commit; not part of task M0-T092. Recorded by: orchestrator, 2026-08-27.

---

# G5 Dependency-Security Gate Report

**Gate:** G5 (dependency provenance / supply-chain admission) — Tier B specialist review
**Scope:** Single-package version bump `pip==26.1.2 -> pip==26.2` (advisory-fix admission of an already-admitted package)
**Repo / branch:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` @ `control/D-024-fable-codex-loop`
**Files under review (uncommitted working tree):**
- `services/api/requirements-tools.in`
- `services/api/requirements-tools.lock`

**Reviewer posture:** Read-only. All producer claims independently re-derived from live PyPI, live OSV, and the local age gate. No implementation modified.

## Invariants checked (docs/DEPENDENCY_SECURITY_POLICY.md; .claude/ORCHESTRATION_POLICY.md §G)

| Invariant | Result | Independent evidence |
|---|---|---|
| Exact pin | PASS | `.in` = `pip==26.2`; `.lock` = `pip==26.2` with two `--hash=sha256:` lines |
| Integrity match to official registry | PASS | Both lock hashes are a subset of the live PyPI digests for pip 26.2, with no extra registry hash unaccounted for (both artifacts pinned) |
| Age >= 604800 s vs official publish time | PASS | Live PyPI upload 2026-07-29T21:57:56Z; age gate reports `age=2511402s (29.07d)` |
| Advisory-free at every severity | PASS | OSV query for pip 26.2 returns `{}` (zero vulns) |
| Fail-closed machinery intact | PASS | `dependency_age_gate.py` parsed all 43 pins and returned `RESULT: PASS`, `EXIT=0` |
| No waiver used | PASS | Passes age gate on its own (29.07d); no waiver file added/modified (working tree = only the two files) |
| Diff scope minimal (nothing else introduced) | PASS | `git status --porcelain` = only these 2 files; lock diff = exactly the pip entry |
| Comment-block claims accurate | PASS | All five factual claims re-derived below |

## Verification detail (reproducible)

### 1. PyPI publish time + hash integrity — `https://pypi.org/pypi/pip/26.2/json`
```
info.version: 26.2 | info.yanked: False
bdist_wheel pip-26.2-py3-none-any.whl  upload=2026-07-29T21:57:54.763549Z  yanked=False
   sha256=931c303696af6fa3417112103b1cad26890e5a07eccb5b99783700e33f2b8aad
sdist       pip-26.2.tar.gz            upload=2026-07-29T21:57:56.407153Z  yanked=False
   sha256=2d8542afcc84cdd8e846c2b36b2861fad1da376dd98f8e7113e9108a3c331690
lock hashes subset of registry: True
registry-only hashes (extra): []      # both distributed artifacts are pinned, no dangling artifact
```
Both lock hashes match the registry byte-for-byte; neither artifact is yanked. The whl hash `931c3036…` and sdist hash `2d8542af…` correspond exactly to the `.in` comment's whl/sdist attribution.

### 2. Age gate — `python services/api/scripts/dependency_age_gate.py services/api/requirements-tools.lock`
```
PASS  pip==26.2  uploaded=2026-07-29T21:57:56.407153+00:00  age=2511402s (29.07d)
RESULT: PASS - every admitted artifact is >= 7 days old      EXIT=0
```
29.07 d = 2,511,402 s >= 604,800 s. Passes on its own; no waiver needed.

### 3. Advisory status — OSV (`api.osv.dev`)
```
POST /v1/query {pip, PyPI, 26.2}  -> {}                       # zero advisories for 26.2
GET  /v1/vulns/PYSEC-2026-3721:
   id: PYSEC-2026-3721 | aliases: ['CVE-2026-13346']
   details: pip would incorrectly handle doubly-encoded package URLs from indexes
            allowing files to be installed to arbitrary locations on disk...
   affected pip PyPI ranges: introduced 0, fixed 26.2
   26.1.2 affected: True | 26.2 affected: False
POST /v1/query {pip, PyPI, 26.1.2} -> 1 vuln: PYSEC-2026-3721 (CVE-2026-13346)
```
Confirms the advisory that turned the CI pip-audit gate red genuinely affects 26.1.2 and is fixed exactly in 26.2. 26.2 is the oldest advisory-free fix version (OSV `fixed: 26.2`), matching the `.in` comment's rationale for not jumping to 26.2.1.

### 4. Diff scope — `git status --porcelain` / lock diff
```
 M services/api/requirements-tools.in
 M services/api/requirements-tools.lock          # only these two files
lock diff (content):
 -pip==26.1.2 + 2 old hashes  ->  +pip==26.2 + 2 new hashes   # nothing else
```
No other pin moved, no transitive added/removed, no stray hash left behind. pip is a dependency-graph leaf (no runtime deps), so a version bump correctly produces zero transitive churn — consistent with the exact-one-entry lock diff. The `# via -r requirements-tools.in / pip-api` annotation is correctly preserved.

### 5. Comment-block accuracy (`.in` lines 46–56)
- "PYSEC-2026-3721 was published against 26.1.2" — CONFIRMED (26.1.2 affected).
- "26.2 is the fix version" — CONFIRMED (OSV fixed: 26.2).
- "published 2026-07-29T21:57:54Z per live PyPI" — CONFIRMED (whl upload 21:57:54Z; sdist 21:57:56Z).
- "OSV query for pip 26.2 returns zero advisories" — CONFIRMED (`{}`).
- "sha256 whl 931c3036… / sdist 2d8542af… verified against the registry" — CONFIRMED.

## Findings

No Critical, High, or Medium findings. This is a clean, textbook advisory-fix bump of an already-admitted leaf package.

**LOW / informational (no remediation required; verification-completeness notes for the orchestrator):**

- **INFO-1 — pip-audit not re-executed in reviewer sandbox.** The actual blocking gate (dual pip-audit) needs the project venv, which is not available read-only. I substituted a direct OSV query (the same vulnerability corpus pip-audit consults), which confirms pip 26.2 is clean and 26.1.2 was flagged. Recommend the orchestrator confirm the CI pip-audit context turns green on the bumped lock. Not a defect. (Orchestrator note: local `pip-audit -r requirements-tools.lock --no-deps --strict` from the hash-verified tooling venv reported "No known vulnerabilities found", exit 0, before this review; CI confirmation attached at the merge-forward.)
- **INFO-2 — `lock_tools.sh --check` byte-identity not re-run.** Re-generation needs pinned uv 0.11.28 + network. Corroborated indirectly: the lock parses cleanly (all 43 pins consumed by the age gate) and the diff is exactly the pip entry with no formatting drift. The CI `--check` job remains the byte-identity guarantor. Not a defect. (Orchestrator note: local `scripts/lock_tools.sh --check` with the lock-pinned uv 0.11.28 reported byte-identical PASS before this review.)
- **INFO-3 — age comment says "29.06d at admission" vs live gate "29.07d".** ~20-minute clock drift between the producer's computation and my run; both are far above the 7-day floor. The comment's `2026-07-29T21:57:54Z` is the wheel upload time while the age gate measures from the sdist (`…:56Z`); the difference is sub-second-scale and immaterial. Not a defect.

## Conclusion

The change satisfies every §G / DEPENDENCY_SECURITY_POLICY invariant: exact pin, registry-exact integrity for both artifacts, 29.07 d age (well over the 604800 s floor, no waiver invoked), zero advisories at every severity on the admitted version, minimal single-entry diff with no collateral pin/transitive/hash movement, and an accurate admission-evidence comment. The advisory motivating the bump (PYSEC-2026-3721 / CVE-2026-13346) is real, affects the outgoing 26.1.2, and is fixed in the incoming 26.2. The security review dimensions (cross-tenant isolation, service-role secrecy, private storage, SSRF/injection, upload controls, prompt-injection, least privilege, log redaction) are not applicable to a build/tooling lock bump and carry no exposure here.

**VERDICT: PASS**
