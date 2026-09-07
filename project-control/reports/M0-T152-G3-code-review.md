# GATE REPORT — M0-T152 (D-033 T-A: supervisor gate-wave engine)

**Gate:** G3 (independent code review — correctness, tests, maintainability)
**Reviewer:** code-reviewer (read-only, independent; not the producer)
**Reviewed identity:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t152`, branch `task/M0-T152-gate-wave-engine`, HEAD `cc25bdc15e4e982259a71f6903f370e6d1d8adf9`
**Date:** 2026-09-07

## 1. Identity verified
- `git rev-parse HEAD` = `cc25bdc15e4e982259a71f6903f370e6d1d8adf9` — matches the frozen candidate.
- Tree clean (`git status --porcelain` empty); branch correct.
- Range `0e067b6a..cc25bdc1` contains four commits (`26c973ea`, `382abf6d`, `09fdea16`, `cc25bdc1`) — one more than the three named in the packet: `382abf6d` is an orchestrator control-plane **packet-copy sync** (see §2).

## 2. Diff boundary
`git diff 0e067b6a..cc25bdc1 --stat` touches 7 files. Six are in `allowed_paths` (`gate_wave.py`, `loop.py`, `cli.py`, `.claude/rules/supervisor-freeze.md`, `test_agent_supervisor_gate_wave.py`, `test_agent_supervisor_loop.py`, plus the producer report). The one path **outside** `allowed_paths` is `project-control/tasks/M0-T152.json`, changed **only** by control-plane commit `382abf6d` (adds the DL-2 checkpoint-envelope note to `notes[]`). That is the orchestrator's own control-plane record, not a producer code edit — **benign, not a scope violation**. No stray production/source path. `cli.py` also carries two behavior-neutral kwarg re-wraps (`model_chain`/`model_available`, `worker_turnover`/`guardrail_bridge` collapsed onto single lines); byte-neutral at runtime.

## 3. Per-scenario findings (against real code)

- **S1 OFF==today / F6** — PASS. `assert_wave_enabled` (gate_wave.py:206-214) is the single load-bearing switch; `maybe_run_post_complete_stage` returns None with `owner_enabled=False` or non-COMPLETE (gate_wave.py:1025-1028). CLI seam `run_with_post_complete_stage` (gate_wave.py:1086-1092) returns the loop's own `to_dict()` object unmodified when the flag is absent — test `test_flag_off_is_exactly_the_loop_run_and_touches_nothing` asserts `assertIs(result, loop.returned[0])` (real identity, not equality) with MustNotRun tripwires. F6 by-name refusal in `managed_wave_start_gate` (gate_wave.py:217-251), sealed in the hash-chained audit log; LT-01 pin present (see S7).

- **S2 dispatch/digest binding, forgery-resistant** — PASS. Reviewer identity resolved from the **control-plane packet** roster ∩ controller constant `DEFAULT_GATE_REVIEWERS` (gate_wave.py:575-581, 957-958) — worker-uninfluencable; producer from `packet["producer_agent"]`. Per-dispatch unique path + `dispatch_digest` (plan_dispatch:385-393); `_assert_reviewer_separated` (328-360) and `_assert_verdict_bound` (469-486) fire on the live path via `plan_dispatch` and `bind_verdict`; `write_verdict_report` refuses a pre-existing planted file at the unique path (509-514); `verdict_digest` re-derived (494-499). Reviewer==producer, foreign-task, unsealed, tamper, and planted-path all fail closed. *Minor observation D-2 below.*

- **S3 allow-set (F1)** — PASS. `CONTROL_PLANE_ALLOW_SET={"gate","submit"}` (73), per-subcommand arg allow-lists (77-81), current-queue-task pin (623-630). `ControlPlaneRecorder.build_argv` is the sole path to `project_control.py`; 11 out-of-scope subcommands + out-of-queue id + unknown-arg + flag-like-value all refused (tests 572-595).

- **S4 immunization (F3)** — PASS (MED scope). `WORKER_AUTHORED_DATA_CLAUSE` verbatim in all four `GATE_CONTRACTS` (test 700-705); contract redacted via `redact_structure` (426); packet pre-supplying its own contract refused (420-424); `emit PASS` injection negative binds the reviewer's actual REVISE→FAIL (test 730-740).

- **S5 G2 capture** — PASS. `capture_g2` marks FAIL on non-ok/nonzero-exit/timeout/unrunnable (726-753), timeout never success; recorded with reserved `orchestrator` label via `record_self_check`; failing G2 → `REWORK` **before** any independent dispatch (931-936). G2 cannot satisfy an independent gate (recorded as G2; project_control.py gate-class rules untouched — that file is not in the diff).

- **S6 freeze-rule amendment** — PASS. Applied paragraph `.claude/rules/supervisor-freeze.md:43-51` is **byte-identical** to the producer report §1 diff, and its quoted R007 clause matches `D-033-R007.text` in `requirements.json` verbatim. Placed after the D-024 recognition, mirroring its wording; diff is `+10` lines only, nothing else changed.

- **S7 modularity + regression** — PASS. `gate_wave.py` = **915 SLOC** (checker rule: non-blank, non-`#`), above JUSTIFY-750, **below HARD-1000**; §4 of the report records the required cohesion justification. `loop.py` diff is **empty** (byte-identical to base — the LoopConfig wave field added in `26c973ea` was fully removed in `09fdea16`); `git grep` finds **zero** wave/managed references in loop.py; **LT-01** `test_the_managed_wave_switch_never_reaches_loop_config` asserts the field is absent AND that passing it raises `TypeError` (loop test 294-312). `cli.py` coupling = the 4 named touch points only (import :227, seam call :2937-2941 replacing `loop.run(...).to_dict()`, F6 gate :2960, switch registration :3372); `gate_wave → loop` is one-way, constant-only (`MODE_LIMITED_AUTO`).

