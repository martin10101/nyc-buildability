# M0-T126 — G3 DELTA report (independent code-reviewer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the SAME independent code-reviewer identity
that recorded the G3 FAIL at e029c8a, re-verdicting its three blocking defects plus delta
regression at the remediation identity 2d46fb0 (delta re-review pattern; reviewer read-only
throughout). DELTA VERDICT: PASS — G3-1/G3-2/G3-3 all RESOLVED; no new blocking findings;
non-blocking carries O2 (D9 selection simulation-only, defensible), O3 (full golden pack owed
at M0-T127), O4 (one producer-recomputed runbook digest not independently recomputable from
the sandbox; the two register-named digests match). Recorded as gate G3 PASS at the new
identity, superseding the FAIL record at e029c8a (which remains in history).

---VERBATIM-BEGIN---
Confirmed. Design-record §8 (lines 250-253) honestly documents the property-3 limitation in the amendment's exact "wherever technically enforceable" wording; §0 flags the R378 reconciliation; FakeRunner genuinely captures `extra_turns` (so the G3-2 dispatch test is non-vacuous). The argument threading is clean and additive.

Here is my delta gate report.

---

# G3 (code-reviewer) DELTA Gate Report — M0-T126 (remediation re-review)

**Task:** M0-T126 — durable checkpoint design + defect corrections (D-024 Amendment 22)
**Prior verdict:** FAIL at `e029c8a` (defects G3-1/G3-2/G3-3), recorded.
**Reviewed identity:** `2d46fb0` (verified stable: `git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` empty; HEAD `eee8ef0`)
**Delta diff:** `git diff 767b833 2d46fb0`
**Scope:** re-verdict my three defects + delta regression only (read-only; read-only pytest reproduced).

## DELTA VERDICT: **PASS**

All three blocking defects are genuinely remediated at the dispatch/document level with removal-sensitive tests, the acceptance-evidence overclaim is corrected, and the delta introduces no behavior change outside the correction scope. Reproduced: 8 defect packs **401 passed**; the 7 targeted remediation tests pass; command-doc tooth exit 0; modularity 335 files / **0 failures**.

---

## Per-defect re-verdict

### G3-1 — Rotated orientation wired at the dispatch level — **RESOLVED**
- `loop_turnover.with_reorientation` now takes `(loop, seam, prompt)` and front-loads the `rotated=True` property-1 packet via new `orientation.oriented_reorientation_prompt` (orientation.py:208-233), gated on `loop._turn_budget` (loop.py:684, wired from cli.py:2869 `turn_budget=turn_budget`). Both call sites updated (loop.py:2783, 2900); grep confirms **no other caller** of the old 2-arg signature anywhere in `tools/` (interface change fully propagated).
- Dispatch-level proof is real: `RotatedOrientationDispatchTests::test_rotated_dispatched_prompt_carries_cadence_paths_and_required_output` (loop.py test:1940) drives an actual context-threshold rotation and asserts the **successor's dispatched prompt** (`runner.prompts[1]`) contains the ORIENTATION sentinel, "ROTATED successor", the rotation reason, "CHECKPOINT CADENCE" with the exact `by turn {early_checkpoint_by}` / `{total_turns} turns total` / "FINAL turn is reserved", "RELEVANT FILES" + an allowed path, and "EXACT REQUIRED OUTPUT" + the schema — the elements the S11.3 handoff alone lacked. Removal-sensitive: `test_without_a_budget_the_rotated_prompt_is_not_enriched` proves `turn_budget=None` yields the handoff but NOT the packet.

