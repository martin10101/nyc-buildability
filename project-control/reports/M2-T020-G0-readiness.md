# M2-T020 G0 readiness (definition-of-ready) — 2026-09-06

Administrative G0 recorded by the orchestrator under D-032 Amendment 2 (owner continuous-build
directive). Packet completeness verified:

- **Objective**: bounded and precise — compose the EXISTING accepted spatial adapters behind the
  default provider with settings-gated enablement (default OFF); no new engine, no rule changes;
  all fail-safes preserved. Grounded in verified finding A of
  `D-032-review-reconciliation.md` (adapter exists with zero app/ callers;
  `rule_evaluation.py:91-92` returns None).
- **Allowed paths** (5): one new provider module, the provider seam in `rule_evaluation.py`, two
  test files, producer report. Forbidden paths fence off rules, connectors, the engine/adapter
  internals, and the control plane. Disjoint from every other claimed task's scope.
- **documented_test_commands** (2): validated against the closed command profile (loop AUTO tier).
- **Acceptance scenarios** (4): default-off parity, live path with doubles through the DEFAULT
  provider, fail-safe preservation, modularity.
- **Directive refs**: D-032:ALL cited; registry evaluation ok, applicable set empty, nothing
  missing (selective-citation guard clean).
- **Gates**: G0, G2, G3, G4, G5 — engineering change on the product API path.
- **Baseline**: worktree `wt-m2t020` (branch `task/M2-T020-live-spatial-provider`) at the
  certified candidate lineage HEAD so control-plane state matches the packet.

Verdict: PASS — ready to claim for the supervised-loop producer.
