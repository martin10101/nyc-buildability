<!-- Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
     (report-preservation rule, 2026-07-16). Transport entity-decoding only: the harness
     neutralized ">" as "&gt;" and "<" as "&lt;" in several spots; decoded back. -->

Independent review complete. All security behaviors verified by source inspection, regex probing, and re-run test suites (52 unit-G tests + 333 touched-surface regression tests, all passing at the frozen SHA). Below is the full G5 report.

---

# Gate Report

- Gate ID: G5 (security)
- Task ID: M0-T094 (D-024 unit G — operator channel)
- Reviewer: security-reviewer (independent, read-only)
- Producer: fable-orchestrator-session
- Result: PASS
- Clean environment/worktree used: reviewed at frozen deliverable SHA `f6edf11d74d5e126439ce804750bca4c1ccd7fa5` (HEAD `3c4b888` adds only `project-control/tasks/M0-T094.json`, verified control-plane-only); source inspection + regex probing + test re-runs on the primary checkout (temp-dir side effects only).

## Acceptance criteria reviewed

Scope granted to this gate (per campaign record and report §3): the NEW hook / skills / settings wiring plus the `ask` bridge and `status` section-14 extension. Verified the pre-existing guard packs are UNTOUCHED and that the new attack surface is safe. `git diff --name-only f6edf11~1..f6edf11` contains neither `.claude/hooks/agent_dispatch_guard.py` nor `.claude/hooks/readonly_agent_guard.py` — confirmed byte-identical (guards not in the deliverable diff).

## Directive/requirement verification

