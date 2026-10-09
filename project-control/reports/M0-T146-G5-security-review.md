# G5 Security/Privacy Review — M0-T146 (Codex reviewer MAX reasoning effort)

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only). Reviewer: independent security-reviewer agent (read-only), returned 2026-09-04 (UTC).

**Task:** M0-T146 — thread supervisor-set reasoning-effort tier into the FROZEN Codex reviewer.
**Content commit:** 431018cf • **HEAD reviewed:** ff79da01470c9ad7e8313d0a6704e9efd44fa139
**Reconciliation:** 3 commits sit between the content commit and HEAD (`f0783781` evidence map, `781e0687` submit record, `ff79da01` G2 PASS) — all control-plane only. `git diff 431018cf..HEAD` on the three source files (`codex_reviewer.py`, `config.py`, `test_agent_supervisor_reviewer.py`) is **empty**; the reviewed source is byte-identical at HEAD.
**Scope:** read-only inspection + read-only test/probe scripts. No writes, no git/gh/project_control.

## Check 1 — Narrow-exception integrity — PASS

`config.assert_no_effort_key` (config.py:154-182) admits **only** the exact path `PERMITTED_EFFORT_KEY_PATHS = {("codex","review_reasoning_effort")}` and only with a value in `CODEX_REASONING_EFFORT_TIERS = (minimal, low, medium, high, xhigh)`. `_walk_keys` (122-133) records every key at every depth including intermediate mapping keys and list items, so a nested/container `effort` key cannot hide. Membership is exact full-tuple match (`tuple(path) in PERMITTED_EFFORT_KEY_PATHS`), not a leaf/substring test.

I ran 15 adversarial config probes directly against `assert_no_effort_key`:

| Probe | Result |
|---|---|
| `codex.review_reasoning_effort = "xhigh"` | ADMITTED (intended) |
| `... = "ULTRA"` / `""` / `"xhigh "` (trailing space) | REJECTED `effort_value_invalid` |
| `... ` as TABLE / as int `5` | REJECTED `effort_value_invalid` |
| `codex.reasoning_effort` | REJECTED `effort_key_forbidden` |
| `codex.tuning.effort` (nested) | REJECTED `effort_key_forbidden` |
| `codex.tuning.review_reasoning_effort` (deeper path) | REJECTED `effort_key_forbidden` |
| **`claude.review_reasoning_effort`** | REJECTED `effort_key_forbidden` |
| top-level `review_reasoning_effort` | REJECTED `effort_key_forbidden` |
| `codex.Review_Reasoning_Effort` (case variant) | REJECTED `effort_key_forbidden` |
| `codex.review_reasoning_effort_extra` (leaf superset) | REJECTED `effort_key_forbidden` |
| `effort` used as intermediate container key | REJECTED `effort_key_forbidden` |
| effort key inside a list element | REJECTED `effort_key_forbidden` |

The Claude/Fable prohibition is fully intact: `claude.review_reasoning_effort` is rejected — only the `codex` path is permitted. `assert_no_effort_key` is invoked on both config-load paths (config.py:369 immutable controller, :543 `load_model_selection` before `ProviderSelection` is built at :565), so the value is validated before use. `_require_string_or_empty` only `.strip()`s a value that already passed strict enum validation on the raw form, so whitespace is not a bypass. **No key path or value slipped the narrowing.**

## Check 2 — argv-injection surface — PASS

`build_argv` (codex_reviewer.py:104-156) enum-validates **before** insertion: `if reasoning_effort not in CODEX_REASONING_EFFORT_TIERS: raise ReviewError("reasoning_effort_invalid")`, then appends the two fixed tokens `["-c", f"model_reasoning_effort={reasoning_effort}"]`. The `-c` key name and `model_reasoning_effort=` prefix are hard-coded literals — no arbitrary `-c key=value` is reachable; the only variable is the enum tier. argv is a list (no shell), so a tier value is always one token.

7 injection probes through `build_argv` all failed closed:
- `"xhigh --dangerously-skip-permissions"`, `"medium -c sandbox=danger"`, `"xhigh\n--effort=max"` → all `ReviewError: reasoning_effort_invalid` (rejected before any token is built).
- valid `xhigh`/`medium` → build `... -c model_reasoning_effort=<tier> -`; empty → no `-c` added.

