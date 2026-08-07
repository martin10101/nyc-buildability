# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-07 (D-010 session rotation)**. **The block below supersedes the older sections
further down** (kept only as history); the ledger wins on any conflict.

## CURRENT STATE (2026-08-07 — confirm against the ledger + git)

**Owner directive D-010 (Autonomous Engineering V2) is captured, verified, and executing.** This
session (rotated at a safe seam per D-010-R108 after M0-T041) merged six PRs; accepted count **60**.

- **D-010 captured** as the canonical directive (PR #155): source-001 = verbatim intake file
  (`.claude/OWNER_DIRECTIVE_AUTONOMOUS_ENGINEERING_v2.md`, retained per R101 until a cleanup decision);
  source-002 = owner launch instruction; 110 reqs (R001..R096 = AD-001..AD-096 1:1; R097..R110
  launch rows) + independent capture verification PASS. Amendments: v2 applicability binding
  (PR #157 — conjunction-semantics fix, rows were inert); **source-003 = owner-typed authorization
  for the M0-T040 commit + pre-merge G3/G5/DCV sequence (R111/R112)**; v4 = R078/R089 → M0-T045.
- **Task architecture** (PR #156): parent **M0-T037** + wave-1 **M0-T038..M0-T045**
  (minimum-autonomy lane per 0A.8) + backlog B-1..B-6 + product lane — see
  `project-control/reports/D-010-INITIATIVE-PLAN.md` (AD traceability + rollback points).
- **ACCEPTED + MERGED this session:** M0-T038 (handoff preservation, PR #158 — G3 caught a real
  39-char-SHA defect in the prior session's update; preserve-with-correction); M0-T039 (supervisor
  freeze, PR #159 — tree `e8eeb4fa`, suite baseline 1165/1163/0/2, defect-only lane rule);
  **M0-T040 (ADR-006 autonomy tiers, PR #160)** — Tier A/B/C/D verbatim from D-010 §5, D-004-R721
  superseded FOR TIER A ONLY, G6 split recorded, 22-test policy suite; the commit itself was
  **owner-executed** (`b841b4f`) after the auto-mode classifier twice denied the permission-model
  edit — authorization captured as D-010 source-003; G3+G5(security)+DCV all PASS **before** merge
  per R112; M0-T041 (supervisor gap-closure A, PR #161) — quota classifier (fail-closed, no
  verified_live fixture), R207 live sampling, pending_prompt hardening; B-1..B-4 verified already
  fixed in V1.1; suite 1189/1187/0/2; G3+G4+G5+DCV PASS at identity `78ed0cc1`.
- ⛔ **SHADOW-ONLY throughout; R595 supervised rehearsal remains the MANDATORY BLOCKING prerequisite
  before ANY activation** (M0-T036-ACTIVATION-CHECKLIST; D-010-R104). ADR-006 changes the authority
  MODEL only; the orchestrator executes Tier A actions manually until the activation path completes.

## NEXT SESSION — resume checklist

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (origin/main was
   `24b0ff6` at rotation).
2. **Next dependency-valid unit: M0-T042** (Codex ephemeral review integration + root AGENTS.md;
   deps M0-T041 accepted). **M0-T043** (context-pack builder, no deps, disjoint paths) may run
   parallel under the 2-agent cap — but note ledger writes serialize through state.json, so prefer
   sequential task branches (T042 then T043) unless prepared to reconcile a state.json merge.
   Then M0-T044 (GitHub flow; deps T039+T040 ✓), then **M0-T045 (R595 rehearsal + promotion pack)**.
3. **Pre-R595 hardening items registered for M0-T045** (from M0-T041 reviews, all non-blocking):
   G4 coverage locks — (a) pending_prompt failure-path-preserves-record regression, (b) empty-shape
   verified-fixture-not-catch-all lock, (c) real-sampler CLI wiring integration test + WARN-notify
   path + doctor unit test; G5 INFO-1 — before flipping any quota fixture to `verified_live=True`,
   confirm captured live bytes are TRUE account-quota exhaustion (not transient 429).
4. Task workflow that works (proven ×4 this session): task branch from origin/main → G0 + claim →
   producer (isolated scope) → commit deliverables → evidence map + packet N2-widening → progress →
   submit (identity stamps at HEAD; commit ledger writes) → parallel independent reviews (≤2 agents)
   → record gates (reports committed FIRST, gates stamp at HEAD) → DCV → verification row stamped at
   accept-time HEAD **uncommitted**, accept, commit together → push → PR → CI green → merge (Tier A
   per ADR-006). Worst-case rework loop proven on M0-T038 (honest FAIL recorded → fix → delta
   re-reviews → PASS).
5. **Classifier-denial protocol (proven on M0-T040):** if the auto-mode classifier denies a commit of
   permission-model/self-instruction files, STOP, surface to the owner with the exact `!` command
   line; owner types authorization (capture verbatim as a D-010 amendment) and runs the commit
   in-session; then the mandated independent reviews before merge. Never route around the classifier.
- **Reviewer models:** gate reviewers ran `claude-opus-4-8` + `xhigh` (the 5 flipped agent files
  remain **uncommitted in the PRIMARY checkout** per the standing fallback; revert to
  `claude-fable-5` pins when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`.
- **Primary checkout** (`…\nyc-development-feasibility-claude-pack`, branch task/M0-T036-supervisor-bridge
  @ 57ccb44): left intact per D-010-R109/R099. Its uncommitted docs/SESSION_HANDOFF.md diff is now
  OBSOLETE (superseded by the corrected, merged M0-T038 version + this refresh) and may be discarded
  at next convenience; the 5 reviewer-pin edits stay by design; other untracked files classified in
  the Phase 0 record (D-010 capture PR #155 context).
- **Dormant batch (Lane 3 item 1, AD-066):** D-009 + M0-T019 + M2-T014 preserved on origin
  (`control/D-009-depsec-and-m0t019-dispatch @ a953d0d`, `task/M0-T019-fes9-exception @ e96d718`);
  resume after the minimum-autonomy lane or as the product chain restarts; B-017 clears with the
  regenerated-lock CI evidence. Old PR #64 is stale (supersede/close when the batch resumes).
- **Owner touches this session: 1** (the M0-T040 authorization — exactly the touch the safety
  surfaces exist to require). Standing holds unchanged: deployment/G6/Graphify/expansion.

## Machine-readable handoff (D-010 §7.2; sha256 digest over the JSON with digest="")

```json
SEE project-control/reports/session-handoff-2026-08-07.json (digest 641b086ed6ec12fb9eff1f46a63c79d5de39654b57defd91583e574e2a211b4b)
```

---

_History (pre-this-session, may be stale):_

## PRIOR STATE (2026-08-05 late, superseded)

- **`task/M0-T036-supervisor-bridge`** — **M0-T036 ACCEPTED (shadow-only) 2026-08-06; MERGED to `main`
  2026-08-07T00:06:56Z (owner-authorized).** accepted count **56**. Delta re-gate V1.2.3 at `4ff4d88`
  all PASS (G3/G4/G5 + DCV); 585-req independent `verification.json` (584 PASS + R593 NA); acceptance
  commit `9d7573f`. **PR #154 MERGED → `main` = `cec785f97ac1037df1fb2e1b114260eb106b7de0`** via the
  repository-required **merge-commit** method (no bypass; branch not deleted). The merged head was a
  **content-empty trigger commit `57ccb44`** (git tree `67e97dda` — byte-identical to acceptance head
  `4f8c1d2`); it existed ONLY to emit a push/PR event so the **8 required checks** could run during the
  **2026-08-06 GitHub Actions major outage** (15:22 UTC; webhooks throttled) — no file content changed.
  All 8 required checks PASS on `57ccb44` (plus 8 non-required, 16/16 green). **SHADOW-ONLY; nothing
  activated.** R593 resolved via owner Option A (accepted residual deferred to R595, D-007-R618/R621).
- **M0-T019 / D-009 / M2-T014 batch** — see the dormant-batch note above; historical detail in
  `project-control/reports/BATCH-RESUME-2026-08-05.md` (on the batch branch).
- Standing rules carried forward: reviewer-model fallback (revert on "Fable is back"); owner
  escalation boundary (D-008); batching at submit; ledger writes via `tools/project_control.py` only;
  directives written with explicit LF; task files CRLF-preserved on edit.
