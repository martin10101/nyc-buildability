# Producer report — M0-T168 (D-091 T5): independent Claude reviewer path

Producer: ai-pipeline-engineer. Worktree: /root/project/w-M0-T168,
branch task/M0-T168-claude-reviewer-path.
Guard: `rev-parse --show-toplevel` = /root/project/w-M0-T168; branch correct;
HEAD was 1d22a07a0514126eb8b1386f53d9c7b8534247da (claim seam) at start.

## Files changed

- `tools/agent_supervisor/claude_reviewer.py` (NEW, 578 lines) — the whole new
  module; all new logic lives here per `docs/CODE_MODULARITY_POLICY.md`.
- `tools/test_agent_supervisor_claude_reviewer.py` (NEW, 335 lines) — 26 tests,
  one per acceptance scenario plus fail-closed edge cases, injected fake runner,
  no live provider call.
- `review_packet.py` — NOT changed. The packet needs no new field: the
  Codex-review-leak refusal and the frozen-head confirmation are read structurally
  from the existing packet shape (`sections.git.head.value`), so review_packet's
  public interface stays byte-stable. (Packet lists it as "changes if needed"; not
  needed.)
- `project-control/reports/M0-T168-producer-report.md` — NOT written by me:
  forbidden_paths marks `project-control/**` orchestrator-only, and task step 7
  directs the report to the scratchpad. This file is that report, for the
  orchestrator to place at submit.

## What changed and why

Added a SECOND independent reviewer beside `codex_reviewer.py`, matching the
D-091 design doc §2 flow (producer freezes head H → Codex review AND Claude
review, each fresh/read-only, neither sees the other → T6 combiner reads both).
The module mirrors `codex_reviewer.py`'s construction so the two verdicts share
one shape: it reuses `codex_reviewer.ReviewOutcome`, `validate_decision`,
`map_decision_to_tier`, `ReviewError` and `models.CodexDecision`, so a Claude
review and a Codex review are the identical dataclass for the combiner.

