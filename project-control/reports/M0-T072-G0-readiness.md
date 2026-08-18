# M0-T072 G0 readiness — controller external-config manifest binding repair

Recorded by the orchestrator (G0 administrative class) at branch `task/M0-T072-manifest-config-binding`,
base `4a604ff` (control/D-017-a-to-z-completion, D-017 capture; parent of PR #226).

## Checks (7/7 PASS)

1. **Packet completeness — PASS.** Objective, business reason, gates (G0/G2/G3/G4/G5), reviewers
   (code-reviewer, qa-engineer, security-reviewer, directive-compliance-verifier), 9 acceptance
   scenarios (AS-1..AS-9 mirroring D-017-R051's nine regression proofs), allowed/forbidden paths,
   inputs, and risks are populated in `project-control/tasks/M0-T072.json`.
2. **Governing directive active — PASS.** D-017 captured (source-001 + source-002 amendment, 123
   requirements) and `python tools/validate_directive_compliance.py --check` exits 0 at this HEAD.
   Stage-1 rows D-017-R037..R053 bind M0-T072 in `applicability.task_ids`.
3. **Supervisor-freeze qualifying evidence cited — PASS.** The packet's
   `supervisor_freeze_qualifying_evidence` field cites AD-093 §2 items (reproduced defect +
   demonstrated security risk) with exact source anchors (cli.py:443/1551/2704-2705,
   cli.py:2228-2237, cli.py:3023-3028, manifest.py extra_files with zero production callers);
   the same citation will appear in the implementation commit message (freeze rule §3).
4. **Scope resolvable — PASS.** allowed_paths resolve against HEAD (manifest.py, cli.py, README.md
   tracked; new test module, regenerated runbook, and three report files are declared additions);
   validator c17 passes. Forbidden paths exclude the A1 unit files, code_graph, apps/, services/,
   .claude/, and the untouched supervisor modules (config.py, policy.py, broker.py, loop.py).
5. **No conflicting open work — PASS.** No open PR touches `tools/agent_supervisor/**`
   (PR #222 merged; PR #226 is the capture this branch is based on). The A1 worktree remains clean
   and unstarted; this task edits none of its paths.
6. **Dependencies clear — PASS.** Packet has no ledger dependencies. D-017 sequencing places this
   task before the Stage-2 live-controller update (D-017-R054 depends on R053).
7. **Baseline obligation understood — PASS.** Any change to `tools/agent_supervisor/**` must
   re-establish the M0-T039 freeze suite baseline (>= 1165 tests, 0 failures); the full supervisor,
   project-control, directive-compliance, and new regression suites will be run and recorded
   (D-017-R052, harness).

Conclusion: task moves backlog → ready for claim by the orchestrator (producer precedent M0-T070).
