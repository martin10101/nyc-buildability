# M4-T001 — G0 Definition-of-Ready reconciliation

- Gate ID: G0 (administrative readiness, orchestrator)
- Task ID: M4-T001 — Rules-engine foundation: versioned rule system + first rule family (R5 residential FAR)
- Recorded by: orchestrator
- Result: PASS (ready to start; lead-only per owner directive 2026-07-21)

## Dispatch-hold release
The task packet `risks[0]` ("DISPATCH HOLD: awaits owner review of the 2026-07-20 planning report; sequenced after M2-T013 acceptance") is **released for M4-T001 only** by owner directive 2026-07-21. Survey holds M2-T014/T015/T016, GDS/3D expansion holds, M6-T001, and all other owner holds remain in force (unchanged).

## Readiness checks (2026-07-21, base main `dea19b6`)
- **Dependency M2-T013 (uncertainty taxonomy):** accepted ✓ — its facts-with-uncertainty are an input contract; rules must propagate, never collapse.
- **ZR source research input:** `docs/research/zoning-resolution-2026-07-16.md` present ✓ (accepted official-source research: source, versioning, access).
- **Contracts + M2-T010 tooling:** available ✓ (rule contracts follow the canonical-schema discipline; additive-only, disclosed).
- **Rules module:** none exists yet (`services/api/app/rules/` absent) — clean greenfield start ✓.
- **Client R5 benchmark sheet:** NOT present ✗ → bounded human-input blocker **B-010** filed. It gates ONLY the client-validation acceptance item; all architecture/engine/snapshot/draft-rule/second-family/synthetic-fixture work proceeds without it (owner directive 2026-07-21).
- **G6 qualified-human legal gate:** standing human dependency for any `verified`/`published` rule labeling; the engine (G3/G4) is acceptable independently. No rule will be labeled verified/published by any agent.

## Scope binding
Producer: rules-engineer discipline, executed lead-only (no producer subagent dispatched, owner directive 2026-07-21). Reviewers (independent, after a frozen implementation SHA + CI): code-reviewer (G3), qa-engineer (G4). G6 is a separate recorded human event.
Required gates: G0, G2, G3, G4, G6. File scope per packet `allowed_paths` (services/api/app/rules/**, services/api/tests/rules/**, docs/RULES_ENGINE_ARCHITECTURE.md, section-level ZR snapshots at the architecture-doc-defined location, additive rule-definition/evaluation-trace schemas via M2-T010 tooling, own producer report). Forbidden: publishing/verifying any rule, hardcoding R5 into the engine core, touching profile/connectors/spatial/apps-web, bulk ZR ingestion, project-control beyond own report, .claude/**.

## Verdict
**G0 PASS** — ready. Proceed lead-only with the architecture doc + versioned DSL + deterministic evaluator + R5 FAR draft family + second-family representability proof + section-level ZR snapshots + synthetic/golden scenario pack, then freeze an implementation SHA and dispatch G3/G4 reviewers. B-010 tracks the client-benchmark validation item only.
