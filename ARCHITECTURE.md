# ARCHITECTURE.md -- NYC Buildability

Architecture context for agents and reviewers. This is NOT a file tour (agents can
read files). It answers only what is hard to infer safely, and it cites existing law
in `CLAUDE.md` and `.claude/rules/**` rather than restating it. Where this document
and the ledger (`project-control/`) disagree, the ledger wins.

Legend for verification: every named component below resolves to a real path; a
hostile reviewer should be able to open it. Nothing here invents a component.

---

## 1. WHAT EXISTS -- the high-level map

- **Next.js analyst frontend** -- `apps/web/` (Next.js: `next.config.ts`,
  `apps/web/src/`). Served from a Render web service `nycdf-web`, not Vercel
  (ADR-004). Four analyst stages Property -> Confirm -> Compare -> Evidence
  (`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`). Placeholder until M2.
- **FastAPI service** -- `services/api/app/`. Application factory `create_app()` in
  `main.py`, versioned routes under `/api/v1` (`app/api/v1/`). Internal subsystems:
  - `connectors/` -- official NYC-source clients: `bbl.py` (BBL normalize/validate),
    `pluto_soda.py`, `ztldb_soda.py`, `mappluto_geometry_arcgis.py`,
    `zoning_features_arcgis.py`.
  - `spatial/` -- the accepted M2-T013 lot/zoning intersection substrate
    (`engine.py`, `adapter.py`, `live_provider.py`, `geometry.py`, `policy.py`,
    `models.py`, `coverage.py`, `crosscheck.py`).
  - `rules/` -- the deterministic rule engine: DSL, evaluator, registry,
    integration, lifecycle, units, response serialization.
  - `profile/` -- connector facts -> canonical property-profile document
    (`builder.py`, `contract.py`).
  - `documents/`, `scenario/`, `resilience/`, `contracts/` -- document ingestion
    gate, scenario building, resilience wrappers, contract wiring.
- **Supabase** -- Postgres/PostGIS/Auth/Storage/pgvector; migrations under
  `supabase/`. The single persistent production data store (`CLAUDE.md` principle 5;
  thin-client policy `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`).
- **project-control ledger** -- `project-control/` (`master_plan.json`, `state.json`,
  `tasks/`, `reports/`, `gates/`, `directives/`, `blockers/`, `checkpoints/`). This is
  the source of truth for WORK state (`CLAUDE.md` "Source of truth"). Read it with
  `python tools/project_control.py status`.
- **Agent supervisor** -- `tools/agent_supervisor/` -- the deterministic Codex<->Claude
  autonomous build loop (owner directive D-007). Modes: `shadow` and `supervised`
  cannot act on their own; `limited-auto` is built but OFF and refused without an
  explicit owner enable input (`tools/agent_supervisor/README.md`). It is FROZEN
  (`.claude/rules/supervisor-freeze.md`; baseline in
  `project-control/reports/M0-T039-supervisor-freeze.md`).
- **Deployment** -- `render.yaml` (Render Blueprint: API + workers + cron + frontend);
  GitHub Actions CI. Deploy model of record: `autoDeployTrigger: off` in production,
  deploy only after migrations + checks + human approval (ADR-003/ADR-004;
  `.claude/rules/deployment.md`).

---

## 2. WHO OWNS WHAT -- one responsibility owner each

The overriding rule (`CLAUDE.md` principle 1): AI retrieves, classifies, drafts, and
explains; deterministic code calculates; qualified humans approve legal
interpretations. Concretely:

- **Connectors own official-source fetch + provenance.** Every fact carries source ID,
  original field/value, normalized value, timestamp, dataset/version, effective date,
  BBL, confidence, conflict status (`.claude/rules/backend-api.md`; enforced in
  `profile/builder.py`, which re-verifies provenance referential integrity before
  returning). Official source order: API > Open Data > bulk > HTML > PDF.
