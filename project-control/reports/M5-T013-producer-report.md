# M5-T013 Producer Report — Evidence / provenance endpoint (re-checkpoint)

**Task:** M5-T013 — Evidence / provenance endpoint (`GET /api/v1/properties/{bbl}/evidence`),
verbatim + honest, over the internal flag-gated API.
**Branch:** `task/M5-T013-evidence-endpoint`  **Producer:** backend-engineer (persistent-local-29)
**Directive:** D-038 (ALL) — positive product deliverable (Compare UI → **Evidence view**).

Producers do not self-accept. This report is evidence for the independent G0/G1/G3/G4/G5 gate wave.

**Revision (gate-wave rework, 2026-09-10).** The G1/G3/G5/DCV wave ruled the transport itself
sound — the DCV classified all 1,339 leaves (1,332 transported byte-equal, 7 server-authored, none
a legal value) and G5 proved the two-form serialisation check discriminates — but found a serious
**OMISSION**: the assembled document was a silent projection that dropped 18 required
source-contract fields, including the qualifications that make its headline figure honest. That is
fixed (section "What the document carries", and section 9 for the evidence), together with the
typed `rule_conflict` object and the five test-strength corrections. Nothing about the transport
semantics changed; the document simply now carries everything it was always claiming to.

## Why this is a re-checkpoint

The prior checkpoint's bundled evidence **truncated**, so the reviewer could not inspect the full
`evidence.py` handler, the serialisation guards, or the acceptance-test bodies AS-3..AS-8 and the
egress assertions. Per the packet's requested action I took the **"reduce repetitive commentary"**
path (not packet chunking): the over-long module/function docstrings in the two source files were
compacted **without changing one line of code or test logic**, the documented suites were rerun,
and this report is deliberately short — it **references** the source by span + digest and embeds
only the two spans named as must-be-visible, so nothing critical is inlined at a size that truncates.

No behaviour changed. Proof it is comment-only: the AS-2 source scan
(`test_as2_module_does_no_arithmetic_or_reevaluation`: `build_scenario`/`import math` absent,
`evaluate_property(` appears exactly once) and the AS-7 scope-note assertions still pass unchanged
after the trim (see test results below).

## Digest-bound evidence (SHA-256 of the exact working-tree bytes tested)

**LINE-ENDING BASIS — stated explicitly, correcting the previous table (DCV finding).** The
previous revision published two digests computed on *different* bases: `evidence.py`'s matched the
**LF-normalised** (git blob) bytes while `main.py`'s matched the **on-disk CRLF** bytes. Both were
genuine, but a reviewer running the published one-liner (which reads the file as it sits on disk)
saw a spurious mismatch on one row and had no way to tell which basis applied. These files are
CRLF in the working tree, so the two bases differ by exactly one byte per line. Both are now given
for every file, labelled:

| File | on-disk bytes (CRLF) — what the one-liner below reproduces | LF-normalised (git blob) — what `git hash-object` / `git show` reproduces |
|---|---|---|
| `services/api/app/api/v1/evidence.py` | `fa37a6b834e690a405104b678d9866ee2ec2c4702f2da6206085b6f9a5637c15` | `53b115588144836359d792de3c9dd6f2beb589c49e85aa6ae0988317471e49a6` |
| `services/api/app/main.py` (unchanged) | `97be914803e6ea93a4e8c9a603eedf2b59a78b762bf5c40a7c04b2f2e10ce875` | `b6930f0c87a5c7980efd1dd92948f4e9f13597c8a70ba04a756a4e192d7c4809` |
| `services/api/tests/api/test_evidence_api.py` | `45c22b984439c5ed9c3827da3d8e3b50ee1cb14e67a611540923ff8bc3afdc62` | `b1c1a74ddd056d0899c6a6260e7c8fe189d87b95d13cd5b77f96adc35b5cd5c6` |

`main.py`'s on-disk digest is byte-identical to the previously published value, which confirms it
is genuinely unmodified by this rework (`git diff --stat services/api/app/main.py` is empty).

