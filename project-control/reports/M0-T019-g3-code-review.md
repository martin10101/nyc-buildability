<!-- VERBATIM reviewer return (code-reviewer agent, G3, M0-T019), saved unchanged by the
orchestrator per the report-preservation rule (transport: agent return channel, 2026-08-07).
Leading sentence of the return retained below. VERDICT: FAIL (Defect 1, D-009-R021). -->

I have completed my independent verification. Let me compile the gate report. Here is my full verdict and report.

---

# Gate Report

- **Gate ID:** M0-T019-G3 (code review; D-009-R015-mandated re-run over amendment 1 / Option B)
- **Task ID:** M0-T019 (frontend framework security upgrade + permanent machine-enforced dependency-security policy)
- **Reviewer:** code-reviewer (independent; != producer frontend-engineer / != orchestrator)
- **Producer:** frontend-engineer (increment 3, Option B close-out)
- **Result:** **FAIL** (one blocking directive-conformance defect: D-009-R021; all code deliverables pass)
- **Clean environment/worktree used:** worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `control/D-009-batch-close`. Frozen review head **2aee4ff**. Confirmed the delta 2aee4ff→current HEAD (7c7368d) is ledger-only (`project-control/gates/M0-T019-G2.json`, `reports/M0-T019.json`, `state.json`, `tasks/M0-T019.json`), so the deliverable tree is byte-identical to the frozen head. Diff base origin/main.

## Acceptance criteria reviewed

Reviewed the full M0-T019 material in packet scope: `apps/web/package.json`, the CI-regenerated `apps/web/package-lock.json` (bot commit 1d678fd), `apps/web/.npmrc`, `apps/web/scripts/dependency_age_gate.mjs` + `scripts/tests/dependency_age_gate.test.mjs` (40 tests), the three workflows (`ci.yml` web-dependency-security job, `generate-lockfile.yml`, `scheduled-web-audit.yml`), `docs/DEPENDENCY_SECURITY_POLICY.md`, the CLAUDE.md principle #15 rule, the reports (`M0-T019-producer-report.md`, `M0-T019-fes9-mootness-2026-08-07.md`, `M0-T019-evidence-map.json`), and the fixtures under `project-control/reports/m0-t019-fes9-mootness/`. Re-derived the mootness-by-lapse position against directive rows D-009-R008..R021 and source-002-amendment.md.

## Directive/requirement verification

