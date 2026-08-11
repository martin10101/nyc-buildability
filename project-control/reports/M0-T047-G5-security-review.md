# M0-T047 — G5 security review (VERBATIM reviewer return)

Independent reviewer: `security-reviewer` (read-only; reviewer != producer orchestrator).
Returned via agent channel; saved verbatim (transport entity-decoding only).

---

All checks are verified. Here is my G5 report.

---

# G5 Security Gate Report — M0-T047 (admit nanoid 3.3.17 to apps/web)

**Gate:** G5 (dependency-security / security review)
**Task:** M0-T047 — remediate GHSA-2v37-7h3g-55p8 by admitting nanoid 3.3.17 via exact-pin override
**Directive:** D-009 dependency-security (D-009-R002/R003/R004/R005)
**Reviewed SHA:** `c032dfe54bc2c947d1b86b7f87988d658a04a6cd` (PR #220 HEAD, branch `control/session15-acceptance`)
**Reviewer:** security-reviewer (read-only, ADR-005)
**Method:** Independent re-derivation from the frozen SHA + PR #220 CI machine evidence. Producer report treated as claims to reproduce, not evidence.

## Identity / freshness verification
- `gh pr view 220` → `headRefOid = c032dfe…a6cd` == reviewed SHA; `state OPEN`, `mergeable MERGEABLE`, base `main`. The reviewed content is the live PR HEAD (not stale).
- The two required security jobs executed against `c032dfe` on three runs (`gh run view … headSha`): `31543737246` (push), `31543741054` (pull_request), `31543741030` (pull_request) — all `conclusion: success`, all `headSha = c032dfe…a6cd`. Evidence is bound to the reviewed identity.

## 1. Advisory remediation (D-009-R002) — PASS
Machine evidence, `web-dependency-security` job `93951647965`/`93951659768`:
- `Blocking npm audit (--audit-level=low; dev deps included)` → `found 0 vulnerabilities`
- `Blocking npm audit (JSON total vulnerabilities must be 0)` → `npm audit JSON: total vulnerabilities == 0 across all severities`

Independent full-tree job `web tree re-audit` (`93951659800`) reproduces: `found 0 vulnerabilities`, `total vulnerabilities == 0 across all severities`. Both jobs fail closed on any finding at any severity. A zero-advisory result at nanoid 3.3.17 confirms GHSA-2v37-7h3g-55p8 is remediated **and** no new advisory is introduced by the bump. The npm-CLI self-advisory check also passed at runtime: `RESULT: PASS — no advisory affects npm@11.18.0` (the co-located `# RESULT: FAIL…` / `# FAIL-CLOSED…` lines are the step's echoed branch templates in the command-echo group, not runtime output — the runtime line at 22:46:21 is the PASS).

## 2. Exact pin + integrity (D-009-R003/R004) — PASS
- `apps/web/package.json` `overrides` block adds exactly `"nanoid": "3.3.17"` — literal version string, no `^`/`~`/range.
- `apps/web/package-lock.json` `node_modules/nanoid` = `3.3.17`, `resolved = https://registry.npmjs.org/nanoid/-/nanoid-3.3.17.tgz`, `integrity = sha512-xQLf0A3HOMlgHq0n247/LRuAOYmB7dXJ/DvAxGvsSBij45XtBSmQycu+F8ODbHwns/XyFZagyL1+J0Offw1E0g==` (matches the value stated in the packet). CI reports the lock as `integrity-verified` against the official npm registry; the deterministic unit tests confirm the gate **fails closed** on integrity mismatch, missing lock integrity, and registry lacking `dist.integrity`.

## 3. Age ≥ 7 complete days (D-009-R003/R004) — PASS
Committed-lockfile age gate, re-evaluated at run time 2026-08-11T22:46 (today):
- `PASS  nanoid@3.3.17  uploaded=2026-08-03T10:39:22.487Z  age=734805s (8.50d)` (dep-security job); re-audit job: `age=734795s (8.50d)`.
- `RESULT: PASS — every committed registry package is >= 7 days old and integrity-verified` (both jobs).
- 734,805 s ≥ 604,800 s threshold. Consistent with owner-recorded D-010-R233 eligibility on/after 2026-08-10T10:39:22Z (= upload + 604800 s); today (2026-08-11) is past it.
- Deterministic boundary tests present and green: 604800 s passes / 604799 s fails; missing/malformed publication timestamp and unexpected resolved host fail closed. **No age-only waiver was invoked** — the pass rests on genuine ≥7-day age.

## 4. Supply-chain hygiene — PASS
- nanoid is a **pre-existing** dependency: the lock diff is a patch bump `3.3.16 → 3.3.17` (present at 3.3.16 before). Not a new package → no new-package G5 provenance admission is triggered; this is remediation of an existing dependency.
- A patch version bump of an existing utility introduces no lifecycle-script surface change, no maintainer-change red flag, and no secret/credential surface. No new code, network, storage, auth, upload, or SSRF/injection surface is added by the diff.
- CI least-privilege observed: security jobs run with `GITHUB_TOKEN` `Contents: read, Metadata: read`; token redacted in logs (`token: ***`). No secret leakage in captured output.

## 5. Scope (no policy/workflow/age-gate weakening) — PASS
Commit `c032dfe` touches exactly three files: `apps/web/package.json`, `apps/web/package-lock.json`, `project-control/reports/M0-T047-producer-report.md`. No `.github/workflows/**`, no age-gate/audit script, no dependency-security policy file is modified. The security gate machinery is unchanged; the fresh green CI is produced by the same enforcement code, not a weakened one.

## Cross-check against required G5 security categories
Cross-tenant isolation, service-role secrecy, private storage, SSRF/injection defenses, upload controls, prompt-injection defenses, least privilege, log redaction: **N/A to this diff** — a lockfile/override version bump of an ID-generation utility adds no runtime code path or data-plane surface touching any of these. No regression to any of them is introduced (no such code changed). Log-redaction and least-privilege in the CI pipeline itself are intact (token redacted; read-only token scopes).

## Findings
- Critical: none. High: none. Medium: none. Low: none.
- Observation (non-blocking): PR #220 is a multi-purpose control branch (title references D-011 / M2-T016 / M0-T055). This gate scopes only the M0-T047 nanoid change (commit `c032dfe`), which is self-contained (3 files) and whose security posture is fully validated by whole-tree CI on the exact HEAD. Acceptance/merge sequencing of the broader PR is an orchestrator concern, not a security defect.

## Conclusion
All five required checks reproduce independently at the frozen SHA on live PR #220 CI: advisory-free at every severity (fail-closed audit + full-tree re-audit both zero), exact pin, registry-integrity-verified, ≥7-day age genuinely satisfied (8.50 d, no waiver), pre-existing patch bump (no new-package admission), and scope limited to the two apps/web files plus the producer report with no policy/workflow/age-gate weakening.

VERDICT: PASS
