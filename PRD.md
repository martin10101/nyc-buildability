# Product Requirements Document
## NYC Development Feasibility & Zoning Intelligence Platform

**Working name:** NYC Buildability  
**Document status:** Build-ready v1  
**Primary implementation agent:** Claude Code  
**Architecture:** Cloud-first; no required local data storage  
**Geographic scope:** All five boroughs of New York City  
**Product category:** Preliminary zoning and development feasibility decision-support system

---

## 1. Product vision

Build a cloud application in which a user enters a New York City address or BBL and receives:

1. A consolidated official-data property profile.
2. The zoning and legal rule families potentially applicable to the property.
3. Deterministic calculations for rules that have been converted into approved machine rules.
4. Multiple ranked development scenarios optimized for different objectives.
5. Plain-English explanations with exact source sections and data provenance.
6. Explicit flags for missing information, conflicting government records, unsupported rule families, discretionary approvals, and professional-review requirements.
7. A downloadable feasibility report.

The application is a **preliminary development feasibility assistant**, not a permit approval, legal opinion, architectural certification, engineering analysis, or guarantee of DOB acceptance.

---

## 2. Core product principle

The system must keep these three responsibilities separate:

### A. AI retrieval and interpretation
AI locates, classifies, compares, summarizes, and proposes structured interpretations of government material.

### B. Deterministic calculations
Code performs FAR, floor-area, height, setback, yard, lot-coverage, density, parking, and other numerical checks.

### C. Professional validation
A qualified human reviewer approves or rejects machine-rule interpretations before those rules may be labeled “verified.”

AI may generate a draft rule. AI may never silently publish a draft legal interpretation as a verified rule.

---

## 3. Success definition

A successful initial production release must accept any NYC address and:

- Resolve it to a canonical address and BBL where possible.
- Retrieve available official property and zoning data.
- identify all detected zoning districts, overlays, special districts, split-lot conditions, landmark flags, flood flags, and relevant data conflicts.
- Apply every approved rule supported by the current engine.
- Display unsupported or uncertain areas transparently.
- Generate at least three distinct development scenarios when enough data exists.
- Cite every material input and every legal rule used.
- Preserve source snapshots and rule versions so a historical report can be reproduced.
- Store all persistent application data in cloud services rather than on the user’s PC.

---

## 4. Users and roles

### 4.1 Organization owner
- Manages company account, billing, users, and organization settings.
- Can see all organization projects.
- Can configure default objectives and report branding.

### 4.2 Analyst
- Creates property analyses.
- Confirms or corrects property assumptions.
- Generates and compares scenarios.
- Adds notes and exports reports.

### 4.3 Zoning reviewer
- Reviews AI-extracted rule proposals.
- Compares proposed structured logic against exact source text.
- Approves, edits, rejects, suspends, or supersedes rules.
- Creates test cases for each approved rule.

### 4.4 Administrator
- Manages source connectors, ingestion jobs, failed jobs, system coverage, and rule releases.
- Can inspect source versions and data conflicts.
- Cannot mark a rule verified unless also assigned the zoning-reviewer role.

---

## 5. Primary user flow

1. User signs in.
2. User selects **New Property Analysis**.
3. User enters:
   - Street address and borough, or
   - BBL.
4. System calls the official NYC address/geocoding source.
5. System displays possible matches if ambiguous.
6. User confirms the property.
7. System builds a property profile from official sources.
8. System displays:
   - Confirmed facts
   - Assumed facts
   - Conflicts
   - Missing facts
9. User selects one or more optimization goals.
10. User answers only questions that cannot be obtained reliably from public data.
11. Rules engine calculates applicable constraints.
12. Scenario engine generates and ranks valid or conditionally valid development approaches.
13. User opens any result to see:
   - Input data
   - Formula
   - Applied rule
   - Exact source citation
   - Effective date
   - Confidence/coverage status
   - Assumptions
14. User saves the analysis and exports a report.

---

## 6. Optimization goals

The user may rank or weight:

- Maximum zoning floor area
- Maximum estimated usable/sellable/rentable area
- Maximum dwelling-unit potential
- Maximum residential area
- Maximum commercial area
- Mixed-use opportunity
- Minimum likely approval complexity
- Minimum parking burden
- Minimum construction complexity
- Minimum reliance on discretionary approvals
- Affordable-housing opportunity
- Conservative/low-risk zoning approach
- Compare all materially different feasible approaches

