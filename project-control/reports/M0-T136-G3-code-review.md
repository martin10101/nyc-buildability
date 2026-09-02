# M0-T136 G3 independent code review (verbatim reviewer return)

Recorded by the orchestrator/verifier session per the report-preservation rule
(`.claude/rules/project-control.md`): the reviewer's return is saved VERBATIM below
(transport entity-decoding only: `&amp;` decoded to `&`). Reviewer: `code-reviewer`
(read-only, independent; producer = `mrl-tranche-b-producer`). Received 2026-09-02.

---

# GATE REPORT — M0-T136 (D-024 Amendment 40, MRL Tranche B) — G3 Code Review

**Reviewer:** code-reviewer (independent, read-only)
**Task:** M0-T136 · **Branch:** candidate/D-024-mrl-option-b · **Frozen candidate:** `1489879e` (tree `0babc469`) · **HEAD:** `1da9d513`
**Diff reviewed:** `git diff 6f5d12a6..1489879e` · **Verdict basis:** actual source, re-derived requirements, independent test runs

## VERDICT: PASS

No BLOCKING or MAJOR defects. Four NOTE-level observations recorded below; none block acceptance. The independent `directive-compliance-verifier` pass (per-requirement R515–R598) is a separate gate and is not part of this G3 verdict.

## Scope & reproduction

- Confirmed no production/test code changed after the freeze: `git diff --name-only 1489879e..1da9d513 -- tools/ apps/ services/` is empty; post-freeze commits are reports/docs/state only. The working tree therefore equals the frozen candidate, so read-only checks below are against the reviewed identity.
- Independent focused test runs at the frozen tree:
  - `pytest test_agent_supervisor_mrl_launch_manifest + _launch_path + _exec_chain + _subagent_contract` → **216 passed**
  - `pytest test_..._mrl_one_shot + _one_shot_review + _codex_decision + _worker_result + _transport + _exec_identity + _remote + _launch_draft` → **217 passed**
- `python tools/modularity_check.py --check` → **rc 0**, 0 failures (only warnings; `claude_runner.py` no longer flagged after the `checkpoint_extraction` split).

## Findings against the acceptance contract

**B1 launch manifest (AS-B1, R558–R561) — PASS.** `mrl_launch_manifest.verify_launch` re-observes every one of the twelve R559 fields from git/filesystem/packet (`observe()`); the manifest's own values are never used as observations. `test_manifest_values_never_used_as_observations` proves a missing observation *raises*, never falls back to the manifest. All twelve fields carry a dedicated one-field mutation test (`mrl_launch_manifest.py` tests lines 225–297) plus an all-together test. Refusals are typed (`ContractError`/`LoopError`/`refusals.Refusal`) and pre-provider — `preflight_launch` runs at PREFLIGHT before the runner is constructed (`cli.py:_run_loop` line ~2701). `launch_manifest_base_ref_missing` is surfaced specifically at `mrl_launch_path.py:89` (`code = exc.code if exc.code.startswith("launch_manifest_") else "launch_manifest_invalid"`) with its paired test at `tools/test_agent_supervisor_mrl_launch_path.py:226`.

**B2 exec chain (AS-B2, R562–R566) — PASS.** `mrl_exec_identity.sha256_file_complete` streams the whole file; the docstring and `test_every_call_rehashes_no_cache` confirm no size/mtime cache. All five mandated mutation classes are covered in `tools/test_agent_supervisor_mrl_exec_chain.py`: same-size/restored-mtime (181), wrapper retarget (194), entrypoint replacement (209), updater re-enablement (255–263), model/version mismatch (307–318), plus a bonus vendor-binary replacement. Chain resolution parses the real `.cmd` shim text (never inferred from filename) and fails closed on any unresolvable link. `observe_version` returns `""` on nonzero/exception so `verify_runtime_reported` fails closed.

