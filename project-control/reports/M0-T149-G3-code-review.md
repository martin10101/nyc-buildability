# G3 Independent Code Review — M0-T149

- **Task:** M0-T149 "Constrain supervisor-executed documented test commands to a non-mutating program profile" (M0-T148 G3 LOW-1 follow-up; qualifying evidence AD-093)
- **Reviewed identity:** frozen candidate **ed04c4bb** (integrated at f1e6de26; the six reviewed files are byte-identical at current HEAD 7248aed5 — `git diff --stat ed04c4bb HEAD -- <files>` empty), branch `candidate/D-024-mrl-option-b`
- **Reviewer:** code-reviewer (independent, read-only; producer supervised-loop-fable-worker) — producer ≠ reviewer
- **Directive regime:** D-032:ALL; the directive-compliance-verifier pass is separate and its verdict is recorded in the directive's `verification.json` (not this report)

## Commands run (from repo root, reproducible)

| Command | Result |
|---|---|
| `git show ed04c4bb -- <policy/evidence/tests/reports>` | diff inspected (read-only) |
| `python -m pytest tools/test_agent_supervisor_policy.py -q` | **113 passed, 1 skipped** in 4.14s |
| `python -m pytest tools/test_agent_supervisor_reviewer.py -q` | **123 passed** in 69.90s |
| `python -m ruff check tools/agent_supervisor/evidence.py tools/agent_supervisor/policy.py tools/test_agent_supervisor_reviewer.py tools/test_agent_supervisor_policy.py` | **All checks passed!** |
| `python tools/modularity_check.py --check` | **selected 357 files; failures 0; warnings 13**; exit 0 |
| `python -c "...supervisor_execution_refusal(<probes>)"` | classifier probes (read-only); reproduced F1/F2/F5 below |

