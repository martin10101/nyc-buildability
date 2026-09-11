<!-- Verifier return preserved by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &gt; -> >, &lt; -> <).
Verifier: independent directive-compliance-verifier subagent, returned 2026-09-11. -->

# M2-T021 Directive-Compliance Verification (DCV) — D-038

- Task: M2-T021 (Geoclient v2 address-resolution connector)
- Directive under review: D-038 (build-product-not-self), cited "D-038:ALL"
- Repo: C:/Users/MLFLL/Downloads/nyc-zoning/ctl24
- Branch: candidate/D-024-mrl-option-b
- HEAD at verification: 8a2d28269dbf1d29ac51e663cdb3a9efd2580fcd (confirmed unchanged; still HEAD at finish)
- Verifier: directive-compliance-verifier (independent; NOT the producer, NOT any gate reviewer)
- Discipline: read-only. Wrote no file; ran no pytest/ruff; ran no project_control.py/git/gh write verbs.
  All probes were `python -c` reads with PYTHONDONTWRITEBYTECODE=1 and read-only git/gh.

## VERDICT: PASS — RULING: ROW-SUFFICES (no owner-gated amendment required)

## 1. Validator (read-only)
`python tools/validate_directive_compliance.py --check` -> EXIT 0, twice, no file output.

## 2. Applicable-requirement set for M2-T021 — derived three independent ways -> EMPTY
- (a) requirements.json applicability blocks, read directly:
  - R001/R002/R005/R006/R007 -> applicability.task_ids = ["D-038-BOOTSTRAP"] (sentinel; not M2-T021)
  - R003/R004 -> applicability.task_ids = ["M5-T003".."M5-T013"] (does NOT include M2-T021)
  - Conjunction semantics (_applicability_matches): a non-empty task_ids excluding the task => no match. None apply.
- (b) reg.derive_applicable(task) across ALL 36 active directives -> applicable=[], unresolved=[].
- (c) reg.evaluate_task_refs(task) -> ok=True, applicable_ids=[], cited_ids=[], missing_ids=[],
      invalid_refs=[], unresolved=[], reasons=[]. Selective-citation guard satisfied; no un-cited
      applicable directive anywhere in the registry.

## 3. Applicability ruling (based on what accept() actually validates)
- pc._directive_accept_reasons(t,"M2-T021") currently returns exactly:
    ["D-038/M2-T021: no task_verification row (fail closed)"], deferrals=[].
- Reading the code: even with an empty applicable set, accept() iterates the cited directives and
  calls reg.task_verification_result("D-038","M2-T021", <empty>, identity, reviewed_sha). In
  _v2_task_unresolved, absence of a task row is a fail-closed reason. So exactly one row is required.
- In-memory simulation (no writes) against reg.task_verification_result:
    * Variant A — applicable_requirement_ids [] + requirements []  -> reasons [] (ACCEPT-CLEARS).
    * Variant B — R003/R004 populated                              -> FAIL: "non-applicable
      (extra/cross-task) rows: D-038-R003, D-038-R004" + "recorded applicable_requirement_ids
      do not equal the derived applicable set".
    * Variant C — empty row, wrong reviewed_sha                    -> FAIL: reviewed_sha stale
      (negative control confirms the check is real).
- Conclusion: an EMPTY-applicable row suffices and is the ONLY correct shape. The G3 gate's
  "reconcile via an owner-gated amendment" is a recommendation about substantive R003/R004 coverage,
  not a machine precondition. Binding M2-T021 into R003/R004 task_ids would require an owner amendment
  AND would re-impose full PASS rows — neither required nor proposed here (registry is evidence the CLI
  consumes, not a second lifecycle authority).

## 4. Content identity (recomputed by the verifier)
- pc._task_git_identity(reg_mod, t) -> identity e4c61cfd35e5eeff7f3a46c7e611943325da6701316f7a3b438b427381f871a1,
  resolved_sha 8a2d28269dbf1d29ac51e663cdb3a9efd2580fcd, error=None (require_clean passed).
