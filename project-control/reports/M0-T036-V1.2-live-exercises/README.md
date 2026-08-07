# M0-T036 — V1.2 live exercises (orchestrator-run, 2026-08-04)

- Authorization: D-007 amendment 10 (R592–R594) — the three live exercises use synthetic probe
  units only; shadow-only stays in force for real work; nothing forwards to any real task.
  Evening execution authorized by D-007 amendment 11 / D-004 amendment 26.
- Controller: `C:\SupervisorController` at `b16d502` (V1.2 code `33e3336` included; pulled
  current by the owner this session). Runtime bases: fresh per-run directories under the session
  scratchpad (never the owner-plane `%LOCALAPPDATA%` runtime).
- Workload: throwaway synthetic git repo (own bare origin, branch `synthetic/probe-v12`);
  task packet `synthetic-probe-packet.json` (task_id SYNTH-PROBE-V12, allowed_paths README.md +
  docs/**). Worker: installed `claude.exe` (account-default model per controller config);
  reviewer: installed `codex.cmd`, model gpt-5.6-sol per `model_selection.toml`.
- Every subdirectory here preserves one run VERBATIM: the `start --json` output, stderr (when
  non-empty), and the runtime `audit.jsonl`, `audit.jsonl.head.json`, `supervisor_journal.sqlite3`.

## Packet correction (recorded)

The packet staged by the prior session allowed `"docs/"`. `policy.path_matches` gives a
TRAILING-SLASH pattern no directory expansion (`policy.py:216` requires `not pattern.endswith("/")`
before appending `/**`), so `"docs/"` matches NOTHING and every docs write would have routed to
ASK instead of AUTO. Restaged with `"docs/**"` before exercise 1. Finding for packet-authoring
convention: a bare-directory allowed path must be written WITHOUT a trailing slash (or as an
explicit `/**` glob).

## Exercise 1 — live allow round-trip (QA gap 1): PASS

Invocation (ex1/, run_id `run_v12_ex1_allow`): `start --mode supervised --max-cycles 1` with the
inputs above. Result — one full supervised cycle:

- Path `PREFLIGHT → START_CLAUDE → CLAUDE_RUNNING → CHECKPOINT_RECEIVED → COLLECT_EVIDENCE →
  CODEX_REVIEW → VALIDATE_DECISION → POLICY_CHECK → COMPLETE`, stopped `stage_complete`; audit
  chain intact (13 events).
- **The wired broker permitted a live in-scope tool and it actually executed**: audit seq 4
  `approval_auto` / `APPROVE_ONCE` / `AUTO:in_scope_file_write` (rule S4.1/in_scope_edit) for the
  worker's Write of `docs/probe-note.md`; the file exists with the exact instructed content
  (`synthetic-worktree-docs-listing.txt`). The broker REJECTED the CLI's `setMode:acceptEdits`
  always-allow suggestion (recorded in the same event).
- Live Codex decision COMPLETE (gpt-5.6-sol, attempt 1). Model verification on-stream: no
  mismatch; context usage read off the stream (64,694 tokens; `usage_known` live-confirmed).

QA gap 1 (allow leg never exercised live) is CLOSED.

## Exercise 2 — context-threshold seam rotation (QA gap 4): rotation ARMED live; seam actuation structurally blocked (finding below)

Four runs preserved (ex2a–ex2d), all `--context-rotation-threshold 1 --max-cycles 2`:

- ex2a: worker unit + live review completed; the reviewer returned **ROTATE_SESSION** (S9
  decision path) because the unit prompt itself said "rotation exercise" — run stopped at
  `PREPARE_ROTATION`. V1.2 flag: `rotation_pending=True` armed live (ctx 64,215 ≥ 1),
  `rotation_pending_flagged` audited. Lesson: probe wording leaks into the reviewer's decision.
- ex2b/ex2c/ex2d (neutral "continuity probe" wording): every run completed cycle 1 live —
  checkpoint valid, evidence packet built, live decision **CONTINUE** with a next prompt,
  `rotation_pending=True` with reason `context_threshold` armed and audited — then stopped
  `operator_declined` at the supervised approval hold (WAIT_FOR_OWNER).

What is live-evidenced: the V1.2 context-threshold trigger (R743–R745) fires on a REAL worker
stream (usage read live, threshold crossed, durable flag + audit event, unit never interrupted —
S11.2 held). What is NOT live-evidenced: `_rotate_at_seam` actuation (archive → mint → relaunch),
which remains proven by the unit suite only (the dedicated V1.2 rotation tests).

## Exercise 3 — induced model mismatch: live DETECTION PASS; seam actuation blocked by the same finding

Three runs preserved (ex3a–ex3c), all `--expected-worker-model claude-does-not-exist-99
--max-cycles 2`:

- Every run: the worker LAUNCHED on its real (account-default) model — never on the fake id —
  and the stream verification flagged **`model_mismatch=True` live** (R739 per-event
  verification), arming `rotation_pending` with reason `model_downgrade`, audited.
- ex3a decision REVISE, ex3b/ex3c decisions CONTINUE; all stopped `operator_declined` at the
  supervised approval hold, before the seam.

The owner's "live-detected model mismatch (may be induced)" (D-004-R745) is CLOSED. The seam
rotation actuation on `model_downgrade` is blocked live by the same structural finding as
exercise 2.

## FINDING (first-class; returns to the owner): a live supervised run cannot reach the rotation seam

The V1.2 seam fires only between cycles, after a forwarded prompt is SENT (`loop.run()`); in
supervised mode a forward requires an operator approval bound to a digest over the reviewer
decision's instruction fields, including `next_claude_prompt` VERBATIM (`approval_digest_for`).
Two independent mechanisms make that unreachable live:

1. **No continuation path for a held prompt.** A run that stops `operator_declined` parks the
   journal at WAIT_FOR_OWNER. `CYCLE_ENTRY_STATES` is `{PREFLIGHT, CLAUDE_RUNNING}`, and the
   state machine's defined exits `owner_approved_pending_prompt` / `owner_answer_validated` are
   fired by NO CLI command (`approve-once` answers broker asks only). This is the exact analogue
   of pilot finding F-2 (PAUSED_RECOVERY had no operator exit before the V1.1 `clear-recovery`
   command).
2. **Digest pre-approval cannot converge on a live reviewer.** The only approval channel is
   `--approve-prompt-digest` at launch, which requires knowing the digest BEFORE the decision
   exists. Six live attempts (ex2b, ex2c, ex2d, ex3a, ex3b, ex3c) with byte-identical unit
   prompts produced six DISTINCT decision digests — gpt-5.6-sol re-words `next_claude_prompt`
   every run, and the decision file is unlinked after reading, so the wording is not even
   recoverable post-hoc. Accumulated digest pools (2–3 known digests pre-approved per retry)
   never matched.

The deterministic fake-harness tests pass because harness decisions are reproducible; the live
mechanism as built requires operator foreknowledge of LLM output. Disposition: recorded here and
surfaced to the V1.2 delta re-gate reviewers and the owner. The natural cure is a small follow-up
unit (e.g., a CLI command that fires `owner_approved_pending_prompt` against the pending-prompt
record on the SAME journal, mirroring the V1.1 `clear-recovery` precedent) — NOT built tonight:
it is new functional scope in the approval/forwarding control surface and is not covered by the
V1.2.1 authorization (D-007-R597/R598 is the quota-substitution correction only).

## Boundaries honored

Synthetic probe units only; the only prompts ever held for forwarding were synthetic and NONE
were sent (`forwarded_message_ids` empty in every run); shadow config untouched; no real task
was referenced by any unit; runtime bases isolated from the owner-plane runtime directories;
evidence preserved verbatim per run. The supervised single-forward rehearsal was NOT performed
(remains unauthorized, D-007-R600); limited-auto untouched.
