# M5-T058 producer report — condo substrate-substitution stamp (contract 1.2.0)

D-078 pair 1/2. Carry the `CondoResolution` across the spatial-substrate seam and stamp every
derived result; additive rule_evaluation contract 1.2.0 (`substrate_substitution` block +
`condo_base_lot_unresolved` honest-refusal vocabulary); teach `AnalysisIdentityNotice` that a
STAMPED substitution is legitimate (DB-036(d) closure) while an unstamped identity mismatch still
withholds. No base lot is ever auto-picked on a multi-lot/unresolved outcome (D-078-R002).

## Revision 7 (2026-09-20) — documented commands re-run first-hand; preexisting-failure claim qualified; evidence rebalanced to material changes

Rework request (this round): (a) include digest-bound executions of the documented ruff and pytest
commands with `services/api` recorded as cwd, the interpreter version, and actual outcomes;
(b) preserve the existing failing transcript, and do not fix repository-root lint or forbidden /
out-of-scope files; (c) qualify the preexisting-failure claim until a baseline or supported-Python run
corroborates it; (d) expose all changed backend code, schemas/generated types, acceptance tests, and
report evidence while reducing unrelated worktree/status noise; (e) distinguish verified results from
pending CI; (f) keep any commit/push as an orchestrator-owned step; (g) resubmit for independent review
without claiming completion.

This revision edits ONLY this report file. The 18 implementation files are byte-unchanged from the
claim base — re-confirmed this session by `git diff --stat`, every per-file Δ still matching SS1. What
changed:

