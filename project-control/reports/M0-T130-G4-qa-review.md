# M0-T130 G4 QA review (VERBATIM reviewer return; saved unmodified by the orchestrator per the report-preservation rule)

Reviewer: independent unnamed qa-engineer roster spawn (read-only). Reviewed identity
commit `20bfa449` (blobs verified). Verdict: FAIL (C1 blocking High / C2 blocking
Medium — the same modularity findings as G3, remediated at `fa13cf8b` BEFORE this
record landed; C3/C4 non-blocking). Recorded by orchestrator 2026-08-31.

---VERBATIM-BEGIN---
# G4 QA Gate Report — M0-T130 (reserved-turn delivery defect fix)

**Task:** M0-T130 — deferred reserved-turn injection at genuine idle + robust unit-completion latch
**Reviewed identity:** commit `20bfa449` (blobs verified: `claude_runner.py` = `5dd12f72`, `test_agent_supervisor_runner.py` = `ef2eeeb7`)
**Checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (working-tree files `git hash-object`-confirmed byte-identical to the committed blobs)
**Reviewer:** qa-engineer (read-only; no repo writes, no ledger/git mutations)
**Directive regime:** in-regime (`directive_refs: D-024 ALL`); DCV requirement-map is the `directive-compliance-verifier`'s pass, not mine.

---

## Duty 1 — Runner pack

Command (in ctl24, against the reviewed blob):
```
python -m pytest tools/test_agent_supervisor_runner.py -q
```
Output: `78 passed in 11.20s`. **CONFIRMED — 78 passed.**

## Duty 2 — Test quality

**(a) Fidelity of the `absorbs_early_second_prompt` fake vs the journey-3 measurement.** Faithful. The journey-3 report (s2) records: the reserved prompt was *absorbed into the first in-flight turn* (queue op `remove`/`absorbed_mid_turn`), the CLI emitted **one** terminal `result` with **no** checkpoint, and the two written prompts collapsed so `results_seen(1) < expected_results(2)` -> the session stayed open and rode the 900 s wall. The fake encodes exactly that shape: a reader thread collects `user` prompts for a 0.8 s window; if `early >= 2` it emits **one** merged `result` (`"merged turn, working phase truncated; no checkpoint"`) and then blocks in `reader.join()` (session left open — the wall-ride shape). With deferred delivery the fake sees only the single launch prompt (`early == 1`), answers with the checkpoint, and the reserved demand is skipped as moot. This reproduces both symptoms (truncation + non-terminating accounting) without a live provider.

**(b) Removal-sensitivity of the four paths** — each names a distinct mechanism whose revert I traced to a failing assertion:

| Path | Test | Mechanism whose revert fails it | Failure under revert |
|---|---|---|---|
| absorption-impossible | `ReservedTurnDeliveryTests::test_an_absorbing_cli_never_sees_an_early_second_prompt` | deferred write (`pending_turns = list(extra_turns)`; NOT written at launch) | launch-time writes -> fake sees 2 early prompts -> merged no-checkpoint result -> wall-ride at the 15 s test timeout -> `result.ok` False + `elapsed < 10.0` fails. Producer's red-on-mutant demonstrates this exact case (1 failed/3 passed). |
| skip-when-decided | `SessionCloseTests::test_a_checkpoint_in_the_first_result_skips_the_reserved_turn` | the `if checkpoint_question_decided(events): pending_turns.clear()` branch | inject-always -> reserved turn written -> `session_open_two_turns` emits a 2nd result -> `len(results)==1` fails. |
| injection-when-missing | `ReservedTurnDeliveryTests::test_reserved_turn_is_injected_when_the_first_result_lacks_one` | the `write(user_message(pending_turns.pop(0)))` injection | drop the injection -> only the no-checkpoint result 1 -> `missing_checkpoint` (or wall-ride) -> `result.ok`/`len(results)==2` fails. |
| fast-honest-failure | `ReservedTurnDeliveryTests::test_no_checkpoint_after_the_reserved_turn_fails_fast` | robust latch `results_seen >= expected_results and not pending_turns` (R422) | require-checkpoint-to-latch mutation -> no-checkpoint outcome never latches -> wall-ride at 60 s -> `elapsed < 30.0` + `not timed_out` fail. |