Reviewer reproduces the **on-disk** column with:
`python -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path(r'services/api/app/api/v1/evidence.py').read_bytes()).hexdigest())"`
and the **LF** column with the same snippet plus `.replace(b'\r\n', b'\n')` before hashing.

## Test results (documented suites, rerun after the trim)

| Command | Result |
|---|---|
| `python -m pytest services/api/tests/api` | **371 passed** in 9.80s (0 failed, 0 regression; **59** evidence tests + 312 pre-existing — was 349 with 37 evidence tests) |
| `python -m pytest services/api/tests/scenario` | **388 passed** in 0.99s (0 regression; this rework touches no scenario module) |

The pre-existing count is unchanged at 312 (371 − 59), so nothing outside this task's own test file
changed behaviour.

Environment: Python 3.11.9, pytest 8.4.2 (local sandbox, `rootdir=services/api`, `configfile=pyproject.toml`).
Fully offline through the injected fetcher/substrate seams — no network, Supabase, or Geoclient.

## Where to inspect the critical source (line spans as of this rework)

`services/api/app/api/v1/evidence.py` (digest above):

| Item | Span |
|---|---|
| `STATUS_STATE_MATRIX` (single source of truth) | L123–L135 |
| `_RELOCATED_SOURCE_FIELDS` (the declared relocation map) | L155–L167 |
| `_gap_markers` incl. the new `rule_conflict` branch | L259–L321 |
| `assemble_evidence_document` (whole-trail verbatim transport) | L324–L390 |
| `_assert_json_safe` (fail-closed serialisation guard) | L393–L403 |
| `get_evidence` handler (flag guard → 422 → connector map → guarded rebuild/assembly/serialise) | L406–end |

`services/api/tests/api/test_evidence_api.py`:

| Scenario | Span |
|---|---|
| AS-3 body-less / non-GET 405 / malformed-BBL 422 pre-fetch | L405–L455 |
| AS-4 flag-gated 404 / no OpenAPI / existing flag reused | L458–L501 |
| AS-5 matrix == rule-eval set / thin-trail 200 / every emitted pair | L504–L632 |
| AS-6 fail-closed (rebuild/assembly/serialise raises; both json.dumps forms) | L635–L722 |
| AS-7 never Verified (server-authored scope) | L725–L753 |
| AS-8 additive registration / **egress landmine** / existing routes | L755–L878 (egress at L851) |

### Embedded span 1 — serialisation guard (`_assert_json_safe`, evidence.py L393–L403)

```python
def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send.

    json.dumps(doc, allow_nan=False) rejects NaN/Infinity; the ensure_ascii=False
    + .encode('utf-8') form is EXACTLY what Starlette's JSONResponse.render uses and
    is the one that raises on an unpaired surrogate. The two disagree about unpaired
    surrogates and the renderer uses the second (M5-T012 G5 BLOCKING-1), so running
    BOTH here lets the caller fail closed to a typed 500 instead of an untyped ASGI 500."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
```

### Embedded span 2 — egress landmine core (test AS-8 `test_as8_evidence_request_runs_fully_offline`, L987; landmine setup L996–L1018, assertion L1056)

Every real outbound path is monkeypatched to a landmine that **records the attempt as well as
raising** (blocking socket construction would deadlock the anyio portal, so egress is asserted at
the seam), and the fixture transport is exercised; `egress == []` fails even if a connector
swallows the raise:

```python
monkeypatch.setattr(pluto_soda, "_OPENER", _LandmineOpener())
monkeypatch.setattr(resilience_transport, "DEFAULT_OPENER", _LandmineOpener())
monkeypatch.setattr(http.client.HTTPConnection, "connect", _landmine("http.client.HTTPConnection.connect"))
monkeypatch.setattr(http.client.HTTPSConnection, "connect", _landmine("http.client.HTTPSConnection.connect"))
monkeypatch.setattr(socket, "create_connection", _landmine("socket.create_connection"))
# ... request driven through the fixture transport ...
assert egress == []
```