The system must never use the word “best” without identifying the objective being optimized.

---

## 7. Scope of legal and regulatory knowledge

### 7.1 Zoning Resolution
Required for:
- Permitted uses
- FAR and zoning floor area
- Density
- Height and setback
- Base height and street wall
- Yards, courts, and open space
- Lot coverage
- Parking and loading
- Overlays
- Special-purpose districts
- Inclusionary/affordable-housing zoning provisions
- Transit-zone or other mapped modifications
- Definitions and measurement rules
- Special permits and authorizations as flagged possibilities

### 7.2 Basic code-feasibility layer
The first full product must include enough non-zoning feasibility logic to avoid presenting impossible envelopes as practical buildings. Include:
- Approximate core allowance
- Exit/stair count flags
- Elevator assumption
- Corridor and shaft efficiency assumptions
- Lot-line window limitations
- Basic light-and-air feasibility flags
- Approximate floor-to-floor heights
- Accessibility allowance
- Construction/occupancy type questions where they materially affect feasibility

### 7.3 Detailed plan-code compliance
Exact window placement, room-by-room compliance, fire-rating design, structural design, detailed egress geometry, mechanical design, and construction-document approval are outside the first scenario engine. They may be added later as a schematic-layout or plan-review module.

---

## 8. Government-source strategy

The system must use the following priority order:

1. Official API
2. Official Open Data/SODA endpoint
3. Official downloadable CSV, GeoJSON, shapefile, geodatabase, or other structured dataset
4. Official HTML page ingestion
5. Official PDF/document ingestion
6. Controlled browser automation where no structured source exists
7. Manual review only for records that cannot be reliably processed

Screenshots and OCR must not be the default ingestion method.

### 8.1 Mandatory initial official-source families

The API research agent must discover, document, test, and version the best available official sources for:

- NYC Geoclient / Geosupport: address, BBL, BIN, coordinates
- PLUTO / MapPLUTO
- NYC Zoning Tax Lot Database
- NYC GIS Zoning Features
- NYC Zoning Resolution
- DOB NOW Open Data
- BIS or equivalent historical property records
- Certificates of Occupancy data where available
- DOB violations and complaints
- ACRIS master/property/document datasets
- Landmark and historic-district data
- Flood/coastal hazard data
- Pending land-use and zoning-map-change data where available
- Relevant DOB bulletins and code resources
- NYC Construction Codes
- New York State Multiple Dwelling Law or official state source

### 8.2 Source registry requirement

Every external source must have a record containing:

- Source ID
- Agency
- Name
- Official URL
- Source type
- API/dataset identifier
- Authentication requirement
- Rate limits
- Update frequency
- Geographic coverage
- Fields available
- Terms/usage notes
- Connector implementation
- Last successful ingestion
- Latest source version
- Health status
- Known limitations
- Fallback source

No production connector may be created without a source-registry record.

---

## 9. Data provenance

Every fact used in a calculation must preserve:

- Source ID
- Original field name
- Original value
- Normalized value
- Retrieved timestamp
- Dataset version or page/document version
- Effective date where available
- Property/BBL to which it applies
- Confidence
- Whether user confirmed or overrode it
- Conflict status

The system must retain the exact source snapshot used for each report so the report can be reproduced later.

---

## 10. Rule lifecycle

Statuses:

1. `discovered`
2. `extracted_draft`
3. `needs_review`
4. `approved`
5. `published`
6. `suspended`
7. `superseded`
8. `rejected`

Only `published` rules may generate a **Verified** result.

Each rule must contain:

- Stable rule ID
- Title
- Rule family
- Jurisdiction
- Applicability conditions
- Inputs required
- Deterministic expression or function reference
- Output/constraint
- Units
- Priority and override relationships
- General-rule/special-rule relationship
- Exceptions
- Cross-references
- Exact source section
- Source document version
- Effective start/end dates
- Reviewer
- Review timestamp
- Test cases
- Change history
- Release version

---

## 11. Rules DSL

