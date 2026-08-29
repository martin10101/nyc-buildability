# G5 DELTA Re-Review — M0-T115 (consolidated correction round)

**DELTA VERDICT: PASS** (unchanged from prior PASS; all correction deltas verified — no gate weakened, no new surface added).
**Frozen review identity:** `29fc1e28e1e5c56036a87689d3ded203bf11f238` — verified `git rev-parse HEAD` == frozen SHA (branch `control/D-024-fable-codex-loop`; correction commit `c550309`). No mismatch.
**Delta range reviewed:** `git diff 4d3760e..29fc1e2` (4 commits). Prior review was at `4d3760e`.
**Reviewer:** independent G5, read-only.

## Production deltas since the prior PASS
- `broker.py` (+35): new module-level helper `owner_unanswered_asks(journal)` — the single shared read-time reconciliation predicate.
- `recovery_probes.py` (net −16): `probe_pending_requests` refactored onto the helper (its inline copy removed).
- `loop_turnover.py` (+25/−5): new `seam_safety_state(journal, facts)` feeds the rotation seam through `owner_unanswered_asks` (the 4th `open_asks()` consumer, previously raw).
- Tests: +1 probe hardening test (LOW-2), +5 seam reconciliation tests (G3 BLOCKER-1).
- `cli.py` deliberately untouched (status command keeps its identical pre-existing inline copy).

## Predicate semantics — identical to what I verified in round 1 — CONFIRMED
`owner_unanswered_asks` (broker.py:741-773): `_owner_answered` = `ask_id.startswith("ask_")` AND `isinstance(record, dict)` AND `record.get("status") != STATUS_PENDING` ("PENDING_OWNER"), keyed at `APPROVAL_PREFIX + ask_id[4:]` = `"approval/" + request_id`. This is byte-for-byte the predicate I already validated. An ask is removed from the blocking set only when a broker approval record exists as a dict with a non-PENDING status — a genuine owner answer. Missing record, non-dict record, still-PENDING record, and non-broker ask (`ask_id` not starting `"ask_"`) all remain blocking. Unchanged.

## (1) Single-source predicate + conservative degrade — CONFIRMED SAFE
- **Read-error propagation:** the helper calls `journal.open_asks()` then `journal.all_state()` with NO internal try/except; both errors propagate to the CALLER. The probe wraps the call in one try/except → `_unknown("pending_requests_unreadable")` (fail-closed, never empty). This preserves the round-1 fail-closed behavior for BOTH `open_asks` and `all_state` errors, now through a single handler. Verified by the new LOW-2 test.
- **Conservative degrade:** `if getattr(journal, "all_state", None) is None: return asks` — a journal object lacking `all_state` (reduced test fakes) keeps ALL asks blocking. This is the more-restrictive/fail-closed direction. In production the real `DurableState` always has `all_state`, so this branch is test-only. Safe.

## (2) LOW-2 accepted — CONFIRMED
`test_an_unreadable_approval_state_is_not_an_empty_one` added: a `HalfReadable` fake whose `open_asks()` returns an ask but `all_state()` raises `OSError` → probe returns `passes=False, known=False, reason_code="pending_requests_unreadable"`. Directly proves the refactored helper still fails closed on an unreadable state. Good disposition.

