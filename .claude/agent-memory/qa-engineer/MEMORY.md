# Memory index

- [Reproduce producer self-check numbers](gate-reproduce-producer-numbers.md) — re-run every documented self-check at the frozen SHA; producer counts (modularity warnings, per-file test split, class count) drift and skew optimistic
- [Connector override fixture isolation](connector-override-fixture-isolation.md) — verify each fail-closed override trigger is isolated (or reason-fragment-bound), the override never over-fires, and >=cutoff classifiers assert both sides of the boundary
- [Supervisor gate reproduction](supervisor-gate-reproduction.md) — reusable facts for gating agent_supervisor stabilization tasks (count reconciliation, D5 replay, golden_run subset, static-analysis false positives)