Security-relevant requirements independently re-derived from `project-control/directives/D-024-fable-codex-loop/requirements.json` at the frozen SHA. (Full per-requirement DCV over all 54 applicable reqs is the directive-compliance-verifier's pass; this table is my security-scoped verification.)

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R083 | f6edf11 | PASS | 8 `/loop-*` skills exist, each `disable-model-invocation: true`; thin CLI wrappers, not prompt-based commands; `/btw` explicitly excluded. `.claude/skills/loop-*/SKILL.md` |
| D-024-R084 | f6edf11 | PASS | Feature-detected via committed fixture; exact-token match, `decision:"block"`, prompt-erasure; no `additionalContext`/`hookSpecificOutput` (asserted by test S13). loop_command_interceptor.py:53-55,114-117 |
| D-024-R085 | f6edf11 | PASS | `ask` uses read-only Codex packet, grants no mutation tools; timeout → one durable request id. operator_ask.py:262-369; build_argv contract |
| D-024-R086 | f6edf11 | PASS | graceful-stop journals intent BEFORE ack (test `test_the_journal_write_precedes_the_acknowledgment_in_source`); emergency > graceful > pause; emergency-stop maps to existing verb. operator_channel_cli.py:63-98 |
| D-024-R087 | f6edf11 | PASS (1 MINOR hardening) | Exact match (probed), argv-only/no-shell, bounded I/O, UTF-8/metachar safe, repo-root+campaign identity, timeout+tree-kill, secret+control-seq redaction both directions, read-only Codex, no arbitrary exec, no background duplicate, digest-only audit. See MINOR-1 (status --json). |
| D-024-R088 | f6edf11 | PASS | Honest second-terminal fallback documented; zero-context proof carried `pending-owner-C1`, never faked; `ask` genuinely added (was absent from CLI). |
| D-024-R089 | f6edf11 | PASS | Idle/active behavior tested; queued input NOT advertised as real-time (fixture `queued_input_behavior`, test asserts). |
| D-024-R111 | f6edf11 | PASS | Full §16.5 matrix present S1–S14 incl. metachar/Unicode/quoted/multiline/empty/oversized, terminal-escape both directions, timeout single-request, hook fail-closed, exact-match-only, distinct ids. 52/52 pass. |
| D-024-R149 | f6edf11 | PASS | Installed-version fixture `loop_interception_detection_2_1_248.json`; unproven UserPromptExpansion carried, not adopted. |
| D-024-R158 | f6edf11 | PASS | Thin owner controls as skills with `disable-model-invocation: true`. |
| D-024-R159 | f6edf11 | PASS | UserPromptExpansion tested-but-unproven → UserPromptSubmit honest path; no `/loop` collision (probed `/loop` passes through). |

## Steps independently executed

1. `git diff --stat f6edf11~1..f6edf11` and `git diff --name-only … | grep guard` — guards not in diff; HEAD delta is task-file only.
2. Read every new/changed file: interceptor hook, operator_ask.py, operator_status.py, operator_channel_cli.py, cli.py/durable_state.py diffs, settings.json, all 8 SKILL.md, fixture, schema, test file, reports.
3. Traced the reused read-only contract: `codex_reviewer.build_argv` (`--sandbox read-only`, `FORBIDDEN_REVIEWER_FLAGS`) → `process.assert_argv_safe` (no shell strings/NUL/hard-deny/effort/owner-activation) → `process.run` minimal_env + Job-Object/taskkill/killpg tree termination → `redaction.redact_text/redact_structure` + `models.digest_of` (SHA-256).
4. Probed the command regex against injection edge cases (embedded/second-line control tokens, metachar suffixes, substring near-misses).
5. Ran `tools/test_agent_supervisor_operator_channel.py` → 52 passed.
6. Ran touched-surface regression: command_authority+reviewer → 110 passed; controller_succession+phase1+start_reentry → 171 passed.
7. `python tools/modularity_check.py --check` → 0 failures.
8. Scanned committed unit-G artifacts for literal secrets and home-path leaks.

## Expected versus actual

| Property | Expected | Actual |
|---|---|---|
| Prompt-injection into controls | Only exact whole-prompt `/loop-<verb>` triggers | Confirmed: `hello\n/loop-emergency-stop`, `please /loop-stop`, `/loop-status;x`, `/loop-statuses`, `/loop` all pass through untouched; only exact tokens intercept |
| Shell injection | argv arrays, shell=False, question as ONE element | Confirmed; question travels on stdin inside packet, absent from argv (test asserts); metachars are data |
| Read-only Codex / no mutation | `--sandbox read-only` forced, forbidden flags refused | Confirmed in build_argv + assert_argv_safe; minimal_env for child |
| Audit privacy | Digests + sizes only, no raw Q/A | Confirmed; test asserts raw "lot 42" absent from audit.jsonl |
| Timeout → no duplicate/zombie | Tree killed, ≤1 durable row | Confirmed (Windows Job-Object kill-on-close; hung-supervisor test kills+reports); resubmit keeps same row |
| Output disclosure | Redaction before display, fail-closed | Confirmed for hook (`_bound_for_display` fail-closed) and text CLI; see MINOR-1 for `status --json` |
| Denial | Hook errors never break prompt flow | Confirmed; `main()` always returns 0; malformed/oversized payloads pass through |
| Settings wiring | Additive, guards intact | Confirmed additive; interceptor first on UserPromptSubmit; PreToolUse guards unchanged |

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\loop_command_interceptor.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\operator_ask.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\operator_status.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\operator_channel_cli.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\cli.py` (status §14 + verb registration)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\durable_state.py` (`ask_by_id`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\codex_reviewer.py` / `process.py` / `redaction.py` / `models.py` (reused contract)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\settings.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\skills\loop-*\SKILL.md` (8)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\loop_interception_detection_2_1_248.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\schemas\operator_ask_answer.schema.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_operator_channel.py`

## Human-style walkthrough findings

The operator channel behaves as documented: exact `/loop-*` commands are consumed pre-model and their bounded, redacted result is displayed via the block reason; near-miss/embedded text falls through to the model unchanged; controls outside the campaign repo and `/loop-ask` without provider env fail closed with the exact second-terminal command to run. Non-security UX nit (not a finding): a `/loop-status`-plus-trailing-text prompt is intercepted and the trailing text dropped (named as ignored chars) rather than passed to the model — this is the safer outcome and is intentional.

## Regression/security/provenance findings

Cross-tenant isolation, service-role secrecy, private storage, and SSRF are **N/A for this diff** — the unit is a local operator-control channel over the supervisor CLI with no Supabase/network/storage/outbound-URL surface. The only external process is the read-only, minimal-env Codex reviewer. Least privilege (read-only sandbox, minimal env, fail-closed), prompt-injection defense (whole-prompt exact match + `disable-model-invocation`), and log redaction were the focus and are verified below.

**MINOR-1 — `status --json` emits the payload without `redact_structure`; unit G routes the new `section14` (and its own graceful-stop reason) through that unredacted path.**
`tools/agent_supervisor/cli.py:1537-1538` prints `json.dumps(payload, indent=2)` with no redaction, whereas the sibling text path at `cli.py:1554-1556` correctly wraps `render_concise(payload["section14"])` in `redact_structure`. Unit G adds `"section14": compose_status(...)` (cli.py:1534), composed from durable records that can contain sensitive owner text — most concretely the **graceful-stop reason**, which unit G's own `set_graceful_stop` stores verbatim (`stop_intent.py:85`, no write-time redaction), plus session records and transition details. Attack scenario: owner runs `/loop-stop pausing to rotate <token-shaped string>`, then later runs `status --json` and pastes/commits the output to this PUBLIC repo — the token-shaped reason appears unredacted, while the same reason is masked on the text path and (doubly) via the `/loop-status` hook. This contradicts the project's own M0-T079 C2 rule ("stdout is a TRANSMISSION, so it obeys redaction") that `emit_payload` embodies. Mitigating context, why this is MINOR not MAJOR: (a) the unredacted `--json` path is **pre-existing** (checkout, runtime_dir, `open_asks` questions, transition details were already emitted raw); (b) the owner-facing operator channel — the `/loop-status` hook — uses the redacted text path plus `_bound_for_display`, so the delivered control surface is safe; (c) `section14` reads **no** environment variables and adds **no** new absolute path (the checkout path was already in the payload). **Recommended one-line correction** (schedule as a follow-up; does not block this gate): `print(json.dumps(redact_structure(payload).value, indent=2, default=str))`, matching `emit_payload`.

**ADVISORY-1 — env-var trust for `/loop-ask`.** The hook trusts session `SUPERVISOR_CODEX_EXECUTABLE`/`SUPERVISOR_CONFIG`/`SUPERVISOR_MODEL_SELECTION` (loop_command_interceptor.py:171-189) for the Codex path. Acceptable: setting session env already implies process control (equivalent to code exec), it mirrors the second-terminal CLI's `--codex-executable`, execution is `shell=False`, and it fails closed when any of the three is unset. No new privilege.

**ADVISORY-2 — `/loop-ask` question is a positional argv element that may begin with `-`.** loop_command_interceptor.py:187-189 passes `argument` as one element after `ask`. A question starting with `-` (e.g. `/loop-ask --show`) is seen by argparse as an option and errors out — fail-closed, only a confusing message. A single argv element **cannot** be split into flag+value, so `--show`/`--resubmit` cannot be smuggled and no durable row can be read via the hook. Hardening: insert a `"--"` end-of-options separator before the question.

**ADVISORY-3 — hook subprocess tree-termination on POSIX.** The hook uses plain `subprocess.run(timeout=…)` (loop_command_interceptor.py:203-206), which SIGKILLs only the direct child. For `/loop-ask` (the only verb spawning a Codex grandchild) the 45 s hook timeout precedes the 90 s ask window; on Windows (production) the ask CLI's kill-on-close Job Object reaps the Codex child when the parent dies, but on POSIX (dev/CI) a **read-only** Codex grandchild could briefly orphan. No duplicate durable request is created (queue-on-timeout needs the parent alive). Hardening: reuse `ProcessContainer` or `start_new_session` + process-group kill for the hook's own child.

**ADVISORY-4 — repo-wide `[HOME]`-masking.** The owner's absolute path `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` and Windows username appear at `project-control/reports/M0-T094-operator-channel.md:148` and are already pervasive across 30+ committed report/doc files (including prior accepted G5 reports and SESSION_HANDOFF.md). Pre-existing repository practice, not a unit-G regression; low sensitivity (not a credential). A repo-wide masking pass is an owner-discretion cleanup, out of scope for this gate.

**Positive confirmations (verified, not merely claimed):**
- Guard packs untouched in the deliverable commit.
- Exact-token matching holds against injection (probed): embedded/second-line control tokens never fire — the interceptor only ever sees the literal user prompt and requires the entire stripped prompt to equal `/loop-<verb>`; retrieved-content/prompt-injection cannot trigger a control.
- Model cannot self-invoke any control (all 8 skills `disable-model-invocation: true`); the ask packet instruction is worker-text-clean.
- Read-only Codex contract intact end-to-end; `ask` grants no mutation tools; question never enters argv.
- Redaction both directions + size bounds; audit records digests only (raw text absent).
- Durable ids `oper_`+16 hex (64-bit, collision-resistant); `ask_by_id` uses a parameterized query (no SQLi); `show_ask` refuses non-`oper_` ids (read-scope bounded away from broker rows); resubmit and second-timeout keep exactly one row.
- settings.json additive; hook emits only `{decision, reason}` (no context injection); hook `main()` always returns 0 (never breaks prompt flow).
- Test secrets built at runtime only (`"ghp_" + "a1B2"*5`) — no committed literal matches gitleaks/redaction patterns.
- Modularity: 0 failures; four focused new modules (232/400/279/244 SLOC).
- No regressions: 52 + 110 + 171 = 333 tests pass at the frozen SHA.

## Defects

None blocking. One MINOR (MINOR-1, `status --json` redaction — pre-existing path expanded by section14; recommended one-line fix) and four ADVISORY hardening items.

## Required rework

None required to pass this gate. Recommended (non-blocking) follow-ups, in priority order: MINOR-1 (route `status --json` through `redact_structure`), ADVISORY-2 (`--` separator in the loop-ask argv), ADVISORY-3 (process-group kill for the hook child). MINOR-1 should be carried as a tracked hardening item since unit G's own graceful-stop reason is a new sink into the unredacted JSON path.

## Reviewer conclusion

The unit-G operator channel is soundly designed for its threat model. The headline security property for this unit — prompt-injection cannot drive control actions — holds strongly: only a whole-prompt exact `/loop-<verb>` token intercepts, the hook sees only the literal user prompt, and the model cannot self-invoke the skills. The `ask` bridge faithfully reuses the hardened read-only Codex contract (no mutation tools, argv-only, minimal env, tree-terminated timeout, digest-only audit), input/output are bounded and redacted both directions, identity is validated, and every failure path fails closed with a visible second-terminal instruction. The guard packs are untouched and the settings/skills wiring is additive and user-only. The single MINOR is a pre-existing unredacted `status --json` path that unit G expands with `section14`; it does not compromise the reviewed control surface (the operator hook is redacted) and warrants a one-line follow-up rather than blocking.

VERDICT: PASS
