# WORKING_KNOWLEDGE — current section: D-059 dependable-answers + A2 geometry (D-054 Tier 2)

## Loop-packet contract for WEB tasks (learned the hard way, run persistent-local-36, 2026-09-17)

Five packet defects each killed a run of the relaunched loop on M5-T032; every future loop
packet (web tasks especially) must satisfy ALL of these up front:

1. **Checkpoint envelope:** packet `worktree` = the FULL controller-authoritative path, and the
   packet carries the instruction to leave `starting_sha`/`current_sha`/`branch`/`worktree` as
   `""` in the worker checkpoint (controller fills them; any worker-supplied value must match
   EXACTLY — short SHAs/names fail closed as `checkpoint_field_mismatch`).
2. **Producer report path** (`project-control/reports/<task>-producer-report.md`) MUST be in
   `allowed_paths` — the worker's Write is held forever otherwise.
3. **documented_test_commands profile:** plain single commands only (no quotes, parens,
   chaining, redirection) — a prose "CI is the authority" line there aborts launch with
   `bad_documented_test_commands`. Put CI-authority prose in `outputs`/`inputs`.
4. **Thin client = NO local npm** (no node_modules anywhere, ~6 GB free): web tests CANNOT run
   locally. Web packets follow the M5-T023 pattern — worker edits + commits + python checks
   only; CI on the pushed head is the executable authority; orchestrator pushes and captures
   CI + any live smoke evidence at the seam. Never document npm/npx commands for the loop, and
   tell the worker not to propose WebFetch (network is owner-default-deny).
5. **After a `consecutive_revision_loops` (or any counter) breaker trip, the tally is durable
   per run-id:** relaunch REQUIRES a fresh `--run-id` (edit the ACTIVE-TASK block in
   `autostart-launch.ps1`); `clear-recovery` alone re-refuses with `budget_exhausted`.

Recovery drill order when a run dies mid-task: read audit tail → fix the packet defect (BOTH
packet copies: ctl24 + the task worktree) → deny stale asks (strip `\r` from digests piped
through git-bash!) → `clear-recovery` if PAUSED_RECOVERY → fresh run-id if a counter tripped →
relaunch via autostart-launch.ps1 → re-arm the audit-tail watcher. Worker file edits survive
all of this (they live in the task worktree, uncommitted).

Machine-sleep crash recovery (run 38, 2026-09-17): a sleep/reboot kills supervisor + worker +
orchestrator session together, leaving a STALE lock (pid dead), a journal stuck in
CLAUDE_RUNNING (so `clear-recovery` refuses — it only fires from PAUSED_RECOVERY), a forked
audit chain (mid-write), and boot refusal `unit_dispatch_unreconciled`. Order: repair script
(archives fork) → gather read-only evidence (pending_effects 0, children 0, asks empty, edits
confined to the task worktree) → run `recovery.reconcile_dispatch_intent(journal)` via the
scripted journal-open from the loop-task-switch drill (NO CLI verb) → fresh run-id → relaunch.
Worker edits survive in the worktree; the new run resumes from packet + tree.

Watcher + ask mechanics (learned re-arming for run 36, 2026-09-17):

- The watcher's lock-pid check MUST NOT use Git-Bash `ps -p` — MSYS ps cannot see native
  Windows pids and reports the live supervisor as dead (false LOOP BREAK). Use
  `tasklist //FI "PID eq $PID" //NH | grep -q $PID` with a 5 s recheck before alarming.
