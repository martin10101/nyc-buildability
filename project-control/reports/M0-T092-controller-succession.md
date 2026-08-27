# M0-T092 — Unit F: controller state machine, safe seams, exact-once succession, outage handling (D-024 Phase D)

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R102** (Phase D; packet-named). Status: **STAGED (claim + G0 + scenario pack)** — this
session (under owner directive D-031, ~750k context then handoff) authored the scenario pack and
reuse boundary at a clean seam and hands off; the successor implements from this frozen pack with
a fresh context budget. This mirrors how the current session was itself handed M0-T105 ("in flight
at 20% with scenario pack"). No implementation code is written in this staging seam.

## 0. Reuse boundary (R018/R029: prove existing architecture, extend — never duplicate)

Unit F is a **prove-and-extend** unit over the accepted supervisor. The existing surface (all
accepted, supervisor-FROZEN — every change diffs against `M0-T039-supervisor-freeze.md` and must
re-establish the suite baseline):

| Accepted module | Lines | What it already provides (REUSE, do not duplicate) | Unit-F extension |
|---|---|---|---|
| `state_machine.py` | 411 | 23 states already incl. IDLE, RECOVER_BOOT, PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING, ROTATION_PENDING, PREPARE_ROTATION, VERIFY_HANDOFF, START_FRESH_SESSION, WAIT_FOR_OWNER, PAUSED_RECOVERY, USAGE_LIMIT_WAIT, SCHEDULED_RESUME, EMERGENCY_STOPPED, HALTED, COMPLETE; `Transition` table, `is_legal`, `BLOCKING_STATES`, `TERMINAL_STATES`, journaled `transition()` | prove the section-3 (R029) minimum-state set maps to these; add ONLY genuinely missing states/transitions with a cited requirement; renewable-epoch lease transitions |
| `durable_state.py` | 680 | `DurableJournal` (sqlite, integrity_check, transitions, before/after-effect records, idempotent set_state), per-checkout runtime dir OUTSIDE the repo, cloud-sync warning | epoch-lease renewal fields; exact-once succession records; crash-window before/after-effect reconciliation |
| `lease_runtime.py` | 163 | controller lease acquire/hold | renewable epoch lease; single-winner race resolution (R028/R030) |
| `recovery.py` | 579 | crash/restart recovery, recovery probes | watchdog-restart no-duplicate (R031); bounded read-only orientation while children drain |
| `turnover_controller.py` | 559 | model/session turnover seam | exact-once successor (R031 class 1); native resume is NEVER a seam substitute (R160) |
| `session_continuity.py` | 361 | session continuity/handoff bridge | smallest-complete handoff packet (R067); no silent truncation (§7) |
| `preflight.py` | 321 | Codex transport preflight | version-probed/structured/read-only/schema-validated/identity-bound/fail-closed (R024/R025); bounded-backoff durable retry vs blocked-with-handoff (R033) |
| `start_gate.py` | 406 | start-gate / activation checks | host-restart auto-resume via approved user-level mechanism OR truthful activation-blocker report (R032) |
| `handoff.py` | 260 | handoff packet assembly | section-7 safe-seam validation (atomic batches, known lease ownership, recorded checks, no unanswered permission, external effects confirmed/not-attempted/ambiguous-marked, children reconciled) |
| unit C `native_runtime.py`/`runtime_backend.py` | — | feature-detected native producer host; exactly one active backend (R180) | consume as the producer host; native session identity/naming (unit C); `--worktree` baseRef pinned head/explicit reset |
| unit D `event_bus.py` + recorders | — | durable hook/event feeds | seam-detection + completion signals feed from unit-D events (R155 carried) |
| unit E `goal_*` | — | bounded `/goal` inner continuation | per-assignment continuation; `/goal` is NOT a safe-seam substitute (R160 parallel) |

R018 duty: for each section-3 behavior, the producer must FIRST prove whether the existing module
already satisfies it (cite the code) and only add machinery for a genuine gap — documented in the
report with the citation. The M0-T091 carried advisory bundle (G5 L1–L5, G3 NIT-1/2, G4 ADV-1)
folds in HERE where those guards are touched.

## 1. Acceptance-scenario pack (recorded pre-implementation; section-16.3 matrix)

| ID | Scenario (Given / When / Then) | Kind | Key reqs |
|---|---|---|---|
| S1 section-3 state set | Given the accepted state machine, when the section-3 minimum set is mapped, then every required distinction (stopped/inactive; starting-reconciling; orienting; selecting/dispatching; producer-running; landing; awaiting-owner; paused; usage-limited; rotating; terminal) is present or added with a cited requirement; illegal transitions raise. | deterministic | R029 |
| S2 renewable epoch lease | Given one durable campaign identity, when epochs advance, then continuity is a renewable sequence of bounded epochs with ONE active controller lease at a time — never one immortal process; a lease renews or expires, never forks. | deterministic | R028 |
| S3 idempotent journaled transitions | Given any material transition, when journaled, then it is durable + idempotent; a replay/restart never creates two controllers, two successors, duplicate pushes, or duplicate PR comments. | deterministic | R030 |
| S4 stop-intent precedence survives restart | Given an owner graceful-stop or emergency-stop, when the controller restarts, then the stop intent SURVIVES and WINS over queued/recovered work (pause/resume/graceful/emergency precedence; emergency ≥ graceful ≥ pause ≥ queued). | deterministic | R027/R029 |
| S5 three interruption classes | Given model/session turnover vs controller-crash vs provider/host outage, when each occurs, then each is handled SEPARATELY: turnover→bounded handoff + exact-once successor; crash→watchdog/launcher restart with no duplicate; outage→explicit backoff/blocked. | deterministic | R031 |
| S6 safe-seam detection + handoff validation | Given a candidate seam, when validated (section 7), then ALL hold: atomic batches complete, lease ownership known, checks recorded, NO unanswered permission prompt, external effects each confirmed/not-attempted/ambiguous-marked, children reconciled, smallest-complete handoff packet assembled, NO silent truncation — else the seam is refused. | deterministic | R067/§7 |
| S7 exact-once rotation (lease race) | Given two candidate successors racing the lease, when they contend, then EXACTLY ONE wins; the loser dispatches nothing; the durable store shows one successor. | deterministic | R028/R030 |
| S8 controller-crash reconciliation | Given a crash at each labeled window (before/after a before-effect, before/after an after-effect, mid-transition), when the watchdog restarts, then state reconciles with no duplicate producer and no double external effect; bounded read-only orientation runs while children drain. | deterministic (crash-window matrix) | R030/R031 |
| S9 host-restart auto-resume | Given a host reboot, when the approved user-level startup mechanism is available, then the same one-command start resumes the EXACT campaign; when higher-precedence policy forbids host-start registration, the system REPORTS that truthfully as an activation blocker (never silently fails to resume). | deterministic + policy | R032 |
| S10 Codex transport preflight fail-closed | Given a Codex decision, when preflighted, then it is version-probed, structured, read-only, schema-validated, identity-bound; a missing/malformed/unparseable/timed-out/identity-mismatched decision dispatches NOTHING and accepts nothing. | deterministic | R024/R025 |
| S11 outage backoff vs blocked | Given a transient Codex/model/network/rate-limit failure, when it occurs, then bounded backoff with jitter + durable retry state (never a tight loop, never unlimited); an auth/billing/compatibility failure enters blocked-with-handoff (not backoff); no-eligible-authorized-work enters bounded idle. | deterministic | R033 |
| S12 Gate-0 recovery for a new session | Given a new/successor session, when it boots, then Bootstrap Gate 0 (cwd==worktree root, MCP-clean) is enforced BEFORE any write; failure → read-only diagnosis only, fresh session required. | deterministic | R125–R128 |
| S13 one-backend + native-resume-not-a-seam | Given the native runtime host, when a producer is hosted, then exactly ONE active backend (R180); native resume is used for continuation but is NEVER accepted as a safe-seam fresh-context turnover substitute (a large/confused conversation is not resumed merely because it is technically resumable). | deterministic | R160/R180 |
| S14 no worker-visible token pressure | Given any worker-facing assignment/handoff text the controller composes, when validated, then it carries NO token quota/countdown/%/conserve pressure (reuse `subagent_contracts.assert_worker_text_clean`, fail closed). | deterministic | R045 |
| S15 telemetry honesty carried | Given any usage number the controller records for a succession decision, when stored, then it carries a source/confidence label; missing is unknown, never zero. | deterministic | R042 |
| C1 live succession canary (OWNER-GATED) | Given the installed 2.1.247 runtime, when an owner-approved exact-command canary drives one real bounded rotation (producer launch → seam → successor), then exact-once succession and no-duplicate are proven end-to-end. | live canary (owner exact-command approval, R192/R197) | R183 |

## 2. Owner-gated item (flagged, not blocking the deterministic core)

Like units C–E, the LIVE succession canary (C1) needs an owner-approved exact launch command
(R192/R197). The deterministic section-16.3 matrix (S1–S15) is built and verified WITHOUT it; C1
strengthens the R183 required-proof evidence (real rotation, watchdog restart, no duplicate
producer) and is queued for owner approval.

## 3. Implementation guidance for the successor (not yet done)

- **Prove-first (R018):** for each of S1/S2/S5/S6/S8, first cite the existing module behavior; add
  code only for a proven gap; record the proof in this report §4 (to be populated).
- **Freeze duty:** every touch to `tools/agent_supervisor/**` cites D-024-R102 (or a more specific
  applicable R-id) in the commit; re-establish the `M0-T039-supervisor-freeze.md` suite baseline;
  guard packs (`readonly_agent_guard.py`, `agent_dispatch_guard.py`) are forbidden_paths — untouched.
- **Crash-window matrix (S8):** model the labeled windows against `durable_state` before/after-effect
  records; assert reconciliation determinism (the M0-T104 C2 no-duplicate model + unit-D restart-safe
  replay are the precedents).
- **Test file:** `tools/test_agent_supervisor_controller_succession.py` (section-16.3 matrix incl.
  Gate-0 recovery cases, crash windows, lease races, stop-intent persistence).
- **Modularity:** several target modules are already 400–680 lines; extend via focused new modules
  or cohesive additions with a recorded boundary justification (code-architecture rule) rather than
  growing a single file past the warn/justify thresholds.
- **DCV scale:** the applicable set is 65 requirements — the evidence map and verification.json rows
  will be large; assemble the evidence map incrementally per behavior cluster.

## 4. Evidence (populated during implementation — successor)

(pending — staging seam only; no implementation in this session per D-031 handoff)
