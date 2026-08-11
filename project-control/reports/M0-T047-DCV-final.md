# M0-T047 — Directive-compliance verification (VERBATIM reviewer return)

Independent reviewer: `directive-compliance-verifier` (read-only; verifier != producer orchestrator).
Returned via agent channel; saved verbatim (transport entity-decoding only). `reviewed_manifest_sha256`
`__ORCH_FILL__` placeholders were filled by the orchestrator with the G3/G5 gate `content_manifest_sha256`
`c57ae9c91eee1b38e77d2da5bd307dc5510b7ebb0cc8b458c861718d52cd4544` in the applied verification.json rows.

---

I have all evidence reproduced independently. Registry integrity validator ran clean (no output = no integrity/digest errors; consistent with `registry.errors == []` and both directives `active` with `errors: []`). Here is my report.

---

# Directive-Compliance Verification — M0-T047 (nanoid 3.3.17 remediation)

**Reviewed commit:** `c032dfe54bc2c947d1b86b7f87988d658a04a6cd` (branch `control/session15-acceptance`, PR #220)
**Producer:** orchestrator · **Verifier:** directive-compliance-verifier (producer ≠ verifier) · **Read-only pass**
**Repo:** `martin10101/nyc-buildability`

## 1. Applicability — reproduced independently

Method: `import tools.directive_registry`, `DirectiveRegistry().load()`, loaded `project-control/tasks/M0-T047.json`, called `derive_applicable(task)` and `evaluate_task_refs(task)`.

```
registry errors: []
derive_applicable applicable: ['D-010-R233', 'D-010-R246']
derive_applicable unresolved: []
evaluate_task_refs: ok=True
  applicable_ids = ['D-010-R233', 'D-010-R246']
  cited_ids      = ['D-010-R233', 'D-010-R246']
  missing_ids=[]  invalid_refs=[]  unresolved=[]  reasons=[]
```

- **Applicable = {D-010-R233, D-010-R246}, ok:True** with the corrected refs (`D-009:ALL` + `D-010:{R233,R246}`). Confirmed.
- **D-009 subset EMPTY:** all 21 D-009 rows carry `applicability.task_ids = ["M0-T019"]` (task_type `frontend`, milestone M0); M0-T047 is `security-hygiene` → every D-009 row `matches=False`. Confirmed.
- Both D-010 rows are **classification `hold`** → `hold` ∉ `LIFECYCLE_ELIGIBLE_CLASSIFICATIONS {obligation, sequencing}`, so they are **not** lifecycle-deferral-eligible and must verify **PASS directly at accept**. Confirmed.
- Task packet `directive_refs` (M0-T047.json lines 62-74): `D-009:ALL` + `D-010:["D-010-R233","D-010-R246"]`.

## 2. D-010-R233 — "age-eligible on/after 2026-08-10T10:39:22Z; do not bypass its package-age rule" → **SATISFIED (PASS)**

- **Age-eligible:** nanoid 3.3.17 published `2026-08-03T10:39:22.487Z` (task inputs; lock integrity `sha512-xQLf0A3HOMlg…`). +604800 s ⇒ eligible on/after `2026-08-10T10:39:22Z`. Today **2026-08-11** is after that instant (age > 7 d). The two security check-runs were created `2026-08-11T22:45:18Z`.
- **Machine gate PASS on the reviewed head** (`gh api …/commits/c032dfe/check-runs`, all 33 = success):
  - `web-dependency-security (audit + committed-lock age gate + npm CLI advisory)` = **success**, `head_sha=c032dfe…04a6cd`, run 31543741054 job 93951659768 (also run 31543737246 job 93951647965).
  - `web tree re-audit (blocking on any finding / too-new / outage)` = **success**, `head_sha=c032dfe…04a6cd`, run 31543741030 job 93951659800.
- **CI ran on the reviewed head:** `gh pr view 220 --json headRefOid` = `c032dfe54bc2c947d1b86b7f87988d658a04a6cd`.
- **Age rule NOT bypassed / NO waiver:** `apps/web/scripts/dependency_age_gate.mjs` is fail-closed — "no allowlist/exception" (lines 19/27), `MIN_AGE_SECONDS = 604_800` (line 46), `if (ageSeconds >= MIN_AGE_SECONDS)` (line 231). No waiver file exists under `apps/web`; `apps/web/package.json` carries only the exact-pin override `"nanoid": "3.3.17"` with no exception key.

## 3. D-010-R246 — "do not touch the M0-T047 nanoid age gate; separate task, existing date/policy" → **SATISFIED (PASS)**

- **Diff scope** (`git diff --name-only c032dfe^ c032dfe`): `apps/web/package.json`, `apps/web/package-lock.json`, `project-control/reports/M0-T047-producer-report.md`. **No** `.github/workflows/*`, **no** `apps/web/scripts/dependency_age_gate.mjs`, **no** `docs/DEPENDENCY_SECURITY_POLICY.md`. The third file is the producer report — an `allowed_paths` artifact (M0-T047.json line 26), not a gate/policy/workflow file — so R246's subject (the age gate / dependency policy) is untouched.
- **Byte-identical to #219 tip 7ac2f91** (`git rev-parse <sha>:<path>`):
  - `c032dfe:apps/web/package.json` = `90e801ae…` == `7ac2f91:apps/web/package.json` = `90e801ae…`
  - `c032dfe:apps/web/package-lock.json` = `6e75bff6…` == `7ac2f91:apps/web/package-lock.json` = `6e75bff6…`
- **Nanoid-only change:** package.json adds exact-pin override `"nanoid":"3.3.17"`; lock `node_modules/nanoid` `3.3.16 → 3.3.17` (`resolved` registry.npmjs.org, `integrity sha512-xQLf0A3HOMlg…`). No other locked version changed.
- **Gate ran through its EXISTING unchanged path and passed** (same check-runs as R233).

## 4. D-009 empty row → verification-completeness only

`accept()` fail-closes when a **cited** directive has no `task_verification` row, independent of applicability. D-009 is cited (`ALL`) but its applicable subset is empty, so an empty-set row is required (precedent: D-001 M0-T057, D-010 M0-T060). No D-009 requirement is verified as satisfied here because none is applicable.

## Prohibited-action check
PR #220 `state=OPEN`, `mergeStateStatus=CLEAN`, task status `awaiting_gate` (progress 85). Nothing merged/accepted/deployed for M0-T047 at review time.

## Per-requirement ledger
| Req ID | Verdict | Primary evidence |
|---|---|---|
| D-010-R233 | **SATISFIED** | web-dependency-security + web tree re-audit = success on c032dfe (created 2026-08-11T22:45:18Z, past 2026-08-10T10:39:22Z eligibility); fail-closed gate, no waiver |
| D-010-R246 | **SATISFIED** | diff = 2 apps/web files (nanoid-only) + producer report; blobs byte-identical to 7ac2f91; no workflow/gate/policy file touched |
| D-009 (applicable subset) | **EMPTY / N/A** | all 21 D-009 rows scope to M0-T019; `matches=False`; resolver-derived subset empty |

(The two verification rows the verifier produced are applied to D-009's and D-010's `verification.json`, with `reviewed_manifest_sha256` filled to the G3/G5 gate manifest `c57ae9c9…`.)

VERDICT: PASS
