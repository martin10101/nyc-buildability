# M0-T157 Producer Report — resolver-test fixture repair

Producer: orchestrator. Packet + claim recorded; cites D-001:ALL (governance coverage).

## Change (one test function, tools/test_directive_compliance.py :290-303)

`test_s12_wrong_directive_reference_fails_closed` no longer hardcodes "D-042" (which the
owner's real D-042 capture made EXIST, breaking the nonexistence premise and failing the
control-plane CI job at run 34726200121 / job 103640653970). The id is now DERIVED from the
live registry: max registered D-<nnn> + 500, guarded by an isdigit filter and an explicit
`assertNotIn` BEFORE use — the fixture can never collide with a future capture because the
derivation slides upward as the registry grows. The resolver behavior under test is
unchanged: evaluate_task_refs must return ok=False with a "does not exist" invalid_ref.

## Verification (real output)

- `python tools/test_directive_compliance.py ResolverTests -v` -> ALL tests OK (incl. the
  repaired s12 against the CURRENT 42-directive registry containing the real D-042).
- `python -m ruff check tools/test_directive_compliance.py` -> All checks passed.
- The control-plane CI job at the fix head is the executable authority (S2).

No production file touched; the resolver, validator, and registry modules are forbidden
paths and byte-unchanged.
