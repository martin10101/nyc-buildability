# M0-T104 G5 security review (round 1) — VERBATIM reviewer return

Orchestrator note: saved verbatim from the security-reviewer agent-return channel
(transport entity-decoding only: `&lt;` → `<`). Reviewer: independent read-only
security-reviewer spawn; review conducted at deliverable identity `ac305ae`
(HEAD `b8ce5cb`, control records only). Verdict recorded by the orchestrator: PASS
with required corrections (blocking handling per `.claude/rules/project-control.md`
gate-verdict semantics — see the progress_log entry recording the blocking condition).

---

# Gate Report

- **Gate ID:** G5
- **Task ID:** M0-T104 (D-024 Amendment 3 unit C — native runtime adapter)
- **Reviewer:** security-reviewer (independent, read-only)
- **Producer:** fable-orchestrator-session
- **Result:** **PASS** (with required corrections — blocking for the unit that wires this seam)
- **Clean environment/worktree used:** Reviewed the working tree at the described deliverable identity `ac305ae` (HEAD `b8ce5cb` adds only control records). Ran the two in-scope test packs read-only (`pytest`); no writes, no git/gh/project_control.

## Acceptance criteria reviewed

Scope files all read in full: `tools/agent_supervisor/native_runtime.py`, `runtime_backend.py`, `tools/test_agent_supervisor_native_adapter.py`, `tools/test_agent_supervisor_capability_probe.py`, the four `*m0t104*` fixtures, and both producer reports. Cross-referenced the un-scoped dependencies `capability_probe.py` (classify_flags, probe allowlist) and `telemetry_redaction.py` (redact_user_paths) that the masking/detection paths call.

Re-ran the acceptance packs independently:
- `pytest tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_capability_probe.py -q` → **72 passed in 18.37s** (53 adapter + 19 probe). The `@requires_claude` live rows executed (claude present on this runner), so the drift tooth and live `agents --json` parse were exercised, not skipped.

## Directive/requirement verification

