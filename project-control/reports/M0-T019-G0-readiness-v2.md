# M0-T019 — Fresh G0 readiness (v2, full-scope re-dispatch under D-009)

**Gate:** G0 (administrative dispatch-readiness). **Result:** PASS. **Recorded by:** orchestrator.
**Frozen base:** origin/main `d5d9b506c8be63eafd00ad92bd2d3dab2012d067`. **Date:** 2026-08-04.

Supersedes the original G0 (PR #63). Bound to the **full-scope** packet + the new frozen SHA per the
restart sequence (`M0-T019-frontend-security-reconciliation-2026-07-23.md` §4a). Governance-path edits
(`.github/workflows/`, `CLAUDE.md`) are authorized by the fresh owner-activated directive **D-009**.

## Scope (full — no deferral)

Next/React security upgrade (next==15.5.21, react==19.1.2, react-dom==19.1.2, eslint-config-next==15.5.21,
override postcss==8.5.10 — re-verify at implementation); committed-lockfile release-age gate
`apps/web/scripts/dependency_age_gate.mjs` + tests (FE-S9); exact pins (FE-S10); npm@11.18.0 tooling pin +
continuous advisory check (FE-S11); blocking audit (FE-S2) + scheduled audit workflow (FE-S7);
`docs/DEPENDENCY_SECURITY_POLICY.md` (FE-S8); and the concise permanent rule appended to `CLAUDE.md`.

## Readiness checklist

| Check | Evidence |
|---|---|
| Dependencies accepted | M0-T018 accepted; M0-T020 accepted — both clear. |
| Governance authorization | Fresh directive **D-009** (owner-activated 2026-08-04) is active and scoped (task_types governance, task_ids M0-T019); `covers_governance(M0-T019)` = True. Claim cites `D-009:ALL`; s19/D-001-R118 guard satisfied for `.github/workflows/` + `CLAUDE.md`. |
| Age blocker eligible | next@15.5.21 / eslint-config-next@15.5.21 (published 2026-07-21T15:59Z) crossed 7 days on 2026-07-28T15:59:32.231Z (past). B-013 resolvable with registry-time evidence at implementation. |
| CI infra clear | B-009 (Actions billing) resolved; B-016 (PR API outage) resolved. GitHub Actions authoritative for web suites (thin-client: no local node_modules). |
| Stale lineage superseded | PR #64 (115 behind) superseded — not merged/rebased; its worktree already absent. Fresh build re-forks from the frozen SHA on a new branch. |
| Producer / reviewers | Producer: frontend-engineer (claude-opus-4-8). Reviewers: G3 code-reviewer, G5 security-reviewer (both != producer). Gates: G0/G2/G3/G4/G5. |

## Key implementation risk carried into dispatch (not a blocker)

Lockfile regeneration under thin-client: local npm is prohibited (owner PC disk budget), so the committed
`apps/web/package-lock.json` update must be produced and verified in **GitHub Actions CI**, never by a local
install. FE-S9 age gate must use bounded retries + backoff and fail closed with a distinct
`infrastructure_unavailable` result on registry outage; never warning-only; never treat a network failure as
advisory-free.

**Verdict: PASS — cleared for full-scope dispatch at `d5d9b50` under D-009.**
