# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff — seq 110: 204 pending-accept; landed by /session-handoff (re-run)

Reason: owner directive embedded as the turnover reason — recorded VERBATIM as
`project-control/directives/D-054-persistent-knowledge-files/source-001.md` (two-tier
persistent-knowledge system; captured + implemented this seam, not duplicated here for
budget). Generated 2026-09-14 (UTC) by the wave-3/4 orchestrator session
(session_01JjK8w1YXwFBjUS8PRrTfHp). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
`candidate/D-024-mrl-option-b` (tip = this seam's capture commit; 0/0 after push). `main`
untouched. PR #241 OPEN — NEVER merge. Dirty at landing: ONLY conventional reviewer
agent-memory files + session scratchpad. Campaign-continuity CLI: known-stale — ledger+git.

## NEW (D-054): two knowledge files — READ TIER 2 NOW

- **Tier 1** `.claude/rules/PROGRAM_KNOWLEDGE.md` — compressed program-wide pointers,
  auto-injected into every session (you already have it). APPEND when you discover something
  program-wide useful; eager budget (context_budget_check, 6000 tok) is the hard cap —
  compress, never raise.
- **Tier 2** `docs/WORKING_KNOWLEDGE.md` — living current-section knowledge (street-width /
  A2 + C-district lanes right now): wave-4 close state, B-lane map, exception build inputs,
  C-district family specs, D-053 relaunch runbook pointers. **MUST-READ at resume.** Update
  it while working; at section close PRUNE finished material or PROMOTE durable items to
  Tier 1 (D-054-R003).

## WHAT THIS SESSION DELIVERED

1. **WAVE 3 CLOSED — 202 accepted.** M4-T016 (A2 geometry-mechanics research, 201st) +
   M4-T017 (C-district research, 202nd), end-to-end: G0/G1, T017 PASS-with-corrections arc
   (ORCH-CORRECTED F5/F6 + same-reviewer delta-attestation), 10/10 DCV rows, accepted at
   920110be, checkpoint `CP-2026-09-13-wave3-closed`. Headline: live §12-10 "street, wide"
   AMENDED 3/26/2026 (fuller than accepted pin); C4-6→R10; 33-122/123 structural-only.
2. **D-050 arc absorbed live:** Amendment 1 (R005 active notification) + Amendment 2 (R006
   immediate-push queue + Closed register). THREE owner Astra research passes archived under
   `docs/research/owner-research/` (discovery aids ONLY, R002); RQ-001/2 closed
   (own research), RQ-003/4 ANSWERED, RQ-005 answered-in-part (residual: DCM field-level
   width convention — DCP contact + Section/Alteration-Map path recorded).
3. **D-051 captured** (owner corrections): bounded negatives only; UNKNOWN stays factual
   state; **fail-closed-to-narrow is NOT universally conservative** (§23-431 street-wall
   counterexample) — every consuming rule validates its own fallback or keeps
   assumption/review labels. **D-052 captured (OQ-3 OWNER-DECIDED):** DRAFT width policy —
   75-ft threshold (exactly 75 = WIDE), exceptions-checked-first, one-sided-bound rule
   ('<75' narrow; '>75','>=75','75-90' wide; '<=75','60-75','70-80' UNRESOLVED),
   UNKNOWN→map-resolution, provenance quintuple, DRAFT-until-G6; closure in architect doc §D.
4. **WAVE 4 BUILT + FULLY GATED, ACCEPT PENDING (→204):** M4-T018 (fresh §12-10 capture +
   snapshot reconciliation — G1 PASS byte-exact; amendment PREDATES the 2026-07-22 snapshot;
   superseded-text carriers: the snapshot, M4-T013 report, `r5_setback.rule.json`; NOT the
   r6_r7_r8 rule) and M4-T019 (D-052 policy layer `dcm_street_width_policy.py` + 94 tests —
   G3 PASS w/ R005 ruling qualitative-bounds-SATISFY; G4 PASS w/ blocking F1 applied
   (per-field no-default assertion, mutation M6 now CAUGHT) + BOTH delta-attestations).
   Producer commits cherry-picked (00b28626/a6c73ec0), submits at 42e57a6a, gates at
   fef69aae. 712-test regression green; ruff clean; classifier byte-immutable.
5. **D-053 captured by peer @ fef69aae (verified by this session): RELAUNCH THE CODEX LOOP**
   on the campaign queue — R001 loop does the job, R002 authority UNCHANGED (no
   auto-accept/merge, R595 shadow), R003 repo-only comms + this session's successor = quiet
   monitor + owner bridge (D-050-R005 leg), R004 Astra roles distinct, R005 verify→execute→
   report loop-live. **NOT yet executed.**
6. **D-054 captured + implemented at this seam:** the two-tier knowledge system (files above;
   registry `directives/D-054-persistent-knowledge-files/`; index.json entry same commit;
   context_budget_check PASS 5330/6000 eager).

## IN FLIGHT AT LANDING

- **Wave-4 combined DCV verifier was RUNNING** (read-only, dispatched at frozen head
  a7cc1757; 20 rows: T018 ×6, T019 ×14; prompt asked for the standard conditional-restamp
  pre-authorization). If its result did not land in-session: **RE-DISPATCH** the same
  combined DCV (directive-compliance-verifier, read-only, frozen at live HEAD) — cheap and
  safe; all evidence is committed. Never resume a killed producer; re-dispatching a
  read-only verifier is always safe.

## NEXT ACTIONS (exact order)

1. **Close wave 4:** collect/re-dispatch the DCV → assemble v2 blocks into D-045/D-046/
   D-051/D-052 verification.json (reviewed_sha = restamp target per the verifier's
   authorization; manifests in gates/M4-T018-G1.json + M4-T019-G4.json records; producer =
   the task's material producer) → accept M4-T018 + M4-T019 (**204**) → checkpoint →
   ONE seam commit → push.
2. **Execute D-053 (the relaunch):** verify capture (done once by this session — re-verify),
   then the documented relaunch mechanics (orchestrator memory: loop-relaunch-mechanics /
   task-switch drill — 5 start blockers, certified-cwd manifest binding, checkout_key,
   ask stores, NEVER audit-write verbs vs a live run, watcher quiet mode). Report loop-live
   at the owner seam (discharges R005). After live: STOP hand-conducting waves; quiet
   monitor + final authority only (R002).
3. Wave-5 packet candidates the loop (or you, if the owner defers relaunch) should draw:
   B3 (DCM geometry parse-and-expose sibling), B4 (buffer engine; B6 done), snapshot-update
   task (zr-12-10 refresh per M4-T018 + G1 advisory: conflict visible, no re-adjudication),
   C-district families 1–3 (M4-T017 §9), B7 wiring LAST (G3 advisory A1 = acceptance
   criterion: exceptions_checked=True only when checked AND none-apply-or-implemented;
   coverage only after real multi-feature collection).

## OWNER RETURN ITEMS (D-050-R005 seam list)

- **RQ-005 residual OPEN**: DCM field convention — DCP email draft ready in the archived
  report (owner sends); per-frontage Section/Alteration Maps close individual sites now.
- RQ-003/RQ-004 ANSWERED (consumed by future D-049-R004 conversion + A4 triage tasks →
  then SATISFIED/Closed-register per R006). Mobile push DISABLED in /config (R005 phone leg
  dead until owner flips it). backend-engineer agent-file model flip (classifier-blocked;
  override used + recorded each dispatch). D-043 walkthrough + live-URL confirm. Supabase
  B-001. G6 ask (architect doc §A–B; §D records the OQ-3 decision). PR #241 unmerged.

## TIPS THIS SESSION PROVED (full set in orchestrator memory)

- **Directive capture REQUIRES a `directives/index.json` entry in the SAME commit** — an
  unindexed capture is INVISIBLE (validator silently passes around it; new-task fails
  closed). Classification vocab: `return`, never `return_item` (c1 set in validator:444).
- Gate CLI fails closed when allowed_paths resolve to ZERO tracked files → seed committed
  placeholders at contract time (report/module/test stubs, ruff-clean).
- Transient c14 INVALID during peer mid-write happened TWICE — re-run at the settled head
  with a DIRECT exit code (`| tail` eats the real code) before reacting.
- DCV conditional-restamp pre-authorization: request UP FRONT in the DCV prompt; the
  verifier can extend an imperfect condition itself (cond-3′ per-commit ruling, ~4 min).
- PASS-with-corrections arc: orchestrator applies tagged [ORCH-CORRECTED per <gate> Fn]
  edits → rework→resubmit at new frozen head → SendMessage delta-attestation to the SAME
  reviewers (~1 min each; both G3 identity-carry and G4 discharge proven) → gates at the
  corrected head. Peer heads-up protocol works: 3-way interleaved commits, zero collisions.
- `cd services/api` in Bash PERSISTS cwd across calls — cd back or use absolute paths.
- submit --report must live under project-control/reports/ (build tasks: save the producer
  return verbatim there and reference it).

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. R595/live-actuation stays shadow (D-053-R002 reaffirms). Expansion hold
(lot-outline increment excepted). §G for any admission (zero new deps this session). Internal
-only deploy. Thin client. G6 owner-only; DRAFT-until-G6. Stop-and-ask only credentials/
payments/legal (D-008). Bootstrap Gate 0 first. Producers claude-sonnet-5 (D-047);
reviewers/orchestrator pinned set unchanged.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/M4-T018.json` + `tasks/M4-T019.json` (awaiting_gate,
all required gates PASS) · `directives/{D-051,D-052,D-053}*/` + index.json ·
`gates/M4-T018-G{0,1}.json`, `gates/M4-T019-G{0,3,4}.json` + the four G-reports under
`reports/` (attestations embedded in the G4 report) · `reports/M4-T01{8,9}-evidence-map.json`
· `reports/M4-T018-zr1210-wide-street-reconciliation.md` (B6 pin) ·
`services/api/app/connectors/dcm_street_width_policy.py` (+test) ·
`docs/RESEARCH_REQUESTS.md` · `docs/ARCHITECT_REVIEW_QUESTIONS.md` §D ·
`docs/research/owner-research/` (3 archived discovery aids)