- Ask-alert pattern (owner directive 2026-09-17 "ping me-side so questions are answered
  right away"): queued asks serialize in audit.jsonl as `"decision":"DEFER_TO_OWNER"`
  (detail carries `"tier":"ASK"` / `policy_rule S4.3/...`) — the words `undocumented_command`
  / `pending_prompt` NEVER appear in the audit line, so a watcher grepping only those goes
  silent while asks pile up (run-37 gap: 8 queued unnoticed). Watch for
  `DEFER_TO_OWNER|"tier":"ASK"` AND poll the journal's unanswered `queued_asks` count
  (sqlite read-only) as belt-and-braces.
- Not every undocumented-command ask is a packet gap. Two benign classes seen in run 36:
  (a) the worker chains `; echo FOO_EXIT=$?` onto a documented test command — chaining can
  NEVER be a documented_test_command (profile forbids it), and the worker self-recovers by
  retrying the exact documented form within seconds → deny the chained ask as stale;
  (b) worker `git add` / `git commit` — git writes are never AUTO (policy S4.3), so the
  worker's local checkpoint commits arrive as ASKs by design → approve-once when staging is
  in-scope. The supervisor stores only command DIGESTS; recover the actual command text by
  timestamp-matching the ask's `queued_at_utc` against Bash tool_use entries in the worker
  session transcripts under `~/.claude/projects/C--…-wt-m5t032/*.jsonl` (subagent files too).

Also: the full `validate_directive_compliance.py` run starves against a live loop worker on
this box (each `_run_git` call crawls to its 60 s bail under disk contention) — run it between
units, or rely on the control-plane CI job (same validator, clean runner) for the seam verdict.

## D-059 MVP-review work order (owner 2026-09-14) — the CURRENT priority lane

Owner transmitted a commissioned read-only MVP review (of the branch at 16272c05) with a
covering message; captured VERBATIM as **D-059** (12 requirements R001–R012, source-001.md
carries both the message and the full review byte-faithfully). It judges progress against the
EXPANDED D-045 scope, not the old FAR demo. Standing items every session must respect:

- **R006 claims discipline (prohibition, permanent):** never present the accepted-task count as
  an MVP completion percentage or as finished customer features (138 of 210 are foundation /
  control-plane); never repeat the old "2–4 hours saved per lot" estimate as demonstrated; time
  saved comes ONLY from the R007 benchmark; don't cite the resolved B-022 as a current reason
  the product is unfinished.
- **R008 delivery sequence (8 steps)** governs remaining MVP order; step 1 = make today's
  answers dependable (this is where M5-T027/M5-T028 sit), step 2 = street/lot measurement
  (M4-T020 + M4-T021 both ACCEPTED), then envelope → units → C/M campaign → corpus →
  production workflow → professional proof.
- **R007 benchmark protocol:** ~15–20 real parcels across all five boroughs incl. condo/billing
  lots, mixed-address parcels, split zoning, special districts, wide-street boundary cases;
  record the architect's checked answer, BOTH elapsed times, corrections, usefulness. G6 + B-010
  stay open regardless.
- **R004 spatial-failure protocol:** the recorded `spatial_intersection_absent` on BBL
  3022647515 must be root-caused from the deployed commit + settings + typed logs and
  reproduced — it is NOT justified to say B3/B4 alone fixes it (the live provider doesn't use
  the centerline module and has its own `LIVE_SPATIAL_PROVIDER_ENABLED`); the deploy checklist
  must also name `LIVE_SPATIAL_PROVIDER_ENABLED` and `INTERNAL_SCENARIO_ENABLED`. STILL OPEN.
- **R009 status-prose reconciliation:** master_plan.json milestone summaries are stale (M2
  survey rows, M3 acceptance). STILL OPEN. Verified counts at 2026-09-14: M0 138, M1 9, M2 21,
  M3 1, M4 15, M5 26 = **210 accepted** (2026-09-14 session close).
- Fix lane: **M5-T027 ACCEPTED (208th)** — R001 recorded-data wording, R002
  bldgarea-zero-with-buildings fail-closed, R003 evaluation-derived labels. **M5-T028 ACCEPTED
  (209th)** — opened from M5-T027's own G3 advisory A1, which found the R003 defect class
  surviving in FIVE live-wired modules (`derive.py:82` DERIVED_RANGE_LABEL emitted
  unconditionally, `breakeven.py:155`, `comparison.py:118/:129`, `ranking.py:114`,
  `sensitivity.py:128`). **R003 is now CLOSED PROJECT-WIDE**: its DCV swept BEYOND the five for
  a sixth defective module (none found — `evidence.py`'s hit is a docstring never serialized)
  and proved the remaining literals are unreachable aliases by tracing the live route's imports
  and the server-side-only `scenario_document` build. Still-out-of-scope carriers (candidates,
  NOT defects in the accepted work): `scenario.schema.json` prose and the apps/web presentation
  surface, both forbidden paths in those packets.
- **The reviewer-finds-what-the-task-missed pattern is now twice-proven** and worth repeating:
  M5-T027's G3 found the five-module gap the packet never scoped, and M4-T021's G4 found a
  provenance drop no test could have caught (the output fields did not exist). Give reviewers a
  standing licence to look just outside the packet boundary — both of this session's most
  valuable findings came from there.

Living file for the section under construction NOW. Handoff names it a must-read; update it
while working; at section close PRUNE finished material (git keeps history) or PROMOTE
durable items to `.claude/rules/PROGRAM_KNOWLEDGE.md`. Ledger stays authoritative.

## Wave-4: CLOSED (pruned per D-054-R003 — detail in git history + the DCV report)

- M4-T018 (203rd) + M4-T019 (204th) ACCEPTED; 20/20 DCV rows PASS
  (`reports/M4-T018-M4-T019-dcv-verification.md`); checkpoint CP-2026-09-14-wave4-closed.
  Nothing in flight. Next big block: D-053 relaunch (section below).

## Gate/lifecycle mechanics learned the hard way (2026-09-14 — each cost a real cycle)

Recorded because every one of these was discovered by a refusal mid-arc, not by reading docs.

- **Default gate set.** `new-task` without `--gates` yields **G0,G2,G3,G4,G5**, not the
  G0,G3,G4 the earlier packets used. All three packets contracted this session carry the fuller
  set. G2 is the producer self-check gate and the CLI rejects the producer's own agent name for
  it — record with `--reviewer orchestrator` (role `self_check`, never counts as independent
  review). A required gate ALSO needs its reviewer listed in the packet's `reviewer_agents`;
  all three packets required G5 but omitted `security-reviewer`, so the completed review could
  not be recorded. **Fix by ADDING the reviewer — never by removing the gate.**
- **Post-submit edits invalidate the frozen submission identity.** The `[ORCH-CORRECTED]`
  docstring fix on M4-T021 landed after its submit, and `accept` failed closed with
  "frozen-evidence identity mismatch … re-submit and re-verify". The fix is to re-freeze:
  `awaiting_gate → rework → in_progress → submit` (the lifecycle forbids the direct hops).
  Gates recorded AFTER the edit stay valid — no re-run needed, and both reviewers' identity-carry
  attestations covered it.
- **`accept` scans open blockers' `affects` AND `detail`** for a word-bounded task id
  (`_blocker_references`, docstring: "can only block acceptance, never allow it" — it accepts
  false positives). B-024's historical sentence "the loop stopped while attempting packet
  M4-T021" therefore blocked that packet's acceptance. Correct the *reference*, preserve every
  fact/quote/sha, move the id to an unscanned field, and log a dated `scope_corrections` entry —
  **never close or downgrade a blocker to get past it** (B-024 is still open).
- **PASS-with-required-corrections + reviewer disagreement.** G3 returned PASS-with-corrections
  while G4 returned FAIL on the SAME submission, and the two disagreed on EC-5. Inventory the
  whole failure surface before fixing (principle 17), rule the disagreement explicitly in a
  written record (`reports/M4-T021-rework-ruling.md`), then rework once and send a
  delta-attestation to the SAME reviewer agents (they stay resumable and return in ~1 min).
  Ruling heuristic that settled it: when a packet incorporates a precedent BY NAME, the
  precedent's actual source mechanism is the specification — the reviewer who read the
  precedent beats the reviewer who read only the packet prose.
- **`tools/test_directive_compliance.py` takes ~54 min (129 tests).** It is slow, not hung.
  Three agents relaunched it after apparent timeouts, stacking four parallel 54-minute runs.
  Launch it ONCE in the background with a long budget.
- Orchestrator edits to production source are acceptable ONLY as tagged
  `[ORCH-CORRECTED per <gate> <finding>]` comment/docstring fixes with the superseded text
  preserved and BOTH independent reviewers re-attesting afterwards — the DCV ruled this
  "compatible, narrowly" and explicitly not a precedent for functional code.

## A2 build map (B-lanes; statuses)

- B5 ruling = DONE (D-052). B6 = DONE (M4-T018 report = the pin). **B3 = DONE — M4-T020
  ACCEPTED 2026-09-14 (207th)**, module `dcm_street_centerline_geometry.py` (DCV 5/5,
  CI green). **B4 = DONE — M4-T021 ACCEPTED (210th)** (`wide_street_buffer_engine.py`, 40 tests,
  connectors suite 792; 5/5 gates + DCV 5/5, after a G4 FAIL + rework). B7 (wire into
  r6_r7_r8_wide_street_conditional_far.rule.json — currently cites zr-23-22 ONLY, performs
  no wide-street determination) = OPEN, do LAST.
- **B7 BINDING PRECONDITIONS (from the M4-T021 reviewers — do NOT rediscover these when B7 is
  scoped):** (1) *G3 modularity ruling:* do NOT split `wide_street_buffer_engine.py`, but B7's
  rule-wiring and the named-street override table MUST land as their own module(s) consuming
  this one — never added into this file (the DCM parse/classify/policy four-file split is the
  precedent). (2) *G5 advisory A1:* the engine has NO input-size or coordinate-magnitude bound
  of its own — `len(wide_segments)`, per-path vertex count, and plausible-EPSG:2263-extent are
  all unbounded here, relying entirely on upstream transport caps (MAX_RESPONSE_BYTES 10 MB,
  MAX_RESULT_RECORD_COUNT 2000/page, HARD_MAX_PAGES). Acceptable today ONLY because nothing
  reaches this module from a request path. **Before B7 wires it behind a handler, add a typed
  fail-closed bound (and/or an extent sanity check alongside the existing finiteness check) or
  make it a binding requirement of B7's own contract.**
- **B4 judgment calls the producer disclosed for the reviewers to rule on** (carry into B7):
  `Ec5AttestedPreconditions` is required/no-default but does NOT gate computation on the
  attested boolean VALUES (reading: the pinned research says B4 is not blocked on B5/B6/B7);
  `quad_segs=8` pinned for determinism continuity, not source-derived; no multipolygon/holes
  lot fixture. EC-4 tangency was characterised empirically (GEOS: intersects=True with a
  zero-area LineString) and the legal-tolerance question left OPEN for G6 —
  `BOUNDARY_TOLERANCE_FT` is proven never imported (AST name scan).
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

## D-053 loop — shift 1 HARVESTED; shift 2 BLOCKED on B-024 (Fable exhausted)

- **Shift-1 harvest fully landed 2026-09-14**: M4-T020 (the loop worker's build) cherry-picked
  byte-identical (patch-id 3ea576a6, blob-proven), G3/G4 PASS zero blocking, DCV 5/5,
  **ACCEPTED as the 207th**. The loop's unit DID produce accepted product code end-to-end.
- **Shift 2 could NOT run.** Relaunch (run `persistent-local-35`, packet M4-T021, the
  relaunch_m4t021.ps1 adaptation) passed preflight, reached START_CLAUDE, then stopped
  `REFUSED (unsafe, exit 11) fable_exhaustion_turnover_recorded` at 62.1s. Fable is exhausted
  ACCOUNT-WIDE including the extra usage D-058-R004 relied on — corroborated independently by
  `model_switch_tracker.py --query` showing this orchestrator session force-migrated Fable 5 →
  Opus 5 at 08:45:24Z on a recorded USAGE/RATE LIMIT (explicitly not a safety refusal).
  Root cause per the controller doctor: the live account-quota CLI signature has never been
  captured, so the turnover probe leaves the failure 'unknown' and holds the fail-closed pause.
  **The worker-pin flip is OWNER-ONLY** (controller S3.2 rule 6 + the classifier's model-file
  guard) → **blocker B-024** carries the exact one-line edit. Authorization is pre-recorded as
  **D-060-R002**; revert obligation D-060-R003. Candidate follow-up the doctor named: capture
  the live quota signature now that a genuine exhaustion finally happened.
- **Loop continuity without the loop (D-060-R001):** the blocked packet was produced by an
  orchestrator-dispatched producer instead (deviation recorded in the M4-T021 progress log).
  When the owner restores the pin, point the relaunched loop at the NEXT packet, not M4-T021.

## D-053 loop — shift 1 detail (persistent-local-34 closed benignly at unit completion)

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
