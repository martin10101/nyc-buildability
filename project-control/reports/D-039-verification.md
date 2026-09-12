<!-- Verifier return preserved by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &gt; -> >).
Verifier: independent directive-compliance-verifier subagent, returned 2026-09-12 (UTC). -->

# D-039 Bootstrap Directive-Compliance Verification (DCV)

- Directive: D-039 (m4-dependency-correction), owner decision 2026-09-11 ("Correct both")
- Sentinel task_id: D-039-BOOTSTRAP (all 5 requirements bind it; no per-ledger-task rows accrue)
- Repo: C:/Users/MLFLL/Downloads/nyc-zoning/ctl24, branch candidate/D-024-mrl-option-b
- HEAD at verification: ccc3066725fa5a267468d5f7f8e2ae309ab86e58 (confirmed; still HEAD at finish)
- Verifier: directive-compliance-verifier (independent; producer = orchestrator)
- Discipline: read-only. Wrote no file; ran no pytest/ruff; ran no project_control.py/git/gh write verbs.

## VERDICT: PASS (D-039-R001..R005 all PASS) + capture integrity confirmed

## Identity basis (stated because the sentinel binds no allowed_paths)
- No _task_git_identity content manifest exists for a non-ledger sentinel. Per instruction the identity
  basis is the D-039 directory content digests, and reviewed_manifest_sha256 is the sha256 of the D-039
  requirements.json FILE BYTES = 46d4d36b07af4d7ea76f7feb93703bb952325730adf5a1d50a66a7004d49bb33
  (5753 bytes), which independently EQUALS manifest.requirements_content_digest_sha256 (cross-check).

## Capture integrity
- source-001.md sha256 d8bb8a59df474f725881f1628b00773b311b1a46767084c74c0f228c3c8a3b03
  == manifest.sources[0].content_digest_sha256  -> MATCH.
- requirements.json sha256 46d4d36b... == manifest.requirements_content_digest_sha256 -> MATCH (raw bytes).
- tools/validate_directive_compliance.py --check -> EXIT 0.
- Row shape simulated through reg.task_verification_result(D-039, D-039-BOOTSTRAP, {R001..R005},
  46d4d36b, reviewed_sha=ccc30667) -> reasons []; 4-of-5 negative control failed (extra-row +
  declared!=derived), proving the check is live. NO DEVIATION from the requested shape was required.

## Requirement-by-requirement (verified live against the tree)
- R001 PASS - project-control/tasks/M4-T010.json dependencies == [] (was ['M4-T001']); change in ccc30667.
- R002 PASS - project-control/tasks/M4-T009.json dependencies == []; change in ccc30667.
- R003 PASS - both packets carry one CLI-progress rationale entry (full CLI key-set incl. percent 90 /
  85, agent orchestrator, 2026-09-12T01:04:06Z / 01:04:27Z) naming D-039, the M4-T007/M4-T008 deps=[]
  precedent under owner directive 2026-07-21 (in M4-T001's progress_log), and the untouched G6 hold.
- R004 PASS - sequencing intact: M4-T010 awaiting_gate (not yet accepted), M4-T009 in_progress; NO
  gate/verification shortcut - ccc30667 touches no gate record; M4-T010 gates predate it (G0 @39f8e75c,
  G1/G3/G4 @0f92a5f0) and are unchanged; the D-038 row is re-anchored by the independent verifier.
- R005 PASS - HOLD PRESERVED: M4-T001 awaiting_gate / accepted_at null; all 11 rulesets/*.rule.json
  needs_review; M4-T002..T006 all awaiting_gate, none touched by ccc30667.

## Correction-commit scope (ccc30667, parent 0f92a5f0)
D-039 directory (manifest/requirements/source-001/verification) + index.json +
reports/M4-T010-directive-verification.md + tasks/M4-T009.json + tasks/M4-T010.json ONLY.
No gate records, no source code, no M4-T001/T002-T006 packets, no rulesets.

## Prohibited-action evidence
Nothing accepted (M4-T010 awaiting_gate; M4-T001 never accepted); G6 hold on M4-T001 untouched; no rule
past needs_review; parked M4-T002..T006 queue unchanged.

## Instruction to orchestrator
Append the D-039 row to project-control/directives/D-039-m4-dependency-correction/verification.json
(task_verifications[]) and this report to project-control/reports/D-039-verification.md; append the
re-anchored M4-T010 D-038 row to D-038's verification.json; then run accept M4-T010 (now unblocked -
sole remaining accept reason is the row itself), then commit.
