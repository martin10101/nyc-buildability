# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff — seq 111: D-058 seam; 204 accepted + THREE tasks staged mid-arc

Reason (owner, VERBATIM): "finish up at a seam let thee codex loop stay alive make sure to
add the knowlge we learnd from this seasen in the right md files like we designd make sure
the loop uses the extra useig fable (reg weekly just got used up)" — captured as **D-058**.
Generated 2026-09-14 (UTC) by session_01JjK8w1YXwFBjUS8PRrTfHp. Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`, tip at
landing ≈ the seam-close commit after `a476939c` (checkpoints CP-2026-09-14-seam-d058 — its
--commit sha is MISTYPED — and the corrective -r2 with the true sha). `main` untouched.
PR #241 OPEN — NEVER merge. Dirty at landing: ONLY conventional reviewer agent-memory files
+ session scratchpad. **MUST-READ: docs/WORKING_KNOWLEDGE.md (Tier 2).**

## WHAT THIS SESSION DELIVERED

1. **D-053 EXECUTED — loop went LIVE and completed shift 1.** M4-T020 (B3 geometry
   parse-and-expose) contracted/G0/claimed; supervisor down-state drill; detached launch
   (run persistent-local-34) after two classifier blocks + one owner no-artifact `!` try;
   preflight fully verified; worker BUILT the module, ran all 4 documented commands,
   `claude_unit_completed` (audit 845), closed on the benign checkpoint worktree-field
   mismatch. Producer material verified green (39 tests + ruff) and committed at
   **wt-m4t020 `d7766b8d`** (branch task/M4-T020-dcm-geometry). NOT yet integrated/gated.
2. **D-055 captured+executed** (owner: Fable for main + reviewers): model_selection.toml →
   claude-fable-5 + ["claude-opus-4-8"] quota fallback; five gate-reviewer agent files
   reverted to fable-5 (89c4e304 flip undone). **D-058-R004 now governs:** regular weekly
   Fable quota exhausted per owner; loop + reviewers CONTINUE on fable-5 via EXTRA USAGE;
   pin stays; opus chain = last resort only, never a pin flip.
3. **D-043 owner walkthrough happened live** (R001 evidence: full flow works on owner
   device). Findings: (1) provenance links missing + (2) lot outline invisible → fixed in
   M5-T025; (3) ZoLa blank = PROVEN city-side outage (labs-layers-api /v1/layer-groups
   HTTP 500, owner console + independent fetch; our link verified twice); (4) 125-vs-83
   Taylor St = PLUTO one-address-per-lot (verified live vs SODA), UX carry-forward
   candidate packet.
4. **D-056 captured + M5-T025 BUILT AND FULLY GATED**: safe provenance source links
   (constant-prefix + validated Socrata id, both surfaces), lot-outline root-cause fix
   (one-time `load` never fires on degraded-GL device; style.load arm + error surface +
   maxZoom 19.5), NavigationControl zoom. G3 PASS w/ F1 record-correction applied
   ([ORCH-CORRECTED] comment/report/evidence-map edits at 63495416) + delta-attestation;
   G4 PASS + mechanical identity-carry; **CI green at BOTH heads** (18/18 at 10aaedcc; all
   jobs at f5e7f4a1). REMAINING: DCV rows + accept.
5. **D-057 captured + M5-T026 BUILT** (plain-URL mode): additive INTERNAL_RULE_EVAL_DEFAULT_ON
   (absent = today's behavior; kill switch + bookmarks preserved; zero e2e edits), 71-row
   gate matrix, checklist §2a. Producer material integrated at **0b112357**; CI on the
   seam push pending verify; submit/G3/G4/DCV/accept REMAIN.
6. **D-054 knowledge tiers updated** (D-058-R003): Tier-1 append landed (classifier-retry
   pattern, empty-.test.ts-placeholder trap, evidence-map shape, \r-strip; budget PASS);
   Tier-2 current (loop shift-1 close, relaunch pattern, MapLibre rule, findings).

## IN FLIGHT AT LANDING

- **No sub-agent alive**; both producers + both reviewers returned and are reconciled.
  The loop is DOWN (benign completion); supervisor state PAUSED_RECOVERY (checkpoint
  refusal) — run the down-state drill before relaunch. Session-bound watcher died with
  the session (nothing to watch).
- **CI run on the seam tip** (M5-T026 code) was in flight at landing — verify before
  gating M5-T026.

## NEXT ACTIONS (exact order)

1. **M5-T025 acceptance**: dispatch directive-compliance-verifier (read-only, primary
   checkout, pin the live head; request conditional-restamp pre-auth UP FRONT) over
   D-056-R001/2/3 + D-046-R001/2 + D-040-R001 at the gated identity; then `accept`; then
   tell the owner the deploy step (below). Advisories to carry as candidates: G3 A1/A2/A7,
   G4 NB-1/2/3.
2. **M5-T026**: verify CI green on the tip → submit (evidence map, canonical
   `requirements:{id:[prose]}` shape) → G3 (code-reviewer) + G4 (qa-engineer) wave →
   DCV → accept. Then the owner's activation var note (D-057-R004).
3. **M4-T020**: cherry-pick `d7766b8d` → submit → G3 (code-reviewer) + G4 (qa-engineer)
   (+ ruff/api CI evidence) → DCV (D-045/D-046 rows) → accept.
4. **OWNER SEAM MESSAGE** (D-056-R006 + D-057-R004 + D-043): Render web service → Manual
   Deploy (branch tip) → add env var `INTERNAL_RULE_EVAL_DEFAULT_ON` = `1` (web service
   only; save restarts, no rebuild) → refresh plain `/property`. Honest note: T025 is
   review-complete, T026 review completes next session.
5. **Relaunch the loop (D-053/D-058 shift 2)**: next packet (B4 buffer engine, or hold
   until M4-T020 accepted since B4 consumes B3); adapt scratchpad/relaunch_m4t020.ps1
   (fresh run-id persistent-local-35, new packet/branch); down-state drill first (deny
   stale asks w/ \r-strip, clear-recovery); worker stays fable-5 (D-058-R004). Then quiet
   monitor + stamp only.

## OWNER RETURN ITEMS

Manual Deploy + DEFAULT_ON var (above). Extra-usage enablement/limits = owner account
setting (D-058-R004). claude-sonnet-5 on the loop config.toml allowlist (D-053-R004).
RQ-005 DCP email. Supabase B-001. G6. PR #241 stays open. D-043 posture: internal only.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. R595/auto-accept stays shadow (D-053-R002). Expansion hold
(lot-outline increment excepted). §G admissions (zero new deps this session). Thin client
(NO local npm/node_modules anywhere — CI is the executable authority for web). G6
owner-only; DRAFT-until-G6. Stop-and-ask only credentials/payments/legal (D-008).
Producers sonnet-5 via dispatch override (D-047); reviewers/orchestrator fable-5 (D-055).

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/{M4-T020,M5-T025,M5-T026}.json` ·
`directives/{D-055,D-056,D-057,D-058}*/` + index.json · `gates/M5-T025-G{0,3,4}.json`,
`gates/{M4-T020,M5-T026}-G0.json` · `reports/M5-T025-{G3-code-review,G4-test-adequacy,
producer-report,evidence-map}` · wt-m4t020 commit `d7766b8d` · `docs/WORKING_KNOWLEDGE.md` ·
`docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` (§2a new) · audit chain seq 776–847.

