<!-- Saved VERBATIM by the orchestrator from the code-reviewer agent-return
     channel (report-preservation rule). Transport entity-decoding only
     ("&lt;" -> "<", "&gt;" -> ">"). -->

I have completed a comprehensive independent G3 code review. All review dimensions verified against the frozen reviewed identity. Here is my gate report.

---

# GATE REPORT — G3 Code Review — M0-T093 (D-024 Unit H1: guardrail-refusal classification + bounded 4.8 bridge)

**Reviewer:** code-reviewer (independent, read-only)
**Task:** M0-T093 — D-024 Phase E; supervisor-freeze qualifying evidence D-024-R103
**Frozen reviewed content identity:** `b58772027f2e9fb0d631f204dc249f29f1489404` (deliverables 633a9d1 + 0f4fc6a; packet amendment c7c0a36)
**Branch:** control/D-024-fable-codex-loop
**Verdict:** PASS (with 3 non-blocking observations)

## 1. Frozen-identity / control-plane isolation — VERIFIED

- `git diff b587720..HEAD -- tools/` is **EMPTY** (confirmed). Later commits are control-plane only.
- The single post-freeze commit `654a083` touches only `project-control/{gates,reports,state,tasks}` (in-regime submit + G2 self-check). No `tools/` change.
- `git status --porcelain` clean; working-tree `tools/` is byte-identical to b587720, so the on-disk files I reviewed ARE the frozen identity.

## 2. Facade-split fidelity — VERIFIED VERBATIM

- `diff <(git show 84f658e:tools/agent_supervisor/loop.py | sed -n '528,854p') <(sed -n '28,354p' tools/agent_supervisor/pending_prompt.py)` → **empty** (byte-identical). The 327-line pending-prompt approval-binding block (`approval_digest`, park/approve/consume records, M0-T048 covered-instruction reconstruction, M0-T046 sealed-audit cross-check) moved verbatim.
- Facade re-export block (loop.py 534-546) re-exports all 9 public names (2 constants + 7 functions) with `# noqa: E402,F401`.
- Consumer coverage confirmed: `cli.py` imports `approve_pending_prompt`, `verify_covered_instruction` from `.loop`; test packs import `approve_pending_prompt/consume_pending_prompt/pending_prompt_key` and use `lp.APPROVAL_DIGEST_FIELDS`; `test_agent_supervisor_audit_anchor.py` imports `pending_prompt_key` from `.loop`. All resolve through the facade. `start_gate.py`/`loop_turnover.py` import no moved name.
- The four accepted facade test packs pass unchanged at HEAD: pending_prompt **19**, park_approve_binding **9**, audit_anchor **6**, c2_binding **10** (matches report §4.2).

## 3. Classifier (guardrail_refusal.py) — VERIFIED fail-closed

- Decision order matches R068/R075: (1) None/uninspectable → AMBIGUOUS; (2) **quota-direction delegated to `classify_exhaustion` FIRST** → NOT_A_REFUSAL(quota) before any refusal recognition; (3) recognized-shape scan gated by three independent conditions — no co-occurring negative-guard signal (else CONTRADICTORY→AMBIGUOUS), `references_fable` attribution (else not_attributable→AMBIGUOUS), and `AuthorizedTaskRecord.proven` (task_id+authorization+acceptance_criteria; else authorization_unproven→AMBIGUOUS); (4) each negative guard routes to its own typed NOT_A_REFUSAL, refusal-looking-but-unrecognized → AMBIGUOUS.
- Corpus load is fail-closed: missing/malformed/one-bad-entry → empty corpus (recognizes nothing). Whole `classify_*` wrapped in try/except degrading to AMBIGUOUS (no fail-open crash).
- Condition codes are a closed vocabulary, disjoint from quota-side codes (asserted by S16 `test_refusal_and_quota_codes_are_disjoint`).
- S2 proves separation in BOTH directions over the model_turnover/claude_runner shape set (quota→never refusal; refusal→never exhaustion).

## 4. Bridge (refusal_bridge.py) — VERIFIED; no path reaches expansion or a second/live actuation

- `BridgeRestrictions`: closed 4-op vocabulary (`PERMITTED_BRIDGE_OPERATIONS`); explicit `FORBIDDEN_BRIDGE_OPERATIONS` typed-refused; anything else → `bridge_unknown_operation` (fail closed). `begin_landing()` at construction so `register_child` refuses new children; `may_spawn_children()` always False. `retire()` requires reconciled children, validates the handoff, latches `_retired`, after which every `authorize()` raises `bridge_retired` — irreversible, never continues past the first seam.
- **Double-gate `assert_actuation_permitted`** requires BOTH `shape_verified_live` AND `owner_authorized`; every fixture is `verified_live=false` and no R595 flag exists, so it always raises (S6 `test_live_actuation_is_double_gated`). `GuardrailBridgeIntegration` has **no actuation channel** and `evaluate()` returns `actuated=False` unconditionally (record-intent-only). No reachable code calls the gate with both True.
- `continuation_choice` selects only an exact allowlisted `model-continuation` matching the configured bridge model (unlisted model → refuse-all; no match → stop; >1 match → ambiguous refuse). Every other prompt shape is never answered.
- CAS counter (`record_reentry_attempt`): compare-and-swap loop retries on concurrent write (no lost update); raises `reentry_cap_exhausted` at MAX=2 (no third attempt). Bound to the restart-stable `RefusedRequest.digest()` (pure function of request fields, no run_id). S14 closes a real on-disk `DurableJournal` and reopens it, proving the count survives restart at 2 and a different request has its own counter.
- Semantic validator (`assert_semantic_preserved`): the transform is generated verbatim from structured fields; claimed-mode enforces exact equality of task_id/purpose/authorization, constraint superset (add-only), criteria set-equality, whole request_text; text-mode enforces verbatim containment of every material field plus an encoded-blob guard. Each prohibited transform (purpose/authorization/criteria alter, constraint delete, fragmentation, omission, encoding) has a distinct typed code and a negative test (S11). Euphemism is excluded structurally by the verbatim-containment requirement. Sound for the generated-text flow.
- `bridge_output_disposition` (R074): no/unrecognized verdict → review_required (never auto-accepted); FAIL/BLOCKED → rejected; only explicit PASS accepts. `decide_after_cap` (R072) is reachable only after the durable cap, refuses a different task, and BLOCKS conservatively on higher-precedence conflict / unlisted model / missing features / oversized-or-unknown workload / failed model_fit. `fallback_model_scope` (R165) returns fixed policy-boundary constants regardless of the native setting.