## 4. Mutation-test verification table (each disables exactly the line it names; guard proven load-bearing)

| Test (line) | Mocks | Proves | Load-bearing? |
|---|---|---|---|
| `test_MUTATION_removing_the_switch_check…` (291) | `assert_wave_enabled`→no-op | OFF then runs a full wave (WAVE_COMPLETE, reviewer.calls>0, records>0) | YES |
| `…removing_identity_separation_admits_the_forgery` (532) | `_assert_reviewer_separated`→no-op | reviewer==producer dispatch succeeds | YES |
| `…removing_the_binding_check_admits_a_foreign_verdict` (540) | `_assert_verdict_bound`→no-op | a M0-T999 record binds to the M0-T152 dispatch | YES |
| `…removing_the_allow_set_lets_accept_through` (626) | `_assert_subcommand_allowed`→no-op | an `accept` argv builds | YES |
| `…removing_the_queue_bound_lets_another_task_through` (635) | `_assert_current_queue_task`→no-op | `gate M0-T999` argv builds | YES |
| `…removing_the_reassert_lets_an_ungated_flag_enable` (922) | `managed_wave_start_gate`→None | ungated flag records the enable + runs the launch | YES |

Each has a matching non-mutated red/green partner (421, 448, 572/583, 910, 260). All six are genuine, not decorative.

## 5. Test adequacy / documented commands
- 63 gate-wave tests + 127 loop tests (method counts confirmed by grep). Coverage includes fail-closed park/rework paths, G6 pre-dispatch park, UNAVAILABLE→park, gate-class drift guard, and full ON-path end-to-end.
- Captured evidence `M0-T152-documented-commands-cc25bdc1.txt`: pytest gate_wave 63 passed / loop 127 passed / ruff clean / modularity — **all EXIT 0**.
- I **independently re-ran** `python tools/modularity_check.py --check` (read-only): `selected 358 files; failures 0; warnings 13`, EXIT 0, with `gate_wave.py … above the justification threshold; record a cohesion justification in review` present. Confirms S7 mechanically.

## 6. Defects / observations (severity-ranked; none blocking)
- **D-1 (LOW / evidence fidelity):** The modularity section of the captured artifact `project-control/reports/M0-T152-documented-commands-cc25bdc1.txt` is **filtered/truncated** — it shows only 5 of the 13 real warnings, omits the `selected … failures … warnings` summary line, and (notably) omits `gate_wave.py`'s own review_signal warning (which sorts first among `agent_supervisor/`). The true tool output is 13 warnings / 0 failures / EXIT 0, which I reproduced. Recommend the orchestrator re-capture verbatim tool output for a clean audit trail. Does not affect the gate result (command genuinely exits 0).
- **D-2 (LOW / maintainability, T-A scaffold):** `WaveDeps.worker_worktree` is threaded in (post_complete_stage:1058) but **never read** by `run_gate_wave`; `admit_verdict_file(worker_worktree=…)` and `verify_verdict_report` are unit-tested but **not invoked on the live serial wave path** (the live verdict originates from the sealed in-process `ReviewRecord`, not a file). Live forgery-resistance is intact via the guards on the live path (§S2). Recommend T-B either wire the file read-back verification into the live flow or document these as intentional defense-in-depth API surface.
- **D-3 (INFO):** Producer report §5 calls the 13 warnings "pre-existing"; one (`gate_wave.py`) is new. Immaterial.

## 7. Conclusion
Identity confirmed and clean; diff within scope (only the benign orchestrator task-JSON sync sits outside `allowed_paths`); all seven acceptance scenarios reproduce against the real code; all six enforcement mutations are load-bearing with red/green partners; loop.py is byte-identical with the LoopConfig field removed and TypeError-pinned; the module is fail-closed throughout with one-way coupling; all four documented commands exit 0 (modularity independently reproduced). The three observations are advisory, not blocking corrections — the feature is correct and complete for the T-A (DEFAULT-OFF scaffold) scope, and D-033-R005 (nothing activates) holds at the code level (the wave records gates only; never accept/submit-for-acceptance/queue-advance/commit).

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the code-reviewer agent-return channel (2026-09-07 overnight gate wave, task notification ab1eac4180957e057; leading corroboration sentences removed as transport framing, HTML entity-encoding of `>` decoded in the mutation table, content unaltered).*
