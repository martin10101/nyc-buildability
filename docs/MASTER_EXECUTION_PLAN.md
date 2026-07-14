# Master Execution Plan — NYC Buildability (Full Production)

Owner of this plan: orchestrator (only the orchestrator edits it). Ledger source of truth: `project-control/`. Milestone definitions: `docs/IMPLEMENTATION_SEQUENCE.md`. Updated: 2026-07-14.

Scope: the complete citywide product in PRD.md — every NYC property accepted, all mandatory official-source families ingested, complete Zoning Resolution corpus, published machine rules with professional approval, scenario engine, evidence viewer, reproducible reports. Coverage activates progressively; the architecture is citywide from the start. No prototype shortcuts become production behavior.

## Workstreams

- **WS-A Control & CI** — control plane, monorepo, CI, environments, secrets policy
- **WS-B Cloud foundation** — Supabase schema/RLS/storage, Render services, Vercel, deployment/rollback
- **WS-C Source intelligence** — source registry, research, connectors, provenance, drift detection
- **WS-D Geospatial** — PostGIS geometry, districts/overlays intersections, split lots
- **WS-E Legal corpus** — Zoning Resolution ingestion, versioning, retrieval, embeddings
- **WS-F Rules platform** — DSL, evaluator, extraction pipeline, reviewer UI, releases, coverage matrix
- **WS-G Scenario engine** — objectives, constraint solving, diversity, scoring, feasibility layer
- **WS-H Product UI** — Property/Confirm/Compare/Evidence, reviewer/admin areas
- **WS-I Reporting & ops** — reports, observability, golden properties, hardening, release

## Task board

Legend: gates per `project-control/config.json` defaults unless noted. Producer ≠ reviewer always. Every task requires acceptance scenarios before implementation (G0).

### M0 — Engineering control plane and cloud foundation (ACTIVE)

| ID | Title | WS | Producer | Reviewer(s) | Gates | Depends | Cloud needs | Status |
|---|---|---|---|---|---|---|---|---|
| M0-T000 | Control-plane lifecycle verification | A | progress-auditor | orchestrator, qa-engineer | G0,G3 | — | — | ACCEPTED |
| M0-T001 | Repository/control-system audit | A | progress-auditor | orchestrator | G0,G3 | — | — | ACCEPTED |
| M0-T002 | Official-source discovery: address/BBL/BIN resolution | C | official-source-researcher | data-contract-verifier (G1), orchestrator (G3) | G0,G1,G3 | — | — | AWAITING G1 |
| M0-T003 | Independent bootstrap review | B | cloud-architect | orchestrator | G0,G3 | — | — | ACCEPTED |
| M0-T004 | Monorepo skeleton + GitHub Actions CI (lint/test scaffold, remote-first) | A | backend-engineer | code-reviewer (G3), qa-engineer (G4) | G0,G2,G3,G4 | M0-T003 | GitHub Actions | READY NEXT |
| M0-T005 | Secrets policy + .env.example + secret-scanning CI check | A | backend-engineer | security-reviewer (G5) | G0,G2,G3,G5 | M0-T004 | GitHub Actions | BACKLOG |
| M0-T006 | ADR set: cloud architecture, environment separation (dev/staging/prod), deployment+rollback procedures, Render Blueprint (render.yaml) | B | cloud-architect | code-reviewer | G0,G3 | M0-T003 | — (authoring only) | BACKLOG |
| M0-T007 | Supabase project confirmation + baseline migration framework (migrations in git, applied remotely) | B | supabase-engineer | security-reviewer, qa-engineer | G0,G2,G3,G4,G5 | B-001, M0-T004 | Supabase | BLOCKED (B-001) |
| M0-T008 | Auth + organizations + RLS baseline + audit_events (tenancy core) | B | supabase-engineer | security-reviewer (G5), qa-engineer | G0,G2,G3,G4,G5 | M0-T007 | Supabase | BLOCKED (B-001) |
| M0-T009 | Canonical contracts v1: property profile, source fact, coverage status, analysis state machine (typed, versioned, shared) | A | backend-engineer | code-reviewer, data-contract-verifier | G0,G2,G3,G4 | M0-T004 | — | BACKLOG |

M0 exit gates: G3, G4, G5 across the milestone.

### M1 — Official-source registry and connector framework

