VERDICT: PASS

# G5 Security Review — M0-T110 unit K (`/loop-codex` Codex discussion channel)

**Reviewed SHA:** `eacbb43bd7dc0df4584476a2c0ba9ab01b1006c6` (confirmed via `git rev-parse HEAD`; matches the expected reviewed head exactly).
**Branch:** `control/D-024-fable-codex-loop`
**Directive:** D-024 Amendment 8, rows R231–R240, R246, R248, R249. Verbatim source: `project-control/directives/D-024-fable-codex-loop/source-008-amendment.md`.
**Reviewer:** security-reviewer (read-only). **Producer:** fable-orchestrator-session.
**Scope reviewed:** the 8 named files plus the reused security primitives (`codex_reviewer.build_argv`, `process.assert_argv_safe`/`minimal_env`, `redaction.py`, `operator_ask` sanitizers, `refusals.py`, `start_gate.emit_refusal`, `operator_channel_cli.emit_payload`).

## Verdict basis (one line)
Every reply/prompt path is fail-closed, bounded, redacted, and read-only; no code path leads from a hostile Codex reply or a crafted `/loop-codex` prompt to any actuation (stop/pause/task/ledger/git); durable rows carry bounded+redacted text or digests; no new network/dependency/settings surface. No BLOCKING/MAJOR/MINOR findings; four ADVISORY/INFO hardening notes.

## What I executed vs inspected

**Executed (read-only):**
- `git rev-parse HEAD`, `git log`, `git diff --stat 1b5513f..HEAD` (task-scoped and full range).
- `python -m pytest tools/test_agent_supervisor_codex_channel.py` → **52 passed**.
- `pytest -k "K2 or K6 or interception or security or redact or argv or timeout or identity"` → **16 passed**.
- `pytest tools/test_agent_supervisor_operator_channel.py tools/test_agent_supervisor_reviewer.py` → **135 passed** (reused-harness regression: 54 + 81).
- **Adversarial CLI injection probes** (the real downstream parser):
  - `codex show "--checkout=C:/Windows"` → argparse consumes the option, then `error: the following arguments are required: thread_id` (aborts; no provider call, no state write).
  - `codex continue --codex-executable /real --config /c --model-selection /s "--codex-executable=/evil" -- "msg"` → argparse abort (missing required positional; the executable-override never fires a provider call).
  - `codex continue ... "--window=0.001" -- "msg"` → argparse abort.
- `python tools/modularity_check.py --check` → **failures 0**; `codex_channel.py`/`codex_channel_cli.py` are not in the warn list.

**Inspected:** all 8 diff files; the reused primitives above; the verbatim amendment rows R234–R240/R248; the K-pack test bodies; repo-wide grep for consumers of the new durable namespaces.

## Threat-model walk — per-surface conclusions

