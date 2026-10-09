# DCV Report — M0-T115 (D-024 Amendment 12, unit O)

**OVERALL VERDICT: PASS** — all three applicable requirement rows SATISFIED on primary evidence I reproduced myself. One non-blocking NOTE (a producer self-count is off by one; the requirement's literal obligations are still fully met — orchestrator should correct the "9 tests/5 guards" figure in any downstream summary).

**Frozen review identity:** `4d3760e10aae9b0e1d074dbe95760702dc36518b` — `git rev-parse HEAD` returned exactly this. No mismatch; not BLOCKED.

**Applicable set (re-derived, not trusted from the packet):**
`evaluate_task_refs(M0-T115.json)` → `ok=true`, `applicable_ids=["D-024-R272","D-024-R273","D-024-R274"]`, `cited_ids` identical, `missing_ids=[]`, `invalid_refs=[]`, `unresolved=[]`. Matches expected.

**Deliverable:** commit `91664bb` (parent `8d46318`), +247/-0 across exactly 5 files, all strictly within `allowed_paths`: `tools/agent_supervisor/broker.py` (+15), `tools/agent_supervisor/recovery_probes.py` (+26), `tools/test_agent_supervisor_command_authority.py`, `tools/test_agent_supervisor_recovery_probes.py`, `project-control/reports/M0-T115-repair-record.md`. Path-scoped content identity confirmed: `git diff 91664bb HEAD` over these 5 paths is empty (byte-identical); the 3 later control commits touch only control-plane files (gates/reports/state/task json). Verifying at HEAD == verifying at 91664bb.

## Per-row table

| Row | Verdict | Primary evidence I personally verified | Notes |
|---|---|---|---|
| D-024-R272 | **SATISFIED** | Own packet/claim/commits separate from M0-T114; T114 is a separate un-executed backlog packet on different files; no broadening | See below |
| D-024-R273 | **SATISFIED** | Probe change is read-only in-memory filtering (zero journal writes); broker uses pre-existing documented `resolve_ask` surface; pre-fix raw row proven still-unanswered after probe; no journal-editing tooling in history since 871cab8 | See below |
| D-024-R274 | **SATISFIED** | 4 defect tests cover deny→restart AND approve-once→restart against both new and pre-fix journals; I reproduced GREEN (117 passed); RED+REVERT-PROOF documented with exact commands; residual honestly disclosed | Count NOTE below |

## R272 — same-window, separate, no broadening — SATISFIED
- **Own lifecycle:** M0-T115 has its own G0/claim (`be5e09a`, `8d46318`), deliverable (`91664bb`), evidence-map/G2 (`848d68b`), and G2-PASS/submit (`4d3760e`) — all distinct from M0-T114. Amendment 12 itself was captured as its own file (`b180754`).
- **M0-T114 is separate and not yet executed:** `project-control/tasks/M0-T114.json` exists with `status="backlog"`; its `allowed_paths` = `telegram_sink.py`, `live_observation.py`, `test_agent_supervisor_telegram_sink.py`, `test_agent_supervisor_golden_run.py`, `M0-T114-residual-fixes.md` — a disjoint file set. Its turn follows in the same window.
- **No M0-T114-scoped file in this diff:** the 5 files in `91664bb` are only broker.py, recovery_probes.py, the two supervisor test packs, and the repair record. Neither `telegram_sink.py` nor `live_observation.py` appears.
- **No broadening:** `cli.py` is a forbidden path and is untouched; the change is +247/−0, cohesive to the defect (broker mirrors its own `revoke_all` M0-T070 pattern; probe mirrors the existing `cli.py` status reconciliation).

## R273 — no manual runtime-journal edit — SATISFIED
- **Probe is read-time only:** `probe_pending_requests` reads `journal.all_state()`/`open_asks()` and filters `open_asks` in memory; grep of the probe diff for `set_state|resolve_ask|.write|open(` → NONE. Read-only proof is baked into the test: `test_a_pre_fix_denied_request_journal_does_not_block_restart` asserts `len(journal.open_asks()) == 1` after the probe passes (line 41) — the raw pre-fix row is unchanged.
- **Broker writes only through a documented surface:** `deny_request`/`approve_once` call `journal.resolve_ask("ask_<request_id>", …)`, a pre-existing durable-state method (`tools/agent_supervisor/durable_state.py:673`) already used by `revoke_all` (M0-T070 precedent, broker.py:699). R273 explicitly permits state changes "through a documented CLI/broker surface." This resolves NEW answers going forward; it is not a hand-edit of the durable state file, and pre-fix journals are made truthful purely by the read-time reconciliation.
- **No journal-editing tooling in history:** rigorous added-line scan `git log -p 871cab8..HEAD | grep '^+' | grep -i 'NYCBuildabilitySupervisor|LOCALAPPDATA|edit_journal|hand_edit'` → exit 1, no matches. No live/dispatch/deploy surface touched by the diff.

## R274 — path proofs vs new + pre-fix records — SATISFIED
Four defect tests, covering both paths × both journal shapes:
1. `test_deny_resolves_the_queued_ask_row_not_just_the_approval_record` — deny, **new** journal (asserts `open_asks()==[]`, queued_asks row answered, record=DENIED).
2. `test_approve_once_resolves_the_queued_ask_row` — approve-once, **new** journal.
3. `test_a_pre_fix_denied_request_journal_does_not_block_restart` — deny, **pre-fix** journal (probe reconciles at read time; raw row proven still unanswered → also anchors R273).
4. `test_a_pre_fix_approved_request_journal_does_not_block_restart` — approve-once, **pre-fix** journal.

Guards (4): `test_a_digest_mismatch_deny_leaves_the_ask_row_open`, `test_a_broker_ask_with_a_pending_record_still_blocks`, `test_a_broker_ask_with_no_approval_record_still_blocks`, `test_a_non_broker_ask_still_blocks_regardless_of_state`.

- **GREEN reproduced by me:** `python -m pytest tools/test_agent_supervisor_command_authority.py tools/test_agent_supervisor_recovery_probes.py -q` → **117 passed in 16.85s** (matches the expected 117).
- **RED + REVERT-PROOF documented with exact commands/results:** repair-record §3 records RED = "4 failed, 6 passed" pre-fix (the four defect tests fail); REVERT-PROOF = `git stash push broker.py recovery_probes.py` → 4 failed → `git stash pop` → 4 passed. I did **not** re-execute the stash-based revert-proof (read-only mandate — `git stash` mutates the tree). Removal-sensitivity is independently established by code inspection: the parent `8d46318` lacks both `resolve_ask` calls and the read-time reconciliation, so tests asserting `open_asks()==[]` / probe-passes deterministically fail pre-fix — consistent with the recorded RED. So this is verified on primary evidence (diff + reproduced GREEN + inspected assertions), not on the producer's claim alone.
- **Honest residual, not a hidden gap:** repair-record §4 final bullet states the real end-to-end deny→clear→restart against the REAL pre-fix journal executes at the R276 resume after M0-T116 recertification; the probe boundary tested here is the exact step that refused live (`run_M0_T107_unitJ`, exit 11, `UNSAFE_OR_DRIFTED pending_requests`). Disclosed as a decomposition residual.

**NOTE (non-blocking self-count discrepancy):** the commit message and this task's instruction both say "9 new tests (4 defect + 5 guards)." Actual added test functions = **8** (4 defect + 4 guards); a 9th body added is the `_queue_broker_ask` helper (not a test). The repair-record §4 guard enumeration itself lists only 4 (digest-mismatch, pending, no-record, non-broker), consistent with 8. R274's literal text mandates both paths × both journal shapes with removal-sensitive tests — all present — and prescribes no guard count, so the requirement is fully met. The "9/5" figure is an off-by-one in the producer's summary; recommend the orchestrator correct it in any downstream narrative.

## Registry / integrity / prohibited-action evidence
- **Source digest match:** independent `sha256(source-012-amendment.md)` = `d0846b48045dd7868c1725614069541647473e764e4eb1b6426cec7ec3de5cce` == manifest `content_digest_sha256`. Amendment 12 verbatim (`---VERBATIM-BEGIN/END---`) present with forward-trace mapping to R272–R276.
- **Validator:** `python tools/validate_directive_compliance.py --check` → **EXIT=0** (completed in-runtime; not killed).
- **Prohibited actions — none:** task `status="awaiting_gate"` (progress 85), NOT accepted; no accept commit for M0-T115; diff touches no live/dispatch/deploy/canary surface (grep for live_observation/telegram_sink/canary/deploy/dispatch → NONE). Nothing merged/accepted/dispatched/deployed/installed/purchased/closed for this unit.

## Exact commands run
- `git rev-parse HEAD`
- `python -c "...directive_registry...evaluate_task_refs(M0-T115.json)"`
- `git show --stat 91664bb`; `git show 91664bb -- broker.py recovery_probes.py`; full test-file diffs
- `grep -rn "def resolve_ask" tools/agent_supervisor/`; `grep -n resolve_ask broker.py`
- `git log --oneline 871cab8..HEAD`; `git log -p 871cab8..HEAD | grep '^+' | grep -i '<journal-edit needles>'` (exit 1)
- `python -m pytest tools/test_agent_supervisor_command_authority.py tools/test_agent_supervisor_recovery_probes.py -q` → 117 passed
- `python tools/validate_directive_compliance.py --check` → EXIT=0
- `python -c "sha256(source-012-amendment.md)"`; `git diff --stat 91664bb HEAD -- <5 reviewed paths>` (empty); `git diff --name-only 91664bb HEAD`

**No requirement is VIOLATED or UNVERIFIABLE.** Verdict: **PASS.**
