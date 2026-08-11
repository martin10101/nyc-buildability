# CONTROL-PLANE VERIFICATION REPORT — M0-T057 (control-plane-verifier)

Saved verbatim by the orchestrator (transport only). Reviewer: `control-plane-verifier` (independent,
read-only; ≠ producer `orchestrator`, ≠ co-reviewer `code-reviewer`). Corroborating independent review
alongside the G3 code review. Reviewed head `8221419` / identity `6525ddfb`.

## VERDICT: PASS

The M0-T057 guard is control-plane-sound: additive, fail-closed at every lifecycle transition, and does not spuriously flag any legitimately-accepted or in-flight task. One non-blocking hygiene observation (an inert/redundant grandfather entry) is recorded below; it does not weaken any control and requires no correction before acceptance.

## Findings against the five required checks

### 1. Robust to #220's accepted state — CONFIRMED
`python tools/validate_directive_compliance.py --check` → exit 0 at HEAD. The guard does not flag any accepted or in-flight task. M0-T055/M2-T016/M0-T053/M0-T057 all bind real tracked files → non-empty, untouched by c17. Authoritative no-under-coverage proof: exit 0 means every in-regime task not grandfathered and not path-free-opted-in resolves NON-empty.

### 2. Grandfather allowlist correctness — CONFIRMED (with one non-blocking observation)
Frozen set at HEAD (8 entries): {M0-T026, M0-T032, M0-T054, M0-T056, M3-T002, M3-T003, M3-T004, M3-T005}.
- M0-T026, M0-T032, M0-T054 — allowed_paths == [] → trivially empty; need grandfathering (M0-T054 is the accepted continuation task that binds no code).
- M3-T002/T003/T004/T005 — prose pathspecs; under GIT_LITERAL_PATHSPECS each matches 0 tracked objects (independently confirmed by git ls-files). CONFIRMED empty.
- M0-T055 correctly DRAINED — absent, accepted, allowed_paths=['docs/LEAN_OPERATING_PROCESS.md'] (tracked) → non-empty (identity f3a6a363). No longer grandfathered and no longer needs it.

Runtime still fails closed on the empty entries: the runtime guard (`_task_git_identity`) does NOT consult the grandfather set — it is validator-only. Any attempt to submit/gate/accept the empty tasks is hard-refused by `frozen_git_identity(..., allow_empty_identity=False)`. No under-coverage (proven by exit 0).

OBSERVATION (non-blocking) — one over-coverage entry: M0-T056 is in the allowlist but now resolves NON-empty at HEAD — its allowed_paths bind 7 tracked files (tools/agent_supervisor/worker_turnover.py, turnover_controller.py, turnover_adapters.py, model_turnover.py, loop.py, cli.py, tools/test_agent_supervisor_model_turnover.py). It was an empty stub at the M0-T057 baseline (7cc1fed) and has since gained real paths (status ready). The membership is inert — the validator hits `if entries or cp_entries: continue` before the grandfather branch, so it neither suppresses a real error today nor affects the runtime guard. Recommended (not required) cleanup: drain M0-T056 from `_EMPTY_IDENTITY_GRANDFATHERED` at the next control-plane touch, exactly as M0-T055 was drained this session. Not a blocking correction.

### 3. Fail-closed at lifecycle transitions — CONFIRMED
`_task_git_identity` (project_control.py:375) reads `path_free_opt_in(t)` and calls `frozen_git_identity(..., allow_empty_identity=opted_in)`; it never touches the grandfather set. The empty-manifest refusal lives in `frozen_git_identity` (directive_registry.py:1622). submit (523), gate (1135), accept (552) all route through this one function and fail closed on its error. A malformed opt-in fails closed via `path_free_opt_in` (directive_registry.py:1227), enforced identically in CLI and validator.

### 4. No weakening of existing controls — CONFIRMED
Strictly additive: a NEW refusal branch inside `frozen_git_identity` gated by `allow_empty_identity` (default False, skipped when non-empty); a NEW validator function `_validate_empty_identity` appended, leaving c1–c16 untouched. Gate independence, acceptance evidence (v2), dirt/freshness/reviewed_sha checks unchanged. M0-T057's own allowed_paths resolve non-empty (identity 6525ddfb ≠ empty-set hash) and carry no opt-in marker, so the guard does not block M0-T057's own acceptance. 52 targeted guard/regression tests pass.

### 5. Ledger reconciliation — CONFIRMED
M0-T057.json: HEAD-committed status backlog/progress 0; live working tree shows the legal mid-gate state (awaiting_gate, G0/G2 recorded, in-flight submit for the G3 gate). directive_refs [{D-001, ALL}]; evidence map records 0 applicable D-001 requirements (legitimate empty-set citation, M2-T014/M0-T033 precedent). reviewer_agents [control-plane-verifier, code-reviewer]; producer_agent orchestrator; required_gates [G0, G2, G3]. No premature acceptance: accepted_at null; only G0 (administrative) + G2 (self-check) recorded, both legitimately orchestrator-run; independent G3 pending. Producer orchestrator ≠ both independent reviewers; the RESERVED_ORCHESTRATOR producer is valid via the governance exception. Both G0/G2 record reviewed_sha 8221419 (== HEAD) and identity 6525ddfb.

## Blocking corrections
None.

## Non-blocking recommendation
Drain M0-T056 from `_EMPTY_IDENTITY_GRANDFATHERED` (it now resolves non-empty; the entry is inert and its allowlist comment is stale), mirroring the M0-T055 drain done this session. Purely hygienic; safe to defer.

VERDICT: PASS — record the G3 gate as PASS.
