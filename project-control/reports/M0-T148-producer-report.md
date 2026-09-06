# M0-T148 producer report - evidence-packet completeness repair (D-032-R020)

Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t148`, branch
`task/M0-T148-packet-completeness`, base `83594de2`. Producer edits only; the
orchestrator commits and integrates.

## The defect (recap)

The M0-T147 packet-based review contract promises the reviewer that every
worker-tree fact arrives as a supervisor-collected, digest-bound packet section,
but `loop._collect` built the packet from git facts + project_control +
checkpoint only. `git diff HEAD` cannot show untracked files, and workers can
never commit (orchestrator-only git), so any task whose deliverables are NEW
files was invisible to content review: run persistent-local-04 REVISEd four
identical times and tripped `consecutive_revision_loops`. Three evidence classes
were missing: untracked deliverable contents, the task contract, and
supervisor-executed test transcripts.

## What changed, per file

### tools/agent_supervisor/evidence.py (all new collection logic here)

- New module constants with rationale in-source: `MAX_UNTRACKED_FILES = 32`,
  `UNTRACKED_CONTENT_BYTES = DEFAULT_SECTION_BYTES` (16,384), and
  `DEFAULT_COMMAND_TIMEOUT_SECONDS = 300.0`.
- `parse_command` added to the existing `from .policy import (...)` (no new
  dependency; policy was already imported).
- Porcelain parsing helpers (`_parse_porcelain_untracked`, `_c_unquote`,
  `_bounded_names`): decode git's `??` entries including C-quoted paths with
  spaces, backslash escapes, and octal-escaped non-ASCII (UTF-8) bytes. Verified
  against real git output on this host (`?? "caf\303\251.py"`, `?? "with
  space.py"`, `?? pkg/sub/file.py`).
- `EvidenceCollector.collect_untracked_content(porcelain)`: reads each `??`
  path via the existing bounded `read_file` (per-file byte bound; the digest is
  always of the FULL file). A missing/failed OR truncated porcelain is recorded
  as a fail-visible `__enumeration__` entry; a count over the cap records an
  explicit fail-visible `__cap__` entry naming the omitted files (bounded);
  never a silent omission. Reuses `CollectionResult`/`_failure`.
- `EvidenceCollector.collect_task_packet(task_id)`: reads
  `project-control/tasks/<id>.json` via `read_file`; a blank id or a missing
  file returns a `CollectionResult` failure (missing_file / missing_task_id) so
  the builder routes it into `failed_collections`.
- `EvidenceCollector.run_command` / `collect_command_transcripts`: execute the
  given documented commands via `process.run` (`self._run`) with `cwd` = the
  worker worktree. The command string is tokenized by the classifier's own
  `policy.parse_command` (single source of truth) and refused (`unrunnable_
  command`) unless it is one clean, metacharacter-free segment; `assert_argv_
  safe` is applied before running. Each transcript records argv (list form),
  exit_code, timed_out, duration_seconds, and bounded stdout/stderr. A nonzero
  exit is recorded as an `ok` transcript carrying that exit; a timeout is
  recorded with `timed_out=True` and its partial transcript. Nothing is raised
  or dropped. An empty command list yields `{}` -> an explicit empty section.
- `results_section(results)`: renders a group of `CollectionResult`s as one
  self-describing section for `extra_sections=` (which bypasses the builder's
  `failed_collections` routing), so each entry - ok OR failed - is fail-visible
  inline. Empty mapping -> `{}` (explicit empty section).
- `EvidenceCollector.collect_completeness(task_id, git_facts, documented_
  commands)`: one call returning `(task_packet, extra_sections)` ready for
  `build_packet`. Bundled here to keep the oversized loop module's growth to a
  single call and keep all collection logic in the collector.

### tools/agent_supervisor/loop.py (minimal wiring only)

- `_collect` now calls `collector.collect_completeness(...)` and threads
  `task_packet=` and `extra_sections=` through the existing `build_packet`
  parameters when a collector is present. No behavioral change when
  `collector is None` (shadow/unit tests). Net +6 SLOC (see below).

### tools/agent_supervisor/codex_reviewer.py

- `REVIEW_INSTRUCTIONS` item 1 rewritten: `git.diff_content` is now described as
  "the patch text of the worker's TRACKED changes ONLY" and states `git diff
  HEAD` cannot show new files and the worker cannot commit them - the false
  "the ACTUAL patch text of every uncommitted change" premise is removed. Items
  1/2/4 name and explain `untracked_content`, `task_packet`, and
  `command_transcripts` and fold them into the cross-check and the
  worker-authored-data immunization clause. Preamble comment updated for
  M0-T148. Text stays pure ASCII and deterministic; the codex output schema and
  the decision enum are unchanged.

