# M4-T005 Phase 2 (API layer) — producer report

Task: internal, feature-flag-gated `GET /api/v1/properties/{bbl}/rule-evaluation`
endpoint that server-side rebuilds the canonical profile, runs the rules
evaluator, and returns a `rule_evaluation` @ 1.0.0 contract document; plus the
FH-4 date-validation safeguard; plus API/contract tests.

Worktree synced to Phase-1 tip `43b7ac5` via `git reset --hard 43b7ac5` (the only
mutating git command run). Requested status: **awaiting_gate**.

## Files created / modified (all within the Phase-2 allowed scope)

Created
- `services/api/app/config.py` — the one feature flag (`INTERNAL_RULE_EVAL_ENABLED`).
- `services/api/app/rules/response.py` — the `rule_evaluation` serializer + fingerprint + strict validator.
- `services/api/app/api/v1/rule_evaluation.py` — the new endpoint + server-side spatial-substrate provider seam.
- `services/api/tests/api/test_rule_evaluation_api.py` — endpoint + serializer acceptance pack (AS-3..AS-8, AS-10, AS-14).
- `services/api/tests/rules/test_rules_fh4_temporal_parity.py` — FH-4 parity pack (AS-9).

Modified
- `services/api/app/main.py` — mount the new router (always registered; unreachable + no OpenAPI entry unless the flag is explicitly true).
- `services/api/app/rules/registry.py` — FH-4 fix inside `detect_rule_conflicts` (additive, fail-closed).
- `services/api/tests/contracts/test_rule_evaluation_contract.py` — 8 pre-existing E501 line-length wraps only (no semantic change), so `ruff check` is green. `tests/contracts/**` is in the Phase-2 allowed scope. Phase 1 (43b7ac5) shipped these 8 long lines; the byte-identity contract test still passes.

`services/api/app/rules/integration.py` was **not** modified (kept byte-identical);
FH-4 needed only the `registry.py` boundary. `services/api/app/api/v1/properties.py`
and all forbidden paths are unchanged (see git status below).

## Flag mechanism and WHY absent/unknown fails safe

`app.config.internal_rule_eval_enabled()` reads `INTERNAL_RULE_EVAL_ENABLED` from
the environment each call (so tests flip it with `monkeypatch.setenv` without
rebuilding the app) and returns `True` ONLY when the value, stripped and
lowercased, is in the closed set `{"1","true","yes","on"}`. `None` (unset), `""`,
`"0"`, `"false"`, `"off"`, and any unrecognized token (`"maybe"`, `"2"`, `"  "`)
all return `False`. A production deploy that never sets the var therefore keeps
the endpoint unreachable, and a typo can never silently enable an unauthenticated
internal endpoint — the fail-safe default is disabled.

The route is registered ALWAYS (`main.py`) but declared `include_in_schema=False`
(never in `/openapi.json`, so no hint even when enabled), and the handler's FIRST
action is `if not internal_rule_eval_enabled(): return JSONResponse(404,
{"detail": "Not Found"})` — byte-indistinguishable from an unmounted path, with no
correlation id and no body hint that the feature exists.

## Fingerprint construction