| ID | Title | WS | Producer | Reviewer(s) | Gates | Depends |
|---|---|---|---|---|---|---|
| M1-T001 | source_registry + source_versions + ingestion_jobs schema & migrations | C | supabase-engineer | security-reviewer, data-contract-verifier | G0,G2,G3,G4,G5 | M0-T008 |
| M1-T002 | Connector framework: interface, fixtures harness, provenance contract, rate-limit/backoff, schema-drift detection | C | backend-engineer | code-reviewer, qa-engineer | G0,G2,G3,G4,G5 | M0-T009 |
| M1-T003 | Geoclient v2 resolve-address connector (+ GeoSearch fallback) with contract tests & fixtures F1–F16 | C | backend-engineer | data-contract-verifier (G1) | G0,G1,G2,G3,G4,G5 | M1-T002, B-004 |
| M1-T004..T016 | Research + registry records for each remaining mandatory source family (PLUTO/MapPLUTO, Zoning Tax Lot DB, GIS Zoning Features, Zoning Resolution, DOB NOW, BIS, CO data, DOB violations/complaints, ACRIS, landmarks, flood, pending land-use, DOB bulletins/codes, NYS MDL) — one research task each | C | official-source-researcher | data-contract-verifier | G0,G1,G3 | M0-T002 pattern |
| M1-T017 | Admin source-registry + connector-health screens | H | frontend-engineer | human-journey-reviewer | G0,G2,G3,G4 | M1-T001 |
| M1-T018 | Job system: DB-backed queue, idempotency, heartbeat, resume, dead-letter | C | backend-engineer | qa-engineer, code-reviewer | G0,G2,G3,G4,G5 | M1-T001 |

### M2 — Citywide property intelligence
PLUTO/MapPLUTO import (Render workers, chunked), tax-lot geometry (PostGIS), zoning districts/overlays/special districts intersection engine incl. split lots (geospatial scenario pack), DOB/DOF/ACRIS fact connectors, landmark/flood/pending flags, conflict engine, canonical property profile assembly, Property + Confirm screens. Producers: geospatial-engineer, backend-engineer, frontend-engineer, supabase-engineer. Reviewers: data-contract-verifier, qa-engineer, human-journey-reviewer, security-reviewer. Gates: G1,G3,G4,G5.

### M3 — Versioned legal corpus
Zoning Resolution full ingestion with section hierarchy, tables, definitions, cross-references, effective versions, snapshots (Supabase Storage), diffing, embeddings (pgvector), retrieval, prompt-injection defenses, evidence viewer. Producers: legal-corpus-engineer, ai-pipeline-engineer, frontend-engineer. Gates: G1,G3,G4,G5.

### M4 — Rule engineering and professional-review system
Rules DSL v1 (JSON, versioned), deterministic evaluator with traces, draft extraction pipeline (schema-constrained AI), reviewer UI, test-case framework (positive/negative/boundary/exception), releases, coverage matrix, general/special priority + exceptions. First verified releases require qualified human approval (G6). Producers: rules-engineer, ai-pipeline-engineer, frontend-engineer. Gates: G3,G4,G5,G6.

### M5 — Scenario and optimization engine
Objective model, constraint solver, scenario diversity, practical code-feasibility layer (PRD 7.2), conditional/professional-review paths, stable scoring, Compare + Evidence screens. Producers: scenario-optimization-engineer, frontend-engineer. Gates: G3,G4,G5,(G6 where legal rules involved).

### M6 — Reporting, operations, validation, launch
Reproducible PDF/Excel/JSON reports (generated on Render, stored in Supabase), golden-property library, freshness monitoring, observability, client validation, hardening, G7 release with human production approval.

### M7 — Advanced capabilities
Cost/revenue assumptions, schematic massing, Revit integration, collaboration, external professional-review workflow.

## Acceptance-example policy
Every task packet embeds executable scenarios per `docs/ACCEPTANCE_SCENARIO_STANDARD.md` covering normal, boundary, missing-data, invalid-input, conflicting-source (where applicable), external-API failure, auth failure (where applicable), user-visible recovery, provenance verification, and cross-tenant security (where applicable). M0-T001..T003 packets demonstrate the format.

## Human-only actions
Tracked exclusively in `docs/HUMAN_ACTIONS_REQUIRED.md` + `project-control/blockers/`. Currently: B-001 Supabase token, B-002 Render key, B-003 Vercel, B-004 Geoclient key; later G6 professional approval and G7 production approval.

## Next executable tasks (no human action needed)
1. **M0-T004** monorepo skeleton + GitHub Actions CI — unblocked.
2. **M0-T006** ADRs + render.yaml Blueprint authoring — unblocked.
3. **M0-T005** secrets policy — after T004.
4. **M0-T009** canonical contracts v1 — after T004.
5. **M1-T004+** official-source research fan-out — unblocked (research needs no keys).
