<!-- Verifier return preserved by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &gt; -> >, &amp; -> &).
Verifier: independent directive-compliance-verifier subagent, returned 2026-09-12 (UTC).
ORCHESTRATOR EXECUTION NOTE: both Warning-A repairs were executed BEFORE the accepts (D-039
sentinel row removed per c5; scope.task_ids emptied per c15; validator EXIT 0 re-confirmed) and
Warning B was answered on the record in M4-T011's progress_log (the G4 review was a separate
independent qa-engineer subagent invocation, distinct from the orchestrator-executed production). -->

# M4-T009 + M4-T011 Directive-Compliance Verification (DCV) — D-038

- Repo: C:/Users/MLFLL/Downloads/nyc-zoning/ctl24, branch candidate/D-024-mrl-option-b
- HEAD at verification: b45f9d0b2721e67c970898e18bd3a43dec752727 (confirmed; stable at finish)
- Verifier: directive-compliance-verifier (independent; NOT producer, NOT any gate reviewer)
- Discipline: read-only. Wrote no file; ran no pytest/ruff; no project_control.py/git/gh write verbs.

## VERDICT
- M4-T009 (D-038): PASS — RULING ROW-SUFFICES (empty-applicable row).
- M4-T011 (D-038): PASS — RULING ROW-SUFFICES (empty-applicable row).
- TWO WARNINGS below (registry invalidity from D-039; M4-T011 G4 role collision) — neither blocks
  these two accepts, but both need the orchestrator's attention.

## Shared mechanics (both tasks)
- Applicable set EMPTY, three ways: requirements.json applicability (R003/R004 task_ids M5-only,
  R001/R002/R005/R006/R007 -> sentinel D-038-BOOTSTRAP); reg.derive_applicable() over 36 active
  directives = [] unresolved []; reg.evaluate_task_refs() ok=True, missing=[] (no selective citation).
- _directive_accept_reasons returns EXACTLY 'no task_verification row (fail closed)' for each; no
  deferrals; no dependency reason (both dependencies=[] via D-039). Variant-A empty-applicable row
  clears the directive portion (reasons []) for both.
- Machine reports content_manifest_sha256 already match the recomputed identities (frozen-evidence OK).

## M4-T009
- Identity b3dc14fb (recomputed, err=None), reviewed_sha b45f9d0b. Cites D-038:['D-038-R003'] but R003
  is not applicable, so the row is empty-applicable (over-citation is permitted; the row's
  applicable_requirement_ids must equal the DERIVED [] set, not the cited set).
- Gates: G0 PASS admin (orchestrator, 17e8eb78); G1/G3/G4/G5 PASS independent_review at 3058fa0c by
  code-reviewer/data-contract-verifier/qa-engineer/security-reviewer, all != producer backend-engineer.
- Byte-identity: diff over rulesets/**, tests/rules/**, M4-T009-producer-report.md is EMPTY 317df044..HEAD.
- Arc: AS-5 unit - 5 family rules record citation content_digest_sha256 (consuming M4-T010 schema/loader)
  + R1-R12 provenance test; producer commit 317df044 (7 files, all allowed_paths, zero self-infra,
  engine.py untouched). CI at 032dffe7 then surfaced 6 api test failures (single-member family selection;
  production correct) -> repaired as M4-T011.
- Substance (voluntary): R003 product rule-engineering; R004 fully offline (rule JSON + fixture tests).
- Prohibited: awaiting_gate/not accepted; 317df044 not on origin/main (no merge); 3058fa0c/b45f9d0b unpushed.

## M4-T011
- Identity 2cbb4bb2 (recomputed, err=None), reviewed_sha b45f9d0b. Cites D-038:ALL -> expands to nothing.
- Gates: G0 PASS admin (orchestrator, 223c69dc); G1 PASS (code-reviewer) + G4 PASS (qa-engineer) at
  3058fa0c (required_gates G0/G1/G4; QA test-repair packet).
- Byte-identity: diff over the four exact-file api test modules + M4-T011-producer-report.md is EMPTY
  40cd4544..HEAD.
- Arc: TEST-ONLY repair of the 6 CI failures (applicable-trace selection in test_evidence_api.py,
  test_rule_evaluation_api.py, test_scenario_analysis_api.py, test_scenario_api.py); production selection
  verified correct; producer commit 40cd4544 (5 files, zero app/ code, zero self-infra); CI GREEN at
  e919d9ec (api + exact-production-install).
- Substance (voluntary): R003 product test-quality repair; R004 fully offline (fixture api tests).
- Prohibited: awaiting_gate/not accepted; 40cd4544 not on origin/main (no merge); commits unpushed; no PR.

## WARNING A — registry currently INVALID (validator EXIT 1), from last session's D-039 writes
  c5  [D-039] D-039-BOOTSTRAP task_verification has malformed task_id
  c15 [D-039] scope includes accepted task M4-T010 that does not cite D-039
- c5: validator (line 160) requires task_verification.task_id to match ^M\d+-T\d{3}(-R\d+)?$; the
  D-039-BOOTSTRAP row returned last session violates this (reg.task_verification_result accepted it, the
  validator does not). FIX: remove the D-039-BOOTSTRAP row from D-039 task_verifications[] (D-038
  precedent: BOOTSTRAP requirements carry no task rows; R001-R005 evidence lives in D-039-verification.md).
- c15: D-039 scope.task_ids=[M4-T010,M4-T009]; M4-T010 accepted and cites D-038 only. FIX: drop accepted
  non-D-039-citing tasks from scope.task_ids (they stay named in title + audit_log).
- These do NOT block M4-T009/M4-T011 (reg.errors/D-038.errors/D-039.errors all empty; c5/c15 are
  validator-computed; neither task cites D-039). But accepting M4-T009 ADDS a second c15 error. Recommend
  repairing D-039 to restore validator EXIT 0 before/with these accepts.

## WARNING B — M4-T011 G4 producer/reviewer role collision
- producer_agent 'qa-engineer/orchestrator'; G4 reviewer 'qa-engineer'; packet reviewer_agents include
  'qa-engineer'. accept()'s literal check passes (strings differ) and this does not affect the D-038 row,
  but the qa-engineer role both produced and reviewed the G4 testing gate. Confirm the G4 reviewer was a
  distinct invocation from the producing qa-engineer.

## Item 5 — two accepts at one anchored HEAD: SAFE
accept() commits nothing (save() to task packet + state only), so HEAD stays b45f9d0b for both;
frozen_git_identity require_clean is scoped to each task's own paths (disjoint: M4-T009 rulesets/tests-
rules/report vs M4-T011 four api tests/report), and neither is touched by the other accept or by the
orchestrator's D-038 verification.json/report writes. Write BOTH rows before either accept; each accept
reads the registry fresh and filters rows by task_id. No mechanism refuses the two accepts.

## Instruction to orchestrator
1. (Recommended) Repair D-039 first: remove the D-039-BOOTSTRAP task_verification row (c5) and drop
   accepted tasks from D-039 scope.task_ids (c15); confirm validator EXIT 0.
2. Append both rows above to D-038 verification.json (task_verifications[]) and this report to
   project-control/reports/M4-T009-T011-directive-verification.md.
3. Run accept M4-T009, then accept M4-T011 (both at HEAD b45f9d0b, before any commit), then commit.
4. Do NOT populate R003/R004 into either row (a populated row fails accept()).
5. Confirm M4-T011 G4 reviewer independence (Warning B).
