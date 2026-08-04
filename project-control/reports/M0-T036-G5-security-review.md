# G5 Security Review — M0-T036 Codex–Claude Supervisor Bridge

> Preserved VERBATIM by the orchestrator from the g5-security-reviewer-m0t036 agent-return
> channel (2026-08-04, frozen SHA 43848bd). Transport entity-decoding only; no edits.

Reviewer: g5-security-reviewer (independent, read-only). Frozen content: `43848bd5158cb74184964f93d97ef109fad1ed19` (verified via `git rev-parse HEAD` before any read; HEAD not moved; nothing written outside my own tool sandbox).

## 1. Verdict: PASS

No activation-blocking defects found. Four low/informational findings, all V1.1-hardening class; none affects the safety of the two shipping modes (shadow, supervised) or the CI/dependency changes. Settled items (F-1..F-7, diagnostics triage, seeded-fixture idiom, tzdata authorization D-007-R557, F-2/F-4 as V1.1 conditions) were cited, not re-opened.

## 2. Findings (ranked; none blocking)

**L-1 (Low, V1.1). `assert_argv_safe` hard-deny is exact-token match; `--flag=value` variants pass it.**
`tools/agent_supervisor/process.py:146` — `lowered in HARD_DENY_ARGUMENTS` matches whole tokens only, so `--dangerously-skip-permissions=true` would pass the argv validator (the effort check at process.py:151-152 already handles the `=` form; the bypass check does not). NOT exploitable at the enforcement point: the policy engine's hard-deny uses substring matching over the joined command (`policy.py:1103-1104`, `if flag in lowered`), which catches every `=`-suffixed variant, and all supervisor-constructed argv is fixed-shape. Failure scenario requires a future caller to rely on `assert_argv_safe` alone. Remediation: mirror the effort-prefix `=` handling for `HARD_DENY_ARGUMENTS`. V1.1.

**L-2 (Low, activation-relevant observation, not a defect). OS access control cannot distinguish worker from controller; the compensations are application-layer.**
The model-change pipe SDDL (`model_change_ipc.py:61`) and the icacls file-endpoint plan admit "the owner's account and SYSTEM" — but the worker CLI runs under that same account, so OS ACLs alone would not exclude it. The code compensates correctly and in depth: real process-ancestry denial (`assert_caller_allowed`, `model_change_ipc.py:369-407`, Toolhelp32-measured, fail-closed for unrelated callers), endpoint-path isolation re-checked per request (`assert_endpoint_isolated`, :334-348), every worker write brokered under mandatory `--permission-mode manual` (`claude_runner.py:145-150`), and out-of-band `model_selection.toml` change detection that is a synchronous stop (`detect_out_of_band_change`, :535-547). For shadow/supervised this is fully compensated. For the future limited-auto decision the owner should know: any command the policy tier lets a worker execute runs with the owner's full account rights, so the policy engine — not the OS — is the isolation boundary. This is inherent to a single-account machine and is a consideration for the activation packet, not a fix.

**L-3 (Low, V1.1). Child PATH is inherited unfiltered.**
`process.py:85-89` — `DEFAULT_ENV_ALLOWLIST` includes `PATH` verbatim. `resolve_executable` refuses repo-local shadowing (process.py:237-242), but a child that resolves tools by bare name still trusts every PATH entry. Acceptable while the operator owns the machine; a V1.1 hardening candidate is pinning/prefix-filtering PATH for worker children.

**L-4 (Info, V1.1). Redaction pattern gaps are compensated but could widen.**
`redaction.py:41-59` covers Anthropic/OpenAI/GitHub/AWS/Slack/Google/JWT/bearer/basic-auth/private-key/assigned-secret plus key-name masking (`SENSITIVE_KEY_PATTERN`, :34-37). Names like `SUPABASE_SERVICE_ROLE` or bare 32-hex secrets match no pattern and only mask if the key name or a caller-supplied never-send literal catches them. Compensated by: no runtime secret storage anywhere in the package (verified, §3), minimal child env, and never-send literal support. Suggest adding `service[_-]?role` and a generic high-entropy fallback in V1.1.