**B3 subagent contract (AS-B3, R567–R580) — PASS.** Configurable concurrent/total limits, `MAX_DEPTH=1` enforced, foreground-only enforced, controller-issued parent/child ids with global accounting in an O_EXCL-locked ledger (lock timeout fails closed), MCP and out-of-inventory denial, `isolated-worktrees` explicitly refused (single-writer only). `RestrictedProfile` composes the real measured flags (`--restricted`, `--permission-mode dontAsk`, `--tools`, `--allowedTools`/`--disallowedTools`, `--strict-mcp-config`, `--settings`, `--agents`). `effective_grants()` + `test_tools_alone_grants_nothing` prove `--tools` alone grants nothing; over-limit fan-out denied; managed policy (present or absent) is hashed into the pinned identity.

**B4 one-shot wiring (AS-B4, R581–R585) — PASS.** One fresh process / one prompt / stdin closed / no resume-second-message-background is enforced at multiple layers with mutation tests each: `mrl_transport.FORBIDDEN_FLAGS` + single-spawn counter; `one_shot_second_dispatch`, `one_shot_extra_turns`, `one_shot_second_spawn`. Total run accounting via `ledger.close()` and a processes-total bound at settlement. Descendant-zero proof is genuinely fail-closed: `prove_zero_descendants` returns `proven=False` with `source="unavailable"` when the table is unobservable and `proven=False` with the remaining pids when the tree is non-empty; `_settle` marks containment `descendants_remaining` on any unproven tree. Reviewer decision is bound to a controller-observed base ref (`observe_remote` real `ls-remote`, `git_binding_from_observation`, validated 40-hex SHAs), and `build_codex_decision` makes APPROVE→COMPLETE conditional on `invariants_ok is True and gates_ok is True` (strict identity), else HOLD.

**CLI/loop wiring — PASS.** `cli._run_loop` cleanly selects `OneShotRunner`/`OneShotReviewer` only when a manifest is applied; the legacy `ClaudeRunner`/`CodexReviewer` pair is otherwise byte-unchanged. Under a manifest: `turn_budget=None` (no reserved-turn injection, so `reserved_turn_injection(None)==()` — confirmed), `max_turns` is the manifest's hard bound, and `first_prompt = args.prompt` raw. `start_report_lines` was extracted to `start_gate.py` byte-identically to keep `cli.py` at its grandfathered ceiling; `loop.py` is unmodified and the `run_unit`/`review` signatures are drop-in compatible with its existing call sites (`loop.py:1689`, `2041`). Modularity check passes.

**Full-diff allowed-paths scan (focus area 6) — PASS.** Every production/test file is under `tools/agent_supervisor/` or the packet's named test allowlist; docs, `CLAUDE.md`, and the engineering-reliability skill are allowed. The only forbidden-path touches are `project-control/{tasks,state,campaigns,directives,gates}` and the M0-T134 continuity reports — all orchestrator-capacity B0 governance-continuity commits (`state.json` is a trivial accepted-list/pointer update). `modularity_baseline.json` is byte-identical to base; `modularity_exceptions.json` removes only the `claude_runner.py` entry (AS-B0-1).

**AS-B0-2 / AS-B5 / AS-NEG — PASS.** CLAUDE.md principle 17 + the skill's "Defect convergence" section carry all seven required elements concisely and non-duplicatively. `CONTROLLER_UPDATE_RUNBOOK.md` §11 is prominently obsoleted in favor of `MRL_LAUNCH_RUNBOOK.md`; PowerShell tests preserve raw `$LASTEXITCODE` and the mutant harness proves piping/`Tee-Object`/`$?` cannot green a child exit 7; the ten-item canary package is present-only and explicitly not executed. Read-only git confirms: clean tree, no upstream configured, no remote `candidate/*` ref, `origin/control/D-024-fable-codex-loop` untouched at `6f5d12a6`. (PR #241's remote state requires a network `ls-remote` — deferred to the orchestrator per the evidence-capture division of labor; local evidence shows nothing was pushed.)

## NOTE-level observations (non-blocking; no action required for this gate)

