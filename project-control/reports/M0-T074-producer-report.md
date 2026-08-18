# M0-T074 producer report — deterministic complexity-based model routing

Producer: orchestrator. Branch `task/M0-T074-model-routing`, base `6bfc60a`
(stacked on task/M0-T073-modularity-enforcement per the ci.yml no-concurrent-overlap
protocol). Governing rows: D-017-R114..R123, bound at claim.

## Deliverables (requirement → artifact)

| Rows | Artifact | Content |
|---|---|---|
| R114 | `tools/model_routing.py` | routing by measured complexity/risk/capability; NO self-selection API (no model/preferred/override parameter exists) |
| R115 | `classify()` + policy §Bands | LOW/MEDIUM/HIGH/CRITICAL with the owner's exact work shapes |
| R116 | `Signals` dataclass (frozen, closed) | all ten owner signals typed; unknown signal names are a TypeError; every verdict carries determining_signals; ambiguity raises one band, never lowers |
| R117 | `load_permitted_models` + `route` + `record_quota_fallback` | allowlist read through the frozen supervisor's own config loader (read-only import; config bytes SHA-256 recorded as evidence); empty allowlist or unknown tier → RoutingError; nothing ever writes config.toml or model_selection.toml (`test_router_never_writes_config_or_selection`) |
| R118 | `route()` single-model branch | claude allowlist = [claude-opus-4-8] → adaptive_available=False, "UNAVAILABLE … not pretending selection occurred" |
| R119 | routing rules | LOW/MEDIUM → lower-cost permitted; HIGH/CRITICAL → stronger permitted; security-reviewer/directive-compliance-verifier/final-acceptance → strongest permitted independent reviewer |
| R120 | `escalate_after_failure` + `record_quota_fallback` | one recorded level for failed LOW/MEDIUM (reason mandatory); HIGH/CRITICAL never re-routed ("not silently downgraded"); quota fallback a separate recorded decision class |
| R121 | decision record + `append_decision`/`finalize` | task ID, band, determining signals, chosen model, permitted-model evidence (allowlist + config sha256), fallback status, context size, result, nullable telemetry (null ≠ zero); append-only JSONL under the per-checkout runtime dir (durable_state convention, outside the repo) |
| R122 | `tools/model_routing_corpus.json` (15 frozen cases) + `tools/test_model_routing.py` (21 tests) + ci.yml `model-routing` job | simple stays inexpensive (terra); HIGH/CRITICAL always sol and cannot route weaker; unauthorized/self-selected model, unrecorded fallback, and ungrounded classification all impossible |
| R123 | policy §Current honest state | protected allowlist change = owner action via the established procedure; repository implementation completes first; the router never requests it |

## Evidence

- `python tools/test_model_routing.py` → **21 tests OK** (corpus stability;
  grounded classification; allowlist boundaries; single-Claude honesty;
  escalation/no-downgrade; separate quota fallback; record fields; JSONL append;
  protected-config-format loading via the real supervisor loader; no
  config/selection writes in source).
- `python tools/modularity_check.py --check` on this branch → 0 failures
  (240 files; model_routing.py ≈ 300 SLOC, under the 600 warning threshold).
- Protected boundary: `tools/agent_supervisor/**` untouched (forbidden path);
  allowlist read-only; current live allowlist re-confirmed read-only at Stage 0
  identity: codex `[gpt-5.6-sol, gpt-5.6-terra]`, claude `[claude-opus-4-8]`.

## Boundary answers (modularity R111 discipline)

1. Responsibility: routing policy (docs), deterministic engine (tools), frozen
   proof corpus (fixture json). 2. Placement: new modules; no existing owner.
3. Thresholds: no file near a threshold. 4. Extraction: n/a. 5. Stable
   interfaces: none changed; ci.yml additive job only. 6. Boundary tests:
   `tools/test_model_routing.py`. 7. Modularity CI check: PASS.