`process.EFFORT_ARGUMENT_PREFIXES = ("--effort","--reasoning-effort")` (process.py:81) and `assert_argv_safe` (152-197) are **unchanged**. Confirmed by probe: `--effort`, `--effort=max`, `--reasoning-effort`, `--reasoning-effort=xhigh` all `HardDenyError`; the `-c model_reasoning_effort=xhigh` config-override token is correctly admitted (it is not a `--effort` flag and does not match the `prefix + "="` form). `build_argv` still terminates with `assert_argv_safe(argv)` and `FORBIDDEN_REVIEWER_FLAGS`. The reviewer invocation retains **`--ephemeral --ignore-user-config --strict-config --sandbox read-only --json`** with the `sandbox != REQUIRED_SANDBOX` guard intact (121-125) — no weakening.

## Check 3 — No provider-trust regression — PASS

The effort value originates only from supervisor state: `self.selection.selection("codex").reasoning_effort` (config file, validated) or the hard-coded `DEFAULT_REVIEW_REASONING_EFFORT="xhigh"`. `_effort_ladder` derives tiers from the config value and `resolution.fallback_engaged` (a supervisor model-resolution flag), never from model output. The model still produces only a schema-validated `CodexDecision` (`assert_codex_output_schema_strict`, unchanged); nothing in the decision path feeds back into effort. Read-only + `--ephemeral` + supervisor-recorded model (`resolution.model`) invariants preserved.

Retry is **bounded**: `_effort_ladder` returns at most `(primary_tier, "medium")` for the primary model (2 tiers) or `("medium",)` for a fallback model (1 tier). Each tier runs `_review_at_effort`, whose retry is `for attempt in range(1, self.max_attempts + 1)` (codex_reviewer.py:664) — the pre-existing bounded schema retry, unchanged. Total invocations ≤ 2 × `max_attempts`. No unbounded ladder.

## Check 4 — Regression / secrets / logging / new surface — PASS

- `python -m pytest tools/test_agent_supervisor_reviewer.py` → **92 passed** (20.0s).
- `tools/test_agent_supervisor_adversarial.py` + `tools/test_agent_supervisor_process.py` → **123 passed, 1 skipped** — all prior reviewer denials/invariants preserved.
- The suite directly asserts the narrowing and argv behavior: `test_the_effort_key_exception_is_narrow`, `test_no_user_effort_flag_reaches_the_reviewer_argv`, `test_build_argv_rejects_an_effort_outside_the_enum`, `test_the_effort_ladder_steps_down_from_the_max`, `test_the_effort_tiers_match_the_documented_enum` — matching my independent probes.
- No secret is introduced or logged. The only new emitted signals are event names `codex_effort_downgraded` / `model_fallback_engaged` (no sensitive payload). `-c model_reasoning_effort=xhigh` is not a secret. No new network call, no new file write (the pre-existing decision `tempfile` is unchanged), no new env inheritance.

## Check 5 — Freeze discipline — PASS

- Change cites **D-024-R775 / Amendment 52-53 (R774)** qualifying evidence in both packet and commit message, and D-004-R159 is **narrowly** superseded (owner-authorized; blocker B-021 resolved) — supported by the tight one-path exception verified in Check 1.
- **ruff**: `All checks passed!` on `codex_reviewer.py` and `config.py`.
- **modularity**: `modularity_check.py --check` exit code **0** (no failure). `codex_reviewer.py` is a pre-existing WARN (above warning threshold); the ~101 added lines are cohesive to the same responsibility (reviewer argv + bounded effort ladder), no dumping-ground/unrelated-domain mixing; `config.py` not flagged.
- Freeze-baseline plausibility: `pytest tools/ --collect-only` → **4206 tests collected**, consistent with the producer's 3633 pass/2 skip/0 fail baseline subset; the three suites I executed are fully green.

## Bypass attempts — none succeeded

15 config-key/value variants and 7 argv-injection payloads (spaces, newlines, appended `--dangerously-*`/`-c sandbox=`, bad enum, case, leaf-superset, nested, table, list, top-level, Claude path) all fail closed. No effort key or value slips the narrowing; no argv injection is reachable.

## Findings

- **Critical/High/Medium:** none.
- **Low/Informational:** `codex_reviewer.py` remains above the modularity warning threshold (non-blocking, RC=0); growth is cohesive. No action required for this gate.

Cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls, and prompt-injection surfaces are **not applicable** to this diff (supervisor argv/config only); the reviewer-hardening surfaces that are in scope (read-only sandbox, ignore-user-config, strict-config, effort-flag hard-deny, no provider-influenced control value, log redaction) are all preserved. Least privilege holds: effort is supervisor-set, enum-bounded, config-file-only.

VERDICT: PASS
ctl24 HEAD reviewed: ff79da01470c9ad7e8313d0a6704e9efd44fa139 (content identity 431018cf; source byte-identical at HEAD)
