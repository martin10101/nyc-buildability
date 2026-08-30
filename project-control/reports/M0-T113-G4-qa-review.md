<!-- Saved VERBATIM by the orchestrator from the G4 qa-engineer agent-return channel
     (transport entity-decoding only). Review head 702c64c. NOTE: the reviewer's angle-
     bracket placeholders and entity-encoded characters are preserved as returned. -->

G4 review complete. All evidence reproduced from primary artifacts at the frozen head. Here is the gate report.

---

# G4 QA GATE REPORT — M0-T113 (D-024 Amendment 9 R187/R595 limited-auto activation act + first-loop operation proof)

**Reviewer:** qa-engineer (independent, read-only)
**Frozen reviewed SHA:** `702c64c8131a17570e2b9f8815734816b2aa0776` (branch `control/D-024-fable-codex-loop`; confirmed = frozen head; shared checkout clean at session start)
**Task state:** awaiting_gate | task_type governance, path_free_governance=true | directive_refs D-024:ALL
**Method:** direct read of committed deliverables at the frozen SHA + read-only reads of the out-of-repo supervisor runtime records (`audit.jsonl` + `supervisor_journal.sqlite3`, opened `mode=ro`) + read-only git against the shared object DB via my own worktree. The worktree guard blocked every git invocation that redirected to the shared checkout (`cd`, `--git-dir`) and rejected compound heredocs; I ran the equivalents against my linked worktree (same object DB) and via scratchpad scripts. I did **not** run the live supervisor `status` CLI — that could mutate the frozen runtime state the pending acceptance depends on; the journal it renders was read directly instead (documented as an INFO note, not a BLOCKED reason).

---

## 1. PROOF-GOAL VERIFICATION (the crux) — CONFIRMED

Claim: *routine discovery reached a structured checkpoint with ZERO ask-stops.*