I confirmed no test would stay green under its named revert. **Caveat:** the producer executed a live red-on-mutant proof only for the **first** mutant (launch-time writes). The other three are verified by code-trace, not by an executed mutant — sound, but only path 1 has recorded red-on-mutant evidence. The `never_checkpoint` path's removal-sensitivity partially overlaps `no_checkpoint_then_checkpoint` for the "dropped injection" mutation; its **unique** guard is the fast-failure *timing* (a mutation that made completion require a checkpoint fails only here). Plus `test_checkpoint_question_decided_vocabulary` pins the helper (no-candidate -> inject; valid/conflicting -> skip) and the pre-existing `test_the_wall_watchdog_still_owns_the_runaway_unit` guards the watchdog. Coverage is adequate and removal-sensitive.

**(c) Timing robustness.** Low flake risk. The 0.8 s sleep gates only the `early` count; the healthy path's `elapsed` is ~0.8 s + overhead, far under the `< 10.0` bound, and the mutant wall-ride is ~15 s — a wide two-sided margin. `never_checkpoint`'s `< 30.0` (timeout 60 s) is comfortable. One low-probability tail: the absorption test's `len(results) == 1` assumes the fake's reader consumes the launch prompt within 0.8 s (so `early == 1`); if a pathologically loaded machine failed to deliver/read one stdin line in 0.8 s, `early == 0` would let the `while` loop emit a 2nd result (drained post-completion into `raw_events`) and `len==1` would fail. The prompt is written at launch before the fake's sleep even elapses, so this is very unlikely, but see C4.

## Duty 3 — Deliberate test-semantics change

`git show 20bfa449 -- tools/test_agent_supervisor_runner.py` confirms **exactly one** existing test was modified: `test_every_extra_turn_gets_its_terminal_result_before_the_close` -> renamed to `test_a_checkpoint_in_the_first_result_skips_the_reserved_turn`, asserting `len(results) == 1` (was `== 2`). The only `-def test_` in the diff is that rename; **no test was deleted.** The lost invariant ("a written extra turn gets its terminal result before close") is preserved by the new `no_checkpoint_then_checkpoint` path (2 results, valid checkpoint). **CONFIRMED.**

## Duty 4 — Baseline reconciliation

Independently reran the whole supervisor suite in ctl24:
```
python -m pytest tools/ -k "agent_supervisor" -q
-> 3039 passed, 2 skipped, 560 deselected in 267.43s
```
Matches the claimed `3039 passed / 2 skipped`. Arithmetic from the diff: five `+def test_` (4 genuinely new + 1 rename target) and one `-def test_` (the rename source) = **net +4 methods, 1 repurposed (name-only), 0 deletions**; runner pack 74 -> 78. `3035 baseline + 4 = 3039`. The commit touched only `test_agent_supervisor_runner.py` among test files (modified, not removed). **CONFIRMED.**

## Duty 5 — Honest residuals

Adequate, with one wording overstatement. The unmeasured max-turns-semantics disclosure (report s4.1) is present and correctly labels the cumulative-vs-per-run question as unmeasured, deferred to the next live journey. The claim "**either semantic strictly improves on the absorbed shape**" is **sound on its strongest reading**: because the reserved turn is now injected only at genuine idle (after result 1), the working phase can no longer be truncated — an *unconditional* improvement over the absorbed shape, where the worker got "your turns are spent" ~4 real turns in and did discovery only. In the worst cumulative case (CLI refuses a post-exhaustion injected turn), *if* the CLI still emits a terminal `result` for the refusal -> fast honest failure; *if* it silently drops the prompt with no result -> a wall-ride of the **same** duration as today's defect but **with the working phase completed** — i.e. no regression on any axis. So "strictly improves" holds. The only overstatement is the categorical "not a hang": the hang tail genuinely exists if a refused turn yields no terminal result (see C3, non-blocking).

## Duty 6 — Missed failure modes (all fail closed; none blocking)

- **Result then more events before the injection write:** none — the injection `write(...)` is synchronous inside the `result` branch; there is no program-order gap. Not a defect.
- **Duplicate result events:** the stream parser dedups by `uuid`/`message_id` (`_seen_ids`, line 509-514), so same-uuid duplicates never inflate `results_seen`. A *distinct-uuid* second result for one turn is abnormal CLI behavior, pre-existing, and fails closed (early latch -> honest `missing_checkpoint`, not a wrong success).
- **Checkpoint between result 1 and injection write:** impossible in-process (synchronous). A checkpoint arriving *before* result 1 in-stream is seen by `checkpoint_question_decided(events)`. A *late* checkpoint after result 1 (abnormal ordering) -> an unnecessary reserved turn, and if the injected turn adds a distinct candidate -> `multiple_distinct`/`conflicting_duplicate` -> refused (fails closed). Low severity, abnormal-stream-only.
- **stdin closed early:** `write()` swallows `BrokenPipeError`. If the process **exited**, stdout EOFs -> loop ends cleanly (no hang). If the process is **alive-but-stdin-closed**, the injected prompt is lost, no result 2, `expected_results` unmet -> wall-ride correctly owned by the watchdog. Tail risk, not a regression.
- **control_request during the injected turn:** handled by the unchanged control loop; the injected turn is an ordinary turn. Fine.