Create a versioned JSON-based domain-specific language capable of representing:

- Boolean applicability conditions
- District/overlay/special-district matching
- Numeric thresholds
- Tables and lookups
- Formulas
- Minimums and maximums
- Piecewise calculations
- Rule priority
- Overrides and modifications
- Exceptions
- Required user questions
- Missing-data behavior
- Conflict behavior
- Result severity
- Source references

Example only:

```json
{
  "rule_id": "NYC-ZR-EXAMPLE-001",
  "version": 1,
  "status": "extracted_draft",
  "family": "maximum_height",
  "applies_when": {
    "all": [
      {"field": "zoning_district", "operator": "in", "value": ["EXAMPLE"]},
      {"field": "development_type", "operator": "eq", "value": "new_building"}
    ]
  },
  "requires": ["street_type", "affordability_option"],
  "calculation": {
    "type": "lookup_table",
    "table_id": "example_height_table",
    "output": "permitted_height_ft"
  },
  "result_check": {
    "left": "proposed_height_ft",
    "operator": "lte",
    "right": "permitted_height_ft"
  },
  "source_refs": [],
  "test_case_ids": []
}
```

Do not hard-code legal text directly into UI components.

---

## 12. Coverage and confidence model

Each result must have exactly one coverage status:

- `verified`
- `conditional`
- `professional_review_required`
- `data_conflict`
- `unsupported`
- `not_applicable`

Each result must also have a data-completeness status:

- `complete`
- `missing_noncritical`
- `missing_critical`

AI confidence scores must never substitute for legal-review status.

---

## 13. Scenario engine

### 13.1 Inputs
- Canonical property profile
- Approved applicable rule set
- User-confirmed assumptions
- Objective weights
- Practical building-efficiency assumptions
- Optional construction-cost assumptions

### 13.2 Outputs
Generate materially distinct scenario families, not cosmetic duplicates:

- Maximum residential
- Residential + commercial
- Conservative/low-complexity
- Affordable-housing or bonus approach where potentially applicable
- Alternate massing approach
- Existing-building enlargement/conversion where user selects it
- Other approaches discovered by the rule system

### 13.3 Scenario fields
- Scenario title
- Objective
- Development type
- Uses
- Zoning floor area by use
- Estimated gross building area
- Estimated net/usable area range
- Height
- Base height
- Stories
- Footprint
- Setbacks/yards
- Dwelling-unit range
- Parking/loading estimate
- Core/efficiency assumptions
- Verified constraints
- Conditional constraints
- Unsupported checks
- Discretionary approvals flagged
- Main advantages
- Main risks
- Score breakdown
- Full provenance

### 13.4 Validation
The engine must reject a scenario when it violates a published hard rule and no explicit exception path applies.

A scenario with unresolved critical information may be shown only as **Conditional** or **Professional Review Required**.

---

## 14. Cloud architecture

### 14.1 Required providers

#### Supabase
Use for:
- Managed PostgreSQL database
- PostGIS geospatial data
- Authentication
- Row Level Security
- Private file/document storage
- pgvector embeddings and semantic retrieval
- Database migrations
- Audit records
- Lightweight scheduled/database jobs

#### Vercel
Use for:
- Next.js web frontend
- Preview deployments

#### Render
Use for:
- Python FastAPI API
- Source ingestion workers
- Geospatial import/normalization workers
- AI extraction jobs
- Scenario-calculation jobs
- Scheduled source monitoring
- Long-running background processing

#### GitHub
Use for:
- Source control
- Pull requests
- CI
- Issues and project milestones
- No confidential client model/data files

### 14.2 Why workers are separate from Supabase Edge Functions

Do not run large PDF parsing, GIS imports, full dataset ingestion, or lengthy AI extraction inside Edge Functions. Use container workers with resumable jobs. Supabase Edge Functions may be used for short authenticated endpoints, webhooks, or lightweight tasks.

### 14.3 No required user-PC storage

Persistent records, documents, embeddings, reports, and analysis results must be stored in the cloud.

The browser may hold:
- Authentication session
- Temporary form state
- Normal HTTP cache

The browser must not be the sole location of any project or legal data.

Provide:
- “Clear local session data” option
- Configurable session timeout
- No sensitive payloads in browser logs
- No API secrets in frontend code

