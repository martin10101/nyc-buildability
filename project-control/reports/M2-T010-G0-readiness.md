# G0 Definition-of-Ready — M2-T010 (orchestrator, administrative)

**Task:** Contract-publication tooling — derive client supported-versions from the canonical schema, drift regression, contract.py docstring fix
**Reviewer:** orchestrator (administrative) · **Result:** PASS · **Date:** 2026-07-20

G0 readiness confirmed before dispatch (owner-approved next wave + 2026-07-20 amendment):

1. **Objective unambiguous** — packet `project-control/tasks/M2-T010.json` (with the 2026-07-20 owner amendment): make the web client `SUPPORTED_CONTRACT_VERSIONS` derive from the canonical schema enum; add a negative drift regression; prove AND preserve the backend derivation chain so BOTH declarations follow the single canonical source; fix the stale `contract.py` docstring (1.2.0→1.3.0). No contract version after 1.3.0 published.
2. **Dependencies** — M2-T006 accepted (contract 1.3.0). No unmet dependency.
3. **File scope exclusive & disjoint** — allowed paths (packages/contracts tooling, apps/web/src/lib + its tests, the one contract.py docstring, services/api/tests/api) proven disjoint from the parallel M2-T011 task. Test scope narrowed to `services/api/tests/api/**` at the 2026-07-20 amendment specifically to guarantee disjointness. Parallel dispatch authorized (planning PR #49).
4. **Inputs/outputs defined** — canonical schema enum, typegen pipeline + byte-identity CI jobs, client contract lib, backend contract module. Outputs: derivation mechanism, drift regression test, docstring fix, producer report.
5. **Acceptance scenarios exist** — CT-S1..CT-S7 in the packet (single-source derivation, drift red-path, compatibility, docstring, no-publication proof, CI regression, backend-chain proof).
6. **Required gates assigned** — G0, G1 (data-contract-verifier), G2 (producer self-check), G3/G4 (code-reviewer). Producer ≠ any independent reviewer.
7. **Execution location & disk** — local checkout for Python-side proof + GitHub Actions CI as the authoritative web-suite evidence (thin-client policy: no local `apps/web/node_modules`). Negligible disk footprint.
8. **Cleanup/storage routing** — no durable artifacts on the owner PC; all output is source in Git.

Ready-to-start criteria met. Task dispatched to backend-engineer in isolated worktree.
