# Whole-System Trust Replan — Control-Only Proposal (2026-07-23)

**Control-only.** Owner directive 2026-07-23 Part 3. No merge, task movement, claim, dispatch, implementation, acceptance, checkpoint, deployment, purchase, dependency install, or PR closure. This is a **proposal**: it maps every discovered gap to an existing task, a proposed packet area, a blocker, or an explicit continuing limitation. **No new task IDs are contracted** (per the directive — IDs are assigned only after the ledger is reconciled and this proposal is approved). This is a **separate lane from PR #93** (the legal-source/document-corpus lane).

`/replan-project` was invoked. Evidence below is grounded in a read-only codebase inventory (three independent sweeps); file:line citations are to the canonical main tree (`origin/main` = `1acb9b5`).

> **Completeness note (owner directive):** this replan is complete only when every discovered gap has an explicit disposition. §3 (inventory) and §4 (defect matrix) each carry a disposition column; nothing is left in narrative.

---

## 1. Reconciliation (independently verified)

| Item | Value |
|---|---|
| `origin/main` | `1acb9b5` (unchanged) |
| PR #93 | OPEN, head `7ff5304` (rev-5 legal-corpus lane; five packets; not merged) |
| PR #91 | OPEN, superseded (not closed) |
| PR #94 | OPEN (Part 1 frontend-security reconciliation) |
| PR #64 (M0-T019) | OPEN, 115 behind / 8 ahead of main (stale; superseded) |
| Ledger (authoritative main **and** this #95 branch) | **42 accepted / 8 awaiting_gate / 4 backlog / 2 blocked / 1 claimed** |
| Note on "9 backlog" | The five M3 backlog proposals exist **only on unmerged PR #93**. "9 backlog" is the **hypothetical combined state after #93 merges**, not #95's current ledger. This #95 branch adds only a report doc — its backlog count is **4**. |
| M4-T007+ | uncontracted |

---

## 2. End-to-end dataflow trace + immutable-storage hierarchy

**Production surface today = ONE synchronous endpoint.** `GET /api/v1/properties/{bbl}` (`services/api/app/api/v1/properties.py:306`): `normalize_bbl` → injected PLUTO fetcher (resilient) → `build_property_profile(result)` (PLUTO-only) → `validate_profile` → 200. The frontend calls only this (`apps/web/src/lib/api.ts:168`). **No auth, no database, no run orchestrator, no snapshot set, no report/export.**

| # | Boundary | Implementation | Storage / owner | Identity+dates+hash | State model | Retry/timeout/cancel | Invalidation | PRODUCTION-INVOKED |
|---|---|---|---|---|---|---|---|---|
| 1 | address/BBL → identity | `connectors/bbl.py normalize_bbl` (`properties.py:318`) | none (inline) | canonical BBL only | typed 422 on malformed | n/a | n/a | **yes** (BBL only; **no address/geosearch connector wired** despite fixtures) |
| 2 | source connectors | `connectors/pluto_soda.py:600 fetch_by_bbl` → `PlutoFetchResult` | none persisted (result object) | provenance_id, fact_key, value_digest, response_digest, dataset_version, retrieved_at; `effective_date=None` | conflicts, drift_signals, absent_columns | typed errors; drift never retried | digest-based | **PLUTO yes; ZTLDB / MapPLUTO-geometry / zoning-features connectors NO** (built+tested, not wired) |
| 3 | resilience/retrieval (nearest thing to "capture") | `resilience/fetcher.py:146 ResilientPlutoFetcher` | **in-memory `TTLCache` + LKG, process-local, lost on restart** (`resilience/cache.py`, `fetcher.py:105`) | version-segmented cache key; `staleness` stamped | staleness surfaced to profile | bounded retry, breaker, budget; **no cancellation** | TTL/LRU/key-version; LKG superseded on success | **yes** |
| 4 | extraction/normalization | `pluto_soda._normalize_value:525` over 108-col inventory | in result.facts | value_digest/response_digest | drift_signals, absent_columns, notes | inherited | digest | **yes; no AI extraction exists** |
| 5 | canonical profile | `profile/builder.py:557 build_property_profile` → `property_profile@1.4.0` | HTTP body only; `profile_revision` hard-coded `1` | `reproducibility` block (correlation_id, dataset_version, retrieved_at, response_digest, staleness) | 5 independent `status_dimensions`; `rule_coverage="not_computed"` | route 500 guard | none (stateless rebuild) | **yes (PLUTO-only); wave/geometry/spatial keys NO** (route passes none) |
| 6 | source reconciliation | `profile/zoning_crosscheck.py:319 crosscheck_lot_zoning` (PLUTO×ZTLDB×geom) | would flow to profile | canonical facts | typed cross-source conflicts | connector resilience | n/a | **no** (route never passes it; single-source only) |
| 7 | spatial analysis | `spatial/engine.py` (shapely) via `spatial/adapter.py` | result object | policy/geometry-version pins | rich uncertainty taxonomy; PRR | ArcGIS resilience | geometry-version | **no** (rule-eval endpoint hard-defaults spatial substrate to `None`, and is flag-off) |
| 8 | rule applicability & precedence | `rules/integration.py:446 evaluate_property` → `rule_evaluation@1.0.0` | result object | rule_id/version, evaluated_as_of, in_effect | 6 coverage statuses; conflict → FAILSAFE, never auto-picked; caps at `conditional`; `assert_not_verified` | pure | rule lifecycle (no `published`) | **partial — flag-gated OFF** (`config.py INTERNAL_RULE_EVAL_ENABLED`, default 404; no `as_of_date`, no spatial → fail-safe PRR) |
| 9 | deterministic calc (FAR) | `rules/evaluator.py` + `rules/operations.py` + DSL | trace | ZR snapshot pins | fail-closed on unresolved provenance | pure | snapshot-version | **partial — same flag** |
| 10 | scenario generation | `scenario/builder.py:342 build_scenario` → `scenario` schema | result doc | needs_review + not-Verified always | envelope constraints all `missing`; typed `no_scenario` | pure | n/a | **no — no scenario endpoint exists at all** |
| 11 | human review / publication | `rules/lifecycle.py` states; `analysis_state*` schemas | **none — no workflow engine, no persistence, no transition** | — | labels only | — | — | **no** |
| 12 | report / UI / export | `apps/web` profile UI (`lib/contract-matrix.ts`, client re-validate); AbortController+12s timeout | — | — | (status,state) matrix enforced | abort/timeout | — | **profile UI yes; rule-eval surface NO (flag-off); report/export ABSENT** |

**Immutable-storage hierarchy that SHOULD exist (proposed, §5):** raw response bytes (content-addressed, immutable, dedup, replayable) → per-analysis `source_snapshot_set` (compatibility + permitted skew) → canonical entities (versioned) → evidence spans (M3-T003 lane) → rule releases (hashed) → run record (immutable run id, as_of_date, snapshot set, rule release, engine/config hashes) → report (pins the full manifest). **Today none of this is persisted** — "storage" is an in-memory TTL cache (`resilience/cache.py`); `supabase/migrations/` holds only `.gitkeep`.

---

## 3. Inventory of deferred/incomplete work — with dispositions

Every item maps to: an **existing task**, a **proposed packet area** (§5 letter), a **blocker**, or an **explicit continuing non-launch limitation**. Grouped by area. (The ~150 `professional_review_required` rule occurrences are one intentional fail-closed pattern — "no canonical field exposes this modifier" — consolidated under D, not reprinted.)

| # | Item (file:line) | Type | Disposition |
|---|---|---|---|
| A1 | `connectors/mappluto_geometry_arcgis.py:10` deferred geometry connector | deferred task | existing M2 geometry lane (B-001/B-002) |
| A2 | `api/v1/properties.py:141` drift-monitor **STUB** | stub | proposed **B** (orchestrator/source-monitor) |
| A3 | PLUTO/ZTLDB/geometry/zoning-features connectors built but **NOT wired** to production route (§2 rows 2/6/7) | unwired | proposed **A/B** (wire via run orchestrator + snapshot set) |
| A4 | Address/geosearch connector missing (`ConfirmScreen.tsx:209/295`, `PropertyLookup.tsx:302`) | missing connector | proposed **A** + existing M1 (Geoclient B-004) |
| A5 | No immutable capture store; in-memory TTL only (`resilience/cache.py`) | missing infra | proposed **A** (immutable capture) + blocker B-001 (storage) |
| A6 | Connectors on fixtures until keys (`HUMAN_ACTIONS_REQUIRED.md` §4/§7) | fixture-only | blockers B-004 (Geoclient), Socrata token |
| B1 | Rule extraction pending G6 (`rulesets/*.rule.json` limitations) | pending approval | existing M4 + G6 hold |
| C1 | Tax-lot geometry contract deferred; EPSG UNKNOWN (`property_profile.schema.json:61` OPEN-WITH-FLAG) | deferred contract | existing M2 geometry + proposed **C** |
| C2 | zoning-lot ≠ tax-lot documented limitation (`rules/integration.py:297`) | limitation | proposed **C** + M3-T004 closure (PR #93 lane) |
| C3 | geometry not in profile (`ConfirmScreen.tsx:217`) | not wired | proposed **C** |
| D1 | `r5_residential_far.rule.json:89` `special-district-far-modifier (not yet implemented)` | unimplemented modifier | proposed **E** + existing M4 |
| D2 | QRS FAR + per-DU 0.60 equivalent-FAR **not computed** (`r5_residential_far.rule.json:100`) | partial legal-math | proposed **E** + M4 |
| D3 | overlay/special-district/historic/large-site modifiers fail-closed (no canonical field) across `r5*_height`, `r5_setback` | unimplemented modifiers | proposed **C** (fields) + **E** (rules) + M3-T004 closure |
| D4 | R5A pitched-plane setback not reduced to a depth (`r5a_height.rule.json:57`) | uncomputed geometry | proposed **C/E** |
| E1 | scenario foundation only, no endpoint/optimizer (`scenario/__init__.py`) | foundation-only | existing M5-T001 + proposed **H** |
| E2 | only R5 family wired; others → unsupported stub (`scenario/builder.py:774`) | single-family | proposed **E/H** |
| F1 | professional-review workflow UI not available (`ProfessionalReviewPanel.tsx:5`) | deferred UI | proposed **F** |
| F2 | confirmation persistence not wired (`ConfirmScreen.tsx:344/364`) | not wired | proposed **B/F** |
| F3 | financial engine deferred (`property_profile.schema.json:340` Phase C) | deferred engine | proposed **H** (out of near-term launch) |
| G1 | `source_fact.schema.json` **OPEN** (no additionalProperties) — mandatory provenance record accepts extra keys | open contract | proposed **G** (HIGH) |
| G2 | `analysis_state_transition.schema.json` **OPEN** — audit record accepts unknown keys | open contract | proposed **G** |
| G3 | fixture-only schema fields (`scenario.schema.json:105`, `rule_evaluation.schema.json:148`) | fixture-only | keep; proposed **G** negative tests |
| G4 | district-code enums not modeled (`property_profile.schema.json:80` OPEN-WITH-FLAG) | deferred enum | existing M2 zoning-source + proposed **C/G** |
| H1 | internal rule-eval endpoint disabled-by-default (`config.py`, `rule-evaluation.ts:75`) | feature flag | existing M4; flag stays off until §5-E/F land |
| H2 | `supabase/migrations/.gitkeep` only — no RLS/tenancy/storage | missing infra | proposed **I** + blockers B-001/B-002 |
| H3 | D5 production-deploy workflow does not exist (`IMPLEMENTATION_STATUS.md:65`) | unbuilt | proposed **I** + B-012 deploy hold |
| H4 | worker + cron entrypoints REMOVED, "restoration owed" (`render.yaml:137-154`) | removed infra | proposed **B** (restore under real entrypoints) |
| I1 | 3D massing / premium UI / financial / opportunity-search unbuilt (DRAFT-for-review docs) | expansion | expansion hold (owner review) |
| J1 | truncated/bounded reports (`missing-inputs.ts`, `validate-profile.ts:40`) | documented limitation | continuing limitation (disclosed) |

**No item is dropped:** every row has a disposition. Items marked "continuing limitation" or "expansion hold" are explicit non-launch limitations, not silent omissions.

---

## 4. Defect matrix (severity · evidence · consequence · current safeguard · missing control · disposition)

| ID | Sev | Defect + evidence | Mechanical consequence | Current safeguard | Missing control | Proposed disposition |
|---|---|---|---|---|---|---|
| DF-1 | **P0** | **No auth/RLS/tenancy** anywhere; `supabase/migrations/.gitkeep` only; `main.py:6-11` "auth NOT enabled" | any deploy exposes all data cross-tenant | service documented INTERNAL/DEV-only; not deployed | JWT issuer/aud validation, org membership, RLS on every row/object/job/report, positive+negative cross-tenant tests | proposed **I**; blockers B-001/B-002; **B-012 deploy hold** (no public exposure) |
| DF-2 | **P0** | **Legal math on binary float**; `rules/operations.py:41/46/77` (`float(a)`, `round(v,10)`, `a/b`); no `Decimal` in `services/` | FAR/coverage/yard boundary at exact threshold subject to representation error (e.g. exact FAR equality) | 10-dp determinism rounding; fail-closed non-finite guards; geometry floats **isolated** (`evaluator.py:157` reads typed classes only) | Decimal/rational from canonical strings; per-rule rounding mode/scale/order; unit enforcement; adversarial threshold tests | proposed **D**; **owner made this a mandatory blocker for M4 rule publication → B-014** (references M4-T001..T006) |
| DF-3 | **P0** | **No run orchestrator / snapshot set / persistence**; synchronous per-request; `profile_revision` frozen `1` (`builder.py:669`); no DB | a partial multi-source analysis could be presented as complete; no reproducible run; no as_of coherence | single-source PLUTO path only; wave/spatial not wired (can't silently combine) | immutable run id + as_of_date + source_snapshot_set + typed stage states; coherent cache/LKG/breaker across restarts | proposed **A/B**; blocker B-001 (storage) |
| DF-4 | High | **`source_fact` contract OPEN** (`source_fact.schema.json`, no additionalProperties) — mandatory provenance record | undocumented/typo fields silently accepted into provenance | producer uses allowlist dict assembly (`profile/builder.py:297`) | `additionalProperties:false` (or single versioned `extensions`); negative typo/leak tests | proposed **G** |
| DF-5 | High | **`analysis_state_transition` contract OPEN** | audit records accept unknown keys | schema exists but no runtime writes it | close contract; allowlist serializer | proposed **G** (+ **B** when the state machine is built) |
| DF-6 | High | **Optional inputs inside exception predicates fail-OPEN** (`evaluator.py:196` raw two-valued `_eval_predicate`; optional missing only noted `:505-507`) | a missing optional input silently skips an exception that would DOWNGRADE coverage → fail-open miss of an escalation | required + applicability inputs DO use three-valued indeterminate path (`evaluator.py:511-518`) | route optional-input-missing inside an exception to indeterminate/PRR, never false | proposed **E**; amend M4 evaluator |
| DF-7 | High | **No report/export + no report invalidation**; no export module anywhere | changed sources/rules cannot supersede a report; no reproducible artifact | no report exists yet (nothing to mislead) | reports pin the full analysis manifest; supersede/invalidate on upstream change; injection-safe, tenant-scoped signed export | proposed **H** |
| DF-8 | Med | **Connectors not wired to production** (ZTLDB/geometry/zoning-features, crosscheck, spatial — §2 rows 6/7) | citywide analysis runs on PLUTO alone; zoning-lot/spatial facts absent | additive-only builder; route passes none (honest emptiness) | wire via the run orchestrator + snapshot set with reconciliation | proposed **A/B/C** |
| DF-9 | Med | **`semi_corner` risk / lot taxonomy** (directive 3B; `rules/integration.py:297`) | tax-lot area could be mislabeled zoning-lot area | zoning-lot≠tax-lot documented; PLUTO code never sets legal lot type | canonical zoning-lot entity from legal boundary + street lines; corner/interior/through/portions | proposed **C** + M3-T004 closure (PR #93) |
| DF-10 | Med | **`as_of_date` not supplied on any live path** (rule-eval endpoint omits it, `rule_evaluation.py:252`) | no explicit analysis date; law-effective vs vesting vs existing-condition dates not distinguished at runtime | rules engine supports as_of; fail-closed on invalid | thread explicit analysis date + the four date types through the run | proposed **B/E** |
| DF-11 | Low | confidence-as-legal-signal | (none — correctly separated) | `builder.py:283` "NEVER from confidence"; schema warnings | keep separated; add regression that confidence never feeds coverage | proposed **F** (regression only) |

---

## 5. Proposed packet areas (A–J) — ownership, mapping, dependencies

**No new task IDs are contracted here.** Each area maps to existing tasks/milestones where possible; genuinely new responsibilities are named as *proposed packets* for owner approval, then ID-assigned after reconciliation. One owner per source tree/schema/artifact; downstream imports read-only; no overlapping allowed paths; reuse existing resilience/storage/document-security primitives.

| Area | Scope (owner directive) | Maps to / proposed | Key deps |
|---|---|---|---|
| **A** Machine source registry + immutable capture + snapshot sets | machine-readable registry row per `SOURCE_ID` (full field list in §5B); CI rejects unregistered connector/endpoint; exact raw-byte capture, content-addressed/immutable/dedup/replayable; `source_snapshot_set` per analysis with skew rules; coherent-snapshot pagination | extend M1 registry (accepted) → machine-readable + CI gate (**proposed**); **depends on accepted M3-T002** for the generic append-only content-addressed storage primitive, imported **read-only** (ownership resolved in §5C) | **accepted M3-T002** (storage primitive); B-001 storage; M1 (accepted) |
| **B** Analysis-run / job orchestrator | immutable run id, tenant, as_of_date, snapshot set, rule release, engine/config hashes; async/persistent/idempotent/resumable/cancellable; per-source budgets + whole-run deadline; typed stage states; partial-never-complete; coherent cache/LKG/breaker across restarts; restore worker + source-monitor entrypoints | **proposed** (new); `analysis_state*` contracts exist; restore `render.yaml:137-154` worker/cron under real entrypoints | A; B-001/B-002; DF-3 |
| **C** Canonical zoning-lot + physical-context model | distinct address/BBL/tax-lot/condo/building/zoning-lot entities; zoning lot may span tax lots (dated evidence); no MapPLUTO-area-as-zoning-area; frontage/lot-lines/street-lines/street-width class/block-face/legal portions; corner/interior/through/irregular/multi-frontage/remaining-portion; **no `semi_corner`** unless enacted source; missing topology blocks dependent rules | extend M2 geometry (M2-T009 accepted; M2-T014/15/16 survey **HELD**); **proposed** canonical zoning-lot entity; ties to M3-T004 closure (PR #93) | M2 geometry; M3-T004; DF-9 |
| **D** Exact legal math + units | Decimal/rational from canonical strings; per-rule rounding mode/scale/order; unit enforcement; canonical decimal serialization + formula/unit traces; geometry-float isolation with explicit conversions; adversarial threshold/rounding tests | **amend M4** `rules/operations.py`+`evaluator.py` (**proposed** rework); blocks M4 publication | M4 engine; DF-2 |
| **E** Rule applicability, precedence, closure, coverage | true/false/unknown predicates; missing/malformed never false/not_applicable; explicit analysis date + 4 date types; authority-tier ≠ precedence; machine-readable jurisdiction/status/effective-window/scope/amendment/supersession/project-instrument; closure over links/unlinked/defs/tables/footnotes/exceptions/modifiers; coverage certificate; no final value from one matched rule | **M4** rules + **M3-T004** closure (PR #93); fix DF-6 optional-in-exception fail-open; **proposed** coverage-certificate | M3-T004; M4; DF-6/DF-10 |
| **F** Provenance, human review, publication | deprecate generic confidence as legal signal (keep separated); track retrieval-fidelity/normalization/authority/freshness/conflict/review/coverage separately; full derivation graph; immutable user decisions; G6 verifies reviewer authorization+eligible evidence+closure+tests+rule-release hash; approved/suspended/superseded/rejected/revoked; upstream change invalidates downstream without deleting history | **proposed** review workflow + publication state machine (`analysis_state*` runtime); G6 (existing hold) | B (runtime); E; DF-11 |
| **G** Strict versioned contracts | close production objects `additionalProperties:false` or single versioned `extensions`; allowlist serializers; negative typo/undocumented-field/diagnostic-leak tests; schema migration + compat rules | **proposed** contract-hardening (close `source_fact`, `analysis_state_transition`; audit all) | DF-4/DF-5 |
| **H** Scenario, optimizer, 3D, reports | hard/soft constraints + objectives; infeasible/timeout/unsupported/approximate/optimal outcomes; pin solver/version/config/seed/discretization/tolerance/gap; no AI numbers into solver; 3D visualization-only; reports pin manifest + draft/partial/review state; supersede/invalidate; injection-safe tenant-scoped signed export | **M5** (foundation exists) → **proposed** optimizer + reports/export; 3D under **expansion hold** | E; **/dependency-security** for any solver; DF-7 |
| **I-foundation** Auth, tenant identity, RLS, base security contracts | JWT iss/aud, organization membership, tenant identity, RLS, tenant-scoped object ownership, base migration + security contracts; RLS pos+neg tests. **Precedes any persistent B analysis-run records** | **M0-T007/T008** (blocked B-001) + **proposed** RLS/tenancy | B-001; DF-1 |
| **I-operations** Production workers, deploy, observability, ops | production workers, deployment, readiness (≠liveness≠source-health), observability/telemetry/alerting, rate/quota/upload/decompression budgets, durable queue + DLQ + recovery, backup/restore/PITR, retention, incident procedures. **Follows or integrates with the accepted B orchestrator** | **proposed** ops; restore `render.yaml:137-154` worker/cron; **B-012 deploy hold** | **accepted B**; B-001/B-002; DF-1/DF-3 |
| **J** End-to-end expert golden corpus + launch gate | expert-reviewed cases across every borough/lot-type/condo/split-district/overlay/landmark/flood/street-width/vesting/source-mismatch/conflict/outage/stale-cache/restart/schema-drift/pagination/changed-during-read/rounding/unknown-applicability/override/supersession/tenant-isolation; replay/property-based/mutation/metamorphic/differential/failure-injection harnesses; CI deterministic+offline; live smoke separate, never silently updates goldens | **M6** golden-property library → **proposed** expert corpus + launch gate (G7) | all above; §6 |

### 5A. Approval scope — architecture only (NOT contracting)

**Approving or merging #95 approves the ARCHITECTURE only.** It does **not** contract or authorize any A–J implementation. Before any A–J work begins, a **separate control PR** must create exact task IDs with: outputs, allowed/forbidden paths, dependencies, **explicit blocker references**, acceptance preconditions, G0–G5 acceptance scenarios, harness owner, producer-report path, and any control-plane regressions. Until then the A–J holds in §7C are **not** machine-enforced.

### 5B. Machine source-registry — required fields (Area A)

Every registry row (one per connector `SOURCE_ID` and legal/document channel) must carry **at least**: stable **source ID**; official **authority/publisher**; approved **endpoint/domain + dataset identity**; **authentication/credential class**; **rate + pagination limits**; **access/usage terms**; **version/change signals**; **freshness + staleness rules**; **coherent-snapshot method**; **fallback/LKG policy**; **source-health monitoring**; **responsible owner**; and **known limitations + downstream claims blocked**. **CI must reject an unregistered connector or endpoint** (a build-time gate over the registry vs the connector allowlist).

### 5C. Revised dependency graph + M3-T002/A ownership resolution

**Proposed order (owner sequencing decision):** `A + I-foundation → B → I-operations`. C/D/E proceed per their exact dependencies but may **not** be production-wired around A / B / I-foundation.

```
accepted M3-T002 (storage primitive)
        │ (read-only import)
        ▼
   A (registry + capture + snapshot sets) ── + ── I-foundation (auth/tenant/RLS)
        │                                          │
        └──────────────┬───────────────────────────┘
                       ▼
                  B (run orchestrator, persistent runs)
                       │
                       ▼
                 I-operations (workers/deploy/observability/backup)
   C / D / E: per their own deps; NOT production-wired around A/B/I-foundation.
```

**M3-T002 ↔ A ownership (explicit disposition):**
- **A depends on accepted M3-T002** for the generic append-only, content-addressed storage primitive, and **imports that interface read-only**.
- **A separately owns** its own trees: **API-response capture manifests, connector observations, and the `source_snapshot_set` contracts** — all **outside** the M3 legal-corpus-owned trees (`services/api/app/corpus/**`).
- **A may not modify or duplicate `app/corpus/storage`.**
- **If this cross-lane dependency is rejected** (e.g. the owner prefers the legal-corpus and connector-data storage stay fully separate), the fallback is a **neutral shared-storage packet** owned by neither lane, and M3-T002 is updated to consume it. Either way, "reuse" is not left ambiguous.

| Harness | Target area | Deterministic/offline? |
|---|---|---|
| Replay (raw-bytes → identical outputs) | A capture, run reproducibility | yes (frozen fixtures) |
| Property-based (invariants over generated inputs) | D math, E predicates | yes |
| Mutation (does the suite catch a seeded fault?) | D/E/G | yes |
| Metamorphic (relational invariants, e.g. scaling lot area scales FAR cap) | D/E/H | yes |
| Differential (native vs independent recompute) | D math, A snapshot skew | yes |
| Failure-injection (outage/stale/restart/drift/pagination/changed-during-read) | A/B resilience | yes (injected), + **separate scheduled live smoke** |
| Expert golden corpus (borough/lot/condo/overlay/… full list) | J launch gate | yes; live smoke separate and **never silently updates goldens** |

**Rule:** ordinary CI is deterministic + offline (frozen official fixtures); scheduled live-source smoke tests are a separate suite and may never silently update golden expectations.

---

## 7. Holds — classified by how they are actually enforced

**Honesty correction (owner directive):** a hold is only "enforced" if a machine gate, an existing structural fact, or an existing blocker record actually prevents the outcome. A hold named in §5 is **not** machine-enforced merely because §5 says so, and a **proposed** A/B task does **not** inherit B-001 until that task has a real ID and B-001's blocker record explicitly references it. The table below splits holds into three classes.

### 7A. Currently machine-enforced (a gate/precondition actually blocks today)
| Hold | Enforcement |
|---|---|
| Existing M4 rules cannot be accepted (draft/awaiting G6) | ledger: M4-T001..T006 all `awaiting_gate`; the `accept` precondition requires all required gates PASS incl. G6 (not recorded) |
| Fixture-only cannot make **M3-T002 / M3-T003 / M3-T005** accepted (PR #93 lane) | **S9 control-plane regression** proves the CLI blocks their acceptance while **B-001** (which names exactly those three) is open — but only on the **unmerged PR #93 branch**; not in force on main until #93 merges |
| Construction-Code corpus (M3-T005) blocked | on the #93 branch: **B-011** (scope) + **B-001** (storage) reference M3-T005; not in force on main until #93 merges |
| No `verified` label from the rules engine | `assert_not_verified` (`rules/integration.py:38`); coverage caps at `conditional`; profile `rule_coverage="not_computed"` (code on main) |
| Decimal/rational legal math required before M4 rule **publication** (owner decision) | **B-014** (new, this PR) references M4-T001..T006 → blocks their acceptance until exact-decimal math + typed units land; enforced on the #95 branch (in force on main only when this PR merges) |
| Public deployment blocked | **B-012** (Part 1 / PR #94 branch); `render.yaml` autoDeploy off |

### 7B. Structurally prevented only because no downstream task/code exists yet (not a machine gate)
| Hold | Why it holds today |
|---|---|
| M4-T007+ not started | **no M4-T007 task file exists**; nothing to run. This is absence, not enforcement. The further prerequisites (accepted M3-T004 closure + A/C/D/E) become real gates only when M4-T007 is contracted with explicit dependency + blocker references. |
| M5-T001 is foundation only | `scenario/__init__.py` "service-layer only, no endpoint" — **no scenario endpoint exists**; nothing wires it. Absence, not a gate. |
| Built-but-unwired connectors can't mislead | the production route simply never calls them (§2). Absence, not enforcement. |

### 7C. Proposed — NOT yet enforced (require contracting before they bind)
| Intended hold | Not yet enforced because |
|---|---|
| Compatible-snapshot / canonical-zoning-lot / exact-legal-math / three-valued prerequisites gate M4-T007 | these are **§5 proposals**; no task IDs, no blocker records reference M4-T007 yet |
| Proposed A/B ingestion tasks gated by B-001 (durable storage) | **A/B do not inherit B-001** — B-001 references only M3-T002/T003/T005. A/B inherit it only after they receive real IDs and B-001 (or a new blocker) is amended to name them |
| Any "no Verified/complete/buildable unless every required domain evaluated from compatible snapshots under an approved rule release" system-wide guarantee | depends on the run orchestrator (B), coverage certificate (E), and snapshot set (A) that **do not exist yet** |

---

## 8. Dependency & ownership rules (applied to all proposed areas)

- Exactly one owner per source tree/schema/artifact; downstream imports upstream artifacts read-only; **no overlapping allowed paths**.
- Reuse existing `app.resilience.*` (transport/cache/breaker/budget), the M3-T002 content-addressed storage interface, and the M3-T003 shared untrusted-document security surface.
- **No AI/RAG framework** for deterministic legal work.
- Any proposed production/cloud **OCR, paid API, solver, queue, or new parsing library** requires **`/dependency-security`** + a **stop-and-report owner decision** before selection or installation.
- Every eventual packet must carry exact outputs, dependencies, blockers, acceptance preconditions, G0–G5 scenarios, harness owner, and producer-report path (assigned at contracting, not here).

---

## 9. Owner decisions (RECORDED) · paid-service questions · continuing limitations

**Owner decisions RECORDED (owner directive 2026-07-23):**
1. **A–J architecture: approved in principle**, subject to the corrections in this revision — **not yet contracted**. IDs/outputs/paths/deps/blockers/preconditions/scenarios/regressions are created in a separate control PR before any A–J implementation (§5A).
2. **Decimal/rational legal math + typed units: a MANDATORY BLOCKER for M4 rule publication** → recorded as **B-014** (references M4-T001..T006; blocks their acceptance until exact-decimal math + typed units land). This resolves DF-2's disposition.
3. **B-013: age exception DECLINED — WAIT** until `2026-07-28T15:59:32.231Z` (Part 1, PR #94).
4. **Sequencing: `A + I-foundation → B → I-operations`** (§5C); C/D/E per their deps but not production-wired around A/B/I-foundation.
5. **Public deployment holds remain** (B-012).
6. **No implementation follows merely from merging #95** (§5A).

**Paid-service / credential questions (stop-and-report; NOTHING purchased or authorized here):**
- **No purchase is authorized in this proposal.** Exact current pricing must be **re-verified immediately before any owner purchase approval.**
- **Geoclient** access is official and **expected to be free** (B-004, free subscription key).
- **B-002 (Render) is currently `resolved_temporary`** and must be **revalidated before deployment**.
- **The declared production Render architecture includes PAID Starter web services and PAID worker/cron capacity** (not free-tier). **Production Supabase is expected to require Pro/paid** reliability + backup (PITR) features.
- Any future solver / queue / cloud-OCR / paid API / new parsing library → **`/dependency-security` + stop-and-report owner decision** before selection or install.

**Final reports vs bounded diagnostic lists (owner directive item 8):**
- **Bounded API/client error lists are acceptable** (e.g. `missing-inputs.ts`, `validate-profile.ts` "further problems omitted (bounded report)").
- **A final evidence or professional-review report may NEVER silently truncate** material missing inputs, conflicts, citations, or limitations. It **must include the complete machine-readable artifact** or a **visible continuation/pagination** control. This distinction is a requirement on Areas F (review) and H (reports); J1 below is re-scoped to "bounded *diagnostic* lists only".

**Continuing (disclosed) non-launch limitations:**
- PLUTO-only production analysis; ZTLDB/geometry/spatial/rules/scenario not production-invoked (§2).
- No persistence, run orchestrator, report/export, or auth today.
- Bounded/truncated **diagnostic** lists are acceptable; **final reports must not silently truncate** (above).
- 3D massing / premium UI / financial / opportunity-search under expansion hold.

---

## 10. Confirmation

Nothing was merged, moved, claimed, dispatched, implemented, accepted, deployed, purchased, installed, or closed. **Authoritative main ledger unchanged: 42 accepted / 8 awaiting_gate / 4 backlog / 2 blocked / 1 claimed** (this #95 branch adds a report doc + the B-014 blocker record; the five M3 backlog proposals live only on unmerged PR #93; "9 backlog" is the hypothetical post-#93 combined state). This document is a proposal; contracting happens only after owner approval and ID reconciliation. **Merging #95 approves the architecture only — it does not contract or authorize any A–J implementation** (§5A).
