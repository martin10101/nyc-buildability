# M0-T125 — Ten-class defect register (D-024-R384)

Analyzed identity: HEAD 13cd5973. Every claim carries a citation; live claims cite the preserved
audit chain (seq N), the preserved worker transcript, or a committed report. "In-scope" = on the
Amendment-22 journey seams (R372/R373). Severity: what it does to the COMPLETE journey.

## D1 — Presented commands are not derived from the live arg/seam contract (class 10 + 2) — HIGH, IN-SCOPE
Evidence: M0-T124 §4 item-2 start (no `--worktree`) refused live pre-dispatch, exit 11
`cwd_primary_checkout` (M0-T107-amendment20-start-refusal.md §1; §3 states no test covers the CLI
presentation surface); M0-T124 §5 correction admits "certification packages must re-derive the
presented start command from the live `start` arg contract". Systemic sweep (file 1 §C.2): the
CORRECTED §5 command still carries five silent defaults — no `--checkout` (journal addressed by
invocation cwd, cli.py:3175; a different cwd silently creates/addresses a different runtime and
run id), no `--repo` (D2), no `--branch` (branch probe unpinned, recovery_probes.py:142-165), no
`--stage` (falls back to packet.status), no `--max-cycles` (single-cycle, feeds D10).
Correction (M0-T126): a command-document validation tooth — extract every `!`-prefixed command
from certification docs + runbook, dry-run it against `build_parser()`, `dispatch_inputs_missing`,
and `evaluate_packet_worktree_binding` with the named packet; fail CI on any drift; pin
`--checkout`, `--repo`, `--branch`, `--worktree`, `--max-cycles` explicitly in presented commands.
Test implication: removal-sensitive — deleting `--worktree` (or the tooth) from a presented
command must fail a test (the R387 "command-document validation" scenario).

