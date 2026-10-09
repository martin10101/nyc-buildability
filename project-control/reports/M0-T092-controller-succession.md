# M0-T092 — Unit F: controller state machine, safe seams, exact-once succession, outage handling (D-024 Phase D)

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R102** (Phase D; packet-named). Status: **IMPLEMENTED — awaiting gates.** The staging
session (under owner directive D-031) authored §0–§3 at a clean seam; the successor session
implemented from this frozen pack (§4 below carries the R018 proofs and evidence). Scope
amendment during implementation (orchestrator act, recorded in the task progress log):
`allowed_paths += tools/test_agent_supervisor_phase1.py` — its structural assertion
`len(STATES) == 23` is part of the frozen suite baseline and must move to 27 with the cited
R029 additive states; no other existing test hardcodes the count.

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

## 4. Evidence (implementation session)

### 4.1 R018 prove-first: the section-3 (R029) distinction map

R029 requires the state machine to distinguish 18 conditions. 14 map to the accepted D-007
machine unchanged; 4 had NO faithful representation and were added (additive only — no existing
state, trigger, or edge was changed; `BLOCKING_STATES` and `TERMINAL_STATES` are untouched):

| R029 distinction | Discriminator (cited code) |
|---|---|
| stopped/inactive | `IDLE` (existing) |
| starting-reconciling | `RECOVER_BOOT` (existing; `recovery.recover_boot` S11.5 algorithm) |
| orienting | `START_FRESH_SESSION` + READY gate (`turnover_seam.require_ready`); read-only orientation while children drain is `child_handoff.TurnoverCoordinator.successor_may_orient_read_only` + `epoch_lease.may_orient_read_only` |
| selecting/dispatching | `POLICY_CHECK` → `FORWARD_PROMPT` (existing) |
| producer running | `CLAUDE_RUNNING` (existing) |
| landing | `ROTATION_PENDING` (mid-unit flag state) + `PREPARE_ROTATION` (existing) |
| awaiting/reconciling child work | **`AWAIT_CHILDREN` (NEW)** — the drain window between `PREPARE_ROTATION` and rotation had no state; `TurnoverCoordinator` tracked children with nowhere for the machine to dwell |
| reviewing | `CODEX_REVIEW` + `VALIDATE_DECISION` (existing) |
| correcting | composite: `POLICY_CHECK`/`FORWARD_PROMPT` with the journaled `REVISE` decision (`codex_reviewer.REQUIRED_BY_DECISION["REVISE"]` → `next_claude_prompt`); the decision is journaled in the transition detail, so the machine + journal jointly distinguish a correction forward from an ordinary one |
| checkpointing | `CHECKPOINT_RECEIVED` + `COLLECT_EVIDENCE` (existing) |
| primary-session rotation | `PREPARE_ROTATION` → `VERIFY_HANDOFF` → `START_FRESH_SESSION` (existing) |
| temporary lower-model bridge | composite: `CLAUDE_RUNNING` + the durable orchestrator-role switch record (`loop.effective_model` reads the journal; the pinned-model return happens at the next seam via `loop_turnover`) — the bridge is a running mode with identical mechanics, distinguished durably, not a distinct dwell |
| paused | `PAUSED_RECOVERY` (existing, blocking) |
| graceful stopping | **`GRACEFUL_STOPPING` (NEW)** — no graceful-stop intent existed anywhere (only emergency + pause flags); paired with the durable `stop_intent.GRACEFUL_STOP_KEY` |
| emergency stopped | `EMERGENCY_STOPPED` (existing, blocking+terminal) |
| recovery/reconciliation | `RECOVER_BOOT` + `RECONCILE_EXTERNAL_EFFECT` (existing) |
| blocked | `WAIT_FOR_OWNER` / `HALTED` (existing, blocking) |
| idle-no-eligible-work | **`NO_ELIGIBLE_WORK` (NEW)** — the machine had no non-busy resting place short of `IDLE` (whose only exit is the operator's `start_command`); paired with the durable bounded-idle record (R028 no-busy-loop, R033 bounded idle) |

Fourth addition: **`CODEX_OUTAGE_BACKOFF` (NEW, R033)** — distinct from `USAGE_LIMIT_WAIT`
(which requires a provider-parseable reset deadline); a transport outage has no deadline, which
is exactly why R033 demands backoff-with-jitter and a durable retry state. 17 new documented
transitions; every new edge is walkable (S1 tests) and every new state has an exit.

### 4.2 R018 prove-first: reuse proofs per scenario (gap → extension)

| Scenario | Existing surface proven (cited) | Genuine gap → what was added |
|---|---|---|
| S2/S7 epoch lease | `locking.SingleInstanceLock` = process liveness only; `lease_runtime.LeaseLedger` = in-memory subagent write scopes; `campaign_continuity.advance` = stale-read detection, its docstring names the Phase-D controller lease as the missing cross-process exact-once | NEW `epoch_lease.py` (renewable epochs, single-winner CAS succession, boot reconciliation) + ONE additive `DurableJournal.compare_and_swap_state` (read+compare+write in one `BEGIN IMMEDIATE` txn) |
| S3 idempotent transitions | `state_machine.transition` idempotent-repeat no-op; `durable_state.record_transition` single-txn commit; `record_before_effect` refuses duplicate action ids | none — re-proven at the succession level (replayed succession refused) |
| S4 stop precedence | `recovery.set_emergency_stop`/`set_manual_pause` durable; `DurableFlags.blocking_reasons` beats autostart; `clear_emergency_stop` owner-only | NEW `stop_intent.py` (graceful intent + emergency>graceful>pause precedence + finish-current-unit semantics) |
| S5 interruption classes | turnover: `turnover_seam.SeamTurnover` full path; crash: `recovery.recover_boot` + `locking`; outage: nothing transient-specific | outage class → NEW `outage_policy.py`; crash/turnover reuse proven, lease layer added on top |
| S6 seam validation | `rotation.assert_safe_to_rotate` + `RotationSafetyState` (10 §7 conditions); `handoff.validate_handoff` (14-field R067 packet, refuses empties + `/clear` automation); `child_handoff.ChildHandoff` refuses transcript-sized payloads (no silent truncation) | additive `RotationSafetyState.children_unreconciled` + `UNSAFE_MOMENT_CHECKS` entry + `safety_state_from_run(unreconciled_children=…)` — the children-reconciled §7 condition had no seam input (R066) |
| S8 crash windows | `durable_state` before/after-effect records; `recovery.classify` AMBIGUOUS on pending effects; `integrity_check` rolled-back detection; `turnover_seam` U12 arm-gate-before-complete ordering | none — matrix tests prove each window incl. the lease-commit window |
| S9 host restart | `resume_scheduler.build_autostart_plan` / `verify_installed_definition` / `AutostartInstaller` (owner-gated); `runtime_backend.activation_limitations` truthful blockers (R032) | none — proven by tests (drifted installed definition reported, blockers name the one-command start) |
| S10 Codex preflight | `codex_reviewer.validate_decision` (strict shape, six decisions, identity binding to task+checkpoint), `no_decision_error` (missing/rejected classification), `protocol.CapabilityManifest.differences` (version drift named) | none — fail-closed proven by tests (R024/R025) |
| S11 outage | `codex_reviewer.provider_failure_reason` (bounded, redacted input string); `resume_scheduler` = usage-limit deadlines only; `circuit_breakers` = failure counting, no cause classes or retry schedule | NEW `outage_policy.py`: closed transient/blocking vocabulary (unknown → BLOCKING, fail closed), `BackoffPolicy` (bounded attempts, cap, injected rng jitter), durable `RETRY_KEY`, blocked-with-handoff record, bounded idle with `MAX_IDLE_SECONDS` ceiling, R033 permissions split |
| S12 Gate 0 | enforcement was procedural (campaign restriction text, handoff profile); `native_runtime.DispatchSpec` passes `--strict-mcp-config` to children only | NEW `bootstrap_gate.py`: deterministic R125–R128 evaluation (primary-cwd identity via `durable_state.canonical_checkout_path`, added-dir-not-equivalent, MCP unknown-fails-closed, R127 diagnosis payload, R128 adoption rule) |
| S13 one backend / resume | `runtime_backend.select_runtime_backend` (fail-closed to controller, R180/R153); `session_continuity.decide_continuity` (closed impossibility reasons; `CONTEXT_SHEDDING_REASONS` makes native resume structurally not-a-seam, R160) | none — proven by tests |
| S14 worker text | `subagent_contracts.assert_worker_text_clean` (R045) | none — asserted over the landing instruction and adversarial texts |
| S15 telemetry | `telemetry_records.Measurement` (source/confidence labels; missing = unknown never zero, R042) | `epoch_lease.succeed(usage=Measurement…)` — a succession decision stores its usage only as a labelled Measurement, or not at all |

### 4.3 Deliverables and test evidence

New modules: `tools/agent_supervisor/epoch_lease.py`, `stop_intent.py`, `outage_policy.py`,
`bootstrap_gate.py`. Additive edits: `state_machine.py` (+4 states, +17 transitions),
`durable_state.py` (+`compare_and_swap_state`), `rotation.py` (+`children_unreconciled`),
`turnover_seam.py` (+`unreconciled_children` param), `tools/test_agent_supervisor_phase1.py`
(state count 23→27 with citation). Guard packs (`readonly_agent_guard.py`,
`agent_dispatch_guard.py`) untouched; forbidden paths untouched.

Tests: `tools/test_agent_supervisor_controller_succession.py` — the §1 matrix S1–S15 as 15
test classes, **70/70 PASS** (stdlib unittest; injected clocks/rng; no network, no providers,
no sleeps). Full supervisor-freeze suite baseline re-established (see §4.4). Pre-existing,
untouched residual: `rotation.py:48` carries an unused `Sequence` import that predates this
unit (confirmed via stash at the staged HEAD); left alone as out of cited scope.

### 4.4 Suite baseline + mutation evidence

**Full-suite baseline (composed; the change-graph makes it complete):** the full
`python -m pytest tools/ -q` run at tree T1 — which already contained every unit-F production
change — finished **2911 passed / 3 failed / 3 skipped in 32:11**, the 3 failures being
exactly the three live drift teeth (below). The T1→T2 delta is the drift re-capture only
(`event_drift.py` pointer, three test files, three new fixture files — no production logic);
its complete consumer set (verified by repository-wide grep: the three test files themselves;
`telemetry_core` pins the historical 2026-08-25 fixture) re-ran at T2: **195/195 PASS**, plus
the matrix **70/70 PASS**. Two additional full-suite background runs were externally stopped
before completing (recorded, not hidden); CI on the pushed branch supplies the independent
whole-suite confirmation at the frozen identity.

Mutation testing: **13/13 mutants KILLED** by the matrix, baseline re-established PASS after
every restore (`__pycache__` cleared around each run). Mutants: live-takeover allowed;
succession ignores a lost CAS; CAS always wins; precedence swapped; non-owner clears graceful
stop; unlimited retry attempts; backoff cap dropped; unknown cause fails open; idle bound
dropped; unknown MCP passes Gate 0; added-dir treated equivalent; every transition legal;
children-reconciled seam check dropped. Full-suite counts recorded below at submit.

M0-T091 carried advisory bundle (G5 L1–L5, G3 NIT-1/2, G4 ADV-1): folds in "where those guards
are touched" — this unit touched neither guard pack (`readonly_agent_guard.py`,
`agent_dispatch_guard.py` are forbidden paths and untouched), so the bundle does not activate
here; it remains carried on the M0-T109 guard-hardening backlog.