## What the document carries, field by field (G1 LOW-3 — previously undisclosed)

The previous report described the document as carrying "the provenance trail" without stating which
fields that meant, so the projection was invisible to a reader of the report as well as to the test
pack. Stated plainly, now that it is true:

| Evidence document key | Source | Carriage |
|---|---|---|
| `source_coverage` | the `rule_evaluation` **root** | **every** one of its 20 required fields except the two relocated below — deep copy, wholesale. Includes `coverage_status`, `coverage_source`, `data_completeness`, `needs_review`, `professional_review_required`, `fail_safe`, `fail_safe_reason`, `rule_lifecycle_statuses`, `reasons`, `family_coverage`, **and** `contract_version`, `zoning_district`, `lot_area_sq_ft`, `lot_area_source`, `spatial_context`, `spatial_uncertainty`, `rule_conflict` |
| `rule_citations[i]` | each `evaluation_trace` | **every** one of its 19 required fields — deep copy, wholesale — plus exactly one server-authored key, `claim_verification_status`. Includes `outputs` and `citations` **and** `evaluated_inputs`, `applicability_outcome`, `applicability_trace`, `computation_steps`, `data_completeness`, `uncertainty`, `exceptions_applied`, `notes`, `input_validation`, `rule_release`, `effective_window`, `determination` |
| `evaluated_input` | `rule_evaluation.evaluated_input` | the whole sub-document (all 4 required fields) — deep copy |
| `profile_provenance` | `profile.provenance` | every record, deep copy |
| `source_field_routing` | — | server-authored: the declared relocation map, `{"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}` |
| `contract_version`, `document_kind`, `bbl` | — | server-authored document identity |
| `overall_verification_status`, `rule_citations[i].claim_verification_status` | derived ONLY by echoing the source `coverage_status` | server-authored; `_verification_status` is the only place a claim can be labelled verified, and it can only echo |
| `verification_scope_note` | — | server-authored fixed text stating the scope of the verification claim |
| `evidence_completeness`, `gaps` | classified from already-present machine fields | server-authored typed markers; no new legal fact |

**Nothing is excluded.** The only two source root fields that appear under a different key are
`evaluations` and `evaluated_input`, and that relocation is **declared in the response** via
`source_field_routing` rather than left implicit — which is also what the test pack asserts through,
so key-set equality against the source contract is total. Per the packet's rule, if a field ever
genuinely must be excluded it belongs in that map with a documented reason appearing in the
response; silent omission is what this rework removed.

**Why `ensure_ascii=False` in `_assert_json_safe` is not redundant (G5 note).** Unpaired surrogates
arriving from the SODA seam are already stopped *earlier*: `pluto_soda._value_digest` canonicalises
every parsed fact with `json.dumps(..., ensure_ascii=False).encode("utf-8")` and therefore raises on
one before a fact can reach a profile. The two-form check here is defence-in-depth for content that
does **not** come through that path — a future seam, an overridden/injected fetcher, or
server-authored text — and it is the check that makes the renderer/validator disagreement
impossible rather than merely unlikely. Worth a line so a future reader does not read it as
duplicated work and delete it; G5 confirmed that dropping the `ensure_ascii=False` half makes the
unpaired-surrogate test fail, i.e. the suite catches exactly the M5-T012 mistake.

## Acceptance-scenario coverage map (unchanged from prior submission)

- **AS-1** `test_as1_evidence_document_carries_the_whole_trail_verbatim` — 200 versioned doc with
  (a)-(d); source id / retrieval timestamp / citation string byte-equal to a freshly rebuilt
  (WITH-substrate) baseline; `test_as8_direct_assembly_is_pure_transport` proves full-record
  byte-equality within one build.
- **AS-2** `test_as2_cap_and_citations_are_byte_identical_to_the_trace`,
  `test_as2_module_does_no_arithmetic_or_reevaluation`.