## D2 — `--repo` defaults to the primary checkout: evidence + review bound to the wrong tree (class 4) — HIGH, IN-SCOPE
Evidence: `repo = pathlib.Path(args.repo or checkout).resolve()` (cli.py:2642);
`EvidenceCollector(repo_root=str(repo))` (cli.py:2705); `CodexReviewer(..., repo=str(repo))`
(cli.py:2700-2701); `production_task_authority(..., repo_root=str(repo))` (cli.py:2661-2663). The
certified §5 command names no `--repo`, so on the next journey with a valid checkpoint the git
facts in the evidence packet and the reviewer's `-C <repo>` working tree are the ORCHESTRATOR'S
PRIMARY CONTROL CHECKOUT (ctl24), not the task worktree/repo the checkpoint describes; the
reviewer's verified_repo_head correlation is then against the wrong tree. (The worker cwd itself
is correctly seam-bound — this is the evidence/review half of the cycle-2 leakage class.)
Correction: derive repo from the packet (or from `--worktree`'s repository) and REFUSE when
repo == primary_checkout while the packet declares an isolated worktree — the same fail-closed
pattern as `evaluate_packet_worktree_binding`; plus D1's command pinning.
Test implication: adversarial start with packet-declared worktree and no --repo must refuse (or
provably bind evidence/review to the worktree's repo); replay fixture from the preserved packet.

## D3 — Fixed 12-turn unit bound, no checkpoint reservation, sizing machinery unwired (class 6 + 1) — HIGH, IN-SCOPE (seed b VERIFIED)
Evidence: `max_turns: int = 12` (claude_runner.py:306), `--max-turns` default 12 (cli.py:3256);
live counted stop at exactly 12/12 turns — 36 assistant events ALL `stop_reason: tool_use`,
tools Glob/Grep/Read only, 2m24s, no checkpoint JSON anywhere (preserved transcript; audit seq
50-53); first prompt = 2,176 chars total: the one-line default `--prompt` + the S8.3 contract —
NO task/lineage/worktree/progress orientation (transcript first user event; cli.py:3251). The
same terminal class occurred twice before (audit seq 8, 40). Nothing reserves a final turn,
requires an early checkpoint, or sizes turns: `workload_sizing.py` (smallest-complete packet
planner, M0-T090) has ZERO consumers in the package (grep: only workload_classifier is imported,
by refusal_bridge/spawn_decision/startup_overhead/subagent_contracts). Full fixed-bound map with
exhaustion behavior: file 1 §C.5.
Correction: implement Amendment-22 items 1-5 — front-loaded orientation packet in the FIRST
prompt (packet task_id/objective/worktree/branch/allowed_paths/documented commands/exact required
output — build_forwarded_prompt already proves the shape for later cycles,
codex_reviewer.py:663-700); early + incremental checkpoint contract; a reserved emission turn
(inject a final "emit the checkpoint NOW" user turn at max_turns-1 via the extra-turns/stdin
channel, claude_runner.py:1316); class-based turn allowance under a documented hard ceiling
(wire workload_classifier/sizing), never merely a raised constant.
Test implication: replay fixture of the preserved 12/12 transcript must fail the old design and
pass the new (turn-exhaustion converts to an honest incomplete-but-resumable checkpoint, R379).

## D4 — `native_tools_guidance_appended` is degenerate; the committed report mis-attributes it (class 7 + 3) — MEDIUM, IN-SCOPE (seed c REFUTED as stated)
Evidence: the flag is computed AFTER `with_checkpoint_contract` (claude_runner.py:1199-1206), and
the contract TEXT already embeds the folded guidance (931), so on every fresh prompt the flag is
False while the guidance IS present. Primary proof: the preserved transcript's first user prompt
contains BOTH sentinels ("CHECKPOINT CONTRACT (S8.3)" and "NATIVE-TOOL PREFERENCE
(D-024-R294)"), yet audit seq 50 records `native_tools_guidance_appended: false`. Therefore
M0-T107-amendment20-live-journey-2.md §2(a)'s explanation ("the digest-bound prompt predates
M0-T120 on this RESUMED run lineage") is WRONG: the dispatched prompt was the default `--prompt`
with the current folded contract appended at dispatch (`checkpoint_contract_appended: true`), not
a pre-T120 digest-bound body. The worker "nevertheless routed natively" because the guidance was
delivered.
Correction: record guidance PRESENCE (sentinel-in-final-prompt) in the audit detail (or rename
the field); append-only corrective note on the journey-2 report.
Test implication: assert the audit field equals presence-of-sentinel on the dispatched bytes for
fresh, old-contract, and pre-seeded prompts (three shapes).

## D5 — `context_tokens` records cumulative usage, consumed as live context by the 400k ceiling (class 7) — HIGH, IN-SCOPE (seed d VERIFIED)
Evidence: `inspect_stream` takes the PEAK per-event sum of every `*token*` field
(claude_runner.py:670-722); the CLI's terminal `result` usage is cumulative across turns, so the
recorded peak is cumulative: audit seq 50 records 694,251 while the transcript's final live
usage is ~72.5k (67,935 cache_read + 3,962 cache_creation + 647 output). Consumers making
THRESHOLD decisions against it: (1) `_flag_rotation_if_needed` sets rotation_pending at >=
threshold (loop.py:946-953) — fired at 604,772 (seq 24); (2) `_rotate_over_ceiling_before_first_
dispatch` (loop.py:997-1011); (3) `launch_seam.evaluate_ceiling` on every resume
(launch_seam.py:269-302, fed by `with_resume`/`actuate_resume`, claude_runner.py:1163-1172,
loop_turnover.py:156-173); (4) the durable continuity record (session_continuity.py:120-128,
loop.py:1598-1608). Consequence: any unit of roughly >=7 tool-turns exceeds 400k cumulative at
~60k live context, so continued multi-unit operation forces a context-shedding reorientation
after nearly EVERY unit (session continuity permanently defeated), while a genuinely full live
context is not separately measurable. The cycle-2 numbers (604,772 / 640,224) carry the same
semantics; the code's own docstring admits "policy signal (cumulative processed tokens)"
(claude_runner.py:670-676) but the ceiling prose says "live context".
Correction: compute a live-context estimate (max over per-turn events of input+cache_read+
cache_creation+output, EXCLUDING the cumulative terminal result event — the transcript proves
per-turn events carry it) as the ceiling input; keep cumulative as a separate recorded field.
Test implication: replay fixture built from the preserved transcript asserting live ~72k vs
cumulative ~694k are recorded separately and the ceiling consumes the live figure; adversarial
case at exactly 400,000.

## D6 — Unit journaled post-hoc: journal rests at START_CLAUDE for the whole unit; audit order inverted (class 8 + 9) — MEDIUM, IN-SCOPE (seed e VERIFIED)
Evidence: `claude_process_started` commits only AFTER `run_unit` returns (loop.py:1620-1625)
while `_audit_run` appends `claude_unit_completed` at the end of run_unit
(claude_runner.py:1479, 1600-1629) — live seq 8/9, 21/22, 40/41, 50/51 (completed before
started, started's timestamp after completion). Consumer assessment: `verify_chain` validates
sequence/prev_digest only (audit_log.py:1-30) — chain intact; `verify_approved_digest_against_
audit` scans by event type — unaffected; no machine consumer depends on cross-event order; risk
is human/verifier misreading PLUS the real hazard: the DURABLE state is START_CLAUDE during the
entire unit, so a supervisor crash mid-unit re-enters at START_CLAUDE (loop.py:156-181, B-018)
and dispatches AGAIN. Protection is child accounting + job object: a child that died WITH the
crash leaves a record that probes determined-dead (recovery.py:161-178) => NOT unaccounted =>
SAFE_CHECKPOINT => re-dispatch of a unit whose provider calls (and any brokered AUTO-tier
effects) already ran once.
Correction: commit the CLAUDE_RUNNING transition at launch (runner launch callback before the
first stdin write), or journal a dispatch-intent record that recovery treats as
AMBIGUOUS_EFFECT until reconciled.
Test implication: crash-injection replays immediately after Popen, after partial stream, and
after checkpoint-in-stream-but-before-extract (three of the R387 interruption scenarios).

## D7 — Recovery classification ignores the per-launch enable; `safe_auto_resume` is dead code (class 9 + 1) — LOW (presentation) / documented-hold (structure), IN-SCOPE (seed f VERIFIED)
Evidence: `classify` reads only the DURABLE `limited_auto_enabled` flag (recovery.py:349-357);
that key has ONLY False-writers (broker.py:702; remote_approvals.py:293, 306), so the
`safe_auto_resume` branch (recovery.py:358-362, resume_permitted=True) is unreachable — correct
under the R595 hold (autostart must never self-resume) but undocumented as dead code. The
`cmd_start` epilogue always prints the classification block (cli.py:3097-3101), so an
owner-typed start CARRYING `--owner-enable-bounded-auto` still prints "resume permitted: False …
limited-auto was NOT already owner-enabled … waits for an explicit operator start" and then
dispatches (proven: start-refusal report §1; audit seq 46-49). The flag is consumed correctly by
the GATE (LoopConfig/bounded_mode_gate); only the classification/report channel misleads.
Correction: when the invocation itself is the explicit operator start, annotate the block ("this
start IS the explicit operator start; the per-launch enable is honored by the mode gate, not by
recovery") or suppress `resume permitted` on operator-typed starts; mark `safe_auto_resume`
explicitly R595-gated in recovery.py.
Test implication: golden assertion on the start epilogue for an enabled dispatching launch.

## D8 — PREPARE_ROTATION strands the journal on a legal Codex ROTATE_SESSION verdict (class 1 + 9) — HIGH, IN-SCOPE
Evidence: entered at loop.py:2035 and the run stops ("rotate_session"); NO caller exists for any
exit (`handoff_generated`, `children_still_draining`, `unsafe_rotation_point` — trigger sweep,
file 1 §B rows 44-45); PREPARE_ROTATION is not in CYCLE_ENTRY_STATES (loop.py:181) so the next
start raises `bad_cycle_entry_state`; no operator surface covers it (clear-recovery requires
PAUSED_RECOVERY, cli.py:1868; restart_channel covers HALTED/EMERGENCY_STOPPED/WAIT_FOR_OWNER
only). ROTATE_SESSION is one of the six schema-legal decisions (models.py:189-191,
codex_reviewer.py:139), so one reviewer verdict permanently strands the campaign journal.
Correction: route the verdict through the EXISTING seam machinery (set rotation_pending +
reason, close the cycle into PREFLIGHT via `cycle_closed`, let the next dispatch rotate at the
proven seam), or add an operator exit surface; do not build the dead PREPARE_ROTATION/
VERIFY_HANDOFF/START_FRESH_SESSION chain live.
Test implication: adversarial replay — Codex returns ROTATE_SESSION, next start must dispatch (a
removal-sensitive test on whichever exit is chosen).

## D9 — COMPLETE strands; next-task selection does not exist (class 1) — HIGH, IN-SCOPE
Evidence: `decision_complete` enters COMPLETE (loop.py:2041); `run_closed` (COMPLETE->IDLE) has
ZERO callers (trigger sweep); COMPLETE not in CYCLE_ENTRY_STATES => every later start on this
checkout refuses `bad_cycle_entry_state`. There is NO next-task/unit selection surface anywhere:
`start` binds exactly one `--task-packet`; nothing walks the ledger for the next bounded task
(the NO_ELIGIBLE_WORK family, rows 77-80, is likewise caller-less). The R373 journey tail
("exactly-once task advancement, next-task selection, continued multi-unit operation") is
unimplemented beyond a single packet's cycles.
Correction: an audited close-run surface or an automatic `run_closed` on the next start after
COMPLETE (mirroring owner-restart's discipline), plus an explicit next-packet selection step
(owner-supplied ordered packet list, or ledger query) feeding a fresh start_command — with
exactly-once advancement recorded per task.
Test implication: the R388 consecutive-simulated-advancements scenario is IMPOSSIBLE to satisfy
until this exists; simulate task A COMPLETE -> select+dispatch task B -> assert exactly-once and
no duplicate advancement across a crash at the boundary.

## D10 — Forwarded CONTINUE prompt lost across process boundaries; duplicate-id collision on re-decision (class 5 + 8) — HIGH, IN-SCOPE
Evidence: within a run, the next unit's prompt is `result.forward.sent_prompt`
(loop.py:2685-2691). A run that ends at CLAUDE_RUNNING (certified shape: `--max-cycles` default
1 => `max_cycles_reached` after a successful forward, loop.py:2737-2738) leaves the reviewed
prompt marked SENT in the outbox — but the next start calls `loop.run(args.prompt)` (cli.py:2864)
and `run()` has NO branch for CLAUDE_RUNNING entry that reads the sent row back (only
FORWARD_PROMPT is resumed, loop.py:2628; the only outbox readers are loop.py:2401
`unsent_outbound` and a status count, grep-verified). The next unit therefore receives the
generic default `--prompt`, and the Codex-directed instruction is never delivered. Second facet:
cycle indices reset to 1 each start (loop.py:2604), so a re-decision producing the SAME
instruction mints the SAME message id (loop.py:2317-2327) => `duplicate_suppressed` =>
`forward_suppressed` stop (loop.py:2411-2413, 2677-2679) — cross-run identity collides with
within-run exactly-once.
Correction: on CLAUDE_RUNNING entry with a sent-but-unconsumed outbox row for this run, resume
THAT row's bytes as the first prompt (exact mirror of the approved-forward resume); persist a
durable next-unit-prompt pointer consumed exactly once; include the advancing cycle number from
the journal, not a per-process counter.
Test implication: cross-process scenario — cycle 1 forwards, process exits (max_cycles), fresh
start must dispatch the forwarded bytes (removal-sensitive on the resume branch), and a
duplicate re-decision must not dead-end the run.

## D11 — In-flight run never consults durable stop/pause flags between cycles (class 9) — MEDIUM, IN-SCOPE
Evidence: between-cycle gates are budget + rotation only (loop.py:2654-2703); EMERGENCY_STOP_KEY
is read inside the loop only by `_resume_approved_forward` (loop.py:2485); DurableFlags are read
at start/recovery/CLI surfaces only. An owner setting `stop`/`pause`/`emergency-stop` from a
second terminal while a multi-cycle limited-auto run executes does not stop the run until its
own bounds end (the flags gate the NEXT start).
Correction: read `stop_intent.effective_intent` + EMERGENCY_STOP_KEY at the between-cycle seam
(same place as `_budget_stop`) and stop synchronously with the intent's precedence.
Test implication: simulated advancement with the flag set between cycles must stop before the
next provider dispatch (one of the R387 interruption scenarios).

## D12 — `graceful-stop` records an intent nothing consumes (class 1 + 9) — MEDIUM, IN-SCOPE
Evidence: the verb writes GRACEFUL_STOP_KEY (operator_channel_cli.py:33,64-95;
stop_intent.py:87); the ONLY reader is the status display (operator_status.py:134-139); it is
absent from DurableFlags/autostart_permitted (recovery.py:102-132) and from the loop; the
GRACEFUL_STOPPING edges (state_machine.py:294-306) have no callers. A graceful stop therefore
neither lands the current unit-then-stops nor blocks the next start.
Correction: fold into D11's between-cycle intent check (graceful => finish the in-flight unit,
land its checkpoint, do not dispatch the next) and into the recovery blocking-reasons read.
Test implication: graceful-stop set mid-run => current unit completes, next dispatch refused
with the graceful reason; graceful-stop set at rest => next start refuses until cleared.

## D13 — Durable run-budget starts (and recovery classifies SAFE) before the blocking-state gate (class 8 + 7) — LOW/MEDIUM, IN-SCOPE
Evidence: `budget_ledger.start()` runs in `_run_loop` (cli.py:2717-2726) BEFORE
`run_cycle`'s `assert_can_act`; `classify` never reads `current_state` (recovery.py:290-362).
Live: seq 32-33 — a start against the HALTED journal classified SAFE_CHECKPOINT and journaled
`run_budget_started` (03:01:47Z), then the loop refused (`bad_cycle_entry_state`-class); the
later resumed budget reported "elapsed 9745.3s (RESUMED)" counted from that refused start
(M0-T107-cycle2-live-journey.md §1). A refused start thus mutates durable budget state and
starts the owner's wall clock.
Correction: check `machine.assert_can_act()`/entry-state before `budget_ledger.start()`; include
the blocking journal state in the pre-dispatch report (the classification text already
misleads here, compounding D7).
Test implication: start over HALTED/PAUSED asserts zero durable budget mutation and a
classification report that names the blocking state.

## D14 — Argparse requires nothing for `start`; enforcement is split across three layers with different refusal shapes (class 2 + 10) — MEDIUM, IN-SCOPE
Evidence: zero argparse-required start args (parser introspection, file 1 §C.1); the six-input
gate (start_gate.py:422-435) does NOT include `--worktree`, so a packet-declaring launch missing
it is refused by the deeper seam with `unsafe`/exit 11 rather than by the
`missing_required_inputs` listing (`stale_state`/exit 13) — exactly the M0-T124 §4 shape; other
absences degrade silently (--checkout=cwd cli.py:3175; --repo=checkout D2; --branch="" unpins
the branch probe; --stage=packet.status).
Correction: when the packet declares a worktree, add `--worktree` to `dispatch_inputs_missing`
(name the missing flag in one consolidated refusal); consider requiring `--checkout` explicitly
for `start` in unattended shapes.
Test implication: contract test enumerating the dispatch-required set and asserting every
presented command satisfies it (joint with D1's tooth).

## D15 — Runbook drift (class 3) — LOW, IN-SCOPE (presented-command surface)
Evidence: docs/CONTROLLER_UPDATE_RUNBOOK.md §1 digests are stale — protected config
`6aef12a9…` vs live `A1F99501…` (M0-T113 §5 A2 after the owner's approved edit);
model-selection `0e2432c0…` vs `FCBBF70F…` (M0-T113 §5 A1; the report itself flags the doc
refresh); §5 writes the manifest INSIDE the repo tree (`--out tools\agent_supervisor\…`) while
certified practice stores it OUTSIDE (`%LOCALAPPDATA%\…\ctl24-activation\`, M0-T113 §1 item 10,
M0-T124 §5 command); §11 presents the retired M0-T063 campaign identities. §9a and the
launch-seam appendix (lines 319-351) are current and parser-consistent.
Correction: regenerate §1/§5/§11 from live sources under D1's tooth.
Test implication: the D1 command-document validation covers the runbook's command blocks.

## D16 — Legacy/stale durable records on the journey (class 7) — LOW, IN-SCOPE (verified bounded)
Evidence: (i) the pre-T123 continuity record carries no token key => read as unknown
(session_continuity.py:148-160, correct fail-closed) — the live shed therefore keyed ONLY on the
leftover rotation_pending flag (`shed_context_tokens: null`, `known_over_ceiling: false`, seq
48); with the flag already consumed, a legacy over-ceiling session would not shed — but it also
cannot be resumed (evaluate_ceiling REFUSES unknown telemetry at every resume path,
launch_seam.py:289-294), so exposure is bounded to a missed proactive shed, not a resume.
(ii) determined-dead child records are cleared only by the launching runner's settle
(recovery.py:190-208); records from a crashed supervisor persist and are re-probed on every
recovery forever (no GC) — noise, fail-safe direction.
Correction: fold (i) into D5's re-recording; add a recovery-time sweep that archives
determined-dead child records with provenance.
Test implication: legacy-record fixtures (no-token continuity record; dead child record) through
start/recovery.

## D17 — No test consumes the owner-presented command shapes (class 10) — MEDIUM, IN-SCOPE
Evidence: the live §4 refusal escaped 2,889 passing tests, five certifications, and the R350
preflight because certification is non-live and no test parses the presented documents
(M0-T107-amendment20-start-refusal.md §3, explicit); test sweep: launch-seam tests cover refusal
codes (tools/test_agent_supervisor_launch_seam.py, 64 tests) and bounded-mode tests drive
cmd_start with fully-named harness inputs (tools/test_agent_supervisor_bounded_mode.py, 91
tests), but none reads M0-T124/runbook command text.
Correction: D1's tooth, wired into CI and into the certification checklist ("re-derive the
presented start command…" — the carried follow-up in M0-T124 §5, now made mechanical).
Test implication: the tooth IS the removal-sensitive test; it must fail when a doc command and
the parser/seam contract diverge in either direction.

## Checked-and-CLEAN (absence of findings as evidence — what was examined and passed)
1. launch_seam.py (read in full): Windows path folding, basename-vs-absolute packet matching,
   exact-at-ceiling >=, unknown-telemetry REFUSE, unconditional pre-Popen enforcement
   (claude_runner.py:1224-1235) — no gap found; live-proven refusal (exit 11) and shed (seq 48).
2. Exactly-once forwarding IN-PROCESS (loop.py:2378-2436): enqueue-then-send-then-mark, duplicate
   suppression, resumed-unsent row keeps its own bytes — clean (defect D10 is the CROSS-process
   boundary only).
3. extract_checkpoint (claude_runner.py:725-780): conflicting duplicates and multiple distinct
   checkpoints refused rather than chosen — satisfies the R380/R382 direction; clean.
4. Checkpoint/decision record strictness (models.py:96-237): unknown-field rejection, usage
   never zero, six-decision validation with per-decision required fields — clean.
5. Codex reviewer (codex_reviewer.py, read in full): read-only argv guard, fresh process per
   attempt, bounded retry carrying the validation error, provider-failure vs missing-file
   classification, self-report mismatch recorded — clean.
6. restart_channel.py preconditions and exactly-once edge firing under the lock — clean;
   owner-restart live-proven (seq 34/35).
7. Cross-process approved-forward integrity (pending_prompt digest binding, sealed-audit
   cross-check, covered-instruction reconstruction; loop.py:2466-2586, cli.py:1982-2032) — clean.
8. Audit chain mechanics (audit_log.py:1-120): tamper/reorder/truncation detection with the head
   sidecar — clean (the D6 ordering is a producer-side commit-point issue, not a chain defect).
9. Session-id conflict handling (claude_runner.py:1327-1342; loop.py:1609-1619): ambiguous
   identity dropped, never resumed — clean.
10. Child-process accounting record/settle/refuse (claude_runner.py:1482-1568; recovery.py:
    155-223): honest orphan-live naming, per-(pid,token) clears — clean apart from D6's
    crash-window semantics and D16(ii) noise.
11. clear-recovery / resume-pending-prompt fail-closed guards (cli.py:1848-2045) — clean;
    live-proven (seq 15/44, and the M0-T045..T048 digest chain).
12. The bounded-mode owner gate (start_gate.py:61-91; loop.py:253-331): refusal-by-name in both
    directions (mode without enable; enable without gated mode), sealed refusal audit — clean.