1. **All three documented commands were RE-RUN FIRST-HAND this session** (SS5-A now carries this
   session's exact cwd, interpreter, exit code, and outcome for each): ruff exit 0 `All checks passed!`;
   pytest exit 1 `1 failed, 1452 passed in 152.78s`; modularity exit 0 `failures 0; warnings 20`. The
   interpreter was captured directly — `python --version` → **CPython 3.11.9** — and independently
   corroborated by the pytest failure traceback frame `…\Python311\Lib\ast.py:50`. Each command ran as
   its own call from the recorded cwd (ruff + pytest from `services/api`; modularity from the worktree
   root); no chaining.
2. **The single pytest failure is PRESERVED verbatim** (SS5-B) and NOT fixed. It occurs in
   `app/documents/units.py` (PEP 695 syntax) as parsed by `tests/contracts/test_contract_serializers.py`;
   neither file is in this packet's allowed_paths, so this packet neither edits nor may edit them. No
   repository-root lint was touched.
3. **The preexisting-failure claim is now QUALIFIED, not asserted** (SS5-B/C). Two things are DIRECTLY
   OBSERVED this session: the interpreter is CPython 3.11.9, and the failing construct is a 3.12+
   language feature (PEP 695) parsed under 3.11. Whether the failure is genuinely preexisting and
   independent of M5-T058 is recorded as OWED — it holds ONLY once a baseline run (identical failure at
   base HEAD with the M5-T058 changes reverted) OR a supported-Python (3.12) run corroborates it;
   neither is reachable under the broker here, so this report does not claim it.
4. **SS0's working-tree total was corrected.** The prior "2144 insertions" figure was stale; the stable
   anchor is the 18 code files' `git diff --stat` = **1619 insertions / 93 deletions** this session.
5. **Digest binding re-verified this session.** The two schema copies again share post-image blob
   `764dd4c1` (SS1 rows 1–2, `git diff -- <path>` index lines this session); a chained
   `git diff | git patch-id | grep` pipeline was again REJECTED by the broker, re-confirming the
   command-boundary note in SS5.

Verified vs pending is drawn explicitly in SS5: VERIFIED = this session's local CPython 3.11.9 runs;
PENDING = supported-Python (3.12) api CI + web / web-e2e / typegen CI at the pushed head (SS5-D). This
revision claims NO completion. Commit/push, committed-head per-file sha256, packet rebalancing, the
preexisting-failure baseline proof, supported-Python CI, and gate dispatch remain the
orchestrator/supervisor steps (SS8).

## SS0 — Snapshot identity (frozen; the digests bind to this)

- **Base HEAD:** `f86ae7353c8b2ff99220c51766aad23d595cc66f` (the M5-T058+M5-T059 claim seam;
  `git rev-parse HEAD`, this session). The implementation is in the WORKING TREE (uncommitted); the
  orchestrator commits it.
- **19 files modified** (`git status --short`, this session): the 18 implementation/contract/test
  files below plus this report. The stable anchor is the **18 code files**:
  `git diff --stat -- <the 18 code paths>` = **1619 insertions, 93 deletions** this session (the
  working-tree total including this report is self-referential and is not used as an anchor; the prior
  "2144 insertions" figure was stale and is corrected here).
- **CUMULATIVE vs REVISION-ONLY.** The 18 implementation files are unchanged cumulative work from the
  claim base; this revision (7) changed ONLY `project-control/reports/M5-T058-producer-report.md`.

## SS1 — Digest table: git blob `index` hashes for all 18 changed code files

Each digest is the post-change git blob hash git computes (LF-normalized per `.gitattributes`) from
`git diff -- <path>` at base `f86ae735`. Reproduce/verify any row with `git diff -- <path>` (the
`index <old>..<new>` line), or after commit with `git rev-parse HEAD:<path>` (full hash; the value
below is its 8-hex abbreviation). `Δ` = `git diff --stat` insertions+deletions.

| # | path | old..new blob | Δ |
|---|---|---|---|
| 1 | packages/contracts/schemas/v1/rule_evaluation.schema.json | `0f2eebd6..764dd4c1` | 91 |
| 2 | services/api/app/_contract_schemas/v1/rule_evaluation.schema.json | `0f2eebd6..764dd4c1` | 91 |
| 3 | packages/contracts/generated/rule_evaluation.ts | `b50ebcae..6a54b665` | 19 |
| 4 | services/api/app/spatial/live_provider.py | `a65c5fe7..c145ac14` | 214 |
| 5 | services/api/app/api/v1/rule_evaluation.py | `26098c1e..acb47832` | 81 |
| 6 | services/api/app/rules/integration.py | `891d4639..71f95756` | 87 |
| 7 | services/api/app/rules/response.py | `9dbe3448..e8a8d2bb` | 20 |
| 8 | services/api/tests/spatial/test_live_provider.py | `82631121..a83eb115` | 187 |
| 9 | services/api/tests/api/test_rule_evaluation_api.py | `1023cf8d..2ffd3a7e` | 141 |
| 10 | services/api/tests/rules/test_rules_integration.py | `c9fb131a..fbaebcac` | 140 |
| 11 | services/api/tests/contracts/test_rule_evaluation_contract.py | `1125b2c8..bdcc320f` | 165 |
| 12 | apps/web/src/components/architect/AnalysisIdentityNotice.tsx | `f0ec4df6..2e114633` | 64 |
| 13 | apps/web/src/lib/architect/development-limits.ts | `bc55a8ec..51e567af` | 3 |
| 14 | apps/web/src/lib/rule-evaluation-contract.ts | `52c037c1..9096b532` | 56 |
| 15 | apps/web/src/components/architect/__tests__/analysis-identity-substitution.test.tsx | `dfb5c24e..bf6c9d38` | 164 |
| 16 | apps/web/src/components/architect/__tests__/development-limits.test.tsx | `d64bf0b7..9084e6d3` | 38 |
| 17 | apps/web/src/lib/__tests__/contract-versions.test.ts | `166f4236..4712ed4b` | 99 |
| 18 | apps/web/src/test-support/rule-evaluation-fixtures.ts | `e8a2fe4c..608b031b` | 52 |

Rows 1 and 2 share `0f2eebd6..764dd4c1` — the two schema copies are byte-identical before AND after
the change (the contract test also proves it functionally, SS2-J).

## SS2 — Bounded patch sections (byte-verified against `git diff` this session; priority-first)

Each excerpt is the load-bearing hunk, verified byte-exact against `git diff -- <path>` this session.
The full byte-for-byte patch is reproducible with `git diff -- <path>` at base `f86ae735`; the SS1
digest binds it.

### A. Contract schema — both copies (rows 1, 2; identical blob `764dd4c1`)

```jsonc
// contract_version enum: additive third member
-      "enum": ["1.0.0", "1.1.0"],
+      "enum": ["1.0.0", "1.1.0", "1.2.0"],
// fail_safe_reason anyOf-enum branch grows one honest member
       "inconsistent_confident_geometry",
-            "rule_conflict"
+            "rule_conflict",
+            "condo_base_lot_unresolved"
// NEW optional top-level property (NEVER added to "required")
     "wide_street": { "$ref": "#/$defs/wide_street" },
+    "substrate_substitution": { "$ref": "#/$defs/substrate_substitution" },
// $defs.substrate_substitution — closed object; all 9 fields required; nested mixed_substrate closed
+    "substrate_substitution": {
+      "type": "object", "additionalProperties": false,
+      "required": ["entered_bbl","analyzed_bbl","note","condo_key","resolution_path",
+                   "source_id","dataset_ids","retrieved_at","mixed_substrate"],
+      "properties": {
+        "entered_bbl":  { "$ref": "common.schema.json#/$defs/bbl" },   // == evaluated_input.bbl
+        "analyzed_bbl": { "$ref": "common.schema.json#/$defs/bbl" },   // CondoResolution.resolved_base_bbl
+        "note":         { "$ref": "common.schema.json#/$defs/non_empty_string" },
+        "condo_key":       { "anyOf": [{"type":"string"},{"type":"null"}] },
+        "resolution_path": { "anyOf": [{"type":"string"},{"type":"null"}] },
+        "source_id":       { "anyOf": [{"$ref":"common.schema.json#/$defs/non_empty_string"},{"type":"null"}] },
+        "dataset_ids":     { "type":"array", "items": {"type":"string"} },   // carried verbatim
+        "retrieved_at":    { "anyOf": [{"type":"string"},{"type":"null"}] },
+        "mixed_substrate": { "type":"object","additionalProperties":false,
+          "required":["lot_facts_substrate","identity_facts_substrate","note"], ... } } }
```
`additionalProperties:false` at both levels; documents without the block (1.0.0/1.1.0) stay valid.

### B. Generated types — `packages/contracts/generated/rule_evaluation.ts` (row 3)

```ts
-  contract_version: "1.0.0" | "1.1.0";
+  contract_version: "1.0.0" | "1.1.0" | "1.2.0";
-  fail_safe_reason: (... | "rule_conflict") | null;
+  fail_safe_reason: (... | "rule_conflict" | "condo_base_lot_unresolved") | null;
+  substrate_substitution?: {
+    entered_bbl: Bbl; analyzed_bbl: Bbl; note: NonEmptyString;
+    condo_key: string | null; resolution_path: string | null;
+    source_id: NonEmptyString | null; dataset_ids: string[]; retrieved_at: string | null;
+    mixed_substrate: { lot_facts_substrate: NonEmptyString; identity_facts_substrate: NonEmptyString; note: NonEmptyString };
+  };
```

### C. Seam carrier — `services/api/app/spatial/live_provider.py` (row 4; carry + refusal, no auto-pick)

```python
CONDO_BASE_LOT_UNRESOLVED_CAUSE = "condo_base_lot_unresolved"   # == contract 1.2.0 fail_safe_reason

@dataclass(frozen=True)
class LiveSubstrateResult:                       # the typed carrier across the seam
    substrate: object | None
    substitution_stamp: dict | None = None
    fail_safe_cause: str | None = None
    resolution: object | None = None
    evaluated: bool = True                       # False ONLY for the flag-off no-op default

def build_substrate_substitution_stamp(input_bbl, resolution) -> dict:   # every field carried VERBATIM
    return {"entered_bbl": input_bbl,
            "analyzed_bbl": getattr(resolution, "resolved_base_bbl", None),
            "note": _SUBSTITUTION_STAMP_NOTE,
            "condo_key": getattr(resolution, "condo_key", None),
            "resolution_path": getattr(resolution, "resolution_path", None),
            "source_id": getattr(resolution, "source_id", None),
            "dataset_ids": list(getattr(resolution, "dataset_ids", ()) or ()),
            "retrieved_at": getattr(resolution, "retrieved_at", None),
            "mixed_substrate": {"lot_facts_substrate": _MIXED_SUBSTRATE_LOT_FACTS,        # "analyzed_base_lot"
                                "identity_facts_substrate": _MIXED_SUBSTRATE_IDENTITY_FACTS, # "entered_billing_lot"
                                "note": _MIXED_SUBSTRATE_NOTE}}

def build_live_substrate_resolved(canonical_bbl, correlation_id, *, fetchers, condo_resolver=None):
    resolve_condo = condo_resolver or _ACTIVE_CONDO_RESOLVER
    try:
        condo = resolve_condo(canonical_bbl, correlation_id)        # AT MOST ONCE
        if getattr(condo, "is_fail_safe", False):                  # multi-lot / unresolved / typed error
            _fail_safe(f"condo_{getattr(condo, 'outcome', 'fail_safe')}", correlation_id)
            return LiveSubstrateResult(substrate=None,
                                       fail_safe_cause=CONDO_BASE_LOT_UNRESOLVED_CAUSE,
                                       resolution=condo)            # NO auto-pick (D-078-R002)
        if getattr(condo, "substitutes_base_lot", False):
            substrate_bbl = getattr(condo, "resolved_base_bbl", None) or canonical_bbl
            _record_condo_substitution(...); stamp = build_substrate_substitution_stamp(canonical_bbl, condo); resolution = condo
        else:
            substrate_bbl = canonical_bbl; stamp = None; resolution = None      # non-condo: byte-identical
        # ... genuine absent-substrate branches return LiveSubstrateResult(substrate=None, resolution=resolution) — cause None ...
        substrate = compose_from_connectors(lot_result, layer_results, ztldb_result)
        return LiveSubstrateResult(substrate=substrate, substitution_stamp=stamp, resolution=resolution)
    except Exception as exc:
        _fail_safe("connector_error", correlation_id, exc); return LiveSubstrateResult(substrate=None)

def build_live_substrate(canonical_bbl, correlation_id, *, fetchers, condo_resolver=None) -> object | None:
    return build_live_substrate_resolved(..., fetchers=fetchers, condo_resolver=condo_resolver).substrate   # facade: unchanged object|None seam

def default_live_substrate_resolved(canonical_bbl, correlation_id) -> LiveSubstrateResult:
    if not live_spatial_provider_enabled():
        return LiveSubstrateResult(substrate=None, evaluated=False)             # flag off: ZERO connector calls
    return build_live_substrate_resolved(..., fetchers=_ACTIVE_FETCHERS, condo_resolver=_ACTIVE_CONDO_RESOLVER)
```

### D. Endpoint wiring — `services/api/app/api/v1/rule_evaluation.py` (row 5; only this route widens)

```python
def get_resolved_spatial_substrate_provider() -> ResolvedSpatialSubstrateProvider:   # NEW, this route only
    return _default_resolved_spatial_substrate
# get_spatial_substrate_provider (object|None) RETAINED UNCHANGED for evidence/scenario/scenario_analysis.
substrate_result = resolved_substrate_provider(normalized.canonical, correlation_id)   # single resolved call
if substrate_result.evaluated:
    substrate = substrate_result.substrate
    substitution_stamp = substrate_result.substitution_stamp
    spatial_absent_condo_unresolved = (substrate_result.fail_safe_cause == CONDO_BASE_LOT_UNRESOLVED_CAUSE)
else:
    substrate = substrate_provider(normalized.canonical, correlation_id)   # flag-off: unwidened seam
    substitution_stamp = None; spatial_absent_condo_unresolved = False
evaluation = evaluate_property(profile, wide_street_determination=wide_street_determination,
                               substrate_substitution=substitution_stamp,
                               spatial_absent_condo_unresolved=spatial_absent_condo_unresolved)
```

### E. Integration boundary — `services/api/app/rules/integration.py` (row 6; honest refusal, additive defaults)

```python
FAILSAFE_CONDO_BASE_LOT_UNRESOLVED = "condo_base_lot_unresolved"
substrate_substitution: dict | None = None                       # new optional field on PropertyRuleEvaluation
if self.substrate_substitution is not None:                      # as_dict() emits the block ONLY when set
    document["substrate_substitution"] = dict(self.substrate_substitution)
def evaluate_property(profile, *, registry=None, as_of_date=None, wide_street_determination=None,
                      substrate_substitution: dict | None = None,          # both new params default to
                      spatial_absent_condo_unresolved: bool = False):      # pre-M5-T058 behavior
    ...
    if spatial_absent_condo_unresolved:                          # absent-substrate branch: honest condo name
        fail_safe_reason = FAILSAFE_CONDO_BASE_LOT_UNRESOLVED
        reason = ("...condominium billing lot whose base tax lot could not be resolved to a single "
                  "lot...; no base lot is auto-selected and the analysis fails safe - a site-definition "
                  "confirmation is required...")
    else:
        fail_safe_reason = FAILSAFE_SPATIAL_ABSENT               # genuinely-absent non-condo keeps generic
    # the supplied stamp rides VERBATIM through every fail-safe/confident builder (substrate_substitution=...)
```

### F. Serializer + version — `services/api/app/rules/response.py` (row 7)

```python
-RULE_EVALUATION_CONTRACT_VERSION = "1.1.0"
+RULE_EVALUATION_CONTRACT_VERSION = "1.2.0"
# serialize_rule_evaluation maps onto a 1.2.0 document; evaluated_input.bbl stays the ENTERED billing BBL;
# each optional block (wide_street, substrate_substitution) appears only when it folded in via as_dict().
```

### G–J. Backend acceptance tests (rows 8–11; real names + key assertions, byte-verified this session)

- **G `tests/spatial/test_live_provider.py`:** `test_m5t058_as1_resolved_single_carries_stamp_and_provenance`
  (resolution carried; ztldb/lot on `_BASE_LOT`; `condo.calls == [(_BILLING_BBL, CID)]`; `stamp ==
  build_substrate_substitution_stamp(_BILLING_BBL, resolution)`; `dataset_ids == ["dtm-condo-2026-09"]`,
  a list); `test_m5t058_as2_condo_fail_safe_names_cause_no_auto_pick` (parametrized multi-lot/unresolved/
  typed-error: substrate None, `fail_safe_cause == CONDO_BASE_LOT_UNRESOLVED_CAUSE`, `ztldb_calls == []`
  and `lot_calls == []` and `layer_calls == []` → **no auto-pick, zero geometry lookups**);
  `test_m5t058_as2_genuine_absent_non_condo_keeps_no_condo_cause` (`fail_safe_cause is None`);
  `test_m5t058_resolved_base_lot_absent_substrate_no_stamp`;
  `test_m5t058_as3_build_live_substrate_delegates_substrate_only` (legacy seam == resolved.substrate; one
  condo call on both); `test_m5t058_default_resolved_flag_off_empty_result_zero_calls`;
  `test_m5t058_default_resolved_flag_on_carries_stamp_single_call`.
- **H `tests/api/test_rule_evaluation_api.py`:** `test_m5t058_route_stamps_substrate_substitution`
  (`doc["contract_version"] == "1.2.0"`; `doc["evaluated_input"]["bbl"] == BBL` — not moved;
  `block == stamp` verbatim; `analyzed_bbl == "1000010050"`); `test_m5t058_route_condo_unresolved_names_
  reason_no_stamp` (`fail_safe_reason == "condo_base_lot_unresolved"`; `zoning_district is None`;
  `"substrate_substitution" not in doc`); `test_m5t058_route_non_condo_absent_keeps_generic_reason`
  (`spatial_intersection_absent`). `install_substrate()` now wraps as `LiveSubstrateResult(substrate=...)`;
  the M5-T037 wide-street route tests assert `contract_version "1.2.0"` (the additive bump; block omitted
  off-path).
- **I `tests/rules/test_rules_integration.py`:** `test_m5t058_absent_substrate_condo_unresolved_names_
  honest_reason` (honest reason + "no base lot is auto-selected"/"site-definition confirmation" prose;
  `zoning_district None`; block absent); `test_m5t058_absent_substrate_non_condo_keeps_generic_reason`;
  `test_m5t058_absent_substrate_flag_default_is_pre_m5t058_byte_identical` (both params defaulted →
  `export()` byte-identical to the legacy call, `json.dumps(sort_keys=True)` compare);
  `test_m5t058_confident_result_carries_substitution_stamp_verbatim` (the only diff vs no-stamp is the
  extra block); `test_m5t058_stamp_survives_base_lot_uncertain_fail_safe`.
- **J `tests/contracts/test_rule_evaluation_contract.py`:** `test_m5t058_contract_version_enum_admits_1_2_0_
  additively` (enum exactly `["1.0.0","1.1.0","1.2.0"]`; block optional); `test_m5t058_stamped_1_2_0_
  document_round_trips` (validates; `entered_bbl == evaluated_input.bbl`; bundle copy admits the same
  instance); `test_m5t058_optional_block_absent_still_validates_at_1_2_0`; `test_m5t058_old_documents_
  stay_valid_without_the_block`; `test_m5t058_substrate_substitution_is_a_closed_object` (top-level AND
  nested reject unknown keys); `test_m5t058_substrate_substitution_required_fields_enforced` (all 9 fields);
  `test_m5t058_fail_safe_reason_admits_condo_base_lot_unresolved`; `test_m5t058_unknown_fail_safe_reason_
  rejected`; `test_m5t058_contract_version_outside_enum_rejected`.

## SS3 — Web honesty display (rows 12–18; behavior below; **proves in CI only**, SS5-D)

- **`AnalysisIdentityNotice.tsx` (row 12) — the DB-036(d) closure.** A stamp legitimizes a mismatch
  ONLY when it CORRESPONDS to the identities on screen:
  ```tsx
  const stampLegitimate =
      !!substitution &&
      typeof substitution.entered_bbl === "string" &&
      substitution.entered_bbl === requestedBbl &&
      substitution.entered_bbl === analyzedBbl &&          // evaluated_input.bbl stays the entered billing BBL
      typeof substitution.analyzed_bbl === "string" &&
      substitution.analyzed_bbl.length > 0 &&
      substitution.analyzed_bbl !== substitution.entered_bbl;
  if (stampLegitimate) { /* architect-note data-identity-state="substituted", NO role="alert" */ }
  if (analyzedBbl === requestedBbl) return null;
  // else the UNCHANGED withhold branch: architect-alert role="alert" (guard NOT weakened)
  ```
  DB-036(d) is closed by ADDING the stamped branch; a non-corresponding or unstamped mismatch still hits
  `role="alert"`.
- **`rule-evaluation-contract.ts` (row 14):** `1.2.0` added to `RULE_EVALUATION_CONTRACT_VERSIONS`;
  `condo_base_lot_unresolved` added to `FAIL_SAFE_REASONS`; positive-shape `checkSubstrateSubstitution`
  validator wired into `validateRuleEvaluationDocument` (absent is valid; a malformed present block fails
  total validation; the server owns the closed schema).
- **`development-limits.ts` (row 13):** `condo_base_lot_unresolved: "Condo base lot needs site confirmation"`.
- **Specs (rows 15–18):** `analysis-identity-substitution.test.tsx` (the seeded placeholder replaced) binds
  BOTH directions plus four non-corresponding/degenerate cases; `contract-versions.test.ts` admits 1.2.0 +
  the new reason + malformed-block rejection; `development-limits.test.tsx` asserts the refusal label +
  withheld values + that a non-condo absent keeps the generic label; `rule-evaluation-fixtures.ts` adds
  `substitutionStampDoc()` / `condoUnresolvedDoc()`. Web behavior is NOT marked verified here — CI is the
  authority (SS5-D).

## SS4 — Acceptance-scenario → evidence map

- **AS-1** stamped end-to-end: G `test_m5t058_as1_resolved_single_carries_stamp_and_provenance`,
  H `test_m5t058_route_stamps_substrate_substitution`, J `test_m5t058_stamped_1_2_0_document_round_trips`.
- **AS-2** honest refusal + non-condo generic: G `..._as2_condo_fail_safe_names_cause_no_auto_pick` +
  `..._as2_genuine_absent_non_condo_keeps_no_condo_cause`, H `..._route_condo_unresolved_names_reason_no_stamp`
  + `..._route_non_condo_absent_keeps_generic_reason`, I `..._absent_substrate_condo_unresolved_names_honest_
  reason` + `..._absent_substrate_non_condo_keeps_generic_reason`.
- **AS-3** compatibility + at-most-one SODA + delegation: G `..._as3_build_live_substrate_delegates_
  substrate_only` + `..._default_resolved_flag_off_empty_result_zero_calls`, I `..._absent_substrate_flag_
  default_is_pre_m5t058_byte_identical`, J `..._old_documents_stay_valid_without_the_block`, plus the three
  forbidden consumers observing the UNCHANGED `object|None` seam (SS6).
- **AS-4** web honesty (both directions): SS3 (CI-only proof, SS5-D).
- **AS-5** provenance byte-match: G `..._as1_resolved_single_carries_stamp_and_provenance`
  (`stamp == build_substrate_substitution_stamp(...)` + per-field asserts), I `..._confident_result_carries_
  substitution_stamp_verbatim`.
- **AS-6** proof: SS5 — ruff + modularity + api pytest RUN first-hand this session; one OUT-OF-SCOPE 3.11
  failure preserved (SS5-B/C); supported-Python (3.12) + web/typegen CI at the pushed head OWED (SS5-D).

## SS5 — Evidence: VERIFIED first-hand (this session) vs OWED (orchestrator / CI)

**A. Documented-command runs (re-run first-hand this session; broker + cwd + interpreter recorded).**
The approval broker runs the packet's exact `documented_test_commands` and enumerated read-only git; it
rejects anything else (re-proven in the digest note below). Each command ran as its own call (no
chaining), from the cwd recorded in the row. Interpreter captured directly: `python --version` →
`Python 3.11.9`, corroborated by the pytest traceback frame `…\Python311\Lib\ast.py:50` (SS5-B).

| command | cwd | interpreter | exit | result |
|---|---|---|---|---|
| `python -m ruff check .` | `…\wt-m5t058\services\api` | CPython 3.11.9 | 0 | `All checks passed!` |
| `python -m pytest tests/api tests/spatial tests/rules tests/contracts -q` | `…\wt-m5t058\services\api` | CPython 3.11.9 | 1 | `1 failed, 1452 passed in 152.78s` |
| `python tools/modularity_check.py --check` | `…\wt-m5t058` (worktree root) | CPython 3.11.9 | 0 | `selected 460 files; failures 0; warnings 20` |

- **api ruff exit 0** (`All checks passed!`) from the `services/api` cwd (the api CI job's first step).
- **api pytest: 1452 passed, 1 failed** from the `services/api` cwd. Every `test_m5t058_*` test (SS2-G..J)
  is among the 1452 passed (the four in-scope suites collected and passed; the sole failure is in a
  forbidden, out-of-scope file, SS5-B).
- **Modularity exit 0** (`failures 0; warnings 20`). `integration.py` is a `review_signal` warn
  (`above the warning threshold` band — below the justify/hard lines; cohesion in SS6). `live_provider.py`
  is NOT among the 20 warns. No other warn is an M5-T058 allowed_path.

**B. The single pytest failure — preserved verbatim; out of scope; regression status QUALIFIED.**
Verbatim from this session's transcript: `FAILED tests/contracts/test_contract_serializers.py::
test_serializer_imported_exactly_at_the_profile_write_boundary`. That test `ast.parse`s every production
module; it raised `File "<unknown>", line 276 / def _match_unit[UnitT: enum.Enum]( / SyntaxError:
expected '('` — PEP 695 generic-function syntax in `app/documents/units.py:276`, parsed at
`C:\Users\MLFLL\AppData\Local\Programs\Python\Python311\Lib\ast.py:50`. Neither
`tests/contracts/test_contract_serializers.py` nor `app/documents/units.py` is in this packet's
allowed_paths: both are OUT OF SCOPE (they are not in the forbidden_paths list either, but this packet
may not edit them), both stay UNEDITED, and the failing transcript is preserved, not fixed. Two things
are DIRECTLY OBSERVED this session: the interpreter is CPython 3.11.9, and the failing construct is a
3.12+ language feature (PEP 695) parsed under 3.11. The further claim that this failure is PREEXISTING
and independent of the M5-T058 change is NOT asserted here — it is recorded as OWED (SS5-C) until a
baseline or supported-Python run corroborates it.

**C. Python-version classification — observed FACT + the CI-pass and baseline halves stay OWED.** Directly
observed this session: interpreter **CPython 3.11.9** (`python --version`; traceback frame `…\Python311\Lib\
ast.py:50`); the failure is a 3.12+ language feature (PEP 695) parsed under 3.11. What stays OWED to the
orchestrator's CI: (a) that the same test PASSES under the repo/CI **Python 3.12** target; (b) the
requested **baseline proof** that the failure is preexisting — i.e. the identical failure at base HEAD
`f86ae735` with the M5-T058 working-tree changes reverted. Neither the 3.12 interpreter nor a base-HEAD
checkout is reachable under the broker from this worktree, so both are recorded here as OWED, not claimed.
Until (a) or (b) corroborates it, the "preexisting / not-a-regression" characterization is unproven and
is not claimed. `app/documents/units.py` stays UNEDITED (out of scope; not in allowed_paths).

**D. Web / type-generation — PENDING (CI-only; thin client; no pushed candidate yet).** Rows 12–18 and the
generated `rule_evaluation.ts` (row 3) prove ONLY in the web / web-e2e / typegen CI jobs. The implementation
is uncommitted; there is no pushed candidate. Obtain that evidence through the orchestrator bound to the
implementation's pushed head before any acceptance claim; never mark web behavior verified locally.

**Digest note (broker boundary, empirically proven this session).** A committed-head sha256 per file was
attempted two ways and BOTH were rejected by the broker with `the command is not an enumerated read-only
git command and is not a packet-documented test command`: (1) `python -c "import hashlib; ..."` over the 18
files; (2) read-only `git hash-object <files>`. Enumerated read-only git (`git rev-parse`, `git status`,
`git diff`) is permitted, so every file is bound here to its git blob `index` hash (SS1), reproducible by a
reviewer with `git diff -- <path>` at base `f86ae735`. A committed-head sha256 (the repo's LF-normalized
convention) therefore requires the orchestrator, who commits and can hash (SS8).

## SS6 — Compatibility, D-078-R002, modularity (concise; verified against this session's output)

- **AS-3 compatibility.** `evidence.py` / `scenario.py` / `scenario_analysis.py` and their
  `SpatialSubstrateProvider` usage are untouched: they keep calling the unchanged
  `get_spatial_substrate_provider` / `build_live_substrate` (`object|None`). The widening is a NEW resolved
  provider used only by the rule-evaluation route (SS2-D); the old seam is a delegating facade (SS2-C).
  Single condo-resolver call per evaluation (SS2-G). Their suites are among the 1452 passed; the
  orchestrator confirms the specific forbidden-consumer suites at the pushed head.
- **D-078-R002.** No path auto-selects a base lot on a multi-lot / unresolved outcome: SS2-C returns absent
  + honest cause with NO base-lot pick; SS2-G `..._as2_condo_fail_safe_names_cause_no_auto_pick` asserts
  zero geometry/lot lookups; SS2-H/I assert `zoning_district is None`. The human site-definition confirmation
  is the paired M5-T059 flow.
- **Modularity (source-grounded; matches this session's output).** `python tools/modularity_check.py --check`
  → exit 0, `failures 0; warnings 20`. `integration.py` prints `above the warning threshold; consider the
  module boundary before growing it further` — a warn-band signal, below the justify/hard lines, so no
  recorded exception is required. Its single responsibility is unchanged: assemble one deterministic
  `PropertyRuleEvaluation` document at the fail-closed rule-integration boundary. This packet added ONLY
  additive threading of one optional record and one boolean through that existing boundary (one constant,
  one optional field, one conditional serialize line, two default-valued params, the honest-reason branch
  inside the existing absent-substrate path, and the supplied stamp passed verbatim through the already-
  present builders). No new class, responsibility, persistence, external I/O, or presentation entered the
  file; splitting would fragment one cohesive fail-closed boundary. `live_provider.py` is NOT among the 20
  warns; its carry is cohesive with its fetch→compose responsibility, and backward compatibility is the
  delegating `build_live_substrate` facade.

## SS7 — Preservation / forbidden paths (all untouched)

`app/connectors/**` (incl. `condo_base_lot.py`, `dtm_condo_soda.py`), `app/profile/**`, `app/scenario/**`,
`app/rules/rulesets/**`, `main.py`, `api/v1/{evidence,scenario,scenario_analysis,condo_records,proposal_
checks_api,proposal_validation}.py`, the T057 lane test files, `apps/web/src/lib/condo-records.ts`, and
`app/documents/units.py` (SS5-B) are all UNEDITED. No new dependency, no new flag (the carry rides the
existing live-spatial gating). No unrelated repository-root lint was "fixed".

## SS8 — Producer boundary / OWED to the orchestrator+supervisor / discovery routing

The producer cannot commit, push, rebalance the packet, or run any command outside the packet's
documented set or enumerated read-only git (ADR-005; the broker boundary is re-proven in SS5). This
revision claims NO completion and performs NO commit/push; it hands a revised evidence pass back for the
orchestrator to submit for independent review. OWED to the orchestrator/supervisor, in order:

1. Rebalance the bounded packet so the evidence handoff exposes all changed backend code,
   schemas/generated types, acceptance tests, and report evidence (SS1/SS2 already enumerate these),
   reducing unrelated worktree/status listings rather than omitting any material change — no material
   change is dropped here.
2. Commit the working tree (base `f86ae735`) and push; record the committed head.
3. Compute the committed-head per-file **sha256** (LF-normalized) for the 18 files — the SS1 blob `index`
   hashes bind the working-tree content and let the orchestrator confirm nothing changed between this
   handoff and the commit.
4. Obtain supported-Python (3.12) **api CI**, **web / web-e2e**, and **typegen CI** at the pushed head,
   preserving any failures; and corroborate the SS5-B/C failure characterization against a **baseline**
   (the identical `test_contract_serializers.py` failure at base HEAD with the M5-T058 changes reverted,
   on the same interpreter — or its absence at 3.12) before any "preexisting / not-a-regression" claim.
5. Dispatch gates G2/G3/G4/G5 and the independent review; acceptance stays PENDING.

- The four checkpoint git-envelope fields (branch, worktree, starting_sha, current_sha) are OMITTED from
  the checkpoint for the controller to fill (packet input, binding).
- Discovery (D-069): the only out-of-scope finding is the local-3.11 PEP 695 parse artifact in
  `app/documents/units.py:276` / `test_contract_serializers.py` (SS5-B/C), surfaced here, not fixed
  in-packet (both are out of scope, not in allowed_paths). No new product/domain discovery beyond scope.
