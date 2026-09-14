# D-060 source-001 — Owner 2026-09-14: keep the loop going (Fable-exhaustion hard stop)

## Capture context

Delivered mid-session (session_01JjK8w1YXwFBjUS8PRrTfHp) on 2026-09-14 at ~08:57 UTC, immediately
after the orchestrator relaunched the build loop (run `persistent-local-35`, packet M4-T021) and
the run safe-stopped. Baseline `origin/main`: d8b3899f. Capture head: 7150edef.

**Primary evidence frozen at capture (both records independent, neither self-reported by a model):**

1. Supervisor run log `m4t021-20260914-044426.out.txt` (run persistent-local-35): preflight
   passed, dispatched in limited-auto, then —
   `DISPATCHED in limited-auto mode. cycles=1 final_state=PAUSED_RECOVERY stopped=fable_exhaustion_turnover_recorded`
   `REFUSED (unsafe, exit 11): fable_exhaustion_turnover_recorded`
   `the unattended run stopped on 'fable_exhaustion_turnover_recorded' and cannot resolve it without a human`
   (elapsed 62.1s; owner touches 1 of budget 2). Supervisor state after: PAUSED_RECOVERY,
   trigger=unsafe_condition; audit chain ok at head sequence 857; no pending approvals.
2. Runtime model-switch tracker for this session (`model_switch_tracker.py --query`, reads the
   Claude Code transcript + the runtime's own usage-limit records, never model self-report):
   started on Fable 5; switch 1 at 2026-09-14T08:45:24.207Z Fable 5 -> <synthetic>, switch 2 at
   2026-09-14T08:57:00.822Z -> Opus 5; **recorded reason for both: "USAGE/RATE LIMIT reached —
   the runtime fell back to the other model. NOT a safety refusal."** Currently running Opus 5.

Together these establish that Fable 5 is exhausted for this account **including the extra usage**
D-058-R004 relied on — the loop's worker cannot start on the Fable pin, and the orchestrator
session itself was force-migrated off Fable. Known cause of the loop's inability to self-recover
(already documented in `C:\SupervisorController\model_selection.toml` under D-036-R002): the
live launch-probe seam for auto-turnover is not wired, so `turnover_controller` records the
turnover and safe-stops on an unprobed candidate rather than switching unattended. Documented
recovery precedent: manual pin to the allowlisted `claude-opus-4-8`, performed by the owner on
2026-08-09 and again on 2026-09-07 (D-036-R002). The immutable `config.toml` allowlist already
carries `["claude-fable-5", "claude-opus-4-8"]`, so the empty-allowlist blocker recorded in the
earlier exhaustion arc (D-010-R296) no longer applies.

## Owner message (verbatim) {#owner-message-verbatim}

Go on make sure the loop keeps going

## Standing context this directive resolves {#resolved-question}

D-058-R004 (captured 2026-09-14) reads: the loop + reviewers continue on `claude-fable-5` via
EXTRA USAGE; the pin stays; "opus chain = genuine-hard-stop last resort only, never a pin flip."
The successor prompt restated it as "never flip the pin to opus **outside** a genuine hard-stop
fallback." The evidence above is that genuine hard stop: the loop is REFUSED-unsafe and cannot
run at all on the Fable pin. The owner's instruction, given after the exhaustion began, directs
that the loop keep running. This directive records that the last-resort condition is now MET and
the armed fallback may be actuated, with the revert obligation preserved.
