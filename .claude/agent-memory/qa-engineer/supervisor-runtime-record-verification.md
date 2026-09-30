---
name: supervisor-runtime-record-verification
description: How to independently verify agent-supervisor limited-auto loop-operation claims (dispatch, checkpoints, ask-stops, halts) from the runtime records, read-only, and the M0-T115 ask-row seam gotcha
metadata:
  type: reference
---

Verifying "the loop actually ran / stopped fail-closed" claims (D-024 activation units like M0-T113):
the authoritative runtime records live OUTSIDE the repo at
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\<sha256_head-of-checkout-path>\` — one dir per checkout
path (ctl24 = `33dfa57d54dbc5d1...`). Each holds `audit.jsonl` (hash-chained event log),
`audit.jsonl.head.json` (last seq+digest), and `supervisor_journal.sqlite3`.

**Read them directly, read-only** (`sqlite3.connect(f"file:{db}?mode=ro", uri=True)`); do NOT run the
live `python -m tools.agent_supervisor status` for a frozen gate — it could mutate frozen runtime
state that later acceptance depends on. The journal IS what status renders.

Key signals:
- `claude_unit_completed` events = dispatched worker runs. `permission_decisions: []` = ZERO ask-stops
  (the proof-goal signal); `["deny","deny","deny"]` + `error_category:"missing_checkpoint"` = the
  ask-stop/S14 failure mode. `checkpoint_id` non-empty + `returncode:0` = structured checkpoint reached.
- State chain is in the `transitions` table; `state_kv.current_state` is the resting state. A refused
  pre-dispatch restart records a `recover_boot` (UNSAFE_OR_DRIFTED) but NO transition, so the journal
  correctly "stays at PREFLIGHT" (don't mistake this for a discrepancy).
- Counters live in `state_kv['run_budget/<run_id>']`: claude_runs_per_task, codex_reviews_per_checkpoint,
  model_calls_per_task, external_writes_per_task, restart_attempts, resumes.
- `effects`/`outbox`/`inbox` tables = external writes / Telegram / inbound; 0 rows corroborates
  "zero external writes / presence-only Telegram".
- Verify chain integrity: each line's `prev_digest` == previous line's `digest`, seq monotonic 1..N,
  head.json == last line.

**M0-T115 ask-row seam gotcha:** after an owner `deny`, the raw `queued_asks` rows KEEP
`answered_at_utc=''` (unresolved at row level). Resolution is READ-TIME reconciliation only (status CLI),
never a row edit. So verify "0 open asks" via the `state_kv['approval/<id>']` records (`status:DENIED`),
NOT the queued_asks table — and the unresolved rows are POSITIVE evidence the journal was not hand-edited.

**DCV vs QA:** the directive-compliance-verifier is a SEPARATE reviewer. Its
`verification.json` block for the task carries `applicable_requirement_ids` (the authoritative resolver
set — cross-check the producer's evidence-map keys against it) but its per-req states can be all
`pending` at QA-gate time; the DCV PASS is a distinct acceptance-blocking gate, not a QA defect.
