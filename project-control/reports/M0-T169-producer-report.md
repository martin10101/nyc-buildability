# Producer report — M0-T169 (D-091 T6): review combiner

Producer: ai-pipeline-engineer
Worktree: /root/project/w-M0-T169  branch task/M0-T169-review-combiner
Claim-seam: 3a5e247bcc5f4b424086a98cffc6695a3d352012
Head after work: ef6dcd7c2de72236dffdbb2dffb5d6ee0de4904d
Directive refs: D-091-R003 (combiner never the producer), D-091-R001, D-091-R007; R008 (combining model is the owner's choice, no default).

## Guard
`git -C /root/project/w-M0-T169 rev-parse --show-toplevel` = /root/project/w-M0-T169; branch task/M0-T169-review-combiner; HEAD at claim time 3a5e247b (verified, no reset needed).

## Files changed (only the two allowed code paths)
- tools/agent_supervisor/review_combiner.py  (replaced the one-line placeholder; 702 lines, SLOC under the 600 warn threshold — not flagged by modularity_check)
- tools/test_agent_supervisor_review_combiner.py  (new; 43 tests, no live provider calls)
The third allowed output (project-control/reports/M0-T169-producer-report.md) is orchestrator-saved; the producer did not write under project-control/ (forbidden to the producer). git show --name-only HEAD = exactly those two files.

## Design (how each rule is enforced in CODE, not by the model)
Public surface in review_combiner.py:
- Verdict vocabulary `PASS/FAIL/UNVERIFIED` with a severity order (PASS<FAIL<UNVERIFIED). `review_verdict(outcome)`: None or not-`ok` -> UNVERIFIED; an `ok` CONTINUE/COMPLETE with no blocking_findings -> PASS; everything else -> FAIL.
- `unverified_outcome(code, msg)` — wraps a reviewer that RAISED a launch exception as a decision-None FAIL outcome (honors M0-T168 note N1: a raised launch exception counts as FAIL).
- `CombinerInputs(frozen_head, diff_text, command_outputs, extra_shas)` — the deterministic, code-checkable evidence. `diff_new_lines()` parses the unified diff to the set of NEW-side line numbers per file; `has_sha()` matches a SHA that prefixes the frozen head or appears in the inputs.
- `evidence_present(evidence, inputs)` — True only for one of three checkable kinds whose target code confirms present: `file_line` (line in that file's diff hunks), `command_output` (exact substring of a supplied command output), `sha` (present per has_sha). Malformed/unknown/bool-line citations -> False.
- `CombinedFinding` (finding_id, source tag codex|claude, kind blocking|verdict|unverified, detail, refutable, refuted, refutation) and `CombinedReview` (verdict, findings, per-reviewer verdicts, frozen_head, model_used, accepted/rejected counts, notes) with JSON `to_dict()` preserving provenance.
- `_collect_findings(source, outcome)` — the UNION in code: a missing/untrustworthy review -> one NON-refutable `unverified` finding; an `ok` review -> one `blocking` finding per blocking_findings entry; a non-approve review that itemized none -> one synthetic `verdict` finding so a bare FAIL cannot vanish.
- `_apply_refutations` — accepts a proposed refutation only when it names a known, refutable finding AND `evidence_present` passes; otherwise the finding stays (counted rejected). An `unverified` finding is non-refutable and can never be dropped.
- `_worst_unrefuted_verdict` — PASS only when no finding survives; a surviving blocking/verdict -> FAIL; a surviving unverified -> UNVERIFIED.
- `ReviewCombinerConfig(enabled=False, model="", timeout_seconds=600)` + `from_mapping` (strict, unknown keys rejected, enabled only on real bool True, model must be str, timeout must be number) and `review_combiner_enabled(controller_config)` default-off helper (section key `review_combiner`).
- `ReviewCombiner.combine(...)` refusal order, all BEFORE any process: (1) model unset -> `combiner_model_unset`; (2) switch off -> `combiner_disabled`; (3) identity == producer/codex/claude reviewer -> `combiner_not_independent`; (4) frozen_head not a 40-hex SHA, or the two reviews pin different heads / a head != the frozen head -> `head_not_frozen` / `reviews_of_different_heads`. Then union-in-code, then (only if a refutable finding exists) invoke the model read-only via `claude_reviewer.build_argv` (grounded flags only; no guessed flag), parse `{"refutations":[...]}` defensively, apply only code-checked refutations, compute the worst unrefuted verdict. A model launch exception / timeout / unparseable output applies NO refutation (fail-safe).

Not wired in: nothing in loop.py / gate_wave.py / codex_reviewer.py / claude_reviewer.py imports or names review_combiner (asserted by a test). The combiner only reviews; it never records a gate (ADR-005).

## Each acceptance scenario and its proving test (tools/test_agent_supervisor_review_combiner.py)
- primary (union, source tags, worst verdict): `PrimaryUnionTests.test_two_pass_reviews_combine_to_pass_without_invoking_the_model` (both PASS -> PASS, model not called), `test_union_keeps_both_source_tags_and_worst_verdict` (two findings tagged codex+claude, verdict FAIL), `test_combined_review_is_json_serializable_with_provenance`.
- boundary (dropped only with code-checked evidence; uncited leaves it in): `RefutationEvidenceTests.test_file_line_in_diff_refutes_the_only_finding_then_pass`, `test_command_output_substring_refutes`, `test_short_sha_prefix_of_head_refutes`, `test_uncited_refutation_does_not_drop_the_finding` (MUTATION), `test_absent_file_line_refutation_is_rejected`, `test_wrong_file_line_refutation_is_rejected`, `test_refutation_for_unknown_finding_is_ignored`, `test_evidence_present_unit`.
- never weaker: `NeverWeakerTests.test_fail_plus_pass_never_combines_to_pass` (MUTATION), `test_non_approve_verdict_without_findings_still_fails`, `test_stop_for_owner_is_not_pass`, `test_halt_unsafe_with_fake_evidence_stays_fail`, `test_combined_pass_needs_every_blocking_refuted`.
- missing/ambiguous: `MissingOrAmbiguousTests.test_missing_review_is_unverified_never_pass`, `test_empty_review_is_unverified`, `test_timeout_review_is_unverified`, `test_raised_exception_review_is_unverified` (N1), `test_unverified_review_cannot_be_refuted_away`, `test_missing_review_finding_is_never_refutable_so_model_is_skipped`, `test_other_finding_refuted_but_missing_review_still_unverified`, `test_reviews_of_different_heads_are_refused`, `test_review_head_not_matching_frozen_head_is_refused`, `test_non_sha_frozen_head_is_refused`, `test_malformed_model_output_applies_no_refutation`, `test_model_launch_exception_is_fail_safe`, `test_model_timeout_is_fail_safe`.
- independence: `IndependenceTests.test_refuses_when_combiner_is_the_producer`, `test_refuses_when_combiner_is_the_codex_reviewer`, `test_refuses_when_combiner_is_the_claude_reviewer`, `test_distinct_identity_is_allowed`.
- settings/switch: `SettingsAndSwitchTests.test_config_defaults_off_and_model_unset`, `test_unset_model_refuses_before_any_process`, `test_default_config_refuses_model_unset`, `test_disabled_switch_refuses_even_with_a_model`, `test_review_combiner_enabled_is_off_by_default`, `test_from_mapping_strict_and_fail_closed`, `test_model_invocation_uses_the_read_only_reviewer_argv`, `test_nothing_in_the_loop_calls_the_combiner`.
- unit: `VerdictAndDiffUnitTests.test_review_verdict_mapping`, `test_diff_new_lines`.

## Commands run (venv /root/project/lanes-runtime/venv)
- `python -m pytest -q tools/test_agent_supervisor_review_combiner.py` -> 43 passed in 0.33s.
- `python -m pytest -q tools/test_agent_supervisor_claude_reviewer.py` -> 26 passed in 0.27s (imported reviewer).
- `python -m pytest -q tools/test_agent_supervisor_reviewer.py` -> 125 passed, 119 subtests in 64.03s (imported codex reviewer).
- `python -m ruff check tools/agent_supervisor/review_combiner.py tools/test_agent_supervisor_review_combiner.py` -> All checks passed!
- `python3 tools/modularity_check.py --check` -> selected 640 files; failures 0; warnings 27; EXIT=0; review_combiner.py NOT flagged (0 occurrences in the report).
- `git show --name-only HEAD` -> exactly the two allowed code files.

## Assumptions / judgment calls
- Verdict mapping: only CONTINUE and COMPLETE are approving (PASS). REVISE/HALT_UNSAFE/STOP_FOR_OWNER/ROTATE_SESSION are non-approvals treated fail-safe as not-PASS. A non-approve review with no itemized blocking finding gets a synthetic `verdict` finding so a bare FAIL cannot silently pass. This directly satisfies "if either review is FAIL ... never PASS" while still allowing the directive's "every blocking finding refuted with evidence -> PASS" path.
- Evidence kinds limited to the three the task names (file:line in the diff / command output / SHA), each checked deterministically. The combiner model is invoked via claude_reviewer.build_argv (the only grounded read-only argv); no CLI flag was guessed. The owner's R008 model choice is a required setting with no default — the combiner never picks or hard-codes a model.
- `combine()` refuses when disabled (combiner_disabled) in addition to the unset-model refusal — the strongest fail-closed reading of "a switch that defaults off". Model-unset is checked first so the default config surfaces `combiner_model_unset`.

## Limitations / could-not-do
- No live provider call: per CLAUDE.md the real Claude/Codex print-mode envelope is not re-verified here; tests inject a fake runner and prove the loop/argv/guards/parse, never the live CLI contract. Live enablement waits for the D-091 recertification (T3) and a preflight round-trip — consistent with the claude_reviewer posture and the default-OFF switch.
- Single module, cohesive, under the modularity warn threshold; no second module was needed.
- Did not run the full supervisor glob or test_directive_compliance (memory/time; CI runs the full glob). Did not push/merge/gh/project_control (orchestrator-only).

END-OF-REPORT

---

# Rework (M0-T169 G3/G5 FAIL — advisory-only redesign)

Both independent reviews FAILED the same safety property (G3-1, G5 B1/B2): the old evidence check verified only that a cited token was PRESENT somewhere, not RELEVANT. The frozen head SHA is present for every unit, so a model could drop ANY refutable finding (even a HALT_UNSAFE) and flip combined FAIL -> PASS — a prompt-injection hole breaking design §2 rule 4 (never upgrade FAIL to PASS). Orchestrator decision: make model proposals ADVISORY ONLY.

What changed in tools/agent_supervisor/review_combiner.py:
1. Model proposals are ADVISORY disputes, never refutations. A dispute whose evidence passes the hardened checks is RECORDED on the finding as `disputed=True` with the cited evidence + the model's reason + an "ADVISORY ONLY" note, but the finding is NEVER removed and the combined verdict is NEVER changed by it. Renamed CombinedFinding.refutable/refuted/refutation -> disputable/disputed/dispute; CombinedReview.refutations_* -> disputes_recorded/disputes_rejected.
2. The combined verdict is computed in code as `worst_verdict(review_verdict(codex), review_verdict(claude))` (PASS<FAIL<UNVERIFIED) — the worst of the two reviews' verdicts (union). FAIL+anything is never PASS; a single FAIL is never upgraded; the model cannot move it.
3. Hardened, finding-bound evidence (`evidence_supports_dispute(evidence, finding, inputs)`): `sha` counts ONLY when it is a supervisor-vouched `extra_shas` member AND is not the frozen head or any prefix of it (dropped `head.startswith` and the diff/outputs substring path — the G5 B1 primitive is gone); `file_line` must EQUAL the finding's own reported location (`_finding_location`: {file,line} or "path:line") AND be a real new-side diff line; `command_output` must be a substring of >= MIN_COMMAND_OUTPUT_EVIDENCE_CHARS (20) of a supplied output.
4. Synthetic `verdict` findings and `unverified` findings are non-disputable (disputable=False); only reviewer `blocking` findings can be disputed.
5. When enabled, an empty combiner identity is refused (`combiner_identity_required`) so the independence guard always runs; `_assert_independent` no longer early-returns on empty.
6. Docstring rewritten to state the true, stronger guarantee: the model can never drop a finding or change the verdict; disputes are advisory annotations for the human gate.
7. Prompt/instructions (COMBINER_INSTRUCTIONS, `_dispute_prompt`) rewritten: state the advisory role, hand the model `vouched_shas` (not the head as evidence), and require finding-bound evidence; model output key is `disputes` (legacy `refutations` still parsed).

Tests (tools/test_agent_supervisor_review_combiner.py, 47 cases) flipped/added per the orchestrator:
- Flipped the enshrining tests: the old test_command_output_substring_refutes / test_short_sha_prefix_of_head_refutes / the "aaaaaaa" case now assert REJECTION (no drop, verdict unchanged).
- Red/green: test_halt_unsafe_with_head_sha_citation_stays_fail_finding_present and test_full_frozen_head_sha_citation_is_rejected (B1); test_present_but_unrelated_file_line_is_rejected and test_present_but_trivial_command_output_is_rejected and test_file_line_not_in_diff_is_rejected_even_if_it_equals_location (B2); test_bound_file_line_records_an_advisory_dispute / _long_command_output_substring / _vouched_non_head_sha (valid bound citation -> disputed=True, finding present, verdict unchanged); test_a_valid_dispute_does_not_drop_the_finding_or_flip_to_pass and test_fail_plus_pass_is_always_fail (mutations); test_verdict_finding_cannot_be_disputed; test_unverified_finding_cannot_be_disputed; test_enabled_combiner_with_empty_identity_is_refused; evidence_supports_dispute/worst_verdict units.

Commands (venv): pytest tools/test_agent_supervisor_review_combiner.py -> 47 passed; pytest tools/test_agent_supervisor_claude_reviewer.py -> 26 passed; ruff check (both files) -> All checks passed!; modularity_check --check -> selected 640 files; failures 0; EXIT=0; review_combiner.py not flagged.

END-OF-REPORT
