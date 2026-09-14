# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff — seq 112: D-059 MVP-review work order; 208 accepted; loop DOWN on B-024

Generated 2026-09-14 (UTC) by session_01JjK8w1YXwFBjUS8PRrTfHp. Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`.
`main` untouched. PR #241 OPEN — NEVER merge.
**MUST-READ: `docs/WORKING_KNOWLEDGE.md` (Tier 2) — its D-059 section leads the file.**

## THE ONE OWNER ACTION BLOCKING THE LOOP (B-024)

`C:\SupervisorController\model_selection.toml` line 39: `model = "claude-fable-5"` →
`model = "claude-opus-4-8"`, save. Then relaunch via `scratchpad/relaunch_m4t021.ps1`
(adapt: fresh run-id, next packet). Authorization is PRE-RECORDED as **D-060-R002**; revert
obligation **D-060-R003** (back to Fable the moment it returns). Do NOT retry the edit as the
agent — the classifier blocks it and the controller states the write is the owner's
(S3.2 rule 6). Alternative: the owner raises extra usage on the account, restoring Fable and
making the edit unnecessary. Full evidence in `project-control/blockers/B-024-*.json`.

## WHAT THIS SESSION DELIVERED

1. **Four acceptances: 204 → 208.** M5-T025 (205th, D-056 walkthrough web fixes), M5-T026
   (206th, D-057 default-on gate mode), M4-T020 (207th, B3 DCM geometry — the loop worker's
   own build carried end-to-end), M5-T027 (208th, D-059 step-1 fixes).
2. **D-059 captured** — the owner's uploaded MVP review + covering message, verbatim, 12
   requirements. Standing: **R006 claims discipline** (never present task counts as MVP
   completion; never repeat the 2–4 h/lot estimate as demonstrated), **R008** 8-step delivery
   order, **R007** 15–20-parcel benchmark protocol. STILL OPEN: **R004** (spatial-failure root
   cause + checklist vars) and **R009** (master_plan.json milestone prose is stale).
3. **D-060 captured** — loop continuity under the Fable hard stop (see B-024 above).
4. **D-059 fix lane:** M5-T027 ACCEPTED (bldgarea-zero-with-buildings now fails closed;
   recorded-data wording; evaluation-derived labels). **M5-T028 in review** — closes the five
   live-wired modules a G3 reviewer found still hardcoding ZR 23-21. **D-059-R003 is NOT
   closed project-wide until M5-T028 is accepted** (recorded in the DCV rows).
5. **M4-T021 (B4 buffer engine) BUILT but in REWORK** on three blocking findings — see below.

## IN FLIGHT AT LANDING

- **M4-T021 rework producer** (3 findings, ruling in `reports/M4-T021-rework-ruling.md`).
- **M5-T028**: G3 PASS recorded; **G4 + G5 reviewers running**; then DCV + accept.
- CI running on recent heads — verify green before any acceptance (own pushes cancel
  in-flight runs; hold pushes while a needed run executes).

## M4-T021 REWORK — the three blocking findings and the rulings

Both gates returned and DISAGREED on one item; the orchestrator ruled (full reasoning in
`project-control/reports/M4-T021-rework-ruling.md`, gates recorded G3 PASS-with-corrections /
G4 FAIL):

1. **EC-5 must VALUE-GATE (G3-F1).** The packet incorporates the D-052/M4-T019
   `AttestedPreconditions` precedent BY NAME; G3 read that precedent's source and found it
   returns `DECISION_UNRESOLVED` when the attestation is False. Shipping `STATUS_COMPUTED` on a
   `(False, False, "not yet checked")` attestation is the exact silent-skip failure the packet
   names. G4 had ruled it acceptable (NB-2) without reading the precedent — **ruling: G3
   prevails**; return a typed not-attested state instead.
2. **quad_segs (G3-F2).** The comment claiming 8 matches shapely's implicit default is FALSE —
   `BaseGeometry.buffer` (the API actually called) defaults to 16; the 8 belongs to the unused
   top-level `shapely.buffer()`. Reproduced live (67 vs 35 vertices; 33365.48 vs 33214.45 sq ft).
   Ruling: set **16**, correct the claim, add an end-cap-proximate test (currently untested —
   every fixture keeps caps away from the lot).
3. **Provenance dropped (G4-F1).** `source_retrieved_at`/`source_raw_digest` are required
   *inputs* but appear on NO output dataclass, so a result cannot be traced to the fetch that
   produced it — violates contract item 5 and permanent principle 2, and was untestable as
   shipped. Ruling: remedy (a), thread them onto `SegmentContribution` +
   `WideStreetBufferResult` in BOTH branches with tests. Disclosure alone was refused.

After rework: resubmit at the corrected head → delta-attestation from BOTH the same reviewers →
re-record gates → G5 → DCV → accept.

## PROCESS CORRECTIONS MADE THIS SESSION (carry forward)

- **Tasks contracted without an explicit `--gates` list get the FULLER default set
  G0,G2,G3,G4,G5** (earlier tasks used G0,G3,G4). M5-T027/M5-T028/M4-T021 all carry it. G2 is
  the producer self-check gate and is recorded by the ORCHESTRATOR (`--reviewer orchestrator`,
  role self_check) — the CLI rejects the producer's own name.
- **A required gate also needs its reviewer on the packet's `reviewer_agents` roster.** All
  three packets required G5 but omitted `security-reviewer`, so the CLI refused the completed
  review. Fixed by ADDING the reviewer, never by removing the gate. `reviewer_agents` is
  neither `allowed_paths` nor `directive_refs`, so material identity/restamp conditions are
  unaffected.
- **Evidence-map `material_commit` = the cherry-pick commit**, not the follow-up seam commit
  that carries only state/task files (a G3 reviewer caught this mislabel).

## OWNER RETURN ITEMS

B-024 model edit (above). Render Manual Deploy for BOTH services (web is behind on
M5-T025/026/027; the api is still the 2026-09-11 build predating the R1–R12 FAR families) plus
`INTERNAL_RULE_EVAL_DEFAULT_ON=1` on the WEB service (D-057-R004). Extra-usage
enablement/limits = owner account setting. RQ-005 DCP email. Supabase B-001. G6. PR #241 stays
open.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. R595/auto-accept stays shadow. Expansion hold (lot-outline increment
excepted). §G admissions (zero new deps this session). Thin client (no local npm/node_modules;
CI is the executable authority for web). G6 owner-only; DRAFT-until-G6. Stop-and-ask only
credentials/payments/legal (D-008). **D-059-R006 claims discipline is permanent.**
Gates are never relaxed to make an acceptance pass.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/{M4-T021,M5-T028}.json` ·
`directives/{D-059,D-060}*/` + `index.json` · `blockers/B-024-*.json` ·
`reports/M4-T021-rework-ruling.md` + its G3/G4 reports ·
`reports/M5-T02{7,8}-*` · `docs/WORKING_KNOWLEDGE.md` ·
`.claude/rules/PROGRAM_KNOWLEDGE.md` (eager budget 5741/6000 tok — **compress before
appending**).

