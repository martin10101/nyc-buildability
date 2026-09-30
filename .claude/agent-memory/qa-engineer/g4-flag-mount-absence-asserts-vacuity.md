---
name: g4-flag-mount-absence-asserts-vacuity
description: Judging mutation-sensitivity of flag-gated route mount tests, and route-introspection asserts that can pass vacuously across fastapi versions
metadata:
  type: feedback
---

For a G4 on flag-gated route MOUNT tests, an "absence" assert (`assert not any("<path>" in p for p in paths)`)
can pass VACUOUSLY if the route-introspection helper is blind to the routes it enumerates. The linchpin
is the sibling flag-ON POSITIVE assert using the SAME helper: if the helper is blind, the positive assert
FAILS. So verify the negative absence asserts are meaningful by confirming the positive registration assert
passes in the same environment.

**Why:** fastapi>=0.139 / starlette>=1.0 record each `include_router` as ONE `_IncludedRouter` entry
(`path is None`) whose `original_router.routes` holds the prefixed routes; older versions flatten into
`app.routes`. Introspecting `app.routes` without expanding MISSES every included route on 0.139 — the
mount-presence assert fails while absence asserts pass vacuously. The accepted fix (M5-T062, mirrors
`tests/api/test_evidence_api.py::_flattened_route_list`) expands `original_router.routes` in place with an
`isinstance(path, str)` filter; it is a no-op on the old layout.

**How to apply:** when the reviewer sandbox runs a DIFFERENT fastapi than pinned CI (e.g. 0.128 local vs
0.139 CI), you cannot prove the 0.139 behavior locally — the local run only proves the no-op-on-old-layout
path. Complete the evidence chain with: (a) read the helper for correctness (non-str filtering, no-op
fallback `[route]` when `original_router` is None), (b) confirm the flag-ON positive assert is green in
pinned CI (orchestrator-captured), (c) note the positive/negative-same-helper linkage. For revoke
scope-before-status ordering, the discriminating test needs a FOREIGN probe against a NON-ACTIVE record
asserting 404 (NotFound), not 409 (NotActive); an active-record cross-property probe passes under BOTH
orderings and does not discriminate. Prove it with a status-first regression subclass in a scratch script.
