---
name: no-defaults-dataclass-test
description: A zero-arg TypeError test does NOT prove each precondition dataclass field lacks a default; use dataclasses.fields() — matters for the D-052/geometry attestation pattern
metadata:
  type: feedback
---

When reviewing test adequacy for fail-closed **attestation / precondition dataclasses**
(pattern introduced by `AttestedPreconditions` in
`services/api/app/connectors/dcm_street_width_policy.py`, D-052/M4-T019; will recur in
the B3/B4/B7 geometry lane), a test that only asserts `SomeDataclass()` (zero args)
raises `TypeError` is INSUFFICIENT.

**Why:** In a frozen dataclass, only the *last* field can be given a silent default
without a class-definition error, and zero-arg construction still raises even after
that default is added. So the "no defaults" test passes while the last precondition
silently defaults to `True` — the exact "precondition theater" named risk. In M4-T019
this survived mutation (`exceptions_checked: bool = True`, the R001 zoning-exceptions
gate) with all 93 tests still green.

**How to apply:** Require a `dataclasses.fields()` assertion that no field carries a
default/`default_factory`:
`for f in dataclasses.fields(T): assert f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING`.
Treat a bare zero-arg-TypeError test as a Medium test-adequacy gap on any fail-closed
attestation object. See [[mutation-probe-outside-repo]].
