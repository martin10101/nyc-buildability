# M0-T146 producer report — Codex reviewer MAX reasoning effort + fallback ladder

- **Task:** M0-T146 (governance/security; D-024 Amendment 52 R767–R773 + Amendment 53 R774–R783).
- **Producer:** orchestrator (owner-authorized feature exception to the supervisor freeze;
  qualifying evidence **D-024-R775**, cited here and in the commit).
- **Date:** 2026-09-04 (UTC).

## 1. Resolved decision: "max" → `xhigh`

codex-cli 0.146.0 has no literal `max` reasoning tier. The authoritative config reference lists
`model_reasoning_effort` as exactly `minimal / low / medium / high / xhigh` (default `medium`),
and `codex --strict-config` fails closed on any other value. Per the owner ("max = whatever the
top is called"), **max resolves to the verified ceiling `xhigh`**. Whether `gpt-5.6-sol` honors
`xhigh` at the API level is model-dependent and confirmable only on a live review (owner-gated);
the ladder below steps down to `medium` if the top tier fails.

## 2. Changed files (exactly three code/test paths + this report)

| Path | Change |
|---|---|
| `tools/agent_supervisor/config.py` | Narrowed `assert_no_effort_key` to admit ONLY `codex.review_reasoning_effort` (R774), value-validated against the new `CODEX_REASONING_EFFORT_TIERS`; every other effort key stays permanently forbidden. Added `ProviderSelection.reasoning_effort`, parsed from `[codex] review_reasoning_effort`. (Also removed one pre-existing empty f-string prefix to keep the file ruff-clean.) |
| `tools/agent_supervisor/codex_reviewer.py` | `build_argv` now threads the supervisor-set tier via `-c model_reasoning_effort=<tier>` (R775), enum-validated + fail-closed (R779) — NOT the hard-denied `--effort`/`--reasoning-effort` flags (R769). Added the effort ladder (`_effort_ladder` + `_review_at_effort`): the primary model runs at the configured/default **max** and steps DOWN to `medium`; a fallback MODEL runs at `medium`; each downgrade emits a `codex_effort_downgraded` notify, and the existing `model_fallback_engaged` notify surfaces the Sol→fallback step (R777/R778). |
| `tools/test_agent_supervisor_reviewer.py` | Flipped the old "no effort at all" test to the new policy; added positive/negative/enum/narrowing/ladder/fallback-tier tests (R771). |
| `project-control/reports/M0-T146-codex-max-effort.md` | This report. |

## 3. The narrow R159 supersession (R774)

`D-004-R159` ("no effort key ever written / the supervisor never passes effort") is superseded
**only** for the supervisor-set `codex.review_reasoning_effort`, per owner directive D-024
Amendment 53. Enforced precisely: `assert_no_effort_key` admits that single key with a valid
tier and rejects every other effort key (proved by `test_the_effort_key_exception_is_narrow`);
`process.EFFORT_ARGUMENT_PREFIXES` still hard-denies user-injected `--effort`/`--reasoning-effort`
in any synthesized argv (the `-c model_reasoning_effort=` config-override form is a different,
permitted shape). The Claude/Fable effort prohibition is untouched (deferred, R783).

## 4. Config-driven + easy swap (R776) + the ladder (R777) + notification (R778)

- The reviewer model (`review_model`) and its effort (`review_reasoning_effort`) are single
  runtime-config values, so switching either — including to a future `gpt-6-astra` (R781) — is a
  one-line change with no code edit. The default when unset is `xhigh` (the max).
- Ladder: `sol@xhigh → sol@medium → <fallback model>@medium`. `resolve_model` already gives the
  Sol→fallback model step with a `model_fallback_engaged` NOTIFY; the effort ladder adds the
  intra-model `xhigh→medium` downgrade with a `codex_effort_downgraded` NOTIFY. Both notify
  events flow to the owner surface via `ReviewOutcome.notify_events → loop`. (Runtime config to
  make `gpt-5.6-luna` the low-end fallback — adding it to the codex allowlist + `fallback_models`
  — is applied at the controller during the owner-gated reinstall; the code supports it now.)

## 5. Validation

- `python -m pytest tools/test_agent_supervisor_reviewer.py` → **92 passed** (exit 0), including
  8 new/updated effort tests: build_argv positive (`-c model_reasoning_effort=xhigh`), omit-when-
  unset, enum-reject (`reasoning_effort_invalid` on "ultra"), the narrow key exception
  (admit `codex.review_reasoning_effort`, reject bad value + other effort keys), the ladder
  `("xhigh","medium")`/`("medium",)`, and the fallback-model-at-medium + notify.
- `python -m pytest` on config/model-chain/invariants/adversarial suites → **244 passed** (exit 0).
- `ruff check` on all three files → **All checks passed**.
- `python tools/modularity_check.py --check` → **failures 0**. `codex_reviewer.py` is 737 SLOC —
  WARN band (600), under the JUSTIFY threshold (750); not a failure. Cohesion note (principle 16):
  the reviewer is one cohesive responsibility (build one read-only Codex review + bounded retries
  + resolved-model recording); the effort ladder is part of that review responsibility, so it
  stays in-module rather than fragmenting the review flow.
- Full `test_agent_supervisor_*` freeze baseline (≥1165 tests, 0 failures): **3633 passed, 2
  skipped, 0 failed** (exit 0, 289s) — the M0-T039 freeze baseline is reconciled at the new
  frozen identity.

## 6. R247 recert + reinstall + live confirmation (R780, owner-gated)

This changes the frozen supervisor tree, so the `M0-T039` suite baseline must reconcile (above)
and **R247 recertification** runs at the new frozen identity. The controller **reinstall** (so the
live loop uses the new code + the runtime config carrying `review_reasoning_effort = "xhigh"` and
the Luna fallback) and the **live confirmation** that `gpt-5.6-sol` accepts `xhigh` (and that the
account has `gpt-5.6-luna`) are **owner-gated** — the session launches no live review.

## 7. Producer self-checks (G2)

1. Scope: exactly the three allowed code/test paths (+ this report). PASS.
2. R159 narrowing is tight (only `codex.review_reasoning_effort`; user-injected flags still
   denied). PASS.
3. Fail-closed on an out-of-enum value; no unrecognized tier reaches `--strict-config`. PASS.
4. All prior reviewer/config denials preserved (92 + 244 green). PASS.
5. Deferred Claude-side effort NOT touched (R783). PASS.

Independent G3 (code) + G5 (security) + DCV follow.
