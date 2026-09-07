# M0-T109 / D-024-R754 — Second-Round Independent Verification (Closure DCV)

**Verifier:** directive-compliance-verifier (named `independent_verifier` for D-024-R754)
**Head reviewed:** `f64ea5f1920ae73a0cebe239de8728c9ff736862` (branch `candidate/D-024-mrl-option-b`) — confirmed via `git rev-parse HEAD`
**Mode:** read-only. Evidence reproduced from primary sources (live audit chain, git objects, packet/queue files); producer narratives and the two prior matrices treated as claims.
**Requirement text (authoritative), D-024-R754, `requirements.json` line 24751, `source_ref` `source-051-amendment.md#verbatim-owner-directive`:**
> "Across the next two or three real operational tasks, obtain durable evidence for every remaining local-autonomy capability: (1) … (2) … **(3) an accepted task automatically advances to the next ready task;** (4) … (5) … (6) … (7) the foreground owner view accurately shows task, stage, worker model, Codex verdict, pending owner decision, and final result."

## 1. What I independently reproduced

**Live run-06 audit chain** (`C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\9aca7075…\audit.jsonl`, 82 records) — recomputed with the controller's own `tools/agent_supervisor/audit_log.py`:
- `AuditLog.verify_chain()` → `ok=True`, records_checked=82, head_seq=82, head_digest=`dff7607edfd84b66ecbb2a879b75f6ab939008c053e5ed9980ccbeca86e92907`.
- Independent per-record recompute (not via `verify_chain`): **82/82 digests match, 0 prev-link breaks**, genesis `prev_digest` = 64 zeros. Integrity holds.

**The fact-3 window, reproduced field-by-field from the chain:**

| seq | ts (UTC) | event | key fields |
|----|----|----|----|
| 49 | 04:27:59.116 | `codex_review_decision` | decision=`COMPLETE`, policy=`stage_complete`, run=`persistent-local-06` |
| 51 | 04:27:59.151 | state_transition | `decision_schema_valid`, reviewed_checkpoint=`M0-T025-2026-09-07-handoff-unit-01` |
| 52 | 04:27:59.169 | state_transition | POLICY_CHECK→COMPLETE, `decision_complete` |
| 53 | 04:27:59.214 | `cross_task_advancement` | task_id=`M0-T025`, checkpoint=`M0-T025-2026-09-07-handoff-unit-01`, **newly_recorded=true**, run_id=`""` |
| 54–56 | 04:35:19–21 | `approval_owner_denied` ×3 | decision=`DENY`, `denied by the owner at the CLI` (3 distinct request_ids) |
| 57 | 04:37:20.630 | `recover_boot` | `SAFE_CHECKPOINT` |
| 58 | 04:37:20.649 | `cross_task_dispatch` | **successor=true**, task_id=`M0-T149`, worktree=`wt-m0t149` |
| 59–60 | 04:37:20 | state_transition | run_closed COMPLETE→IDLE, start_command IDLE→PREFLIGHT, **operator_initiated=true** |
| 61 | 04:37:20.842 | `run_budget_resumed` | resumes=5, `run_budget/persistent-local-06` |
| 79–82 | 04:51:57 | claude_unit_completed / state_transition / owner_touch_recorded | observed_models=`['claude-fable-5']`; PAUSED_RECOVERY `checkpoint_field_mismatch starting_sha='bb71b2ef'…`; `no_valid_checkpoint` |

**Mechanism (read from `tools/agent_supervisor/next_task.py:824–888`):** `cross_task_advancement` (seq 53) records that the *completed* task M0-T025 advanced; `cross_task_dispatch successor=true` (seq 58) is the actual dispatch of the *next* task. Under queue v3 (`ordered=[(M0-T025,False),(M0-T025,True),(M0-T149,True)]`, `--max-tasks 2`) the duplicated M0-T025 was counted `already_advanced` (line 832) and consumed the second slot, so the original owner boot hit `max_tasks_reached` (line 838) **without ever dispatching M0-T149**. Only after the orchestrator authored successors-only queue v3b (commit `207191db`, verified at HEAD to list `tasks=[M0-T149]`) and the owner relaunched did seq 58 fire.

