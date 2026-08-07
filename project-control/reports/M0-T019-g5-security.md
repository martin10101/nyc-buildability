<!-- VERBATIM reviewer return (security-reviewer agent, G5, M0-T019), saved unchanged by the
orchestrator per the report-preservation rule (transport: agent return channel, 2026-08-07).
Leading sentence of the return retained below. -->

I have completed my independent verification. All security-material facts are confirmed from the frozen tree. Here is my G5 security report.

---

# G5 Security Review — M0-T019 (Frontend framework security upgrade + permanent machine-enforced dependency-security policy)

**Directive:** D-009 (+ amendment 1 / "Option B"), re-run mandated by D-009-R016
**Task:** M0-T019
**Reviewer:** security-reviewer (independent; producer = frontend-engineer; producer ≠ reviewer)
**Review tree:** worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `control/D-009-batch-close`
**Frozen reviewed identity:** `2aee4ff7f00367c56d9217e900b5912d3b407a94` (material identity; current HEAD `7c7368d9` differs only in control-plane/ledger files — verified below)
**Diff base:** `origin/main`
**Date:** 2026-08-07

## VERDICT: PASS (no blocking findings; 3 LOW/informational non-blocking notes)

---

## 1. Identity / frozen-head verification

- Current worktree HEAD is `7c7368d9` (a ledger-only commit "identity at 2aee4ff"). `git diff 2aee4ff..HEAD` touches **only** `project-control/gates/M0-T019-G2.json`, `project-control/reports/M0-T019.json`, `project-control/state.json`, `project-control/tasks/M0-T019.json`. **Zero** M0-T019 material files differ; working tree is clean. Reading the working tree therefore faithfully reflects the frozen material identity at `2aee4ff`.
- Material scope diff vs `origin/main`: `ci.yml` (+82), `generate-lockfile.yml` (+65/-), `scheduled-web-audit.yml` (new, +88), `CLAUDE.md` (+1), `apps/web/.npmrc` (new, +19), `apps/web/package-lock.json` (regenerated), `apps/web/package.json` (+44), `dependency_age_gate.mjs` (new, +494), test file (new, +533), `docs/DEPENDENCY_SECURITY_POLICY.md` (new, +174).

## 2. Method (independent, read-only)

Re-derived every security-material claim from source rather than trusting the producer: read the full gate module (495 lines), the 40-test suite, all three workflows, `.npmrc`, `package.json`, the policy doc, the CLAUDE.md rule diff, the mootness report, the producer report, the evidence map, and all four committed fixtures. Independently parsed the committed `package-lock.json` for host/integrity coverage, re-computed the age arithmetic, and scanned all touched files + fixtures for secrets and for any hidden bypass token. (Live registry calls and the CI runs cannot be executed from the read-only sandbox; those are addressed via committed fixtures + deterministic arithmetic + code inspection, see §7.)

## 3. Core mandate of D-009-R016 — is the authorized weakening actually absent?

**CONFIRMED — the shipped gate contains no exception/allowlist/bypass path.** Verified by full read of `apps/web/scripts/dependency_age_gate.mjs`:

- The only occurrences of `allowlist` / `--ignore` / `suppress` / `exception` (lines 19, 27, 379, 417) are **prose/CLI-message strings describing the ABSENCE** of any such path. There is no allowlist data structure, no `--ignore` argument handling, no skip branch, and **no reference to `brace-expansion` or `sharp`** (or any package name) in the gate logic.
- `MIN_AGE_SECONDS` is a hardcoded `const 604_800` (line 46), referenced only in the comparison (line 231) and log messages. It is **not** read from `process.env` or any config — the gate performs **no** `process.env` reads at all — so the threshold cannot be overridden at runtime.
- Only one `.npmrc` exists in the entire repo (`apps/web/.npmrc`); no root-level `.npmrc` re-introduces a weaker resolver posture.

**The control is NOT weakened relative to its previously-reviewed state; it ships at full strength.** A control authorized to be weakened but shipping unweakened while still admitting the needed pins is strictly stronger than one shipping with the weakening. The security intent of the owner's directive (age as npm-incident infection protection) is met in the strongest form.

## 4. R013 fail-closed conditions — all intact