- **AS-3** `test_as3_request_body_cannot_influence_the_response`,
  `test_as3_no_non_get_method_is_served` (405), `test_as3_malformed_bbl_is_typed_422_no_connector_call`.
- **AS-4** `test_as4_flag_off_or_unknown_is_generic_404`,
  `test_as4_reuses_the_existing_rule_eval_flag_not_a_new_one`,
  `test_as4_openapi_never_lists_the_route_and_is_byte_identical_off_and_on`.
- **AS-5** `test_as5_matrix_equals_the_rule_evaluation_route_emitted_set`,
  `test_as5_thin_professional_review_trail_is_a_normal_200_typed_document`,
  `test_as5_every_emitted_pair_is_in_the_matrix`, `test_as5_no_match_is_documented_404_no_trail`.
- **AS-6** `test_as6_rebuild_stage_raise_is_typed_internal_error_500`,
  `test_as6_assembly_stage_raise_is_typed_internal_error_500`,
  `test_as6_unserialisable_assembled_document_is_typed_contract_error_500` (surrogate / NaN / inf),
  `test_as6_confident_document_survives_both_json_dumps_forms`.
- **AS-7** `test_as7_no_server_authored_claim_is_verified`,
  `test_as7_verification_status_only_echoes_the_source_case_insensitively`.
- **AS-8** `test_as8_evidence_route_is_registered_last_and_after_the_pre_existing_routes`,
  `test_as8_existing_routes_unaffected`, `test_as8_evidence_request_runs_fully_offline`,
  `test_as8_direct_assembly_is_pure_transport`.

## Modularity — ORCHESTRATOR ACTION REQUIRED

`evidence.py` is a single cohesive assemble-and-serialise responsibility. AS-8 requires
`python tools/modularity_check.py --check` to pass, but that command is **not** in this packet's
`documented_test_commands` and `tools/**` is listed in this packet's `forbidden_paths`, so — as in
the previous submission, and as the coordinator anticipated — I **did not and cannot** run it. The
orchestrator/supervisor must run it through the authorized command process and attach the result.

So the signal is still available without that tool, I measured the module the same way the checker
counts (non-blank, non-comment-only lines), in-process, touching nothing under `tools/**`:

| | raw lines | SLOC |
|---|---|---|
| HEAD `29ca7bca` (before this rework) | 518 | **410** |
| after this rework | 548 | **418** |

**+8 SLOC**, as the coordinator predicted: restoring the whole trail *deleted* more hand-picking
code than the fix added. The two projection literals (≈45 lines of per-key re-keying) collapsed into
one dict comprehension and one list comprehension; the growth is the `rule_conflict` gap branch, the
`_RELOCATED_SOURCE_FIELDS` declaration, and docstring rationale. Comfortably under the 600 warn
threshold either way, and the module's responsibility did not change.

## Files changed (allowed paths only)

- `services/api/app/api/v1/evidence.py` — **BLOCKING-1**: the assembler now transports the whole
  trail (each citation group = the entire `evaluation_trace` + one server-authored status;
  `source_coverage` = the entire `rule_evaluation` root minus the two declared relocations;
  `evaluated_input` = the whole sub-document), with `_RELOCATED_SOURCE_FIELDS` emitted as
  `source_field_routing` so the relocation is declared in the response. **BLOCKING-2**: an explicit
  `rule_conflict` branch in `_gap_markers` carrying the whole typed object. Plus docstring
  corrections. No change to any guard, matrix, status or serialisation behaviour.
- `services/api/tests/api/test_evidence_api.py` — 37 → **59** tests: key-set equality against the
  bundled source schema, whole-subtree byte-equality, a total `_stable_view`, the verification-claim
  walk, the route-view no-query-parameter assertion, the fetch-stage guard, and direct unit tests
  for the two pure classifiers including the `rule_conflict` gap.
