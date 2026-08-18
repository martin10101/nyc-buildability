# M0-T063 G0 readiness (administrative) — D-013 Unit A1

Recorded by the orchestrator at the D-013 bootstrap session (2026-08-18), baseline
origin/main `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1` (PR #221 merged; Codex go-live
runway complete; M0-T056 accepted — ledger 85).

## Readiness checks

| # | Condition | Verdict |
|---|---|---|
| 1 | Owner authorization captured | PASS — D-013 source-002 (owner typed, 2026-08-18): initiative authorized, A1/A2 split approved, decisions 1–10 fixed. |
| 2 | Directive capture valid | PASS — D-013 registry (manifest, 2 sources with SHA-256, 88 requirements, verification stub) present; `validate_directive_compliance.py --check` green at bootstrap HEAD (evidence in bootstrap commit). |
| 3 | Task packet complete | PASS — M0-T063 packet carries objective, exact allowed/forbidden paths, inputs, outputs, five acceptance scenarios (AS-1..AS-5), verified gate profile G0/G3/G4/G5 with independent reviewer roster (M0-T030 infrastructure precedent, owner decision 10), refs `D-001:ALL; D-013:ALL`. |
| 4 | Dependencies | PASS — none; A1 is the first initiative unit. A2–F (M0-T064..M0-T069) are dependency-ordered path-free roadmap reservations. |
| 5 | Scope hazards disclosed | PASS — `.github/workflows/ci.yml` overlap with open PR #64 disclosed in packet risks (additive step only; stop-with-overlap-report rule); `tools/agent_supervisor/**` forbidden (owner decision 9); code-graph generator/query and context_pack read-only references (decisions 7/8). |
| 6 | Baseline-first ordering | PASS — packet requires the baseline harness to freeze existing generator behavior before any caching integration (D-013 s10/s11). |

G0 = PASS. Task moves backlog → ready for claim by the supervised worker.