---

## 15. Supabase database domains

Use UUID primary keys and `created_at`, `updated_at` timestamps unless a dataset requires a stable official natural key.

### Identity and tenancy
- `organizations`
- `organization_members`
- `user_profiles`
- `roles`
- `audit_events`

### Sources and ingestion
- `source_registry`
- `source_versions`
- `ingestion_jobs`
- `ingestion_job_events`
- `raw_source_records`
- `source_documents`
- `source_document_versions`
- `source_chunks`
- `source_chunk_embeddings`

### Geographic/property data
- `boroughs`
- `tax_lots`
- `tax_lot_geometries`
- `buildings`
- `addresses`
- `property_source_facts`
- `property_fact_conflicts`
- `zoning_district_geometries`
- `commercial_overlay_geometries`
- `special_district_geometries`
- `landmark_geometries`
- `flood_geometries`
- `pending_land_use_actions`

### Legal/rules
- `legal_sections`
- `legal_section_versions`
- `rule_families`
- `rules`
- `rule_versions`
- `rule_source_links`
- `rule_dependencies`
- `rule_exceptions`
- `rule_test_cases`
- `rule_test_runs`
- `rule_releases`
- `rule_release_members`

### Analysis
- `projects`
- `project_properties`
- `property_profiles`
- `property_profile_facts`
- `user_assumptions`
- `analysis_runs`
- `analysis_results`
- `scenario_runs`
- `scenarios`
- `scenario_metrics`
- `scenario_constraints`
- `scenario_scores`
- `professional_review_items`
- `reports`

### System
- `feature_flags`
- `coverage_matrix`
- `api_connector_health`
- `system_settings`

---

## 16. Supabase Storage buckets

Private by default:

- `source-originals`
- `source-snapshots`
- `source-pdfs`
- `gis-imports`
- `generated-reports`
- `organization-uploads`
- `debug-artifacts`

Apply Row Level Security and signed URLs. Public buckets are prohibited for confidential organization files.

---

## 17. Security

- Multi-tenant organization isolation using Supabase Auth + RLS.
- Service-role key only in trusted backend/worker environments.
- Never expose service-role key in frontend.
- Encrypt provider secrets in deployment secret managers.
- Audit all rule approvals, user overrides, report generation, and administrative changes.
- Rate-limit public endpoints.
- Validate and normalize all address/BBL input.
- Scan uploaded documents before processing.
- Use private storage buckets.
- Add retention policies.
- Add account data export/deletion workflows.
- Prevent prompt injection from ingested government pages:
  - Treat source content as untrusted data.
  - Never allow source text to issue tool instructions.
  - Use strict structured-output schemas.
  - Restrict AI tools in extraction workers.
- Redact secrets and personal data from logs.

---

## 18. Application pages

### Public/auth
- Sign in
- Password reset
- Invitation acceptance

### Main application
- Dashboard
- New analysis
- Address confirmation
- Property profile
- Questions/assumptions
- Scenario comparison
- Scenario detail
- Evidence/source viewer
- Reports
- Saved projects

### Review/admin
- Source registry
- Connector health
- Ingestion jobs
- Source-version comparison
- AI extraction queue
- Rule review
- Rule test cases
- Rule releases
- Coverage matrix
- Conflict review
- User/organization administration
- Audit log

---

## 19. Evidence viewer

Every result must allow the user to inspect:

- Fact or rule used
- Calculation
- Units
- Source agency
- Source dataset/document
- Section/record identifier
- Retrieval/version date
- Exact relevant excerpt
- User overrides
- Rule version
- Test status
- Link to official source

The application must make it impossible to export a material calculation without a provenance record.

---

## 20. Reports

Generate PDF and optionally Excel/JSON.

Report sections:

1. Disclaimer
2. Property identification
3. Data sources and retrieval dates
4. Existing-property summary
5. Zoning profile
6. Detected overlays/special conditions
7. User-confirmed assumptions
8. Scenario comparison
9. Detailed scenario pages
10. Verified calculations
11. Conditional items
12. Professional-review items
13. Data conflicts
14. Unsupported rule families
15. Source citations
16. Rule release/version
17. Reproducibility identifier