Primary artifact: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\33dfa57d54dbc5d11d55dd8bab9248280e6568ef0e50002ba04a38543967a7ed\audit.jsonl` (31 events, hash-chain intact, seq monotonic 1..31, head.json seq 31 digest `53db08f2…` = last line).

**Rerun `claude_unit_completed` (audit seq 21, 2026-08-30T01:41:24Z):**
- `permission_decisions: []` — **ZERO ask-stops** ✓
- `events: 143` ✓
- `observed_models: ["claude-fable-5"]`, `model_mismatch: false` ✓
- `returncode: 0` ✓
- `checkpoint_id: "M0-T107-ready-2026-08-29-01"`, `output_digest: 2ac59818538b8b63…` (= evidence checkpoint digest `2ac59818…`) ✓
- `context_tokens: 604772` (= the rotation figure) ✓

**Checkpoint-received chain (journal `transitions` table, cycle 2):** `PREFLIGHT → START_CLAUDE → CLAUDE_RUNNING → CHECKPOINT_RECEIVED → COLLECT_EVIDENCE → CODEX_REVIEW → VALIDATE_DECISION → POLICY_CHECK → HALTED`. `state_kv.current_state = "HALTED"`, `last_trigger = "decision_halt_unsafe"`. ✓ Matches evidence addendum-2 item 6 exactly.

**Contrast with the FIRST activation (audit seq 8, 2026-08-29T05:07:16Z):** `permission_decisions: ["deny","deny","deny"]`, `returncode: 1`, `error_category: "missing_checkpoint"`, `checkpoint_id: ""`, 115 events → S14 stop (transition `CLAUDE_RUNNING → PAUSED_RECOVERY [unsafe_condition]`). The three deferrals (audit seq 5-7, all `DEFER_TO_OWNER`, rules `S4.3/fallthrough` + `S4.3/unclassified_command`) carry request-digests `5637335f…/56cbd282…/ae36645d…`, matching the queued_asks and the addendum-1 denials exactly.

**The delta is real and durably recorded:** 3 ask-stops + no checkpoint (first) → 0 ask-stops + validated structured checkpoint (rerun). The subsequent `HALT_UNSAFE` (Codex `gpt-5.6-sol`, finding *"The mandatory fresh, independent repository review was not completed, so issuing CONTINUE would rely on the untrusted worker checkpoint"*, audit seq 27/30) is the certified review-independence stop, not a proof-goal failure. **PROOF GOAL MET.**

---

## 2. R260 ITEM-COMPLETENESS

**First-activation 7-item report** (`M0-T113-activation-evidence.md`):

| # | Item | Present | Specific + checkable anchor | Independently verified |
|---|---|---|---|---|
| 1 | Activation record + effective mode | Y | mode `limited-auto`, `limited_auto_enabled/dispatched true`, ctrl `0.4.0-phase4`, 11/11 probes, job_object; manifest `b07818fa` | audit seq 2/4 (`start_command`,`preflight_pass`, mode limited-auto) ✓ |
| 2 | Controller PID/session/run identity | Y | run `run_M0_T107_unitJ`, dir `33dfa57d…`, budget digest `c1a51d3a…`, start 05:05:19Z, elapsed 117s, exited exit 11 | run_id + budget_digest `c1a51d3a…` in run_budget; start 05:05:19.747Z; 05:05→05:07 ≈117s ✓ |
| 3 | Selected campaign task | Y | M0-T107, `supervisor-loop-fable-producer`, `wt-m0t107`, `task/M0-T107-plugin-portability` @ `796e18f` | ask records cwd `wt-m0t107`, branch string match ✓ |
| 4 | First bounded dispatch evidence | Y | provider_calls 1, claude_runs 1/12, 3 held cmds w/ ids+digests, all DEFER_TO_OWNER, S14 | audit seq 5-11 + queued_asks (3 read-only discovery cmds) ✓ |
| 5 | Operator commands | Y | full documented set (status/pause/resume/graceful-stop/stop/pending-approvals/approve-once/deny/clear-recovery + /loop-*) | deny + clear-recovery exercised (addendum 1); consistent ✓ |
| 6 | Telegram state | Y | configured no, queued 0, delivered 0, one-way R242, presence-only | `outbox`=0 rows ✓ |
| 7 | Awaiting owner | Y | 3 ASK requests + resume decision | approval records + PAUSED_RECOVERY ✓ |

**Addendum-2 (R276 rerun) 8-item confirmation set:**

| # | Item | Verified against primary artifact |
|---|---|---|
| 1 | Run identity resumed, resumes=1, budget digest byte-identical, 3 denied asks reconciled | run_budget `resumes:1`, `budget_digest c1a51d3a…`; audit seq 19 run_budget_resumed ✓ |
| 2 | One-time repin R285, pinned digest `d6f6c29a8ac6b3cf…` | `state_kv.cli_executable_identity`: repinned_by `operator --repin-cli-identity`, digest `d6f6c29a…`, replaced `8a9c9c90…`; audit seq 17 ✓ |
| 3 | Routing tooth `native_preferred` | Not in journal (probe result in start JSON output) — see MINOR-1 |
| 4 | Live Fable 5, session `02b014ee…`, 143 events, rc0, 2 calls | audit seq 21/22, `provider_session_continuity`, run_budget (claude_runs 2, codex 1, model_calls 3) ✓ |
| 5 | First checkpoint achieved, packet 46,025 B digest `5539a2be…`, permission_decisions [] | audit seq 21 (`output_digest 2ac59818…`, `permission_decisions:[]`), seq 26 (`packet_bytes 46025`, `5539a2be…`) ✓ |
| 6 | Certified fail-closed HALT_UNSAFE, S9 touch 2/2, exit 10 | transitions + audit seq 27-31; finding text verbatim; owner_touch_ledger S9 counted ✓ |
| 7 | Rotation pending 604,772 > 400k | `state_kv.rotation_pending=true`, reason `context_threshold`; audit seq 24 ✓ |
| 8 | HALTED, 0 open asks, 0 pending effects, 31 events, worktree clean, no external writes | current_state HALTED; effects 0; audit 31 events chain OK; external_writes_per_task 0 ✓ |

Every required item present, specific, and anchored. No vague claims.

---

## 3. EVIDENCE-MAP COVERAGE

- **32/32 applicable rows present.** `M0-T113-evidence-map.json` keys = `{R250-R271, R273, R276, R277, R280, R284, R285, R298-R301}`. This set is **identical** to the DCV's `applicable_requirement_ids` for M0-T113 in `verification.json` — no under-coverage, no over-coverage. R274 (referenced descriptively inside R269's evidence) is correctly NOT an applicable row.
- **Conditional rows honestly labeled:** R298 = "IN EXECUTION at submit"; R299 = "IN EXECUTION; discharged by the acceptance-time report"; R300/R301 = "RECORDED AND BINDING (conditional protocol)". None falsely labeled SATISFIED. ✓ R255 honestly qualified ("advancement gated by the certified review, which correctly held"). No row over-claims relative to citations.

**Six spot-checks against primary artifacts:**
- **R252** (preflight before every start): preflight report has the 14-row matrix (§1-4), §5 re-preflight PASS, §6 R276 stop-on-drift, seq-33 rerun preflight — multiple preflights, one per start. ✓
- **R263** (read-only live probe BEFORE change, passed): `M0-T113-fable-probe.md` + `state_kv.cli_capability_probes` — control-response VERIFIED `sha256_head 8a9c9c90…` (= the pre-repin `replaced_digest`), Probe B `init_model:["claude-fable-5"]`, 1 denial, `target_file_created:false`. ✓
- **R267** (no launch until manifest re-recorded AND preflight re-passes): §5 A3 manifest `b07818fa` then launch `cfc6b16`; audit seq 2/4 preflight_pass precedes START_CLAUDE. ✓
- **R270** (no restart-looping): run_budget `restart_attempts: 0`; audit shows the Amendment-11 refusal (seq 16) then NO further start until the authorized post-recert rerun (seq 17-20). ✓
- **R284** (R276 rerun from the beginning in order): sequence recorded consistently across progress_log + preflight (manifest `774f9198` 119 files → verify-controller → doctor 43/43 → doctor --live → preflight → start). ✓ (doctor steps not independently re-run — recorded, consistent.)
- **R299** (fresh pre-continuation readback at report time): labeled IN-EXECUTION; my read-time readback discharges its content — HALTED, 0 truly-open asks, effects 0, audit 31-event chain intact. ✓

---

## 4. TIMELINE CONSISTENCY — no anachronisms

Git author dates are `-04:00` (EDT); runtime timestamps are UTC (Z). Cross-checked, each capture precedes its runtime act:

| Arc step | Commit / event | Time | Order |
|---|---|---|---|
| Auth capture (Amdt 9) | `a87b407` | 2026-08-28 23:59:51 -04:00 | — |
| Amendment 10 | `c5ca81a` | 2026-08-29 00:33:21 -04:00 | after |
| Re-preflight PASS / launch authorized | `cfc6b16` | 00:59:14 -04:00 = 04:59:14Z | before start |
| **Activation start** | audit seq 1-2 | **05:05:19Z** | after cfc6b16 ✓ |
| Ask-stop S14 | audit seq 10-11 | 05:07:16Z | ✓ |
| Amendment 11 | `871cab8` | 01:28:26 -04:00 = **05:28:26Z** | before denials |
| Owner denials + clear-recovery | audit seq 12-15 | 05:28:50-52Z | after Amdt 11 ✓ |
| Seam-defect restart refusal | audit seq 16 UNSAFE_OR_DRIFTED | 05:33:51Z | ✓ |
| Amendment 12 window (T115/T114/T116) + Amdts 13/14 + T118/T120/T119 recerts | commits | 08-29 17:23 → 21:20 -04:00 | ~20h gap ✓ |
| M0-T119 ACCEPTED (unlocks rerun) | `c88c2b9` | 21:20:28 -04:00 = **2026-08-30 01:20:28Z** | before repin |
| doctor --live probe | `cli_capability_probes` | 01:21:11Z | after T119 accept ✓ |
| Rerun steps 1-5 green / classifier-denied step 6 | `4919007` | 01:28:00Z | ✓ |
| Bash-mangled attempt 1 | `dec29d2` | 01:37:57Z | journal stayed PREFLIGHT ✓ |
| One-time repin | audit seq 17 | 01:38:23Z | ✓ |
| **Rerun dispatch + checkpoint** | audit seq 21 | **01:41:24Z** | ✓ |
| HALT_UNSAFE | audit seq 27-31 | 01:41:42Z | ✓ |
| LIVE-PROOF commit / seq 33 / Amdt 15 | `0c7b7d8`/`3a83a3c`/`14e32a9` | 01:45:06→02:02:57Z | after halt ✓ |

The ~20-hour gap between the seam-defect refusal (05:33Z 08-29) and the repin/rerun (01:38Z 08-30) is fully accounted for by the recert window. Amendment captures always precede the runtime acts they authorize. **No anachronism found.**

---

## 5. NEGATIVE SPACE

- **No unreported dispatch/provider call.** Scan of all runtime dirs (mtime ≥ 2026-08-29) referencing `run_M0_T107_unitJ`/`M0-T107` returns exactly **one** dir (`33dfa57d…`) with exactly **2** `claude_unit_completed` events. Counters reconcile: claude_runs 2/12 (2 Fable), codex_reviews 1/3, model_calls_per_task 3 (2 Fable + 1 Codex). No hidden run dir, no stray dispatch.
- **Zero external writes corroborated three ways:** `external_writes_per_task: 0`, `effects` table 0 rows, and no `*write*/*effect*/*forward*` event types anywhere in the 31-event chain. `outbox`/`inbox` 0 rows (Telegram never sent).
- **Nothing in the journal contradicts the reports.** `launched_child_processes: []`, hash chain intact, head matches.
- Gap the proof does not close (see findings): the S11.5 probe breakdown (11/11, 12/12), the M0-T120 `native_preferred` routing verdict, and the raw `start` JSON output live in ephemeral task logs, not committed artifacts — only their aggregate outcomes (`preflight_pass`, dispatched, repin) are re-readable in the journal.

---

## 6. FINDINGS

1. **INFO — DCV pass still pending (acceptance-blocking, separate gate).** `verification.json`'s M0-T113 block has the correct 32-ID `applicable_requirement_ids` but every row is `state: pending`. The directive-compliance-verifier is a distinct reviewer_agent; acceptance is refused until it flips all 32 rows to PASS at the reviewed identity. Not a QA defect; flagged so the orchestrator does not accept on the QA verdict alone.
2. **INFO — status CLI not executed by design.** I verified the underlying journal directly rather than run the live supervisor and risk mutating frozen runtime state. If the orchestrator wants the CLI-rendered view on record, it can capture `python -m tools.agent_supervisor status --json` as committed evidence; the raw journal already substantiates every field.
3. **MINOR — "0 open asks" depends on M0-T115 read-time reconciliation, not the raw rows.** The `queued_asks` table still holds 3 rows with `answered_at_utc=''` (the pre-fix seam state); only the `approval/<id>` records show `status: DENIED`. The reports disclose this honestly (R273; preflight §6). The unresolved rows are in fact positive evidence the journal was not hand-edited. No action required; noted so a future reader does not mistake the raw rows for open asks.
4. **MINOR — routing/probe-detail claims not anchored to committed artifacts.** Addendum-2 item 3 (`native_preferred`) and the 11/12 pre-dispatch probe enumerations are asserted from ephemeral `start` JSON output; only aggregate `preflight_pass`/dispatched/repin are re-readable. Aggregate outcomes are verified; the granular probe list is not independently reproducible from committed evidence.
5. **INFO — minor internal wording tension on the Amendment-11 refusal resting state.** Addendum-1 item 3 says the restart "parked back in PAUSED_RECOVERY" (matches the `recover_boot` `next_state: PAUSED_RECOVERY`), while the preflight §6 and progress_log say "journal PREFLIGHT" (matches the committed `transitions` table — the refusal recorded no transition). Both are defensible from different journal fields; the material facts (dispatched false, 0 provider calls, exit 11, nothing written) are accurate. No correction required.
6. **INFO — R257 PR #241 non-merge not re-verified here.** `gh`/git-remote checks are outside my read-only sandbox; the prohibition is a DCV/T119-G5 concern. No runtime evidence contradicts it (no writes, no forwards, no merge events).

No BLOCKER and no MAJOR findings. The operational proof obligations of the packet are met and reproducible from primary artifacts at the frozen SHA.

---

## Commands run (read-only) + key result lines

- `git -C <my-worktree> rev-parse control/D-024-fable-codex-loop` → `702c64c8131a17570e2b9f8815734816b2aa0776` (= frozen SHA)
- `git -C <my-worktree> log --no-walk --date=iso-strict a87b407 c5ca81a 871cab8 cfc6b16` → dates as tabulated in §4
- scratchpad `verify_chain.py` over `audit.jsonl` → `AUDIT LINES: 31`; `SEQ monotonic 1..N: True`; `CHAIN LINKAGE OK: True`; seq8 `permission_decisions=['deny','deny','deny'] returncode=1 error_category='missing_checkpoint'`; seq21 `permission_decisions=[] returncode=0 checkpoint_id='M0-T107-ready-2026-08-29-01' events=143 observed_models=['claude-fable-5']`; write/effect/forward events: none
- scratchpad `dump_transitions.py` (sqlite `mode=ro`) → 13 transitions ending `POLICY_CHECK → HALTED`; `current_state="HALTED"`; approvals `9f45b2ca/c73f9247/7e4b33d8` all `status=DENIED`; `queued_asks` 3 rows `answered_at_utc=''`; effects/outbox/inbox = 0/0/0
- scratchpad `inspect_journal.py` → run_budget counters `claude_runs_per_task:2, codex_reviews_per_checkpoint:1, model_calls_per_task:3, external_writes_per_task:0, restart_attempts:0, resumes:1, exit_reason:halt_unsafe`; `cli_executable_identity` repinned `d6f6c29a…` replaced `8a9c9c90…`
- scratchpad `scan_runs.py` → dirs referencing `run_M0_T107_unitJ` with mtime≥2026-08-29: **1** (`33dfa57d…`, claude_unit_completed=2)

---

**G4 VERDICT: PASS**

(Independently reproducible; operation-beyond-launch and the zero-ask-stops-to-structured-checkpoint proof goal are confirmed at frozen SHA `702c64c`. The PASS is a QA verdict only — acceptance remains gated on the still-pending directive-compliance-verifier PASS across all 32 applicable rows, per finding 1. Findings 2-6 are non-blocking.)
