# G3 Independent Code Review — M0-T146 (Codex reviewer MAX reasoning effort + fallback ladder)

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only). Reviewer: independent code-reviewer agent (read-only), returned 2026-09-04 (UTC).

- **Task:** M0-T146 (owner-authorized feature exception to supervisor freeze; D-024 Amendment 52 R767–R773 + Amendment 53 R774–R783; qualifying evidence D-024-R775)
- **Reviewed content commit:** `431018cf` — **material identity confirmed:** all four changed paths hash-identical at commit `431018cf` and at repo HEAD `ff79da01` (git rev-parse per-file: SAME × 4).
- **Reviewer:** independent (read-only); producer was orchestrator.
- **Scope of diff:** exactly 3 code/test paths + 1 report (`git show --stat`): `codex_reviewer.py` (+101), `config.py` (+67/-20), `test_agent_supervisor_reviewer.py` (+96), `M0-T146-codex-max-effort.md`. No forbidden path touched.

## Check 1 — Effort threading in `build_argv` — PASS
`build_argv` adds `["-c", f"model_reasoning_effort={reasoning_effort}"]` **only** when `reasoning_effort` is truthy (line 142-149), validated against `CODEX_REASONING_EFFORT_TIERS` else raises `ReviewError("reasoning_effort_invalid")`. The pair is appended **before** `argv.append("-")` (line 150), so the config-override precedes the stdin marker; `test_build_argv_threads_the_supervisor_set_effort` asserts `argv[-1]=="-"` and presence of `-c`/`model_reasoning_effort=xhigh`. It survives `assert_argv_safe`: I confirmed `EFFORT_ARGUMENT_PREFIXES=("--effort","--reasoning-effort")` refuses only tokens equal to / starting with those prefixes+`=`; the token `model_reasoning_effort=xhigh` starts with `model_`, and `-c` is not denied — so the config-override form passes while user-injected `--effort`/`--reasoning-effort` stay hard-denied (`process.py:81,183`). "max" resolves to `xhigh` correctly: no literal `max` in the enum; `DEFAULT_REVIEW_REASONING_EFFORT="xhigh"` supplies the ceiling when config is unset; a literal `"max"`/`"ultra"` would be rejected (`test_build_argv_rejects_an_effort_outside_the_enum`).

## Check 2 — Narrow R159 exception in `config.assert_no_effort_key` — PASS
`PERMITTED_EFFORT_KEY_PATHS = {("codex","review_reasoning_effort")}` (exact full-path tuple). `assert_no_effort_key` (lines 154-182): for every key whose leaf contains "effort", it admits only the exact permitted path, and on that path raises `effort_value_invalid` if the value is not a valid tier; every other effort key still raises `effort_key_forbidden`. `ProviderSelection.reasoning_effort` defaults to `""` (line 511) and is parsed from `[codex] review_reasoning_effort` via `_require_string_or_empty` (lines 571-573). `test_the_effort_key_exception_is_narrow` proves all three branches (admit valid, reject bad value, reject a different effort key). Verified.

**Minor, non-blocking:** the permitted-path exception is evaluated by *both* loaders (`assert_no_effort_key` runs for the controller config too), and `review_reasoning_effort` is not in `_RUNTIME_ONLY_KEYS`. A `[codex] review_reasoning_effort` mistakenly placed in the immutable `config.toml` would be silently admitted and then *ignored* (the controller loader never reads it) rather than rejected as a misplaced runtime key. Inert and non-exploitable (config.toml is manifest-covered), but a hardening opportunity: add `review_reasoning_effort` to `_RUNTIME_ONLY_KEYS`, or restrict the permitted path to the runtime file.

## Check 3 — Effort ladder + refactor fidelity — PASS
`_effort_ladder` (lines 623-644): fallback-engaged resolution → `(medium,)`; primary → `[primary_tier]` with `primary_tier = configured or DEFAULT("xhigh")`, appending `medium` **only** when `_rank(medium) < _rank(primary_tier)` (strict step-*down*; never up, never sideways). `test_the_effort_ladder_steps_down_from_the_max` confirms `("xhigh","medium")` primary and `("medium",)` fallback. `_review_at_effort` is the extracted bounded schema-retry loop; the diff shows the per-tier loop body moved **verbatim** — the only change is `_invoke(payload, resolution.model)` → `_invoke(..., reasoning_effort)` and the `_invoke` signature gaining `reasoning_effort=""`. The init (`last_error/last_returncode/last_stdout`), the `max_attempts` loop, model-self-report mismatch handling, success outcome, and the halt outcome/audit are unchanged. So the per-tier behavior is preserved exactly; the ladder wrapping is the new authorized behavior (the *default effort* deliberately changes from provider-default `medium` to `xhigh` per the owner directive — intended, not a regression). `review()` iterates the ladder (lines 604-621), returns on `outcome.ok` used as a **property** (`if outcome.ok:`, line 614; `ok` is `@property`, lines 504-506), appends `codex_effort_downgraded` to `step_notify` for `index>0`, and returns the last outcome when the ladder is exhausted. A valid `HALT_UNSAFE` is a schema-valid decision → `ok==True` → returned immediately (no wasteful step-down). Correct.

