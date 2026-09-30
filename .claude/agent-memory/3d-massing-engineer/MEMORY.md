# Memory index

- [massing_model input-guard ordering](massing-model-input-guard-ordering.md) — the fixed precedence in _prepare_ring; add a lot-only NYC check as a SECOND pass (raw, pre-collapse, post-magnitude) or you break accepted tests
- [massing_model in-process mutation harness](massing-model-inprocess-mutation-harness.md) — whole-module text-mutation injected into sys.modules to prove each new guard reddens; baseline GREEN, mutants RED