### tools/agent_supervisor/review_packet.py

- No change needed. The new sections live under `sections`; the guard's
  `_scan_marker_keys(sections, ...)` (none of the new names are prohibited
  markers) and the whole-packet structural byte cap (`_scan_packet_size`) already
  cover them exactly as they cover `diff_content`. Verified by a passing guard
  test and a load-bearing mutation test (see S5 below).

## New section formats

- `sections.untracked_content`: `{ "<repo-relative path>": {"ok": true,
  "value": "<bounded file text, explicit TRUNCATED marker if over bound>",
  "digest": "<sha256 of FULL file>", "truncated": bool}, ... }`. Fail-visible
  entries: `"__enumeration__"` / `"__cap__"` -> `{"ok": false, "error_category":
  ..., "detail": ..., "argv": [...]}`.
- `sections.task_packet`: rendered by the builder's `task_packet=` path as
  `{"file": {"value": "<bounded JSON text>", "digest": "<sha256 of full>"}}`;
  a missing contract appears as `task_packet.file` in `failed_collections`.
- `sections.command_transcripts`: `{ "<command string>": {"ok": true, "value":
  {"argv": [...], "exit_code": int, "timed_out": bool, "duration_seconds":
  float, "stdout": "<bounded>", "stderr": "<bounded>", "stdout_truncated":
  bool, "stderr_truncated": bool}, "digest": "<sha256 of full untruncated
  outcome>", "truncated": bool}, ... }`. Empty -> `{}`.

## Bounds chosen and rationale

- `MAX_UNTRACKED_FILES = 32`: a hand-authored new-file deliverable set is small
  (the reproducing M2-T020 case had three); 32 covers a broad multi-file feature
  while bounding growth. Surplus is recorded fail-visible, and the overall packet
  byte cap (`DEFAULT_PACKET_BYTES` -> `STOP_FOR_OWNER`) remains the ultimate
  honest backstop.
- `UNTRACKED_CONTENT_BYTES = 16,384` (== `DEFAULT_SECTION_BYTES`): shows enough
  of a typical source file for review; oversize is truncated with the explicit
  marker while the digest still binds the full file, so the reviewer can detect
  and partially read it rather than being handed nothing.
- `DEFAULT_COMMAND_TIMEOUT_SECONDS = 300.0`: a per-command wall-clock ceiling; a
  timeout is recorded with `timed_out=True`, never treated as success (S14). The
  digest binds the full untruncated outcome (argv, exit, timed_out, streams) and
  deliberately EXCLUDES duration so two runs of the same command with the same
  output share a digest.

## Tests added

tools/test_agent_supervisor_reviewer.py:
- `UntrackedContentTests`: `test_each_untracked_file_is_one_digest_bound_entry`,
  `test_a_quoted_or_spaced_or_unicode_path_round_trips`,
  `test_an_oversized_file_is_truncated_with_a_full_content_digest`,
  `test_over_the_count_cap_is_fail_visible_never_a_silent_omission`,
  `test_a_missing_or_failed_porcelain_is_recorded_not_assumed_clean`,
  `test_the_porcelain_parser_handles_crlf_and_quoted_paths` (S1).
- `TaskPacketCollectionTests`:
  `test_the_contract_is_collected_and_rides_digest_bound`,
  `test_a_missing_contract_is_an_explicit_failed_collection`,
  `test_a_blank_task_id_is_refused_not_read_as_a_path` (S2).
- `CommandTranscriptTests`:
  `test_a_passing_command_records_argv_exit_and_output`,
  `test_a_failing_command_records_its_real_nonzero_exit`,
  `test_a_timeout_is_recorded_with_its_partial_transcript`,
  `test_a_command_with_shell_metacharacters_is_refused_not_run`,
  `test_an_empty_documented_list_yields_an_explicit_empty_section`,
  `test_the_digest_binds_the_full_untruncated_outcome` (S3).
- `PacketContractTruthfulnessTests`: `test_the_three_new_sections_are_named`,
  `test_the_false_every_uncommitted_change_claim_is_gone`,
  `test_the_instructions_stay_pure_ascii_and_deterministic`,
  `test_the_decision_enum_and_the_boundary_anchors_are_unchanged` (S4).
- `NewSectionImmunizationTests`:
  `test_a_secret_in_an_untracked_file_is_masked_like_one_in_diff_content`,
  `test_redaction_is_load_bearing_a_section_added_after_it_would_leak`,
  `test_the_new_sections_pass_the_prohibited_content_guard`,
  `test_the_structural_byte_cap_is_load_bearing_for_a_hostile_untracked_file`
  (S5). Real synthetic git repos are used for S1; a fake runner for S3; hostile
  content is a runtime-assembled FAKE secret (no scanner suppression).

