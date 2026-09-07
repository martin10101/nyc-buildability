# M0-T149 producer report - enforced non-mutating supervisor-execution profile

Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t149`, branch
`task/M0-T149-command-profile`, base `bb71b2ef`. Producer edits only; the
orchestrator commits and integrates. Qualifying evidence (supervisor-freeze
S2/S3): **AD-093 demonstrated security risk** - M0-T148 G3 LOW-1
(`project-control/reports/M0-T148-G3-code-review.md`), defense-in-depth gap at
accepted commit 53d642a1. Directive binding: the task packet carries
`directive_refs` D-032:ALL.

## The defect (G3 LOW-1 recap)

M0-T148 made `documented_test_commands` an ACTIVE supervisor-side execution
surface (`evidence.EvidenceCollector.run_command`). The admission validator
`policy.validate_documented_test_commands` deliberately admits ANY single
clean metacharacter-free segment - including mutating shapes such as
`git push origin b` or `rm -rf tools` - because the field also serves
worker-command shape matching. Until this task, the ONLY thing preventing such
a command from being EXECUTED at review time was that the orchestrator authors
the task packet: convention, not guard, and the M0-T148 report's "never git"
claim rested on it.

## What changed, per file

### tools/agent_supervisor/policy.py (the profile - inspection-only)

- `POLICY_VERSION` bumped `1.0.0` -> `1.1.0` (a rule changed; the version is
  bound into approval digests, and no test pins the literal).
- New closed constants, each with in-source rationale:
  - `SUPERVISOR_EXECUTABLE_TEST_PROGRAMS = frozenset({"python", "python3",
    "py", "pytest", "ruff"})` - grounded in every packet actually written
    (all documented commands in `project-control/tasks/*.json` are
    python-launched suites/checkers, plus the bare console-script forms of the
    same runners). **git is deliberately absent**: collector git facts flow
    through `assert_read_only_git`, so a documented command never needs to run
    git, and the M0-T148 "never git" property becomes machine-enforced.
  - `SUPERVISOR_EXECUTABLE_PYTHON_MODULES = frozenset({"pytest", "ruff",
    "unittest"})` - a closed `-m` set; an open `-m` would readmit
    `python -m pip install`.
  - `_MUTATING_CHECKER_TOKENS` - the tokens that turn the admitted checkers
    into writers. (Superseded by the Rework section below, which adds
    `--add-noqa`, `--output-file`, `-o`, and `clean`; the initial submission
    carried only `--fix`/`--fix-only`/`--unsafe-fixes`/`format`.)
- `supervisor_execution_refusal(command | CommandShape) -> str`: deterministic,
  fail-closed, returns `""` to admit or a reason code to refuse. Layered:
  (1) one clean metacharacter-free segment under the classifier's own
  `parse_command` (`unrunnable_command`); (2) `_is_destructive_segment` reuse
  from the tier engine (`destructive_segment:*` - catches `rm -rf`,
  `del /s`, destructive git shapes even if the allowlist is ever widened);
  (3) closed program allowlist via `_program_name` (case/`.exe`-suffix
  normalized: `GIT.EXE` -> `git`; `program_not_allowlisted:*`); (4) for
  interpreter launchers: refuse inline code (`-c` -> `inline_python_code`),
  non-allowlisted `-m` modules (`python_module_not_allowlisted:*`),
  non-`.py`/odd targets (`unrecognized_interpreter_target:*`), absolute or
  `..`-escaping script paths (`script_outside_repository:*`), and bare
  interpreters (`interpreter_without_test_target`); (5) mutating checker
  tokens (`mutating_checker_token:*`). Nothing in policy.py executes anything;
  the module stays pure classification.

### tools/agent_supervisor/evidence.py (the enforcement point)

- `supervisor_execution_refusal` added to the existing `from .policy import
  (...)` (no new dependency).
- `run_command` applies the profile after its existing single-clean-segment
  precheck and BEFORE `assert_argv_safe`/execution: a refusal returns
  `_failure(command, "non_mutating_profile_refused", ...detail carries the
  reason code...)` - fail-visible in the `command_transcripts` section as an
  `ok: false` entry, never executed, never silently dropped. The docstring now
  states the enforced profile instead of implying admission equals execution
  authority.

### project-control/reports/M0-T148-producer-report.md (ordered correction)

- The "Invariants held" bullet's "never git" wording is corrected in place
  with an explicit `[Corrected by M0-T149 ...]` annotation: it now states that
  the original claim was convention, and describes the enforced guard that
  makes never-git/never-mutating machine-enforced at the execution channel.

## Surfaces deliberately NOT changed (scope discipline)

- `validate_documented_test_commands` (admission) is untouched: it feeds the
  schema-lockstep contract (`schemas/task_packet_commands.schema.json`,
  asserted by `tools/test_agent_supervisor_command_authority.py`, outside this
  task's allowed paths) and the worker-command shape matching. Tightening
  admission would refuse whole runs for historical packet shapes; LOW-1 names
  the execution channel, and that is where the guard now sits.
- `_auto_test_command` (worker-proposed command classification) is untouched:
  constraining worker AUTO through the same profile is a behavior change to
  the tier engine that the packet did not authorize (supervisor-freeze S1:
  no changes beyond the qualifying evidence). Its trust model - orchestrator
  packet authorship plus the `_hard_deny` layer that runs first - is
  unchanged and now documented in `supervisor_execution_refusal`'s docstring
  as an explicitly separate surface. If a reviewer judges that surface to need
  the same profile, that is a new task with its own evidence.

## Tests added (positive AND negative, per the packet)

tools/test_agent_supervisor_policy.py - `SupervisorExecutionProfileTests`
(16 tests):
- positive: every real documented shape this repository writes (pytest/ruff
  module forms, `tools/*.py --check` scripts, bare `pytest -q`/`ruff check .`,
  `python -m unittest discover`), CommandShape input form, determinism.
- negative: `git push origin b` (the LOW-1 reproducer) and read-only
  `git status` both `program_not_allowlisted:git`; `rm -rf tools`,
  `del /s tools`, `rm tools/x.py` destructive; npm/pip/gh/powershell/node/
  curl/make refused; `GIT.EXE`/`Python.EXE` normalization; `python -m pip
  install`, `python -m venv`, dangling `-m`; `python -c`; absolute and
  `..`-escaping script paths; bare/targetless interpreter; `--fix`/`format`/
  `--unsafe-fixes`; empty/chained/substitution shapes stay
  `unrunnable_command`; closure test asserting the allowlists are frozensets
  excluding every delete verb and known mutator/network program.

tools/test_agent_supervisor_reviewer.py - `NonMutatingExecutionProfileTests`
(6 tests):
- spy-runner proofs that `git push origin b`, `rm -rf tools`, and
  `python -m pip install requests` are refused with
  `non_mutating_profile_refused` (+ the specific reason in `detail`) and the
  runner is NEVER invoked; an admitted `python -m pytest tools/x.py -q` still
  executes exactly once; a refusal is fail-visible in
  `results_section(collect_command_transcripts(...))` alongside an ok entry;
  and a load-bearing mutation test - `mock.patch`-widening
  `SUPERVISOR_EXECUTABLE_TEST_PROGRAMS` to include `git` is the ONLY change
  needed for `git status` to reach execution, proving the allowlist (not an
  accident of plumbing) is what blocks it.

## Self-check commands and results (real outputs, final content state)

- `python -m pytest tools/test_agent_supervisor_policy.py -q` ->
  `113 passed, 1 skipped` (was 97 passed, 1 skipped; +16 new).
- `python -m pytest tools/test_agent_supervisor_reviewer.py -q` ->
  `123 passed` (was 117; +6 new).
- `python -m ruff check tools/agent_supervisor/evidence.py
  tools/agent_supervisor/policy.py tools/test_agent_supervisor_reviewer.py
  tools/test_agent_supervisor_policy.py` -> `All checks passed!`
- `python tools/modularity_check.py --check` -> `selected 357 files;
  failures 0; warnings 12` - identical warning set to the pre-edit baseline
  run captured at the start of this unit (all 12 pre-existing; policy.py
  stays within its material-growth limit, no exception added or renewed).

## Line deltas (physical lines; git commits are the orchestrator's)

- policy.py: 2019 -> 2124 (+105: version comment, profile constants with
  rationale, three functions). Baseline SLOC 1577; the modularity gate passed
  with failures 0 and no new warning for policy.py.
- evidence.py: 760 -> 774 (+14: one import, the enforcement block, docstring).
- test_agent_supervisor_policy.py: +117 (test files excluded from modularity
  SLOC).
- test_agent_supervisor_reviewer.py: +76.

## Invariants held

- policy.py still executes nothing; the profile is pure classification.
- `run_command`'s existing behavior for admitted commands is unchanged (same
  transcript shape, digest binding, timeout and nonzero-exit semantics; all
  pre-existing S3 tests pass unmodified).
- Codex output schema, decision enum, REVIEW_INSTRUCTIONS: untouched.
- Pure-ASCII source in all four edited files (ruff clean; no non-ASCII
  introduced).
- Reviewer read-only discipline and orchestrator-only git: untouched.

## Recertification note

This change modifies the certified controller subtree (policy + evidence).
Per the D-032 convergence record section 7, the next launch after closure
requires R247 recertification + source_binding re-pin + controller reinstall
for the changed subtree, and a FRESH run-id. The POLICY_VERSION bump
additionally invalidates approval digests granted under 1.0.0 (strict
direction: previously granted approvals re-verify under the new rules).

## Deviations / limitations (honest residuals)

- The profile constrains PROGRAMS and shapes, not repository content: an
  admitted `python tools/<script>.py` runs arbitrary REPO code. That residual
  is the packet/content trust model (orchestrator authorship + gates) and is
  out of scope for a program profile; it is stated here rather than papered
  over.
- A future supervisor-run task documenting non-python runners (e.g. the
  M0-T139-style `powershell.exe ... run_ps_tests.ps1` shape, or `npm test`)
  will have those commands refused fail-visibly in `command_transcripts`
  rather than executed; the reviewer sees the refusal, and extending the
  closed allowlist is a reviewed one-line diff under the standard gates.
- `format` in `_MUTATING_CHECKER_TOKENS` matches the bare token anywhere in a
  ruff invocation (a path literally named `format` would be refused); the
  fail-closed cost is accepted for simplicity and documented here. (`clean` is
  added on the same basis - see Rework below.)

## Rework (G3 C1 + G5 MED-1 / MED-2, 2026-09-07)

Independent G3 (`M0-T149-G3-code-review.md`, F1/F2/F3/F5) and G5
(`M0-T149-G5-security.md`, MED-1/MED-2/LOW-3, verdict FAIL) found reproducible
bypasses of the "non-mutating" property this task exists to enforce. This
bounded rework closes exactly that cluster; no other behavior changed.

### What changed and why

1. `_MUTATING_CHECKER_TOKENS` completed (G3-F1/F2, G5-MED-1). The denylist of
   ruff argument tokens was incomplete, so source- and file-mutating ruff shapes
   passed the profile:
   - `--add-noqa` (G3-F1 / G5-MED-1) rewrites tracked source in place, the same
     class as `--fix`.
   - `--output-file` and `-o` (G3-F2) write a report file into the worktree
     (`-o` was already treated as unsafe for git via
     `UNSAFE_GIT_SUBCOMMAND_FLAGS`; the two are now consistent).
   - `clean` (G3-F2) deletes the ruff cache; added as a bare token on the same
     fail-closed-cost basis the existing `format` entry documents (a path
     literally named `clean` would be refused - accepted for simplicity).

   Corrected token set (closed):
   `{--fix, --fix-only, --unsafe-fixes, --add-noqa, --output-file, -o, format,
   clean}`. The in-source rationale comment was rewritten so its claim is
   accurate, and the closure test now machine-checks that every one of these
   tokens is in the set AND is refused (`mutating_checker_token:<token>`), so
   the claim cannot drift.

2. Fused `-m<module>` root cause fixed (G5-MED-2). The root cause was that
   `_refuse_interpreter_target` **skipped unrecognized dash tokens**: a fused
   token like `-mpip`/`-mcompileall`/`-mwebbrowser` began with `-`, was neither
   the exact `-c` nor the exact `-m`, so the loop fell through to the next token
   and the first `.py` positional then admitted the command - defeating the
   whole module allowlist. The skip is replaced with fail-closed positive
   handling of every dash token:
   - exact `-m` keeps the space-form module handling;
   - a fused `-m<module>` extracts the module name and routes it through the
     SAME `SUPERVISOR_EXECUTABLE_PYTHON_MODULES` allowlist (shared helper
     `_refuse_python_module`), so `-mpytest` admits exactly like `-m pytest`
     while `-mpip`/`-mcompileall`/`-mpydoc`/`-mwebbrowser` are refused
     `python_module_not_allowlisted:<module>`;
   - `-c` and any fused `-c<code>` are refused `inline_python_code`;
   - ANY OTHER dash token (fused or not: `-W`, `-X`, `-O`, `-B`, `-u`, ...) is
     now refused with a typed reason `unrecognized_interpreter_flag:<token>`
     rather than skipped.

   This intentionally keeps the disclosed G3-F5 limitation: an
   option-with-argument form such as `python -W ignore -m pytest ...` is refused
   at the leading `-W` - fail-closed and fail-visible. No documented command
   uses such a form. The function remains pure classification.

3. POLICY_VERSION stays 1.1.0. The version has never shipped or installed
   (supervisor is shadow-only, R595 not activated), so this rework is folded
   into the same unreleased 1.1.0 rule change; no second bump is added. The
   1.1.0 -> approval-digest binding described in the initial submission is
   unchanged.

4. Modularity claim corrected (G3-F3 / G5-LOW-3). The initial self-check block
   above claimed `warnings 12 - identical warning set`; that is inaccurate. At
   the reworked content `python tools/modularity_check.py --check` reports
   `selected 357 files; failures 0; warnings 13`, and one of the 13 is a NEW
   `symbol_ceiling: tools/agent_supervisor/policy.py` advisory
   ("many top-level symbols; a signal, not a verdict"). The profile added 8
   top-level symbols to policy.py across the original submission and this rework
   (three constants, `_refuse_checker_tokens`, `_refuse_python_module`,
   `_refuse_interpreter_target`, `supervisor_execution_refusal`, plus
   `_ABSOLUTE_PATH_SHAPE`). Cohesion justification (per the modularity rule):
   these symbols are one cohesive unit - the supervisor-execution profile for
   documented commands - each a small single-purpose classifier that composes
   into `supervisor_execution_refusal`; they share the module's existing
   command-shape vocabulary (`parse_command`, `_program_name`,
   `_is_destructive_segment`) and belong beside the tier engine they reuse.
   `failures 0`: the gate passes; the warning is advisory only.

### Tests added / changed for the rework

- `tools/test_agent_supervisor_policy.py` (`SupervisorExecutionProfileTests`):
  `test_the_add_noqa_source_writer_is_refused`,
  `test_a_report_file_writing_ruff_arg_is_refused` (`--output-file` and `-o`),
  `test_ruff_clean_is_refused`,
  `test_a_fused_dash_m_module_is_refused_via_the_allowlist`
  (pip/compileall/pydoc/webbrowser),
  `test_a_fused_dash_c_is_refused_as_inline_code`,
  `test_an_unrecognized_interpreter_flag_is_refused_not_skipped`
  (`python -W ignore -m pytest ...` pins the G3-F5 limitation),
  `test_a_fused_allowlisted_module_still_admits` (fused `-mpytest`/`-mruff`
  admit, so the fix is not a blanket refusal),
  `test_previously_admitted_real_shapes_still_admit` (positive regression),
  and `test_the_mutating_checker_token_set_covers_every_known_writer`
  (closure). The pre-existing `test_a_bare_or_targetless_interpreter_is_refused`
  was updated: `python -u` now yields `unrecognized_interpreter_flag:-u`
  (was skipped) - the intended MED-2 tightening.
- `tools/test_agent_supervisor_reviewer.py`
  (`NonMutatingExecutionProfileTests`): spy-runner proofs at the enforcement
  point that `ruff check --add-noqa .` and fused `python -mcompileall foo.py`
  are refused `non_mutating_profile_refused` and NEVER executed
  (`self.ran == []`).

### Rework self-check outputs (real, final content state)

- `python -m pytest tools/test_agent_supervisor_policy.py -q` ->
  `122 passed, 1 skipped` (was 113 passed, 1 skipped; +9 net new).
- `python -m pytest tools/test_agent_supervisor_reviewer.py -q` ->
  `125 passed` (was 123; +2 new).
- `python -m ruff check tools/agent_supervisor/evidence.py
  tools/agent_supervisor/policy.py tools/test_agent_supervisor_reviewer.py
  tools/test_agent_supervisor_policy.py` -> `All checks passed!`
- `python tools/modularity_check.py --check` -> `selected 357 files;
  failures 0; warnings 13` (supersedes the "warnings 12" claim above; includes
  the new advisory `symbol_ceiling: tools/agent_supervisor/policy.py`).

evidence.py was not changed in this rework (the enforcement point was already
correct; the fix is entirely in the classifier). Nothing outside the six
allowed paths was touched.