---

## 21. API design

Create versioned REST endpoints under `/api/v1`.

Minimum endpoints:

- `POST /resolve-address`
- `GET /properties/{bbl}`
- `POST /properties/{bbl}/refresh`
- `POST /projects`
- `POST /projects/{id}/analyses`
- `GET /analysis-runs/{id}`
- `POST /analysis-runs/{id}/generate-scenarios`
- `GET /scenarios/{id}`
- `POST /reports`
- `GET /reports/{id}`
- `GET /sources`
- `POST /admin/ingestion-jobs`
- `GET /admin/ingestion-jobs/{id}`
- `GET /admin/rules/review-queue`
- `POST /admin/rules/{id}/approve`
- `POST /admin/rules/{id}/reject`
- `POST /admin/rule-releases`

All long-running endpoints return a job ID and are resumable/idempotent.

---

## 22. Job system

Use a database-backed job table or dedicated queue serviced by Render background workers.

Every job must support:
- Idempotency key
- Status
- Progress
- Heartbeat
- Retry count
- Max retries
- Error classification
- Resume cursor/checkpoint
- Input payload
- Output artifact references
- Structured logs
- Cancellation
- Dead-letter/manual-review state

Job types:
- Source discovery
- API schema discovery
- Dataset import
- HTML ingestion
- PDF ingestion
- GIS normalization
- Source diff
- Embedding generation
- Rule extraction
- Rule test execution
- Property refresh
- Scenario generation
- Report generation

---

## 23. AI requirements

### 23.1 Permitted AI tasks
- Official API documentation research
- Connector scaffolding
- Source classification
- HTML/PDF segmentation
- Definition and cross-reference extraction
- Draft rule extraction
- Draft test-case creation
- Ambiguity detection
- Source comparison
- Plain-English explanation
- Code generation
- Unit/integration test generation
- Documentation

### 23.2 Prohibited AI behavior
- Publishing an unreviewed rule as verified
- Inventing missing source values
- Hiding source conflicts
- Claiming permit approval
- Treating model confidence as legal certainty
- Using unofficial summaries where official text is available without clearly labeling them
- Bypassing authentication or access restrictions
- Scraping in violation of source terms
- Capturing credentials in logs

### 23.3 Structured outputs
All production AI extraction must use JSON schemas and be validated server-side. Invalid output is retried or moved to review; it must never be silently coerced into a legal rule.

---

## 24. Testing strategy

### Unit tests
- Rule DSL parser
- Applicability logic
- Formula calculations
- Units/conversions
- Geospatial intersections
- Source normalization
- Scenario scoring
- RLS policies where testable

### Connector contract tests
- Official API response shape
- Field mapping
- Rate-limit handling
- Pagination
- Authentication failure
- Schema drift
- Empty/ambiguous results

### Golden-property tests
Create a growing library of professionally reviewed NYC properties representing:
- Each borough
- Common zoning districts
- Corner/interior/through lots
- Split zoning lots
- Overlays
- Special districts
- Landmarks
- Flood areas
- Existing building/enlargement
- Vacant/new building
- Mixed use
- Data conflicts

Each golden case includes expected property facts, applicable rule families, calculations, and scenario constraints.

### Rule tests
No rule may be published without:
- Positive applicability test
- Negative applicability test
- Boundary-value tests
- Exception test where relevant
- Source citation
- Reviewer approval

### End-to-end tests
Address → BBL → data retrieval → profile → rule evaluation → scenarios → report.

### Security tests
- Cross-organization data access
- Service-key leakage
- Storage access
- Prompt injection
- Malicious upload
- Input validation
- Privilege escalation

---

## 25. Observability

- Structured logs with correlation IDs
- Job dashboards
- Connector health dashboard
- Source freshness alerts
- Rule release audit trail
- Error monitoring
- Performance tracing
- AI token/cost tracking
- Per-analysis cost tracking
- Alerts for schema drift and failed source updates

Never log:
- Passwords
- API secrets
- Full auth tokens
- Confidential uploads
- Unredacted sensitive user data

---

## 26. Delivery phases