### 1. Hook attack surface (`.claude/hooks/loop_command_interceptor.py`, runs on every prompt) — PASS
- **Regex anchoring:** `^/(loop-(?:…|codex))(?:\s+([\s\S]*))?$` applied to `prompt.strip()`. Single greedy `[\s\S]*`, no nested quantifiers → no ReDoS. Anchored `^…$`, so only a prompt that *is* the command matches. `loop-codex` (no slash), `/loop-codexes`, `/loop-codex-new`, `tell me about /loop-codex …` all pass through untouched (proven by `test_similar_text_passes_through_untouched`). **No non-command text reaches execution; no command shape reaches execution without a full anchored match.**
- **argv construction / `--` separator:** free text (question/message) rides as ONE element behind an explicit `--` (lines 134–138), so leading `-`, metacharacters, quotes, Unicode, newlines are inert data. `shell=False`, argv arrays only. **The one residual: the thread-id/message-id positional for `continue`/`show`/`promote`/`close` is placed BEFORE/without `--`** (lines 104–133). I probed this end-to-end: a crafted id shaped like `--codex-executable=/evil` or `--checkout=…` is parsed as an option by the downstream argparse, which then **aborts on the now-missing required positional** — no provider call, no state mutation, and the downstream also re-validates the `cxt_/cxm_` prefix. Not exploitable (see ADVISORY-1 for the defense-in-depth hardening).
- **Env-var trust:** `SUPERVISOR_CODEX_EXECUTABLE/CONFIG/MODEL_SELECTION` are read from `os.environ` (the owner's launch config), never from the prompt. A prompt-injection attacker cannot set them. Trust model is identical to the accepted unit-G `/loop-ask`. Acceptable.
- **Identity validation before execution:** `_repo_root` requires `CLAUDE.md` + `tools/project_control.py` + `tools/agent_supervisor/cli.py` under `CLAUDE_PROJECT_DIR`/`cwd`; a matched control outside the campaign root **fails closed with `_block`** (erased from the model), never executed (lines 217–224).
- **Fail-open vs fail-closed:** oversized (>256 KiB) / malformed / non-dict / non-str-prompt payloads → `return 0` (pass-through, never block a legit prompt). This fail-open direction only means "do not intercept" — it can never *execute* anything (execution requires full match + identity + provider env, all fail-closed). Safe.
- **Timeout/kill:** `subprocess.run(timeout=45s, shell=False)`; on timeout the child is killed and a visible reason is shown. See INFO-1 on the 45 s-vs-90 s nesting.
- **Display safety:** `_bound_for_display` reuses `bound_answer` (control-strip + redact + bound); on import failure it returns a withheld message, never raw output.

### 2. Provider boundary (`codex_channel.py`) — PASS
- **Turn packet (both directions):** owner input via `sanitize_question` (control-seq strip + redact + 4 000-char bound, typed refusals for empty/oversized/non-text); state via `redact_structure(compose_status(...))`; hard `MAX_PACKET_BYTES=56 000` ceiling with a *visible* trim order (`omitted_for_size`) then a typed `packet_too_large` fail-closed refusal. Proven by `test_control_sequences_and_secrets_never_reach_the_packet` (real ESC + fake `ghp_…` token absent from `input_text`) and `test_the_byte_ceiling_trims_visibly_then_fails_closed`.
- **Read-only invocation contract:** `build_argv(...)` with default `--sandbox read-only`, `--ephemeral --ignore-user-config --strict-config --json --output-schema --output-last-message`, `FORBIDDEN_REVIEWER_FLAGS` check, and `assert_argv_safe` (NUL/hard-deny/effort/activation-flag refusal). A discussion turn can never gain mutation tools. `minimal_env()` scrubs the child environment (no ambient credentials). Model comes from `resolve_model` (allowlisted; provider never chooses). Proven by `test_the_turn_rides_the_hardened_read_only_argv`.
- **Hostile reply handling:** `validate_reply` requires a non-empty `reply` and a disposition in the closed 6-set (unknown/missing → typed `disposition_invalid`, never defaulted); `reply`/`confidence_note`/`evidence_refs` are `bound_answer`'d (control-strip + redact + bound); `updated_summary` is redacted+bounded via `_bound_summary` before storage. Terminal escapes, secret-looking strings, and prompt-injection-shaped text are therefore stripped/redacted/bounded before both storage and display, and displayed output is redacted a second time in `emit_payload`. **A reply can NEVER actuate anything:** the module imports no `stop_intent`/`repair_gate`/`project_control`/`github_flow`/`external_effects` (enforced by `test_the_module_imports_no_actuation_surface`), and a repo-wide grep confirms **no code outside the three unit-K files reads the `codex_channel/*`, `boundary_queue`, attention, or promotion namespaces** — the durable rows are inert. URGENT_PAUSE/STOP_FOR_OWNER only write an `actuated:False` attention row + audit and *display* the exact owner command; the owner is the sole actuation path (R239-correct).
- **`read_answer_file` provider-failure rule:** correctly reused — a `turn.failed`/`error` stdout event is never mistaken for an answer (`provider_failure_reason` gate), yielding `no_reply` → typed failure rather than a fabricated reply.

### 3. Durable rows — PASS (privacy-consistent with the ask precedent)
- **Thread row:** owner/codex message `text` stored redacted+bounded (via `sanitize_question`/`bound_answer`); `summary` bounded ≤ 2 000. Bounded human-readable text in rows matches the `QueuedAsk` precedent; the row is local durable state (never git, never transmitted).
- **Promotion row:** `text = bound_answer(...)` + `message_digest`, `authorizes_nothing: True`, `status: recorded_awaiting_capture`, `required_next` names `/directive-compliance` (R240).
- **Attention row / boundary-queue row / message-index row:** carry `reply_digest` + ids only — **no raw text**.
- **Audit log:** digests + sizes only (`reply_digest`, `packet_bytes`), never raw question/reply — proven by `test_the_audit_trail_is_privacy_bounded`. This is exactly the "digests in audit, bounded text in rows" ask precedent.

### 4. Authority boundaries — PASS
- **Promotion authorizes nothing (R240):** owner-typed by construction (`disable-model-invocation: true` skill + pre-model interception); records one CAS-idempotent row; no external consumer. Proven by K5.1–K5.4.
- **Attention never actuates (R239):** confirmed at code level (no reader) and by `test_urgent_and_stop_name_the_exact_command_and_actuate_nothing` (only `codex_channel/` rows written; `actuated:False`).
- **Untouchable guard hooks untouched:** the full change set (`git diff --stat 1b5513f..HEAD`) touches no `agent_dispatch_guard.py`/`readonly_agent_guard.py`/`settings.json`/`.mcp.json`/dependency manifest; `test_R248` asserts no `settings.json`/`mcp`/`urllib`/`requests`/`socket`/guard references in the new modules. **No new network/dependency/global-settings surface (R248).**
- **Honesty (R233/R235):** no `/btw`-equivalence claim in hook/skill/module (`test_no_btw_equivalence_claim_anywhere`); skill documents the queued-until-turn-end limitation, the context-cost of the fallback, and the second-terminal path. Live owner-typed zero-context canary remains pending-owner-C1, honestly stated (consistent with accepted unit G).

### 5. CLI (`codex_channel_cli.py`) — PASS
- Every output path is redacted: `emit_payload` → `redact_structure` (json and lines), and `emit_refusal` → `refusals.emit` → `redact_structure`. No raw-text emission path exists.
- Refusal-code mapping is correct: `_UNSAFE_CODES = ("identity_mismatch","campaign_record_invalid")` → `UNSAFE` (exit 11); all other `ChannelError` codes → `STALE_STATE` (exit 13) — mirrors the accepted `ask` verb exactly.
- Provider inputs are never discovered from PATH or defaulted; missing inputs → typed `codex_input_missing` refusal.

## Findings

**BLOCKING:** none.
**MAJOR:** none.
**MINOR:** none.

**ADVISORY-1 — id positional not behind `--` / not shape-validated in the hook** (`loop_command_interceptor.py:_codex_argv`, lines 104–133). The free-text field is correctly protected behind `--`, but the `continue`/`show`/`promote`/`close` id token is passed to the downstream CLI without `--` and without a hook-side shape check. I confirmed empirically that a crafted option-shaped id (`--codex-executable=/evil`, `--checkout=…`, `--window=…`) is consumed by the downstream argparse and then aborts on the missing required positional — **no provider call, no state mutation, no exploit** — and the downstream re-validates the `cxt_/cxm_` prefix. This is a defense-in-depth/robustness gap, not a vulnerability. *Smallest sufficient fix:* validate the id token in `_codex_argv` against `^(cxt_|cxm_)[A-Za-z0-9]+$` before building argv and `_block` with a visible reason otherwise; this converts a downstream argparse error into a clear owner-facing refusal and closes the theoretical misparse surprise for any future subverb that might not require a positional.

**INFO-1 — hook timeout (45 s) shorter than the default turn window (90 s).** `SUBPROCESS_TIMEOUT_SECONDS=45` wraps `python -m tools.agent_supervisor codex …` whose inner `DEFAULT_TURN_WINDOW_SECONDS=90`. On the primary Windows platform the inner Job Object is kill-on-close, so killing the parent cascades to the codex grandchild (no leak); on POSIX a SIGKILL of the parent could theoretically leave the grandchild until the inner process's own containment fires. This is inherited unit-G structure (identical for `/loop-ask`), not introduced here, and benign on the deployment platform. Consider aligning the hook timeout above the inner window, or passing an explicit `--window` below the hook timeout, so the inner containment always wins.

**INFO-2 — QUEUE_NEXT_BOUNDARY queue is write-only in this unit.** No code reads `codex_channel/boundary_queue`. This is security-positive (the queue is inert and never actuates), but the report's "surfaced for the next safe boundary" is aspirational — the surfacing mechanism is not wired in unit K. No action required for security; flag for functional follow-up.

**INFO-3 — oversized/malformed hook stdin and non-selected events fail open to pass-through.** A `/loop-codex …` prompt on a non-`UserPromptSubmit` event, or inside a >256 KiB / malformed payload, reaches the model as inert text (the skill is `disable-model-invocation:true`, so it cannot self-execute). This is the documented honest fallback (context cost, no execution, no escalation) and the deliberate fail-open-to-pass-through posture. No action required.

## Requirement coverage (independently re-derived from the verbatim source)
R234 (5-subverb surface), R235 (block+erase on the fixture-selected event; honest pending canary), R236 (bounded summary + ≤6 recents + fresh labeled state + evidence refs + read-only inspection), R237 (bulk content structurally absent + byte ceiling), R238 (stable-reference guidance in packet + schema), R239 (closed 6-disposition set, no automatic alteration, no actuation), R240 (promotion owner-gated, authorizes nothing, capture route named), R248 (no continuous mode / live bridge / PR #241 / Agent SDK / MCP / global settings), R249 (five-item first report) — **all verified satisfied at the reviewed identity** by inspection + the passing executable register (K8) and my independent execution.

**Supervisor-freeze duty:** the change re-establishes the suite baseline (report records 2 654 passed / 2 chunks); I re-ran the reused-surface packs (135) + K-pack (52) green with 0 failures. Qualifying evidence D-024-R232/R234 is cited in both the packet and the commits. Modularity: 0 failures.

**Recommendation:** PASS. ADVISORY-1 is a non-blocking defense-in-depth hardening the orchestrator may schedule as a follow-up; INFO-1/2/3 are documentation/robustness notes. No corrections are required before acceptance.

*(Saved verbatim from the reviewer's return by the orchestrator; transport entity-decoding only — `&gt;` decoded.)*
