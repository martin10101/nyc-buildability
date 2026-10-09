<!-- Verifier return preserved by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &gt; -> >, &lt; -> <).
Verifier: independent directive-compliance-verifier subagent, returned 2026-09-12 (UTC).
NOTE: the row JSON this report references was returned anchored at reviewed_sha 0f92a5f0 and is
NOT yet written into the directive verification.json - acceptance is blocked by the non-directive
dependency condition in section 4, pending an owner decision on the dependency correction; the row
will be re-anchored by the same independent verifier before accept. -->

# M4-T010 Directive-Compliance Verification (DCV) — D-038

- Task: M4-T010 (rule-citation content-digest binding: schema + loader)
- Directive under review: D-038 (build-product-not-self), cited "D-038:ALL"
- Repo: C:/Users/MLFLL/Downloads/nyc-zoning/ctl24
- Branch: candidate/D-024-mrl-option-b
- HEAD at verification: 0f92a5f0317d19e449d255859e9c056e3ded8ba0 (confirmed; still HEAD at finish)
- Verifier: directive-compliance-verifier (independent; NOT the producer, NOT any gate reviewer)
- Discipline: read-only. Wrote no file; ran no pytest/ruff; ran no project_control.py/git/gh write verbs.
  All probes were `python -c` reads with PYTHONDONTWRITEBYTECODE=1 and read-only git/gh.

## VERDICT
- DIRECTIVE (D-038): PASS — RULING: ROW-SUFFICES (no owner amendment). Empty-applicable row required and correct.
- ACCEPT PRECONDITION (non-directive): NOT SATISFIED — dependency M4-T001 is awaiting_gate, not accepted.
  accept() will fail until M4-T001 is accepted; this row does not and cannot resolve that.

## 1. Validator + HEAD
- `python tools/validate_directive_compliance.py --check` -> EXIT 0, no file output.
- HEAD = 0f92a5f0 (as coordinator stated), branch candidate/D-024-mrl-option-b, tree clean
  (only untracked scratchpad/ and .claude/agent-memory/qa-engineer/).

## 2. Applicable set for M4-T010 — three ways -> EMPTY
- (a) requirements.json: R001/R002/R005/R006/R007 -> task_ids ["D-038-BOOTSTRAP"]; R003/R004 -> task_ids
      ["M5-T003".."M5-T013"] (exclude M4-T010). Conjunction semantics: none match.
- (b) reg.derive_applicable(task) over all 36 active directives -> applicable=[], unresolved=[].
- (c) reg.evaluate_task_refs(task) -> ok=True, applicable_ids=[], cited_ids=[], missing_ids=[],
      invalid_refs=[], unresolved=[], reasons=[]. Selective-citation guard clear.

## 3. Ruling (from the code)
- pc._directive_accept_reasons(t,"M4-T010") -> exactly ["D-038/M4-T010: no task_verification row (fail closed)"],
  deferrals=[]. _v2_task_unresolved requires one row per cited directive even when applicable is empty.
- Variant A simulation (empty applicable_requirement_ids + empty requirements, producer!=verifier,
  reviewed_manifest_sha256=9a232939, reviewed_sha=0f92a5f0) -> reasons [] (clears the directive portion).
  The M2-T021 proofs that a R003/R004-populated row FAILS and a wrong reviewed_sha FAILS carry over.

## 4. FULL accept() precondition reproduction (read-only)
Returned two reasons BEFORE writing the row:
  - dependency M4-T001 is 'awaiting_gate', not accepted   <-- non-directive ledger gate; STILL BLOCKS accept
  - D-038/M4-T010: no task_verification row (fail closed) <-- cleared by the row above
M4-T001: status awaiting_gate, accepted_at null. The orchestrator must accept M4-T001 before M4-T010.

## 5. Content identity (recomputed)
- pc._task_git_identity(reg_mod, t) -> identity 9a232939d734a8876d2edab7afca24bcbcd6d05d274ff0634e9204811ab67f85,
  resolved_sha 0f92a5f0317d19e449d255859e9c056e3ded8ba0, error=None (require_clean passed).
