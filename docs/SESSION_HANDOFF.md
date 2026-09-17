# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff — seq 113: D-064 executed; 214 accepted; LOOP LIVE on M5-T032 (opus-4-8 worker)

Generated 2026-09-17 (UTC) by session_01SewZxbFqxV3yYhcDb7bMJt. Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`.
Origin `https://github.com/martin10101/nyc-buildability.git`. `main` untouched. PR #241 OPEN —
NEVER merge. Between seq 112 and this session, a ChatGPT/Codex lane delivered and the ledger
accepted **M5-T029 (architect workspace), M5-T030 (lot-specific source links), M5-T031
(development-first FAR meanings), M4-T022 (residential source audit)** → **214 accepted**; owner
handoff `C:\Users\MLFLL\Downloads\NYC_Buildability_Loop_Handoff_2026-09-16.md` is the delivery
record (its §6 address-search defect and §9 spatial gap are the open work).

**D-064** (captured + executed this session): ALL delegated subagents + the loop worker =
`claude-opus-4-8` @ `xhigh` (25 agent files flipped; supersedes D-047/D-055/D-058-R004/D-060
fable defaults for subagent scope — NO revert-to-fable duty remains); main session stays
fable-5; lean-communication = CLAUDE.md principle 19; ZoLa-first links (R005) + batched per-seam
testing (R007) bound to M5-T032; **B-024 RESOLVED** — owner personally edited
`model_selection.toml` (model → opus-4-8, fallback_models → [], doctor overall PASS,
digest cacbdf5a…).

