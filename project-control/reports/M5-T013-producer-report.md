# M5-T013 Producer Report — Evidence / provenance endpoint (re-checkpoint)

**Task:** M5-T013 — Evidence / provenance endpoint (`GET /api/v1/properties/{bbl}/evidence`),
verbatim + honest, over the internal flag-gated API.
**Branch:** `task/M5-T013-evidence-endpoint`  **Producer:** backend-engineer (persistent-local-29)
**Directive:** D-038 (ALL) — positive product deliverable (Compare UI → **Evidence view**).

Producers do not self-accept. This report is evidence for the independent G0/G1/G3/G4/G5 gate wave.

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

Computed inside the documented command `python -m pytest services/api/tests/api` via a disclosed,
temporary in-suite `AssertionError` probe (git hash-object is not broker-approved), then the probe
was removed for the final clean run.

| File | SHA-256 | Binding |
|---|---|---|
| `services/api/app/api/v1/evidence.py` | `0329a4693fc622be6f3d305fd09a4955a5e0bf4284f279307ef37127d65f6c18` | probe-bound (final; file unchanged after) |
| `services/api/app/main.py` | `97be914803e6ea93a4e8c9a603eedf2b59a78b762bf5c40a7c04b2f2e10ce875` | probe-bound (final; not modified in this re-checkpoint) |
| `services/api/tests/api/test_evidence_api.py` | *(compute at commit)* | orchestrator/reviewer-bound — a probe cannot self-bind its own host test file (adding/removing it changes the bytes); the final file is the one that produced **349 passed** clean below |

Reviewer reproduces with:
`python -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path(r'services/api/app/api/v1/evidence.py').read_bytes()).hexdigest())"`.

## Test results (documented suites, rerun after the trim)

| Command | Result |
|---|---|
| `python -m pytest services/api/tests/api` | **349 passed** in 42.63s (0 failed, 0 regression; 37 evidence tests + 312 pre-existing) |
| `python -m pytest services/api/tests/scenario` | **388 passed** in 4.31s (0 regression) |

Environment: Python 3.11.9, pytest 8.4.2 (local sandbox, `rootdir=services/api`, `configfile=pyproject.toml`).
Fully offline through the injected fetcher/substrate seams — no network, Supabase, or Geoclient.

## Where to inspect the critical source (post-trim line spans)

`services/api/app/api/v1/evidence.py` (digest above):

| Item | Span |
|---|---|
| `STATUS_STATE_MATRIX` (single source of truth) | L111–L140 |
| `assemble_evidence_document` (verbatim transport) | L283–L360 |
| `_assert_json_safe` (fail-closed serialisation guard) | L363–L374 |
| `get_evidence` handler (flag guard → 422 → connector map → guarded rebuild/assembly/serialise) | L376–end |

`services/api/tests/api/test_evidence_api.py`:

| Scenario | Span |
|---|---|
| AS-3 body-less / non-GET 405 / malformed-BBL 422 pre-fetch | L405–L455 |
| AS-4 flag-gated 404 / no OpenAPI / existing flag reused | L458–L501 |
| AS-5 matrix == rule-eval set / thin-trail 200 / every emitted pair | L504–L632 |
| AS-6 fail-closed (rebuild/assembly/serialise raises; both json.dumps forms) | L635–L722 |
| AS-7 never Verified (server-authored scope) | L725–L753 |
| AS-8 additive registration / **egress landmine** / existing routes | L755–L878 (egress at L851) |

### Embedded span 1 — serialisation guard (`_assert_json_safe`, evidence.py L363–L374)

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

### Embedded span 2 — egress landmine core (test AS-8; landmine setup L806–L814, request L849, assertion L851)

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

`evidence.py` is a single cohesive assemble-and-serialise responsibility, well under the 600-SLOC
warn threshold (the trim reduced it further). AS-8 requires `python tools/modularity_check.py --check`
to pass, but that command is **not** in this packet's `documented_test_commands` and `tools/**` is a
forbidden path for this producer, so I **did not and cannot** run it. The orchestrator/supervisor
must run it through the authorized command process before the gate wave and attach the result.

## Files changed (allowed paths only)

- `services/api/app/api/v1/evidence.py` — route module; module + `_assert_json_safe` docstrings
  compacted (code unchanged).
- `services/api/tests/api/test_evidence_api.py` — module docstring compacted (all test logic
  unchanged); temporary digest probe added then removed.
- `services/api/app/main.py` — additive registration only (unchanged in this re-checkpoint).
- `project-control/reports/M5-T013-producer-report.md` — this report.