(Full supervisor-suite baseline is the orchestrator's separate capture — not run here, per packet.)

## Verification against the six required checks

**1. LOW-1 closed at the EXECUTION channel, fail-visible — CONFIRMED.**
`evidence.py:498-502` calls `supervisor_execution_refusal(shape)` and returns `_failure(command, "non_mutating_profile_refused", …)` **before** `assert_argv_safe` (504) and `self._run` (508). Reviewer spy-runner tests prove a refused command yields `ok:false`, carries the reason code in `detail`, and `self.ran == []` (never executed); `test_a_refusal_is_fail_visible_in_the_transcripts_section` confirms the refusal renders as an `ok:false` entry in `results_section(collect_command_transcripts(...))` alongside an admitted `ok:true` entry. Never silent.

**2. Layered design + bypass hunt — CORE SOUND; one real gap (F1).**
Layering verified in `policy.py:1015-1045`: single-clean-segment gate → `_is_destructive_segment` reuse → closed `SUPERVISOR_EXECUTABLE_TEST_PROGRAMS` via `_program_name` (case/`.exe`/`.cmd`/`.bat`/`.com`/`.ps1` normalized) → interpreter rules (`_refuse_interpreter_target`) → ruff checker tokens. Every bypass named in the packet is correctly handled (all confirmed empirically): `py -m pip` → `python_module_not_allowlisted:pip`; `python3.exe`/`GIT.EXE`/`Python.EXE` normalized; quoted paths stripped by `_strip_quotes`; `ruff check --fix-only` → `mutating_checker_token:--fix-only`; `pytest --co` admitted (correct — read-only); `tools\..\x.py` → `script_outside_repository` (backslash→slash split catches `..`); absolute/`C:`/UNC paths refused; `-c`, dangling `-m`, bare interpreter all refused. `git push origin b` and `git status` both → `program_not_allowlisted:git`. See **F1** for the one real bypass found.

**3. policy.py pure classification + POLICY_VERSION — CONFIRMED.**
`supervisor_execution_refusal` and helpers only tokenize/inspect (call `parse_command`, `_is_destructive_segment`, `_program_name`, string ops); nothing executes. `POLICY_VERSION` bumped `1.0.0`→`1.1.0` (policy.py:57) and is bound into approval digests via `broker.py:118` (`ApprovalRecord.policy_version` default). Digest implication is real and honestly captured in the producer report's recertification note (1.0.0 approvals re-verify under new rules).

**4. Deliberately-unchanged surfaces — CONFIRMED unchanged.**
`git show ed04c4bb` shows policy.py additions are the new profile block + the version line only; evidence.py adds one import + the enforcement block + docstring. `validate_documented_test_commands` (admission) and `_auto_test_command` (worker-AUTO) are absent from the diff — genuinely untouched. The scope argument (admission feeds the schema-lockstep contract outside this task's allowed paths; worker-AUTO is a separate tier-engine trust model) holds.

**5. New tests — STRONG; do not cover F1.**
`SupervisorExecutionProfileTests` (+16) and `NonMutatingExecutionProfileTests` (+6) give real positive shapes, the LOW-1 reproducers, program/module/interpreter/path/destructive negatives, a `CommandShape`-input test, a determinism test, and a genuine **load-bearing mutation test** (`test_the_profile_guard_is_load_bearing`: `mock.patch`-widening the program allowlist to include `git` is the only change that lets `git status` reach execution; guarded run refuses and never runs). All pass (113+1s / 123). Gap: the ruff-token negatives assert only `--fix`/`format`/`--unsafe-fixes`, so **F1 (`--add-noqa`) is untested**, and the "closed set excludes every mutator" closure test covers programs/modules, not ruff argument tokens.

**6. M0-T148 report correction — CONFIRMED honest.**
`project-control/reports/M0-T148-producer-report.md` is corrected in place with an explicit `[Corrected by M0-T149 per G3 LOW-1: …]` annotation stating the original "never git" was convention not guard, and describing the enforced guard. Editing this accepted-task report is authorized (packet objective + allowed_paths); it is an additive annotation, not a silent rewrite.

## Findings

### F1 — MEDIUM — REQUIRED CORRECTION (blocking for acceptance) — `tools/agent_supervisor/policy.py:976-978`
The ruff argument gate `_MUTATING_CHECKER_TOKENS = {"--fix","--fix-only","--unsafe-fixes","format"}` is a **denylist and is incomplete**. `ruff check --add-noqa` rewrites source files in place (adds `# noqa` directives) — functionally the same class as `--fix` — yet is **admitted**. Reproduced at the reviewed content:
```
'' ruff check --add-noqa .
'' python -m ruff check --add-noqa tools
```
(`''` = admitted → would execute and mutate worker-tree source.) This directly violates the task's central "non-mutating" invariant and makes the in-source comment / producer-report claim that the set captures "the tokens that turn the admitted checkers into WRITERS" inaccurate. **Required fix:** add `--add-noqa` to `_MUTATING_CHECKER_TOKENS` and add a red/green test. Trivial and within this task's allowed paths. The correction must be applied and re-verified before acceptance.

### F2 — LOW (fold into C1's consideration) — `policy.py:976-978`, ruff branch
Two further ruff writes are admitted: `ruff check --output-file out.txt .` (and `-o`) writes a file to the worktree, and `ruff clean` deletes the ruff cache. Both returned `''`. Note the internal inconsistency: `-o`/`--output` is already treated as unsafe-because-it-writes for git (`UNSAFE_GIT_SUBCOMMAND_FLAGS`, policy.py:468) but is admitted for ruff. Recommend the C1 fix also cover `--output-file`/`-o` (and consider `ruff clean`).

### F3 — LOW (report accuracy; gate still passes) — producer report §"Self-check"
The report claims modularity `warnings 12 … identical warning set … no new warning for policy.py`. At the reviewed content the check reports **failures 0 (gate passes, exit 0)** but **13 warnings**, including `symbol_ceiling: tools/agent_supervisor/policy.py` and `review_signal: tools/agent_supervisor/evidence.py`. The change added 7 top-level symbols to policy.py (105→112 by AST count), which plausibly tripped/worsened the `symbol_ceiling` advisory. Non-blocking (advisory, failures 0), but the report's "identical 12-warning set / no new policy.py warning" is not reproducible; the producer should acknowledge the added symbols with a one-line cohesion note.

### F4 — LOW / informational (by-design, disclosed) — `SUPERVISOR_EXECUTABLE_TEST_PROGRAMS`
The closed program allowlist refuses legitimate non-python test runners present in at least one **accepted** packet (M0-T139: `powershell.exe -NoProfile … run_ps_tests.ps1` → `program_not_allowlisted:powershell`). These are refused **fail-visibly**, not executed; the producer disclosed this residual. No action required, but the orchestrator should note that activating the supervisor against such a packet will refuse those commands until the allowlist is extended by a reviewed diff.

### F5 — LOW / informational — `_refuse_interpreter_target` (policy.py:990-1012)
The first non-dash token is treated as the script target, so interpreter option-with-argument forms (`python -W ignore -m pytest …`) are falsely refused (`unrecognized_interpreter_target:ignore`, reproduced). No documented command uses such forms today, so no real false refusal; fail-closed and fail-visible. Noted as a limitation.

### F6 — LOW / informational (within disclosed residual)
A repo-relative `argv[0]` whose basename matches the allowlist (e.g. `./python`, `tools/python`) passes `_program_name` normalization and executes as a repo binary. This is inside the producer-disclosed "repo content trust" residual (an admitted `python tools/<script>.py` already runs arbitrary repo code); not a new surface.

## Governance / modularity
Qualifying evidence AD-093 (demonstrated security risk) cited in packet + commit; directive D-032:ALL bound. `modularity_check --check` failures 0, exit 0 (advisory warnings only; see F3). Pure-ASCII, ruff clean. Reviewer read-only discipline honored (a file-write probe was correctly blocked by the guard; redone without writes).

## Disposition
Core deliverable is correct and well-tested: the LOW-1 execution-channel gap is closed, refusals are fail-visible and pre-execution, the guard is proven load-bearing, POLICY_VERSION/digest handled, unchanged surfaces genuinely unchanged, and the M0-T148 correction is honest. One reproducible defect (F1) lets a source-mutating ruff shape through the very "non-mutating" profile this task exists to build; it is narrow, low-impact (shadow-only channel, orchestrator-authored packets, adds comments), and trivially fixable, so it is recorded as a **required correction blocking acceptance** rather than a rework FAIL, per this repo's PASS-with-required-corrections semantics.

**Required correction (blocking for acceptance):**
- **C1** — Add `--add-noqa` to `_MUTATING_CHECKER_TOKENS` (F1), extend to `--output-file`/`-o` and consider `ruff clean` (F2), and add a red/green test asserting `ruff check --add-noqa` is refused. Re-verify (`pytest` both suites + ruff) before the orchestrator accepts.

**Recommended (non-blocking):** annotate the modularity warning note (F3); no action needed on F4-F6 (disclosed/informational).

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the code-reviewer agent-return channel (2026-09-07 gate wave; transport framing removed, HTML entities decoded, content unaltered). C1 is BLOCKING for acceptance per the gate-verdict semantics (.claude/rules/project-control.md).*
