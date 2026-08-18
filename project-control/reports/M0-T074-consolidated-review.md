# M0-T074 consolidated review (code + security + directive-compliance) — verbatim reviewer return

Preserved verbatim by the orchestrator (report-preservation rule; transport
entity-decoding only). Independent reviewer subagent, read-only, at frozen HEAD
`3d392e0` (branch `task/M0-T074-model-routing`). Producer ≠ verifier. One
consolidated agent performed the code, security, and directive-compliance passes
(proportionate: routing is a bounded new module that does not touch the frozen
supervisor). Gates G3/G4/G5 are recorded from this single independent review.

---

# M0-T074 Consolidated Review — Model Routing (D-017-R114..R123)

## OVERALL VERDICT: **PASS**

Frozen HEAD `3d392e0`, merge-base with `task/M0-T073-modularity-enforcement` = `638ad74`. The M0-T074 code (`tools/model_routing.py`, test, corpus, policy, ci.yml) is byte-identical to its implementation commit `1059ab4`; later commits add only control-plane lifecycle records. All 21 tests pass; the router is honest against the live protected config; no supervisor, directive, or config files are modified.

## Exact command outputs
```
$ python tools/test_model_routing.py                  → Ran 21 tests OK
$ python tools/validate_directive_compliance.py --check → EXIT=0
$ git diff --name-only <merge-base> HEAD -- tools/agent_supervisor/     → 0 files
$ git diff --name-only <merge-base> HEAD -- project-control/directives/ → 0 files
# live config sha256 6aef12a9…fffde == D-017-R004 hash; claude=[claude-opus-4-8]; codex=[gpt-5.6-sol,gpt-5.6-terra]
claude CRITICAL/security-reviewer → chosen=claude-opus-4-8 adaptive_available=False "…UNAVAILABLE… not pretending…"
codex CRITICAL → gpt-5.6-sol ; codex LOW → gpt-5.6-terra
```

## CODE
1. Tests 21/21.
2. classify() sound: CRITICAL evaluated first and returns immediately (cannot be outvoted); every CRITICAL/HIGH R115 shape has a forcing signal; ambiguity raises exactly +1 and only for LOW/MEDIUM, never lowers HIGH/CRITICAL. Could not construct a CRITICAL-classifies-lower or HIGH-classifies-MEDIUM given correct signals. The only under-classification path is the caller omitting a CRITICAL signal — inherent to any signal classifier, out of module scope, partially mitigated by ambiguity fail-up.
3. route() deterministic, no self-selection param; empty allowlist / unknown-tier model / unknown provider all fail closed with RoutingError.

## SECURITY
4. Read-only allowlist via the supervisor's load_controller_config (parses TOML, no writes); records config-bytes SHA-256; no write path to config/selection; tools/agent_supervisor/** untouched (0 files); test_router_never_writes_config_or_selection present.
5. Single-model honesty (R118) re-derived from the LIVE config: hash matches directive; claude has exactly one model; route() returns adaptive_available=False, chosen=claude-opus-4-8, honest UNAVAILABLE; the single-model branch precedes the strongest-reviewer branch.
6. No subprocess/urllib/requests/socket/Popen/os.system (the one "requests" token is English prose).
7. CI model-routing job strictly additive; actions/checkout SHA-pinned identical to 16 other jobs; no secrets, no permissions block, single python3 run; consistent with the accepted sibling modularity job.

## DIRECTIVE-COMPLIANCE — R114..R123 all PASS
R114 no self-selection param; R115 four bands + corpus RC-01..15 + forcing signals; R116 closed Signals covers all 11 signals, unknown name TypeError, determining_signals cited, ambiguity +1; R117 read-only allowlist, config SHA recorded, no write path, supervisor untouched; R118 live claude=1 honest UNAVAILABLE; R119 LOW/MEDIUM lower-cost, HIGH/CRITICAL stronger, reviewer roles strongest; R120 one-level escalation w/ mandatory reason, HIGH/CRITICAL refused, quota fallback separate kind; R121 record fields complete, nullable telemetry, append-only JSONL outside repo; R122 15-case corpus + 21 CI tests + additive job; R123 policy names allowlist change as owner action after implementation. No directives/** changes; validator exit 0.

## Non-blocking observations (do not gate acceptance)
1. Consuming integration out of scope: classify() cannot up-classify a task whose CRITICAL signal was never set by the orchestrator; documented, mitigated by ambiguity +1; supervisor-side wiring deferred to a separate task. Acceptance is the routing ENGINE, not live wiring.
2. Two context-token fields (Signals.estimated_context_tokens drives classification; route() kwarg only records) — minor API footgun; both R116/R121 satisfied.
3. task.allowed_paths names M0-T074-evidence.md but the shipped file is M0-T074-evidence-map.json — cosmetic.
4. LOW→MEDIUM escalation keeps the lower-cost model (both bands map lower-cost) — consistent with R119, honest.
5. dependency_graph_spread 2-10 with a single file contributes nothing (threshold >10) — sound judgment call.
6. model-routing CI job has no explicit setup-python (relies on ubuntu 3.12 tomllib) — consistent with sibling; optional pin.
