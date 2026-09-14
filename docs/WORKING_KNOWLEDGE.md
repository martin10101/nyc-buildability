# WORKING_KNOWLEDGE — current section: street-width / A2 geometry + C-district lanes (D-054 Tier 2)

Living file for the section under construction NOW. Handoff names it a must-read; update it
while working; at section close PRUNE finished material (git keeps history) or PROMOTE
durable items to `.claude/rules/PROGRAM_KNOWLEDGE.md`. Ledger stays authoritative.

## Wave-4: CLOSED (pruned per D-054-R003 — detail in git history + the DCV report)

- M4-T018 (203rd) + M4-T019 (204th) ACCEPTED; 20/20 DCV rows PASS
  (`reports/M4-T018-M4-T019-dcv-verification.md`); checkpoint CP-2026-09-14-wave4-closed.
  Nothing in flight. Next big block: D-053 relaunch (section below).

## A2 build map (B-lanes; statuses)

- B5 ruling = DONE (D-052). B6 = DONE (M4-T018 report = the pin). B3 (geometry
  parse-and-expose sibling module — geometry ALREADY arrives, parse_segment_page discards
  it), B4 (100-ft buffer engine, EPSG:2263; B3 + mappluto_geometry_arcgis), B7 (wire into
  r6_r7_r8_wide_street_conditional_far.rule.json — currently cites zr-23-22 ONLY, performs
  no wide-street determination) = OPEN. Do B7 LAST.
- **B7 acceptance criterion (G3 advisory A1, elevated):** `exceptions_checked=True` only when
  exceptions checked AND (none apply OR each applicable one implemented/resolved);
  `frontage_match_method=coverage_established` only after real multi-feature collection
  (E 96 St segmentation). Policy API: any non-{wide,narrow} decision = "not classified" —
  don't key routing solely off routed_to (G3 A4).
- T019 leftovers for B7/next packet: 3 concrete inequality test cases (`<=74`→narrow,
  `<80`→UNRESOLVED, `>60`→UNRESOLVED, G3 A2); optionally persist classifier `basis` (A3);
  genuine conflicting-records test + per-rule fallback tests (G4 F2/advisories);
  per-field no-default assertion = standard guard for any new attestation dataclass.

## Exception-rule build inputs (from M4-T018 report §3)

- Named-street override table: 2 rows (Broadway W94–97 Mn CD7; Allen St Rivington–Delancey
  Mn CD3), legislative facts w/ §12-10 anchors — needs a CD+cross-street matcher (nothing
  accepted keys on those today), distinct override provenance code. OPEN: "separated by
  mapped public park" grammatical scope; "may be considered" vs "is" (both routed, G6-class).
- C5-3/C6-4/C6-6 alternate-width test: avg ≥75 AND min ≥65 per portion — needs portion-level
  avg/min width NO accepted connector computes. 70-ft connector clause (<700 ft between two
  ≥75 portions) similarly geometric.
- Snapshot-update task (rules-engineer, separate): zr-12-10.snapshot.json carries superseded
  flat-75 text (retrieved 2026-07-22, AFTER the 3/26/2026 amendment — already stale at
  capture); carriers = snapshot + M4-T013 report + r5_setback.rule.json;
  `section_last_amended: 2024-12-05` metadata defect (page banner, not the term stamp).
  Corrective addendum flows to carriers; conflict visible; NO re-adjudication of past
  acceptances without qualified-human ruling (G1 advisory 1).

## C-district build (from accepted M4-T017 §9)

- 3 bounded families: (1) overlay commercial FAR (33-121, 20 rows, keyed by UNDERLYING R
  district; image-rendered-PDF rows need text-source spot-check — G1 A1 row list in
  M4-T017-G1 report); (2) standalone FAR (33-122/123) — REPORT IS STRUCTURAL-ONLY, family-2
  research must capture values from a text source (F5/A2; owner research has the values as
  discovery aid: C4-6=3.4, C4-7=10.0, non-monotonic); (3) equivalents ROUTING (34-112,
  C4-6→R10) — reuses residential rule files unmodified. 34-111 substitutions (GTZ qualifying
  R1–R5→R5; non-qualifying R1/R2→R3-2) run BEFORE residential rule selection. 35-31 mixed
  caps NOT additive; 35-32 qualifying-site 2.5 GTZ. OQ-3(T017)=33-121 R9A 7.50 vs rule 7.52
  factual check. 32-121/122: no residential in C7/C8, C3A building-type limits.

## Research-channel state (D-050)

- Queue: RQ-003/RQ-004 ANSWERED (consume in D-049-R004 conversion task + A4 triage → then
  SATISFIED/Closed register). RQ-005 residual OPEN: DCM field-level width convention — DCP
  email draft ready in `docs/research/owner-research/RQ005_Independent_Confirmation_…md`
  (owner sends; DCPOpendata@planning.nyc.gov); per-frontage closes via Section/Alteration
  Maps (index in DCP labs-layers-api config; PDFs at nycdcp-dcm-alteration-maps DO spaces).