### Phase 0 — Repository and cloud foundation
- GitHub repository
- Monorepo structure
- CI
- Supabase project
- Vercel project
- Render FastAPI Web Service + background worker
- Dev/staging/production environments
- Secret management
- Basic auth and organizations

### Phase 1 — Official-source discovery
- Source registry
- Official API/dataset research
- Connector proof tests
- Source documentation
- Health-check framework

### Phase 2 — Citywide property profile
- Address/BBL resolution
- PLUTO/MapPLUTO
- Zoning districts and overlays
- Special districts
- Landmark/flood flags
- Existing DOB/DOF facts
- Data conflict engine
- Property profile UI

### Phase 3 — Legal corpus
- Zoning Resolution ingestion
- HTML/PDF versioning
- Section hierarchy
- Cross-references
- Embeddings/RAG
- Source diffing

### Phase 4 — Rule platform
- Rules DSL
- Extraction pipeline
- Reviewer UI
- Test-case framework
- Releases
- Coverage matrix

### Phase 5 — Scenario engine
- Objective model
- Constraint solver
- Practical efficiency layer
- Multiple scenario generation
- Ranking
- Explanations

### Phase 6 — Reporting, full-system validation, and production launch
- Evidence viewer
- PDF report
- Golden properties
- Client validation against known properties
- Performance/security hardening

### Phase 7 — Expansion
- Additional code-feasibility modules
- Cost/revenue assumptions
- Schematic massing
- Revit integration
- Team collaboration
- External professional-review workflow

---

## 27. Definition of done for the first production release

The first production release is complete when:

1. A user enters one of the client’s known properties.
2. The system resolves the correct BBL.
3. The property profile matches reviewed official data or transparently displays conflicts.
4. The system applies a reviewed set of zoning rules.
5. It generates at least three materially different scenarios.
6. Every important number can be traced to a source and formula.
7. The client can compare the system’s output with their existing manual analysis.
8. No critical error is hidden.
9. The report can be regenerated from stored source and rule versions.
10. A zoning professional signs off on the initial production rule set’s interpretations.

---

## 28. Product boundaries for the first production release

- Guaranteeing DOB approval
- Producing construction documents
- Replacing an architect, engineer, attorney, expediter, or zoning specialist
- Fully detailed apartment layouts
- Structural calculations
- Exact construction cost estimate
- Automatically filing with DOB
- Automatically purchasing or negotiating a property
- Supporting non-NYC jurisdictions

---

## 29. Required disclaimer

Display prominently in the application and reports:

> This platform provides preliminary development and zoning feasibility information based on available public records, user-provided assumptions, and the platform’s current rule coverage. It is not a legal opinion, architectural or engineering certification, DOB determination, permit approval, or guarantee that a proposed development will be approved. Results must be reviewed by qualified New York professionals before reliance, acquisition, design, filing, financing, or construction.

---

## 30. Official starting references for the research agent

Use official sources first:

- NYC API Portal: https://api-portal.nyc.gov/
- NYC Open Data: https://opendata.cityofnewyork.us/
- NYC Department of City Planning data/resources: https://www.nyc.gov/content/planning/pages/resources
- NYC Zoning Resolution: https://zoningresolution.planning.nyc.gov/
- NYC Department of Buildings: https://www.nyc.gov/site/buildings/
- NYC Department of Finance: https://www.nyc.gov/site/finance/
- Supabase documentation: https://supabase.com/docs
- Claude Code documentation: https://code.claude.com/docs

The research agent must verify current endpoints and dataset identifiers rather than assuming URLs from this PRD remain unchanged.

---

## 31. Implementation constraints for Claude

- Research official documentation before choosing an endpoint or library behavior.
- Save research findings with source URL and retrieval date in `docs/research/`.
- Never guess an API schema.
- Add connector fixtures and contract tests before merging a connector.
- Use migrations for every database change.
- Keep legal logic out of frontend components.
- Keep AI-generated draft rules separate from published rules.
- Do not use local-only databases in production.
- Do not expose Supabase service-role credentials.
- Do not call the project production-ready until security, provenance, and golden-property tests pass.


---

## 32. Crisp product-flow requirements

The application must present a simple, controlled sequence even though the backend is complex.

### 32.1 Primary flow