## (3) LOW-1 declined-with-reason — DISPOSITION ACCEPTABLE
The decline reason (cross-surface predicate consistency; divergence between surfaces is this unit's defect class; the no-status-record shape is unreachable in-code per my own round-1 analysis) is sound and I accept it. My LOW-1 was explicitly informational/defense-in-depth, and I confirmed in round 1 that only the broker writes `approval/*` records and always sets a defined status, so the `!= PENDING`-treats-absent-status-as-answered shape is not reachable in-code. This unit's central purpose is predicate CONSISTENCY across the probe, seam, and status consumers; introducing an answered-status allowlist in the shared helper while `cli.py` keeps `!= PENDING` would re-introduce exactly the cross-surface divergence this unit exists to eliminate. If the hardening is ever wanted it should be applied uniformly across all three surfaces in a separate change. Declining it here is the correct call. LOW-1 stands as a non-blocking, cross-surface future-hardening note, not a defect.

## (4) Rotation seam fail-opens NOTHING — CONFIRMED
Traced the full seam path:
- `seam_safety_state` → `safety_state_from_run(open_asks=owner_unanswered_asks(journal))` sets `approval_pending = bool(len(open_asks))` (turnover_seam.py:116).
- `_seam.execute` calls `assert_safe_seam(safety_state)` (turnover_seam.py:633) → `rotation.assert_safe_to_rotate`, and `approval_pending` is in `UNSAFE_MOMENT_CHECKS` (rotation.py:615), so a set flag raises `RotationError` → `SeamTurnoverError("unsafe_seam", …)` which "Always fails closed" (turnover_seam.py:76).
- Call site (loop.py:1092-1108) converts `SeamTurnoverError`/`LoopError` into `_turnover_refused` — the owner is told and the run pauses; the rotation-record and relaunch (lines 1109+) never execute.

Net effect: the seam stops refusing ONLY for genuinely owner-answered broker asks (the intended fix for pre-fix journals); a PENDING request, a broker ask with no record, and a non-broker ask (`rotation_pause/…` etc.) all still refuse the seam. Proved by the 5 new tests (`SeamSafetyFeedReconciliationTests`): pre-fix DENIED/APPROVED_ONCE → `approval_pending` False; PENDING/no-record/non-broker → `approval_pending` True. The change removes a false-refusal, never a real safety check, and adds no fail-open.

**One new LOW/informational (robustness, non-blocking):** a read error inside the seam path (`open_asks()` or the newly-added `all_state()` raising) propagates from `seam_safety_state` as a RAW exception (e.g. `OSError`), not a `SeamTurnoverError`, so it is not converted to the graceful `_turnover_refused` path at loop.py:1095. This remains fail-closed — the exception aborts `full_turnover` before line 1109, so NO rotation occurs and the run never rotates through an unreadable approval state — but the stop is a hard propagation rather than a clean refusal. (Round-1/pre-fix code already propagated `open_asks()` errors this way; the delta only adds `all_state()` as a second such source.) Optional remediation: wrap `seam_safety_state` to raise `SeamTurnoverError("safety_state_unreadable", …)` on read failure, mirroring the probe's `_unknown` handling, for a graceful owner-facing refusal. Not a gate weakening or fail-open; no seam test exercises this branch (minor coverage note).

## Secrets / deps / config / PR / R273
- **gitleaks** `--log-opts "4d3760e..29fc1e2"` → `no leaks found`, 4 commits, **EXIT 0**.
- **No new dependency** — only added imports are internal (`from .broker import owner_unanswered_asks`, in the probe and the seam). No dep manifest / lockfile touched.
- **No `.claude`/hook/MCP/settings change** in the correction diff.
- **No activation surface** — grep of the production diff for `limited-auto|activat|allowlist|policy_tier|classif|SHADOW|241` → none. Supervisor stays SHADOW-ONLY.
- **R273 upheld** — `owner_unanswered_asks` performs NO writes (only `open_asks()` + `all_state()`, both reads); `seam_safety_state` and the refactored probe only read; the broker answer-path `resolve_ask` writes (validated in round 1) are unchanged and execute only inside future owner answers; tests use in-memory/temp journals. No live-runtime-journal write in this unit.
- **PR #241:** confirmed OPEN/unmerged by the orchestrator (my round-1 deferred item); no reference in this diff, and a code diff cannot mutate a PR.
- **state.json:** correction added `M0-T115-G3` to `failed_gates` (honest recording of the gate-wave G3 FAIL at e945491); `M0-T115` remains in `active_tasks`, not `accepted_tasks` — no self-acceptance.

## Tests run
`python -m pytest tools/test_agent_supervisor_recovery_probes.py tools/test_agent_supervisor_command_authority.py tools/test_agent_supervisor_turnover_live_seam.py -q` → **211 passed** (Python 3.11.9, 18.9s), including the new LOW-2 probe test and all 5 seam reconciliation guards.

## Commands run (read-only)
- `git rev-parse HEAD` / `--abbrev-ref HEAD`; `git log --oneline 4d3760e..29fc1e2`; `git diff --stat`/`git diff 4d3760e..29fc1e2` (full + per-file)
- `git diff --name-only 4d3760e..29fc1e2 | grep -iE 'requirements|pyproject|package…|\.claude/|hook|mcp|settings'`
- `python -m pytest …recovery_probes.py …command_authority.py …turnover_live_seam.py -q`
- `C:/Users/MLFLL/.gitleaks/gitleaks.exe detect --source . --no-banner --redact --log-opts "4d3760e..29fc1e2"`
- Source reads: `broker.owner_unanswered_asks`, `loop_turnover.seam_safety_state`/`full_turnover`, `turnover_seam.safety_state_from_run`/`assert_safe_seam`/`execute`, `rotation.UNSAFE_MOMENT_CHECKS`/`assert_safe_to_rotate`, loop.py:1092-1122 call site.

**Bottom line:** The correction introduces a single shared read-time reconciliation predicate with semantics identical to the round-1 PASS, extends the same fix to the 4th `open_asks()` consumer (the rotation seam), and adds the requested hardening test. Both security-critical gates (S11.5 restart probe and the rotation seam) still fail closed on every genuinely-open ask (pending/no-record/non-broker) and abort on unreadable state; only genuine, digest-verified owner answers are reconciled out. No secrets, no new dependency, no `.claude`/hook/MCP/activation change, R273 upheld, 211 tests pass. One new non-blocking LOW/informational note (seam read-error propagates as a raw exception — fail-closed but non-graceful) and the standing cross-surface LOW-1 (declined, disposition accepted). **DELTA VERDICT: PASS.**
