# M0-T019 Frontend Security Reconciliation + Owner Decision Request (2026-07-23)

**Control-only.** Owner directive 2026-07-23 Part 1 (P0 dependency reconciliation). No merge, no task movement, no dispatch, no implementation, no dependency installed. This branch amends the M0-T019 packet and adds two blockers; it does not touch `apps/web`.

## 1. Reconciled state (independently verified)

| Item | Verified value |
|---|---|
| `origin/main` | `1acb9b510541cfa87afff6b2dc197880e01a389b` (unchanged; matches the directive's reference) |
| PR #64 branch `task/M0-T019-frontend-security` | head `3908082`; **115 commits behind / 8 ahead** of origin/main (substantially stale — confirmed) |
| M0-T019 ledger status | `claimed` (frontend-engineer, 10%) — **not moved by this amendment** |
| Current main `apps/web/package.json` | `next 15.3.4`, `react 19.1.0`, `react-dom 19.1.0`, `eslint-config-next 15.3.4` (matches the directive's observation) |
| Prior M0-T019 target | `next/eslint-config-next 15.5.20` — **STALE** |

## 2. Advisory evidence (verified 2026-07-23 via official pages)

- **React CVE-2025-55182** (react.dev/blog/2025/12/03/…): unauth RSC **RCE, CVSS 10.0**. Affected: react-server-dom-* **19.0, 19.1.0, 19.1.1, 19.2.0**. Fixed: **19.0.1, 19.1.2, 19.2.1** → the **19.1.x fix is 19.1.2**. The page also references later React CVEs (CVE-2025-55184/67779 DoS, CVE-2025-55183 source exposure, **CVE-2026-23864** DoS discovered 2026-01-26). **Action:** keep react/react-dom **19.1.2** but re-verify it is advisory-free against those later CVEs at implementation; move to a newer 19.1.x patch if not.
- **Next.js July 20 2026 security release** (nextjs.org/blog/july-2026-security-release): updates in **v16.2.11 (Active LTS)** and **v15.5.21 (Maintenance LTS)**; **4 HIGH** (CVE-2026-64641/64642/64645/64649) + **5 MEDIUM** (CVE-2026-64643/64644/64646/64647/64648). **Action:** target **next==15.5.21** and **eslint-config-next==15.5.21** (Maintenance-LTS line; Next 16 remains prohibited).

## 3. Control amendment applied to M0-T019 (this branch)

1. Target updated: **next/eslint-config-next 15.5.20 → 15.5.21**; react/react-dom **19.1.2** retained with a re-verify-against-later-React-CVEs requirement; postcss override 8.5.10 (re-verify).
2. **Implementation must begin from a freshly frozen current-main SHA** captured at dispatch; **do NOT merge or mechanically rebase the stale PR #64 branch** (115 behind) — it is **superseded**.
3. Next 16 / 16.x / canary / preview prohibition preserved.
4. Full-lock re-verification requirement preserved (runtime + dev + build + optional + tooling): FE-S2 blocking audit, FE-S9 committed-lockfile age gate, FE-S10 exact pins, FE-S11 npm-tooling advisory check all retained.
5. New blockers referenced: **B-013** (age exception) on M0-T019; **B-012** (public-deploy hold) standing.

## 4. Owner decision requested — AGE-ONLY emergency exception (B-013)

**next@15.5.21 was published 2026-07-20 → ~3 days old as of 2026-07-23 → under the 7-complete-day age gate.** Applying this security patch now requires an **AGE-ONLY** emergency exception, which the agent may **not** self-authorize.

Please choose:
- **(a) GRANT** an AGE-ONLY exception for `next@15.5.21` + `eslint-config-next@15.5.21` — recorded with the policy's exception fields (packages, reason = security-patch-under-age-gate, authorizer, timestamp, **auto-expiry 2026-07-27**, scope = these two packages only). It waives **only** age.
- **(b) DECLINE** — wait until **2026-07-27**, when 15.5.21 reaches 7 complete days and no exception is needed.
- **(c)** direct a different official patched 15.x target.

**Under every option**, no advisory affecting the installed version, integrity/hash failure, unverified package, unexpected registry host, or failed test may be waived.

## 5. Deployment hold (B-012)

Public frontend deployment / production exposure of `apps/web` is **blocked** until the reconciled M0-T019 upgrade is **accepted** and its P0 security gates pass. B-012 is written **not** to reference `M0-T019` in its `affects`/`detail` (only in a non-scanned `gated_by_task` field) so it cannot deadlock M0-T019's own acceptance; accepting M0-T019 clears it. (The API separately remains INTERNAL/DEV-only with no auth/RLS — B-001 chain.)

## 6. What was NOT done
- M0-T019 **not** moved/re-dispatched/claimed/implemented; PR #64 **not** merged or rebased; **no** dependency chosen or installed; `apps/web` untouched.
- This is a control-file amendment (packet + 2 blockers + this report) on a dedicated branch, pending owner approval + the B-013 decision.