### G3-2 — Reserved-turn injection reaches the channel + evidence-map corrected — **RESOLVED**
- `turn_budget.reserved_turn_injection`/`reserved_turn_message` (turn_budget.py:269-306) produce the mandatory "emit the checkpoint NOW / do NOT start any new tool call" demand; `loop.py:1637` now passes `extra_turns=tb.reserved_turn_injection(self._turn_budget)` into `run_unit`, which writes it to the worker stdin channel (claude_runner.py:1347). Removal-sensitive: `reserved_turn_injection(None)` → `()`, so every unbudgeted dispatch is byte-for-byte the prior shape.
- Dispatch-level proof is non-vacuous: `ReservedTurnInjectionDispatchTests` asserts `runner.extra_turns_seen[0] == tb.reserved_turn_injection(budget)`; FakeRunner genuinely records `extra_turns` (loop.py test:107, 138-141).
- Evidence-map **R378 is corrected** (`M0-T126-evidence-map.json`): it now states the original row "overclaimed and was corrected," describes the real injection, and honestly hedges "wherever technically enforceable … the --max-turns streaming model cannot hard-block a tool call." This matches the code and design-record §8 (lines 250-253). The residual softness (CLI can't hard-block a tool call in the reserved turn) is exactly what the amendment's "wherever technically enforceable" language permits and is now documented rather than overclaimed; fail-closed exhaustion (R381) remains the backstop.

### G3-3 — D15 runbook fully regenerated — **RESOLVED** (against the register's D15 line)
- §1 digests updated to the values the register cited as live: protected-config `6aef12a9…`→`A1F995016B541B9D…1436` (raw) and LF-normalized `9560f901…`→`4c67875b…e75f`; model-selection `0e2432c0…`→`FCBBF70F…DD2B` (matches register/M0-T113 §5).
- §5 manifest moved outside the tree, and every `--manifest`/rollback reference in §6/§7/§8/§10/§11 now points to `$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` (the certified location the register named).
- §11 regenerated to the current D-024 campaign (branch `control/D-024-fable-codex-loop`, `wt-d024-a1`, `M0-T127.json`); the invented `--run-id run_M0_T063_A1` and retired M0-T063 identities are removed (the only residual "M0-T063" hit is an explanatory prose sentence, not a stale command). Tooth still passes (exit 0, 12/0); the §11 start command retains all five pinned flags.

## Dimension 4 — Delta regression — **PASS**
- `SupervisedLoop.__init__` gains `turn_budget: Any = None` (default None) — additive; every existing caller/test gets None → no enrichment, no injection (confirmed: all pre-existing loop/recovery/runner/launch_seam tests in the 401 pass unchanged). cli.py threads the real budget in one line.
- `with_reorientation` signature change is internal and fully propagated (2 callers, both updated; no test uses the old form).
- The `extra_turns` addition changes the dispatched stdin only on the production budget path; no gate/owner/broker-allowlist/audit/R595/bounded-mode change (design-record §285 confirms, and I verified no such code is touched). No hang risk (runner returns on process exit or expected results).
- **orientation.py:226 Pyright Optional-access → confirmed FALSE POSITIVE:** `if not isinstance(budget, TurnBudget) or not budget.dispatchable:` — the `or` short-circuits, so `.dispatchable` is only evaluated when `budget` is a `TurnBudget`; the early return narrows `budget` to `TurnBudget` before the `with_orientation(...)` call at line 233. Runtime-safe.
- Modularity 0 failures (loop.py 2034/2088, within limit); all 11 changed files inside allowed_paths.

## New findings
- **None blocking.** No new defects in the delta.
- Non-blocking, carried forward unchanged (already known to the orchestrator): (O2) the D9 advancement/selection machinery remains exercised in simulation only, not autonomously wired — defensible under R595/no-live-launch and R388's "simulated"; (O3) the full ~3h13m `golden_run` (R247/R390) is packet-assigned to M0-T127 and must be run at this frozen identity before recert PASS; (O4) the §1 LF-normalized digest `4c67875b…` is a producer-recomputed value I could not independently recompute against the owner-local live config — the two digests the register explicitly named (`A1F99501…`, `FCBBF70F…`) match its cited live values, and orchestrator integration verification corroborates the code side; flagged for the record.

---

**Requested gate result: PASS.** My three prior blocking defects (G3-1/G3-2/G3-3) are resolved with reproducible, removal-sensitive evidence at material identity `2d46fb0`; delta regression is clean. Reproduction commands run: `git diff 2d46fb0 HEAD -- …` (empty), `git diff 767b833 2d46fb0`, `pytest` on the 8 defect packs (401 passed) and the 3 remediation classes (7 passed), `python tools/supervisor_command_doc_check.py` (exit 0), `python tools/modularity_check.py --check` (0 failures). I made no writes outside `.claude/agent-memory/code-reviewer/` and ran no `project_control.py`/git-write/`gh`/supervisor write verb.
---VERBATIM-END---