Re-derived each requirement from source at the frozen head. The producer's evidence map was treated as claims to reproduce.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-009-R001 (authorization to edit governance paths) | 2aee4ff | PASS | `.github/workflows/{ci,generate-lockfile,scheduled-web-audit}.yml` + CLAUDE.md #15 edited under authorization |
| D-009-R002 (no unresolved advisory; audits fail closed; no waiver) | 2aee4ff | PASS | Gate + all three workflows fail closed with no `--ignore`/suppression; overridden pins advisory-free (bulk-advisory fixture `{}`) |
| D-009-R003 (min-release-age=7, exact pins, lockfile integrity) | 2aee4ff | PASS | `.npmrc` (`min-release-age=7`, `save-exact=true`, `package-lock=true`) + exact pins in package.json + integrity present on every lock entry |
| D-009-R004 (fail-closed age gate + blocking audit + scheduled re-audit; infra_unavailable) | 2aee4ff | PASS | `dependency_age_gate.mjs` + ci.yml web-dependency-security + scheduled-web-audit.yml; `INFRASTRUCTURE_UNAVAILABLE` kind implemented and unit-tested |
| D-009-R005 (new-package provenance review; prefer existing) | 2aee4ff | PASS | Policy §5; task adds no NEW packages (version bumps/overrides only); sharp/brace-expansion provenance recorded (producer report §2b) |
| D-009-R006 (emergency exception age-only/owner/auto-expiry/no wildcard) | 2aee4ff | PASS | Policy §6 consistent with shipped gate (owner-action-outside-the-tool; gate contains no exception path) |
| D-009-R007 (concise rule in CLAUDE.md) | 2aee4ff | PASS | CLAUDE.md principle #15 added verbatim |
| D-009-R008 (owner Option B decision captured) | 2aee4ff | PASS | source-002-amendment.md#the-directive verbatim |
| D-009-R009 (implement scoped exception path) | 2aee4ff | PASS (NA-by-lapse accepted) | Empty exception set is permitted by R011 upper-bound + R012 revert-to-plain-gate; gate ships byte-unchanged; see opinion below |
| D-009-R010 (do NOT lower global 7-day threshold) | 2aee4ff | PASS | `MIN_AGE_SECONDS = 604_800` unchanged; boundary comment retained |
| D-009-R011 (exempt nothing beyond two-pin upper bound) | 2aee4ff | PASS | No allowlist/version literal in the gate (grep-clean apart from header prose); empty exception set |
| D-009-R012 (auto-expiry → revert to plain gate; registry UTC clock) | 2aee4ff | PASS | Gate clock from registry `Date` header (RegistryClient.utcNow); shipped end-state is exactly the plain 7-day gate |
| D-009-R013 (age-only waiver; all other conditions fail-closed) | 2aee4ff | PASS | Vacuously preserved — every package (incl. the two pins) flows through identical fail-closed logic |
| D-009-R014 (advisory-free + pre-incident publish; re-verify) | 2aee4ff | PASS | Fixtures: bulk advisory `{}`; publish ts brace-expansion 2026-07-30T10:17:06.961Z, sharp 2026-07-01T11:28:34.077Z — both before 2026-08-04 |
| D-009-R015 (re-run G3 over the change) | 2aee4ff | PASS (this review) | This is the independent G3 re-run at the finalized head |
| D-009-R016 (re-run G5 over the change) | 2aee4ff | UNVERIFIABLE (separate G5 security-reviewer pass) | Out of this reviewer's remit |
| D-009-R017 (regenerate lockfile via CI, validated) | 2aee4ff | PASS (corroborated) | Lock authored by `github-actions[bot]` (commit 1d678fd, 2026-08-07 19:24:55Z); workflow gates the commit step on npm ci + npm audit + FE-S9 + FE-S11 all passing; recommend orchestrator confirm run ids 31211100620 (failed) / 31211311419 (succeeded) in the Actions log |
| D-009-R018 (run remaining gates on finalized head) | 2aee4ff | PARTIAL (orchestrator) | G2 self-check recorded; G3 = this pass; G4/G5 pending |
| D-009-R019 (capture exception + authorization verbatim) | 2aee4ff | PASS | source-002 + producer report §7 + mootness report |
| D-009-R020 (report accept-readiness) | 2aee4ff | PASS | Producer report §7d |
| **D-009-R021** (update every "no exception path" assertion so no committed text contradicts shipped gate) | 2aee4ff | **FAIL** | Task-file FE-S5/FE-S8/FE-S9 and new FE-S12 assert a **machine-realized** exception + "deterministic unit tests" that **do not exist** in the shipped byte-unchanged gate — see Defect 1 |
| D-010-R121 (session ordering: dep-security batch first) | 2aee4ff | PASS (informational; outside D-009) | Batch resolved first in control/D-009-batch-close |

## Steps independently executed