## 5. State machine — VERIFIED

- +2 states (`GUARDRAIL_BRIDGE`, `REPRESENT_FABLE`), +11 documented transitions; all target states pre-exist. Both states are non-blocking, non-terminal, have entry and exit edges (no stranded states), and every new edge is walkable through the real `StateMachine` and carries a non-empty doc (PhaseE tests + end-to-end path walk). Count assertions updated 27→29 in both `phase1` and `controller_succession` with citations.

## 6. Loop seam — VERIFIED minimal + byte-identical default

- The guardrail seam (loop.py 1596-1620) is placed **AFTER** the quota `worker_turnover` seam (R075 ordering) and BEFORE the unchanged `no_valid_checkpoint` fallthrough. Guarded by `if self._guardrail_bridge is not None`; constructor default `None`. `test_absent_integration_leaves_the_path_unchanged` proves the default path is behaviorally unchanged (`no_valid_checkpoint` + PAUSED_RECOVERY). `test_quota_seam_evaluates_first_and_wins_its_signal` proves loop-level R075 precedence. Real-`SupervisedLoop` seam tests confirm recognized-refusal → `guardrail_refusal_recorded` + PAUSED_RECOVERY + journaled identity-preserving record with no re-entry consumed.

## 7. Reproduced checks

- `python -m tools.test_agent_supervisor_guardrail_bridge` → **Ran 71 tests, OK** (matches report §4.3).
- Facade packs: pending_prompt 19 / park_approve_binding 9 / audit_anchor 6 / c2_binding 10 → all OK.
- `python tools/modularity_check.py --check` → **0 failures**, 7 advisory warnings.
- `ruff 0.13.0 check <6 new/changed supervisor+test files>` → **All checks passed!**
- Additive-only `model_turnover.py` public aliases (no removed names); fixture JSON is provenance-honest (`confidence: documented`, `verified_live=false`, `status: pending-owner-C1`). Redaction test proves `sk-ant-` secrets are stripped and the excerpt bounded.

## 8. Non-blocking observations (do not affect verdict)

1. **Modularity — refusal_bridge.py cohesion justification not recorded in producer report.** The file is 970 physical lines and trips the `review_signal` at the justify (750 SLOC) threshold; `modularity_check --check` passes at 0 failures (below the 1000 hard cap, so no exception file is required). Report §4.2 records loop.py's baseline_growth resolution but does not explicitly record a cohesion justification for the NEW module. As reviewer I record it: the module is genuinely cohesive around the single R070-R074 bounded-bridge policy responsibility (journal record, continuation choice, restriction layer, output disposition, R071/R073 transform+validator, durable counter, R072 lower-tier decision, R165 scope, status facts, loop seam), sharing `BridgeError`/`RefusedRequest`/the durable journal keys, with no unrelated domain logic, storage, or presentation mixed in. A future extraction of the R073 re-presentation transform + validator is worth considering if the module grows further.
2. **Pre-existing loop.py F401s (5):** `re`, `.evidence.STOP_FOR_OWNER`, `.owner_touch.{COUNTED_TOUCH_KINDS,OWNER_TOUCH_KEY,TOUCH_NOTIFY}`. Confirmed unrelated to the move (the moved block imports none of them; its own deps `build_forwarded_prompt`/`DENY_AND_HALT`/`is_synchronous_stop` remain used in loop.py), and outside CI's ruff scope (CI runs `ruff check .` with `working-directory: services/api`). Honestly disclosed in report §4.2; not a regression from this unit.
3. **Control-plane / evidence writes:** the unit diff also touched `project-control/tasks/M0-T093.json` (packet allowed_paths amendment c7c0a36, an orchestrator control-plane action) and `project-control/reports/M0-T093-evidence-map.json` (49-row DCV evidence). These are outside the producer's code scope and are the orchestrator/DCV artifacts; the full 49-requirement directive verification is the independent `directive-compliance-verifier` pass (verification.json), not this G3 code gate.

## Conclusion

The code is correct, uniformly fail-closed, honestly documented (SHADOW-ONLY, record-intent-only, pending-owner-C1, verified_live=false all stated truthfully), and comprehensively tested. The classifier decision order, CAS/restart counter semantics, bridge restriction completeness (no reachable expansion or live/second actuation), semantic-preservation soundness, state-machine legality, loop-seam minimality with a byte-identical default path, and the verbatim facade split all hold under independent reproduction. The observations are documentation/hygiene notes that do not block the gate.

Relevant files (absolute):
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\guardrail_refusal.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\refusal_bridge.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\pending_prompt.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\loop.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\state_machine.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\model_turnover.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\guardrail_refusal_shapes_2_1_248.json
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_guardrail_bridge.py
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T093-guardrail-bridge.md

VERDICT: PASS
