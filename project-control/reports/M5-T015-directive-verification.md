<!-- Verifier return preserved by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &gt; -> >, &lt; -> <).
Verifier: independent directive-compliance-verifier subagent, returned 2026-09-12 (UTC). -->

# M5-T015 Directive-Compliance Verification (DCV) — D-038

- Task: M5-T015 (address-entry UI, form + resolution outcomes + full error matrix; design-spec Packet 1)
- Directive: D-038 (build-product-not-self), cited "D-038:ALL", regime 1.0
- Repo: C:/Users/MLFLL/Downloads/nyc-zoning/ctl24, branch candidate/D-024-mrl-option-b
- HEAD at verification: e989db844694a0fbdb8c149232c462b919ec912d (git rev-parse HEAD confirmed; stable at finish)
- Verifier: directive-compliance-verifier (independent; NOT producer frontend-engineer/orchestrator, NOT any of the four gate reviewers)
- Discipline: read-only. Wrote no repository/control-plane file; ran no write verb of project_control.py/git/gh. Reproduced evidence via git reads, validate_directive_compliance.py --check, and read-only imports of tools modules.

## VERDICT: PASS — RULING: ROW-SUFFICES (empty-applicable row; no owner amendment)

## 1. Validator + registry integrity
- `python tools/validate_directive_compliance.py --check` EXIT 0.
- reg.errors = []. D-038 status=active, is_active=True, errors=[].
- 7 requirements, all in locked_requirement_ids. Single source: source-001.md, content_digest a237dd50…; NO amendment files present -> no amendment to reconcile.

## 2. Intake matrix (source-001.md vs requirements.json) — faithful
- R001 <- "nonstop" (loop liveness/watcher/D-035 restart; explicitly "not weakened"). R002 <- "no more building itself" (prohibition on self-infra as build target; M0-T155 not the target). R003 <- Q2 "Unblocked product engineering" (positive product deliverable, G0 packet). R004 <- Q1 "Not right now" (no Supabase/Geoclient; fixtures/public connectors only). R005 <- credential carry-forward (decision, non-binding). R006 <- no-bypass reaffirmation of standing holds. R007 <- return report.
- No requirement is missing, weakened, or combines two materially different source obligations. R006 restates existing standing prohibitions/holds (a preservation/no-bypass clause anchored to source-001.md#verbatim) rather than inventing a new obligation, and softens nothing. Matrix judged faithful. (This intake result does not affect the M5-T015 verdict, because the applicable set for this task is empty — §3.)

## 3. Applicable set = EMPTY (proven three independent ways)
- (a) requirements.json bindings, read directly: R001/R002/R005/R006/R007 applicability.task_ids = ["D-038-BOOTSTRAP"] (non-ledger sentinel); R003/R004 applicability.task_ids = M5-T003..M5-T013 (EXCLUDE M5-T015). Every requirement has empty task_types/milestones/paths — no fallthrough binding on a frontend/M5 task.
- (b) reg.derive_applicable(M5-T015) -> applicable=[], unresolved=[] (whole-registry sweep across all active directives attaches nothing).
- (c) reg.evaluate_task_refs(M5-T015) -> ok=True, applicable_ids=[], cited_ids=[], missing_ids=[], invalid_refs=[], unresolved=[], reasons=[]. Selective-citation guard CLEAR (D-038:ALL expands to the empty applicable subset; no applicable-but-uncited requirement).

## 4. Content identity (shared path)
- pc._task_git_identity(reg_mod, M5-T015) = frozen_git_identity over the 8 exact-file allowed_paths, require_clean=True.
- identity = 0678bb0947d5e24ea60730e1972aabb4444b0e85c542a285cce0fb4dc3f4c877; resolved_sha = e989db84 (== HEAD); err = None (clean).
- MATCHES machine report project-control/reports/M5-T015.json content_manifest_sha256 (0678bb09…, applicable_requirements=[]) AND all four gate records' content_manifest_sha256 (0678bb09…). (Note: the machine report's reviewed_sha field is the submit-time SHA de3195d5; the identity is content-based and is byte-stable to HEAD — see §6.)

## 5. Accept preconditions (full _directive_accept_reasons dry-run)
- Reasons returned (verbatim, count=1): "D-038/M5-T015: no task_verification row (fail closed)".
- Deferrals: none. This row is the SOLE remaining accept precondition (fail-closed as designed).
- Dependency M2-T022 status=accepted (accepted_by=orchestrator, 2026-09-12T03:25:15Z) -> no dependency reason.
- A row populated with R003/R004 would FAIL accept() as extra/cross-task; the empty row is correct.