- Qualifying-residential-site (RQ-003 yield, for the D-049-R004 conversion packet): routes
  (a)(1)–(c) + affordability paragraph; §114-02 excludes >5-acre 2024-12-05 Special Bay
  Ridge lots — §12-10-only eligibility function is WRONG; cross-refs §23-21/§23-424
  (35/35, 35/45, 45/55)/§27-111/§66-11; print/PDF capture still owed.

## D-053 loop — shift 1 COMPLETE (persistent-local-34 closed benignly at unit completion)

- **Run persistent-local-34 (M4-T020 B3) FINISHED its unit**: worker built the module, ran
  all four documented commands auto-approved (audit seq 838–844), `claude_unit_completed`
  seq 845; close = the benign checkpoint refusal (seq 846: worktree-FIELD mismatch,
  'wt-m4t020' vs full path — same DL-class as the starting_sha variant) → synchronous stop.
  **Work verified green by the orchestrator (39 tests + ruff) and COMMITTED at wt-m4t020
  `d7766b8d`** (branch task/M4-T020-dcm-geometry). NEXT for M4-T020: cherry-pick to
  candidate, submit + G3/G4 wave + DCV + accept (normal arc).
- **Relaunch pattern for shift 2** (successor): adapt `scratchpad/relaunch_m4t020.ps1`
  (new packet/branch, fresh run-id persistent-local-35+); down-state drill first
  (pending-approvals denies w/ \r-strip, clear-recovery from PAUSED_RECOVERY, worktree
  reset to claim head). **D-058-R004: worker stays claude-fable-5 via EXTRA USAGE**
  (regular weekly exhausted per owner; opus chain = genuine-hard-stop last resort only,
  never a pin flip).
- **D-055 (owner, captured+executed 2026-09-14)**: Fable while it lasts for main + reviewers —
  model_selection.toml = fable-5 w/ ["claude-opus-4-8"] quota fallback (D-036 revert done);
  five gate-reviewer agent files (89c4e304 set) back to `model: claude-fable-5`, effort key
  removed. Standing cycles stay armed: on the next exhaustion, worker falls back via
  reason_code quota_exhausted; reviewer files flip per reviewer-model-fallback (revert on
  owner's next "Fable is back"). D-047 sonnet-5 loop-allowlist item still open (owner
  settings, D-053-R004).
- Launch traps proven this arc: classifier-block → capture-directive-then-retry-once
  (promoted to Tier 1); owner `!`-prefix attempt produced NO artifacts (script never ran).
  MapLibre trap (M5-T025 G3-corrected root cause): a one-time `load` listener as the SOLE
  draw contingency never fires on a degraded-GL device — always arm `style.load` + an
  `error` handler; `isStyleLoaded()` fast path = defense-in-depth.
- Posture now: **quiet monitor + owner bridge only** (R002/R003); NO auto-accept/merge (R595
  shadow); gates/acceptance stamped by the orchestrator at the seam; relaunch-per-task via
  `scratchpad/relaunch_m4t020.ps1` pattern (new packet path/branch/run-id each time).
- Wave-5 queue after M4-T020: B4 buffer engine, zr-12-10 snapshot-update task, C-district
  families 1–3, B7 wiring LAST (G3-A1 acceptance criterion).

## D-043 owner walkthrough findings (2026-09-14, live Render deploy)

- Deploy WORKS end-to-end on the owner's device: web service created by hand per the
  checklist; `?ruleeval=on` address flow resolves live (CORS correct), confirm card +
  property profile + provenance disclosures render. This is the D-043-R001 evidence leg
  (owner-confirmed live URL). Real URLs stay out of repo/chat per D-043-R002.
- **Finding 1 (confirmed, candidate packet): provenance panel has no outbound source link.**
  `ProvenanceDisclosure.tsx` renders `source_id` (internal slug e.g. nyc-dcp-pluto-soda),
  `dataset_id`, and only `urlHost(request_url)` as TEXT. A safe clickable link is
  constructible TODAY without reflecting any server string: constant allowlisted host +
  validated dataset-id token → `https://data.cityofnewyork.us/d/<dataset_id>` (same
  constant-prefix + validated-token pattern as the ZoLa link, G5 F-1 discipline). Small
  focused web packet; same treatment applies to RuleEvaluationResult.tsx line ~135.
- Finding 2 (pending owner retest): lot-outline map shows gray panel — outline may just be
  SMALL (fitBounds maxZoom 18 caps a single tax lot to fingernail size; no basemap is
  deliberate, none admitted). Owner to scroll-zoom center; if truly absent → defect packet
  (console evidence requested). Polish candidates if present: higher maxZoom for small lots,
  basemap admission (needs G5 source admission).
