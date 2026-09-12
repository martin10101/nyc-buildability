<!-- Verifier return preserved by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &gt; -> >).
Verifier: independent directive-compliance-verifier subagent, returned 2026-09-12 (UTC). -->

# M5-T014 Directive-Compliance Verification (DCV) — D-038

- Task: M5-T014 (compare-screen empty-from assertion repair; test-only)
- Directive: D-038 (build-product-not-self), cited "D-038:ALL"
- Repo: C:/Users/MLFLL/Downloads/nyc-zoning/ctl24, branch candidate/D-024-mrl-option-b
- HEAD at verification: 0b392c1a43eace559c3aff33ef209162c1070e56 (confirmed; stable at finish)
- Verifier: directive-compliance-verifier (independent; NOT producer, NOT any gate reviewer)
- Discipline: read-only. Wrote no file; ran no pytest/ruff/vitest; no project_control.py/git/gh write verbs.

## VERDICT: PASS — RULING: ROW-SUFFICES (empty-applicable row; no owner amendment)

## 1. Validator: validate_directive_compliance --check EXIT 0. reg.errors=[].

## 2. Applicable set = EMPTY (three ways)
- requirements.json: R003/R004 task_ids M5-T003..M5-T013 exclude M5-T014; R001/R002/R005/R006/R007 -> sentinel.
- reg.derive_applicable() -> [] unresolved [].
- reg.evaluate_task_refs() -> ok=True, applicable_ids=[], cited=[], missing=[], invalid=[], unresolved=[].

## 3. Ruling / accept preconditions
- FULL accept() reproduction returned EXACTLY ['D-038/M5-T014: no task_verification row (fail closed)'],
  no deferrals; dependencies=[] (no dependency reason); all gates PASS.
- Variant-A empty-applicable row at identity 289f71ec / reviewed_sha 0b392c1a -> reasons []. A
  R003/R004-populated row would fail (extra/cross-task).

## 4. Content identity
- pc._task_git_identity -> identity 289f71ec..., resolved_sha 0b392c1a, err=None (require_clean passed).
- Machine report M5-T014.json content_manifest_sha256 = 289f71ec (MATCH); applicable_requirements [].

## 5. Gates (primary records)
- G0 PASS admin (orchestrator, packet commit 4d529f50).
- G1 PASS independent_review (code-reviewer) + G4 PASS independent_review (qa-engineer), both at effb2146.
- G4 reviewer-role overlap pre-answered (M4-T011 precedent): producer is orchestrator-executed
  qa-engineer/orchestrator; G4 reviewer is a separate independent qa-engineer subagent; literal
  reviewer!=producer check passes; not a D-038 matter.

## 6. Byte-identity
- diff over the two allowed_paths (compare-screen.test.tsx, M5-T014-producer-report.md) is EMPTY
  31d3683e..HEAD. Last reviewable change = 31d3683e; later commits (f5a30e51 submit, effb2146 gate
  recordings, 0b392c1a ledger) are control-plane only.

## 7. Arc + repair substance (read from the +8 diff)
- contracted 4d529f50 (G0 admin) -> producer material 31d3683e (2 files, test-file +8/-0 + report;
  zero self-infra, zero app/component code) -> submit f5a30e51 -> wave G1/G4 PASS 2-0.
- The repair sets rules[0].effective_to = rules[1].effective_from (a real end date DERIVED from a sibling
  fixture, never an invented literal) so a blanked effective_from renders through the per-slot empty-FROM
  label branch instead of the both-absent collapse; the component's accepted both-absent design is
  untouched. This fixes the assertion that had failed on every web-e2e run since M5-T004.

## 8. CI-only verification posture
- Thin client (apps/web/node_modules absent per LOW_STORAGE policy): no local frontend test run.
- RED externally recorded (web-e2e failing since M5-T004); GREEN captured as committed evidence at
  project-control/reports/M5-T014-ci-evidence.txt: run 34673373030, job web-e2e conclusion=success,
  completedAt 2026-09-12T04:38:06Z, first green since M5-T004; only the two owner-gated reds remain; api
  and exact-production-install green. CI is the authority; no local green claimed.

## 9. Substance (voluntary; neither R003/R004 machine-applicable)
- R003: product test-quality repair (Compare Step-3 provenance assertion), zero self-infra, test-only.
- R004: offline vitest/Playwright vs recorded-official fixtures; no Supabase/Geoclient.

## 10. Prohibited-action evidence
- status awaiting_gate, accepted_by null (NOT accepted); 31d3683e not an ancestor of origin/main (no
  merge); origin/candidate at f5a30e51 so effb2146/0b392c1a UNPUSHED; no open PR.

## Requirement ledger (D-038, all 7)
- R001/R002/R005/R006/R007 NOT APPLICABLE (sentinel D-038-BOOTSTRAP).
- R003 NOT APPLICABLE (M5-T003..M5-T013 exclude M5-T014); substance SATISFIED voluntarily (note only).
- R004 NOT APPLICABLE (same); substance SATISFIED voluntarily (note only).
- Machine-applicable set = {} -> row applicable_requirement_ids = [], requirements = [].

## Instruction to orchestrator
Append the row to D-038 verification.json (task_verifications[]) and this report to
project-control/reports/M5-T014-directive-verification.md; then run accept M5-T014 (sole remaining accept
reason is the row). Do NOT populate R003/R004 into the row.