- `services/api/app/main.py` — **unchanged** by this rework (`git diff --stat` empty); the additive
  registration from the original submission stands.
- `project-control/reports/M5-T013-producer-report.md` — this report.

## Gate-wave rework — defects, fixes and load-bearing evidence

### BLOCKING-1 (G1) — the document was a silent projection dropping 18 required fields

**Measured before the fix** (in-process, over the default F01 fixture + confident substrate):

```
rule_evaluation ROOT: 14/20 represented
  MISSING (6): ['lot_area_source', 'lot_area_sq_ft', 'rule_conflict', 'spatial_context',
                'spatial_uncertainty', 'zoning_district']
evaluation_trace:     7/19 represented
  MISSING (12): ['applicability_outcome', 'applicability_trace', 'computation_steps',
                 'data_completeness', 'determination', 'effective_window', 'evaluated_inputs',
                 'exceptions_applied', 'input_validation', 'notes', 'rule_release', 'uncertainty']

  outputs presented: {"max_residential_far": 1.5, "max_residential_floor_area_sq_ft": 15000.0}
  [DROPPED] exceptions_applied: "A higher maximum residential FAR (up to 2.00 for R5/R5A/R5B per
            ZR 23-21) applies to zoning lots that are 'qualifying residential sites'. ..."
  [DROPPED] notes: "... it is NOT an evidence-based determination ..."
  [DROPPED] computation_steps: identity 1.5 -> multiply -> 15000.0
  [DROPPED] rule_release: {"lifecycle_status": "needs_review", ..., "verified_eligible": false}
  [DROPPED] zoning_district "R5" / lot_area_sq_ft 10000.0 / lot_area_source / spatial_context /
            spatial_uncertainty / rule_conflict
```

6 + 12 = **18 fields**, matching G1's count. The harm is not the count: a **qualified** cap was
rendered **unqualified** in the one surface built to audit it — the reader saw `15000.0` with no
sight of the documented exception that a higher FAR may apply, nor of the note saying this is not an
evidence-based determination. "No summarisation that could change meaning" and "never silently
omitted" were both breached.

**After the fix:**

```
rule_evaluation ROOT: 20/20 represented   MISSING (0): []
evaluation_trace:     19/19 represented   MISSING (0): []
evaluated_input:      4/4                 MISSING (0): []
  [CARRIED] exceptions_applied / notes / computation_steps / rule_release /
            determination / uncertainty / zoning_district / lot_area_sq_ft /
            lot_area_source / rule_conflict / spatial_context / spatial_uncertainty
```

### BLOCKING-2 (G1 HIGH-1) — `rule_conflict` dropped, no gap marker

`rule_conflict` is the typed object the engine **deliberately preserves for reviewers**
(`app.rules.integration._conflict_result`): it names *which* rules compete, over which outputs, and
each one's effective window. Driven through `_gap_markers` with a faithful conflict document:

```
BEFORE  gap subjects : ['rule_evaluation', 'evaluation_trace', 'coverage']
        marker with subject 'rule_conflict'      : False
        any marker naming the competing rule ids : False
AFTER   gap subjects : ['rule_evaluation', 'evaluation_trace', 'rule_conflict', 'coverage']
        marker with subject 'rule_conflict'      : True
        any marker naming the competing rule ids : True
```

The marker is `{"kind": "data_conflict", "subject": "rule_conflict", "reason": <the conflict's own
note>, "detail": <the whole typed object, deep-copied>}`, and the generic posture markers still
fire — the conflict marker *adds* information rather than replacing them. G1 noted it could not
drive a live conflict document without editing forbidden paths; the same constraint applies to me,
so this is asserted by calling the pure classifier and the pure assembler directly, which is also
the honest place to test a pure function.

### How H-1 … H-5 were closed