Owner-gated C1 succession canary: NOT executed (R192/R197 exact-command approval required);
the deterministic core above is built and verified without it (§2).

**Consolidated correction round (post round-1 gates; all three gates were PASS with LOW
findings, fixes applied by orchestrator election, per the M0-T104/T105/T106 pattern):**
- **F1 (G3 LOW-1 / G5 LOW-1, convergent):** `outage_policy` reason-text classification now
  scans BLOCKING keywords FIRST — a blocking token anywhere outranks every transient token,
  so mixed strings like "authentication failed: connection reset" classify BLOCKING and
  never enter the retry loop (R033's letter). Collision tests added (5 phrasings).
- **F2 (G3 LOW-2):** `epoch_lease.may_dispatch_writes` makes `external_effects_reconciled`
  keyword-REQUIRED (no default), matching the mirrored
  `child_handoff.successor_may_dispatch_writes` contract; omission is now a `TypeError`.
- **F3 (G4 LOW-1/2/3):** matrix additions — `expired()` boundary pinned (the renew-by
  instant is still owned; strictly-after expires), double-`release()` idempotency, and
  full `may_dispatch_writes` reconciliation gating (children / effects / required-arg).
- **F4 (G4 ADVISORY-3):** `acquire_first` refusal on a released record now directly tested
  (epoch 1 at most once; later epochs only through `succeed`).
Matrix after the round: **75/75 PASS**; two new targeted mutants (blocking-first order
reverted; effects check dropped) both KILLED — **15/15 mutants total**.
Residuals carried (non-blocking, recorded): G5 ADVISORY-2 (journal reason-string
re-redaction boundary note) and ADVISORY-3 (diagnosis terminal-escaping note) — both
live-wiring-time hardening for the R595 activation path; G3 ADVISORY-1 (succession-log
append non-atomic; authoritative records unaffected — accepted design); G3/G4 ADVISORY-2
(composed suite baseline; CI at the frozen identity is the whole-suite confirmation);
G4 ADVISORY-1 (the two R029 composite distinctions are documentation-backed; hard-testing
the REVISE/bridge journal reads belongs to the loop-wiring units).

**Provider CLI drift increment (qualifying evidence: reproduced drift, supervisor-freeze §2;
R149/R102).** The installed Claude CLI auto-updated **2.1.247 → 2.1.248** during unit F's
verification, firing all three live drift teeth exactly as designed (capability-probe reprobe,
event-bus catalog tooth, native-adapter detection tooth): first full-suite run **3 failed /
2911 passed / 3 skipped**, all three failures being the teeth. Re-captures per each tooth's
own prescribed remedy: capability probe re-run (every probed flag/verb classification
IDENTICAL to 2.1.247; only the version string and help-text hash changed; `[HOME]`-masked,
leak-checked); native detection re-run (`build_detection_fixture` diff = `claude_version` +
`task` fields only; `background_host_ready` still true); hooks docs re-fetched from
code.claude.com/docs/en/hooks (31-event set verified identical name-for-name). New fixtures
`capability_probe_live_2026-08-27_m0t092_2_1_248.json`,
`native_runtime_detection_2026-08-27_m0t092.json`, `hook_event_catalog_2_1_248.json`; the
2.1.247 fixtures stay committed as history; `event_drift.CATALOG_FIXTURE_PATH` and the three
test files' current-fixture pointers/shape assertions moved forward (scope amendment 2,
recorded in the progress log). The three affected files + matrix + phase1 re-ran 265/265 PASS.

