# G0 Readiness Record — M2-T003 (Property API boundary + contract-version hardening)

- **Gate:** G0 definition-of-ready (administrative; recorded by the orchestrator)
- **Recorded:** 2026-07-17
- **Task:** M2-T003, implementation, producer backend-engineer, reviewers data-contract-verifier (G1) + code-reviewer (G3/G4)

## Readiness checklist

- **Objective unambiguous:** YES — packet clarified via control PR #13 (7087ee1). Contract 1.2.0 is the current canonical property-profile contract; make the builder declare it (no stale 1.0.0), validate declared-version-vs-emitted-key-set, generate TypeScript types from the canonical 1.2.0 schema, enforce exact HTTP-status/state pairs, emit a bounded error on unsupported contract versions, and record the HTTP-500+state=no_match transport fixture. Grounded in `packages/contracts/README.md` §167 (the deferral M2-T004 explicitly handed here).
- **Dependencies:** M2-T004 ACCEPTED (24th; contract 1.2.0 published to the closed enum). No mocked dependencies.
- **File scope exclusive:** `services/api/**`, `packages/contracts/**`, additive `.github/workflows/ci.yml` type-generation drift check, own producer report. Verified NON-overlapping with the only other in-flight task M0-T016 (scope `tools/**` only) and with M2-T002/M1-T009 (not yet claimed). No shared migrations or contracts with an active writer.
- **Inputs/outputs defined:** packet `project-control/tasks/M2-T003.json` (post-#13). Inputs: §167 deferral, settled 1.2.0 schema, current `properties.py`/`builder.py` emission, M1-T005/M1-T006 G3 review notes, handwritten web API types (read-only input). Outputs: backend response validation, pair-matrix enforcement, contract_version resolution to 1.2.0, deterministic typegen + CI drift check, 500+no_match fixture, producer report.
- **Acceptance scenarios:** S1–S10 in the packet (valid-profile validation, fault injection→typed 500, pair matrix, 500+no_match fixture, typegen determinism, contract_version consistency, 1.0.0/1.1.0 backward-compat, unsupported-version bounded error, G1 mapping re-verification, full-suite regression).
- **Source documentation available:** `packages/contracts/README.md` (contract 1.2.0 + §167), the settled schema, and the accepted M2-T004/M1-T005/M1-T006 evidence — all in-repo. No external credentials.
- **Credentials:** none required (no live source calls; deterministic contract/API work). No blocker needed.
- **Gates assigned:** G0, G1 (data-contract-verifier), G2 (producer self-check), G3 + G4 (code-reviewer).
- **Execution location and disk:** producer edits code in the isolated worktree `.claude/worktrees/M2-T003` (source-only checkout, small). Heavy validation — full API pytest, typegen determinism/drift, web-e2e regression — runs in **GitHub Actions CI** on the task PR, not on the owner PC (thin-client policy). Type generation runs in CI; committed generated output is small text. No bulk datasets, no local DB, no new heavy local toolchain.
- **Low-storage budget:** respected — worktree is source-only; generated TypeScript types are KB-scale committed text; no downloads. Owner PC stays well within the 4 GB floor / 2 GB additive ceiling.
- **Cleanup/cloud routing:** durable output committed to GitHub via the task branch → PR; worktree removed after merge through the normal deletion-approval flow. No local-only artifacts.

Result: PASS — ready to claim and dispatch.
