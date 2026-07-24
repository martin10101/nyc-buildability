# G4 CONTROL-PLANE VERIFICATION — ROUND 2 (rework at `ed8a6776`)

- Verifier: control-plane-verifier (independent; producer = orchestrator; producer != verifier)
- Reviewed head: `ed8a6776f89c9f2b17ecad35e528a0180fe6bfd1`; content-manifest identity `9ab6c9601b1a60f903d1a399d57192f662d96e912fdc50304ba931894b3004be` (both independently reproduced; frozen_git_identity at HEAD returns exactly this identity, resolved sha == HEAD, clean stamp err None — the new N2 "reviewed commit must be HEAD" guard passes correctly and does not block the live stamp).

## VERDICT: PASS

The rework strengthens enforcement without disturbing any control-plane invariant. No forbidden state change, scope-clean delta, no new deadlock, manifest/independence/holds intact, full battery green.

## Itemized findings

1. No forbidden state change — CONFIRMED. `git show ed8a6776:project-control/tasks/M0-T023.json`: status=awaiting_gate, progress_percent=95, producer_agent=orchestrator, reviewer_agents=[directive-compliance-verifier, control-plane-verifier, code-reviewer, security-reviewer]. Not accepted, not 100%. origin/main still 1acb9b5; nothing merged. No new checkpoint. master_plan.json unchanged (milestone statuses + accepted count 42 unchanged); state.json diff limited to +"M0-T023" in active_tasks + timestamp (legal sync_state side-effect).

2. Scope discipline of the rework delta — CONFIRMED. `git diff --stat bd8e1011..ed8a6776` = exactly 3 files (directive_registry.py, project_control.py, test_project_control.py), all within allowed_paths; ZERO forbidden paths (no apps/services/packages, no agent_dispatch_guard.py/its test, no other task file, no master_plan.json, no migration_manifest.json).

3. progress() regime-entry guard does NOT deadlock an already-active pre-regime task — CONFIRMED. The guard (project_control.py:699-715) fires only when enabled AND not in_regime AND target!=canceled AND cur not in _CONTINUATION_STATUSES AND target in _CONTINUATION_STATUSES. A legitimately already-active task has cur in {claimed,in_progress,self_check,awaiting_gate}, so the guard never fires. Machine-proven: PROOF 4 accepts an already-active in-manifest legacy task; PROOF 6 lifecycle-only progress keeps grandfathering; PROOF 7 re-enters via claim --directive-refs; PROOF 7b/7c close only the illegitimate laundering path. Re-entry hatch real: CLAIMABLE_STATUSES={ready,rework}; claim() performs regime entry. No status stranded.

4. Migration manifest, reviewer independence, holds — CONFIRMED unchanged. Manifest lock intact (sha256==manifest.migration_manifest_sha256=e14190fa; 57 entries/unique/64-hex; not touched by the delta). Roster unchanged; CLI still bars orchestrator from independent gates and producer==reviewer. Expansion hold, agent_dispatch_guard, blockers all byte-unchanged by the delta.

5. Rework code changes reviewed for regressions/bypass — CONFIRMED sound. N1 intersection only removes a false cross-task/missing-row failure for multi-directive tasks (identity for single-directive M0-T023); no applicable requirement silently dropped; not a bypass. N2 fails closed unless resolved commit == HEAD; submit/gate/accept use HEAD, so no legitimate flow blocked (clean stamp at HEAD returns err None). _run_git hardening (GIT_LITERAL_PATHSPECS=1, timeout=60, --end-of-options, both-column R/C) is defense-in-depth with no behavioral regression.

6. Test + validator battery at ed8a6776 — CONFIRMED green (14 project-control groups incl. the 9 adversarial proofs; validate --check exit 0).

7. Head binding — CONFIRMED (frozen_git_identity over M0-T023 allowed_paths at HEAD returns 9ab6c960, sha ed8a6776, err None).

## Non-blocking observation (expected precondition, not a violation)

The on-disk G2-G5 gate records + verification.json were stamped at reviewed_sha 4529ffc / identity db32be26, now doubly stale vs ed8a6776 / 9ab6c960. Acceptance remains correctly BLOCKED by the stale-identity + per-task-v2 guards until G3/G4/G5 and the directive per-task verification are RE-RECORDED at 9ab6c960 / ed8a6776. This is the expected precondition; the present round-2 review is part of that re-verification wave.

Round-2 verdict: PASS, bound to reviewed_sha ed8a6776 / identity 9ab6c960.
