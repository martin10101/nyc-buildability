# M0-T149 Directive-Compliance Verification (DCV) report

**Task:** M0-T149 — "Constrain supervisor-executed documented test commands to a non-mutating program profile (G3 LOW-1 follow-up to M0-T148)"
**Regime:** D-001; task cites `directive_refs = [{D-032: ALL}]`, `directive_regime_version 1.0`
**Producer of code:** supervised-loop-fable-worker (run persistent-local-06) — **verifier ≠ producer** (this row by directive-compliance-verifier)
**Candidate commit:** `ed04c4bb` · **Reviewed/integration SHA:** `f1e6de26` · **Frozen HEAD:** `7248aed5` (branch candidate/D-024-mrl-option-b)
**Status at review:** `awaiting_gate` (NOT accepted; not merged to main — `git branch --contains f1e6de26` = candidate/D-024-mrl-option-b only)

## Reproduced evidence (each item verified from primary source, producer claims re-derived)

**1. Applicability evaluation — reproduced independently.**
`evaluate_task_refs(M0-T149)` at the merged registry returns exactly:
`ok=true, applicable_ids=[], cited_ids=[], missing_ids=[], invalid_refs=[], unresolved=[], reasons=[]`.
The cited `D-032:ALL` binds ZERO requirement rows: all **21** D-032 requirements are applicability-scoped to `task_ids=[D-032-BOOTSTRAP]` (distribution reproduced: `{('D-032-BOOTSTRAP',): 21}`, zero rows off-BOOTSTRAP, zero empty-`task_ids` wildcards); `task_id=M0-T149` matches none. **SATISFIED.**

**2. Selective-citation exposure — full sweep, none found.**
Reproduced `derive_applicable` semantics over **all 32 active directives** (D-001…D-034, **3623** requirement rows): `matched (applicable) = 0`; `all-empty-wildcard rows = 0`; no UNRESOLVED. Specific to the supervisor concern: **D-024 has 783 requirements, and 0 carry any `paths` / `task_ids` / `task_types` / `milestones` applicability that reaches M0-T149** (path-applicability rows = 0). Therefore no un-cited directive requirement becomes machine-applicable via M0-T149's allowed_paths. The supervisor-freeze duty is a path-scoped **rule**, not a machine-applicable directive row; it is discharged by the AD-093 citation (item 3), not by a bound requirement. **No selective-citation exposure. SATISFIED.**

**3. Supervisor-freeze citation duty (`.claude/rules/supervisor-freeze.md` §2/§3) — cited in BOTH packet and commit.**
- Packet `objective` (M0-T149.json): "qualifying evidence AD-093 = demonstrated security risk (defense-in-depth gap identified at G3 review of accepted commit 53d642a1)" + "project-control/reports/M0-T148-G3-code-review.md LOW-1".
- Commit `ed04c4bb` body: "Qualifying evidence (supervisor-freeze S2/S3): AD-093 demonstrated security risk - M0-T148 G3 LOW-1 (project-control/reports/M0-T148-G3-code-review.md), defense-in-depth gap at accepted commit 53d642a1."
- LOW-1 source exists and matches: `project-control/reports/M0-T148-G3-code-review.md:22` documents the `documented_test_commands` execution surface admitting mutating one-segment commands (`git push origin b`, `rm -rf tools`) as convention-not-guard, recommending the exact follow-up this task performs. **SATISFIED.**

**4. Content identity — six blobs byte-identical; submission record complete.**
`git rev-parse <sha>:<path>` pairs for all six allowed paths are **IDENTICAL** between `ed04c4bb` and `f1e6de26`:
`evidence.py f7e92476…`, `policy.py d465106d…`, `test_agent_supervisor_reviewer.py f0fd00fb…`, `test_agent_supervisor_policy.py 280ce4fa…`, `M0-T148-producer-report.md 20519d55…`, `M0-T149-producer-report.md b82ac3dc…`.
Recomputed authoritative identity via `frozen_git_identity` (exclude/control-plane prefix `project-control/`): `d6a2e753…781d` at `f1e6de26` **and** at HEAD `7248aed5` — byte-stable (restamp convention holds). Submission record `project-control/reports/M0-T149.json` carries `content_manifest_sha256 = d6a2e753…781d` (reproduced, matches) and `reviewed_sha = f1e6de26…` (exists; the integration merge freezing candidate ed04c4bb). **SATISFIED.**

**5. Registry law — no directive-registry mutation.**
`git show --stat ed04c4bb` touches only the six in-scope paths (4 under `tools/`, 2 under `project-control/reports/`); **nothing under `project-control/directives/`**. **SATISFIED.**

**Supporting machinery reproduced at HEAD:** `validate_directive_compliance.py --check` exit 0 (D-032 active, 21 reqs, 0 errors; source digests match); `test_directive_reminder.py` 12/12 OK; `test_project_control.py` all 23 groups OK (incl. S9 selective-citation-refused and S12 empty-identity guard). D-024 loads active, 0 errors.