1. **NOTE** `tools/agent_supervisor/mrl_one_shot_review.py:275-277` — when the container adopts no pid, the descendant proof is synthesized as `proven=True, source="no_pid_adopted"` rather than routed through `prove_zero_descendants`. This is a weaker stance than `mrl_one_shot.py`, but it cannot produce a false COMPLETE: a run that adopted no pid yields no output → `raw is None` → `no_decision` fails the review closed (verified by the surrounding control flow).
2. **NOTE** `mrl_one_shot_review.py:275` proves only `pids[-1]`'s tree. Correct for the current single-spawn Codex path (one adopted pid); would under-cover only if the container ever adopted multiple independent roots, which the design does not do.
3. **NOTE** `mrl_launch_path.py:42-51` fills both `--repo` and `--worktree` from `expected.worktree` (not `expected.repo_root`). Intentional and correct (git must run in the worktree; `repo_root` is verified independently as its own R559 field), but the naming can mislead a future reader.
4. **NOTE** `tools/gate_runner.py` records stdout as a sha256 + byte count, not full text, so a suite record shows only `returncode:0`, not the pass count. This is by design (tamper-evident recorder, verdict = child's raw exit); I independently reran the core modules to compensate.

The producer's own blocker list (producer-report §10) transparently discloses the out-of-packet residue (F22 `loop-start` skill/hook and `loop_command_interceptor.py`, ps_tests not yet in CI, `DEFAULT_DOCS` missing the MRL runbook, pre-existing root-tree ruff F28) as orchestrator follow-ups; these sit behind forbidden paths (`.claude/hooks`, `.github/workflows`) and are correctly out of scope, honestly recorded rather than silently patched.

## Adversarial checks specifically attempted and cleared
- A manifest field trusted without observation — **not found**; `verify_launch` observes all twelve and `test_manifest_values_never_used_as_observations` locks it.
- A hash cache in the security-critical path — **not found**; whole-file streaming, `test_every_call_rehashes_no_cache`.
- An untested denial rule — **not found**; every ledger clause and profile rule has a paired negative test (`_subagent_contract` tests 103-115, 195-214).
- A test asserting on its own fixture — **not found**; the `FakeGit`/`world` fixture supplies observations and mutation tests perturb one side, exercising real comparison code.
- A refusal path that throws a raw traceback — **not found**; git/spawn/IO failures are wrapped into typed `ContractError`/`LoopError`, and `main()` entrypoints map `ContractError`→rc 3.
- Guessed schemas / hard-coded legal or origin values — **not found**; codex triple map is documented-measured, contract schemas are hand-written and enforced dependency-free, base ref is Option-B neutral and never defaulted.

**Relevant files:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_launch_manifest.py`, `mrl_launch_path.py`, `mrl_exec_chain.py`, `mrl_exec_identity.py`, `mrl_subagent_contract.py`, `mrl_subagent_hook.py`, `mrl_one_shot.py`, `mrl_descendants.py`, `mrl_one_shot_review.py`, `mrl_codex_decision.py`, `mrl_remote.py`, `mrl_transport.py`, `mrl_worker_result.py`, `cli.py`, `start_gate.py`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\gate_runner.py`, and the paired test modules under `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\`.

**Summary:** M0-T136 delivers Tranche B as a coherent, defect-convergence-clustered change: a single `start --launch-manifest` entrance whose twelve fields are independently re-observed (manifest never proof), a streaming full-chain executable identity re-hashed with no cache before every spawn covering all five mandated tamper classes, a controller-owned bounded-subagent contract that composes the real restricted-CLI mechanisms and proves `--tools` grants nothing, and a one-shot runner/reviewer pair (one fresh process, one prompt, stdin closed, no resume/second-message/background) with total accounting, genuinely fail-closed descendant-zero proof, and a git-bound controller decision where APPROVE alone never advances — all wired so the legacy path is untouched and no module exceeds its ceiling. Every positive contract has a paired negative/mutation test; I reproduced 433 MRL tests green and the modularity gate clean at the frozen candidate, the diff stays within scope with only orchestrator-capacity control-plane touches outside it, and nothing was pushed. I recommend **PASS**, subordinate to the independent directive-compliance verification of R515–R598.

---

Orchestrator note (not part of the verbatim return): the reviewer deferred the PR #241
remote check to the orchestrator; the orchestrator/verifier session independently ran
`git ls-remote origin refs/pull/241/head` on 2026-09-02 → `4174a3b2` (untouched), and
`git ls-remote --heads origin` shows no `candidate/*` ref and
`control/D-024-fable-codex-loop` = `6f5d12a6` (evidence-capture division of labor,
`.claude/rules/project-control.md`).