## 5. Producer evidence map — all 65 applicable requirements (input to the independent DCV)

Producer: fable-orchestrator-session. The independent verifier re-derives each row against the
frozen deliverable SHA; this map is a claim, never proof. Test ids refer to
`tools/test_agent_supervisor_controller_succession.py` (matrix classes S1–S15).

**Core Phase-D machinery (new/extended this unit)**

| Req | Evidence |
|---|---|
| R028 | `epoch_lease.py`: one durable lease key (`LEASE_KEY`), renewable bounded epochs (`renew` extends by ttl; `expired`; ttl>0 enforced), exact-once succession (`succeed` CAS), no-fork (`acquire_first` refuses when any record exists; `renew` refuses non-owner/expired). Tests S2 (5), S7 (3). |
| R029 | 18-distinction map in §4.1; 4 additive states + 17 documented transitions in `state_machine.py`; illegal transitions raise. Tests S1 (5); `test_agent_supervisor_phase1.py` count updated 23→27 with citation. |
| R030 | `state_machine.transition` idempotent + single-txn journal (existing, proven); `DurableJournal.compare_and_swap_state` (new, one `BEGIN IMMEDIATE` txn); replayed succession refused; duplicate action ids refused. Tests S3 (4), S7 (`test_a_lost_cas_is_a_typed_refusal…`, `test_the_cas_primitive…`). |
| R031 | Three classes separately: turnover (`turnover_seam.SeamTurnover` + `epoch_lease.succeed`), crash (`recovery.recover_boot` + `epoch_lease.reconcile_on_boot` same-epoch resume), outage (`outage_policy`); distinct durable keys proven. Tests S5 (5). Bounded read-only orientation: `may_orient_read_only` always-true + `may_dispatch_writes` gating. |
| R032 | `resume_scheduler.build_autostart_plan`/`verify_installed_definition` (existing; drift reported, never accepted) + `runtime_backend.activation_limitations` truthful blockers naming the one-command start. Tests S9 (3). |
| R033 | `outage_policy.py`: closed transient/blocking vocabulary (unknown→BLOCKING), `BackoffPolicy` (bounded attempts, cap, injected-rng jitter), durable `RETRY_KEY`, `record_blocked_with_handoff`, `begin_bounded_idle` + `MAX_IDLE_SECONDS`, `permissions_during` (land-current yes / dispatch-new never). New states `CODEX_OUTAGE_BACKOFF`/`NO_ELIGIBLE_WORK` + edges. Tests S11 (8). |
| R026 | Durable flags beat queued/recovered work: existing emergency/pause (`recovery`) + new graceful (`stop_intent`); `wins_over_queued_work` true for every intent; owner-only clears. Tests S4 (6). |
| R027 | Precedence emergency>graceful>pause (`effective_intent`); start needs no duration — continuation ends only at completion/no-eligible-work (`NO_ELIGIBLE_WORK`)/stop/block. Tests S4, S1, S11. |
| R036 | Start idempotency existing (`locking.SingleInstanceLock`, loop start reporting); stops durable before acknowledgment: `set_graceful_stop`/`set_emergency_stop` write the journal (transactional) before returning. Tests S4 (survives reopen). |
| R066 | `rotation.UNSAFE_MOMENT_CHECKS` (10 existing §7 conditions) + new `children_unreconciled` condition + `turnover_seam.safety_state_from_run(unreconciled_children=…)`. Tests S6 (each condition refuses; every reason named). |
| R067 | `handoff.HANDOFF_FIELDS` 14-field smallest-complete packet, empties refused, `/clear` automation refused, `STRUCTURAL_FORBIDDEN_SCOPE` always carried (existing, proven); `child_handoff` bounds summaries (no silent truncation). Tests S6 (3). |
| R125–R128 | `bootstrap_gate.py`: primary-cwd identity via `canonical_checkout_path`; added-dir never equivalent (R125); MCP enumeration unknown fails closed, allowlist-exact (R126); R127 diagnosis payload (launch dir, intended root, dirty paths, posture) + `assert_may_write`; R128 `adoption_of_uncommitted` (fresh pass required; never rewrite history). Tests S12 (6). |
| R109 | The full 16.3 matrix: `tools/test_agent_supervisor_controller_succession.py`, 15 scenario classes, incl. Gate-0 recovery cases, crash windows (S8: pending-effect, verified-effect, rolled-back journal, gate-armed/rotation-incomplete, lease-commit), lease races, stop-intent persistence. |
| R102 | The whole unit (this report §4); packet + commits cite D-024-R102. |

