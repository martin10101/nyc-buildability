# M0-T134 G3 — independent code review (MRL Tranche A, D-024 Amendment 39)

**Gate:** G3 (independent code review) · **Reviewer:** code-reviewer (read-only; not the producer)
**Reviewed code candidate:** `5e89175d` · **Reviewed HEAD / identity:** `ad770ad4` / content-manifest
`1c3078c6…` (tools tree byte-identical between `5e89175d` and `ad770ad4`: subtree `1fb85dc8`).
**Verdict: PASS.**

The reviewer independently re-read every changed production/schema module and re-derived each guard;
no defect, no bypass, no responsibility-mixing found. Findings by requirement:

- **R509 split (checkpoint_extraction.py):** genuine behavior-neutral relocation. `claude_runner`
  imports the relocated names and re-exports them; runtime identity check confirms
  `claude_runner.RunnerError/extract_checkpoint/CheckpointError` **are the same objects** as
  `checkpoint_extraction`. Import direction is one-way (`claude_runner → checkpoint_extraction →
  models`); no cycle. Refuse-rather-than-choose checkpoint semantics (missing/conflicting-duplicate/
  multiple-distinct) preserved. cli.py `except RunnerError` unchanged.
- **R501/R503 WorkerResult:** dependency-free `validate_instance` enforces object/string/array with
  `additionalProperties:false`; `bool` is correctly excluded from `str`. Forged factual fields are
  unknown keys → fail closed. Controller builds `ClaudeCheckpoint` from `ControllerObservedFacts`;
  only `summary`/`proposed_next_action` come from the worker; `status` is a fixed enum map.
- **R502/R504/R505 CodexDecision:** `ReviewVerdict.from_provider` binds evidence ids to the
  controller-issued set. `build_codex_decision` uses strict `invariants_ok is True and gates_ok is
  True` (a truthy non-bool → HOLD). `_validate_git_binding` requires present url/ref and 40-hex SHAs;
  the git binding is Option-B neutral (base ref is data; `verified_origin_main` not referenced).
- **R505 remote:** `observe_remote` fails closed on empty url/ref and any non-40-hex ls-remote result;
  the network runner is injectable and never invoked in Tranche A.
- **C7 transport:** `build_one_shot_plan` refuses empty exec/prompt, missing/non-string model (no
  fallback), non-positive `max_turns`/wall-clock (bool-guarded), and every forbidden resume/continue/
  fork/background flag; `run_one_shot` spawns exactly once via a counting wrapper and never loops on
  output. argv is a list (no shell).
- **R511 exec identity:** `sha256_file_complete` streams the whole file with no size/mtime shortcut;
  `verify_executable_chain` recomputes and rejects any change/reorder; `assert_updater_disabled`
  requires `DISABLE_AUTOUPDATER=1` and refuses `DISABLE_UPDATES` (R280); `verify_runtime_reported`
  fails closed on empty/mismatched model or version.
- **R510/R514 gate_runner:** refuses a `str`/`bytes` argv (shell string), runs a direct no-shell
  subprocess so the recorded returncode is the child's own, records the full tamper-evident bundle
  (argv/cwd/timestamps/repo HEAD+tree/exec-chain/returncode/stdout+stderr digests); `render_report`
  is generated from the record; mutation mode reports success only when the mutant is killed.

**Modularity:** unpiped `modularity_check.py --check` → raw exit 0, 0 failures. `modularity_exceptions.json`
and `modularity_baseline.json` are byte-identical to `6f5d12a6` (sha256 `dba91e16…1792c7` /
`8830a47d…731ca5`); the pass comes from the split, not a policy edit. ruff 0.13.0 clean on all 14
Tranche-A `.py` files.

**Scope discipline (trap B):** the exec-chain/transport/remote functions are additive primitives; the
executable-chain supply, live model/version probe, and CLI/loop dispatch are Tranche B, correctly
deferred and disclosed in the producer report §6. No acceptance claim treats them as live closure.

**Non-blocking observations (no change required for Tranche A):** (1) AS-4's "observed-vs-expected
mismatch" is realized at the format/presence level in `mrl_codex_decision`; the semantic observed-vs-
pinned comparison is a live-loop operation deferred to Tranche B. (2) `&` is in `FORBIDDEN_FLAGS` but
lacks its own negative test (covered indirectly; argv-list makes it inert). (3) the gate_runner
PowerShell test proves "records the child's true raw exit, adds no masking"; the anti-pipe-injection
guarantee itself rests on the shell-string refusal, which is tested. None is a defect.
