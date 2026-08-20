Do not merge PR #241. Perform one bounded correction on the existing M5-T002 branch.

First reconcile the live repository and confirm:

- PR #241 is still open.
- PR head is still 2b45a13b5256dcfb3a92e970dfb08c691d7ff13c.
- Base main is still d8b3899f61efa6620e18a26541ced96020f5bef9.
- The working tree is clean.
- No other task owns the affected files.

If any identity changed, stop and report the new state before editing.

COMPLETE BLOCKING FINDING

apps/web/src/lib/scenario-contract.ts does not actually enforce the canonical scenario contract as claimed. Adversarial execution of the actual validator and fetchScenario client proves that it currently accepts:

1. draft_zoning_floor_area_cap_sq_ft = -1
2. draft_zoning_floor_area_cap_sq_ft = 0
3. evaluated_input.bbl = "x"
4. cap_provenance.rule_status = "verified"
5. cap_provenance.citations = [null]
6. assumptions = [null]
7. an unexpected top-level property
8. packages/contracts/fixtures/invalid/scenario/embedded_property_profile.json

The actual fetchScenario HTTP path classifies the negative-cap response as kind="scenario" with accepted cap -1. A null citation passes validation and can then fail inside ScenarioResult’s citation rendering.

This contradicts M5-T002 AS-8 and the code’s promise that every HTTP-200 body is runtime-validated against the canonical generated contract before rendering.

REQUIRED CORRECTION

1. Fix validateScenarioDocument without adding dependencies or changing the canonical schema.
2. Make the browser validator faithfully enforce the existing scenario schema, including:
   - allowed/required keys and additionalProperties behavior;
   - canonical BBL format;
   - finite numeric values;
   - strictly positive non-null draft cap;
   - all nested citation fields and citation item shapes;
   - cap_provenance.rule_status enum;
   - assumption item shapes;
   - constraint item shapes;
   - evaluated_input shape;
   - coverage-matrix rows;
   - integrity-check shape;
   - objects must not be arrays;
   - every other existing canonical constraint needed before casting unknown to Scenario.
3. Keep problem reporting bounded.
4. Every committed valid scenario fixture must pass.
5. Every committed invalid scenario fixture must fail, especially embedded_property_profile.json.
6. Add focused adversarial tests for every reproduced bypass listed above.
7. Add a fetchScenario test proving a negative cap, null citation, and embedded-property invalid fixture become validation_failure—not scenario.
8. Ensure malformed nested data can never reach ScenarioResult.
9. Do not change backend calculations, scenario/rules/profile modules, canonical contracts, dependencies, feature flags, agent setup, supervisor, MCP policy, or unrelated files.
10. Do not include cosmetic cleanup or broad refactoring.

VERIFICATION

Run the focused tests, full web unit suite, typecheck, lint, build, Playwright journeys, API suite, contract drift checks, and every required CI job from a clean checkout.

Because this correction changes the reviewed code identity:

- Freeze the new exact code commit SHA and tree SHA.
- Invalidate the existing G3/G4/G5/DCV conclusions for the previous identity.
- Have independent reviewers and the verifier inspect the same new frozen code identity.
- Reproduce the adversarial cases against the actual implementation.
- Collect all findings before one consolidated correction response.
- After any further change, invalidate reviews again and rerun them.
- Perform one final independent review of the final frozen result.
- Keep PR #241 open and unmerged.
- Return the new exact merge identity and measured test/CI evidence to the owner.

Do not claim complete, safe, correct, accepted, or ready to merge until the adversarial contract tests and final frozen-identity reviews pass.