1. `git rev-parse HEAD` / branch / log — confirmed worktree state; delta to frozen head is ledger-only.
2. `git diff --stat origin/main..2aee4ff` — enumerated the 53-file change set; isolated M0-T019 deliverables.
3. `git log origin/main..2aee4ff -- apps/web/scripts/dependency_age_gate.mjs` — two commits (2e31711, eb80a4d); `git diff` across both showed **comment-only** changes; `git diff eb80a4d 2aee4ff` for the gate = empty. Gate is byte-stable with no exception logic added at any point.
4. Grep of the gate for `allowlist|exception|brace-expansion|sharp|js-yaml|--ignore|1.1.18|0.35.3|4.3.1` — only header prose asserting the *absence* of an allowlist; **zero** version literals or exception code.
5. `node --test scripts/tests/dependency_age_gate.test.mjs` → **40 pass / 0 fail** (14.3s).
6. Read all four mootness fixtures; recomputed age arithmetic (below).
7. Inspected lock entries for next/react/react-dom/postcss/sharp/brace-expansion/js-yaml — versions, resolved hosts, integrity.
8. Grep of all lock `resolved` hosts — **zero** non-`registry.npmjs.org` hosts across 560 resolved entries.
9. `git show -s` on 1d678fd — confirmed `github-actions[bot]` authorship and 2026-08-07 19:24:55Z timestamp.
10. Grep for machine-realized-exception assertions across the tree — the only hit is `project-control/tasks/M0-T019.json`.
11. Grep of the test file for `brace-expansion|sharp|exempt|expired|allowlist|exception` — **no matches** (confirms FE-S12's asserted exception tests do not exist).

## Expected versus actual

- **Gate byte-unchanged / no exception path:** EXPECTED per mootness position; ACTUAL confirmed (git history + grep). ✔
- **Pinned/overridden lock resolution:** EXPECTED next 15.5.21 / react + react-dom 19.1.2 / postcss 8.5.23 / sharp 0.35.3 / brace-expansion 1.1.18 / js-yaml 4.3.1, all registry.npmjs.org with integrity. ACTUAL all confirmed; both brace-expansion instances (root + nested under typescript-estree/minimatch) resolve to 1.1.18 with identical integrity (not ambiguous). ✔
- **Age arithmetic vs fixtures (full-second, gate convention):** brace-expansion@1.1.18 cleared 604800s at 2026-08-06T10:17:06.961Z (~1.38 d before the 2026-08-07T19:20:32Z capture); sharp@0.35.3 ~37.3 d; js-yaml@4.3.1 (published 2026-07-31T17:39:51.183Z) cleared at 2026-08-07T17:39:51.183Z, ~1.75 h before the bot commit at 19:24:55Z. All arithmetically correct and internally consistent. ✔ (Non-blocking note: the js-yaml margin at validation time was razor-thin, ~1.75 h.)
- **Failure→remediation→success sequence:** EXPECTED run 31211100620 FAILED on the js-yaml audit; remediated by js-yaml 4.3.1 override (commit ce3f48c); run 31211311419 SUCCEEDED (bot commit 1d678fd). ACTUAL corroborated by the commit graph and the validate-before-commit gating in generate-lockfile.yml; documented honestly in producer report §7c/§7f and mootness §2. ✔
- **40 unit tests:** EXPECTED boundary 604800/604799 + fail-closed paths. ACTUAL present and passing, incl. look-alike-host rejection (`registry.npmjs.org.evil.com` → UNEXPECTED_HOST), retry-exhaustion → INFRASTRUCTURE_UNAVAILABLE (4 attempts), null-resolved-with-integrity pass, ambiguous fail-closed, and run() end-to-end. Producer report §7e honestly discloses the 32→40 count growth. ✔
- **R021 committed-text consistency:** EXPECTED no committed text contradicts the shipped no-exception gate. ACTUAL — CONTRADICTED by the task-file acceptance scenarios (Defect 1). ✗

## Evidence paths (all absolute)

- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/scripts/dependency_age_gate.mjs` (gate; header lines 19-27 assert no exception path; MIN_AGE_SECONDS line 46; host check line 189)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/scripts/tests/dependency_age_gate.test.mjs` (40 tests; boundary lines 63-78; look-alike host lines 382-390)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/package.json` (pins + overrides lines 17-43)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/apps/web/package-lock.json` (next 6278, react 6814, react-dom 6823, postcss 6698, sharp 7184, brace-expansion 3693 + nested 2831, js-yaml 5920)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/.github/workflows/generate-lockfile.yml` (validate-before-commit; steps lines 50-85)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/.github/workflows/ci.yml` (web-dependency-security job, added lines)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/.github/workflows/scheduled-web-audit.yml`
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/docs/DEPENDENCY_SECURITY_POLICY.md` (§1 line 44-46, §2(b) line 60-69, §6 line 137-157 — all consistent with no shipped exception)
- `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/reports/m0-t019-fes9-mootness/{brace-expansion-packument-excerpt,sharp-packument-excerpt,bulk-advisory-response,js-yaml-remediation-evidence}.json`
- **Defect locus:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/tasks/M0-T019.json` (acceptance_scenarios FE-S5 line 51, FE-S8 line 54, FE-S9 line 55, FE-S12 line 58)

## Regression/security/provenance findings

- **Security posture is sound and strictly stronger than the authorized weakening.** The owner authorized (am.1) a real code-level age exception; the producer instead ships the gate unweakened while all overridden pins clear the full 7-day gate on real registry age. No allowlist parser, no expiry-clock code, no new attack surface. All four enforcement layers present and blocking; every failure branch fails closed; a network outage is a distinct `INFRASTRUCTURE_UNAVAILABLE` result (never advisory-free). GitHub Actions are SHA-pinned.
- **Provenance retained.** Publish timestamps and advisory-free status re-verified against orchestrator-captured live-registry fixtures; the `js-yaml` HIGH advisory (CVE-2026-59870 / GHSA-5p4m-2wfm-xmqj) was caught by the blocking audit and remediated with an advisory-free, ≥7-day version — an honest demonstration of the gate working as designed.
- No test/TS weakening; no `apps/web/src/**` change; no forbidden path touched; Next 16/canary/preview absent.

## Defects

**Defect 1 — BLOCKING (D-009-R021 unsatisfied): committed acceptance-scenario text asserts a machine-realized FE-S9 exception that does not exist in the shipped gate.**

The FE-S9 exception scenario text was added to the task file in commit **e96d718** (am.1 capture, 2026-08-05) in anticipation of implementing the exception. When the producer pivoted to mootness (increment 3, no exception implemented, gate byte-unchanged), this text was **not** reconciled. At the reviewed head `project-control/tasks/M0-T019.json` therefore asserts, in present tense, facts that are false about the shipped gate:

- FE-S5: "FE-S9 **now carries** a SCOPED, owner-authorized, auto-expiring age-only exception for ONLY brace-expansion@1.1.18 and sharp@0.35.3".
- FE-S8: "this exception is **MACHINE-REALIZED in FE-S9** as a scoped, auto-expiring name@version allowlist rather than an owner-action-outside-the-tool" — this also contradicts the shipped `DEPENDENCY_SECURITY_POLICY.md` §6, which still (correctly) describes the owner-action-outside-the-tool model.
- FE-S9: "the tool **carries EXACTLY ONE narrow exception path**: a scoped, owner-authorized, auto-expiring AGE-ONLY allowlist keyed by exact name@version".
- FE-S12: "FE-S9 **carries** a SCOPED … exception … **Deterministic unit tests cover**: an exempted pin under age PASSES while unexpired; the same pin FAILS once expired; a non-listed under-age pin FAILS; an exempted pin with an advisory/integrity/host failure still FAILS."

Reproduction: (a) the shipped gate has no allowlist/version literal (grep of `dependency_age_gate.mjs` returns only header prose asserting the *absence* of one; `MIN_AGE_SECONDS` is a single hard-set 604800); (b) grep of the test file for `brace-expansion|sharp|exempt|expired|allowlist|exception` returns **no matches** — the "deterministic unit tests" FE-S12 claims do not exist. This is exactly the class of contradiction D-009-R021 exists to prevent ("no committed text contradicts the shipped gate behavior").

The producer's R021 NA-by-lapse rationale is **factually inaccurate as stated**: the mootness report §6 and the evidence-map R021 entry both claim "the FE-S5/FE-S8/FE-S9 scenario language remain literally TRUE and must NOT be edited." They do not — the committed scenario language asserts the exception IS machine-realized and unit-tested. The premise for the R021 disposition therefore does not hold.

## Required rework

1. Reconcile the M0-T019 task-file acceptance scenarios with the shipped byte-unchanged, no-exception gate (orchestrator edit, since `project-control/**` is orchestrator-maintained). Either:
   - **(preferred, consistent with the mootness decision)** rewrite FE-S5/FE-S8/FE-S9 to state that the am.1 age exception was authorized but is **moot/unimplemented** (both pins clear the unchanged 7-day gate on real age), the gate ships with **no exception path**, and mark FE-S12 as **not-applicable-by-time-lapse**; remove the false "deterministic unit tests cover [exempted pin]" claim; or
   - implement the scoped exception path + the FE-S12 unit tests to match the scenarios (this reverses the mootness decision and is the weaker outcome — not recommended).
2. Correct the two secondary artifacts that repeat the inaccurate R021 claim: `M0-T019-fes9-mootness-2026-08-07.md` §6 (R021 row) and `M0-T019-evidence-map.json` R021 entry, so they acknowledge the task-file scenario language must be reconciled (not that it "remains literally TRUE").
3. Re-run this G3 code check over the reconciled head to confirm no committed text contradicts the shipped gate.

(Verification note, non-blocking: the CI run ids 31211100620 / 31211311419 are orchestrator/GitHub-side evidence I could not independently re-fetch under the read-only harness. The committed artifacts — the bot-authored, validated lockfile and the validate-before-commit gating in generate-lockfile.yml — corroborate the documented failure→success narrative; recommend the orchestrator spot-confirm the two run ids in the Actions log at accept time.)

## Reviewer conclusion

**Verdict: FAIL** (one blocking defect; everything else PASS).

Explicit opinion on the NA-by-lapse proposals the packet asked me to evaluate:

- **D-009-R009 NA-by-lapse: ACCEPTED (faithful to the directive).** R011 expressly makes the two-pin set "an upper bound; the implementation may create an entry only where actually needed," and R012 makes the exception's decay end-state the plain 7-day gate. With both named pins (and the round-2 js-yaml@4.3.1 remediation) clearing the unchanged 604800s gate on verified real registry age, an empty exception set (∅ ⊆ the ceiling) is a valid realization. The gate is provably byte-unchanged (no exception logic in any on-branch revision), R010's threshold is untouched, and R013's other fail-closed conditions are preserved for all packages. This is a strictly stronger outcome than the authorized weakening, and the age arithmetic checks out against the committed fixtures.

- **D-009-R021 NA-by-lapse: REFUTED as stated → the blocking defect.** The "no exception path" assertions in the gate header and policy doc were correctly left intact and remain true — but the task-file acceptance scenarios (FE-S5/FE-S8/FE-S9/FE-S12) were affirmatively edited to describe a machine-realized exception and its (non-existent) unit tests, and were never reverted. At the reviewed head, committed text therefore contradicts the shipped gate behavior — precisely the condition R021 forbids. The security control and all code deliverables are correct; the fix is a text/consistency reconciliation of the task-file scenarios (and the two reports that repeat the inaccurate claim), after which this G3 should be re-run.

The orchestrator should record this gate as FAIL and route the reconciliation rework; do not accept M0-T019 until the committed acceptance-scenario text matches the shipped no-exception gate.