## SUCCESSOR PROMPT (copy into the new session)

Resume from handoff seq 111: work from durable repository evidence, not assumptions about
the prior conversation. Verify root/branch/HEAD (expect
C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on candidate/D-024-mrl-option-b; origin may have
advanced — ledger and CI win), then read CLAUDE.md, docs/SESSION_HANDOFF.md, and
docs/WORKING_KNOWLEDGE.md (Tier-2 must-read; maintain both D-054 tiers). Run `python
tools/project_control.py status`. State: 204 accepted; M5-T025 fully gated (DCV + accept
remain), M5-T026 built + integrated (CI verify, submit, gates remain), M4-T020 built by
the loop (cherry-pick d7766b8d from wt-m4t020, submit, gates remain); loop DOWN after a
benign unit-complete close — relaunch is NEXT-ACTION 5 with the worker staying
claude-fable-5 via extra usage (D-058-R004; regular weekly exhausted — never flip the pin
to opus outside a genuine hard-stop fallback). Execute the NEXT ACTIONS in the handoff's
exact order; deliver the owner seam message (Manual Deploy + INTERNAL_RULE_EVAL_DEFAULT_ON=1
+ refresh) after M5-T025 acceptance. Stop only for owner-only items
(credentials/payments/legal, PR #241, production, G6, Supabase). Report READY TO RESUME or
BLOCKED before changing anything.
