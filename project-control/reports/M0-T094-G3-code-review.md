<!-- Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel
     (report-preservation rule, 2026-07-16). Transport entity-decoding only: the
     harness neutralized ">" as "&gt;" in one table row; decoded back here. -->

I have completed my independent review. Reused surfaces verified genuine, 52/52 tests reproduced on Python 3.11, ruff (CI 0.13.0) clean on touched files, modularity 0 failures, regression slice green. Here is my full G3 report.

---

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M0-T094 (D-024 unit G — operator channel)
- Reviewer: code-reviewer (read-only)
- Producer: fable-orchestrator-session
- Result: **PASS**
- Clean environment/worktree used: reviewed at deliverable SHA `f6edf11d74d5e126439ce804750bca4c1ccd7fa5` (HEAD `3c4b888` adds only the control-plane submit event); primary checkout `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, read-only.

## Acceptance criteria reviewed

Scenario pack S1–S14 + owner-gated C1 from `project-control/reports/M0-T094-operator-channel.md` §1, plus the six declared gaps in §4.1 (ask verb, graceful-stop verb, section-14 status fields, 8 thin skills, interception hook, R035 alias doc). All reviewed against the actual diff, not the producer's conclusion.

## Directive/requirement verification

Full 54-requirement re-derivation against D-024 source is the `directive-compliance-verifier` pass recorded in `verification.json` (producer ≠ verifier); this G3 confirms the code-level satisfaction of the behavior-bearing requirements the packet names. Every one I could exercise reproduces:

| Requirement | Code identity @ f6edf11 | Verdict | Reproduced evidence |
|---|---|---|---|
| R035 (start alias) | `cli.py` module docstring + `start` help; `loop-start/SKILL.md` | PASS | `test_the_owner_intent_alias_is_documented_verbatim` |
| R027/R036 (no-duration idempotent start) | `cmd_start` rides `SingleInstanceLock`; `--run-wall-clock-seconds` default `None` | PASS | S1 tests; `git` diff shows no new start machinery |
| R034/R042/R094/R095 (section-14 status) | `operator_status.compose_status` reads only durable records; every fact `{value,source,confidence}`; absent = `unknown` never zero | PASS | S2 (5 tests), incl. `test_absent_facts_are_unknown_never_zero`, `test_persisted_measurements_keep_their_own_confidence_label` |
| R036/R086 (durable-before-ack) | `operator_channel_cli.cmd_graceful_stop` journals via `stop_intent.set_graceful_stop` before `emit_payload` | PASS | S3 source-order + round-trip tests |
| R027 precedence (emergency>graceful>pause) | reuses unit-F `stop_intent.effective_intent` | PASS | `test_emergency_outranks_graceful_and_both_stay_durable` |
| R085/R087/R104 (bounded read-only ask + durable fallback + single-window) | `operator_ask.run_ask` reuses `codex_reviewer.build_argv` (`--sandbox read-only`, forbidden-flag refusal), `process.run` (tree-kill on timeout), `models.QueuedAsk`/`queue_ask`/`resolve_ask`, `redaction` | PASS | S4/S5/S6 — argv is read-only reviewer contract; timeout → one `oper_*` row; `--resubmit` same row; tree_terminated true |
| R087/R111 (bridge security matrix) | `sanitize_question`/`bound_answer` strip C0/CSI/OSC both directions, redact, bound; identity + tampered-campaign refusal; byte-bounded packet | PASS | S6 (11 tests) all reproduce |
| R083/R158/R159 (thin user-only skills, no `/loop` collision) | 8 `SKILL.md` with `disable-model-invocation: true`, CLI-calling bodies, no `/loop` dir, no `/btw` | PASS | S7 tests |
| R084/R088/R149 (feature-detected interception, honest proof) | `loop_command_interceptor.py` consults committed fixture; UserPromptSubmit selected; UserPromptExpansion passed-through unfaked; zero-context proof `pending-owner-C1` with second-terminal fallback | PASS | S8/S9/S11 + fixture |
| R084/R111 (exact-match only) | anchored `_COMMAND` regex | PASS | S10 — `/loop-statuses`,`loop-status`,`/Loop-Status`,mention forms all pass through |
| R087/R111 (hook fail-closed) | malformed→pass-through; identity-fail/broken/hung supervisor→`block` with visible reason; timeout kills child | PASS | S12 (4 tests) |
| R045/R184 (no worker pollution) | packet instruction `assert_worker_text_clean`; hook has no `additionalContext`/`hookSpecificOutput`, pass-through emits nothing | PASS | S13 |
| R087/R125–R128 (Gate-0 identity) | `validate_identity` markers + machine-validated campaign records; hook `_repo_root` markers | PASS | S14 — module/CLI(exit 11)/hook levels |

## Steps independently executed

- `python -m pytest tools/test_agent_supervisor_operator_channel.py -q` → **52 passed** (Python 3.11.9). Producer's "51/51" in the operator-channel report understates; G2 self-check's "52/52" is correct.
- `python -m ruff check` (CI 0.13.0) on all six touched code files → **All checks passed**.
- `python tools/modularity_check.py --check` → **failures 0** (cli.py symbol-ceiling warn and durable_state review-signal warn are pre-existing, not new failures).
- Regression slice `command_authority + controller_succession + reviewer + start_reentry` → **201 passed** (moved `_open_runtime`/`_emit` behavior-neutral).
- Reuse verification by reading each cited surface: `codex_reviewer.build_argv` (signature + forbidden-flag refusal + `--sandbox read-only`), `process.run` (tree-kill on timeout sets `tree_terminated`), `stop_intent.set/clear_graceful_stop` + `effective_intent`, `redaction.redact_text/redact_structure`, `models.QueuedAsk`, `policy.resolve_model.usable`, `refusals` exit-code map 10–16, `durable_state.queue_ask/open_asks/resolve_ask/ask_by_id`.
- Confirmed hook entry points exist: `tools/agent_supervisor/__main__.py` and `campaign_continuity.main --status`; no duplicate `ask`/`graceful-stop` subparser in cli.py.
- Confirmed the raw-JSON status line pre-existed at parent (`git show f6edf11^:...cli.py`).

## Expected versus actual

All reproduced results match the producer's claims except the "51/51" count (actual 52, i.e. producer understated). Reuse claims in §0/§4.1 are accurate: no hidden parallel machinery — `operator_status` only reads existing durable keys, `operator_ask` reuses the reviewer/process/redaction/queue surfaces, the hook imports `bound_answer` rather than re-implementing redaction.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\operator_ask.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\operator_status.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\operator_channel_cli.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\cli.py` (lines 227–235 imports; 1531–1557 status; 1802–1806 helper-move stub; 3383 register)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\durable_state.py` (655–672 `ask_by_id`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\loop_command_interceptor.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\settings.json` (UserPromptSubmit registration)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\schemas\operator_ask_answer.schema.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\loop_interception_detection_2_1_248.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_operator_channel.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\skills\loop-*\SKILL.md` (8)

## Human-style walkthrough findings

Not a UI task; the /human-walkthrough / C1 live-interception canary is owner-gated (R192/R197) and correctly deferred. The fixture states `zero_context_proof=pending-owner-C1` and `queued_input_behavior=pending-owner-C1`, advertising the second-terminal CLI as the real-time path — the truthful fallback R088 explicitly permits. This is not a code defect and does not block G3.

## Regression/security/provenance findings

- Redaction is applied on the concise status path, on both new operator verbs (via `emit_payload`), on refusals (via `refusals.emit`), in the ask packet (`redact_structure(compose_status(...))`), in the sanitizer/bounder, and defensively again in the hook display (`_bound_for_display`, fail-closed to a withheld-message if the redaction import fails). No credential-class value is placed on a raw path by the new code.
- Supervisor-freeze qualifying evidence `D-024-R104 (Phase F)` cited in both the packet objective and the commit message (rule §3 satisfied).
- Composed whole-suite baseline `M0-T094-full-suite-T1.txt` = 2971 passed / 3 skipped / 0 failed, meeting the ≥1165 supervisor-freeze duty. CI supervisor-bridge on the pushed SHA is the confirming single-run evidence (not re-run here — orchestrator-captured).

## Defects

None BLOCKING or MAJOR.

**MINOR-1 — `status --json` emits the composed `section14` unredacted while the concise path redacts the same data.**
`tools/agent_supervisor/cli.py:1537-1538` prints `json.dumps(payload, indent=2)` raw; `payload["section14"]` (added at 1534) now carries new durable records not previously on the status JSON surface (`claude_session`/SESSION_KEY, `subagents`/CHILD_PROCESSES_KEY, `controller_lease`, `model_override`, `model_selection_digest`, `usage_limit_record`, campaign authority/restrictions, and `current_task.detail` verbatim). The concise path at `cli.py:1554` wraps the identical section14 in `redact_structure`, and the module's own `emit_payload` doctrine (docstring: "stdout is a TRANSMISSION … M0-T079 routed a raw PAT-bearing remote into the log") treats stdout as redact-required.
Failure scenario: a token-shaped string embedded in a transition `detail` or a child-process argv would print unmasked via `python -m tools.agent_supervisor status --json`, whereas `status` (concise, the default) masks it.
Mitigating context (why MINOR, not MAJOR/blocking): the raw `json.dumps(payload)` status path pre-existed unit G (confirmed at `f6edf11^`), `last_transition` already exposed the same raw transition `detail`, six cli.py handlers share this "command's own `--json` is the raw operator diagnostic view" convention, and none of the new fields is a credential type. Recommended correction (defense-in-depth, non-blocking): route the section14 (or the whole status payload) JSON output through `redact_structure`, matching the concise path and `emit_payload`.

## Required rework

None required for G3 PASS. Recommended (track, non-blocking):
1. MINOR-1: redact the `status --json` output (align with the concise path / `emit_payload` doctrine) — defer to the security-reviewer (G5) for whether the redaction invariant is hard on this command.
2. ADVISORY: correct the "51/51" figure in `M0-T094-operator-channel.md` §intro (line 8) and §4.3 (line 125) to 52 to match reality and the G2 self-check.

## Advisory observations (non-defects)

- Argument-tolerant interception: an argument-less verb followed by conversational text (e.g. `/loop-status why is it broken?`) still executes `status` and blocks the prompt from the model, with the ignored characters named in the header (`loop_command_interceptor.py:194-200,215-217`). This is deliberate and documented ("failing open to the model would forfeit the control"); the prompt is not silently swallowed. Acceptable.
- AskError input-validation codes (`empty_question`, `question_too_large`, `bad_window`, `packet_too_large`, `no_answer`, `answer_empty`) map to refusal outcome `STALE_STATE` / exit 13 (`operator_channel_cli.py:164-169`). Exit 13 ("a fact the run needs is missing or ambiguous") is a loose but defensible fit given no dedicated bad-input code exists; the precise `reason_code` disambiguates. Acceptable.

## Reviewer conclusion

The deterministic core is correct and the security-shaped surfaces are genuinely reused, not re-implemented (R018 held): `build_argv` gives the read-only reviewer contract, `process.run` gives no-background-duplicate tree termination, `stop_intent` gives durable-before-ack graceful stop, `redaction`/`QueuedAsk`/`resolve_model`/`campaign_continuity` are consumed as-is. The helper move (`open_runtime`/`emit_payload` → `operator_channel_cli`, re-imported as `_open_runtime`/`_emit`) is behavior-neutral (bodies identical, call sites unchanged, `AUDIT_FILENAME` drift pinned by test, 201-test regression green, no new unused imports). Status composition is honest (unknown never zero, measurements keep their own confidence label). The hook is exact-match, fail-closed, and does not pollute model context. Feature detection is honestly recorded with the R088-permitted second-terminal fallback; the C1 canary is correctly owner-gated. 52/52 matrix reproduced, ruff clean, modularity 0 failures. The single MINOR (unredacted `status --json` section14) is pre-existing convention broadened by new fields and is a recommended defense-in-depth correction, not a blocker.

VERDICT: PASS
