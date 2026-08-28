# D-024 Amendment 7 — Two-lane golden-run evidence split: injected proof now, natural-event observation deferred (owner instruction 2026-08-28)

Captured: 2026-08-28 UTC by the orchestrator (Fable 5), verbatim from the owner's mid-turn
interactive message (channel: Claude Code interactive session, user message delivered mid-turn
during the M0-T095 unit-H2 independent-review wave; the harness's standard mid-turn delivery
note is framing, not owner text, and is excluded from the verbatim block). Base identity at
capture: branch `control/D-024-fable-codex-loop`, HEAD `5974f42b468f4565460914ce3c9413834cc42000`,
origin/main `d8b3899f61efa6620e18a26541ced96020f5bef9`, tree clean.
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R220..D-024-R230.

Reconciliation (the determination the message itself orders, recorded before any plan change):

- **Lane 1 (deterministic/injected golden-run proof) is ALREADY AUTHORIZED** by the existing
  directive and task plan — R186 (golden-run sequence), R182 (deterministic fixtures,
  accelerated counters, simulated failures, no token-waste simulation), R106/Phase H, and the
  contracted M0-T096 packet objective, which already names fault-injected deterministic suites,
  forced rotations/fallback simulations, crash/restart and ambiguous-effect recovery, the
  two-unit golden run from the exact owner command, one safe primary-session rotation, and one
  injected controller restart without duplicate work. Lane 1 therefore implements WITHIN the
  existing M0-T096 scope; no task-plan change is required for it.
- **The 4.8-bridge feature gate is already mechanized and accepted** (M0-T093/unit H1):
  `assert_actuation_permitted` double-gates live actuation on a measured-live corpus shape AND
  R595; the recognized-shape corpus ships documentation-confidence with `verified_live=false`
  asserted by test; R187 keeps continuous mode disabled after the golden run. This satisfies
  "keep only that bridge shadow-only ... fail safe with a clear durable status" as-built.
- **NEW requirements introduced by this message** (not present in R001–R219, hence this
  amendment): the no-blocking/no-provocation prohibitions (R220/R221), the explicit
  injected-vs-natural labeling duty (R223 — previously only implicit in the R149/R201/R208/R211
  honesty family), the `pending_live_observation` status with its never-fabricate rule (R224),
  the telemetry-reuse instruction (R225), the passive watcher deliverable with its capture
  fields (R226), the compare-then-graduate protocol (R227), the feature-specific gating rule
  (R228), the capture/reconcile/determination process duty (R229 — discharged by this record),
  and the five owner return-report items (R230).

Forward trace: opening paragraph → R229; second paragraph → R220 (sentence 1), R221
(sentence 2); lane-1 list → R222 (bullets 1–5), R223 (bullet 6); lane-2 list → R224
(bullets 1 and 6), R225 (bullet 2), R226 (bullets 3 and 4), R227 (bullet 5); gating
paragraph → R228; plan-change paragraph → R229; report-back list → R230.

---VERBATIM-BEGIN---
OWNER DIRECTION — capture durably before acting and reconcile it against D-024, M0-T093, M0-T096, R187/R192/R197/R595, and the live campaign ledger.

Do not block M0-T096, the golden-run work, or all otherwise-provable readiness work while waiting for a naturally occurring Fable 5 quota, refusal, availability, or model-turnover event. I currently have substantial Fable 5 allowance remaining, and no work should deliberately consume or waste that allowance merely to provoke a natural event.

Separate the evidence into two lanes:

1. Deterministic/injected golden-run proof:
- Execute everything safely testable now.
- Run the real two-unit autonomous golden sequence.
- Force a controlled safe-seam primary-session rotation.
- Inject bounded refusal, quota, fallback, controller-restart, ambiguous-effect and recovery scenarios.
- Prove exact-once succession, no duplicate work, no lost pending action, and correct stop/hold behavior.
- Do not misrepresent an injected event as a naturally observed event.

2. Deferred natural-event observation:
- Record the genuine Fable 5 refusal/quota/model-turnover live canary as pending_live_observation until it naturally occurs.
- Reuse the existing passive sanitized telemetry wherever sufficient.
- Provide a durable, bounded detection and evidence-capture path that notices the natural event during a future running session without prompting or polluting the producer’s context.
- Capture the observed event type, applicable installed-version shape, classification decision, selected response, and sanitized outcome.
- Compare the live behavior with the deterministic/injected proof and graduate only the feature whose live precondition has been satisfied.
- Never fabricate, force, or prematurely mark the natural live canary PASS.

Apply feature-specific gating. A missing natural model-turnover observation must not silently weaken any safety gate, but it also must not unnecessarily block unrelated autonomous-loop capabilities. If the automatic 4.8 bridge cannot safely graduate without measured-live evidence, keep only that bridge shadow-only and make the temporary behavior fail safe with a clear durable status. Continue the remaining campaign and golden-run evidence that is independently provable.

Before changing the task plan, determine whether the existing directive already authorizes this split. If it does, cite the exact requirements and implement within the existing task scope. If it does not, capture this message as an owner amendment and update the requirement/task mapping before implementation.

Report back with:
- What can be fully proven today.
- What remains pending natural observation.
- Whether any pending live observation blocks the general loop or only one feature.
- How the passive watcher operates and when it can observe events.
- The exact behavior if the natural event happens before its feature graduates.
---VERBATIM-END---
