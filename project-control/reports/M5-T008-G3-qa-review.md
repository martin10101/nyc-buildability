# M5-T008 — G3 QA Review (independent)

- **Gate:** G3 (QA / test adequacy / regression / mutation)
- **Verdict:** PASS
- **Reviewer:** qa-engineer (independent; ≠ producer)
- **Reviewed SHA:** `24780f2683dafd41b895fa2d1668814a19a6b3e4`

## Identity
Reviewer auto-isolated (Write-capable); resolved SHA read-only via git ref files: ctl24/.git → worktree HEAD ref candidate/D-024-mrl-option-b → 24780f26 (matches). Reproduced against ctl24 files by absolute path.

## Reproduction & regression — PASS
`pytest services/api/tests/scenario` → 222 passed (Python 3.11.9). ranking... sensitivity file 49 passed; suite minus sensitivity 173 passed (0 regression). `--collect-only` → 49 items from 25 test funcs. 222 = 173 + 49 confirmed. modularity_check → failures 0, sensitivity.py not in the 14 warnings.

## Boundary adequacy (7 boundaries) — all COVERED
1 explicit-values-only/never-fabricate (AS-3). 2 named variable+metric on response AND every point (AS-2). 3 point = surfaced numbers only, no recompute (AS-6/AS-7 assert point["derived"]==derive_practical_usable_range(...) and response_point==cap×factor_product; RECOGNIZED_FACTOR_TYPES=={utilization_factor,efficiency_ratio}==SensitivityVariable members). 4 total/stable order incl duplicates/reorderings (AS-1 forward==reversed==shuffled, duplicate preserved). 5 fail-closed + strict-JSON-safe — strongest (AS-4: malformed variable 8 params, no-cap EMPTY, malformed container incl tuple, degenerate doc, malformed value 11 params incl 10**5000, unserializable object, huge-int, object dict-key). 6 never up-labels/never Verified (AS-5). 7 contract-free/read-only/offline (AS-6 byte-unchanged/not-aliased; offline inherent).

## Mutation sense-check — both load-bearing
- Sanitizer removed (_json_safe→identity): object value → TypeError; huge int → ValueError inside derive() at derive.py:367 (the pre-derive-sanitization crash). Real sanitizer keeps all json-safe. → JSON-safety tests load-bearing.
- Sort made input-order-dependent (_sort_key→constant): AS-1 ordering assertion False + fwd==rev False. → ordering tests load-bearing.

## Not-derivable / empty-baseline — verified
Not-derivable value (0.0 out of derive's (0,1] domain) kept FIRST by value, derivable=False, response_point=None, reason set, derivable_count 2/3, no fabricated point. Empty values → single baseline point (point_count=1, is_baseline=True, value=None, response_point==cap==15000.0, factor_product==1.0), no fabrication.

## Non-blocking notes (no defects)
(1) content-key tie-break for distinct-content points in the same non-finite bucket not distinguished from input-position tie-break by a dedicated test (value-order + duplicate stability + run-to-run determinism ARE tested). (2) never-Verified capping is case-insensitive in code but tests exercise only lowercase. (3) point-level label not asserted directly (whole-tree "no verified" scan covers it). (4) contract-free established by construction not a negative assertion. None affect a required guarantee.
