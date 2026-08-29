# M0-T115 — RepairRecord (H2 8-predicate gate) + red/green/revert-proof evidence

Task: M0-T115 (unit O; Amendment 12 rows R272/R273/R274). Producer:
fable-orchestrator-session. Supervisor-freeze qualifying evidence: **D-024-R270/R272**
(reproduced defect + owner execution order). Reliability standard sections applied:
§1 (cause at the owning boundary), §2 (smallest fitting change), §3.1/§3.3/§3.4
(red-before-green, defect-named tests, revert-proof), §5 (idempotency preserved), §8.

## 1. The defect (reproduced live, named in the tests)

First live limited-auto run `run_M0_T107_unitJ` (2026-08-29): owner denied three ASK
requests via the documented `deny` command; `clear-recovery` succeeded; the identical
certified restart was then REFUSED pre-dispatch — `UNSAFE_OR_DRIFTED`, revalidation failed
`['pending_requests']`, 0 provider calls, exit 11 (`M0-T113-activation-evidence.md`
addendum). Cause, at two write/read boundaries:

- **Write side (`broker.py`):** `deny_request` and `approve_once` set the approval record
  answered but never resolve the `ask_<request_id>` row minted by `defer` — the exact
  omission M0-T070 fixed in `revoke_all` ONLY. `revoke_all` cannot repair it afterwards
  (it skips DENIED records).
- **Read side (`recovery_probes.py`):** `probe_pending_requests` read raw
  `journal.open_asks()` without the M0-T070 read-time broker-reconciliation the status
  command applies (`cli.py` ~1493), so the stale rows blocked every restart forever.

## 2. The fix (smallest fitting change, §2)

- `broker.py::deny_request` and `::approve_once`: on the SUCCESS path only (never on
  digest-mismatch / not-pending refusals), `journal.resolve_ask("ask_<request_id>", …)` —
  the literal `revoke_all` pattern; the row is preserved as answered history, never
  deleted.
- `recovery_probes.py::probe_pending_requests`: broker-origin ask rows (`ask_` prefix)
  whose approval record exists with `status != PENDING_OWNER` are answered history —
  the cli.py predicate mirrored EXACTLY; non-broker asks and pending records block
  exactly as before; an unreadable state read fails closed (`pending_requests_unreadable`).
  This read-time reconciliation is what makes journals written BEFORE the fix — including
  the live one — truthful **without any runtime-journal edit (R273)**.
- NO other changes: no cli.py edit (already correct; FORBIDDEN path), no policy change,
  no new dependency, no schema change. Pre-existing unused imports flagged by local ruff
  (`recovery_probes.py:48 json`, test file `AuditLog`) are unused at HEAD too and are NOT
  cleaned here (§2.4 no silent scope-widening; `tools/` is not lint-gated in CI — the api
  job's `ruff check .` runs inside `services/api`).

## 3. Red → green → revert-proof (§3.1, §3.4; R274 removal-sensitivity)

- **RED (unchanged code):** `python -m pytest tools/test_agent_supervisor_command_authority.py
  -k "resolves_the_queued_ask_row or digest_mismatch_deny" tools/test_agent_supervisor_recovery_probes.py
  -k "pre_fix or still_blocks …" -q` → **4 failed, 6 passed** — the four defect tests
  (`test_deny_resolves_the_queued_ask_row_not_just_the_approval_record`,
  `test_approve_once_resolves_the_queued_ask_row`,
  `test_a_pre_fix_denied_request_journal_does_not_block_restart`,
  `test_a_pre_fix_approved_request_journal_does_not_block_restart`) failed; the six
  guard tests passed (they must hold before AND after).
- **GREEN (fixed code):** both full packs → **117 passed, 0 failed**.
- **REVERT-PROOF:** `git stash push tools/agent_supervisor/broker.py
  tools/agent_supervisor/recovery_probes.py` → the same 4 tests **FAILED** (4 failed,
  113 deselected) → `git stash pop` → **4 passed**. The tests detect the regression.

## 4. R274 path proofs — decomposition

- **deny → clear-recovery → restart, pre-fix journal:** probe-level test constructs the
  EXACT live shape (unanswered `ask_*` row + `DENIED` approval record) → probe PASSES,
  and the raw row is proven STILL unanswered afterwards (read-only; R273).
- **deny → restart, new journal:** broker test proves deny resolves the row (no open ask
  remains at all).
- **approve-once → restart, both shapes:** mirrored pair (`APPROVED_ONCE`).
- **Gate not weakened:** pending records, broker asks with NO record, and non-broker asks
  (rotation-pause) all still FAIL the probe — three dedicated tests.
- **End-to-end live confirmation:** the real deny→clear→restart against the REAL pre-fix
  journal executes at the R276 resume after M0-T116 recertification — the probe boundary
  tested here is the exact step that refused live.

## 5. Affected-pack evidence

broker + command_authority + recovery_probes + recovery + crash + start_reentry + phase1:
**353 passed, 0 failed**. `modularity_check --check` EXIT=0 (broker.py 785 SLOC — above
the 750 justify threshold ONLY via this cohesive +14-line mirror of its own existing
pattern; no responsibility added). Whole-suite + CI evidence lands at M0-T116 (the owner
ordered ONE certification window).

## 6. H2 RepairRecord — the 8 predicates

1. **Wrapper-around-defective-path?** NO — both fixes change the owning functions
   themselves (the answer paths and the probe), not a wrapper.
2. **Stale callers?** `grep resolve_ask` call sites: broker.revoke_all (pattern source),
   the two new call sites, operator_ask.py:357 (independent, unchanged semantics). No
   other deny/approve surfaces exist (`cli.py cmd_deny/cmd_approve_once` delegate to the
   broker methods fixed here).
3. **Regression test fails if fix removed?** YES — recorded revert-proof (§3).
4. **Compatibility exception?** NONE needed (no interface change; `resolve_ask` is
   idempotent — second resolution returns False harmlessly, proven by the pre-existing
   idempotency test).
5. **Root cause vs symptom?** Root cause at both boundaries; the read-side reconciliation
   is not a workaround — it is the SAME truth rule the status command already applies,
   and it is the only non-journal-editing way to honor R273 for pre-fix journals.
6. **Defect named in tests?** YES — docstrings cite the M0-T113 live-restart defect and
   D-024-R274.
7. **Search/graph for other instances?** `deny_request`/`approve_once` were the only
   answer paths lacking the M0-T070 resolution (revoke_all has it; defer mints the row);
   `open_asks()` consumers: cli status (reconciles), operator surfaces (display-only),
   this probe (now reconciles).
8. **Disposition:** FIXED at root; no auto-accept — independent G3/G4/G5 + DCV review
   this record at the frozen identity.
