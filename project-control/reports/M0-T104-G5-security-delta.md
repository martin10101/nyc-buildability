# M0-T104 G5 security review (round 2 — delta re-review) — VERBATIM reviewer return

Orchestrator note: saved verbatim from the resumed security-reviewer agent-return channel
(transport entity-decoding only: `&lt;` → `<`). Delta re-review conducted at re-frozen deliverable
identity `f610aab` (HEAD `94d7bd9`, control records only). Verdict recorded by the orchestrator: PASS.

---

# Gate Report (G5 delta re-review)

- **Gate ID:** G5 (round 2 — delta re-review)
- **Task ID:** M0-T104 (D-024 Amendment 3 unit C — native runtime adapter)
- **Reviewer:** security-reviewer (independent, read-only)
- **Producer:** fable-orchestrator-session
- **Result:** **PASS**
- **Reviewed identity:** deliverable `f610aab` (HEAD `94d7bd9` adds only gate records). Delta from round-1 `ac305ae` reviewed in full against source.
- **Clean environment/worktree used:** Reviewed working tree read-only; re-ran the two in-scope packs. No writes, no git/gh/project_control.

## Acceptance criteria reviewed

Re-read all four changed source/test files and both regenerated fixtures at `f610aab`. Re-ran `pytest tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_capability_probe.py -q` → **77 passed in 17.50s** (was 72; +5 new tests: `test_dispatch_default_backend_still_strips_child_env`, `test_agent_tools_value_charsets`, `test_verb_check_surfaces_daemon_failure`, `test_reconcile_refuses_unavailable_feed`, `test_mask_session_row_comprehensive_all_fields`). The `@requires_claude` live drift/observe rows executed (not skipped).

## Directive/requirement verification

The four round-1 requirement verdicts (D-024-R153/R154/R156/R172) are unaffected by the delta — the corrections harden the same seam without changing its directive posture. R153 fail-closed selection, R154 passive ingestion, R156 worktree pinning, and R172 composition all remain PASS at `f610aab`; the full independent DCV over the applicable set remains the `directive-compliance-verifier`'s separate pass.

## Independent verification of each correction

**F2 (MEDIUM → CLOSED, non-cosmetic).** `NativeBackgroundBackend.__init__` now binds `self._base_env = os.environ if base_env is None else base_env` (runtime_backend.py:147-148) and `dispatch` unconditionally calls `child_environment(self._base_env)` — the old `if base_env is not None else None` branch is gone (runtime_backend.py:158). The strip is now unavoidable. *New-regression check ("cannot leak the parent env in a worse way"):* the default path passes `os.environ` **minus** the CLAUDECODE/CLAUDE_CODE_* markers — strictly a subset of what the old `env=None` path already inherited wholesale, so it cannot leak more than before; it leaks *less* (markers removed). The child still receives PATH/credentials it legitimately needs (same as raw inheritance). `os.environ` is stored by reference and stripped at dispatch time, so it reflects live env. `test_dispatch_default_backend_still_strips_child_env` monkeypatches the markers, default-constructs the backend (no `base_env`), and asserts `CLAUDECODE`/`CLAUDE_CODE_*` are absent while PATH survives — a genuine test of the default path, not the injected-env path. Confirmed closed.

**F3 (MEDIUM/LOW → CLOSED, non-cosmetic).** `mask_session_row` (native_runtime.py:630-644) now maps every value through the recursive `_mask_value` (native_runtime.py:617-627): every string gets `redact_user_paths` + `_mask_uuids`; dicts/lists recurse; non-strings pass through. The `sessionId`/`id` 8-char collapse is guarded by `"-[MASKED]" not in value` so an already-UUID-masked id is not double-processed, and a short non-UUID id >8 chars still loses its tail. *Recursion-bypass hunt:* nested `futureField` dict/list values are masked (verified by `test_mask_session_row_comprehensive_all_fields`: UUID-in-name, home-path-in-waitingFor, and `/home/`+UUID in a nested future field all masked; the test asserts **no** full RFC-4122 UUID survives anywhere in the row). The only unmasked surface is dict **keys** — not a realistic leak channel here because agents-json keys are daemon-controlled field names, not user data (residual R3 below). Confirmed closed.

