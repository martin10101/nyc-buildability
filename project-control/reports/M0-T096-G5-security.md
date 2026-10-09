# G5 Security Review — M0-T096 (D-024 unit I)

> Verbatim reviewer return (security-reviewer agent, read-only, dispatched at frozen HEAD
> `1a935fb`; transport entity-decoding only — `&lt;`/`&gt;` from the return channel rendered
> as `<`/`>`). Recorded by the orchestrator.

## Identity (verified)

- Repository: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`
- Branch: `control/D-024-fable-codex-loop`
- HEAD (`git rev-parse HEAD`): `1a935fb2f6f5859da6418fd6750733be3e7589c7` — matches the frozen packet identity.
- Deliverable code commit: `5ff7f08`. Changed code surface over `2ae057b..5ff7f08` reproduced exactly: `M tools/agent_supervisor/cli.py` (+46/-8), `A tools/agent_supervisor/golden_run.py` (407), `A tools/agent_supervisor/live_observation.py` (451), `A tools/test_agent_supervisor_golden_run.py` (1017). Control-plane commits `5ff7f08..1a935fb` touch only `project-control/**` (directives, gates, reports, state, tasks) — no source, no hooks, no settings, no CI, no dependency manifests.

## What I executed

- `git rev-parse HEAD` / `git diff --name-status 2ae057b..5ff7f08` and `..1a935fb` (read-only) — surface + boundary confirmation.
- `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → `40 passed in 16.21s`.
- Full read of `live_observation.py`, `golden_run.py`, the `cli.py` epilogue + `cmd_start` lock lifecycle, and the depended-on `refusal_bridge.py` / `guardrail_refusal.py` / `telemetry_redaction.py` / `locking.py`.
- Secret-pattern scan over the full unit diff `2ae057b..1a935fb` and over the Amendment-8 capture set (`source-008-amendment.md`, `requirements.json`).
- Grep sweeps: `shell=True`/`os.system`/`subprocess`/`eval`/`exec`/`pickle` in `golden_run.py`; any production import of `golden_run`; process/prompt/messaging primitives in `live_observation.py`; `verified_live` sinks; corpus `verified_live` state.

## Findings

### BLOCKING — none
### MAJOR — none
### MINOR — none

### INFO (defense-in-depth notes; neither blocks; no security exposure)

- **INFO-1 — a `BaseException` inside the epilogue watcher would skip `lock.release()`/`journal.close()`** (`tools/agent_supervisor/cli.py:3052-3069`). The `finally` runs `record_observations(...)` guarded by `except Exception`, then `lock.release()`/`journal.close()`. `except Exception` correctly does NOT swallow `KeyboardInterrupt`/`SystemExit` (those are `BaseException`) — good — but because the watcher now executes *before* the two cleanup calls in the same `finally`, an interrupt landing inside `record_observations` propagates past both, slightly widening the pre-existing "interrupt skips cleanup" window. Impact is low and non-security: the lock is a file lock whose `release()` is idempotent and owner-checked (`locking.py:300-312`) and whose staleness is reclaimed by RECOVER_BOOT on the next `start`; the durable journal is crash-safe (already-committed CAS writes survive), so no corruption or secret exposure results. Optional hardening: nest cleanup in its own `finally` so `lock.release()`/`journal.close()` run even on `BaseException`. Verified: the watcher runs while the single-instance lock is still HELD (acquired via `recover_boot`, `cli.py:2905`; released only at 3068) — this ordering is the *correct* one and is safe against reentrancy/concurrent-instance interleave.

- **INFO-2 — three register-row scalar fields are copied from the raw source, bypassing `sanitize_structure`** (`tools/agent_supervisor/live_observation.py:278-290`): `installed_version_shape` (from the persisted `claude_version` probe), `applicable_shape` (`payload.get("matched_shape")`), and `source_record_key` (a journal key name). All other free text — `classification_decision`, `selected_response`, and the entire `outcome` payload — is passed through `sanitize_structure` (secret redaction + home-path mask + bound), and the leak test proves it (`test_register_rows_are_sanitized_at_the_boundary` injects `api_key=sk-` + 40×`a` plus a 5000-char blob and asserts the secret never reaches the row with `redaction_count>=1`). The three bypassed fields are not attacker-controllable: `matched_shape` is a fixture name from the owner-reviewed committed corpus, `source_record_key` is a controller-generated key prefix/digest, and `installed_version_shape` is a version string. Not exploitable; sanitizing them too would close a defense-in-depth gap.

## Dimension-by-dimension verification

1. **cli.py epilogue scan** — Runs in `finally` AFTER `payload`/`refusal` are computed and does not touch them, so it cannot mask a start failure or corrupt the payload; a watcher error is caught and audited (`live_observation_scan_failed`) and never changes the return code. It writes ONLY its own namespace keys — `pending_live_observation_register`, `pending_live_observation/<digest>`, `pending_live_observation_last_digest` (`live_observation.py:326,336-338,358`) — all other journal access is getter-only. Does not swallow interrupt-class signals (see INFO-1). Runs while the lock is held → safe ordering.

2. **Watcher (`live_observation.py`)** — Mechanically cannot prompt, message a worker, or spawn a process: it imports no process/IPC primitive; the only `subprocess`/`prompt` tokens are docstring prose; `installed_version_shape` deliberately reads the *persisted* probe instead of executing (`:111-123`). Cannot flip `verified_live` (constant `False` at `:289`; source-level test `test_no_code_path_writes_verified_live_true` asserts no `True` sink). Cannot actuate the 4.8 bridge (no bridge call anywhere; `graduation_readiness` only reports `not_ready`). No foreign-key writes. Labeling is fail-closed toward `injected`: `EVIDENCE_CLASSES` has no `live` value; `_evidence_class` (`:247-255`) returns `live_candidate` only when session is `live` AND the payload carries no injected marker — the `INJECTED-GOLDEN-RUN` text backstop downgrades any fixture-born record even under a live scan (`test_the_harness_marker_wins_over_a_live_session_scan`, and end-to-end `test_the_start_epilogue_scans_and_labels_harness_events_injected`). An attacker cannot force a `live` mislabel: there is no `live` class, and `live_candidate` grants nothing — graduation stays owner-reviewed + R595-gated with `verified_live` unchanged. Secret leak attempt reproduced and defeated (see INFO-2).

3. **Bridge wiring** — `AuthorizedTaskRecord` is built from the controller's own committed packet (`cli.py:2772-2782`); `str(...)`/`tuple(...)` coercion means hostile field *types* can't crash it. Unproven authorization stays fail-closed: `proven` requires task_id + authorization + non-empty acceptance_criteria (`guardrail_refusal.py:129-133`), else the classifier returns `AMBIGUOUS_FAIL_CLOSED / CONDITION_AUTHORIZATION_UNPROVEN` (`:400-408`) and `GuardrailBridgeIntegration.evaluate` records nothing. Record-intent-only confirmed: `GuardrailBridgeIntegration` has NO actuation-channel parameter, `evaluate` does `del config`, and `actuated` is always `False` (`refusal_bridge.py:850-970`); the `assert_actuation_permitted` double gate refuses both halves (`test_an_injected_refusal_cannot_actuate_the_bridge`). Injection text in `authorization`/`objective` is only secret-redacted into a trusted-provenance packet field — worker output never sets it — and this path is unchanged from M0-T093 (`refusal_bridge.py` not in this diff).

4. **Harness (`golden_run.py`)** — Fakes materialize to caller-supplied temp dirs (`.bat` wrapper on Windows `:316-319`; shebang + `chmod +x` on POSIX `:321-327`); tests place everything under `tempfile.TemporaryDirectory()` with `addCleanup` and point `--checkout`/`--runtime`/git `cwd` at temp, with `GIT_CONFIG_GLOBAL/SYSTEM=os.devnull` isolation (`:34-35`). No `shell=True`, `os.system`, command-string exec, `eval`/`exec`/`pickle` anywhere — both `subprocess.run` sites use list-form `["git", *argv]` (`:40`, `:173`). No production module imports `golden_run` (grep across `tools/agent_supervisor/*.py` returns none; only the test and evidence docs reference it). Nothing is written into the repository tree.

5. **Boundaries** — `.claude/hooks`, `.claude` settings, `.github`/CI, and all dependency manifests are untouched over the whole unit range (the only `requirements.json` in range is the directive registry, not a Python manifest). No new dependency (stdlib + local imports only). `assert_actuation_permitted` (R595 double gate) and R187 posture unchanged. Amendment-8 capture introduces no secret material — token scans of `source-008-amendment.md` and the R231-R249 registry are clean; R243 is explicitly a FUTURE task's duty and no token-like content landed. The single secret-pattern hit in the entire diff is the synthetic redaction-test literal `"api_key=sk-" + "a"*40` at `test_...golden_run.py:423`, which the same test proves is redacted and never persisted.

6. **Redaction / prompt-withholding** — The new code persists no raw prompt: `live_observation` stores `classification_decision`/`selected_response`/`sanitized_outcome` through `sanitize_structure`, which withholds prompt-like keys as digest references and bounds free text (`telemetry_redaction.py:210-215,114-118`); the cli epilogue passes no prompt; fake-provider "prompts" live only in temp test plans, never in production writes.

Module sizes are within policy thresholds (`live_observation.py` 452, `golden_run.py` 408, `cli.py` net +38); no responsibility mixing observed (detection/read-only-discovery, register persistence, and status/comparison are cleanly separated; the harness is test-only and unimported by production).

VERDICT: PASS
