# M0-T149 DCV — delta re-attestation (rework candidate v2)

**Rework lineage:** frozen candidate v1 `ed04c4bb` → v2 `45b0572c`, merged at HEAD `7804bc03` on candidate/D-024-mrl-option-b, under G3 C1 + G5 MED-1/MED-2 corrections. My v1 PASS bound identity `d6a2e753…` — that identity has now legitimately changed (policy.py + both test files + both producer reports rewritten; evidence.py unchanged), so per my own fail-closed restamp convention I re-verified fully at the new content rather than carrying the prior attestation forward.

**(1) Applicability unchanged — empty set at new content.** `evaluate_task_refs(M0-T149)` at HEAD 7804bc03: `ok=true, applicable_ids=[], cited_ids=[], missing_ids=[], invalid_refs=[], unresolved=[]`. Full sweep of all **32** active directives = **0 matched, 0 all-empty wildcards**. Packet `directive_refs` still `[{D-032: ALL}]`. Registry unchanged (45b0572c touches 0 files under `project-control/directives/`), so D-032's 21 BOOTSTRAP-scoped rows still bind nothing. **SATISFIED.**

**(2) Identity recomputed + byte-stable.** `frozen_git_identity` over the six allowed_paths = `6906f500…8fdb` at candidate `45b0572c` AND at merged HEAD `7804bc03` (require_clean=True at HEAD succeeds — no dirty/untracked material). All six blobs IDENTICAL between 45b0572c and 7804bc03. evidence.py IDENTICAL across the rework (`f7e92476…`, confirming it was untouched); the other five blobs changed vs v1 as expected. **SATISFIED.**

**(3) Resubmission record updated.** `project-control/reports/M0-T149.json` now carries `content_manifest_sha256 = 6906f500…8fdb` (reproduced, matches) and `reviewed_sha = 7804bc03…` with `applicable_requirements=[]`. Evidence-map note updated to record the resubmission at 7804bc03 / rework candidate 45b0572c. **SATISFIED.**

**Supervisor-freeze citation duty (still satisfied):** commit `45b0572c` opens with "Qualifying evidence (supervisor-freeze S2/S3): AD-093 demonstrated security risk - M0-T148 G3 LOW-1 + the G5 gate findings … MED-1/MED-2"; packet objective (unchanged) still cites AD-093. Registry law: 45b0572c changed 5 in-scope files only, nothing under `project-control/directives/`. **SATISFIED.**

*Scope note:* the substance of the G3 C1 / G5 MED-1/MED-2 fixes (completed `_MUTATING_CHECKER_TOKENS`, fail-closed interpreter-flag handling) is code/security correctness graded by the G3 code-reviewer and G5 security-reviewer; this DCV attests only to the D-001/D-032 directive-compliance dimension at the new identity.

## (4) Updated attested D-032 verification.json task row (record verbatim)

```json
{
  "directive_id": "D-032",
  "task_id": "M0-T149",
  "applicable_requirement_ids": [],
  "reviewed_sha": "7804bc03551ae8ddc7b3fa2661150ecac66f1a10",
  "reviewed_manifest_sha256": "6906f5002978d858a312849f67bb58cb6cb1a64d076e7965be7aa5a3d4098fdb",
  "producer": "supervised-loop-fable-worker/orchestrator",
  "verifier": "directive-compliance-verifier",
  "schema_version": "directive_verification/v2",
  "verified_at": "2026-09-07T05:40:00+00:00",
  "note": "EMPTY-SET verification (delta re-attestation at rework candidate v2). M0-T149 cites D-032:ALL, but the shared canonical resolver (directive_registry.evaluate_task_refs / derive_applicable) independently derives ZERO applicable D-032 requirements: all 21 D-032 requirements (incl. Amendment-4 R021) are applicability-scoped to task_ids [D-032-BOOTSTRAP]; none match task_id M0-T149. No selective citation: evaluate_task_refs returns ok=true, applicable_ids=[], cited_ids=[], missing_ids=[], invalid_refs=[], unresolved=[]; a full sweep of all 32 active directives (D-001..D-034, 3623 requirement rows) yields zero requirements matching M0-T149 via its allowed_paths, and D-024's 783 requirements carry zero path/task/type/milestone applicability that reaches this task (D-024 is qualifying evidence via the path-scoped supervisor-freeze rule, not a machine-applicable requirement row). Row exists because accept() fail-closes when a cited directive has no task_verification row (mirrors D-032/M0-T147, M0-T148, M2-T020 empty-set precedents). Verifier != producer (code producer = supervised-loop-fable-worker; this row produced by directive-compliance-verifier). REWORK LINEAGE: frozen candidate v1 ed04c4bb (my prior PASS bound identity d6a2e753...) was reworked to v2 45b0572c under G3 C1 + G5 MED-1/MED-2 (completed _MUTATING_CHECKER_TOKENS and fail-closed interpreter-flag handling in policy.py; +tests); the identity legitimately changed, so this attestation was fully re-derived at the new content rather than carried forward. Supervisor-freeze section 2/3 citation duty satisfied: AD-093 demonstrated security risk (M0-T148 G3 LOW-1) is cited in BOTH the task packet objective and commit 45b0572c (whose message opens with the qualifying-evidence citation plus the G5 MED-1/MED-2 findings). Registry integrity independently reproduced: D-032 active, 0 load errors; validate_directive_compliance.py --check exit 0; registry unchanged (45b0572c touches 0 files under project-control/directives/). Registry law: git diff ed04c4bb 45b0572c --stat changed only 5 in-scope allowed_paths (policy.py, both test files, both producer reports); evidence.py byte-identical across the rework; nothing under project-control/directives/. Reviewed content identity = M0-T149 allowed_paths = 6906f5002978d858a312849f67bb58cb6cb1a64d076e7965be7aa5a3d4098fdb, computed via directive_registry.frozen_git_identity (exclude/control-plane prefix 'project-control/'), byte-identical (identical git object ids for all six blobs) between rework candidate 45b0572c and merged HEAD 7804bc03 -- the reviewed identity is stable, so the mechanical accept-time restamp convention applies (identity stays 6906f500... while allowed_paths blobs are unchanged; if HEAD advances before accept, re-confirm frozen_git_identity still reproduces 6906f500... and stamp reviewed_sha to the accept-time HEAD; fail-closed otherwise). Resubmission record project-control/reports/M0-T149.json carries content_manifest_sha256 6906f500... + reviewed_sha 7804bc03.... G3 (code-reviewer) / G5 (security-reviewer) code and security gate outcomes for the v2 candidate are recorded separately by those reviewers.",
  "requirements": []
}
```

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the directive-compliance-verifier agent-return channel (2026-09-07 delta re-attestation; content unaltered). Supersedes M0-T149-DCV.md's identity binding for acceptance purposes.*
