---
name: supervisor-shadow-effect-specs
description: How to prove a gated external effect (merge/deploy) in the supervisor's shadow harness without tripping D-007 invariant 9 on MODELED_EFFECTS
metadata:
  type: project
---

To journal/reconcile a GATED external effect (e.g. `github_pr_merge`) through the
supervisor's S13.7 machinery WITHOUT wiring it into the live path, do NOT add it to
`tools/agent_supervisor/external_effects.py::MODELED_EFFECTS`.

**Why:** `MODELED_EFFECTS` is the live-path authority ("the model list is the whole
authority"). `test_agent_supervisor_invariants.py::test_invariant_9_no_modeled_effect_performs_a_gated_action`
asserts no entry's name contains `merge`/`deploy` and none is destructive. Adding a
merge effect there fails that invariant and would wire new automatic behavior into a
live path — forbidden under shadow-only / R595 posture.

**How to apply:** `ExternalEffectJournal(journal, extra_specs={...})` resolves specs
per-instance via `_spec_for()` (added for M0-T044): shadow specs first, then the
production registry. A journal built without `extra_specs` still refuses the effect as
`unmodeled_effect`. See `github_flow.SHADOW_EFFECT_SPECS` / `shadow_effects_journal()`
for the pattern, and `ShadowPostureTests` for the proof that the merge stays out of the
production registry. Reuse this for any future gated capability proven in shadow.

Related: idempotency + no-blind-retry guard is `GitHubFlow._guard(action_id)`
(CONFIRMED -> idempotent no-op; PENDING crash-survivor -> reconcile-first, never re-fire).
