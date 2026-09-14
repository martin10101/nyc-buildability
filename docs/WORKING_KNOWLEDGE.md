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

## D-053 relaunch — EXECUTED TO THE LAUNCH STEP (2026-09-14); launch = ONE owner command

- Everything staged by the orchestrator session: **M4-T020 (B3 geometry parse-and-expose)**
  contracted (d7f0f3f8) + G0 PASS + claimed + launch-prep record (a9df0fdd); registry bound
  D-045-R002/R008/R009 + D-046-R001/R002 w/ digest resyncs (evaluate_task_refs ok);
  loop-closed-profile commands; placeholders seeded; supervisor down-state drill DONE
  (3 stale M4-T009 asks denied — CRLF trap: strip \r from parsed digests; PAUSED_RECOVERY
  → PREFLIGHT; 0 children/0 effects); wt-m4t020 @ a9df0fdd, packet copies byte-identical;
  all launch paths verified; run-id **persistent-local-34**.
- **LAUNCH IS CLASSIFIER-BLOCKED for the session** (PowerShell AND Bash routes both denied;
  the detached Start-Process launch is a guarded action class now). Owner runs ONE command
  (survives session end — Start-Process detaches):
  `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\scratchpad\relaunch_m4t020.ps1"`
  (or type it with a `!` prefix in the orchestrator session). Alternative: add a Bash
  permission allow rule for the launch and tell the session to retry.
- **D-036 Thursday model revert ALSO classifier-blocked** (model_selection.toml edit denied):
  loop runs the standing owner-approved opus-4-8 pin; owner item = execute the revert
  recorded verbatim in the file comment (fable-5 + fallback ["claude-opus-4-8"]).
  D-047 sonnet-5: NOT on the loop allowlist → owner settings item (D-053-R004), deviation
  recorded in the M4-T020 G0 report + ledger.
- Watcher: two-phase read-only `scratchpad/loop_break_watcher_m4t020.sh` armed in-session
  (waits for the lock, then quiet BREAK/FREEZE/CLOSED only; a fast CLOSED can be the benign
  DL-2 checkpoint_field_mismatch — inspect wt-m4t020 before assuming failure).
- After loop-live: monitor + owner bridge only (R002/R003); NO auto-accept/merge (R595
  shadow); gates/acceptance stay with the orchestrator at the seam.
- Wave-5 queue after M4-T020: B4 buffer engine, zr-12-10 snapshot-update task, C-district
  families 1–3, B7 wiring LAST (G3-A1 acceptance criterion).