1. `address_entered`
2. `address_resolved`
3. `property_data_loading`
4. `property_data_loaded`
5. `user_confirmation_required`
6. `ready_for_analysis`
7. `rules_evaluating`
8. `rules_evaluated`
9. `scenarios_generating`
10. `scenarios_generated`
11. `report_generating`
12. `report_ready`
13. `failed_recoverable`
14. `blocked_professional_review`

Every analysis run must have exactly one current state. State transitions must be explicit, validated, persisted, and auditable. The AI may not choose or skip workflow states.

### 32.2 Main user experience

The main experience should feel like four clear stages:

1. **Property** — enter address or BBL and choose development objectives.
2. **Confirm** — review official property facts, conflicts, and questions.
3. **Compare** — view ranked, materially different development scenarios.
4. **Evidence** — inspect formulas, assumptions, source facts, legal sections, and review requirements.

Do not expose internal ingestion complexity on the normal analyst screen. Advanced source, rule, and connector operations belong in an administrator/reviewer area.

### 32.3 One canonical property profile

All connectors, rules, scenarios, reports, and UI views must exchange a versioned canonical property-profile contract. Individual modules may not invent competing property schemas.

The profile must contain:

- Identity and address
- BBL/BIN and geometry
- Lot facts
- Existing-building facts
- Zoning districts and mapped features
- Project intent
- Source provenance
- Missing inputs
- Conflicts
- User confirmations and overrides
- Profile version

### 32.4 AI boundaries

AI work must be divided into small, schema-constrained operations such as:

- Classify one legal section
- Extract candidate conditions from one bounded section
- Identify cross-references
- Compare two source versions
- Explain one completed deterministic calculation
- Summarize already-computed scenario risks
- Generate draft test cases that are independently reviewed

A single AI request must never be responsible for retrieving all property data, interpreting the full law, calculating the envelope, generating scenarios, and declaring compliance.

### 32.5 Deterministic workflow control

The backend—not the AI—must control:

- Source selection order
- Workflow state
- Required inputs
- Rule applicability
- Calculations
- Scenario validity
- Coverage labels
- Report completeness
- Retry behavior
- Professional-review escalation

---

## 33. Engineering delivery operating system

The repository must use the project-management, checkpoint, test-scenario, and independent-gate system defined in:

- `docs/AGENT_OPERATING_SYSTEM.md`
- `docs/GATES_AND_CHECKPOINTS.md`
- `docs/PROJECT_CONTROL_PROTOCOL.md`
- `docs/ACCEPTANCE_SCENARIO_STANDARD.md`
- `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`

No implementation task may be marked complete by the agent that performed it. Completion requires an independent gate review with reproducible evidence.

---

## 34. Full-product delivery policy

This project is intended to proceed directly toward the complete citywide product architecture described in this PRD. Development may still be sequenced into milestones and rule releases for engineering control, but temporary shortcuts must not become hidden production behavior.

Each milestone must leave the repository in an integrated, tested state and must advance the production architecture. Mock data, seeded rules, or temporary connectors are permitted only when clearly labeled, isolated behind interfaces, and accompanied by a tracked replacement task.


---

## 35. Low-storage owner-PC constraint

The project owner’s PC has approximately **7 GB of free disk space**. The production and development architecture must therefore be cloud-first and must not require a full local stack.

Mandatory requirements:

- Treat the owner’s PC as a thin client.
- Use GitHub Codespaces or another approved remote development environment for dependency-heavy interactive development.
- Use GitHub Actions for remote builds, tests, and CI validation.
- Use Supabase for persistent database and object storage.
- Use Render for API services, workers, imports, temporary processing, and report generation.
- Use Vercel for frontend deployments and previews.
- Do not install Docker Desktop, a local Supabase stack, PostgreSQL/PostGIS, full citywide datasets, bulk source documents, or embedding indexes on the owner’s PC by default.
- Persistent source files, GIS imports, reports, backups, and AI artifacts must not be stored solely on the local PC.
- Tasks must estimate disk usage during G0 and define cleanup behavior.
- Local execution must preserve at least 4 GB free space and may not intentionally consume more than 2 GB without explicit approval.
- Normal users must access the finished application through a browser and must never need to download citywide datasets.

The controlling implementation details are defined in `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`.
