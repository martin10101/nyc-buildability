# D-024 Amendment 7 — owner report (two-lane golden-run evidence split)

Recorded 2026-08-28 at capture (HEAD `5974f42`); the R230 return items. The watcher-operation
answer is a design commitment discharged inside M0-T096; it will be refreshed with that unit's
delivered evidence.

## 1. What can be fully proven today (lane 1 — injected/deterministic)

Everything M0-T096 already contracts (R186/R182/R106 — no task-plan change needed):
the real two-unit autonomous golden sequence from the exact owner start command; a controlled
safe-seam primary-session rotation; injected bounded refusal, quota, fallback,
controller-restart, ambiguous-effect and recovery scenarios; exact-once succession, no
duplicate work, no lost pending action, and correct stop/hold behavior — all via deterministic
fixtures, accelerated counters, injected runners, and disposable branches/worktrees, labeled
INJECTED (R223). Additionally already accepted and green: refusal classification + bounded
bridge policy (H1), the root-cause repair gate + exact-once GitHub-effect matrices (H2, in its
independent gate wave at capture), rotation/succession, crash/ambiguous-effect reconciliation.

## 2. What remains pending natural observation (lane 2)

Only the genuine live Fable 5 event evidence, recorded as `pending_live_observation` (R224):
- the live refusal-shape corpus confirmation (today: documentation-confidence fixture with
  `verified_live=false` asserted by test — accepted H1 posture);
- the measured-live precondition of the automatic 4.8 bridge's actuation
  (`assert_actuation_permitted` requires a measured-live corpus shape AND R595 — both absent);
- the natural model-turnover/quota observation itself (never provoked; R221).

## 3. Does any pending live observation block the general loop?

No. It gates exactly ONE feature: live actuation of the automatic 4.8 bridge — which is
independently owner-gated by R595 regardless. The general autonomous loop, golden run,
rotation, recovery, and GitHub-effect discipline are independently provable and proceed
(R220/R228). Continuous-mode activation remains owner-gated by R187/R595 on its own terms.

## 4. How the passive watcher operates and when it can observe (R226 — delivered in M0-T096)

A bounded read-only observer over records the supervisor ALREADY writes (R225 reuse: the
sanitized telemetry journal + the accepted guardrail/quota classifier records). When, during
any future running supervised/shadow session, the classifier records a natural refusal, quota,
availability, or model-turnover event, the watcher persists one sanitized durable evidence
record — observed event type, applicable installed-version shape, classification decision,
selected response, sanitized outcome — into the pending_live_observation register. It never
prompts, messages, or injects anything into the producer's context (it consumes existing
journal records only). It can observe whenever a supervised session is actually running when
the event occurs; it cannot observe outside a running session — a truthful limitation, not a
gap to be forced (R221).

## 5. Exact behavior if the natural event happens before its feature graduates

The accepted H1 machinery already governs: the event classifies fail-closed (quota delegate
first, both directions disjoint — R075); the loop records INTENT only and holds safely at the
seam (record-intent-only posture; quota → detect-and-hold; refusal → journaled typed policy
held for the standard review path). NO live 4.8 actuation occurs — `assert_actuation_permitted`
refuses (measured-live shape absent AND R595 absent; fail-safe, proven by test). The watcher
captures the sanitized evidence record and marks the observation satisfied. Graduation of the
bridge afterwards still requires the R227 comparison against the injected proof plus the
standard gates plus R595 — never automatically at the moment of the event.

## 6. Refresh at unit-I delivery (M0-T096; the design commitment in §4 discharged)

The watcher is DELIVERED as `tools/agent_supervisor/live_observation.py` (unit-I deliverable
identity `5ff7f08`), exactly as §4 described, with these delivered specifics:

- **Reuse (R225):** it consumes ONLY records the supervisor already writes — the
  `guardrail_refusal/*` journal rows, the worker-turnover exhaustion transitions, the
  `usage_limit_record`, the `provider_abort_record`, the outage retry/blocked records, and the
  `model_change_audit` list. No new capture machinery; no schema change (the register lives in
  the existing `state_kv` under `pending_live_observation/*`).
- **When it observes (R226):** every `start` session's epilogue runs the scan (wired in
  `cli.py`; a watcher failure is audited and never breaks `start`). It therefore notices a
  natural event recorded during ANY running supervised/shadow session — at that session's end,
  or at the next `start` against the same checkout. It cannot observe outside a running
  session (the truthful §4 limitation, unchanged). It never prompts, spawns, or injects
  context — asserted structurally and behaviorally by test.
- **Capture fields:** one CAS-idempotent sanitized row per distinct event carrying the five
  ordered fields (observed event type; installed-version shape from the PERSISTED capability
  probe; classification decision; selected response; sanitized outcome + redaction count).
- **Labeling (R223):** closed vocabulary `injected` / `live_candidate` — there is deliberately
  NO `live` value; fixture-born evidence (the harness marker) is classed `injected` even when
  scanned by a live session; nothing in the module (or anywhere) can write
  `verified_live=true` — proven by a source-scan test plus behavior tests.
- **Graduation (R227/R228):** `compare_with_injected_proof` produces the comparison REPORT
  (it refuses an injected row on the live side); `graduation_readiness` reports the 4.8
  bridge `not_ready` (measured-live absent AND R595 absent) and the general loop
  `not_gated_on_live_observation`. Both are read-only; graduation remains the owner-reviewed
  fixture `upgrade_procedure` plus standard gates plus R595.

Register state at delivery: `pending_live_observation` with the three awaited observations of
§2; zero live candidates; the injected golden-run reference rows exist for future comparison.
