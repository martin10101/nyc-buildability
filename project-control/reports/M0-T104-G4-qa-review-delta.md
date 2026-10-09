# M0-T104 G4 QA review (round 2 — delta re-review) — VERBATIM reviewer return

Orchestrator note: saved verbatim from the resumed qa-engineer agent-return channel (transport
entity-decoding only: `&lt;` → `<`). Delta re-review at re-frozen deliverable identity `f610aab`
(HEAD `94d7bd9`, control records only). No agent-memory security flag on this run (the reviewer was
asked not to author guard-workaround notes and did not). Verdict recorded by the orchestrator: PASS.

Orchestrator-noted factual correction from this reviewer (accepted): the main report §7 states
"adapter pack 60 passed"; the true count is **58 adapter (53 round-1 + 5 correction) + 19 probe =
77**. The 77 total is correct and matches every run; "60" is an immaterial transcription typo. The
report file is part of the frozen reviewed identity `f610aab`, so it is NOT edited post-freeze (that
would invalidate the gate stamps); the correction is recorded here and in the acceptance note.

---

# GATE REPORT (DELTA RE-REVIEW) — G4 QA — Task M0-T104 correction round

- **Reviewer role:** independent QA (read-only; producer ≠ reviewer)
- **Re-frozen deliverable identity:** `f610aab` (HEAD `94d7bd9` adds only G3/G4 gate records — verified: `f610aab..94d7bd9` touches only `project-control/gates/M0-T104-G3.json` + `-G4.json`)
- **Round-1 verdict:** PASS + 3 advisories (ADV-1 post-stop absence tooth; ADV-2 command-exec error surface; ADV-3 worktree-name/agent-value teeth)
- **Method:** clean `git archive f610aab` extract into scratch; all re-execution there. Python 3.11.9, pytest 8.4.2, `claude 2.1.247` live.
- **VERDICT: PASS** — ADV-2 closed; F1–F4 corrections land with genuine teeth; no regression. 3 non-blocking ADVISORY residuals carried.

## Delta scope verification
`ac305ae..f610aab` production/test diff is confined to `native_runtime.py`, `runtime_backend.py`, `test_agent_supervisor_native_adapter.py` (+ project-control records). Guard/hook paths (`.claude/hooks`, `readonly_agent_guard*`) — **empty diff**, byte-identical to the round-1 state I verified `ALL CHECKS PASSED`. Note: the two `agents_listing` fixtures show **no** byte change under `ac305ae..f610aab` — the F3 comprehensive masking produces identical output on the already-masked capture, so the F3 change is carried entirely by `mask_session_row` code + the new test (not fixture bytes). Fine and expected.

## Claim-by-claim re-execution

