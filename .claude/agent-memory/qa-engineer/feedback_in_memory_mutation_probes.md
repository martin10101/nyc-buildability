---
name: in-memory-mutation-probes
description: Read-only reviewers can produce real mutation evidence by rebinding module attributes in a python -c probe instead of editing source
metadata:
  type: feedback
---

As a read-only gate reviewer, prove guard adequacy with REAL mutation evidence by rebinding the
guard's module attribute inside a one-shot `python -c` probe (e.g. `mod._bounded_message =
lambda m: m`, `mod.ROUTE_MAX_STREET_LINES = 10**9`, `mod._validate_lot_rule_fact_types = lambda
f: None`), driving the route with a `TestClient`, and comparing the mutated response against what
the suite asserts. Restore the original attribute after each probe.

**Why:** the reviewer must never edit implementation files, so the usual "delete the line and
re-run" mutation test is forbidden. Attribute rebinding in a throwaway process achieves the same
proof with zero filesystem writes, and it upgrades a gate finding from "reasoning about
assertions" to reproducible evidence. On M5-T057 this proved guard removal yields HTTP 200 where
the test asserts 422 (guard genuinely bound), and separately that a *cap constant* could drift
400 -> ~468 with the suite still green (exactness unpinned) — a distinction assertion-reading
alone would have missed.

**How to apply:** use it during any G4 gate where the packet demands "a test that would fail if
the guard were removed" or "exactness". Works for routes that resolve collaborators through module
globals; it does NOT work for values captured at import into a local/closure — check the call site
first. Pair it with a measurement probe (print the actual response length/field) before declaring
a bound "exact". See [[gate-evidence-reproduction]].