- _task_git_identity fails closed unless reviewed_sha==HEAD (confirmed by attempting 2fd10488 -> refused).
- Machine report project-control/reports/M2-T021.json already carries content_manifest_sha256 = e4c61cfd
  (so accept()'s frozen-evidence check passes) and applicable_requirements = [].

## 5. Gate records (primary evidence)
- G0: PASS, administrative, reviewer orchestrator, reviewed_sha acf54c63.
- G1: PASS, independent_review, reviewer code-reviewer, reviewed_sha 2fd10488.
- G3: PASS, independent_review, reviewer data-contract-verifier, reviewed_sha 2fd10488.
- G4: PASS, independent_review, reviewer qa-engineer, reviewed_sha 2fd10488.
- G5: PASS, independent_review, reviewer security-reviewer, reviewed_sha 2fd10488.
- Producer = backend-engineer/orchestrator; all four independent reviewers distinct from producer.

## 6. Reviewed content byte-identical to HEAD
- git diff over reviewable allowed_paths is EMPTY for both 2fd10488..HEAD and 01c01c5f..HEAD.
- Last reviewable change = round-2 producer commit 01c01c5f. Every later commit
  (96c398aa resubmit, 2fd10488 delta reports, b5d2470e gate recordings, 8a2d2826 ledger) is
  control-plane only. Gates retain reviewed_sha 2fd10488 (what reviewers read); this row anchors
  HEAD, and identity e4c61cfd proves byte-identity (M5-T004 precedent).

## 7. Round-2 arc (reproduced from git + gate reports)
dc227c0a producer output (6 files, all allowed_paths, zero self-infra)
  -> gate wave d4cdbe79 FAIL 2-2 (G1 FAIL, G4 FAIL; G3 PASS, G5 PASS)
  -> rework eb6a15f8 (one bounded change; also 3 orchestrator record files outside allowed_paths — see errors)
  -> re-review PASS 4-0 with BLOCKING corrections (M2-T021-G{1,3,4,5}-rereview.md)
  -> round-2 split: producer material 01c01c5f + orchestrator records 7a43d2d0
  -> delta re-review PASS 4-0, zero blocking (M2-T021-G{1,3,4,5}-delta.md at 96c398aa/2fd10488).

## 8. R003/R004 substance (voluntary — neither is machine-applicable)
- R003: producer commits dc227c0a/eb6a15f8/01c01c5f touch ZERO files under tools/, .claude/,
  supabase/, packages/, render.yaml, .github/ — genuine product engineering (address-entry foundation).
- R004: verification is fully offline — socket-blocking _no_network fixture + injected transport seam
  + recorded fixtures G01/G02/G03; connector imports no requests/httpx/supabase/psycopg; key read from
  os.environ at call time, header-only. R004's "no live Geoclient" scoped to the 2026-09-08 session
  before the owner supplied the key; its computed applicability to M2-T021 is empty.

## 9. Prohibited-action evidence
- Task status awaiting_gate; accepted_by/accepted_at null (NOT accepted).
- No PR (gh pr list --search M2-T021 empty).
- dc227c0a NOT an ancestor of origin/main == local main d8b3899f (NO merge to main).
- origin/candidate/D-024-mrl-option-b at 96c398aa: gate/ledger commits 2fd10488/b5d2470e/8a2d2826 UNPUSHED.

## 10. Orchestrator errors self-reported (recorded so they are not inherited)
- (1) eb6a15f8 additionally wrote three record files outside allowed_paths (docs/MVP_AGENDA.md,
  project-control/blockers/B-004-geoclient-subscription-key.json,
  project-control/reports/M2-T021-evidence-map.json) — ruled ADR-005 record-authority writes,
  pre-announced in the 430773eb progress_log; corrective practice from round 2 separated producer
  (01c01c5f) and record (7a43d2d0) commits.
- (2) The evidence map struck four G3 overstatements and, in round 2, one further ZERO-files
  over-widening plus an integrity-test undercount (per its own _correction_record). None affect the row.

## 11. Non-gating observation
- services/api/app/connectors/geoclient_address.py is ~758 raw lines; modularity is a G1/CI concern
  (G1 PASSED) and not a D-038 requirement.

## Requirement-by-requirement ledger (D-038, all 7)
- D-038-R001 — NOT APPLICABLE to M2-T021 (task_ids=[D-038-BOOTSTRAP]); not in row.
- D-038-R002 — NOT APPLICABLE (task_ids=[D-038-BOOTSTRAP]); not in row.
- D-038-R003 — NOT APPLICABLE (task_ids M5-T003..M5-T013 exclude M2-T021); substance verified SATISFIED
  voluntarily (product, zero self-infra) but recorded in note only.
- D-038-R004 — NOT APPLICABLE (same task_ids); substance verified SATISFIED voluntarily (fully offline,
  key hygiene) but recorded in note only.
- D-038-R005 — NOT APPLICABLE (task_ids=[D-038-BOOTSTRAP]); not in row.
- D-038-R006 — NOT APPLICABLE (task_ids=[D-038-BOOTSTRAP]); prohibitions independently confirmed intact
  (no push of acceptance commits, no PR, no merge, not accepted).
- D-038-R007 — NOT APPLICABLE (task_ids=[D-038-BOOTSTRAP]); not in row.

Machine-applicable set for M2-T021 = {} -> the row's applicable_requirement_ids = [], requirements = [].

## Instruction to orchestrator
Append the row above verbatim to
project-control/directives/D-038-build-product-not-self/verification.json (task_verifications[]),
preserve this report at project-control/reports/M2-T021-directive-verification.md, then run accept.
Do NOT populate R003/R004 into the row — doing so provably fails accept() (extra/cross-task rows).
