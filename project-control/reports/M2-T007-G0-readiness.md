# M2-T007 — G0 Definition-of-Ready record

- **Task:** M2-T007 — GIS Zoning Features connector (ArcGIS, six canonical DCP layers)
- **Recorded by:** orchestrator (G0 is administrative per the hardened CLI gate classes)
- **Date:** 2026-07-18
- **Owner authorization:** owner approval message 2026-07-17 ("OWNER APPROVAL — NEXT CONNECTOR WAVE"), strict order M2-T007 → M2-T008 → M2-T009, fixture-driven only, no persistence/credentials/production.

## G0 checklist (docs/GATES_AND_CHECKPOINTS.md)

1. **Objective unambiguous** — PASS. Packet objective enumerates the six canonical services, the eight owner safeguards (allowlisting, metadata validation, mandatory paging, resilience reuse, fixture provenance manifests, determinism, scope exclusions, test matrix), EPSG 2263 preservation, and the two-staleness separation rule.
2. **Dependencies accepted or mocked behind contracts** — PASS. M1-T003 (research, accepted; G1-corrected doc `docs/research/zoning-features-ztldb-2026-07-16.md`), M1-T005 (connector framework, accepted), M1-T009 (resilience framework, accepted). No mocks needed; CI is fixture-driven.
3. **File scope exclusive** — PASS. New connector module(s) + new test module(s) + new fixture directory `services/api/tests/fixtures/zoning_features/` + one registry draft file + own producer report. No other task is active (ledger: 0 claimed). Existing connector/test files are read-only inputs by packet rule.
4. **Inputs and outputs defined** — PASS (packet `inputs`/`outputs`).
5. **Acceptance scenarios exist** — PASS. ZF-S1..ZF-S13 in the packet, derived from the research §6 ZF fixture pack plus the owner's negative-case list (multiple pages, empty layer, duplicate page, repeated object IDs, missing object-ID field, missing metadata, wrong CRS, malformed geometry, ArcGIS error with HTTP 200, timeout, rate limit, circuit open, budget exhaustion, schema drift, deterministic digest reproduction). Connector scenario pack minimums from docs/ACCEPTANCE_SCENARIO_STANDARD.md are covered.
6. **Required source documentation available** — PASS. G1-corrected research doc with live-verified service inventories (Z7–Z11), plus registry draft `docs/research/source-registry-drafts/zoning-features.json`.
7. **Credentials** — PASS (none required; ArcGIS services are keyless; no secrets may appear anywhere in fixtures/manifests).
8. **Required gates assigned** — PASS. G0/G1/G2/G3/G4/G5; roster data-contract-verifier (G1), code-reviewer (G3/G4), security-reviewer (G5 — new outbound-request surface: endpoint allowlisting/SSRF bounding is a packet safeguard). Producer: backend-engineer (assigned at claim). Producer ∉ roster.
9. **Execution location and disk usage** — PASS. Implementation and tests on the owner PC thin-client checkout (source + KB-scale JSON fixtures only; well under the 2 GB budget; ≥4 GB free preserved). Full CI in GitHub Actions. Producer fixture capture uses bounded live reads of the six official services (KB responses, disclosed retrieval timestamps); no dataset downloads, no citywide blob, no Docker, no local DB.
10. **Cleanup and durable routing** — PASS. Durable artifacts are git-committed fixtures/reports only; no temp artifacts beyond pytest tempdirs; no cloud persistence (B-001 stands, out of scope).

## Verdict

**G0 PASS** — task is ready; claim by backend-engineer follows in this control PR; worktree `.claude/worktrees/M2-T007`, branch `task/M2-T007-zoning-features-connector` to be created from main after this control PR merges.