**(1) Combined pytest — expect 77, live rows execute: PASS.**
`python -m pytest tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_capability_probe.py -q` → **`77 passed in 19.48s`**. Per-file: adapter **58 passed** (53 round-1 + 5 new), probe **19 passed**. (Commit message's "60 adapter" is an arithmetic typo; actual is 58 + 19 = 77.) The 5 new correction tests are present and green: `test_verb_check_surfaces_daemon_failure`, `test_dispatch_default_backend_still_strips_child_env`, `test_mask_session_row_comprehensive_all_fields`, `test_agent_tools_value_charsets`, `test_reconcile_refuses_unavailable_feed`.

**(2) New tests genuinely pin the corrections — PASS (4 mutants killed in-memory, baselines hold, targets confirmed present):**
- **ADV-2** — mutate `_run_verb` check-branch to `if False:` → `test_verb_check_surfaces_daemon_failure` KILLED. Baseline: `stop("gone")` returns raw `unknown`; `stop("gone", check=True)` raises `stop_failed` (and `logs_failed`/`respawn_failed`).
- **F2** — mutate `dispatch` to `env = dict(self._base_env)` (skip strip) → `test_dispatch_default_backend_still_strips_child_env` KILLED (CLAUDECODE leaks). Confirms the strip is now unavoidable: `base_env=None` → `os.environ`, always `child_environment()`-stripped; no raw-inherit path remains.
- **F4** — mutate `if not feed_available:` guard to `if False:` → `test_reconcile_refuses_unavailable_feed` KILLED. A down feed now fails closed (`reconcile_feed_unavailable`) instead of bucketing every expected id as unexpected-exit → mass duplicate dispatch.
- **F3** — mutate `mask_session_row` to `masked = dict(row)` (no recursive `_mask_value`) → `test_mask_session_row_comprehensive_all_fields` KILLED (full UUID survives in `name`). Confirms masking is a comprehensive recursive pass over every string value.

**(3) ADV-2 closed: PASS.** `logs/stop/respawn` gained `check: bool = False`; `check=True` raises typed `<verb>_failed` on non-success, `check=False` preserves the raw `CommandResult`. Mutation-verified above. The command-exec error surface a wiring unit needs now exists without breaking inspect-the-result callers.

**(4) No regression: PASS.**
- The one changed round-1 test (`test_forbidden_flags_cannot_be_smuggled_via_values`) is **strengthened, not weakened**: rejection now happens at `DispatchSpec` construction (`invalid_tools`, and a new `agent="--cloud=x"` → `invalid_agent`) — earlier and broader than the old post-build `forbidden_flag`. `test_bypass_mode_never_reaches_argv` unchanged (S18 bypass refusal intact).
- `test_restart_no_duplicate_and_unexpected_exit` updated to assert both `needs_controller_review` (renamed for honesty) and the back-compat `safe_to_dispatch` alias — no assertion dropped.
- 0 tests removed (58 = 53 + 5). Guard/hooks byte-untouched. Modularity clean: `native_runtime.py` 492 SLOC / 25 symbols, `runtime_backend.py` 258 SLOC / 9 symbols — both well under WARN 600 / HARD 1000 / symbol ceiling 40; growth stayed within each module's existing responsibility (no dumping-ground, no responsibility mixing).

**(5) Skip hygiene holds: PASS.** With `claude`/`codex` removed from PATH: adapter → **56 passed, 2 skipped** (live tests lines 719/730 skip "claude CLI not installed on this runner"); probe → **17 passed, 2 skipped** (lines 182 claude / 218 codex); both returncode 0, no errors. The 5 new correction tests are deterministic (no skipif) and ran even with `claude` absent — skipif remains attached to the LIVE tests only (M0-T103 ADV-1 regression class stays absent).

## Residuals (ADVISORY — carried, non-blocking)
- **R1 (was ADV-1):** S6 post-stop absence verification is still deterministic-argv + live-canary only; there is no "stop → re-observe → assert absent" reconcile tooth. The new `check=` surface strengthens the *stop-command-failure* path but not the *absence* check. `find_by_identity` (the building block) is tested. Honestly labeled in the report; naturally closes when the seam is wired.
- **R2 (was ADV-3 — mostly closed):** agent/tools flag-shaped values are now **directly tested** (`test_agent_tools_value_charsets` covers `-x`, `--cloud`, `has space`, `a/b`, etc.). Remaining: `WorktreeSpec` `invalid_worktree_name` path still has no direct test.
- **R3 (new, minor):** the post-build `forbidden_flag` denylist branch (`native_runtime.py:457`) no longer has a direct test asserting that specific code — the round-1 test that reached it now asserts the earlier `invalid_tools` construction-time rejection. It remains a defence-in-depth backstop (docstring acknowledges), now reachable only via a prompt token exactly equal to a forbidden flag. Behavior is strictly stronger; purely a coverage note.

## Commands run (from the clean `f610aab` extract)
- `git archive f610aab | tar -x`; `git diff --stat ac305ae..f610aab` (+ fixtures/guard-path subsets); `git diff f610aab..94d7bd9`
- `pytest <adapter> <probe> -q` → 77 passed; `pytest <adapter> -q` → 58; new-test presence via `-v`
- in-memory mutation harness → ADV-2 / F2 / F4 / F3 mutants all KILLED, baselines hold
- skip-hygiene run (empty PATH) → adapter 56p/2s, probe 17p/2s, rc 0
- SLOC via `modularity_check.source_lines` → 492 / 258 (clean)

**Recommendation:** PASS. ADV-2 is closed and mutation-verified; F1–F4 corrections are real, tested, and strictly strengthen the adapter without regressing any prior coverage or the frozen guard packs. The three ADVISORY residuals are appropriate follow-ups (R1/R2 close when the seam is wired or with one small tooth each; R3 is a documentation-grade note). The orchestrator records the gate.
