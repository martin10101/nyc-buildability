# M0-T188 look-back: tasks whose allowed_paths carry an entry that binds no tracked file

Backlog DB-181; owner directive D-090-R557; serves D-001-R146 / D-001-R110. Read-only look-back
run with the COMPLETE rule (reviewers' round-2 note 2) over the task files at the M0-T188
claim-seam head `b416cf0d154400ebf1dcaaabc199da4f4e25bc40`. **This report rewrites no task,
gate, verification or directive record** (every `project-control/tasks/**`, `gates/**` and
`directives/**` path is in M0-T188's `forbidden_paths`). It is the evidence that produced the
frozen `PATTERN_ALLOWED_PATHS_GRANDFATHERED` map in `tools/directive_registry.py`.

## Counts (regenerated from the script output; note 5)

- TOTAL tasks with >=1 non-binding entry: **91**
- ACCEPTED: **79**
- IN-FLIGHT (not accepted): **12** = 7 awaiting_gate + 5 backlog (sum 12)
- FROZEN (task, entry) pairs: **249**

The round-1 rule (only `*`, `?`, leading `:`) found 88 tasks. The complete rule adds 3 tasks
whose PROSE-ANNOTATED entries bind nothing -- **M0-T030** and **M0-T031** (accepted) and
**M6-T001** (backlog) -- and additional prose/brace entries on tasks already listed. See
'The stricter rule caught 3 tasks beyond the 88' below.

## What the complete rule refuses, and what it deliberately does not

A `pattern_allowed_paths` OFFENDER is any entry that does NOT bind the literal file/folder a
reader expects under `GIT_LITERAL_PATHSPECS=1`:
- a glob/pattern (`*`, `?`); a leading `:` (pathspec magic);
- an absolute path (leading `/`), a `..` traversal segment, a backslash, or a control char;
- any entry with a character outside the PLAIN set (ASCII letters, digits, `.`, `_`, `-`, `/`,
  space) that is NOT tracked at HEAD -- this catches bracket ranges (`a/[abc].py`), brace sets
  (`a/{b,c}.py`), Unicode star look-alikes, and prose-annotated entries (`x (note)`).

Deliberately NOT refused (with reason): a plain literal path that does not exist yet (a file
the task will create -- emptiness is the separate empty-identity guard's concern); the one
tracked Next.js bracket route `apps/web/src/app/survey/review/[documentId]/page.tsx` (it has
brackets but IS tracked, so it binds correctly). RESIDUAL: a NEW (untracked) path containing an
unusual char -- e.g. a brand-new `[slug]` route -- cannot be pre-declared literally; the
orchestrator adds it literally at integration, or the packet names its parent folder.

## What this means for the recorded identities (plain statement)

Each offending entry resolves to 0 tracked files under literal pathspecs, so the frozen
content-identity hash that submission, the gates and acceptance compared **did not bind the
files those entries declared**; it covered only whatever LITERAL entries bound. This is a
statement about the content-identity hash only; it does not assert the underlying work was
unreviewed (per DB-181, waves 4/5 covered those files by other means; earlier tasks were not
examined). M0-T188 rewrites none of these records (forbidden); it only prevents NEW entries
from repeating the defect and freezes these entries as grandfathered so
`validate_directive_compliance.py --check` stays exit 0.

## The in-flight listed tasks keep non-binding entries until accepted or made literal

The exemption freezes ENTRIES, not ids (note 3), so a listed task cannot ADD a new non-binding
entry and stay exempt. But the **12** still-in-flight listed tasks keep their
EXISTING non-binding entries (frozen) until they are accepted or their packets are made
literal. Their ids: `M0-T021`, `M3-T002`, `M3-T003`, `M3-T004`, `M3-T005`, `M4-T001`, `M4-T002`, `M4-T004`, `M4-T005`, `M4-T006`, `M5-T001`, `M6-T001`.
Recommend a tracked follow-up (keep DB-181 open) to drain these to literal paths before
acceptance (reviewers' G5 F3 / G3 F2).

## The stricter rule caught 3 tasks beyond the round-1 88 (STOP-and-report, per the round-2 prompt)

The round-2 prompt said to STOP and report if the stricter rule would refuse an entry of any
task NOT on the round-1 frozen list. It does -- these 3, whose prose-annotated entries bind
nothing (the same DB-181 defect class the round-1 glob-only rule missed):

- **M0-T030** (accepted): `.github/workflows/ci.yml (ADDITIVE 'code-graph' job only; existing jobs byte-untouched)`; `project-control/tasks/M0-T030.json (via control CLI only)`
- **M0-T031** (accepted): `.claude/skills/start-controlled-task/SKILL.md (ONE additive navigation-guidance paragraph only)`; `CLAUDE.md (ONE additive routing-table row only; context budget check must stay PASS)`; `project-control/tasks/M0-T031.json (via control CLI only)`
- **M6-T001** (backlog): `(implementation paths contracted per-subtask when dispatched - this packet plans; subtasks implement)`

M0-T030 and M0-T031 are ACCEPTED and in-regime: leaving them un-grandfathered would make
`validate --check` (c18) fail on two accepted tasks -- which the KEEP requirement 'every
accepted task still validates' forbids. Their packets cannot be rewritten (forbidden). So the
only action consistent with the other rules is to freeze their pre-existing entries too; the
frozen map therefore holds 91 tasks / 249 pairs, generated by script (never by hand). This
deviation from the prompt's '88' estimate is surfaced here for the orchestrator.

## The look-back script

Generated by the M0-T188 look-back/generation script (`gen_frozen.py`): it reads each task
file at `b416cf0d`, applies `directive_registry.pattern_allowed_paths(entry, root, commit=b416cf0d)`
(the SAME shared detector the CLI and validator use), and records every offending (task, entry)
pair. The detector's rule is documented verbatim in `tools/directive_registry.py`.

## The full mapping (task -> frozen offending entries), by status

### ACCEPTED (79)

```text
M0-T004 [accepted]
    .github/**
    apps/**
    packages/**
    project-control/reports/M0-T004-*
    services/**
M0-T005 [accepted]
    project-control/reports/M0-T005-*
M0-T005-R1 [accepted]
    project-control/reports/M0-T005-R1-*
M0-T006 [accepted]
    docs/adr/**
    project-control/reports/M0-T006-*
M0-T009 [accepted]
    packages/contracts/**
    project-control/reports/M0-T009-*
M0-T010 [accepted]
    project-control/reports/M0-T010-*
M0-T011 [accepted]
    docs/adr/**
    project-control/reports/M0-T011-*
M0-T015 [accepted]
    apps/web/.env.example (names only)
    docs/ deployment runbook file only (exact path confirmed at G0 from M0-T006 records)
    services/api/app/main.py (health/CORS/security-header middleware wiring only)
    services/api/tests/** (new middleware tests only)
M0-T018 [accepted]
    .github/workflows/** (new exact-production-install job + scheduled audit workflow; existing jobs stay green)
    render.yaml (install command / lock artifact reference only)
    services/api/pyproject.toml (metadata alignment only; ranges stay source of truth)
    services/api/requirements.txt (and any generated services/api/requirements*.lock / requirements-prod.txt the chosen lock format needs)
    services/api/scripts/** (lock-generation / audit helper scripts if needed)
M0-T019 [accepted]
    .github/workflows/** (npm tooling pin, blocking audit step, scheduled audit; existing jobs stay green)
    CLAUDE.md (append the concise permanent dependency-security rule ONLY)
    apps/web/.npmrc (or the repo npm config location) for min-release-age/save-exact
    apps/web/package.json, apps/web/package-lock.json
    apps/web/scripts/dependency_age_gate.mjs - deterministic, fail-closed committed-lockfile release-age gate + continuous npm@11.18.0 CLI tooling advisory verification (owner policy-enforcement amendment 2026-07-20; Node ESM, node-builtins only, no npm deps)
    apps/web/scripts/tests/** - the age-gate's deterministic positive / boundary (604800 pass, 604799 fail) / fail-closed unit tests
M0-T020 [accepted]
    .github/workflows/ci.yml and .github/workflows/scheduled-audit.yml ONLY - the Python tooling/build/audit install steps (including the pip installs inside web-e2e); touch ONLY Python package resolution; existing jobs stay green
    .gitignore (the repository ignore rule covering services/api/**/*.egg-info/)
    project-control/reports/M0-T020-producer-report.md (own producer report only)
    services/api/pyproject.toml - STRICTLY LIMITED to the [project.optional-dependencies].dev pytest specifier ('pytest>=8,<9' -> 'pytest>=9.0.3,<10') plus an adjacent explanatory comment if useful; NO other dependency, version cap, or [tool.*] configuration may change (owner bounded amendment 2026-07-20).
    services/api/requirements-tools.in (exact reviewed DIRECT tooling pins - the source manifest)
    services/api/requirements-tools.lock (exact DIRECT + TRANSITIVE tooling pins + SHA-256 hashes; generated from requirements-tools.in by one documented script; byte-identical regeneration)
    services/api/requirements.txt - regenerate with verified uv==0.11.28 and COMPARE to the accepted lock; commit ONLY if byte-identical (i.e. no change). ANY non-byte-identical difference is a STOP condition: return the exact diff + resolver explanation and do NOT commit a changed production runtime lock without a separate owner instruction.
    services/api/scripts/** (lock_requirements.sh update; the ONE documented tooling-lock generation script; the dependency-policy release-age checker and its deterministic tests)
M0-T022 [accepted]
    apps/web/e2e/fixtures/control-plane/**
    apps/web/src/app/dashboard/**
    apps/web/src/components/dashboard/**
    apps/web/src/lib/dashboard/**
    apps/web/src/test-support/dashboard/**
M0-T030 [accepted]
    .github/workflows/ci.yml (ADDITIVE 'code-graph' job only; existing jobs byte-untouched)
    project-control/tasks/M0-T030.json (via control CLI only)
M0-T031 [accepted]
    .claude/skills/start-controlled-task/SKILL.md (ONE additive navigation-guidance paragraph only)
    CLAUDE.md (ONE additive routing-table row only; context budget check must stay PASS)
    project-control/tasks/M0-T031.json (via control CLI only)
M0-T036 [accepted]
    project-control/tasks/M0-T036.json (CLI lifecycle writes only)
    tools/agent_supervisor/** (create; per D-007 Section 6 layout, adjusted to repository conventions)
    tools/test_agent_supervisor_*.py (create)
M0-T041 [accepted]
    tools/test_agent_supervisor_*.py
M0-T042 [accepted]
    tools/test_agent_supervisor_*.py
M0-T044 [accepted]
    tools/test_agent_supervisor_*.py
M0-T045 [accepted]
    tools/test_agent_supervisor_*.py
M0-T046 [accepted]
    tools/test_agent_supervisor_*.py
M0-T048 [accepted]
    tools/test_agent_supervisor_*.py
M0-T049 [accepted]
    tools/test_agent_supervisor_*.py
M0-T050 [accepted]
    tools/test_agent_supervisor_*.py
M0-T051 [accepted]
    tools/test_agent_supervisor_*.py
M0-T181 [accepted]
    project-control/reports/M0-T181-ci-evidence/**
M0-T184 [accepted]
    project-control/reports/M0-T184-ci-evidence/**
M0-T186 [accepted]
    project-control/reports/M0-T186-ci-evidence/**
M1-T001 [accepted]
    docs/research/pluto-mappluto-*
    docs/research/source-registry-drafts/pluto-mappluto*
    project-control/reports/M1-T001-*
M1-T002 [accepted]
    project-control/reports/M1-T002-*
    services/api/app/connectors/**
    services/api/tests/connectors/**
    services/api/tests/fixtures/pluto/**
M1-T003 [accepted]
    docs/research/zoning-features-ztldb-*
    project-control/reports/M1-T003-*
M1-T004 [accepted]
    docs/research/zoning-resolution-*
    project-control/reports/M1-T004-*
M1-T005 [accepted]
    project-control/reports/M1-T005-*
    services/api/app/api/**
    services/api/app/profile/**
    services/api/tests/**
M1-T006 [accepted]
    .github/scripts/tests/**
    packages/contracts/**
M1-T007 [accepted]
    docs/research/fixtures/m1-t007/**
M1-T008 [accepted]
    services/api/tests/fixtures/** (KB-scale representative fixtures only, if needed)
M1-T009 [accepted]
    .github/workflows/ci.yml (ADDITIVE only)
    services/api/**
M2-T001 [accepted]
    .github/workflows/ci.yml (ADDITIVE web job only - existing jobs untouched)
    apps/web/**
M2-T002 [accepted]
    .github/workflows/ci.yml (ADDITIVE changes to the web job only)
    apps/web/**
M2-T003 [accepted]
    .github/workflows/ci.yml (ADDITIVE type-generation drift check only)
    packages/contracts/**
    services/api/**
M2-T004 [accepted]
    .github/workflows/ci.yml (ADDITIVE only)
    ORCHESTRATOR SCOPE AMENDMENT 2026-07-17 (G1 correction C1 / G3 defect D1): apps/web/src/components/property/__tests__/property-lookup.test.tsx and apps/web/e2e/primary-journey.spec.ts ONLY - the two M2-T001 assertions that hard-coded the retired 108-column completeness value; correction applied by the orchestrator, not the producer, and re-reviewed at the gate delta
    packages/contracts/**
    services/api/** (EXCEPT services/api/requirements.txt and services/api/app/main.py - reserved for M0-T015 during Wave 1)
M2-T005 [accepted]
    apps/web/**
M2-T006 [accepted]
    apps/web/src/lib/__tests__/validate-profile.test.ts (AMENDMENT A1: the version-pin assertion update required by the same vocabulary change ONLY)
    apps/web/src/lib/contract.ts (AMENDMENT A1 2026-07-17: runtime supported-versions vocabulary addition of 1.3.0 ONLY - the client pins a closed SUPPORTED_CONTRACT_VERSIONS set that would reject 1.3.0 payloads at runtime and break the real-builder e2e harness; discovered by the producer per the original STOP condition, packet amended by the orchestrator instead of a follow-up packet because the version bump is atomic by design)
    packages/contracts/**
    services/api/**
M2-T007 [accepted]
    services/api/app/connectors/** (new zoning-features module(s) only; pluto_soda.py and bbl.py may not be modified)
    services/api/tests/connectors/** (new zoning-features test module(s) only; existing test files may not be modified)
    services/api/tests/fixtures/zoning_features/**
M2-T008 [accepted]
    services/api/app/connectors/** (new ZTLDB module(s) only; existing connector files may not be modified)
    services/api/app/profile/** (cross-check/conflict integration ONLY, within contract 1.3.0; no contract-shape changes)
    services/api/tests/connectors/** (new ZTLDB test module(s); existing test files only where the cross-check integration genuinely requires an additive assertion, disclosed in the report)
    services/api/tests/fixtures/ztldb/**
    services/api/tests/profile/** (cross-check integration tests)
M2-T009 [accepted]
    services/api/app/connectors/** (new geometry module(s) only; existing connector files may not be modified)
    services/api/requirements*.txt / pyproject dependency pin for Shapely ONLY if not already present (disclosed in report; version pinned exactly; CI green required)
    services/api/tests/connectors/** (new geometry test module(s) only)
    services/api/tests/fixtures/mappluto_geometry/**
M2-T010 [accepted]
    .github/workflows/** ONLY if the derivation requires a pipeline step change - disclose in report; existing jobs must stay green
    apps/web/src/lib/__tests__/** (regression tests)
    apps/web/src/lib/contract.ts and apps/web/src/lib/validate-profile.ts (derivation consumption only)
    packages/contracts/** (generation tooling only; NO version additions, NO semantic schema changes)
    services/api/app/profile/contract.py (module docstring correction ONLY)
    services/api/tests/api/** ONLY (docstring/packaging-related test touch only if genuinely required, disclosed; NARROWED 2026-07-20 for disjointness with the parallel M2-T011 task - services/api/tests/{connectors,resilience}/** are M2-T011 territory)
M2-T011 [accepted]
    docs/SOURCE_ACCESS_REGISTRY.md (new canonical registry)
    docs/research/source-registry-drafts/** (additive corrections only, disclosed)
    services/api/app/connectors/** (transport-loop extraction only; connector semantics preserved)
    services/api/app/resilience/** (shared module home if placed here)
    services/api/tests/connectors/**, services/api/tests/resilience/** (import updates and new consolidation tests)
M2-T012 [accepted]
    apps/web/src/lib/** (derived declarations + validation consumption)
    packages/contracts/** (1.4.0 publication through M2-T010 tooling)
    services/api/app/_contract_schemas/** (via the sync tooling only)
    services/api/app/api/v1/** (typed error surface only if the new keys require it, disclosed)
    services/api/app/connectors/** and services/api/app/resilience/** ONLY for the enumerated carried defects (each touch disclosed per-defect)
    services/api/app/profile/**
    services/api/tests/**, apps/web/src/lib/__tests__/**
M2-T013 [accepted]
    docs/research/** (V1/V2 accuracy-evidence extracts, small, retrieval-dated)
    services/api/app/spatial/** (new module)
    services/api/tests/spatial/** (new tests + fixtures reusing committed connector fixture packs by reference)
M2-T014 [accepted]
    docs/SOURCE_ACCESS_REGISTRY.md (additive rows only, if it exists at execution time)
    docs/research/fixtures/m2-t014/** (small representative response/metadata extracts only, low-storage policy)
    docs/research/source-registry-drafts/** (additive rows)
M2-T015 [accepted]
    packages/contracts/fixtures/invalid/survey_evidence/**
    packages/contracts/fixtures/valid/survey_evidence/**
    services/api/app/documents/**
    services/api/tests/documents/**
M2-T021 [accepted]
    services/api/app/connectors/**
    services/api/tests/connectors/**
    services/api/tests/fixtures/geoclient/**
M4-T009 [accepted]
    services/api/app/rules/rulesets/**
    services/api/tests/rules/**
M4-T023 [accepted]
    docs/zoning-rule-review/**
    services/api/app/rules/review_register/**
M4-T024 [accepted]
    docs/reference-cases/R6B/**
    services/api/tests/rules/reference_cases/**
M4-T025 [accepted]
    docs/research/zr-snapshots/v1/**
    services/api/app/_zr_snapshots/v1/**
M4-T026 [accepted]
    docs/research/zr-snapshots/v1/**
    services/api/app/_zr_snapshots/v1/**
M4-T027 [accepted]
    docs/reference-cases/R6B/**
    services/api/tests/rules/reference_cases/**
M4-T028 [accepted]
    docs/reference-cases/R6B/**
    services/api/tests/rules/reference_cases/**
M4-T029 [accepted]
    docs/research/zr-snapshots/v1/**
    services/api/app/_zr_snapshots/v1/**
M4-T030 [accepted]
    docs/reference-cases/R6B/**
    services/api/tests/rules/reference_cases/**
M4-T031 [accepted]
    docs/research/zr-snapshots/v1/**
    services/api/app/_zr_snapshots/v1/**
M4-T032 [accepted]
    docs/reference-cases/R6B/**
    services/api/tests/rules/reference_cases/**
M4-T033 [accepted]
    docs/research/zr-snapshots/v1/**
    services/api/app/_zr_snapshots/v1/**
M4-T034 [accepted]
    docs/research/zr-snapshots/v1/**
    services/api/app/_zr_snapshots/v1/**
M5-T004 [accepted]
    apps/web/src/app/property/compare/**
    apps/web/src/components/compare/**
    apps/web/src/lib/scenario-*
M5-T018 [accepted]
    apps/web/src/components/compare/**
M5-T048 [accepted]
    packages/contracts/fixtures/invalid/scenario/**
    packages/contracts/fixtures/semantically_invalid/scenario/**
    packages/contracts/fixtures/valid/scenario/**
M5-T051 [accepted]
    services/api/tests/scenario/fixtures/derivation/**
M5-T054 [accepted]
    services/api/tests/rules/fixtures/proposal_checks/**
M5-T066 [accepted]
    apps/web/src/components/architect/ProposalOutlineMap*.tsx
    apps/web/src/components/architect/__tests__/proposal-outline-map*.test.tsx
M5-T073 [accepted]
    services/api/tests/connectors/fixtures/bridge_ring_pairs/**
M5-T089 [accepted]
    services/api/tests/fixtures/building_footprints/**
M5-T096 [accepted]
    docs/samples/cad/**
M5-T126 [accepted]
    docs/measurement-basis/**
    services/api/tests/scenario/measurement_basis/**
M5-T129 [accepted]
    services/api/app/scenario/three_answers/result_way_*.py
    services/api/tests/scenario/three_answers/test_result_ways_*.py
M5-T130 [accepted]
    services/api/app/scenario/three_answers/result_way_bridge_*.py
    services/api/tests/scenario/three_answers/test_result_way_bridge_*.py
M5-T132 [accepted]
    services/api/app/scenario/three_answers/result_way_*.py
    services/api/tests/scenario/three_answers/test_result_way_*.py
    services/api/tests/scenario/three_answers/test_result_ways_*.py
M5-T133 [accepted]
    docs/measurement-basis/**
    services/api/tests/scenario/measurement_basis/**
```

### IN-FLIGHT (12)

```text
M0-T021 [awaiting_gate]
    services/api/scripts/tests/**
M3-T002 [backlog]
    infra/ingestion/**
    project-control/reports/M3-T002-producer-report.md, project-control/reports/M3-T002-source-capture.md
    services/api/app/corpus/ingest/** (OWNED by M3-T002)
    services/api/app/corpus/storage/** (OWNED by M3-T002)
    services/api/app/corpus/versioning/** (OWNED by M3-T002)
    services/api/tests/corpus/ingest/**, services/api/tests/corpus/storage/**, services/api/tests/corpus/versioning/**
    services/api/tests/fixtures/corpus/capture/**
M3-T003 [backlog]
    packages/contracts/schemas/v1/fixtures/{document_classification,extraction_run,evidence_span,cross_source_comparison,human_review_decision}/**
    packages/contracts/schemas/v1/{document_classification,extraction_run,evidence_span,cross_source_comparison,human_review_decision}.schema.json (NEW additive)
    project-control/reports/M3-T003-producer-report.md, project-control/reports/M3-T003-dependency-security.md
    requirements/lock updates ONLY via the approved /dependency-security process for the selected PDF/OCR library (exact-pinned; recorded in M3-T003-dependency-security.md)
    services/api/app/corpus/document_validation/** (OWNED)
    services/api/app/corpus/evidence/** (OWNED)
    services/api/app/corpus/extractors/** (OWNED)
    services/api/tests/corpus/evidence/**
    services/api/tests/fixtures/corpus/evidence/**
M3-T004 [backlog]
    packages/contracts/schemas/v1/closure_manifest.schema.json (NEW additive)
    packages/contracts/schemas/v1/fixtures/closure_manifest/**
    services/api/app/corpus/closure/** (OWNED by M3-T004; exclusive)
    services/api/tests/corpus/closure/**
    services/api/tests/fixtures/corpus/closure/**
M3-T005 [backlog]
    docs/SOURCE_ACCESS_REGISTRY.md (additive G1 evidence only)
    project-control/reports/M3-T005-producer-report.md, project-control/reports/M3-T005-source-capture.md
    services/api/app/corpus/construction_code/** (OWNED by M3-T005; exclusive)
    services/api/app/corpus/overlay/** (OWNED by M3-T005; exclusive)
    services/api/tests/corpus/construction_code/**, services/api/tests/corpus/overlay/**
    services/api/tests/fixtures/corpus/construction_code/**
M4-T001 [awaiting_gate]
    docs/research/zoning-resolution snapshots location as defined in the architecture doc (small section-level extracts only, low-storage)
    packages/contracts/schemas/v1/** rule-definition/evaluation-trace schemas via M2-T010 tooling (additive only, disclosed)
    services/api/app/rules/** (new module)
    services/api/tests/rules/**
M4-T002 [awaiting_gate]
    services/api/app/rules/** (new integration module; consume profile/spatial via read-only imports only)
    services/api/tests/rules/**
M4-T004 [awaiting_gate]
    services/api/tests/rules/**
M4-T005 [awaiting_gate]
    apps/web/e2e/**
    apps/web/src/app/property/**
    apps/web/src/components/property/**
    apps/web/src/components/rule-evaluation/**
    apps/web/src/test-support/**
    packages/contracts/fixtures/invalid/rule_evaluation/**
    packages/contracts/fixtures/valid/rule_evaluation/**
    packages/contracts/scripts/tests/**
    services/api/app/_zr_snapshots/**
    services/api/tests/api/**
    services/api/tests/contracts/**
    services/api/tests/rules/**
M4-T006 [awaiting_gate]
    project-control/reports/M4-T006-producer-report.md, project-control/reports/M4-T006-input-readiness-matrix.md, project-control/reports/M4-T006-source-capture.md
    services/api/app/_zr_snapshots/v1/*.snapshot.json + the sync_zr_snapshots source dir (NEW official ZR snapshots, byte-identical + hash-guarded, package-data per M4-T005)
    services/api/app/rules/rulesets/*.rule.json (NEW R5 height/setback ruleset file(s); do NOT edit r5_residential_far.rule.json)
    services/api/app/rules/schemas/v1/*.schema.json (ONLY if an additive min/max height-setback DSL field is required; extend additively, never redefine)
    services/api/tests/rules/** (deterministic, fail-closed, effective-date, provenance, rule-conflict, negative-control NC-1..NC-7, installed-wheel deployability tests)
M5-T001 [awaiting_gate]
    packages/contracts/schemas/v1/scenario.schema.json (new ADDITIVE draft output contract; reference coverage_status narrowed to exclude 'verified', never redefined) + its generated typegen/runtime-bundle/fixtures under the existing generated/fixture dirs
    services/api/app/scenario/** (new deterministic foundation module + typed constraint/completeness model; consume profile/rule-evaluation via read-only imports only)
    services/api/tests/scenario/** (acceptance pack AS-1..AS-12)
M6-T001 [backlog]
    (implementation paths contracted per-subtask when dispatched - this packet plans; subtasks implement)
```

## Freezing and regeneration

`PATTERN_ALLOWED_PATHS_GRANDFATHERED` is this exact map (stored compactly as chunked JSON to
respect the modularity growth limit). It NEVER grows by hand -- regenerate by script. Because
M0-T188's tool commits integrate LAST, the orchestrator regenerates the map at the integration
head; a task that drained its non-binding entries to literal paths before then simply resolves
clean and no longer needs the exemption. M0-T188's own allowed_paths are all literal, so it is
correctly absent from the map.
