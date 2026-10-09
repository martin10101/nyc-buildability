# G5 Security Gate Report - M0-T150 (design stage)

- Reviewed: design content f36958c4, verified at HEAD 05f4f655 (identity stable; M2/M0-T151 merges touch disjoint paths)
- Reviewer: security-reviewer (independent, read-only). Verdict: PASS with REQUIRED-AT-IMPLEMENTATION conditions.

## Verified against source (not producer claims)
gate() reviewer/role guards (project_control.py:1076-1173); accept() fail-closed set (:1191-1259);
readonly_agent_guard mutation denylist (:179-181) + unparseable-payload deny; task_verification_result
verifier!=producer + stale-sha fail-closed (directive_registry.py:733, :1004); frozen_git_identity (:1554);
record_advancement CAS single-winner (next_task.py:187-241); bounded_mode_gate + LimitedAutoRefused
activation precedent (start_gate.py:62-92, loop.py:314-331); push_policy.assert_no_execution
unconditional raise (push_policy.py:75). Frozen commit is design-only (2 files, in-scope).
Missing seams I1-I4 honestly labeled, not invented. All 7 attack surfaces assessed; boundaries
(G6/credentials/payments/production/PR #241/push/Tier D) refuse-and-park - PASS.

## REQUIRED-AT-IMPLEMENTATION conditions (BLOCKING for the T-A/T-B/T-C implementation tasks)
- F1 HIGH (authority creep): machine-enforced allow-set bounding the controller's project_control.py
  surface to submit/gate/accept/record_advancement FOR ITS QUEUE'S CURRENT TASK ONLY; never new-task/
  unlock/depend/master-plan/hold/directive writes; negative test for out-of-scope subcommand + out-of-queue task.
- F2 HIGH (verdict forgery): the I2 verdict->gate bridge must bind reviewer identity at dispatch from a
  worker-uninfluencable source, bind decision output to the dispatch by unique path + digest, assert
  reviewer != producer, fail closed on mismatch; dedicated forgery MUTATION test.
- F3 MED (prompt injection): every new G3/G4/G5 + verifier contract carries the M0-T148 worker-authored-
  data immunization clause + redact_structure + review_packet guard + an injection negative test.
- F4 MED (audit integrity): idempotent crash-recovery for the committer (accepted-but-uncommitted resume,
  never re-accept); one hash-chained audit entry per gate/accept/commit.
- F5 MED (SoD tests): mutation tests for matrix rows 4/5/7 AND the two new enforcements (F1, F2).
- F6 LOW: symmetric refusal for each staged enable flag; document runtime-dir OS-ACL posture.
- F7 LOW: bind committer git ops to push_policy.assert_no_execution() at runtime.

Rework at design stage: none. Orchestrator duty: carry F1-F7 verbatim onto the implementation packets;
F1/F2 are blocking acceptance conditions for their tasks with load-bearing negative/mutation tests.
