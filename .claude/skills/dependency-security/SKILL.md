---
description: Route for the permanent dependency-security policy — package admission, age gate, and supply-chain rules. Use before adding/upgrading any dependency, editing a lockfile, or touching audit tooling.
---

This is a router, not a copy of the policy. The authoritative rule is `.claude/ORCHESTRATION_POLICY.md`
§G "Dependency security policy (permanent, no waiver)"; deployment/CI specifics are in
`.claude/rules/deployment.md` (auto-loads under `.github/workflows/**`, `render.yaml`, `infra/**`).

Invariants (see §G for the exact wording — do not restate it elsewhere):
- No known advisory at any severity; every admitted version ≥ 7 complete days old (604800 s passes,
  604799 fails), measured against official registry publish timestamps in UTC, with integrity evidence.
- Fail closed on unavailable/missing/malformed/ambiguous/unmatched registry or integrity evidence.
- No agent waiver, no unlocked bootstrap tool, no dynamic download outside a reviewed lock.

Enforcement (machine, not advisory): `services/api/scripts/dependency_age_gate.py` (Python locks) and
the committed-npm-lockfile age gate. SHA-pin every third-party GitHub Action. Any dependency change is
G5 security-reviewed. Do not modify the gate's behavior without a G5 review.