## 6. Gates + byte-identity of reviewed content
- G0 PASS (orchestrator, administrative, packet 428989b1). G1 PASS code-reviewer; G3 PASS visual-quality-reviewer; G4 PASS qa-engineer; G5 PASS security-reviewer. Each reviewer != producer (frontend-engineer/orchestrator). All four gate JSON records carry content_manifest_sha256 0678bb09 and reviewed_sha b1db3360.
- Delta attestations (preserved verbatim in M5-T015-G1/G3/G4/G5.md) at corrected head 9edfbc73 are all PASS: G3 F1 heading order VERIFIED CLOSED, F2 pick-focus + F3 invalid_input edit affordance VERIFIED; G1 D1 (rawStreetName wording), D2 (754-char raw-vs-bounded discriminating fixture), D3 (stats) resolved; G4/G5 hold PASS.
- Byte-identity: git diff 9edfbc73..e989db84 over the 8 allowed_paths is EMPTY. Files changed after 9edfbc73 are control-plane only (gate JSONs, gate reports, ci-evidence.txt, M5-T015.json, state.json, task JSON). The reviewed work-product is byte-identical from the last producer commit to HEAD.

## 7. Arc + CI evidence
- Arc (git + preserved reports): contract 428989b1 -> G0/claim b646dc0d -> producer material 352aa9de -> progress 6097c8cb -> test-module repair 6787445e -> submit-evidence faeaf37c / submit record 9f679ff7 -> gate wave 3b96a2cd (G3 required correction) -> wave outcome cadfc4c8 -> correction wave 9edfbc73 -> delta attestations b1db3360 -> gate records de3195d5 -> rework-resubmit restamp e989db84 (HEAD).
- CI (thin-client authority) run 34677835271 at 9edfbc73: web (lint+typecheck+build) SUCCESS; web-e2e (vitest+Playwright vs recorded-shaped fixtures) SUCCESS; address-resolution.test.tsx 32 tests PASSED; Test Files 27 passed (27). Only reds are the two pre-existing owner-gated jobs (web-dependency-security, control-plane). Satisfies G1's fresh-CI execution caveat at the corrected head.

## 8. Voluntary substance (NOT machine-applicable; note-only)
- R003 (product-only): the deliverable is genuine user-facing product engineering (address-entry UI Packet 1: AddressForm, AddressResolutionScreen, SuggestionChooser, address-api.ts, additive announce.ts, flag-gated PropertyLookup mount) — zero self-infra / M0 tooling.
- R004 (no cloud creds): builds and verifies offline — fetch stubbed over recorded-response-shaped fixtures, no Supabase, no live Geoclient; package.json/package-lock.json untouched.

## 9. Prohibited-action evidence
- status=awaiting_gate; accepted_by=null (NOT accepted).
- e989db84 is NOT an ancestor of origin/main (d8b3899f) — no merge to main.
- origin/candidate/D-024-mrl-option-b is at de3195d5 -> HEAD e989db84 is UNPUSHED.
- No merged/accepted/dispatched/deployed/installed/purchased/closed action observed. gh not run (read-only); git evidence is consistent with no task PR — orchestrator to confirm PR-state.

## Requirement ledger (D-038, all 7 individually)
- D-038-R001 — NOT APPLICABLE to M5-T015 (binds sentinel D-038-BOOTSTRAP). Evidence: requirements.json applicability.task_ids=["D-038-BOOTSTRAP"]; not in derive_applicable(M5-T015).
- D-038-R002 — NOT APPLICABLE (binds sentinel D-038-BOOTSTRAP). Same evidence.
- D-038-R003 — NOT APPLICABLE (task_ids M5-T003..M5-T013 exclude M5-T015; empty task_types/milestones/paths). Voluntary substance SATISFIED (note only).
- D-038-R004 — NOT APPLICABLE (same binding). Voluntary substance SATISFIED (note only).
- D-038-R005 — NOT APPLICABLE (binds sentinel; non-binding decision).
- D-038-R006 — NOT APPLICABLE (binds sentinel).
- D-038-R007 — NOT APPLICABLE (binds sentinel).
- Machine-applicable set = {} -> row applicable_requirement_ids=[], requirements=[].

## Instruction to orchestrator
Append the empty-applicable row (§ROW) to D-038 verification.json task_verifications[] and this report to project-control/reports/M5-T015-directive-verification.md; then accept M5-T015 (the sole remaining accept reason is this missing verification row). Do NOT populate R003/R004 into the row — a populated row would fail accept() as cross-task.

## Orchestrator PR-state confirmation (appended by the orchestrator)
The verifier could not run gh (read-only discipline). Orchestrator confirms: no PR exists for M5-T015;
the only standing PR posture is unchanged (PR #241 remains open and MUST NOT be merged, unrelated to
this task). This closes the verifier's one flagged confirmation item.