**LOOP STATE AT HANDOFF: LIVE.** Relaunched via `C:\SupervisorController\autostart-launch.ps1`
(ACTIVE-TASK block → M5-T032, repo `wt-m5t032`, branch `task/M5-T032-address-search-links`;
the launcher's `Start-Process` quoting of the spaced `--config` path was repaired in-file).
`clear-recovery` was the audited operator exit from the seq-706 PAUSED_RECOVERY. Watcher armed
(quiet: breaks/stalls/run-end only). **M5-T032** = handoff §6 address-search reliability +
D-064-R005 ZoLa-first links; contracted, G0 PASS, claimed frontend-engineer, progress 20.

## STILL OPEN FROM D-059 (not started — do not report these as done)

- **R004 spatial-failure root cause**: the recorded `spatial_intersection_absent` on BBL
  3022647515 must be traced from the deployed commit + settings + typed logs and reproduced. It
  is NOT justified to claim B3/B4 alone fixes it (the live provider doesn't use the centerline
  module and has its own `LIVE_SPATIAL_PROVIDER_ENABLED`). The deploy checklist must also name
  `LIVE_SPATIAL_PROVIDER_ENABLED` and `INTERNAL_SCENARIO_ENABLED`.
- **R009 status-prose reconciliation**: `master_plan.json` milestone summaries are stale (M2
  survey rows, M3 acceptance state). Verified true counts are at the top of this file.
- R005 (wire built rules into the normal result path), R007 benchmark, R010 demo guidance.

## B7 BINDING PRECONDITIONS (from the M4-T021 reviewers — do not rediscover these)

1. **Modularity (G3 ruling):** do NOT split `wide_street_buffer_engine.py`; B7's rule-wiring and
   the named-street override table MUST land as their own module(s) consuming it.
2. **Input bounds (G5 advisory A1):** the engine has NO size or coordinate-magnitude bound of
   its own — `len(wide_segments)`, per-path vertex count and EPSG:2263 extent are unbounded,
   relying entirely on upstream transport caps. Safe ONLY because nothing reaches it from a
   request path today. **Close it before B7 wires it behind a handler**, or make it a binding
   requirement of B7's contract.

## PROCESS LESSONS THIS SESSION (all cost a real cycle — carry forward)

- Tasks contracted without an explicit `--gates` list get the FULLER default set
  **G0,G2,G3,G4,G5**. G2 is the producer self-check gate and is recorded by the ORCHESTRATOR
  (`--reviewer orchestrator`); the CLI rejects the producer's own name.
- A required gate also needs its reviewer on the packet's `reviewer_agents` roster — all three
  new packets required G5 but omitted `security-reviewer`. Fix by ADDING the reviewer, never by
  removing the gate.
- **An orchestrator correction to material AFTER submit invalidates the frozen submission
  identity.** `accept()` fails closed with "frozen-evidence identity mismatch"; the fix is to
  walk `awaiting_gate → rework → in_progress → submit` and re-freeze. Gates recorded AFTER the
  edit stay valid and need no re-run.
- **`_blocker_references` scans a blocker's `affects` AND `detail`** for a word-bounded task id
  and is deliberately conservative ("can only block acceptance, never allow it"), so historical
  prose naming a packet will block that packet's acceptance. Correct the reference, preserve the
  facts, record the change — never close or downgrade the blocker to get past it.
- Evidence-map `material_commit` = the CHERRY-PICK commit, not the follow-up seam commit.
- `tools/test_directive_compliance.py` takes ~54 minutes (129 tests) — it is slow, not hung;
  run it in the background with a long budget.

## OWNER RETURN ITEMS

B-024 model edit (above). Render Manual Deploy for **BOTH** services — web is behind on
M5-T025/026/027/028 and the api is still the 2026-09-11 build predating the R1–R12 FAR
families — plus `INTERNAL_RULE_EVAL_DEFAULT_ON=1` on the WEB service (D-057-R004).
Extra-usage enablement/limits = owner account setting. RQ-005 DCP email. Supabase B-001. G6.
PR #241 stays open.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. R595/auto-accept stays shadow. Expansion hold (lot-outline increment
excepted). §G admissions (zero new deps this session). Thin client (no local npm/node_modules;
CI is the executable authority for web). G6 owner-only; DRAFT-until-G6. Stop-and-ask only
credentials/payments/legal (D-008). **D-059-R006 claims discipline is permanent.** Gates are
never relaxed to make an acceptance pass.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` · `directives/{D-059,D-060}*/` + `index.json` ·
`blockers/B-024-*.json` · `reports/M4-T021-rework-ruling.md` (the G3/G4 disagreement ruling) ·
`reports/M4-T021-*` and `reports/M5-T02{7,8}-*` · `docs/WORKING_KNOWLEDGE.md` ·
`.claude/rules/PROGRAM_KNOWLEDGE.md` (eager budget 5741/6000 tok — **compress before appending**).

## SUCCESSOR PROMPT (copy into the new session)

Resume from handoff seq 112: work from durable repository evidence, not assumptions about the
prior conversation. Verify root/branch/HEAD (expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on
candidate/D-024-mrl-option-b; origin may have advanced — ledger and CI win), then read CLAUDE.md,
docs/SESSION_HANDOFF.md, and docs/WORKING_KNOWLEDGE.md (Tier-2 must-read; maintain both D-054
tiers). Run `python tools/project_control.py status`. State: **210 accepted, nothing in flight**.
The build loop is DOWN on blocker B-024 (Fable exhausted account-wide; the worker-pin edit is
OWNER-ONLY — do not retry it, the classifier and the controller both refuse it) with
authorization pre-recorded as D-060-R002. D-059's fix lane delivered R001/R002/R003 (R003 closed
project-wide); **R004 (spatial-failure root cause) and R009 (stale master_plan prose) are still
OPEN and must not be reported as done**. Keep work moving via orchestrator-dispatched producers
while the loop is down (D-060-R001). Honour D-059-R006 permanently: never present accepted-task
counts as MVP completion and never repeat the unmeasured time-saved estimate. Stop only for
owner-only items (credentials/payments/legal, PR #241, production, G6, Supabase). Report READY
TO RESUME or BLOCKED before changing anything.
