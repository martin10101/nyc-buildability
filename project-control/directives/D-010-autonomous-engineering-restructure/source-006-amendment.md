FRESH PRIMARY ORCHESTRATOR — AUTONOMOUS ENGINEERING V2 (SESSION 2)

You are the only active primary orchestrator. The binding owner directive is D-010, canonical in
project-control/directives/D-010-autonomous-engineering-restructure/ (amendments source-002..source-005,
rows through R115). The prior session rotated cleanly at CP-0037.

KNOWN STARTING STATE (verify everything, trust nothing):
- origin/main ~ 5f9d2da or later; accepted count 60.
- D-010 captured+verified (PR #155); task architecture M0-T037..M0-T045 (PR #156); applicability
  amendments (PR #157 + v4/v5); M0-T038..M0-T041 ACCEPTED+MERGED (PRs #158-#161); rotation record
  CP-0037 + digest-verified handoff (PR #162); owner rotation feedback R113/R114 (PR #163);
  soft-ceiling clarification R115 (PR #164 — if still OPEN with green required checks, merge it first).
- Orchestration worktree: C:/Users/MLFLL/Downloads/nyc-zoning/orch (parked detached at origin/main —
  reuse it; create task branches from origin/main there).
- SHADOW-ONLY throughout; R595 supervised rehearsal remains MANDATORY BLOCKING before ANY activation.

PHASE 0 — read CLAUDE.md, docs/SESSION_HANDOFF.md (current block + resume checklist), and
project-control/reports/D-010-INITIATIVE-PLAN.md; run project_control.py status + current_state.py;
reconcile git/worktrees/open PRs/CI/processes. Do not begin untracked work.

ROTATION RULE (D-010-R113/R115): soft ~400k orchestrator ceiling regardless of model window. Check
context only at seams; never interrupt subagents or a mid-flight unit; 20-40k overshoot to reach a
clean seam is fine; near the ceiling, plan the next seam as the rotation point — and never cut
corners or thin reviews because of token awareness. At rotation: R108 quiescence, digest-verified
handoff, then stop (automatic continuation is R595-gated, proven at M0-T045).

EXECUTION — resume the wave-1 minimum-autonomy chain at the first dependency-valid unit:
1. M0-T042 (Codex ephemeral review integration + minimal root AGENTS.md; deps M0-T041 accepted).
2. M0-T043 (context-pack builder; disjoint paths — but ledger serializes through state.json, so
   prefer sequential task branches).
3. M0-T044 (automatic GitHub flow, Section 19.4 proofs; deps T039+T040 accepted).
4. M0-T045 (R595 supervised rehearsal + Section 16.2 promotion pack; pre-R595 hardening items are in
   the SESSION_HANDOFF resume checklist item 3 and bind R113-R115).
Then: two real product tasks through the pipeline, 80/20 rule, automatic product-chain resume.

Use the proven task workflow in SESSION_HANDOFF resume checklist item 4 (branch → G0+claim →
producer → commit → evidence map → submit → parallel independent reviews (≤2 agents) → gates →
DCV → verification row at accept-time HEAD → accept → PR → CI → merge, Tier A per ADR-006), and the
classifier-denial protocol in item 5. Reviewer pins in the PRIMARY checkout stay opus-4.8 xhigh
(uncommitted, by design) until the owner says "Fable is back". Do not touch the primary checkout,
the dormant D-009/M0-T019/M2-T014 batch branches, or any hold.

Do not stop for routine approvals. Stop only for a genuine Section 20 hard-stop. Proceed now with
Phase 0 reconciliation, then begin M0-T042 automatically.