## SUCCESSOR PROMPT (copy into the new session)

Resume from handoff seq 112: work from durable repository evidence, not assumptions about the
prior conversation. Verify root/branch/HEAD (expect
C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on candidate/D-024-mrl-option-b; origin may have
advanced — ledger and CI win), then read CLAUDE.md, docs/SESSION_HANDOFF.md, and
docs/WORKING_KNOWLEDGE.md (Tier-2 must-read; maintain both D-054 tiers). Run `python
tools/project_control.py status`. State: 208 accepted; the build loop is DOWN on blocker B-024
(Fable exhausted account-wide; the worker-pin edit is OWNER-ONLY — do not retry it, the
classifier and the controller both refuse it) with authorization pre-recorded as D-060-R002;
M4-T021 is in REWORK on three blocking findings whose rulings are in
project-control/reports/M4-T021-rework-ruling.md; M5-T028 is in review (G3 PASS; G4/G5/DCV
remain) and closes D-059-R003 project-wide. Keep work moving via orchestrator-dispatched
producers while the loop is down (D-060-R001). Honour D-059-R006 permanently: never present
accepted-task counts as MVP completion and never repeat the unmeasured time-saved estimate.
Stop only for owner-only items (credentials/payments/legal, PR #241, production, G6, Supabase).
Report READY TO RESUME or BLOCKED before changing anything.