| Condition | Enforcement (verified) |
|---|---|
| Integrity mismatch | `decide()` → `INTEGRITY_MISMATCH` when lock integrity ≠ official `dist.integrity` (lines 215–218); also `MISSING_INTEGRITY` when the lock or the registry lacks a hash (193–196, 209–214). |
| Unexpected resolved host | `UNEXPECTED_HOST` via `startsWith("https://registry.npmjs.org/")` (line 189); look-alike (`…org.evil.com`) and userinfo (`…org@evil.com`) both rejected — unit-tested (test line 382). |
| Missing/malformed timestamp | `MISSING_TIMESTAMP` for absent or `NaN` publication time (lines 220–229). |
| Advisory hit | Covered by `npm audit --audit-level=low` **and** JSON-total==0 (FE-S2) in `web-dependency-security`, `generate-lockfile`, and `scheduled-web-audit`; plus FE-S11 `decideNpmCli` which fails on any advisory for the pinned npm CLI, fail-closed on outage. |
| Registry outage | Distinct `INFRASTRUCTURE_UNAVAILABLE` after bounded retries (1+3), never treated as advisory-free/age-clean (lines 249, 466–472). Deterministic failures (missing `Date` header, malformed JSON) are **not** retried and fail closed immediately. |
| Ambiguous lock (same name@version, conflicting integrity/resolved) | `parseLock` flags `ambiguous`; `decide()` → `AMBIGUOUS` (lines 146–155, 180–182). |

Clock is taken from the registry's own `Date` response header, not the local/CI clock (lines 316–329) — a tampered runner clock cannot spoof age. Boundary is exact: 604800 passes / 604799 fails (unit-tested). The 40-case suite (`git`-counted; matches the producer's honest §7e correction of the earlier "32") exercises every fail-closed branch offline via injected clock + packument.

## 5. Supply-chain posture of the final pin set

Overrides in `package.json`: `postcss 8.5.23`, `sharp 0.35.3`, `brace-expansion 1.1.18`, `js-yaml 4.3.1`. Independently confirmed present in the lockfile with `resolved`+`integrity`. Committed fixtures + arithmetic:

| Pin | Published (registry) | Age at 2026-08-07 capture | Advisory (bulk endpoint) | vs 2026-08-04 incident window |
|---|---|---|---|---|
| brace-expansion@1.1.18 | 2026-07-30T10:17:06.961Z | ~8.38 d (cleared 7 d 2026-08-06T10:17:06Z) | `{}` (none) | published **before** the incident |
| sharp@0.35.3 | 2026-07-01T11:28:34.077Z | ~37.3 d | `{}` (none) | published **before** the incident |
| js-yaml@4.3.1 | 2026-07-31T17:39:51.183Z | ~7.07 d (cleared 7 d 2026-08-07T17:39:51Z, ~1.7 h pre-capture) | `{}` (none) | published **before** the incident; is the fix for CVE-2026-59870 (js-yaml 4.0.0–4.3.0 HIGH) |

All override versions predate the 2026-08-04 npm bad-publish window, are advisory-free at the same source `npm audit` consults, and are integrity-matched to the current registry. The tightest margin (js-yaml, +1.7 h) is internally consistent: for the successful lockfile run to have passed the fail-closed FE-S9 gate it must have executed after 2026-08-07T17:39:51Z, which matches the report's placement of that run after the 19:23Z remediation capture. The round-2 js-yaml find (caught by the blocking audit in the first, failing regeneration and remediated to an advisory-free ≥7-day version with zero age exception) is genuine evidence the fail-closed design works as intended.

## 6. Lockfile provenance & integrity