**Minor, non-blocking:** on a genuine per-tier failure at `xhigh`, the reviewer now runs a *second* full `max_attempts` at `medium` before halting (up to 6 spawns, plus the model-fallback path), increasing worst-case latency/cost on failure — this is the intended R777 ladder, noted for owner awareness.

## Check 4 — Tests pass; new effort tests genuine — PASS
`python -m pytest tools/test_agent_supervisor_reviewer.py -q` → **92 passed** (20.5s). The 8 new/updated effort tests are genuine and cover positive/negative/enum/narrow-exception/ladder/fallback-tier:
1. `test_build_argv_threads_the_supervisor_set_effort` (positive; before `-`, not a flag)
2. `test_build_argv_omits_effort_when_unset` (negative; no `-c`/no override)
3. `test_build_argv_rejects_an_effort_outside_the_enum` (enum reject → `reasoning_effort_invalid`)
4. `test_the_effort_key_exception_is_narrow` (admit valid / reject bad value / reject other key)
5. `test_the_effort_ladder_steps_down_from_the_max` (ladder tiers)
6. `test_a_fallback_model_review_runs_at_the_downgrade_tier` (`model_reasoning_effort=medium` + `model_fallback_engaged`)
7. `test_the_effort_tiers_match_the_documented_enum` (enum pin)
8. `test_no_user_effort_flag_reaches_the_reviewer_argv` (flipped)

The flipped test correctly asserts **both** no `--effort`/`--reasoning-effort` flag **and** presence of `-c` + `model_reasoning_effort=xhigh` (lines 832-842). The pre-existing `test_an_effort_key_is_refused_in_either_file` still enforces `effort_key_forbidden` for other keys.

## Check 5 — Regression + scope — PASS
- Adjacent suites green: `model_chain` + `invariants` + `adversarial` → **164 passed**.
- `ruff check` on the three files → **All checks passed!**
- `python tools/modularity_check.py --check` → **failures 0** (354 files). `codex_reviewer.py` is classified in the *warning* band (600–750), not the *justification* band (≥750) — consistent with the report's 737 SLOC claim; no expiring exception required.
- Behavior-neutral cleanups confirmed from the diff: `config.py` removed an empty `f""` prefix on `"configuration file not found"` (ruff F541); the test file removed an unused module-level `import os` (`os` only appears inside the FAKE_CODEX subprocess string). Both proven neutral by ruff + full suite green.
- Claude/Fable effort untouched (R783): the permitted path is codex-specific; `claude` `ProviderSelection` carries no effort field; a `claude.*effort*` key would still hit `effort_key_forbidden`.
- Cohesion justification is reasonable: `_effort_ladder`/`_review_at_effort` are tightly coupled to the review flow and self state; the extraction *improves* cohesion by naming the bounded-retry loop rather than fragmenting the review responsibility across a module boundary.

## Owner-gated follow-ups (outside G3 code scope; correctly deferred in report §6)
The ≥1165-test freeze baseline reconciliation, R247 recertification at the new frozen identity, controller reinstall, and live `xhigh`/`gpt-5.6-luna` acceptance confirmation remain owner-gated. `gpt-5.6-luna` is not yet in the codex allowlist (config-time addition, per Amendment 53). These are the orchestrator's/owner's to complete before live activation and are not a G3 blocker. Independent DCV (directive-compliance-verifier) over Amendment 52/53 requirement IDs is a separate pass.

## Defects
None blocking. Two minor non-blocking hardening notes (Check 2: permitted-path admitted-but-ignored in controller config; Check 3: doubled attempts on per-tier failure — intended).

VERDICT: PASS
ctl24 HEAD reviewed: ff79da01470c9ad7e8313d0a6704e9efd44fa139 (content identity `431018cf`)