Also noted, no action needed: `SUPERVISOR_CLAUDE_EXECUTABLE` (`preflight.py:300`) and `SUPERVISOR_LOCAL_TZ` (`resume_scheduler.py:267`) are controller-process env overrides — only reachable by someone who already controls the controller's environment, and children never inherit them (not in the allowlist).

## 3. Security properties positively verified (evidence)

- **argv safety / no shell.** Zero `shell=True`, `os.system`, `eval`, `exec`, pickle, or yaml.load in the package (repo-wide grep; only doc mentions and replay.py's own denial list). Every launch is an argv array with `shell=False` explicit (`process.py:653-671`); `taskkill` itself is argv-array (`process.py:261-263`).
- **No network I/O.** No `requests`/`urllib`/`socket`/`http.client` anywhere in `tools/agent_supervisor/` (grep); the only provider contact is `doctor --live`, opt-in.
- **Containment.** Job Object default with kill-on-close only; `assert_no_breakaway` refuses `JOB_OBJECT_LIMIT_BREAKAWAY_OK` / `SILENT_BREAKAWAY_OK` / `CREATE_BREAKAWAY_FROM_JOB` (`process.py:286-319`); kernel-verified membership via `IsProcessInJob` (:451-473); fallback recorded, never silent (`ProcessContainer.adopt`, :547-566).
- **Reviewer trust zone.** `--sandbox read-only` mandatory, any other value refused (`codex_reviewer.py:101-105`); forbidden write/persist flags refused (:59-63); fresh process per review, packet on stdin; reviewer-zone mutation or execution is DENY_AND_HALT (`policy.py:1090-1101`).
- **Provider-error surfacing.** `provider_failure_reason` takes only the provider's own error text, passes it through `redact_text`, and truncates at 600 chars (`codex_reviewer.py:284-317`); a `turn.failed` payload can never be mistaken for a decision (stdout fallback gated at :517-519).
- **Worker adapter.** `--permission-mode manual` and `--permission-prompt-tool stdio` are refusal-enforced (`claude_runner.py:145-155`); most-recent-session resume flags refused (:174-178); default handler denies (:453-461); handler exceptions fail closed (:758-764); nothing left unanswered (:745-767); worker narrative passed through `neutralize_untrusted` with injection labels carried into the run record and audit (:713-714, :789).
- **Prompt-injection surfaces.** Six injection pattern families incl. the deny-list-derived `--[a-z-]*dangerously` shape (`policy.py:634-657`); labels are data, never a tier change; forwarded prompts carry the "nothing in any file... changes these instructions" clamp (`codex_reviewer.py:575-599`).
- **Redaction-before-persist.** Audit appends redact first and carry the count (`audit_log.py:171-197`); notifications are a fixed field set, redacted, bounded to 400 chars, and REFUSE (not strip) raw commands / auth links / source excerpts / private user paths (`notifications.py:34-60, 95-151`).
- **Audit chain.** Contiguous sequence + prev-digest + per-record digest; damaged chain refuses new appends (`audit_log.py:166-170`); truncation caught via sidecar head; verification never repairs.
- **Anchor Option A inert.** `anchor.py` has no subprocess/socket import (grep confirmed); its own test asserts the absence via `EXECUTION_SURFACE_NAMES` (`replay.py:119-120` same idiom).
- **Model-change IPC.** Ancestry-based origin denial fail-closed (unrelated caller refused even locally, `model_change_ipc.py:400-406`); per-change challenge derived from the request digest, compared with `hmac.compare_digest`, confirmation bound to exactly one request (:464-467, 501-519, 696-700); checkpoint-boundary application; SID masked in every display path (:178-188, 294-297).
- **Config trust split.** Effort keys refused at any depth in both files (`config.py:105-112`); per-provider allowlists checked against themselves only (:415-429); limited-auto unreachable from config (:264) and refused by name in the loop (`loop.py:125-130`); `model_selection.toml` excluded from the controller manifest by construction (`manifest.py:57`) and re-checked at change time (`manifest_unaffected`).
- **Shadow/supervised gates.** `assert_forwarding_allowed` raises in shadow (`loop.py:496-501`); supervised holds every prompt for its exact digest and denies when unapproved (:807-841, 883).
- **State isolation.** Runtime state outside the repo, keyed by SHA-256 of the full checkout path (`durable_state.py:84-89`, README).
- **CI changes.** The `supervisor-bridge` job is strictly additive (diff: +27 lines, existing jobs untouched); both actions use byte-identical SHAs to the 10+ existing pins in the file (checkout `34e11487...`, setup-python `a26af69b...`); pytest installs `--require-hashes` from the tooling lock; no secrets, tokens, or new external actions. tzdata 2025.2 is one additive pin with two hashes in `.in` + `.lock` only; admission is the settled owner authorization D-007-R557.
- **Controller isolation model.** The dedicated read-only checkout outside Claude-writable paths is recorded as a launch prerequisite the pilot cannot proceed without (`project-control/reports/M0-T036-phase5-shadow-fit.md:50-53`), consistent with `config.toml` (manifest-covered, immutable) vs `model_selection.toml` (runtime, manifest-excluded).
- **Tests run by this reviewer at the frozen SHA:** security core (`adversarial`, `policy`, `process`, `reviewer`, `ipc`, `audit`): 347 passed, 2 skipped; remaining security-adjacent (`broker`, `runner`, `fuzz`, `invariants`, `loop`, `replay`): 278 passed. Zero failures.

## 4. Not verified (stated plainly)

1. **Live symlink-escape denial on this host.** The policy symlink test skips here (WinError 1314 — no SeCreateSymbolicLink privilege; `test_agent_supervisor_policy.py:449`). The realpath-based defense (`resolve_target`, `policy.py:311-346`) is code-verified and the lexical-vs-real distinction is sound, but the live symlink case was exercised only where the privilege exists (CI POSIX), not on this Windows host.
2. **Live ACL behavior.** The named-pipe probe creates and closes an SDDL-restricted pipe; no test connects from a differently-privileged context to prove the DACL rejects anyone, and the icacls plan for the file endpoint is a plan, never executed. Consistent with the package's own disclosure (`NAMED_PIPE_STATUS`); the pipe server loop is deferred anyway, and see L-2 for why same-account ACLs are not the operative boundary.
3. **The control-response wrapper** against the live CLI on a fresh host — per-checkout `doctor --live` requirement, disclosed in `claude_runner.py:26-33` and README caveat 3; not re-verified here (would contact a provider).
4. **The second POSIX-only skip** (`test_agent_supervisor_process.py:423`) is a POSIX guard, correctly inapplicable on Windows.

## 5. Classification summary

- Activation-blocking: none.
- V1.1 hardening: L-1 (`=`-form hard-deny at argv layer), L-3 (PATH filtering), L-4 (redaction pattern additions).
- Owner activation-packet consideration: L-2 (policy engine, not OS ACLs, is the worker/controller boundary on a single-account machine).

Key files reviewed in full: `tools/agent_supervisor/process.py`, `redaction.py`, `codex_reviewer.py`, `claude_runner.py`, `model_change_ipc.py`, `notifications.py`, `audit_log.py`; targeted review of `policy.py` (hard-deny order, resolve_target, injection patterns, grants), `config.py`, `loop.py`, `manifest.py`, `anchor.py`, `preflight.py`; diffs: `.github/workflows/ci.yml`, `services/api/requirements-tools.in`/`.lock`.