The core fix logic (deferred `pending_turns`, decidedness gate keyed only to `missing_checkpoint`, latch requiring `results_seen >= expected_results and not pending_turns`) is correct. Production `extra_turns` is at most one element (`turn_budget.reserved_turn_injection` -> `()` or a single message; `loop.py:1635-1637`), so the single-pending path is what ships; the multi-pending generality is handled correctly (one pop per idle, gated each time).

---

## Blocking finding outside the six duties — modularity gate is RED at the reviewed identity

The run-quality-gate remit requires a passing `python tools/modularity_check.py --check` for any task touching handwritten production source. It **FAILS**:
```
python tools/modularity_check.py --check     -> EXIT=1
selected 335 files; failures 1; warnings 11
  FAIL baseline_growth: tools/agent_supervisor/claude_runner.py (1400) -
       grandfathered oversized file grew materially without a reviewed exception
```
Root cause (independently computed with the check's own `source_lines` counting): baseline records `claude_runner.py` = **1258**; `material_growth_limit(1258) = 1258 + max(50, 125) = 1383`. The **parent** `81d5a9ba` sat at **exactly 1383** (`1383 > 1383` is False -> passing). M0-T130 (`20bfa449`) added **17 SLOC -> 1400 > 1383** -> FAIL (`if sloc > limit and exception is None`, line 422). No exception for this path exists in `tools/modularity_exceptions.json`. The commit did not (and per `allowed_paths` could not) touch `modularity_baseline.json`. **M0-T130 introduced this CI-enforced, fail-closed failure** (CLAUDE.md item 16; supervisor-freeze s4). It is not resolvable within the packet's scope. The counting is pure-Python and deterministic across 3.11/3.12, so CI reproduces this result.

The producer report **s3 falsely claims** `"modularity_check --check: PASS (0 failures); ... +~45 SLOC"`. Both are wrong: the check fails, and the effective SLOC delta over the parent is **+17**, not +45. This is a reproducible defect plus an evidence-integrity failure (Permanent Principle 2).

Other producer self-checks I could reproduce hold: `ruff check` on both touched files -> `All checks passed!`; runner pack 78; whole suite 3039/2. The "command-doc tooth exit 0" claim was not independently verified (outside my duties) and is not blocking.

---

## Required corrections

- **C1 — BLOCKING (High).** Resolve the modularity failure. `tools/modularity_check.py --check` exits 1 (`claude_runner.py` 1400 > limit 1383), introduced by this commit. Remedy requires an authorized action outside M0-T130's current scope: a reviewed path-exact entry in `tools/modularity_exceptions.json`, an approved baseline regeneration (D-017-R110), OR (modularity-preferred, given a 1400-SLOC grandfathered file) extract the reserved-turn delivery / `checkpoint_question_decided` logic into a focused module so `claude_runner.py` does not grow. The gate cannot be certified until `--check` exits 0.
- **C2 — BLOCKING (Medium).** Correct producer report s3: it must reflect the actual modularity result (FAIL, with the chosen remedy) and the real SLOC figures (baseline 1258, parent 1383, head 1400, limit 1383), not "PASS (0 failures); +~45 SLOC."
- **C3 — non-blocking (Low).** Tighten residual s4.1 wording: the guaranteed property is "working phase no longer truncated + no regression vs the current wall-ride," not the categorical "fast honest failure, not a hang" — a hang tail remains if a refused post-exhaustion injected turn yields no terminal result.
- **C4 — non-blocking (Low, advisory).** `test_an_absorbing_cli_never_sees_an_early_second_prompt`'s `len(results) == 1` depends on the fake's reader consuming the launch prompt within the 0.8 s window; consider asserting the outcome shape (one checkpoint, no wall) rather than an exact result count, or widening the window, to remove the low-probability slow-machine flake.

The core engineering (deferred injection, decidedness gate, robust latch) and its test coverage pass my QA assessment; the FAIL is driven by the introduced red modularity gate (C1) and the inaccurate compliance evidence (C2), both reproducible.

**VERDICT: FAIL**
---VERBATIM-END---
