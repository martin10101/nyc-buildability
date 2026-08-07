# D-010 initiative plan — Autonomous Engineering V2 (parent M0-T037)

**Directive:** D-010 (captured `c0516f3`, verified PASS, merged PR #155, main `45dfdc2`).
**Parent:** M0-T037. **Author:** orchestrator. **Status:** active plan (updated as tasks land).
**Prohibitions honored:** no enormous task, no enormous PR, no big-bang refactor, no general
legacy cleanup (D-010-R103); supervisor tasks cite qualifying evidence (AD-093); R595 remains a
mandatory blocking prerequisite before ANY activation (D-010-R104; M0-T036-ACTIVATION-CHECKLIST).

## 1. Three-way division (D-010-R102)

### Lane 1 — minimum autonomy (MAY block product work; Section 0A.8 ceiling)
Dependency-ordered; each task is one bounded PR with its own rollback point (revert of its merge
commit; the supervisor stays shadow-only throughout, so reverts are externally safe):

| Order | Task | Bounded unit | 0A.8 capability |
|---|---|---|---|
| 1 | M0-T038 | Preserve post-merge SESSION_HANDOFF update (dedicated PR) | — (R098 obligation) |
| 2 | M0-T039 | Freeze M0-T036 behavior identity + defect-only lane | 1 |
| 3 | M0-T040 | Authority policy: Tier A/B/C/D, ADR-006, policy tests, incident replay | 8 (policy half), 9 |
| 4 | M0-T041 | Quota classifier + G3 B-rows + R207 live sampling + pending_prompt hardening | 2, 3, 6, 7, 9, 10 (defect closure) |
| 5 | M0-T042 | Codex ephemeral review end-to-end + 0A.4 budgets + minimal root AGENTS.md | 4 |
| 6 (∥ with 4) | M0-T043 | Bounded context-pack builder | 5 |
| 7 | M0-T044 | Automatic safe GitHub flow (Section 19.4 proofs, dry-run harness) | 8 (mechanism half) |
| 8 | M0-T045 | R595 supervised rehearsal + Section 16.2 promotion evidence | 11 gateway |

M0-T043 has no path overlap with M0-T041 and may run in parallel under the 2-agent concurrency
cap (D-010-R106). M0-T041/T042/T044 share `tools/agent_supervisor/` and are strictly sequential.

After M0-T045: promote shadow → supervised-auto on evidence; run **two real product tasks**
through the pipeline (0A.8 item 11) → limited-auto promotion on evidence → freeze nonessential
supervisor expansion → 80/20 rule → automatic product-chain continuation (D-010-R110, AD-092,
AD-094, AD-096).

### Lane 2 — non-blocking supervisor backlog (AD-091; contracted only with AD-093 evidence)
Registered here, NOT contracted as ledger tasks yet:

- **B-1** Full path-scoped `AGENTS.md` hierarchy + canonical-policy drift tests (AD-041..AD-043
  beyond the minimal root file delivered in M0-T042).
- **B-2** Code-graph V2 (AD-047..AD-052) beyond relationships needed for context packs; benchmark-gated.
- **B-3** Supervisor generic-core/NYC-adapter boundary (AD-053..AD-054); physical extraction
  (AD-055..AD-056) only after the Section 14.3 gates.
- **B-4** Repository inventory + legacy register (AD-057..AD-059); deletion only per Section 15.
- **B-5** Control-plane defect: task `allowed_paths` with parenthetical annotations defeat the
  content-identity matcher (reproduced on M0-T036, identity `08f8db0e` stable across code changes).
  Evidence-qualified defect fix (AD-093 "reproduced defect"); new tasks in this plan already use
  clean globs.
- **B-6** Remote approvals, extra audit anchoring, replay examples beyond demonstrated defects,
  dashboards, enterprise generalization, commercialization (0A.8 non-blocking list) — parked.

### Lane 3 — NYC product (resumes automatically; Section 0A.11 sequence)
1. Resolve the dormant D-009/M0-T019/M2-T014 batch (AD-066) — existing contracted tasks; branches
   preserved on origin (`control/D-009-depsec-and-m0t019-dispatch @ a953d0d`,
   `task/M0-T019-fes9-exception @ e96d718`); B-017 clears with the regenerated-lock CI evidence.
2. Secure survey/PDF ingestion implementing the accepted M2-T014 findings (AD-067; Section 17.2).
3. Architect correction/review workflow (AD-067).
4. Legal-corpus expansion — M3 chain (AD-068).
5. Systematic zoning-rule families — M4 (AD-069; G6 split per AD-061..AD-063).
6. Scenario-engine expansion — M5 (AD-070).
7. Architect evidence/reporting + pilot flow (AD-071; Section 17.6).
8. Five-borough golden-property validation (AD-072); then the full roadmap (AD-073).

The first two real product tasks for the 0A.8 item-11 proof are drawn from the top of this lane.

## 2. AD-001..AD-096 traceability (D-010-R102 item 6)

| AD rows | Owner |
|---|---|
| AD-001..AD-005 (scope preservation) | Standing constraints on every task; re-verified at each gate and at parent close-out; no task may narrow scope. |
| AD-006..AD-010 (autonomy) | M0-T040 (policy + tests); M0-T044 (mechanism); AD-009/AD-010 also standing operating rules. |
| AD-011..AD-016 (controller architecture) | Existing accepted supervisor (M0-T036) + M0-T041/M0-T042 verification; AD-016 standing practice + M0-T040 split-trigger policy. |
| AD-017..AD-018 (repo memory, handoff) | Proven by M0-T036 (durable state, handoff schema); re-proven in M0-T045 rehearsal. |
| AD-019..AD-026 (registry, telemetry, thresholds) | M0-T041 (classifier, sampling, conservative-unknown, thresholds already model-aware in supervisor; gap-closure verifies). |
| AD-027 (ephemeral Codex) | M0-T042. |
| AD-028..AD-034 (child lifecycle) | Supervisor existing tests + M0-T041 confirmation; live proof in M0-T045 (AD-031/AD-076). |
| AD-035..AD-040 (provider fallback) | M0-T041 (quota classifier is the reproduced gap); Section 19.3 proofs in the M0-T041/M0-T045 suites. |
| AD-041..AD-043 (AGENTS.md, canonical policy) | Minimal root file: M0-T042; full hierarchy + drift tests: backlog B-1. |
| AD-044..AD-046 (context packs) | M0-T043. |
| AD-047..AD-052 (code graph V2) | Backlog B-2 (non-blocking per AD-091); AD-047/AD-052 standing constraints. |
| AD-053..AD-060 (separation, cleanup safety) | Backlog B-3/B-4; AD-058..AD-060 standing prohibitions on every task. |
| AD-061..AD-064 (legal boundary) | M0-T040 records the G6 split; AD-064 lands with pilot UI product tasks (Lane 3 items 3/7). |
| AD-065 | M0-T039. |
| AD-066 | Lane 3 item 1 (existing batch tasks). |
| AD-067..AD-073 (product) | Lane 3 items 2..8 (existing milestones M2..M6 + successors). |
| AD-074..AD-079 (activation, evidence) | M0-T045 (+M0-T044 for AD-077; AD-078 counter starts in M0-T041 telemetry; AD-079 standing). |
| AD-080 (Section 21 report) | M0-T037 close-out. |
| AD-081..AD-088 (Codex efficiency) | M0-T042 (+0A.4 budget shared with M0-T043). |
| AD-089 (usage per product task) | M0-T041 telemetry, measured during Lane 3 tasks. |
| AD-090..AD-092, AD-094, AD-096 (ceiling, 80/20) | Parent-enforced sequencing (M0-T037); measured over rolling 10 completed units. |
| AD-093 (no speculative features) | Standing gate on any new supervisor task; each Lane 1 task carries its evidence citation. |
| AD-095 (efficiency report) | M0-T037 close-out. |
| R097..R110 (launch instruction) | R097/R099 done (Phase 0 record in this session; orch worktree); R098 → M0-T038; R100/R101 done (PR #155); R102/R103 → this plan; R104 → M0-T045 gateway; R105..R109 standing operating rules; R110 → parent sequencing. |

## 3. Rollback points

- Every Lane 1 task = one PR; rollback = revert of that merge commit.
- The supervisor remains **shadow-only** until M0-T045 evidence passes; policy changes (M0-T040)
  are docs/tests until the mechanism tasks land, so reverting them restores the prior posture
  cleanly.
- M0-T039's freeze record pins the last-known-good supervisor identity for any defect-lane revert.
- Activation promotions are mode flags with the emergency-stop path (0A.8 items 9/10) proven in
  M0-T041/M0-T045 before any promotion.

## 4. Allocation measurement (AD-092/AD-095)

Counted over completed bounded task units (product vs control-plane classification per 0A.9):
recorded in each accept note, aggregated in the M0-T037 close-out report over a rolling window of
ten completed units once two limited-auto product tasks complete. Whole percentages only.