- **The deterministic rule engine (`rules/`) owns every legal/numeric calculation.**
  Routes never compute legal values; `api/v1/rule_evaluation.py` explicitly rebuilds
  the profile server-side and delegates all determination to `evaluate_property`.
- **The spatial engine (`spatial/`) owns geometry, district intersection, and
  positional uncertainty** (`.claude/rules/geospatial.md`). It emits
  facts-with-uncertainty and never collapses uncertainty or self-labels "Verified".
- **AI roles retrieve/classify/draft/explain only** -- AI extraction uses strict
  server-validated JSON schemas; no AI-invented value enters a verified result
  (`.claude/rules/backend-api.md`).
- **The orchestrator (main session) owns git, the ledger, and gate recording** -- the
  sole runner of `tools/project_control.py`, git, and `gh` (ADR-005;
  `.claude/rules/project-control.md`). Producers edit only files in their scope;
  reviewers are read-only and return a verdict.
- **Qualified humans own legal approval** -- no rule reaches `published` (and thus a
  "Verified" result) without qualified-human approval at G6
  (`.claude/rules/legal-rules.md`; `CLAUDE.md` principle 12).

---

## 3. WHAT MAY DEPEND ON WHAT -- boundaries and FORBIDDEN edges

Allowed dependency direction (verified from imports):

- `api/v1/*` routes -> `profile.builder`, `connectors`, `rules.integration`,
  `spatial.live_provider` (see `api/v1/rule_evaluation.py` imports).
- `spatial.live_provider` -> `connectors.*` + `spatial.adapter` -> `spatial.engine`.
- `spatial.adapter` consumes connector domain models READ-ONLY (its module docstring
  states "no connector edits").

FORBIDDEN edges (a task that needs one triggers Section 6 STOP):

- The **rule engine and spatial engine never import connectors or AI.** They consume
  already-fetched, already-provenanced domain models. Direction is one-way:
  routes -> providers -> connectors, never the reverse.
- The **frontend never holds a Supabase service-role key and never computes
  compliance.** The browser holds only session/form state and HTTP cache; only
  publishable `NEXT_PUBLIC_*` vars are allowed on the frontend service
  (`.claude/rules/frontend-web.md`; ADR-004 decision item 4).
- **Connectors never write the ledger; workers and reviewers never run git or write
  accepted-task records.** Nothing writes accepted-task state except
  `tools/project_control.py` run by the orchestrator (ADR-005;
  `.claude/rules/project-control.md`).
- **The document ingestion path never lets a declared filename select handling** --
  sniffed content does (`documents/gate.py`); ingested text is untrusted and carries
  no tool instructions.
- **Supervisor code changes only via the frozen defect/directive lane** -- no
  speculative features; a change needs qualifying evidence (a reproduced defect,
  failed scenario, security risk, provider drift, or a cited D-010/D-024 requirement)
  (`.claude/rules/supervisor-freeze.md`).

---

## 4. HOW DATA MOVES -- critical flows with provenance

**A. BBL -> rule evaluation** (`api/v1/rule_evaluation.py` +
`spatial/live_provider.py` + `profile/builder.py`):

```
BBL path param
  -> normalize_bbl (typed 422 before any network I/O)
  -> PLUTO fetch via injected connector (no request body ever accepted)
  -> [spatial substrate, server-side only, gated OFF by default]
       ZTLDB official assignment -> candidate district layer queries
       -> zoning-features + MapPLUTO geometry -> spatial engine compose
       (ANY connector failure / partial page / empty assignment -> None)
  -> build_property_profile (every fact gets a resolvable provenance_ref)
  -> validate_profile (canonical contract; invalid input -> typed 500, no internals)
  -> evaluate_property (deterministic; legal logic only here)
  -> serialize_rule_evaluation + validate document (invalid 200 impossible)
  -> 200 document w/ X-Correlation-ID
```