**Task state at HEAD:** `M0-T025.json` status=`awaiting_gate` (progress 85); `M0-T149.json` status=`awaiting_gate`. **No task was ledger-accepted.**

**Fact-7 artifact:** `project-control/reports/D-024-R754-run06-relaunch-transcript.txt`, commit `3618caee` (verified ancestor of HEAD, `--stat` = 1 file +49). Read in full: its program-output section shows only the relaunch's refusal tail — `mode: limited-auto`, `classification: SAFE_CHECKPOINT`, `next state: PREFLIGHT`, `DISPATCHED … final_state=PAUSED_RECOVERY stopped=no_valid_checkpoint`, `owner touches counted: 1 of budget 2`, `REFUSED (unsafe, exit 11): no_valid_checkpoint`. The header attributes it to `session_01WBbzN5…` (orchestrator paste). It does **not** display worker model or a Codex verdict, and names no task id in the program output.

**Registry integrity:** `python tools/validate_directive_compliance.py --check` → exit 0 (source digests / locked ids intact).

**Facts 1/2/4/5/6:** verified in round 1 (200-record chain) and re-attested by ci-evidence-verifier on the archive; I confirmed the cited records are present in the archive (`…\audit.jsonl.forked-evidence-20260907-033630`, 38 matches for the seq-98/109/REVISE/`cross_task_dispatch` patterns). I did not re-run the archive digest recompute (read-only guard false-positived on the archive path); this is corroborative only and is **not** the basis of my verdict. I do not re-open 1/2/4/5/6.

## 2. Decision on the two open capabilities (judged on the owner's captured text)