In-regime task (D-024:ALL; producer's applicable cited set R153/R154/R156/R172). This G5 pass verifies the security preconditions of each; the full independent requirement-to-evidence DCV is the `directive-compliance-verifier`'s separate pass.

| Requirement ID | Content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R153 (native sessions; feature-detected fallback; never two systems) | ac305ae | PASS | `select_runtime_backend` fails closed to controller on any non-`supported` capability incl. `unknown`/`absent` (native_runtime.py:141-153, runtime_backend.py:74-92); `RuntimeSession.activate` refuses a 2nd backend (runtime_backend.py:110-120); new modules imported only by the test file — no live wiring, existing controller path byte-untouched (grep confirms). |
| D-024-R154 (structured passive observation; never ask Fable; no quotas) | ac305ae | PASS | `parse_agents_json` fails closed on malformed feed (native_runtime.py:517-556); no prompt-mutating path injects token/status questions (only the R156 worktree preamble mutates a prompt); masked listing fixtures committed. |
| D-024-R156 (native worktree isolation / default-branch hazard) | ac305ae | PASS (soft-control residual F5) | `WorktreeSpec` mandates `head`-or-40-hex-SHA base; CLI dispatch path refuses `head` and requires a pinned SHA (native_runtime.py:419-427); reset preamble carries the `--show-toplevel` primary-checkout STOP guard (native_runtime.py:353-360). |
| D-024-R172 (unit-C composition) | ac305ae | PASS | Every named element present: measured-at-use detection (never cached), deterministic identity, native dispatch, agents-json ingestion, attach/logs/stop/respawn, controller fallback, one-backend invariant — all with passing tests. |

## Steps independently executed

1. Read all scope + dependency modules; traced every value that reaches the executed argv.
2. Ran both test packs (72 passed).
3. Independent leak scan of the four m0t104 fixtures for `MLFLL`, drive-rooted user paths, `/home/`, `USERNAME/USER`, and the full RFC-4122 UUID pattern → **no matches**.
4. Grepped the whole `tools/` tree for socket `bind`/`listen`/http-server/`serve`/`port`, cloud/teleport flags, and importers of the new modules.

## Expected versus actual

| Claimed guarantee | Independent result |
|---|---|
| No inbound port / no auto Remote Control | **Confirmed.** Zero `socket.bind/listen`, no `http.server`/`serve`, no framework in either module (grep clean; the only `bind` hits are docstrings). `attach_argv` constructs but never executes. Builder never emits `--teleport/--cloud/--chrome/--environment/--tmux`. |
| Deterministic names carry no hostname/username/secret | **Confirmed by construction.** `derive_session_identity` normalizes to a closed ASCII `^[a-z0-9][a-z0-9-]*$`, rejects bool/out-of-range attempt, caps at 64 chars; unicode is rejected by `fullmatch` on the literal ASCII class; uuid5 uses a fixed constant namespace; no `os.environ`/`gethostname` read anywhere in the derivation. |
| One backend, never two (R153) / R180 replace-not-layer | **Confirmed.** New modules consumed only by tests; no production caller sets `prefer_native`; existing controller untouched and not deprecated. |
| Masked fixtures (public repo) | **Confirmed clean for the committed set;** masking is a field allowlist — see F3 for the latent gap. |
| Permission-bypass structurally impossible | **Practically holds, wording overclaims** — see F1. |

## Evidence paths

- `tools/agent_supervisor/native_runtime.py`
- `tools/agent_supervisor/runtime_backend.py`
- `tools/test_agent_supervisor_native_adapter.py`
- `tools/agent_supervisor/fixtures/{native_runtime_detection,agents_listing,agents_listing_all,capability_probe_live}_2026-08-27_m0t104.json`
- `project-control/reports/M0-T104-native-adapter.md`, `M0-T104-G2-self-check.md`

## Human-style walkthrough findings

The seam is library-only in this change (no supervisor loop wires it). I walked the dispatch path by hand: `DispatchSpec` → `build_background_argv` → `NativeBackgroundBackend.dispatch` → `run_command` (subprocess LIST, no shell). The `--` end-of-options separator correctly quarantines the prompt from flag parsing, and every injected free value sits immediately after its own value-taking option, so a flag-shaped value is consumed as that option's argument rather than a top-level option. This positioning is the real reason the bypass surface is small; the post-build denylist re-check is a secondary net (F1).

## Regression/security/provenance findings

**F1 — LOW / ADVISORY — Denylist is exact-match; `agent`/`tools` value fields are unvalidated free strings.** `build_background_argv` (native_runtime.py:397-433) places `spec.agent` and `spec.tools` verbatim into argv; only `name`, `permission_mode`, and `worktree.name` are charset/enum-validated. The final guard `forbidden = [tok for tok in argv if tok in FORBIDDEN_DISPATCH_FLAGS]` (line 429) is exact membership, so it does **not** catch `=`-syntax (`--cloud=x`), case/abbrev variants, or any dangerous flag outside the 7-item list (`--add-dir`, `--mcp-config`, `--settings`, `--allowedTools`, …). The docstring's "forbidden flags are structurally impossible" overclaims. *Practical exploitability is blocked:* every injected value sits directly after a value-taking option (`--agent <v>`, `--tools <v>`), so commander consumes it as that option's value, not a top-level option — there is no loose top-level position before `--` (the only boolean flag `--strict-mcp-config` is followed by `--tools`/`--`), and the highest-risk flag `--dangerously-skip-permissions` is a boolean caught by exact match. *Compensating control:* orchestrator-only caller (no untrusted input today). *Remediation:* validate `agent`/`tools` against a closed charset (as `name` is) or switch the guard to an allowlist, and soften the docstring wording.

**F2 — MEDIUM (required correction before wiring) — Child-env strip is default-OFF in the backend; the R162 transcript-suppression hazard is reintroduced by the default constructor.** `NativeBackgroundBackend.dispatch` (runtime_backend.py:144-150) does `env = child_environment(self._base_env) if self._base_env is not None else None`. With the **default** `base_env=None`, `env=None` flows to `run_command` (native_runtime.py:104), which passes `env=None` to `subprocess.run` → the child **inherits the full parent environment, including `CLAUDECODE` and `CLAUDE_CODE_*`** — exactly the markers `child_environment` exists to strip. The `dispatch` docstring flatly claims "EXPLICIT child environment (inherited session markers stripped)", which is false on the default path. *Attack/failure scenario:* a future consumer that constructs `NativeBackgroundBackend()` without `base_env` silently dispatches producers that believe they are child sessions and **suppress transcript saving** (lost audit/evidence trail — R162), and inherit any session-scoped posture markers. The helper itself is correct (`test_child_environment_strips_session_markers` passes) and the C1 canary passed an explicit env, so there is **no active leak in this change** (bounded seam, no live caller). *Remediation:* default `base_env` to `os.environ` and always strip (or make `base_env` a required argument), and add a test asserting the default-constructed backend still strips.

**F3 — MEDIUM/LOW (latent, public repo) — `mask_session_row` is a field allowlist, not a comprehensive pass; future rows can leak through non-masked fields.** `mask_session_row` (native_runtime.py:583-597) masks only `cwd` (home + UUID-in-path), `sessionId`, and `id`. It never scans `name`, `waitingFor`, or any future field. The concern's exact scenario holds: a UUID, home path, or secret appearing in `name`/`waitingFor` is committed **unmasked**. The committed whole-JSON leak test (`test_committed_agents_fixture_masked`) catches Windows `:\Users\` fragments in *any* field but does **not** catch full UUIDs-in-`name` or POSIX `/home/…` paths in non-`cwd` fields. *Current committed fixtures are clean* (my independent scan + 72/72 tests). *Remediation:* route every string value of the row through `redact_user_paths` + `_UUID_RE` masking (or `telemetry_redaction.sanitize_structure`) rather than three named fields.

**F4 — ADVISORY — `safe_to_dispatch` naming + empty-listing hazard in restart reconciliation.** `RestartReconciliation.safe_to_dispatch` returns `unexpected_exit` (runtime_backend.py:217-222). Semantics (docstring + `test_restart_no_duplicate_and_unexpected_exit`) require controller review before any re-run, and running identities are correctly excluded (the no-duplicate core is sound; unknown display states park to `blocked_input`, never to missing). *Residual:* the name suggests auto-dispatchable, and `reconcile_after_restart` does not know whether an **empty** `observed_active` means "nothing running" or "`observe()` failed". A future caller that catches an `agents_feed_unavailable` error and reconciles with `[]` would bucket **all** expected identities into `unexpected_exit`/`safe_to_dispatch` → mass duplicate-dispatch. *Compensating control:* the contract gates on controller review; the feed is the local trusted daemon. *Remediation:* have reconcile refuse to run against a known-unavailable feed, or rename the property to reflect "candidates for controller review."

**F5 — ADVISORY (verified residual) — Worktree reset guard is a natural-language prompt preamble (soft control).** `_worktree_reset_preamble` (native_runtime.py:353-360) is prepended to, then followed by, the caller's prompt. A hostile prompt could textually neutralize the FIRST-ACTION/`--show-toplevel` instruction. This is inherent to R156 (native `-w` has no baseRef, so the reset must be an agent instruction) and the prompt is orchestrator-supplied (trusted). The base is charset-validated to 40-hex, so it **cannot** be redirected to the primary checkout via the SHA, and the primary-checkout STOP guard is present. No change needed; recorded as an accepted residual.

**F6 — ADVISORY — Error messages embed unmasked reprs.** `parse_agents_json` raises with `{row!r:.120}` (native_runtime.py:538) and `observe`/`daemon_status` embed `{stderr!r:.120}` (runtime_backend.py:161). Truncated and raised locally (not committed to any fixture), but a row `cwd`/`waitingFor` or a stderr fragment could carry a path if these errors ever reach a shared/persisted log. *Remediation (optional):* mask before interpolation if these strings can reach a persisted log.

### Residuals I verified are covered by compensating controls
- **No inbound port / no Remote Control** — verified absent (no socket/server code; `attach` never executed; no cloud flags emitted). No compensating control needed; genuinely closed.
- **Identity hygiene** — closed-charset by construction; no env/host reads; bool/range/length/unicode all rejected. Genuinely closed.
- **Flag-in-value smuggling (F1)** — blocked in practice by argv positioning + `--` prompt fence + trusted orchestrator caller; exact high-risk flags caught.
- **One-backend / R180** — no live wiring; existing controller untouched; single-activation guard present.
- **Fixture leakage** — committed set independently scanned clean; masking gap (F3) is latent for future captures only.

## Defects

No BLOCKING defect. F2 and F3 are the material tooth-gaps; both are latent (no production consumer in this bounded seam) and do not leak or bypass anything in the committed deliverable.

## Required rework

Recorded as PASS-with-required-corrections (blocking for the next gate/acceptance and, specifically, for the unit that first wires this seam):
1. **F2 (MEDIUM):** make the child-env strip unavoidable — default `base_env` to `os.environ` (always strip) or require it; add a test that the default-constructed backend still strips `CLAUDECODE`/`CLAUDE_CODE_*`. Correct the `dispatch` docstring.
2. **F3 (MEDIUM/LOW):** make `mask_session_row` a comprehensive pass over all string values (home + UUID), not a three-field allowlist; extend the committed leak test to include a UUID needle and `/home/`.
3. **F1 (LOW):** charset-validate `agent`/`tools` or convert the forbidden-flag net to an allowlist; soften "structurally impossible" wording.
4. **F4 (ADVISORY):** guard reconcile against an unavailable feed and/or rename `safe_to_dispatch`.

## Reviewer conclusion

**PASS.** The unit-C native runtime adapter meets its G5 security preconditions in the deliverable as committed: no inbound port and no Remote Control surface (independently verified), identity is closed-charset by construction with no hostname/username/secret, the committed fixtures are leak-clean under an independent scan, the one-backend invariant holds with the existing controller path untouched (replace-not-layer / R180), the feed parser and restart reconciliation fail closed and never auto-resume work, and the permission-bypass/remote-control denylist plus the `--` prompt fence block the realistic smuggling paths for the trusted orchestrator caller. The findings are hardening/latent items (F1-F6): none leaks, bypasses, or opens a port in this change because the seam has no production consumer yet. F2 and F3 must be closed before any unit wires this adapter into a live dispatch loop, and are recorded as blocking corrections for that step. Independent directive-compliance (DCV over the full applicable set at this identity) remains the `directive-compliance-verifier`'s separate pass.

Verdict to record: **PASS** (required corrections F2/F3 blocking for the wiring unit; F1/F4/F6 advisory; F5 accepted residual).
