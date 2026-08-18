# End-to-end compiler benchmark (M0-T075)

## Method

the ACTUAL integrated compiler (context_pack build/emit) invoked per shape with the same task packet, diff base, role, provider/model, reasoning setting (none recorded — the compiler takes no reasoning argument), and source snapshot, cold then warm

## Checks

- **cold_warm_deterministic**: PASS
- **global_budget_or_split_refusal**: PASS
- **required_evidence_completeness**: PASS
- **exact_provenance**: PASS
- **graph_source_evidence_resolved**: PASS
- **advisory_memory_handled**: PASS
- **requirement_texts_end_to_end**: PASS

## Shapes

| shape | cold==warm | budget | sufficient | provenance | evidence |
|---|---|---|---|---|---|
| single_file_bug | True | True | True | True | True |
| cross_module_change | True | True | True | True | True |
| frontend_backend_boundary | True | True | True | True | True |
| schema_change | True | True | True | True | True |
| control_plane_only | True | True | True | True | False |

## Baseline comparison (G0, R042)

- status: compared
- M0-T066: integrated 18 sources vs baseline 8; missing none; no-worse=True
- M0-T067: integrated 17 sources vs baseline 8; missing none; no-worse=True

- provider token savings: UNMEASURED — no provider-reported usage exists in this offline benchmark (D-013-R012/R057)