**F1 (LOW → CLOSED, non-cosmetic).** `DispatchSpec.__post_init__` now validates `agent` against `_AGENT_RE` and `tools` against `_TOOLS_RE`, raising `invalid_agent`/`invalid_tools` at construction (native_runtime.py:411-418). *"Block-then-fall-open" hunt (the specific concern):* I executed the alternation directly — `_TOOLS_RE = r"|[A-Za-z][A-Za-z0-9,\s()*_-]*"` under `fullmatch` accepts `""` (disable-all) and plain lists but **rejects** every flag-shaped value: `--cloud=x`, `-x`, `--tmux`, ` --teleport`, `\t--x`, `--dangerously-skip-permissions` → all `invalid_tools`; `--agent`, `-a`, `a b`, `a/b`, `--cloud` → all `invalid_agent`. The empty leading alternative does **not** zero-width-match a non-empty string under `fullmatch`, so there is no fall-open. Because argv values are single subprocess-list tokens (no shell), a mid-value hyphen (`Bash -tmux`) cannot split into a new flag token; blocking only leading `-` is therefore the complete defence. The `build_background_argv` docstring is correctly softened to "defence-in-depth denylist, not a total proof." Confirmed closed.

**F4 (ADVISORY → CLOSED).** `reconcile_after_restart` gained keyword-only `feed_available: bool = True`; `False` raises `reconcile_feed_unavailable` (runtime_backend.py:282-287), preventing the empty-listing→all-missing→mass-dispatch hazard (`test_reconcile_refuses_unavailable_feed`). The property is renamed `needs_controller_review` with a class-level `safe_to_dispatch = needs_controller_review` alias — I verified `RestartReconciliation.safe_to_dispatch is RestartReconciliation.needs_controller_review` (same property object), so both invoke one getter returning `unexpected_exit`, and the no-duplicate core (observed identities excluded) is intact. Confirmed closed.

**G4 ADV-2 (in scope for security).** `_run_verb(verb, argv, check)` (runtime_backend.py:181-195) raises typed `<verb>_failed` on daemon rejection when `check=True`, default `check=False` preserves the raw result. No new attack surface; error messages truncate `{stderr!r:.120}` (residual R1). Clean addition.

## Regression / security / provenance findings (delta)

No new security regression introduced by the corrections. Independent leak scan (`MLFLL` / drive-rooted `\Users\` / `/home/<user>` / full-UUID regex) over both regenerated `*m0t104*` fixtures → **no matches**. The regenerated `agents_listing` fixtures remain `[HOME]`-masked with sessionIds/ids collapsed to 8 chars and the scratch-path UUID masked; content is materially identical to round 1 (same clean rows), now produced by the comprehensive masker. `os` is the only new import (used solely for `os.environ`). No socket/port/server code introduced (re-confirmed).

## Residuals (all ADVISORY; none blocking; none new-security)

- **R1** — verb/observe/reconcile error messages embed truncated `{stderr!r:.120}` / `{row!r:.120}`; local and not committed to any fixture. Mask before interpolation only if these ever reach a persisted shared log. (Carryover of round-1 F6.)
- **R2 (new, benign)** — `_TOOLS_RE` is tighter than the CLI tool-spec grammar: it rejects colon-style specifiers such as `Bash(git:*)` (verified rejected). This **fails closed** (safe); a future caller needing specifiers must widen the charset under review rather than the adapter silently passing them.
- **R3** — `mask_session_row` masks values recursively but not dict keys; not a realistic leak channel for daemon-controlled agents-json field names. Noted for completeness.
- **R4** — the `feed_available` guard is caller-cooperative (default `True`); a caller that catches an `observe` error, forgets to pass `feed_available=False`, and passes `observed_active=[]` would still bucket all as missing. Now a documented, enforced-when-used contract — acceptable.
- **R5 (accepted, unchanged)** — the R156 worktree reset preamble is a soft natural-language control neutralizable only by a hostile (trusted) prompt; the SHA is 40-hex-validated and the `--show-toplevel` primary-checkout STOP guard is present. Inherent to native `-w` having no baseRef; accepted residual.

## Defects

None.

## Required rework

None. All four required corrections (F1-F4) from round 1 are genuinely and non-cosmetically closed; residuals R1-R5 are advisory and do not gate acceptance.

## Reviewer conclusion

**PASS.** At the re-frozen deliverable `f610aab`, F1-F4 are each independently verified closed with real teeth: the child-env strip is now unavoidable and cannot leak the parent env more than before (it leaks less); the fixture masker is a comprehensive recursive pass with no bypass found for realistic feed shapes; the agent/tools charsets reject every flag-shaped value with no fall-open (alternation + `fullmatch` verified directly) and fail closed on over-tight cases; and restart reconciliation refuses a down feed and no longer misnames its review queue as auto-dispatchable. The G4 ADV-2 `check=` addition is a clean error-surface improvement with no new attack surface. The regenerated fixtures are leak-clean under independent scan, and the two in-scope packs run 77/77 green. No blocking or medium findings remain; the five residuals are advisory and safe.

Verdict to record: **PASS** (residuals R1-R5 advisory; independent DCV remains the directive-compliance-verifier's separate pass).