**Capability 3 — OPEN (not satisfied on durable evidence).** The advancement *decision* is genuinely automatic and zero-touch (seq 49→53, same second, 7 minutes before any owner action). But the owner's load-bearing word is **"automatically advances to the next ready task"** — the move to and dispatch of the *next* ready task. That step was **not** unattended: three owner `approval_owner_denied` events sit in the transition window (seq 54–56), and the successor dispatch (seq 58) occurred only after an **operator-initiated relaunch** (seq 57/59/60 `operator_initiated=true`) following an orchestrator-authored queue repair (v3b, `207191db`). In **no single run** did an accepted/COMPLETE task automatically advance to *and dispatch/run* the next ready task with zero owner touches. Additional weakening: COMPLETE/`stage_complete` is the loop's terminal review verdict, explicitly **not** ledger acceptance (controller's own seq-52 note), and M0-T025 remains `awaiting_gate` — so the strict reading of "accepted" is entirely unmet, and the loop-verdict reading still fails the "automatically/unattended" element.

I have refined, not blindly applied, the first round's "zero owner touches" wording, and I still find it should govern **with reasons**: its purpose was to prove the loop progresses through task transitions without owner mediation, and the durable evidence shows the opposite in this run (owner denials + owner relaunch in the transition). The queue-defect (DL-1) explanation legitimately exonerates the *machinery*, but R754 demands durable evidence of the *capability firing*, and unattended advance-to-next-task did not fire. Adopting the producer's narrower "acceptance-class verdict PLUS successor=true dispatch" definition to reach ALL-SEVEN would drop the "automatically" element — that would be laundering the over-claim, which the charter forbids equally.

**Capability 7 — OPEN (unverifiable from a trustworthy artifact).** The one new durable artifact is a self-attested orchestrator paste that captures only a PAUSED_RECOVERY refusal tail; it does not display worker model or Codex verdict and is not a machine-signed capture. It does not demonstrate the foreground view accurately showing all six fields during a real verdict/advancement flow. This is materially the same gap round 1 found (self-attested; no adequate transcript) and is not closed.

Because at least capabilities 3 and 7 remain open, **R754 cannot flip to PASS**; `accept()` must continue to fail closed on R754, and M0-T109's directive gate is not clearable.

**Minimum to close (restated, actionable):**
- *Fact 3:* one correctly-authored (successors-only) multi-task-queue run where, **within a single unattended boot with zero owner touches**, the chain shows COMPLETE/`stage_complete` → `cross_task_advancement` → `cross_task_dispatch successor=true` → `run_one(next)` on a genuinely different next ready task, recorded contiguously in the hash-chained audit.
- *Fact 7:* a machine-captured (controller-written) foreground/status artifact showing all six fields for a run that actually reaches a Codex verdict and advancement, cross-consistent with the digest-valid chain.

## 3. Mechanical findings (for the acceptance that a PASS would have enabled)

**3a. Current verification.json rows (`…/D-024-fable-codex-loop/verification.json`).**
- R754 per-requirement entry in the M0-T109 task row: `state = "UNVERIFIABLE"`, `verified_at = "2026-09-06T10:20:00+00:00"` (round-1 reasons).
- M0-T109 task-row header: `reviewed_sha = "47ee3a04b46d02bed6af71c849b0793491270aa5"` (STALE vs HEAD `f64ea5f1…`), `reviewed_manifest_sha256 = "d597a4e26d190251c42d2d30b76d47a8cabcd2cbba9bc20ad63f8af089bc855a"`, `verification_report = "project-control/reports/M0-T109-DCV-report.md"`. Requirement-registry row in `requirements.json` (line 24750): `status = "pending"`, `reviewed_sha = ""`.

**3b. Material identity (restamp precondition) — blobs BYTE-IDENTICAL between `47ee3a04` and HEAD `f64ea5f1`:**

| allowed_path | @47ee3a04 | @f64ea5f1 | result |
|---|---|---|---|
| `.claude/hooks` (tree) | `cd24aeea45a43aa3139f6e78dadc223e40909306` | `cd24aeea45a43aa3139f6e78dadc223e40909306` | UNCHANGED |
| `project-control/reports/M0-T109-guard-hardening.md` | `c27862fe76c411b6b6729c42b7c84519fe97089c` | `c27862fe76c411b6b6729c42b7c84519fe97089c` | UNCHANGED |
| `tools/test_readonly_agent_guard_powershell.py` | `0fd81db3be89df83902dc07dd24a5a632b749173` | `0fd81db3be89df83902dc07dd24a5a632b749173` | UNCHANGED |

The reviewed content identity is stable, so the `reviewed_manifest_sha256` (`d597a4e2…`) is unchanged and a mechanical `reviewed_sha` restamp to HEAD is *permissible for accuracy* — but it does **not** clear the gate, because the R754 row stays UNVERIFIABLE.

**3c. Exact verification.json content attested (recorded by the orchestrator; R754 stays UNVERIFIABLE).** See the applied rows in `project-control/directives/D-024-fable-codex-loop/verification.json` and the R754 registry-row `status_reason` in `requirements.json` — recorded verbatim from this report's attestation.

## 4. Minor provenance note (non-material)
Producer prose (queue v3b authority text, D-032 defect-lane doc) names the completing checkpoint `M0-T025-persistent-local-06-u01-cp1`; the authoritative chain records `M0-T025-2026-09-07-handoff-unit-01` (seq 51 reviewed_checkpoint = seq 53 checkpoint_id). The chain is internally consistent; this is a prose/primary-evidence naming discrepancy only and does not affect any finding.

VERDICT: FAIL

---

*Orchestrator preservation note: saved VERBATIM from the directive-compliance-verifier agent-return channel (2026-09-07; transport framing removed, HTML entities decoded; section 3c's inline JSON is applied directly to the registry files and referenced here rather than duplicated). This second-round FAIL supersedes the ci-evidence-verifier's same-day ALL-SEVEN-VERIFIED for the ROW STATE: the two reports agree on artifact authenticity and chain integrity; the named verifier's stricter reading of the owner's captured text ("automatically advances") governs the verification.json state. M0-T109 and M0-T145 remain parked on R754.*
