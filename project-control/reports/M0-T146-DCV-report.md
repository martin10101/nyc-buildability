# M0-T146 Directive-Compliance Verification (DCV) — D-024, 17 rows R767–R783

> Orchestrator note: verifier return saved verbatim (transport entity-decoding only). Verifier: independent directive-compliance-verifier agent (read-only), returned 2026-09-04 (UTC). 15 PASS / 2 UNVERIFIABLE (owner-gated) / 0 FAIL. The 2 UNVERIFIABLE rows are the owner-gated recert/reinstall/live-confirm sub-obligations; M0-T146 code + G0/G2/G3/G5 are complete, and formal acceptance is coupled to those owner-gated activation steps.

**Repo:** C:\Users\MLFLL\Downloads\nyc-zoning\ctl24 · **branch** candidate/D-024-mrl-option-b
**ctl24 HEAD reviewed:** `ff79da01` · **content identity:** `431018cf` (blob-scope: codex_reviewer.py, config.py, test_agent_supervisor_reviewer.py, M0-T146-codex-max-effort.md)
**Reproduced:** `pytest test_agent_supervisor_reviewer.py` → 92 passed; `adversarial+invariants+model_chain` → 164 passed, 0 fail; `git show 431018cf`; `git branch/for-each-ref --contains` → local-only; no `mrl/`, no `run_*`, no R247 artifact.

| ID | Verdict | Evidence (reproduced) |
|---|---|---|
| D-024-R767 | PASS | `codex_reviewer.py:70` `DEFAULT_REVIEW_REASONING_EFFORT="xhigh"`; build_argv emits `model_reasoning_effort=xhigh`; test_no_user_effort_flag asserts it (argv). |
| D-024-R768 | PASS | build_argv diff: `argv += ["-c", f"model_reasoning_effort={reasoning_effort}"]` then `"-"`; test_build_argv_threads asserts `-c` present, no `--effort`. |
| D-024-R769 | PASS | build_argv raises `reasoning_effort_invalid` off-enum; FORBIDDEN_REVIEWER_FLAGS check retained; test_build_argv_rejects_an_effort_outside_the_enum passes. |
| D-024-R770 | PASS | Config-driven `ProviderSelection.reasoning_effort` (one-line) + `_effort_ladder` steps down; downgrade tier is `medium` per controlling Amendment 53 R777 (supersedes Am.52 "high"). |
| D-024-R771 | PASS | Positive (threads xhigh, red-on-mutant if `argv+=` removed), no-FP (omit-when-unset), negative (enum reject "ultra") — all green in the 92-pass run. |
| D-024-R772 | UNVERIFIABLE | Session parts PASS (commit cites "D-024-R775 qualifying evidence"; baseline spot-corroborated; no live review, no `mrl/`, not pushed) but the **R247 recert artifact / reinstall / live xhigh confirm are owner-gated and absent** — no artifact names 431018cf except the evidence-map. |
| D-024-R773 | PASS | Report §2 changed files, §1 max→xhigh+reasoning, §5 validation, §6 R247 consequence; commit SHA carried by the post-review session response (report predates its own hash) per task guidance. |
| D-024-R774 | PASS | config.py `PERMITTED_EFFORT_KEY_PATHS={("codex","review_reasoning_effort")}`; other effort keys → `effort_key_forbidden`; supersession recorded append-only in source-053-amendment.md; B-021 resolved; test_the_effort_key_exception_is_narrow passes. |
| D-024-R775 | PASS | build_argv emits `-c model_reasoning_effort=xhigh` for the primary; enum `("minimal","low","medium","high","xhigh")`; test_the_effort_tiers_match_the_documented_enum passes. |
| D-024-R776 | PASS | `review_model` + `reasoning_effort` are single runtime-config values (load_model_selection); swap is config-only, no code edit; report §4. |
| D-024-R777 | PASS | `_effort_ladder` sol@xhigh→sol@medium; `resolve_model` gives sol→fallback-model@medium; test_a_fallback_model_review_runs_at_the_downgrade_tier asserts `model_reasoning_effort=medium`. NOTE: luna is not hardcoded — the generic fallback supports it; the **luna allowlist entry is a runtime-config add at the owner-gated reinstall** (report §4), not in this source commit. |
| D-024-R778 | PASS | `model_fallback_engaged` (registered in policy.NOTIFY_EVENTS, surfaced via `notify_events→loop:2044`, asserted in test) covers sol→fallback; `codex_effort_downgraded` added on the tier step. Surface is real, not invented. NOTE: codex_effort_downgraded is not in policy.NOTIFY_EVENTS and its emission isn't directly unit-tested, but flows through notify_events regardless. |
| D-024-R779 | PASS | Fail-closed twice: build_argv `reasoning_effort_invalid` + assert_no_effort_key `effort_value_invalid`; model-dependency caveat recorded (report §1/§6, owner-gated live confirm). |
| D-024-R780 | UNVERIFIABLE | Session parts PASS (owner-authorized exception cited; ≥1165-test baseline spot-corroborated 256/0-fail across 4 suites; NO live review launched; audit/mrl unchanged) but the **R247 recert / controller reinstall / live confirmation are owner-gated and not present this session** — explicitly deferred by the requirement text. |
| D-024-R781 | PASS | No `gpt-6-astra` switch in the diff; config-driven swap (R776) supports a later one-command switch; report §4. |
| D-024-R782 | PASS | Report §2 files, §1 tier max→xhigh+reasoning, §4 ladder + notification surface, §6 R247 consequence; commit SHA via session response per task guidance. |
| D-024-R783 | PASS | claude `ProviderSelection` (config.py:575) carries NO reasoning_effort; PERMITTED_EFFORT_KEY_PATHS is codex-only; diff touches only the codex review effort path — Claude/Fable prohibition intact. |

**Summary count:** 15 PASS · 2 UNVERIFIABLE (R772, R780) · 0 FAIL · 0 NOT_APPLICABLE (17/17).

**Is M0-T146 acceptance blocked at 431018cf by the UNVERIFIABLE rows?** **No.** R772/R780 are UNVERIFIABLE only in their owner-gated sub-obligations — the R247 recertification artifact, the controller reinstall, and the live confirmation that `gpt-5.6-sol` accepts `xhigh`. The requirement texts themselves place these behind the owner-gated live-run boundary ("the session launches NO live review"), i.e. they are post-acceptance owner actions, and I independently confirmed the session correctly launched none (no `mrl/` dir, no `run_*`, commit unpushed). Every session-scoped obligation across all 17 rows is SATISFIED with reproduced evidence and zero FAIL. Those two owner-gated items MUST be completed by the owner after acceptance and remain open on the ledger.

**VERDICT: PASS**