*Scope note:* G3 (code-reviewer) and G5 (security-reviewer) code/security gate outcomes are recorded separately by those reviewers/the orchestrator; this DCV row attests only to the D-001/D-032 directive-compliance dimension.

## Attested D-032 verification.json task row for M0-T149 (record verbatim, empty-set precedent)

```json
{
  "directive_id": "D-032",
  "task_id": "M0-T149",
  "applicable_requirement_ids": [],
  "reviewed_sha": "f1e6de26048a0edeb5ac56e203341ae088ae71f5",
  "reviewed_manifest_sha256": "d6a2e753f5f8480da493e9f4bf55fa4c01a1f565ca73b5824aa9cfebefee781d",
  "producer": "supervised-loop-fable-worker/orchestrator",
  "verifier": "directive-compliance-verifier",
  "schema_version": "directive_verification/v2",
  "verified_at": "2026-09-07T05:20:00+00:00",
  "note": "EMPTY-SET verification. M0-T149 cites D-032:ALL, but the shared canonical resolver (directive_registry.evaluate_task_refs / derive_applicable) independently derives ZERO applicable D-032 requirements: all 21 D-032 requirements (incl. Amendment-4 R021) are applicability-scoped to task_ids [D-032-BOOTSTRAP] (distribution {('D-032-BOOTSTRAP',): 21}; none with an empty-task_ids wildcard), so none match task_id M0-T149. No selective citation: evaluate_task_refs returns ok=true, applicable_ids=[], cited_ids=[], missing_ids=[], invalid_refs=[], unresolved=[]; a full sweep of all 32 active directives (D-001..D-034, 3623 requirement rows) yields zero requirements matching M0-T149 via its allowed_paths, and D-024's 783 requirements carry zero path/task/type/milestone applicability that reaches this task (D-024 is qualifying evidence via the path-scoped supervisor-freeze rule, not a machine-applicable requirement row). Row exists because accept() fail-closes when a cited directive has no task_verification row (mirrors D-032/M0-T147, D-032/M0-T148, D-032/M2-T020 empty-set precedents). Verifier != producer (code producer = supervised-loop-fable-worker; this row produced by directive-compliance-verifier). Supervisor-freeze section 2/3 citation duty satisfied: AD-093 demonstrated security risk (M0-T148 G3 LOW-1, project-control/reports/M0-T148-G3-code-review.md:22, defense-in-depth gap at accepted commit 53d642a1) is cited in BOTH the task packet objective and commit ed04c4bb. Registry integrity independently reproduced: D-032 active, 0 load errors; validate_directive_compliance.py --check exit 0. Registry law: git show --stat ed04c4bb touches only the six in-scope allowed_paths, nothing under project-control/directives/. Reviewed content identity = M0-T149 allowed_paths = d6a2e753f5f8480da493e9f4bf55fa4c01a1f565ca73b5824aa9cfebefee781d, computed via directive_registry.frozen_git_identity (exclude/control-plane prefix 'project-control/'), byte-identical (identical git object ids for all six blobs) across candidate commit ed04c4bb, integration/reviewed commit f1e6de26, and HEAD 7248aed5 -- the reviewed identity is stable, so the mechanical accept-time restamp convention applies (identity stays d6a2e753... while allowed_paths blobs are unchanged; the orchestrator may stamp reviewed_sha to the accept-time HEAD only if the identity still reproduces to d6a2e753...; fail-closed otherwise). Submission record project-control/reports/M0-T149.json carries content_manifest_sha256 d6a2e753... + reviewed_sha f1e6de26.... G3 (code-reviewer) / G5 (security-reviewer) code and security gate outcomes are recorded separately by those reviewers.",
  "requirements": []
}
```

*Orchestrator action:* if HEAD advances before `accept()`, re-confirm `frozen_git_identity` still reproduces `d6a2e753…781d` and stamp `reviewed_sha` to the accept-time HEAD before recording; otherwise fail closed.

## Per-item result

- Applicability (empty set): **SATISFIED**
- Selective-citation exposure (incl. D-024): **SATISFIED** (none)
- Supervisor-freeze citation duty: **SATISFIED**
- Content identity + submission record: **SATISFIED**
- Registry law (no directives mutation): **SATISFIED**

No VIOLATED / UNVERIFIABLE / BLOCKED findings on the directive-compliance dimension. The empty applicable set is correct, no un-cited requirement binds, and the empty-set precedent row above is attested for orchestrator recording.

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the directive-compliance-verifier agent-return channel (2026-09-07 gate wave; transport framing removed, HTML entities decoded, content unaltered). NOTE: this attestation binds to the ed04c4bb/f1e6de26 identity d6a2e753…; the G5-FAIL rework will change the allowed-path blobs, so a delta re-attestation at the post-rework identity is required before acceptance (the row's own fail-closed restamp convention).*