**Preflight / supervisor transport (proven reuse)**

| Req | Evidence |
|---|---|
| R024 | `codex_reviewer.validate_decision` strict shape (unknown fields rejected, six decisions, per-decision required fields, identity binding), `build_argv` forbidden-flag refusal, `protocol.CapabilityManifest.differences` version drift named, `capability_probe` version probing (all existing, proven). Tests S10 (4). |
| R025 | Missing/malformed/mismatched decisions raise `ReviewError` and dispatch nothing (`no_decision_error` classification). Tests S10. |
| R021/R022/R023 | Codex boundary unchanged by this unit: read-only reviewer argv + `FORBIDDEN_REVIEWER_FLAGS` (mechanical), no mutation path added; decision validation is the enforcement seam (S10). Diff shows no reviewer-authority change. |

**Roles / authority / campaign rules (satisfied at this unit's boundary)**

| Req | Evidence |
|---|---|
| R002 | This unit's share: fail-closed transport handling (S10), outage handling (S11), controller+host restart recovery (S5/S8/S9). The two-unit golden run is owed by M0-T096, not claimed here. |
| R003/R004/R140 | Producer/supervisor roles preserved: unit F adds controller-side modules only; Fable remains producer; Codex path read-only; ledger/git remain authority (`campaign_continuity` docstring: orientation, not authority). |
| R007 | Successor implemented this unit from durable state alone (frozen pack §0–§3 + ledger + campaign record); no owner re-prompt of the directive occurred. |
| R008 | Zero routine owner questions during implementation; the one owner-gated item (C1 canary) is queued, not asked mid-build. |
| R010 | No PR merged; PR #241 untouched; restriction carried in the campaign record. |
| R017 | Task packet names D-024-R102; deliverable commit message cites D-024-R102. |
| R018 | §4.1/§4.2 prove-first tables with code citations; conflicts: none found (no older implementation contradicts the directive; the pre-existing `rotation.py` unused import predates the unit and is recorded, not hidden). |
| R020 | Producer work stayed inside allowed_paths (scope amendment recorded in the progress log before the phase1 edit); commits/pushes by the orchestrator under Tier A. |
| R139 | Hold discharged before claim: capture+verification+conversion complete (M0-T102 accepted; campaign seq-10 conversion); T092 claimed only after T103–T106 all accepted (ledger). |
| R145/R146 | Within the amendment's authorization (surgical change to an unstarted task; no binary update); prohibitions honored: no activation, no SDK, no new MCP (Gate-0 module ENFORCES MCP-clean), no merges, no model substitution, no bypass flags, no unbounded fan-out (every loop bounded), ledger intact. |
| R143/R164/R166 | Native reuse without duplication: consumes unit-C backend selection (S13), unit-D event feeds (unchanged), unit-E /goal (unchanged); custom control preserved for the R164 list (sequencing, exact-once effects, seams, leases); no native feature adopted as campaign authority. |
| R149 | Deterministic core uses no new installed-CLI feature; the live-canary duty (C1) is owner-gated and queued; existing 2.1.247 fixtures untouched. |
| R181 | Nothing deleted; the diff is additive (`git diff --stat`: 4 modified files, insertions only + 5 new files). |
| R188 | One writer task (M0-T092) at a time; campaign record advanced at accept; fresh producer context (this successor session); reviewers run at the frozen identity. |

**Landing / sizing / health (proven reuse + unit-F integration)**

| Req | Evidence |
|---|---|
| R046 | Existing `rotation.decide_pre_dispatch` + `SessionSignals` (context, checkpoints, compactions, adherence) reused, not duplicated (§4.2); unit F adds no competing continuation heuristic. |
| R050 | Existing private health bands (`rotation.observe_mid_unit`, `runtime_health`) untouched; the one landing instruction is `child_handoff.land_child` (returned once, then None). |
| R051 | No maxTurns/maxBudget cap added anywhere in the new modules; bounds are controller-side (attempts, ttl, idle) and never worker-visible. |
| R053 | `session_continuity.CONTEXT_SHEDDING_REASONS` includes `instruction_adherence_loss` (immediate quality signal) and `rotation.rotation_pending` lets a nearly-complete unit reach its seam (existing, cited §4.1 "landing"). |
| R054 | Landing = finish only what is underway: `GRACEFUL_STOPPING` doc + `stop_intent.may_finish_current_unit` (graceful only) + `child_handoff.register_child` refuses new children once landing. Tests S4/S6. |
| R060 | `lease_runtime.LeaseLedger` + `assert_grantable` (existing) keep producer caps/overlap refusal; epoch lease adds the controller-level single-writer above it (S7). |
| R064 | Progress = durable evidence: journaled transitions, before/after effects, succession log entries, retry/idle records — all asserted durable across reopen (S3/S5/S11). |
| R065 | `child_handoff.TurnoverCoordinator` (existing: healthy children finish, one landing instruction, durable handoffs) + new `AWAIT_CHILDREN` dwell + `epoch_lease.may_dispatch_writes` (no conflicting write lease while draining). Tests S5/S6. |
| R098 | Session ≠ task ≠ assignment: `decide_continuity` resumes a healthy same-model session (S13 resume case) and rotates on shedding reasons; no per-task forced fresh session added. |
| R120 | Bounded rules structural: ttl>0, max_attempts required, MAX_IDLE_SECONDS ceiling, SUCCESSION_LOG_BOUND — no unlimited mode exists to enable. |
| R160 | Native resume never a seam substitute: `CONTEXT_SHEDDING_REASONS` forces reorientation on shedding rotations even when resume is verified. Test S13 (3). |
| R175 | Unit-F behavior set: children finish (`child_may_continue` healthy), stale work quarantined (`land_child` once + unhealthy refusal + `PAUSED_RECOVERY` edges), accepted evidence committed/pushed (orchestrator commits, this deliverable), bounded replacement handoff (R067 packet + reorientation prompt), genuinely fresh session (`START_FRESH_SESSION` + Gate-0 module), no duplicate recovery (S8). |
| R180 | Replace-not-layer: every new module fills a §4.2-proven gap; no parallel duplicate left beside an existing implementation; one active backend proven (S13). |

**Telemetry / worker protection / status**

| Req | Evidence |
|---|---|
| R042 | `epoch_lease.succeed(usage=Measurement…)`: succession usage stored only as a labelled `telemetry_records.Measurement`; no usage → no invented number. Tests S15 (3). |
| R045 | No numeric quota/countdown in any worker-facing text this unit composes; `assert_worker_text_clean` proven over the landing instruction + adversarial texts. Tests S14 (2). |
| R093 | Review packets remain independently reconstructed (`review_packet`/`evidence` untouched); this unit's own gates run against the frozen SHA, not the producer summary. |
| R094 | The bounded durable status record answers without waking Fable: campaign id/state (`campaign_continuity`), stop flags (`stop_intent`/`recovery` keys), lease owner+expiry+epoch (`LEASE_KEY`), retry/idle holds (`RETRY_KEY`/`IDLE_KEY`), succession history (`SUCCESSION_LOG_KEY`). |
| R096 | Notification-sink boundary untouched (`notifications.py`); new events go to the hash-chained audit log (terminal/on-demand); no email configured. |
| R079/R080 | No graph-subsystem edit in the diff; the graph remains an advisory index; nothing here consumes stale graph data (module inputs are the journal + injected facts). |

**Required-proof clusters**

| Req | Evidence |
|---|---|
| R182 | Deterministic fixtures, injected clocks (accelerated counters), simulated failures (fake journals/rng), no live-provider token burn; 13 targeted mutants all killed. |
| R183 | Deterministic share: restart-no-duplicate-producer (S5/S8), MCP default-deny evaluation (S12), worktree/identity checks unchanged; live-platform share carried by accepted unit C/D/E fixtures + the queued owner-gated C1 canary (§2). |
| R184 | No worker quotas (S14); overlapping-scope rejection (existing `assert_grantable` + S7 single-writer); rotation at a safe seam (S6); handoff boundedness + successor reconstruction from durable state alone (S5/S8: reconcile_on_boot + armed-gate survival); refusal vs quota distinct (outage causes vs `resume_scheduler` usage-limit domain, disjoint keys). |
| R185 | Effects exactly-once (S3 duplicate action-id, S8 pending/verified windows); crash between commit and push = the before/after-effect matrix (S8); stale ledger/handoff reconciliation (`campaign_continuity.staleness` + recovery UNSAFE on drift); project suite green (§4.4); independent G3/G4/G5 + DCV at the frozen identity (gate records); mutation demonstration (§4.4). |