| item | closure |
|---|---|
| **H-1** | Three total assertions replace the hand-picked lists: (a) **key-set equality** against the app's *own bundled* `rule_evaluation.schema.json` — so a field added to the source contract and then dropped also fails; (b) **whole-subtree byte-equality** of `source_coverage`, `evaluated_input`, `profile_provenance` and every citation group within one build, plus a deep-copy/aliasing check; (c) `_stable_view` now compares the **entire document** with exactly one empirically-determined volatile leaf masked (`observation_id` — probed as the *only* differing leaf across two identical requests, 67 occurrences). The AS-1 test that compared an independent rebuild was **renamed** to `test_as1_deterministic_provenance_and_citations_transport_byte_equal`, since that is what it actually asserts; the "whole trail" claim now lives on the two tests that really prove it. |
| **H-2** | `test_as6_fetch_stage_raise_is_typed_internal_error_500` injects a fetcher raising a non-`PlutoConnectorError` and asserts the documented `(500, "internal_error")` pair, JSON content type, correlation id, and no leak. |
| **H-3** | The four-path enumeration is replaced by `_verification_claims`, a **walk** over every node; any key in a verification-claim vocabulary must deny verification (never `True`, never the string `"verified"`). The test also asserts the walk actually reaches the top-level, per-group and deeply-nested claim keys, so the walk itself cannot silently stop working. Transported free prose stays deliberately out of scope, as documented on the response. |
| **H-4** | `test_as3_route_declares_no_query_parameter_and_no_body` asserts the route's own FastAPI view: `dependant.query_params == []`, `body_params == []`, `header_params == []`, `cookie_params == []`, `route.body_field is None`, `path_params == ["bbl"]`, methods `["GET"]` — and the same for both `Depends` seams, so a parameter cannot enter through a dependency either. |
| **H-5** | The two pure classifiers are unit-tested directly with synthetic dicts: `_completeness_marker` across all four documented outcomes (`complete` / `thin` / `conflicting` / `professional_review_required` — three of which **no available fixture can reach**) and `_gap_markers` across all seven documented gap branches plus the missing-provenance branch and the new `rule_conflict` branch. No fixtures, no runtime, no network. |

### Mutation evidence — every new assertion is load-bearing

Each mutation was applied to `evidence.py`, the guarding tests run, and the file restored
byte-exact (verified by `diff -q` after every iteration). **24 mutations applied, 24 CAUGHT, 0
SURVIVED** — including all seven mutations G3 reported as survivors:

| id | mutation | verdict |
|---|---|---|
| B1-trace / B1-root | revert to the hand-picked 7-of-19 / 10-of-20 projections | CAUGHT |
| B1-dropone / B1-droptrace | drop a **single** field (`zoning_district`; `exceptions_applied`) | CAUGHT |
| B2-gap / B2-root / B2-detail | remove the conflict branch; drop `rule_conflict` from the root; strip the marker's `detail` | CAUGHT |
| H1-reasons | `source_coverage.reasons` joined into one string | CAUGHT |
| H1-completeness / H1-family / H1-lifecycle | `data_completeness` → `{}`; `family_coverage` → `[]`; `rule_lifecycle_statuses` → `[]` | CAUGHT |
| H1-eibbl / H1-pcv | wrong `evaluated_input.bbl`; wrong `profile_contract_version` | CAUGHT |
| H1-groupkeys | group `rule_version` + `family` dropped | CAUGHT |
| H1-stableview | a per-request-varying value in a nested field the old projection never read | CAUGHT |
| H2 | the fetch-stage generic-500 guard removed | CAUGHT |
| H3-top / H3-nested / H3-status | a new server-authored `verified: True` at the top level; nested per citation group; `overall_verification_status` hardcoded to `"verified"` | CAUGHT |
| H4 | a `terse: bool = False` query parameter that strips `profile_provenance` | CAUGHT |
| H5-complete / H5-thin / H5-napp / H5-prov | classifier branches broken one at a time | CAUGHT |

`B1-dropone` and `B1-droptrace` matter most: they drop **one** field, which is the realistic future
regression, and key-set equality catches it. That is the assertion that holds BLOCKING-1 shut.
