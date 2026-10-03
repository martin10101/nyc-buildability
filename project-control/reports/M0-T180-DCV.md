# M0-T180 — directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `47baed1f15064f6d9570b46f4160e9da30f6d78f` (branch `task/M0-T180-web-lint-chain-braces`; material head `2ad88408`
is an ancestor; the commits after it touch only `project-control/**`). Applicable requirement: **D-090-R083** only
(`evaluate_task_refs`: ok=True, applicable == cited == ['D-090-R083']).

## Verdict: PASS — D-090-R083 (this task's share: the green-baseline repair) SATISFIED.

## Harness evidence (direct exit codes)
- `python tools/validate_directive_compliance.py --check` (from the worktree) → EXIT=0.
- `python tools/test_project_control.py` → exit 0 (23 groups passed); `python tools/test_directive_reminder.py` → exit 0 (12 tests).
- `tools/test_directive_compliance.py` NOT run (hard limit; CI's job).
- CI `control-plane` success at the material head 2ad88408 (ancestor); in progress at 47baed1f at report time (control-only commits);
  web, web-dependency-security and the web tree re-audit already success at 47baed1f.

## Registry intake
Source digests recompute exactly (source-010 `d2455914…`, source-011 `5694e046…`). R083 applicability.task_ids includes M0-T180;
maps_to.tasks = [M0-T180]; R084–R088 bind only the bootstrap sentinel. manifest + index affected_tasks include M0-T180; audit_log records
the append and the bound-with-digest-resync (c14). verification.json row M0-T180 pending with producer frontend-engineer.

## Material repair (primary artifacts)
package.json: −`@eslint/eslintrc 3.3.6`, −`eslint-config-next 15.5.21`; +`@eslint/js 9.39.5`, +`eslint-plugin-react-hooks 7.1.1`,
+`globals 17.12.0`, +`typescript-eslint 8.70.1`, all exact pins. Lock (397 entries): braces / micromatch / fast-glob /
@next/eslint-plugin-next / eslint-config-next ABSENT; admitted set present at exact versions; `@eslint/eslintrc` remains a dev
transitive only. eslint.config.mjs: native flat config (js recommended + typescript-eslint recommended + react-hooks two rules);
six ignores unchanged. overrides byte-identical (no fork override). Four [ORCH-CORRECTED per S3] one-line behaviour-identical edits;
no config rule disabled; age-gate script untouched. Producer commit touched only config + package.json + the two reports; the lock
came from the workflow bot (4844b56b). `git diff --name-only 15b4d656 47baed1f` minus project-control == the 7 allowed apps/web files;
`.github/`, `render.yaml`, `apps/web/.npmrc` unchanged; ci.yml audit step intact (no --omit=dev, no audit-level change). No policy violation.

## Independent gating
G0/G2/G3/G4/G5 PASS, one content_manifest_sha256 `840e30a01e84a09bcfe834167f7d83b9cf30ff10ea293c45cced9b4abcc3a711`; reviewers
orchestrator (G0/G2), code-reviewer (G3/G4), security-reviewer (G5); producer frontend-engineer ≠ any reviewer. Material byte-stable
from the gated head a1d081f4 to 47baed1f.

## CI
generate-lockfile run 37095335970 success (head 4a783382, bot 4844b56b). All 48 check-runs success at 2ad88408 incl. web, web-e2e,
web-dependency-security, control-plane.

## Prohibited-action evidence
PR #348 OPEN, not merged; task awaiting_gate; verification row pending; B-028 open (M0-T180 only in candidate_followup/needs); no local
npm/npx/node.

## Discrepancies
None material. (`@eslint/eslintrc` "dropped" = as a direct dep; 588 → 397 reproduced; control-plane at the frozen head was still
running — authoritative success at the ancestor material head.)

## Restamp pre-authorization (verbatim)
The orchestrator MAY stamp this PASS onto a later head without re-review provided: any later commit whose diff versus 47baed1f touches
only project-control/** (ledger state, task JSON, verification rows, blocker status, checkpoints, reports) AND leaves every M0-T180
allowed-path blob (the 7 apps/web files) byte-unchanged AND leaves the gate records' content_manifest_sha256 840e30a0… unchanged.
Disjoint peer commits on other lanes are tolerated under the same predicate, so long as 2ad88408 remains an ancestor of the restamp
target and the apps/web allowed-path blobs and the gate content_manifest_sha256 are byte-identical to those verified here.

END-OF-REPORT
