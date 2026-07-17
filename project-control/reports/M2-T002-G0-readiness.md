# G0 Readiness Record — M2-T002 (Confirm screen + hardened API client)

- **Gate:** G0 definition-of-ready (administrative; recorded by the orchestrator)
- **Recorded:** 2026-07-17
- **Task:** M2-T002, frontend, producer frontend-engineer, reviewers human-journey-reviewer + visual-quality-reviewer + security-reviewer

## Readiness checklist

- **Objective unambiguous:** YES — PRODUCT_FLOW step 2 Confirm screen on the hardened boundary, resolving M2-T001 carry-forward defects D1–D5 (verbatim in the packet), with exact status/state pair enforcement client-side and runtime validation of 200 profiles against the M2-T003 generated types.
- **Dependencies:** M2-T003 ACCEPTED (26th) — generated TypeScript types (`packages/contracts/generated/property_profile.ts`), backend pair-matrix guarantees, the recorded HTTP-500+state=no_match client-regression fixture (`packages/contracts/fixtures/client_regression/http500_state_no_match.json`, to be wired at the client fetch-stub level per the M2-T003 G3 report O-2), and contract-1.2.0 declaration are all on main at a18b696.
- **File scope exclusive:** `apps/web/**` + own producer report. ORCHESTRATOR OVERLAP RESOLUTION: the packet also allows additive ci.yml web-job changes, but M1-T009 runs in parallel with the same ci.yml allowance — to honor the no-shared-files rule, BOTH producers are instructed to make NO ci.yml edits; new Playwright/vitest suites are picked up by the existing web/web-e2e jobs automatically; any genuinely required CI change is reported for the orchestrator to apply sequentially.
- **Inputs/outputs defined:** packet post-#13-era text; M2-T001 G3 D1–D5 verbatim; PRODUCT_FLOW step 2 spec; design-system docs.
- **Acceptance scenarios:** S1–S8 in the packet (incl. BLOCKING owner-directed S2 regression: 500+no_match must render unexpected_response, never no_match).
- **Source documentation available:** all in-repo (generated types, fixture, design docs, M2-T001 accepted screen). D1 FIELD_LABELS grounding: official PLUTO data-dictionary references already committed with M2-T004's 19-column citation basis + M1 research docs.
- **Credentials:** none. No blocker.
- **Gates assigned:** G0, G2, G3 (human-journey-reviewer), G4, G5 (security-reviewer); visual-quality-reviewer contributes the visual-acceptance evidence within G3/G4 per `.claude/rules/3d-ui-expansion.md` item 11.
- **Execution location and disk:** producer edits source in isolated worktree `.claude/worktrees/M2-T002`; NO local npm install/build/Playwright (owner PC ~1.7 GB free — hard constraint); all builds/tests run in CI on the task PR. Reviewers verify via CI artifacts/traces and code reading.
- **Low-storage budget:** respected — source edits only locally.
- **Cleanup/cloud routing:** task branch → PR → CI → merge; worktree removed after merge via deletion-approval flow.

Result: PASS — ready to claim and dispatch in parallel with M1-T009 (disjoint scopes after the ci.yml resolution above).