- Finding 3 (RETESTED, closed as EXTERNAL — D-056-R004): ZoLa blank; link format verified
  from ZoLa router source (2026-09-12 doc) AND live shell re-fetch 2026-09-14. EVIDENCE
  UPDATE 2026-09-14: the ZoLa HOMEPAGE itself is blank on TWO owner devices (desktop +
  mobile Chrome, 5+ min, multiple refreshes) while the shell fetches fine server-side →
  city-side app/asset failure OR a network shared by both devices (router DNS/ad-block);
  definitively NOT this repo's link and NOT a single-browser config. **ROOT CAUSE PROVEN
  2026-09-14 (owner console + independent fetch): ZoLa's backing service
  labs-layers-api.herokuapp.com/v1/layer-groups returns HTTP 500 (both POST from the app,
  per the owner's console trace on route map-feature.lot, and GET from this side) — a
  city-side outage of ZoLa's layers API; the SPA dies before painting.** No repo change
  owed; none of OUR accepted connectors depend on labs-layers-api (DCM/MapPLUTO go direct
  to ArcGIS/SODA) — the outage does not touch platform data paths. Resilience candidate
  noted: a second escape-hatch link (city Digital Tax Map) beside the ZoLa link on the
  confirm card. NYC Planning Labs contact labs_dl@planning.nyc.gov if persistent.
  Findings 1+2 became the D-056 work order → packet M5-T025.
- **Finding 4 (confirmed vs live PLUTO, candidate packet): address-continuity gap on
  Step 2.** Owner entered "125 Taylor St" → confirm card 125 TAYLOR STREET / BBL 3021720001
  → Step 2 shows "83 TAYLOR STREET" for the SAME BBL. NOT a lookup bug: PLUTO stores ONE
  representative address per tax lot, and live SODA (64uk-42ks, 2026-09-14) returns
  address="83 TAYLOR STREET", lotarea=116000, lotfront=580, lotdepth=200 for that lot —
  a block-sized multi-address lot; Geoclient correctly maps 125 Taylor onto it. UX
  candidate: carry the user-confirmed address into Step 2 ("You searched 125 Taylor St —
  this lot's official PLUTO label is 83 Taylor St") instead of silently swapping labels.
- **Finding 5 (confirmed, candidate packet): year fields render with thousands separators**
  ("Year built 2,005"). Cause: `apps/web/src/lib/format.ts` formatValue line ~15 runs EVERY
  number through toLocaleString("en-US") grouping; year-class fields (yearbuilt, yearalter*)
  need plain rendering. Tiny fix + test. (298 Wallabout walkthrough, live SODA yearbuilt raw
  = "2005".) Minor sibling candidate: the data-completeness banner could link to the
  Missing-inputs section that already enumerates the absent fields (discoverability only —
  the enumeration exists, MissingInputsSection + show-more toggle, nothing is dropped).
- Walkthrough data notes (298 Wallabout, BBL 3022647515, live SODA 2026-09-14): condo lot
  (condono=1313, 75xx billing lot), bldgclass R4 (DOF condo building-class code) under
  zoning R7-1 (different vocabulary - no contradiction); unitsres=unitstotal=20 = DECLARED
  condo units (owner counts 12 apts + 8 basement rooms - consistent if basement rooms are
  separately declared units; authoritative confirmation = the ACRIS condo declaration, out
  of scope); numfloors ABSENT from the official PLUTO record (app honestly shows missing -
  a floors-bearing source (DOB) is a future connector candidate, not a defect).
- **Finding 6 (confirmed, candidate packet): the aggregated "Missing official inputs" card
  is mounted ONLY on the /property lookup view (PropertyLookup.tsx:144) — the Step-2
  Confirm screen shows the completeness summary + per-fact notes but has no list and no
  link.** Candidate: mount or link MissingInputsSection on ConfirmScreen (pairs with the
  Finding-5 banner-link nit).
- **Owner-facing flag map (walkthrough Q&A):** Compare/scenario endpoint is gated by its
  OWN api-side var `INTERNAL_SCENARIO_ENABLED` (config.py:34; fail-safe 404 when unset) —
  NOT by INTERNAL_RULE_EVAL_ENABLED; the D-043 checklist never mentions it (doc-gap
  candidate: checklist addendum). "Confirm facts (not yet available)" is honest-by-design:
  user_confirmations exist in the contract but no endpoint accepts them until the
  analysis-run milestone + persistence/auth (Supabase B-001) land — not a flag.
- **Live-deploy staleness (owner walkthrough, Compare run):** the deployed nycdf-api is the
  2026-09-11 blueprint build (autoDeployTrigger off) — it PREDATES M4-T009's R1–R12 FAR
  families (accepted 9/12): the live scenario coverage matrix says "(R5)" and treats
  higher-density as out_of_scope. The owner's next Manual-Deploy round must cover BOTH
  services (web + api). Scenario for 3022647515 fails closed on `spatial_intersection_absent`
  (profile carries no spatial_intersection section; integration.py:474 — district never
  guessed) — the geometry lane (B3 done, B4 next) + spatial layer is exactly this gap.