- Machine report project-control/reports/M4-T010.json content_manifest_sha256 = 9a232939 (matches);
  applicable_requirements = []. Evidence map M4-T010-evidence-map.json requirements = {} (consistent).

## 6. Gate records (primary evidence)
- G0: PASS, administrative, orchestrator, reviewed_sha db013b52 (packet/base).
- G1: PASS, independent_review, code-reviewer, reviewed_sha ce7a96cb.
- G3: PASS, independent_review, data-contract-verifier, reviewed_sha ce7a96cb.
- G4: PASS, independent_review, qa-engineer, reviewed_sha ce7a96cb.
- Producer = rules-engineer/orchestrator; all three reviewers distinct from producer. Wave 3-0, no rework.
- required_gates = G0/G1/G3/G4 (no G5 for this packet) — all satisfied.

## 7. Reviewed content byte-identical to HEAD
- git diff over the reviewable allowed_paths is EMPTY for both 7bac23c1..HEAD and ce7a96cb..HEAD.
- Last reviewable change = producer commit 7bac23c1. Later commits (79734f11 evidence map, 79f06fde submit,
  39f8e75c G0 record, ce7a96cb gate reports, 0f92a5f0 gate recordings+ledger) are control-plane only.
  Gates retain reviewed_sha ce7a96cb; this row anchors HEAD (identity proves byte-identity).

## 8. Task arc + red/green (reproduced)
- Contracted at G0 base db013b52 -> producer material 7bac23c1 (4 files, all inside exact-file allowed_paths;
  schema +3 additive optional citations[].content_digest_sha256, dsl.py +14 fail-closed _check_refs compare,
  new test module 148 lines, producer report; engine.py + rulesets/** untouched per S6) -> G1/G3/G4 PASS 3-0.
- Anti-vacuity confirmed in the test itself: S3 uses a mismatch-SPECIFIC regex
  (r"records content_digest_sha256 .* but the snapshot on disk stores"), so a schema-shape rejection cannot
  satisfy it; S1 loads every committed rule unchanged (additive back-compat); S2 recomputes
  sha256(verbatim_excerpt) from the snapshot (no literal restatement); S4 schema-rejects malformed digests;
  S5 preserves SnapshotError precedence.

## 9. R003/R004 substance (voluntary — neither machine-applicable)
- R003: product/rule-engineering, zero self-infra paths across the producer commit.
- R004: fully offline, no Supabase/Geoclient, no credentials (hashlib digest comparison; test imports only
  app.rules.dsl + hashlib; no network/socket/requests/httpx).

## 10. Prohibited-action evidence
- Task status awaiting_gate; accepted_by/accepted_at null (NOT accepted).
- No open PR for this work (gh returns only stale 2026-07 M4-footprint control PRs, CLOSED/MERGED, unrelated).
- 7bac23c1 NOT an ancestor of origin/main (NO merge). origin/candidate at 39f8e75c: commits ce7a96cb/0f92a5f0 UNPUSHED.

## Requirement-by-requirement ledger (D-038, all 7)
- D-038-R001/R002/R005/R006/R007 — NOT APPLICABLE (task_ids=[D-038-BOOTSTRAP]); not in row.
- D-038-R003 — NOT APPLICABLE (task_ids M5-T003..M5-T013 exclude M4-T010); substance SATISFIED voluntarily (note only).
- D-038-R004 — NOT APPLICABLE (same); substance SATISFIED voluntarily (offline, no creds; note only).
Machine-applicable set = {} -> row applicable_requirement_ids = [], requirements = [].

## Instruction to orchestrator
1. Append the row above verbatim to project-control/directives/D-038-build-product-not-self/verification.json
   (task_verifications[]) and preserve this report at project-control/reports/M4-T010-directive-verification.md.
2. Do NOT run accept M4-T010 yet: it will fail on 'dependency M4-T001 is awaiting_gate, not accepted'.
   Accept M4-T001 first (through its own gates/DCV), then accept M4-T010.
3. Do NOT populate R003/R004 into the row — a populated row provably fails accept() (extra/cross-task rows).