tools/test_agent_supervisor_loop.py:
- `PacketCompletenessWiringTests`:
  `test_the_reviewer_packet_carries_all_three_new_sections`,
  `test_the_untracked_deliverable_content_and_digest_are_present`,
  `test_the_documented_test_command_was_executed_and_recorded`,
  `test_the_task_contract_rides_digest_bound` (S1-S3 integration through
  `_collect`; fake collector runner, real on-disk deliverable + contract).

S6 (reproduction closure) and the full-suite regression (S7) are the
orchestrator's post-integration steps; the synthetic-repo tests cover the same
behavior here.

## Self-check commands and results (real outputs)

- `python -m pytest tools/test_agent_supervisor_reviewer.py -q` -> `117 passed`
  (was 94 before this task; +23 new).
- `python -m pytest tools/test_agent_supervisor_loop.py -q` -> `126 passed`
  (was 122; +4 new).
- `python -m pytest tools/test_agent_supervisor_evidence*.py -q` -> not run: no
  such file exists (confirmed by the orchestrator; the two suites above are the
  documented commands).
- `python -m ruff check tools/agent_supervisor/evidence.py
  tools/agent_supervisor/loop.py tools/agent_supervisor/codex_reviewer.py
  tools/agent_supervisor/review_packet.py tools/test_agent_supervisor_reviewer.py
  tools/test_agent_supervisor_loop.py` -> `All checks passed!`
- `python tools/modularity_check.py --check` -> `selected 356 files; failures 0;
  warnings 12` (all 12 warnings pre-existing).
- Regression (adjacent review path):
  `python -m pytest tools/test_agent_supervisor_adversarial.py -q` -> `93 passed`;
  `python -m pytest tools/test_agent_supervisor_ephemeral_review.py
  tools/test_agent_supervisor_mrl_one_shot_review.py
  tools/test_agent_supervisor_repair_gate.py -q` -> `190 passed`.

## SLOC / line deltas per file (physical lines; git commits are the orchestrator's)

- evidence.py: 477 -> 760 (+283 physical; measured SLOC 594; not
  grandfathered-oversized, no modularity warning).
- loop.py: 2974 -> 2983 (+9 physical; measured SLOC 2088 == its material-growth
  limit of 2088, baseline 1899). loop.py was already at the ceiling; growth was
  held to one `collect_completeness` call. NO modularity exception added or
  renewed. Note: zero remaining headroom on loop.py - the next edit there needs
  a decomposition, not more lines.
- codex_reviewer.py: 957 -> 982 (+25 physical, REVIEW_INSTRUCTIONS text +
  comment; measured SLOC 766; pre-existing review_signal warning unchanged).
- review_packet.py: 476 -> 476 (unchanged).
- test_agent_supervisor_reviewer.py: 1372 -> 1686 (+314; test files excluded
  from modularity SLOC).
- test_agent_supervisor_loop.py: 2417 -> 2504 (+87).

## Invariants held

- Collector git usage stays read-only: `assert_read_only_git` untouched; the new
  `run_command` runs documented TEST commands (already policy-admitted), never
  git, via `process.run` argv arrays with `assert_argv_safe`.
- Pure-ASCII source in all four production files (evidence/codex_reviewer/
  review_packet 0 non-ASCII; loop.py's 4 non-ASCII are pre-existing em-dashes in
  unrelated comments, none in the edited region).
- The codex output schema and decision enum are unchanged.

## Recertification note

This change modifies the certified controller subtree (evidence/loop/
codex_reviewer collection + review contract). Per the D-032 convergence record
section 7, the next launch after closure requires R247 recertification +
source_binding re-pin + controller reinstall for the changed subtree, and uses a
FRESH run-id (durable breaker tally). This producer change re-triggers R247
recertification.

## Deviations / limitations

- Deviation from the brief's suggestion to consume `command_docs.py`: that module
  is the doc-VALIDATION tooth (owner-presented commands vs the live CLI
  contract), not the runtime source of a task's test commands. The canonical
  runtime source is `TaskAuthority.documented_test_commands`
  (`policy.validate_documented_test_commands` against
  `schemas/task_packet_commands.schema.json`); `_collect` consumes that. No new
  config channel was invented.
- The two `results_section`-rendered sections ride in `extra_sections=`, which
  bypasses the builder's top-level `failed_collections`. Their failures are made
  fail-visible INLINE (each entry carries `ok`/`error_category`/`detail`)
  instead, which satisfies "never a silent omission". Only `task_packet` uses the
  dedicated `task_packet=` path and so a missing contract does reach
  `failed_collections` (S2 requirement).
- loop.py sits exactly at its modularity limit (2088). Adding any further line to
  loop.py will fail the gate; a future change touching `_collect` should
  decompose loop.py rather than grow it.