Independently parsed the committed `package-lock.json` (lockfileVersion verified): **560** `resolved` entries, **all** `https://registry.npmjs.org/…` (0 off-registry, grep-confirmed), and exactly **560** `integrity` lines (1:1 — every resolved tarball carries an integrity hash). js-yaml resolves to a single `node_modules/js-yaml` at 4.3.1 (the `"^4.3.0"` at line 1071 is a consumer's range spec satisfied by 4.3.1; no stale 4.3.0 installed).

## 7. Workflow / least-privilege / SSRF-injection review

- **generate-lockfile.yml** — trigger `workflow_dispatch` **only** (not exposed to forks; requires a write-access actor); `permissions: contents: write` (minimum needed to push the lock). It regenerates with `--package-lock-only` (no script execution, no install), then **validates before committing** (npm ci integrity → blocking npm audit ×2 → FE-S9 age gate → FE-S11), and `git add`s **only** `apps/web/package-lock.json` with a fixed commit message — it cannot smuggle other file changes or commit an unvalidated lock. Bot identity is `github-actions[bot]`. Abuse surface is low.
- **scheduled-web-audit.yml** — `schedule` + `pull_request` (path-filtered to the web dep artifacts) + `workflow_dispatch`; `permissions: contents: read`. Uses `pull_request` (not `pull_request_target`), so fork PRs run with a read-only token and no secret access — no privileged-context injection. Clean.
- **ci.yml** — workflow-level `permissions: contents: read`; the `web-dependency-security` job runs the unit tests, `npm ci`, both audit forms, the age gate, and the FE-S11 check, blocking on every push/PR.
- **All third-party actions are SHA-pinned** (checkout, setup-node, setup-python, upload-artifact) with version comments — satisfies the policy's "SHA-pin every third-party GitHub Action."
- **SSRF/injection:** the gate's only network egress is to hardcoded `registry.npmjs.org`; the packument URL is `${REGISTRY_ORIGIN}/${encodeURIComponent(name).replace("%40","@")}` — the base host is fixed and the lock-derived `name` is URL-encoded (path/host separators neutralized), so a crafted lock entry cannot redirect the request to another host. No shell interpolation of untrusted data anywhere (the CI `node -e` reads only the npm-generated `$RUNNER_TEMP/audit.json`). No command injection.
- **Secrets hygiene:** secret-pattern scan across all touched files and all four fixtures returned only two benign comments ("No secrets are referenced…"). No tokens, keys, or credentials committed. Log output is package metadata only — no redaction concern.
- **Not applicable to this task's scope (noted for completeness):** cross-tenant isolation, service-role secrecy, private storage, upload controls, prompt-injection defenses — no database/Supabase/storage/tenant/AI surface is touched by M0-T019.

## 8. Honesty check (no committed text overstates safety)

- Gate header, policy §1/§2(b)/§6, and CLAUDE.md #15 assert "no exception path/allowlist/suppression" — **literally true** (verified in code).
- Policy §6 ("Emergency exception — AGE ONLY") is honest and internally consistent: it explicitly states the machine gates contain **no** exception path and can only be satisfied by real registry age, so a "paper" exception cannot make the gate pass. It is a governance procedure, not a claimed code bypass.
- `.npmrc` doc accurately describes itself as resolver-time defense-in-depth, **not** the committed-lock gate; it does not falsely claim `ignore-scripts` is set.
- Producer report is candid about limitations: §2b records the postcss 8.5.10→8.5.23 advisory-driven correction (not a waiver); §7e self-corrects the test count (32→40); §4/§6 mark the full-tree audit and zero-drift proof as "needs-CI" and explicitly state the producer does not self-approve.

## 9. Opinion on the R009 / R021 NA-by-lapse proposals (security standpoint)

- **R009 (implement the exception path) → NOT_APPLICABLE-BY-TIME-LAPSE: CONCUR (security-strongest outcome).** The owner authorization (R008/Option B) was permissive, and R011 made the two-pin set an explicit upper bound ("create an entry only where actually needed"). Both pins now clear the unchanged 604800 s gate on real registry age (verified §5), so zero entries are needed. Not building an exception path means no allowlist parser and no expiry-clock logic to get wrong — a smaller attack surface and a fully fail-closed control. From security, this is strictly preferable to the authorized weakening.
- **R021 (update every "no exception path" assertion) → NOT_APPLICABLE-BY-TIME-LAPSE: CONCUR.** Because no exception path ships, those assertions remain literally true; editing them to describe a non-existent path would make the docs less accurate. Leaving them intact is the correct, honest disposition.

Both proposals are, from the security standpoint, the correct and strongest realization of the directive. (Formal per-requirement directive-compliance verification across all D-009 IDs is the directive-compliance-verifier's pass; this review confirms the security-material subset — R010/R011/R012/R013/R014/R016 and the R009/R021 dispositions — is satisfied and honest at the frozen head.)

## 10. Findings

- **LOW-1 (non-blocking, hardening).** `apps/web/.npmrc` does not set `ignore-scripts=true`, so `npm ci` runs dependency lifecycle scripts on the runners. Policy §5 lists `ignore-scripts` as the "preferred where feasible" posture (and the owner's global new-repo default sets it), so this is a defense-in-depth gap, not a policy violation, and no committed text overstates it. Highest-impact exposure is `generate-lockfile.yml`, where `npm ci` (script-running) executes under `contents: write` before the blocking audit; the residual risk is mitigated by exact pinning + ≥7-day age + advisory + integrity checks. Recommend evaluating `ignore-scripts=true` feasibility (sharp 0.33+/esbuild/Next SWC ship platform binaries as optional deps and typically work without install scripts). Does not block: not mandated, not a regression, well-mitigated.
- **LOW-2 (informational / operational assurance).** The gates only block merges if branch protection marks `web-dependency-security` (and, on schedule, `scheduled-web-audit`) as **required** checks — a repo-settings dependency outside the reviewed tree. Separately, the validated lock's bot commit (`1d678fd`, GITHUB_TOKEN) does not auto-trigger downstream CI; however `generate-lockfile.yml` validates the lock inline before committing, and any subsequent human push/PR re-runs `ci.yml` over the lock, so the lock is gated. Recommend the orchestrator confirm the required-check configuration.
- **LOW-3 (informational / evidence-completeness).** The read-only sandbox cannot execute live registry calls or re-run CI runs `31211100620` (fail, caught js-yaml) / `31211311419` (pass, bot commit `1d678fd`). I verified provenance via the committed fixtures, deterministic age arithmetic, and full code inspection — the security posture (no exception path, fail-closed conditions, clean provenance) does not depend on re-execution. Recommend the orchestrator attach the two CI run records and the green `web-dependency-security` result over the finalized head as the authoritative live-gate artifact. Not a defect.

## 11. Conclusion

The security intent of D-009 (including amendment 1) is satisfied in its strongest form: the authorized deliberate weakening was **never implemented**, the fail-closed committed-lock age gate ships byte-intact with no exception/allowlist/env-override path, R013's fail-closed conditions are all present, lockfile provenance is 100% official-registry with full integrity coverage, all override pins are advisory-free/≥7-days/pre-incident, workflows are least-privilege with SHA-pinned actions and no secrets, and no committed text overstates safety. The R009/R021 NA-by-lapse dispositions are, from the security standpoint, correct.

**VERDICT: PASS** — no HIGH/MEDIUM/critical findings; three LOW/informational non-blocking items (LOW-1 ignore-scripts hardening; LOW-2 required-check/branch-protection assurance; LOW-3 attach live-CI artifacts). None blocks acceptance.

---

Key file paths reviewed (all absolute):
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/scripts/dependency_age_gate.mjs`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/scripts/tests/dependency_age_gate.test.mjs`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/.npmrc`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/package.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/package-lock.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/.github/workflows/ci.yml`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/.github/workflows/generate-lockfile.yml`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/.github/workflows/scheduled-web-audit.yml`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/docs/DEPENDENCY_SECURITY_POLICY.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/CLAUDE.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/reports/M0-T019-fes9-mootness-2026-08-07.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/reports/M0-T019-producer-report.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/reports/M0-T019-evidence-map.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/reports/m0-t019-fes9-mootness/{brace-expansion-packument-excerpt,sharp-packument-excerpt,bulk-advisory-response,js-yaml-remediation-evidence}.json`

Note to orchestrator: I did not write any file or run the control CLI/git-write. Please save this report verbatim to `project-control/reports/M0-T019-g5-security.md` and record the G5 gate result (PASS) yourself.

---

<!-- VERBATIM delta re-confirmation return (same security-reviewer agent, continued transcript),
appended unchanged by the orchestrator per the report-preservation rule, 2026-08-07. -->

Delta verification complete. I have everything needed to attest.

The four changed files are all documentation/task-ledger; the entire security-material surface (gate, tests, `.npmrc`, `package.json`, lockfile, all three workflows, policy doc, CLAUDE.md, fixtures) is byte-identical between my reviewed identity `2aee4ff` and current HEAD `693c302`. The changes are honesty corrections, not new claims.

---

# G5 Security Review — Delta Re-Confirmation (append to reports/M0-T019-g5-security.md)

**Reviewer:** security-reviewer (independent)
**Original G5 verdict:** PASS (material identity `b8af26bc` / head `2aee4ff`)
**Delta reviewed at:** current head `693c302d030cf9fe8ce43a4c8f4e5eeb80e5cfd8`, material identity `46e4d83e`, branch `control/D-009-batch-close`
**Date:** 2026-08-07

## DELTA VERDICT: PASS (original PASS stands; no security-material change, no new overstatement)

### D1. Security-material byte-identity — CONFIRMED unchanged
`git diff --stat 2aee4ff..HEAD` over the full security surface — `apps/web/scripts/dependency_age_gate.mjs`, its test file, `apps/web/.npmrc`, `apps/web/package.json`, `apps/web/package-lock.json`, `.github/workflows/{ci.yml,generate-lockfile.yml,scheduled-web-audit.yml}`, `docs/DEPENDENCY_SECURITY_POLICY.md`, `CLAUDE.md`, and the four `m0-t019-fes9-mootness/` fixtures — returns **empty**. The gate ships byte-identical to what I reviewed: still no allowlist/`--ignore`/suppression/exception path, no `process.env` threshold override, hard-set `MIN_AGE_SECONDS = 604_800`. Every §3/§4/§5/§6/§7 conclusion of the original report is preserved verbatim.

### D2. What actually changed — 4 documentation/ledger files only
`git diff 2aee4ff..HEAD` touches only: `project-control/reports/M0-T019-producer-report.md` (added §7h), `project-control/reports/M0-T019-fes9-mootness-2026-08-07.md` (§6 R021 row + §7 item 4 corrected), `project-control/reports/M0-T019-evidence-map.json` (R021 entry corrected), and `project-control/tasks/M0-T019.json` (FE-S5/S8/S9/S12 reconciled; status/progress/progress-log). None is security-material.

### D3. R021 correction is an honesty improvement, not a new overstatement — CONFIRMED
The prior R021 disposition claimed the task-file acceptance scenarios FE-S5/FE-S8/FE-S9/FE-S12 "remain literally TRUE and must NOT be edited." G3 (Defect 1) correctly found those scenarios had been pre-edited at am.1 (commit `e96d718`) to assert a **machine-realized** FE-S9 exception plus **deterministic unit tests** that the mootness pivot never implemented — i.e., they were false about the shipped byte-unchanged gate. The corrected artifacts now:
- **Retract** the inaccurate "remains literally TRUE" claim (explicitly labelled "factually inaccurate" in the mootness §6 R021 row and producer §7h).
- **Split** R021 correctly: the gate-header and `DEPENDENCY_SECURITY_POLICY.md` §1/§2(b)/§6 assertions were left untouched and remained literally TRUE (→ NA-by-lapse); the task-file scenarios were reconciled to the mootness outcome.
- **Reconcile** FE-S5/S8/S9/S12 to honest text: FE-S9 now reads "the tool carries NO exception path — no allowlist, no suppression, no override"; FE-S12 reads "ZERO exception entries were needed and NO exception path was implemented… the 40 shipped unit tests cover the unchanged fail-closed gate." These now match exactly what I independently verified (byte-unchanged gate; 40-test suite; all fail-closed branches).

This removes a documentation overstatement and introduces no new claim about the code. It is a strengthening of the honesty posture, consistent with my original §8 honesty findings.

### D4. Effect on my original §9 opinion — unaffected
My original R021 concurrence was scoped to the gate-header and policy-doc "no exception path" assertions (the security-material doc surface), which **did** remain true and untouched — that assessment stands and matches the corrected disposition. The task-file acceptance-scenario contradiction fell in G3's review scope (acceptance-scenario consistency), was correctly caught there, and has been reconciled; it does not alter any security-material conclusion. My R009 NA-by-lapse concurrence is likewise unchanged (byte-unchanged gate, zero exception entries).

### D5. LOW-2 / LOW-3 disposition update
The orchestrator-reported PR #176 result (33/33 green checks including `web-dependency-security` over the regenerated lock) is the live-CI artifact I requested in LOW-3 — **LOW-3 is discharged** (accepted as orchestrator-captured evidence per the read-only reviewer protocol). LOW-2's operational point is partially met (the `web-dependency-security` job demonstrably ran green over the regenerated lock); the branch-protection required-check configuration remains a repo-settings assurance item outside the reviewed tree. **LOW-1 (evaluate `ignore-scripts=true`) is unchanged** — non-blocking hardening recommendation.

### Conclusion
No security-material changed; the fail-closed committed-lock age gate remains byte-identical with no exception path; the delta consists solely of documentation/ledger honesty corrections that retract a prior overstatement and reconcile the task-file scenarios to the shipped no-exception gate. **My G5 verdict stands: PASS at material identity `46e4d83e` (head `693c302`).** No new blocking findings; LOW-1 open (non-blocking), LOW-3 discharged, LOW-2 partially addressed.