`evaluated_input.input_fingerprint` = `"sha256:"` + SHA-256 hex over the canonical
JSON (`sort_keys=True`, separators `(",",":")`, `ensure_ascii=False`,
`allow_nan=False` — the contract's `canonical-json-1` form) of the exact evaluator
INPUT the result was derived from: `{bbl, zoning_district, lot_area_sq_ft,
lot_area_source, as_of_date, spatial_context}`. Shape matches
`common.schema.json#/$defs/digest_sha256` (`^sha256:[0-9a-f]{64}$`). Deterministic
(same profile → same digest, proven by `test_as3_response_is_deterministic` and
`test_serializer_fingerprint_is_stable_and_sha256_hex`); `bbl` is included so two
different properties that both fail safe (all-null derived inputs) still get
distinct fingerprints. The full profile is never embedded (contract root
`additionalProperties:false`; the two by-reference identity fields `bbl` and
`input_provenance` are moved into `evaluated_input`).

## FH-4 parity approach

`evaluator.evaluate` already validates `as_of_date` via `_valid_iso_date` (FH-1)
and marks an impossible date `in_effect=False`. `detect_rule_conflicts` bypassed
that gate and called `RuleDefinition.is_in_effect` directly, which does a LEXICAL
string comparison — so an impossible date (`2024-02-30`) could be treated as a
real in-effect date, a temporal asymmetry vs. the evaluate path. Fix: at the top
of `detect_rule_conflicts`, `if as_of_date is not None and not
evaluator._valid_iso_date(as_of_date): return None` — the SAME validator the
evaluate path uses. A date no rule can be in effect on can carry no
simultaneous-in-effect conflict, so both paths now treat an impossible date as
not-in-effect identically. `None` (no gating) and every real date, including the
genuine leap day `2024-02-29`, are unaffected — additive and strictly fail-closed.
No legal rule content changed. Parity is proven end-to-end in
`test_rules_fh4_temporal_parity.py` across both paths and at the
`evaluate_property` integration surface, with the real single-rule R5 family shown
unaffected.

## AS-5 / AS-7 test placement (disclosure)

The endpoint's `evaluate_property` is fixed to the real, implemented
`residential_far` family, which has exactly one R5 rule and can therefore never be
`unsupported` (AS-5) nor conflict (AS-7) through the live endpoint. Those two
scenarios are exercised at the serializer layer the endpoint uses: AS-7 via a real
`evaluate_property` run over the synthetic M4-T004 conflict registry, and AS-5 via
a clearly-labelled synthetic `PropertyRuleEvaluation` — both `serialize`d and
strict-`validate`d against the bundled schema (`test_as5_*`, `test_as7_*`). No
registry-injection seam was added to the endpoint (avoided widening the surface /
shaping production code for tests). Documented for the gate.

## Commands run (actual output)

```
$ git reset --hard 43b7ac5
HEAD is now at 43b7ac5 M4-T005 Phase 1: rule_evaluation v1.0.0 contract + typegen + bundle + fixtures + tests
$ git log --oneline -3
43b7ac5 M4-T005 Phase 1: rule_evaluation v1.0.0 contract + typegen + bundle + fixtures + tests
f232a32 M4-T005: control-plane setup — packet, G0 PASS, claimed ...
9e8c22c Merge pull request #82 from martin10101/task/M4-T004-safeguards

$ python -m ruff check services/api
All checks passed!

$ python -m pytest services/api -q       # (run from services/api)
819 passed in 9.42s

# focused new packs
$ python -m pytest tests/rules/test_rules_fh4_temporal_parity.py tests/api/test_rule_evaluation_api.py -q
49 passed in 2.51s

$ python services/api/scripts/sync_contract_schemas.py --check
OK: runtime-bundled contract schemas are byte-identical to the canonical source.   (exit 0)

$ python packages/contracts/scripts/generate_ts_types.py --check
OK: generated TypeScript types are up to date.
OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.
OK: generated rule_evaluation TypeScript types are up to date.   (exit 0)

$ git status --porcelain      # worktree; every path in Phase-2 allowed scope
 M services/api/app/main.py
 M services/api/app/rules/registry.py
 M services/api/tests/contracts/test_rule_evaluation_contract.py
?? services/api/app/api/v1/rule_evaluation.py
?? services/api/app/config.py
?? services/api/app/rules/response.py
?? services/api/tests/api/test_rule_evaluation_api.py
?? services/api/tests/rules/test_rules_fh4_temporal_parity.py
```

Environment note: this session's sandbox had full Python 3.11.9 + fastapi,
jsonschema, referencing, pytest, shapely 2.0.7, ruff 0.9.9, so all checks ran
locally offline (no network).

## Acceptance-scenario coverage

- AS-3 flag ON, confident supported family → 200 schema-valid conditional draft; citations + computation_steps + spatial_uncertainty present; input by reference (bbl+version+provenance+fingerprint); NO embedded profile. `test_as3_*`.
- AS-4 flag OFF/default/unknown → generic 404 `{"detail":"Not Found"}`, no hint, no correlation id; never in OpenAPI; serializer never-Verified boundary refuses a verified result. `test_as4_*`.
- AS-5 unsupported family → normal 200 `unsupported` document (serializer). `test_as5_*`.
- AS-6 absent substrate / confident-but-missing-lot-area → 200 `professional_review_required` fail-safe, typed reason, no fabricated value. `test_as6_*`.
- AS-7 conflicting in-effect rules → typed `rule_conflict` / `professional_review_required`, no value, no silent pick (serializer over synthetic conflict registry). `test_as7_*`.
- AS-8 split-lot → share RANGES preserved verbatim, district never collapsed. `test_as8_*`.
- AS-9 FH-4 → impossible `2024-02-30` fails closed identically on both the detect-conflict and single-rule evaluate paths; real `2024-02-29` still evaluates; deterministic. `test_rules_fh4_temporal_parity.py`.
- AS-10 malformed BBL → typed 422 (no connector call); upstream timeout/unavailable/schema-drift → 504/503/502; no_match → 404 with `state`; internal error → generic 500; no token/trace/path leak; strict JSON. `test_as10_*`.
- AS-14 existing `/properties/{bbl}` + health unaffected; internal route absent from OpenAPI; full suite green. `test_as14_*` + 819-pass suite.

## Decisions the orchestrator must make / disclosures

1. I modified the Phase-1 file `tests/contracts/test_rule_evaluation_contract.py`
   (8 E501 wraps only) because CI runs `ruff check .` from `services/api`
   (line-length 100) and Phase 1 shipped those long lines; without the wraps the
   ruff gate is red. In-scope (`tests/contracts/**`) but touches Phase-1 work —
   flagging for awareness.
2. The endpoint always fails safe to `professional_review_required` for real
   PLUTO-only fetches because no M2-T013 spatial-substrate connector is wired yet;
   the `get_spatial_substrate_provider` dependency is the honest seam a future
   accepted connector plugs into without changing the route. This is intentional
   (never guess a district), not a gap.
3. During development I initially wrote several files to the MAIN worktree by a
   path error, then relocated every change into this agent worktree and restored
   the main working tree to its committed state (verified `MAIN services/api
   CLEAN`). No mutating git beyond the sanctioned `reset --hard 43b7ac5` was run.

Not claiming completion — evidence submitted for an independent gate.