Read-only is built the way Codex's is: a REQUIRED mode with a refusal of every
unsafe value. Codex = `--sandbox read-only`; Claude = `--permission-mode plan`
(Claude Code's read-only planning mode). `build_argv` refuses any other
permission mode — naming the write-enabling enum members explicitly — and sweeps
a `FORBIDDEN_REVIEWER_FLAGS` set (`--continue/-c/--last/--resume/
--permission-prompt-tool`); the hard bypass flags are already refused by
`process.assert_argv_safe`, which every argv passes through.

Fail-closed refusals happen before any process starts:
- `reviewer_is_producer` when the reviewer identity equals the producer's.
- `assert_head_frozen` — frozen_head must be a full 40-hex SHA and must equal the
  packet's own recorded `sections.git.head.value`; a missing packet head fails
  closed. After parsing, the decision's `verified_repo_head` must also equal the
  frozen head (`reviewed_head_mismatch`), so a review of some other head never
  reads as a pass.
- `assert_no_codex_review` — two layers: an explicit peer-review key-name denylist
  anywhere in the packet, and a structural scan for any CodexDecision-shaped
  mapping under any key (and under a `.value` wrapper), excluding the one
  legitimate `last_supervisor_decision` context section.

Malformed/empty output never becomes PASS: `extract_decision_payload` returns
None for empty/no-object output (→ `empty_review_output`); a non-conforming object
fails `validate_decision` (→ its error code); a timeout → `review_timeout`. Each
yields a `ReviewOutcome` with `decision is None`, `ok == False`, and an ASK tier —
never a proceed decision.

Config switch defaults OFF: `ClaudeReviewerConfig.enabled=False`,
`ClaudeReviewerConfig.from_mapping` (strict: only a real bool True enables; unknown
keys refused), and `claude_reviewer_enabled(config)` (only real bool True;
absent/non-bool/False → off). Nothing in `loop.py` references the module (proved by
a test), so with the switch off the single-reviewer loop is byte-for-byte
unchanged until T6 wires it in.

## Modularity answers (CODE_MODULARITY_POLICY)

- New logic in the NEW module `claude_reviewer.py`; `codex_reviewer.py`,
  `gate_wave.py`, `loop.py` untouched (forbidden). 578 lines, one responsibility
  (the Claude reviewer adapter: argv, independence/freeze guards, fail-closed
  parse, switch). `tools/modularity_check.py --check`: selected 604 files;
  failures 0; warnings 27 — claude_reviewer.py is NOT in the warning list.
- review_packet.py public interface preserved (no edit).

## CLI flags used — each verified in fixtures/ (never guessed)

- `-p` / `--print`: `fixtures/capability_matrix_v1.json`
  (`claude.print_mode_output_format`) + `capability_probe_live_*.json`
  `claude_flags["--print"]=="supported"`.
- `--output-format`: `capability_probe_live_*.json`
  `claude_flags["--output-format"]=="supported"`.
- `--permission-mode`: `fixtures/native_runtime_detection_2026-09-24_m0t159.json`
  `flags["--permission-mode"]=="supported"`; value `plan` is a member of the
  installed enum recorded in
  `fixtures/statusline_live_2026-08-27_2_1_247_r162_discharge.json`
  `permission_mode_proof.finding` ("acceptEdits, auto, bypassPermissions, manual,
  dontAsk, plan").
- `--model`: `capability_probe_live_*.json` `claude_flags["--model"]=="supported"`.
- `--tools` deliberately NOT used: recorded "supported" but with NO recorded
  allowlist/denylist semantics; using it would mean guessing. Plan mode is the
  sole, fully-grounded read-only primitive.

HONEST UNCERTAINTY (documented in the module, mirrors claude_runner.py): the exact
print-mode output envelope bytes and stdin-vs-arg behavior are not re-verified live
here; the injected-runner tests prove the loop/argv/guards/parse, not the live CLI
contract. A preflight must confirm the envelope before any live Claude review;
until then the default-OFF switch keeps it inert. (Recertification of the whole
fixture pack is the separate D-091 recert task after all code tasks — packet risk
note.)

## Acceptance scenarios → proving tests

1. primary (read-only argv, allowlisted model, Codex verdict shape):
   `PrimaryReadOnlyArgvTests::test_build_argv_is_read_only_and_pinned`,
   `::test_review_returns_codex_decision_shape`,
   `::test_model_must_be_allowlisted`,
   `::test_envelope_wrapped_decision_is_extracted`,
   `::test_stdin_carries_packet_not_a_codex_review`,
   `::test_build_argv_refuses_write_enabling_mode`, `::test_build_argv_refuses_empty_model`.
2. boundary (identity==producer, or handed the Codex review):
   `IndependenceRefusalTests::test_refuses_when_reviewer_is_the_producer`,
   `::test_refuses_codex_review_under_marker_key`,
   `::test_refuses_codex_decision_shaped_object_any_key`,
   `::test_refuses_codex_decision_under_value_wrapper`,
   `::test_last_supervisor_decision_does_not_false_trip`;
   plus frozen-head half: `FrozenHeadTests::test_refuses_non_sha_frozen_head`,
   `::test_refuses_packet_head_mismatch`, `::test_refuses_packet_without_recorded_head`,
   `::test_decision_reviewing_a_different_head_is_not_pass`.
3. missing/ambiguous (malformed/empty → FAIL/UNVERIFIED, never PASS):
   `FailClosedParseTests::test_empty_output_is_not_pass`,
   `::test_non_json_output_is_not_pass`,
   `::test_object_missing_required_fields_is_not_pass`,
   `::test_bad_decision_value_is_not_pass`, `::test_timeout_is_not_pass`,
   `::test_extract_decision_payload_empty`.
4. failure (switch defaults off; loop unchanged):
   `SwitchDefaultsOffTests::test_config_default_is_off`,
   `::test_enabled_only_for_real_bool_true`,
   `::test_from_mapping_strict_and_fail_closed`,
   `::test_loop_does_not_reference_the_claude_reviewer`.

## Commands and counts

- `python -m ruff check claude_reviewer.py test_...py` → All checks passed! (exit 0)
- `pytest tools/test_agent_supervisor_claude_reviewer.py -q` → 26 passed in 0.35s.
- review_packet.py consumers (run individually — the full
  `pytest tools/test_agent_supervisor_*.py` glob OOMs on the 8 GB server, exit 137):
  - test_agent_supervisor_reviewer: 125 passed, 119 subtests.
  - test_agent_supervisor_ephemeral_review: 31 passed, 6 subtests.
  - test_agent_supervisor_mrl_one_shot_review: 81 passed.
  - test_agent_supervisor_gate_wave: 63 passed.
  - test_agent_supervisor_cross_task: 45 passed.
  - test_agent_supervisor_mrl_launch_path: 52 passed.
  - test_agent_supervisor_repair_gate: 78 passed, 37 subtests.
  - test_agent_supervisor_start_reentry: 16 passed.
  - test_context_pack: 15 passed.
  - test_agent_supervisor_model_chain: OOM (exit 137) even alone — memory, not a
    failure. Proved intact: `--collect-only` = 25 tests collected (exit 0);
    `ModelChainConfigTests` = 9 passed, 9 subtests.
  - test_agent_supervisor_loop: 3 pre-existing env failures
    (`test_a_loop_refusal_is_a_report_not_a_traceback`,
    `test_run2_scenario_clear_recovery_then_start_works`, and the checkpoint_id
    one) — proved pre-existing by moving my two new files aside and re-running on
    the clean base: they still fail (my change adds only new files; loop.py imports
    neither). Not caused by this task; 124 of 127 pass.
- `python tools/modularity_check.py --check` → selected 604 files; failures 0;
  warnings 27 (exit 0); claude_reviewer.py not flagged.

## Assumptions / limitations / could-not-do

- Read-only via `--permission-mode plan`. Plan mode's read-only semantics is
  Claude Code's documented behavior and the enum value is fixture-verified; it is
  the mirror of Codex `--sandbox read-only`. No live re-verification of plan-mode
  write-blocking was performed (thin client; no live provider call allowed).
- No live provider call, no loop start, no push/merge/gh/project_control (all
  forbidden; honored). Committed in-worktree only.
- `review_packet.py` left unchanged (public interface stable).
- Recertification of `tools/agent_supervisor/**` fixtures is the separate post-code
  D-091 recert task (packet risk note), not done here.
- `--tools` left unused to avoid guessing its filter semantics.

END-OF-REPORT
