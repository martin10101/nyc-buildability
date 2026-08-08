# D-010 — source-025 (owner amendment 25, VERBATIM): product-first M2-T015 hardening, scope closure, and resumption

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08). Frozen base at capture: `origin/main` =
`1eb29fbf0e0bad881dc7f097d3f454f3e634cbe9`.

Requirement IDs added by this amendment start at `D-010-R242`; no existing source file or
requirement row (D-010-R001..R241) is edited. Relationship to source-024: continues the
supervised-auto product-proof program (M2-T015 then M2-T016), keeps M0-T053 backlog under the
stated blocking conditions, and adds the eight independently-reviewed product-hardening areas plus
the SB-S1..S9 scope-closure obligation as work INSIDE M2-T015 (routing per §10). Anchors used by
requirement rows: `#starting-point`, `#holds`, `#primary`, `#h1-taxonomy`, `#h2-units`,
`#h3-geometry`, `#h4-correction-history`, `#h5-promotion-gate`, `#h6-fixtures`, `#h7-ci-typegen`,
`#h8-preserve`, `#s9-scope-closure`, `#s10-routing`, `#return-sequence`.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> OWNER DIRECTIVE — PRODUCT-FIRST M2-T015 HARDENING, SCOPE CLOSURE, AND RESUMPTION
>
> The current stabilization is accepted as the starting point:
>
> - main: 1eb29fbf0e0bad881dc7f097d3f454f3e634cbe9
> - PR #194: merged
> - M0-T052: accepted; accepted-task count 72
> - B-018: resolved
> - M2-T015: 55%
> - M2-T015 Unit 3a: committed and pushed at 7802c623a51c1526adead56f03dc24c5fecc6910
> - supervised runtime r3: clean and durably paused
> - M0-T053: contracted backlog
> - LIMITED-AUTO: unauthorized
>
> Capture this owner message verbatim through directive-compliance as the next append-only D-010 owner amendment. Decompose it into atomic requirements and bind them to M2-T015 and any genuinely necessary follow-up task.
>
> Do not reopen or redo accepted M0-T052 work.
>
> Do not start another broad supervisor, controller, ACL, configuration, autonomy, or infrastructure-improvement cycle. The supervisor exists to deliver the product.
>
> M0-T053 already contains the demonstrated remaining child-accounting/containment correction. Keep M0-T053 in backlog for now. It must become blocking before any of the following:
>
> - supervised execution on a host that cannot prove the existing C1 Job-Object requirement;
> - a failure of the per-launch C1 containment proof;
> - migration away from the currently verified host;
> - any future LIMITED-AUTO consideration.
>
> M0-T053 does not need to interrupt M2-T015 or M2-T016 while both remain on the verified, C1-pinned Job-Object host. Unless the C1 proof fails, finish the two product proofs first.
>
> Do not touch the M0-T047 nanoid age gate as part of this work. It remains a separate dependency task and must follow its existing date/policy.
>
> ==================================================
> PRIMARY DIRECTION
>
> After the directive capture and routing record are durable, resume M2-T015 from the clean r3 paused checkpoint under SUPERVISED-AUTO.
>
> Continue the already-planned Unit 3b upload gate and Unit 3c storage/test work, but do not declare M2-T015 complete merely because 3b and 3c finish.
>
> The independently reviewed hardening requirements below are part of completing a reliable survey-evidence product, not supervisor work.
>
> Inspect the current M2-T015 plan, acceptance scenarios SB-S1 through SB-S9, Unit-1 contract, Unit-2 architecture/threat model, and Unit-3a code before assigning the exact remaining units.
>
> Use additional bounded M2-T015 implementation units/checkpoints where necessary instead of forcing all work into an oversized Unit 3c diff.
>
> ==================================================
>
> 1. FACT-TYPE TAXONOMY
>    ==================================================
>
> The current survey_evidence v1 contract intentionally keeps fact_type open.
>
> Develop a grounded canonical taxonomy for the survey fact types the deterministic implementation actually supports.
>
> IMPORTANT COMPATIBILITY CORRECTION:
>
> The current schema description says the closed taxonomy may “land as an additive enum.” Restricting an existing open string field to a closed enum is not additive for previously valid payloads.
>
> Do not close or narrow the existing v1 fact_type wire field if that would invalidate previously valid v1 records.
>
> For v1:
>
> - keep the wire field compatible;
> - enforce the supported taxonomy through deterministic application validation;
> - return a typed unsupported_fact_type result for unknown types;
> - do not silently accept an unknown fact as a material buildability input.
>
> Design a properly versioned v2 only if a genuine wire-contract requirement justifies it. Do not create v2 merely for neatness.
>
> ==================================================
> 2. NORMALIZED-VALUE AND UNIT TYPING
>
> Create deterministic rules connecting:
>
> - fact_type;
> - normalized_value shape;
> - units.
>
> Examples include:
>
> - boundary distance → numeric value + supported distance unit;
> - stated lot area → numeric value + supported area unit;
> - boundary bearing/orientation → canonical defined representation + appropriate unit;
> - elevation → numeric value + supported elevation unit;
> - scale statement → canonical scale representation;
> - address/BBL text → string + unitless.
>
> Do not silently coerce, infer, or guess units.
>
> Ambiguous, mixed, missing, or unsupported units must produce a typed visible failure/unresolved condition and must not be promoted.
>
> Preserve v1 compatibility by enforcing these relationships in application validators unless a properly justified v2 becomes necessary.
>
> ==================================================
> 3. CROSS-FIELD GEOMETRY VALIDATION
>
> Implement deterministic application-level validation for relationships JSON Schema cannot prove, including at minimum:
>
> - x_min <= x_max;
> - y_min <= y_max;
> - finite numeric coordinates;
> - coordinate values valid for the declared coordinate space;
> - bounding-box requirements consistent with locator kind;
> - object-reference requirements consistent with vector-object locator kind;
> - no malformed mixing of raster, PDF-page, survey/world, or other coordinate systems;
> - any additional invariants required by the real implementation.
>
> Invalid or contradictory location/geometry evidence must fail closed with a typed, visible result. It must not become canonical geometry.
>
> ==================================================
> 4. CORRECTION-HISTORY INTEGRITY
>
> Implement deterministic integrity validation proving:
>
> - original_value remains immutable;
> - correction history is append-only;
> - correction entries are chronological;
> - every previous_normalized_value and previous_units matches the immediately preceding state;
> - every corrected value/units becomes the next state;
> - the latest corrected value/units agrees with the record’s current normalized_value and units;
> - AI cannot author or impersonate a human correction;
> - correcting actors use a closed authority model;
> - qualified-professional corrections and confirmations have the required identity and time evidence;
> - a malformed or tampered history cannot be loaded, promoted, confirmed, or used.
>
> Add adversarial tests for deletion, reordering, insertion, timestamp reversal, mismatched previous values, mismatched latest values, actor spoofing, and history mutation.
>
> ==================================================
> 5. MATERIAL-EVIDENCE PROMOTION GATE
>
> The v1 contract may continue to allow validation_results = [] as a visible mid-processing state.
>
> Implement the actual backend/application promotion rule.
>
> A material survey fact must not become:
>
> - canonical geometry;
> - a buildability calculation input;
> - an auto_extracted usable result;
> - a professionally usable result;
> - or any other authoritative downstream value
>
> while required deterministic validation is:
>
> - absent;
> - empty;
> - failed;
> - unresolved;
> - incomplete for that fact type;
> - internally inconsistent;
> - or based only on AI/OCR confidence.
>
> High confidence never substitutes for deterministic validation.
>
> Unit 3a currently controls who may request document transitions, but authority alone is not the complete promotion gate. The processing → auto_extracted and professional-confirmation paths must also prove the required evidence/validation preconditions.
>
> Integrate this without allowing AI input to trigger or veto state transitions.
>
> Add executable tests proving that empty, failed, unresolved, incomplete, tampered, or AI-only material evidence cannot cross the gate.
>
> ==================================================
> 6. STRONGER ADVERSARIAL FIXTURE MATRIX
>
> Expand the synthetic fixture and test matrix to cover:
>
> - unsupported fact types;
> - illegal fact_type/value/unit combinations;
> - ambiguous units;
> - unsupported units;
> - mixed units;
> - invalid or reversed bounding boxes;
> - non-finite coordinates;
> - malformed coordinate-space combinations;
> - correction-history deletion, reordering, insertion, and tampering;
> - current normalized value inconsistent with the latest correction;
> - material evidence with validation_results = [];
> - failed or unresolved material evidence attempting promotion;
> - AI/OCR confidence attempting to substitute for validation;
> - confirmation without qualified identity;
> - confirmation without a valid timestamp;
> - actor-role spoofing;
> - conflicting dimensions;
> - conflicting bearings/orientations;
> - conflicting area representations;
> - wrong-address/BBL evidence;
> - tax-lot divergence where the licensed-survey evidence remains visible and is never silently overwritten.
>
> Use synthetic/redacted fixtures only. Do not introduce private client documents.
>
> ==================================================
> 7. CI, TYPE GENERATION, AND REGRESSION COVERAGE
>
> Every deterministic rule added above must have executable tests and join the appropriate normal CI/gate path.
>
> Do not rely on documentation-only assertions.
>
> Before M2-T015 acceptance, reconcile the contract pipeline completely:
>
> - canonical survey_evidence schema;
> - deterministic application validators;
> - generated TypeScript artifact if required by the existing M2-T010/type-generation discipline;
> - runtime schema bundle if required by the existing contract pipeline;
> - valid and invalid fixtures;
> - byte-identical drift checks;
> - API/backend tests;
> - normal repository CI.
>
> The currently allowed packages/contracts/generated/survey_evidence.ts path is not yet populated. Either generate and validate the required artifact through the established tooling or record a concrete, architecture-supported reason why this schema is lawfully excluded. Do not silently leave contract consumers behind.
>
> ==================================================
> 8. PRESERVE THE EXISTING GOOD ARCHITECTURE
>
> Keep these principles intact:
>
> - immutable original-document SHA-256 identity;
> - per-fact evidence lineage;
> - original uploaded bytes never overwritten;
> - OCR advisory only;
> - AI classification bounded and schema-constrained;
> - AI confidence never authoritative;
> - deterministic normalization, reconstruction, calculation, and validation;
> - qualified-human confirmation boundary;
> - tax-lot/MapPLUTO geometry as a typed cross-check only;
> - licensed-survey evidence never silently overwritten by tax-lot geometry;
> - B-001 production-storage hold stated honestly;
> - no production bucket, credentials, tenant-isolation claim, or live tenant-blind upload endpoint while B-001 remains unresolved;
> - safe temporary-file cleanup and abandoned-job scavenging;
> - no parsing outside a verified isolation boundary.
>
> ==================================================
> 9. CLOSE THE EXISTING M2-T015 ACCEPTANCE SCOPE
>
> Before declaring M2-T015 complete, create a concise implementation-and-test coverage matrix for every existing acceptance scenario SB-S1 through SB-S9.
>
> This is not new scope. It is a check that the already-promised product was actually built.
>
> In particular, the current “3b upload gate + 3c storage/tests, then M2-T016” summary does not by itself prove completion of:
>
> - approved-format routing;
> - real vector-PDF extraction;
> - embedded-text extraction where supported;
> - OCR only for scanned text;
> - line/symbol detection for scanned geometry where supported;
> - bounded AI classification with no authority;
> - deterministic geometry reconstruction;
> - boundary closure;
> - area-versus-stated checks;
> - segment sums;
> - contradictory-dimension checks;
> - scale validation;
> - north/orientation validation;
> - elevation validation where present;
> - address/BBL matching;
> - typed tax-lot geometry comparison;
> - wrong-address rejection/review routing;
> - parser-isolation capability enforcement;
> - malicious/malformed document handling;
> - the complete synthetic fixture matrix;
> - full CI and required gates.
>
> Do not mark a scenario complete based only on a schema, architecture document, model class, fake adapter, or test that never exercises the production implementation path.
>
> At least one clean synthetic supported survey path must run through the real implementation end to end and produce per-fact evidence with deterministic verification.
>
> If the required Landlock/seccomp parser-isolation capability cannot be proven on the intended Render substrate:
>
> - do not fall back to unisolated parsing;
> - implement and test the fail-closed capability-gated path in the environment where it can be proven;
> - keep production parsing disabled;
> - record the exact deployment blocker/follow-up;
> - continue every M2-T015 component that does not require pretending the production substrate is ready.
>
> Do not spend days redesigning hosting merely to erase that honest blocker.
>
> ==================================================
> 10. ROUTING AND ANTI-DETOUR RULES
>
> All eight hardening areas appear to belong naturally inside M2-T015 because they directly implement its existing evidence, deterministic-verification, fail-closed, fixture, and CI requirements.
>
> Keep them in M2-T015 unless the lawful task packet genuinely forbids a required path or the work depends on an external blocked capability.
>
> If something must become a follow-up:
>
> - give it a clear product-facing task name;
> - state the exact reason it cannot lawfully or technically complete inside M2-T015;
> - preserve the acceptance hold it creates;
> - do not silently omit the item;
> - do not create a vague research task.
>
> Every new implementation unit must produce working product code and executable tests. Documentation may accompany code but is not a substitute for it.
>
> No speculative enterprise features.
> No general framework rewrite.
> No supervisor redesign.
> No new ACL/config hardening.
> No infrastructure detour without demonstrated product-blocking evidence.
> No deletion of five-borough, zoning, legal, source, survey, scenario, reporting, visualization, or Revit scope.
>
> ==================================================
> REQUIRED ROUTING RETURN, THEN AUTONOMOUS CONTINUATION
>
> After the owner amendment and routing records are durable, return one concise table showing:
>
> 1. each hardening requirement;
> 2. whether it remains inside M2-T015 or becomes a follow-up;
> 3. its exact task and unit/checkpoint ID;
> 4. the code/test paths assigned to it;
> 5. any compatibility reason requiring v2 rather than compatible v1 application validation;
> 6. the SB-S1–SB-S9 coverage assignment.
>
> If the routing faithfully follows this directive and no genuine owner-only choice is required, do not wait for another general confirmation. Resume M2-T015 autonomously under SUPERVISED-AUTO from the clean r3 checkpoint.
>
> Required sequence:
>
> 1. capture this owner directive durably;
> 2. publish the bounded routing/coverage map;
> 3. resume and complete M2-T015 implementation;
> 4. run its full required G0–G5 lifecycle, directive-compliance verification, CI, PR, merge, and acceptance;
> 5. proceed to M2-T016 as supervised-auto product proof #2;
> 6. keep M0-T053 in backlog until both product proofs finish, unless the C1 Job-Object proof fails or the execution host changes;
> 7. after M2-T016, complete M0-T053 before any host relaxation or LIMITED-AUTO discussion;
> 8. LIMITED-AUTO remains unauthorized and requires a separate explicit future owner decision.
>
> Stop and return only for:
>
> - a genuine owner-only decision;
> - production credentials or provisioning;
> - a real external-service blocker;
> - inability to prove the required parser-isolation boundary;
> - a necessary breaking v2 decision that cannot be avoided compatibly;
> - a failed required gate that cannot be corrected within the bounded task;
> - or a demonstrated safety condition requiring the current supervised run to stop.
>
> Otherwise continue building the actual NYC Buildability product.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