Fail-safe is a NORMAL result, not an error: `unsupported` /
`professional_review_required` / `not_applicable` return a valid 200 document; only
genuine faults become typed errors carrying no traceback, path, or secret. The live
spatial provider never fabricates a substrate -- every failure yields `None`, an honest
"no confident district."

**B. Task lifecycle** (`CLAUDE.md` "Task routine"; ADR-005):

```
packet (project-control/tasks/M<x>-T<n>.json, with acceptance scenarios)
  -> worker produces in-scope files + a report
  -> checkpoint (submit-checkpoint; evidence packet in project-control/reports/)
  -> independent review (run-quality-gate; reviewer != producer, read-only)
  -> gates G0-G7 recorded by the orchestrator
  -> accept (orchestrator only; reads directive verification.json as blocking evidence)
```

---

## 5. WHAT MUST STAY TRUE -- invariants and their enforcing mechanism

Each invariant names the mechanism that makes it hold (not honor-system):

- **AI never calculates a legal value.** -> deterministic engine `rules/` owns
  calculation; independent gates verify (`CLAUDE.md` P1; ADR-005).
- **Never guess a schema, unit, field meaning, or effective date.** -> connector
  validators + canonical-contract validation (`validate_profile`,
  `validate_rule_evaluation_document`) + G4/data-contract review
  (`.claude/rules/backend-api.md`).
- **Fail-safe never fabricates.** -> typed substrate + engine review classes; the live
  provider returns `None` on any failure; the spatial rule forbids collapsing
  uncertainty (`spatial/live_provider.py`; `.claude/rules/geospatial.md`).
- **Every material fact retains provenance.** -> `profile/builder.py` re-verifies
  provenance referential integrity; a material value with no provenance record is a
  defect (`CLAUDE.md` P2; `.claude/rules/backend-api.md`).
- **Secrets are server-side only.** -> env-scoped vars + hardened `.gitignore` +
  gitleaks pre-commit hook; frontend gets only publishable `NEXT_PUBLIC_*`
  (`.claude/rules/frontend-web.md`; ADR-004 item 4).
- **Dependency security is fail-closed, incl. the 7-day age gate.** ->
  `services/api/scripts/dependency_age_gate.py` + committed-lockfile age gate; audits
  on every change, no agent waiver (`CLAUDE.md` P15; `.claude/rules/deployment.md`).
- **Modularity thresholds hold.** -> `tools/modularity_check.py`; new files above the
  hard SLOC threshold fail CI without a reviewed expiring exception
  (`.claude/rules/code-architecture.md`).
- **A producer cannot accept its own work.** -> gates + orchestrator-only acceptance;
  reviewers are read-only (`CLAUDE.md` P7; ADR-005).

---

## 6. WHEN AN AGENT MUST STOP

If a task requires breaking an architectural boundary above, do NOT quietly work
around it. Follow the protocol:

```
STOP -> explain the conflict -> show the impact -> propose the smallest change
```

(from the captured D-034 practice). Do not silently introduce a new architectural
pattern, a competing schema, a cross-boundary import, or a bypass to make a task pass.

This repo's named hard stops (stop and create a blocker / ask the owner -- `CLAUDE.md`
principle 13; ADR-006 Tier D):

- a legal or zoning interpretation (owner/qualified-reviewer only, G6);
- credentials, secrets, accounts, or payment;
- production deploy approval;
- **PR #241** -- never merge (`docs/SESSION_HANDOFF.md`; D-023 source);
- any active owner hold (e.g. the expansion-planning hold in
  `.claude/rules/expansion-agent-dispatch-hold.md`).

Evidence rule: **DONE comes only from gates and evidence, never from implementation
alone** (this is already stronger repo law -- G0-G7, producer-cannot-self-accept,
independent verification; `/engineering-reliability`). Anything you could not verify is
stated explicitly as **UNPROVEN**. This document adds no new lifecycle authority; it
makes the intent behind that law legible.
