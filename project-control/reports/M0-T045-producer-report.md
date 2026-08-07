# M0-T045 producer report — R595 supervised rehearsal + Section 16.2 promotion evidence

**Producer:** backend-engineer (two delegated increments) + owner-executed supervised window
(operator acts) + orchestrator evidence assembly. **Head:** `49fcc43` (code head `afc2da5`).
**Branch:** `task/M0-T045-r595-rehearsal`.

## Deliverables

1. **Increment 1 — pre-R595 hardening (commit `4db6a71`):** the three pinned MUST-RESOLVE sets
   from `M0-T036-ACTIVATION-CHECKLIST.md` resolved with tests (+36; suite 1307/2):
   M0-T041 A1–A4 (pending_prompt failure-path locks; empty-shape fixture lock; real-sampler CLI
   wiring/WARN/doctor tests; live-bytes duty stated), M0-T042 G5 L-1/I-1/I-3 (telemetry
   ValueError; AD-083 byte cap + sole-constructor lock; bounded child capture), M0-T044 G3
   MINOR-1/2 + G5 SEC-1/2/3/INFO-1 (§5.2/5.4 catch-all Tier routing incl. Tier-D owner-stop for
   permission/hook; non-empty authorized_branch; extra_specs guard + instance-level invariant-9;
   redaction discipline; audit_flow_result).
2. **Increment 2 — R595-F1 fix (commit `afc2da5`):** live-discovered defect (approved
   FORWARD_PROMPT journal had no continuation path; parked record held digest only) fixed:
   durable held-prompt text, text-preserving approval with re-approval dead, FORWARD_PROMPT
   loop resume with digest-verified forward-exactly-once (shared outbox core), fail-closed
   degenerate entries, truthful CLI contract; +10 tests incl. the cross-process integration
   lock. Suite **1317 passed / 2 skipped**, zero regressions, reproduced independently by the
   orchestrator after each increment.
3. **R595 supervised rehearsal — ALL legs live-proven** (owner window 2026-08-07, authorization
   D-010-R119, retry agreement R120): threshold trip + armed seam with the unit never
   interrupted; owner digest-bound approval; **live seam actuation** (forward exactly once →
   digest-verified handoff `e75d07c0…` → new session minted → relaunch → successor completed a
   full cycle through live Codex review); re-approval fail-closed; emergency stop mid-unit
   (child tree terminated, no-new-dispatch, owner-only clear, recovery report). Full detail:
   `M0-T045-r595-rehearsal.md`; sealed evidence (26 files, SHA-256 manifest):
   `M0-T045-r595-rehearsal/`.
4. **Section 16.2 promotion-evidence pack:** `M0-T045-promotion-evidence.md` — all 11 items
   COMPLETE with linked evidence; AS-3 claim ceiling stated first (at most shadow →
   supervised-auto readiness; limited-auto needs its own evidence incl. two real product
   tasks); open owner decisions enumerated, never absorbed.

## Acceptance scenarios

- **AS-1:** the rehearsal live-actuated the rotation seam in a real supervised run with the
  complete audit trail preserved (37 chained events, integrity verified); the R593 residual is
  closed **by evidence** (never waiver): the previously-unproven third leg (seam actuation) is
  in `main-run/r4b-start-output.json` + journal. Independent review: the five rostered gates.
- **AS-2:** every 16.2 item links to reproducible evidence (pack table; GitHub leg per owner
  decision R119 stands on accepted M0-T044 proofs + real PR history).
- **AS-3:** the pack claims at most shadow→supervised-auto readiness and says so explicitly.

## Honest limitations

- The rehearsal workload was synthetic (throwaway repo); the forwarded prompt was the
  owner-approved synthetic continuation. The seam/barrier/handoff/forward/rotation mechanics
  exercised are the real production code paths at head.
- Finding R595-F1 was discovered live and fixed same-window (owner agreement R120); the
  discovery run's journal is preserved and is intentionally unresumable (fail-closed old-shape).
- Cross-process resume is locked in-suite via two loop instances sharing one on-disk journal
  with the approval through the real CLI; the live rehearsal itself crossed genuine OS process
  boundaries.
- No quota fixture was flipped `verified_live`; OS-ACL sufficiency and every activation tier
  remain open owner decisions.

## Verification

- Suite: `python -m pytest tools/test_agent_supervisor_*.py -q` → **1317 passed / 2 skipped**
  (orchestrator-reproduced). Validator: `python tools/validate_directive_compliance.py --check`
  → exit 0. Scope: only `tools/agent_supervisor/**`, `tools/test_agent_supervisor_*.py`, the
  packet, and the two allowed report files (+ evidence dir + this report + evidence map) —
  no forbidden path touched.
