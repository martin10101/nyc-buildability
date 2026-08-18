# NANOID_REPAIR_PR_READY — M0-T071 return report (D-015-R028 committed copy)

Returned by the orchestrator on 2026-08-18 after implementation, independent gates, and a fully
green CI run. **Nothing is merged** (D-015 prohibition 6); A1 was not restarted.

1. **Reconciled task ID:** `M0-T071` (M0-T063..M0-T070 allocated across the control/repair
   branches; M0-T071 verified unused repo-wide before contracting).

2. **Branch / worktree:** `task/M0-T071-nanoid-ghsa-2v37` in
   `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t071` — created directly from current origin/main,
   deliberately unstacked from `control/context-intelligence-init` and the M0-T070 branch.

3. **Exact origin/main base SHA:** `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1`.

4. **Exact before/after lockfile entries** (`apps/web/package-lock.json`, `node_modules/nanoid`):
   - BEFORE: `"version": "3.3.17", "resolved": ".../nanoid-3.3.17.tgz",
     "integrity": "sha512-xQLf0A3HOMlgHq0n247/LRuAOYmB7dXJ/DvAxGvsSBij45XtBSmQycu+F8ODbHwns/XyFZagyL1+J0Offw1E0g=="`
   - AFTER: `"version": "3.3.18", "resolved": ".../nanoid-3.3.18.tgz",
     "integrity": "sha512-DTg4MJbGMWkfi6VZFdNt2/caMbQy4Ou+Op/hJQvGEWcnVfoA1QA+xzRKAzw9jD6+GVOOeYr/mIcuDSdug6F6+w=="`
   - Plus the required exact-pin lockstep line: `apps/web/package.json` `overrides.nanoid`
     `"3.3.17"` → `"3.3.18"` (npm ci fails closed without it — proof in the evidence record;
     no direct dependency added).

5. **Official release timestamp / calculated age:** registry `time["3.3.18"]` =
   `2026-08-07T16:41:05.696Z`; authoritative repo age gate measured **917,698 s** at the producer
   run (G4 reviewer independently measured 918,353 s; G5 918,482 s) — all **> 604,800 s**.

6. **Advisory results:** `npm audit --audit-level=low` (dev deps included) → **0
   vulnerabilities**; audit JSON `{info:0, low:0, moderate:0, high:0, critical:0, total:0}`;
   3.3.18 outside every vulnerable range of all four nanoid GHSA advisories
   (2v37-7h3g-55p8, 28wg-ghj8-5hjv, mwcw-c2x4-8c55, qrpm-p2h7-hrv2); npm CLI advisory
   verification for the CI pin 11.18.0 → PASS. G5 additionally verified the tarball's SRI hash
   byte-for-byte against the registry and the downloaded artifact, plus SLSA provenance.

7. **Every file changed** (implementation commit `e7c7d377`): `apps/web/package-lock.json`
   (3 lines), `apps/web/package.json` (1 line), plus control-plane only:
   `project-control/directives/D-015-nanoid-security-repair/` (source-001.md, requirements.json
   28 rows, manifest.json, verification.json), `directives/index.json`, `state.json`,
   `tasks/M0-T071.json`, `gates/M0-T071-G0.json`, reports (G0 review, dependency evidence,
   producer report). The post-gate control-plane commit adds the G2/G4/G5 gate records, the
   two reviewer reports, the evidence map, the submit record, and this return report.

8. **Tests and gates:**
   - Policy suite: deterministic `npm ci` (560 pkgs, integrity-verified); audit 0 at every
     severity; committed-lock age gate PASS; npm CLI advisory PASS; depage unit tests 40/40.
   - Web battery: eslint clean; tsc clean; vitest 287 passed; next build success; Playwright
     E2E green in CI (`web-e2e` job — the local 3.11 sandbox cannot host the 3.12 fixture API).
   - Gates: G0 PASS, G2 PASS (self-check), **G4 PASS (independent qa-engineer)**, **G5 PASS
     (independent security-reviewer)** — both at the frozen commit, run in parallel, zero
     blocking findings. G4 independently reproduced the BEFORE failure and the npm-ci
     fail-closed proof; G5 independently verified integrity/advisories/age with no waiver and
     no suppression anywhere in the diff.
   - GitHub checks on the implementation head: **ALL SUCCESS** across both workflow runs —
     including `web-dependency-security` (the B-019 gate, now green) and `web-e2e`; final
     confirmation on the finished PR head accompanies the return message.
   - Reviewer documentation notes (non-blocking, recorded here per G4 L1/L2): the packet's
     AS-1/AS-6 scenario text and two lines of the G0 report predate the pre-submit contract
     correction that added the override line; the corrected packet fields
     (allowed_paths/objective) govern. Recorded transparently rather than editing recorded
     gate artifacts.

9. **Commit SHA and PR URL:**
   - Frozen implementation commit (reviewed): `e7c7d37745e35c56abb39f854bc14c44d6e87723`
   - PR: https://github.com/martin10101/nyc-buildability/pull/223 (base `main`; OPEN, not merged)

10. **No waiver was used** — confirmed three ways: the age gate passes on merit (>604,800 s);
    no waiver/exception/allowlist/suppression file exists or was modified anywhere in the diff
    (G5 sweep); D-015-R001 records the owner's explicit "NO age waiver is requested or
    authorized."

11. **Exact merge and subsequent branch-sync sequence (owner-controlled; none performed here):**
    1. `gh pr merge 223 --merge` — lands the fix on main; the `web-dependency-security` gate is
       green repo-wide from this point; **B-019 resolves** (update its status to resolved on the
       branch where it lives, or at the control-branch merge).
    2. `gh pr merge 222 --merge` — the supervisor repair into `control/context-intelligence-init`
       (its lock is identical to pre-fix main and untouched; after step 1 its
       `web-dependency-security` check inherits green — re-run checks if branch protection
       requires fresh results on the merge base).
    3. Merge `control/context-intelligence-init` → `main` (PR). Expected conflict:
       `project-control/directives/index.json` (this branch appended D-015; the control stack
       appends D-014) — resolve as the union D-001..D-015 and re-run
       `python tools/validate_directive_compliance.py --check` before completing the merge.
    4. After step 3, the controller-update procedure for the M0-T070 supervisor fix remains
       R595-gated per the PR #222 return report.

**Do not merge** — honored: PR #223 and PR #222 are both OPEN; nothing was merged, activated,
or synced to the control branch by this session.
