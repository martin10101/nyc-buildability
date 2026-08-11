# M0-T047 — G0 readiness (orchestrator)

- Scope tight: 2 tracked files (`apps/web/package.json`, `apps/web/package-lock.json`) + producer report,
  byte-identical to the CI-validated #219 tip `7ac2f91`.
- Directive: in-regime `D-009:ALL`; applicable set is REAL (dependency-security), verified by the
  directive-compliance-verifier DCV, not empty.
- required_gates G0/G2/G3/G5; independent reviewers rostered: code-reviewer (G3), security-reviewer (G5),
  directive-compliance-verifier (DCV).
- Machine evidence: the fresh `web-dependency-security` + `web tree re-audit` + committed-lock age gate on the
  `control/session15-acceptance` HEAD (c032dfe) re-verify advisory-free + integrity + age≥7d at today's date.
- No credentials/secrets/legal/production surface. Acceptance gated on fresh CI green + all reviewer PASS.

Ready to claim. G0 PASS.
