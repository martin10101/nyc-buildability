# M5-T003 Producer Report — Scenario endpoint `GET /api/v1/properties/{bbl}/scenario`

**Task:** M5-T003 (backend) · **Milestone:** M5 · **Directive:** D-038 (ALL)
**Producer:** backend-engineer · **Stage:** claimed → evidence submitted (rework rev)
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t003`
**Branch:** `task/M5-T003-scenario-endpoint`

## 0. Rework summary (what changed this revision)

This revision addresses the reviewer's rework items **within allowed paths only**.
Execution evidence is now **orchestrator-captured and ALL GREEN** (scenario 27/27,
adjacent routes 107, config/flag/rule_eval 111, ruff clean, modularity 0 failures),
attributed to `project-control/reports/M5-T003-orchestrator-captured-evidence.md`
(commit `9cae874f`) rather than self-asserted, with the honest interpreter caveat that
capture ran on Python 3.11.9 (no 3.12 on the machine; the M5-T003 files collect/run
cleanly on 3.11 — only out-of-scope `app/documents/**` needs 3.12). See §6/§6a. Items:

1. **AS-2 now explicitly tests a VISIBLE review reason** (item 6). The split-lot test
   asserts (a) the top-level `reasons` list carries a human-readable professional-review
   explanation and (b) the `zoning_district` constraint provenance carries the exact
   spatial `review_reason` (`lot_overall_class=split_lot_confident`) propagated verbatim
   from the substrate — a machine-readable visible reason, not just the boolean flag.
2. **The matrix is now confirmed against `rule_evaluation` ITSELF** (item 5). A new test
   `test_as5_matrix_equals_rule_evaluation_route_emitted_set` DRIVES the sibling
   rule-evaluation route over the identical offline harness and asserts the scenario
   route's `STATUS_STATE_MATRIX` equals the set that route actually emits. (See §3a for
   why this is done by driving the route: `rule_evaluation.py` exports NO matrix constant.)
3. **§6 modularity command working directory corrected** (item 4): the modularity check
   runs from the **repo root**, not `services/api/` — `tools/modularity_check.py` lives at
   the repo root and scans the whole tree. Commands 1–4 (pytest/ruff) run from
   `services/api/`; command 5 runs from the repo root. See §6.
4. **Bounded, inspectable excerpts embedded** (item 2): the full current test file
   (Appendix A), the two dependency-provider definitions (Appendix B), the rule-evaluation
   route's emission enumeration + shared error-status map (Appendix C), and the scenario
   route's matrix + error mappers (Appendix D) are embedded verbatim with `path:line`
   ranges so the present implementation is inspectable. Digest-binding note in §6a.

## 1. Objective delivered

Exposed the already-built, already-tested deterministic scenario builder
(`app.scenario.build_scenario`) through a NEW read-only, flag-gated endpoint
`GET /api/v1/properties/{bbl}/scenario`. The route rebuilds the property profile
**and** its `rule_evaluation` document SERVER-SIDE over the SAME injected seams
the accepted rule-evaluation route uses, runs `build_scenario`, strict-validates
the body against `scenario@1.0.0`, and returns the documented (HTTP status,
state) matrix that mirrors `services/api/app/api/v1/rule_evaluation.py`.

No new legal calculation lives in the route: the only material number a scenario
carries is the canonical `max_residential_floor_area_sq_ft` cap already present
in the rule_evaluation trace, surfaced VERBATIM by `build_scenario`.

## 2. Files changed (all inside allowed_paths)

| File | Change | Size |
|---|---|---|
| `services/api/app/api/v1/scenario.py` | NEW router; mirrors rule_evaluation.py (flag gate → correlation id → BBL validation → injected fetch → no_match → profile build+validate → evaluate+serialize+validate rule_evaluation → `build_scenario` → validate_scenario_document → 200). `include_in_schema=False`. | 308 lines |
| `services/api/app/config.py` | Added `INTERNAL_SCENARIO_ENABLED_ENV_VAR` + `internal_scenario_enabled()`, refactored to a shared fail-safe `_flag_enabled` helper (existing `internal_rule_eval_enabled` behavior byte-identical). Default OFF. | 67 lines |
| `services/api/app/main.py` | Registered `scenario_v1_router` next to `rule_evaluation_v1_router` (import + one `include_router`); no other change. | 138 lines |
| `services/api/tests/api/test_scenario_api.py` | Acceptance pack AS-1..AS-7, mirroring the rule-evaluation offline harness. This rev: named `SPLIT_LOT_REVIEW_REASON`, AS-2 visible-review-reason assertions, and the new rule-evaluation-route matrix confirmation test. | 790 lines |
| `project-control/reports/M5-T003-producer-report.md` | This report. | — |

Forbidden paths (`app/scenario/`, `api/v1/rule_evaluation.py`, `api/v1/properties.py`,
`packages/contracts/`, `apps/web/`, `supabase/`, `.claude/`, `tools/`) were consumed
READ-ONLY only; none modified.

## 3. Design — seam reuse and the (status, state) matrix

- **Seams:** `fetcher = Depends(get_pluto_fetcher)` (from `properties`) and
  `substrate_provider = Depends(get_spatial_substrate_provider)` (from
  `rule_evaluation`) — the exact two injection points the accepted rule-evaluation
  route uses. Tests override BOTH via `app.dependency_overrides`, so the endpoint
  runs fully offline with NO Supabase and NO Geoclient (D-038-R004 / AS-7).
  Both provider definitions are embedded verbatim in **Appendix B**.
- **Rule-evaluation rebuild:** `evaluate_property(profile)` →
  `serialize_rule_evaluation(..., profile_contract_version=...)` →
  `validate_rule_evaluation_document(...)` — the identical deterministic path
  the rule-evaluation route uses; the serialized document is exactly the shape
  `build_scenario` consumes read-only.
- **`STATUS_STATE_MATRIX`** (single source of truth in `scenario.py`, embedded in
  **Appendix D**) equals the rule-evaluation route's emitted set:
  `{(200,None),(422,validation_error),(404,no_match),(502,schema_drift),(503,rate_limited),(503,source_unavailable),(504,timeout),(500,internal_error),(500,internal_contract_error)}`.
  The scenario-document contract defect reuses `(500, internal_contract_error)`
  (shared with the rebuilt-profile and rebuilt-rule_evaluation contract defects),
  so it introduces NO new pair. The disabled-flag 404 is the generic
  `{"detail":"Not Found"}` (no `state`), byte-indistinguishable from an unmounted
  path — not part of the matrix, exactly as in the mirrored route.
- **Fail-closed:** any conflict / professional-review / spatial uncertainty /
  malformed or absent controlling input yields a typed `no_scenario` /
  `unsupported` scenario document at **200** (a normal, usable result), never an
  invented cap. Genuine faults become the typed API errors above. `build_scenario`
  and `validate_scenario_document` also fail closed on any `verified` status.

### 3a. How the matrix is confirmed against `rule_evaluation` ITSELF (item 5)

`services/api/app/api/v1/rule_evaluation.py` exposes **no** `STATUS_STATE_MATRIX`
constant — its `__all__` is `["get_spatial_substrate_provider", "router"]`. Its
emitted (status, state) pairs are therefore established two independent ways, both
now present:

1. **By execution (new test):** `test_as5_matrix_equals_rule_evaluation_route_emitted_set`
   enables `INTERNAL_RULE_EVAL_ENABLED`, drives `GET /api/v1/properties/{bbl}/rule-evaluation`
   over the SAME offline fixture+substrate harness through every emission path
   (200 confident, 200 split-lot fail-safe, 422 malformed, 404 no_match, 504/503/502
   connector failures, 503 rate_limited, forced 500 internal_contract_error, forced
   500 internal_error), collects the emitted set, and asserts it **equals**
   `scenario.STATUS_STATE_MATRIX`. Test body in Appendix A (lines 551–633).
2. **By inspection (Appendix C):** the rule-evaluation route's emission points are
   enumerated with `path:line` refs and its connector-failure statuses come from the
   SAME `properties._ERROR_STATUS` map the scenario route imports. The derived emitted
   set equals the scenario matrix exactly.

The prior revision's `test_as5_matrix_is_the_existing_property_route_matrix_minus_version_pair`
(cross-check against the accepted `GET /properties/{bbl}` route's published matrix) is
retained as additional evidence; it is now correctly framed as the *property*-route
cross-check, distinct from the rule-evaluation-route confirmation above.

## 4. Acceptance-scenario mapping (AS-1..AS-7)

| AS | Test(s) | Proves |
|---|---|---|
| AS-1 | `test_as1_confident_r5_cap_surfaces_trace_value_verbatim` | Confident R5 (F01 + confident_r5_substrate) → 200 `preliminary`, `coverage_status=conditional`; `draft_zoning_floor_area_cap_sq_ft` **==** the trace `max_residential_floor_area_sq_ft` read back from the mirrored rule-evaluation route (== 15000.0), never recomputed; `cap_label` present; all 8 envelope families MISSING; never `verified`. |
| AS-2 | `test_as2_split_lot_is_no_scenario_ranges_preserved` | Split-lot substrate → 200 `no_scenario` / `professional_review_required`, **a VISIBLE review reason surfaced two ways** — the top-level `reasons` list carries a professional-review explanation, and the `zoning_district` provenance carries the exact `review_reason` `lot_overall_class=split_lot_confident` propagated verbatim — no cap, share RANGES (R5 0.55–0.65, R6 0.35–0.45) preserved, district never collapsed. |
| AS-3 | `test_as3_no_match_is_documented_404` | Valid-but-absent BBL → 404 `no_match` (distinguishable from the disabled 404), `source_id`, correlation id; no scenario body. |
| AS-4 | `test_as4_malformed_bbl_is_typed_422_no_connector_call` (×3), `..._timeout_maps_to_504`, `..._unavailable_maps_to_503`, `..._schema_drift_maps_to_502`, `..._internal_defect_is_generic_500_no_internals`, `test_as4_contract_validation_failure_is_typed_500_no_partial_scenario` | Malformed BBL → typed 422 with NO connector call; upstream failures → 504/503/502; internal defect → generic 500; a built-payload contract-validation failure → typed `(500, internal_contract_error)` — all with no partial scenario and no traceback/secret/path leaked. |
| AS-5 | `test_as5_status_state_matrix_is_the_documented_set`, `test_as5_matrix_is_the_existing_property_route_matrix_minus_version_pair`, **`test_as5_matrix_equals_rule_evaluation_route_emitted_set`**, `test_as5_every_emitted_pair_is_in_the_matrix` | Every 200 body passes `validate_scenario_document`; EVERY documented pair is actually driven (incl. `(503, rate_limited)` via three 429s exhausting `max_attempts=3`, and `(500, internal_contract_error)`) and the emitted set EQUALS `STATUS_STATE_MATRIX`. The matrix is confirmed **against the rule-evaluation route itself** (§3a) AND cross-checked against the accepted `GET /properties/{bbl}` route's published matrix (scenario == property-matrix − `{(500, unsupported_contract_version)}`). |
| AS-6 | `test_as6_flag_off_or_unknown_is_generic_404` (8 values), `test_as6_disabled_request_performs_no_dependency_io`, `test_as6_openapi_never_lists_the_internal_route` | Flag unset/empty/`0`/`false`/`off`/`maybe`/`2`/`"  "` → generic `{"detail":"Not Found"}`, no correlation id, no "scenario"/"flag" hint; route absent from OpenAPI even with the flag ON. A disabled request returns 404 WITHOUT invoking either injected seam's I/O-performing callable — proven with landmine seams and again with the REAL providers (no override). |
| AS-7 | `test_as7_confident_path_is_fully_offline`, `test_as7_existing_property_route_still_works`, and the shared harness under every test above | All scenarios run via FastAPI `TestClient` on the injected PLUTO fetcher + substrate over committed fixtures; no network, no Supabase, no Geoclient, no token read. Existing `/properties/{bbl}` route unaffected. |

## 5. Draft-engineering discipline (PRD §10–§13)

Every scenario carries `needs_review: true`, the not-Verified disclaimer, and a
coverage that tops out at `conditional`; a `verified` status can never leave the
layer (validator + `build_scenario` guards). The surfaced cap is the canonical
trace value only — the endpoint performs no independent legal calculation.
Published acceptance is deferred to G6/legal like the M4 chain.

## 6. Validation posture + exact commands + execution status (EVIDENCE CAPTURED — GREEN)

**Producer execution status — NOT self-run; orchestrator-captured, ALL GREEN.**
This producer worktree cannot execute the suite: the approval broker admits only
enumerated read-only git commands and the packet's `documented_test_commands`, and
the M5-T003 packet documents NONE, so `pytest`/`ruff` would stall the run — I did
not bypass that. Per the evidence-capture division of labor in
`.claude/rules/project-control.md`, the supervisor session (`ctl24-e5`) captured the
executable evidence into a committed artifact and the gate reviewers verify that
stored file. **Every claim below is attributed to that captured artifact, not
self-asserted:**

> **Orchestrator-captured evidence:**
> `project-control/reports/M5-T003-orchestrator-captured-evidence.md`
> (candidate branch, capture commit `9cae874f`), captured against this worktree's
> CURRENT state (edits uncommitted; branch HEAD `62aec042`). The captured digests
> (§6a) bind exactly the files that ran.

**Interpreter caveat (honest correction of the prior revision):** the only Python
usable on the capture machine is **3.11.9** (no 3.12 installed; the py-launcher's
3.13 entry does not resolve; GitHub push is held, so no fresh 3.12 CI). CI targets
3.12. This is valid evidence for M5-T003 because the scenario / rule-evaluation /
property / config / flag test chain **collects and runs cleanly on 3.11.9** — the
prior revision's blanket "this code targets 3.12/PEP 695 and cannot be collected on
3.11" was WRONG for THIS task's files; the only PEP-695 `type`-syntax code is in the
out-of-scope `app/documents/**` + `tests/documents/**` (e.g. `app/documents/units.py`),
never in the four M5-T003 files. The exact interpreter path/version is recorded in
the captured artifact.

**Commands + actual captured outcomes** (interpreter Python 3.11.9; exact path in the
captured artifact):

Working directory `services/api/`:

1. Scenario acceptance suite (this task's deliverable):
   `python -m pytest tests/api/test_scenario_api.py -q` → **exit 0, 27 passed**.
2. Mirrored-route + property/contract regression (this task edited `config.py` and
   `main.py`, shared with the rule-evaluation route and app):
   `python -m pytest tests/api/test_rule_evaluation_api.py tests/api/test_properties_v1.py tests/api/test_property_contract.py -q`
   → **exit 0, 107 passed**.
3. Config-flag unit regression (the `config.py` refactor to the shared `_flag_enabled`
   helper leaves `internal_rule_eval_enabled` byte-identical):
   `python -m pytest tests/ -k "config or flag or rule_eval" -q`
   → the bare form exits 2 ONLY because of 15 **pre-existing** PEP-695 collection
   errors in `tests/documents/**` (deselected anyway; collection aborts before `-k`
   filters — an unrelated 3.11-env artifact). The isolated re-run
   `python -m pytest tests/ -k "config or flag or rule_eval" --ignore=tests/documents -q`
   → **exit 0, 111 passed**. The targeted config/flag/rule_eval tests pass.
4. Required lint (whole tree, CI ruleset `E,F,I,UP,B`, line-length 100, target py312 —
   `services/api/pyproject.toml`):
   `python -m ruff check .` → **exit 0, "All checks passed!"**.

Working directory **repo root** (`C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t003`) —
CORRECTED this revision (item 4): `tools/modularity_check.py` lives at the repo root,
not under `services/api/`, and scans the whole tree, so it MUST be run from the repo
root:

5. Modularity check (production file `scenario.py` is 308 lines — well under the
   warn-600 threshold; `config.py` 67, `main.py` 138; the **test** file is 790 lines
   but a test file is out of the checker's scope — `EXCLUDED_SEGMENTS` contains
   `tests` and `_is_test_file` matches `test_*`):
   `python tools/modularity_check.py --check` → **exit 0, 0 failures, 14 warnings**
   (all pre-existing supervisor / apps-web / connector modules; NONE in the four
   M5-T003 files).

**Fix-forward rule (this packet):** any failure is repaired ONLY inside the four
allowed code/test paths; a failure that would require editing a forbidden path is
reported as a blocker rather than worked around. No such failure arose — the capture
is fully green — so no code fix was needed this revision beyond the test + report
rework.

Reviewers: verify `project-control/reports/M5-T003-orchestrator-captured-evidence.md`
(commit `9cae874f`) as the G0/G1/G3/G4 evidence, confirm the §6a digests still match
the four files at the gate HEAD, and confirm this report's §4 claims against that
captured output before acceptance.

### 6a. Digest-binding note

Cryptographic digest computation is not available to the producer in-sandbox
(`git hash-object` and ad-hoc hashing are not broker-approved for a producer, and the
packet documents no pytest command through which to run a digest probe). The embedded
excerpts (Appendices A–D) are the **verbatim current working-tree content** bound by
`path:line` range, so the present implementation is inspectable without a commit.

The supervisor captured `sha256` digests of the four changed files, **identical
before and after** the test run (no concurrent edit during capture), binding exactly
what ran (branch HEAD `62aec042`, edits uncommitted):

| File | sha256 |
|---|---|
| `services/api/app/api/v1/scenario.py` | `7b5127ced2e69e51635caf07e670dc1eaafd82c669336c5db1c8b04974385d89` |
| `services/api/app/config.py` | `5d27ac07b09fd203f7001cd2480d5a93b23879e188cd9a35b7f9d6dc2cbc300d` |
| `services/api/app/main.py` | `eb5523abcd423a00922681b0512c2b32fc89aa1f8d9540c47aab0cd6113742ab` |
| `services/api/tests/api/test_scenario_api.py` | `47399b4aacf73d7ee246c43d37775884443d86caf49389ebdf504ebca3ad57fe` |

These four files are UNCHANGED after the capture (this revision touched only this
report, which is not among the digested files), so the captured evidence stands as-is.
At the gate HEAD the reviewer re-confirms these digests still match; if a later commit
preserves the digests, the capture remains valid without a re-run.

## 7. Reviewer checklist (G3/G4/G5)

- Confirm the (status,state) matrix equals the rule-evaluation route's emitted set —
  now confirmed by driving that route itself (§3a; Appendix A lines 551–633; Appendix C)
  — and that no distinguishable status leaks the disabled feature (AS-6).
- Confirm the surfaced cap is the trace value verbatim, never recomputed (AS-1).
- Confirm fail-closed 200 `no_scenario` outcomes preserve share ranges, surface a
  VISIBLE review reason (AS-2), and invent no cap; and that no error path emits a
  partial scenario (AS-4).
- Confirm no forbidden path was modified and the flag defaults OFF (fail-safe).

---

## Appendix A — `services/api/tests/api/test_scenario_api.py` (verbatim, lines 1–790)

Current working-tree content of the acceptance pack (the deliverable). This is the
authoritative source for the "omitted test bodies"; AS-2's visible-review-reason
assertions are at lines 353–376 and the rule-evaluation-route matrix confirmation is
at lines 551–633.

```python
"""Internal scenario endpoint acceptance pack (task M5-T003, AS-1..AS-7).

Offline and deterministic. The route's PLUTO fetcher and its server-side spatial
substrate provider are both overridden via FastAPI dependency injection with the
accepted recorded-official PLUTO fixtures (services/api/tests/fixtures/pluto) and
faithful M2-T013 substrate dicts - the SAME harness the accepted rule-evaluation
endpoint test uses - so NO test touches the network, Supabase, or Geoclient
(AS-7). The endpoint rebuilds the profile AND its rule_evaluation server-side
over those seams and runs the already-built deterministic ``build_scenario``.

Coverage of the acceptance scenarios:

* AS-1 confident R5 cap -> 200 preliminary scenario whose cap is surfaced
  VERBATIM from the rule_evaluation trace (asserted equal to the trace value read
  from the mirrored rule-evaluation route, never locally recomputed); cap_label
  present; the 8 envelope families are MISSING; never Verified.
* AS-2 split-lot -> fail-closed no_scenario / professional-review, share RANGES
  preserved (never collapsed), no cap surfaced (a NORMAL 200 document).
* AS-3 no-match BBL -> documented 404 no_match with correlation id; no scenario.
* AS-4 malformed BBL / upstream failure (incl. rate-limit) / internal defect /
  contract-validation failure -> documented typed error; no partial or invented
  scenario is ever emitted and no internals leak.
* AS-5 contract: every 200 body passes validate_scenario_document; EVERY
  documented (HTTP status, state) pair - including (503, rate_limited) and
  (500, internal_contract_error) - is actually driven, the emitted set equals the
  route's documented matrix, and that matrix is cross-checked against the accepted
  GET /properties/{bbl} route's published matrix.
* AS-6 flag-off -> generic 404 indistinguishable from an unmounted path, absent
  from the OpenAPI schema, and reached WITHOUT invoking either injected seam's
  I/O-performing callable (landmine seams prove non-invocation).
* AS-7 offline: AS-1..AS-6 all run under the injected seams over committed
  fixtures via FastAPI TestClient - no network, no Supabase, no Geoclient.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import rule_evaluation as rule_evaluation_module
from app.api.v1 import scenario as scenario_module
from app.api.v1.properties import STATUS_STATE_MATRIX as PROPERTY_MATRIX
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.api.v1.scenario import STATUS_STATE_MATRIX
from app.config import (
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
)
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.rules.response import RuleEvaluationContractError
from app.scenario.contract import ScenarioContractError, validate_scenario_document

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"

# The professional-review reason the split-lot substrate carries. AS-2 asserts
# this exact reason is surfaced VISIBLY in the scenario document (propagated
# verbatim through rule_evaluation.spatial_uncertainty.review_reasons into the
# zoning_district constraint provenance), never silently dropped.
SPLIT_LOT_REVIEW_REASON = "lot_overall_class=split_lot_confident"

# The 8 envelope families the coverage matrix must always list as MISSING
# (constants.MISSING_ENVELOPE_CONSTRAINTS keys; asserted, never imported, so a
# silent change to that tuple surfaces here).
MISSING_ENVELOPE_FAMILIES = frozenset(
    {
        "height_limit",
        "setbacks_yards",
        "lot_coverage_open_space",
        "street_wall_base_height",
        "parking_loading",
        "use_group_overlay",
        "special_districts_overlays",
        "density_bonuses",
    }
)


# --------------------------------------------------------------------------
# Fetcher + substrate override plumbing (fixture-transport, offline) - mirrors
# tests/api/test_rule_evaluation_api.py so the two internal routes share the
# exact same offline harness.
# --------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


class FakeTransport:
    def __init__(self, script: list):
        self.script = list(script)

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        if not self.script:
            raise AssertionError("FakeTransport script exhausted")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def _fetcher(script_factory):
    def fetch(bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=FakeTransport(script_factory()),
            sleep=lambda s: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )

    return fetch


def install_fetcher(script_factory) -> None:
    app.dependency_overrides[get_pluto_fetcher] = lambda: _fetcher(script_factory)


def install_substrate(substrate) -> None:
    app.dependency_overrides[get_spatial_substrate_provider] = (
        lambda: (lambda canonical_bbl, correlation_id: substrate)
    )


def install_landmine_seams() -> None:
    """Override BOTH injected seams with providers whose RETURNED callables raise
    if ever invoked. The providers themselves are cheap (they only return the
    callable), so FastAPI resolves the dependency without side effects - exactly
    like the real ``get_pluto_fetcher`` / ``get_spatial_substrate_provider``,
    which return a function reference and perform their network / spatial I/O only
    when that reference is CALLED. A disabled request that returns 404 before
    calling either seam therefore performs NO fetch or substrate I/O and cannot be
    broken by a failing dependency callable; if the flag check ever regressed to
    run after a seam call, these landmines would fire and fail the test."""
    def _landmine_fetcher_provider():
        def fetch(bbl: str, correlation_id: str):
            raise AssertionError(
                "PLUTO fetcher must not be invoked for a disabled-flag request"
            )

        return fetch

    def _landmine_substrate_provider():
        def provide(canonical_bbl: str, correlation_id: str):
            raise AssertionError(
                "spatial-substrate provider must not be invoked for a disabled request"
            )

        return provide

    app.dependency_overrides[get_pluto_fetcher] = _landmine_fetcher_provider
    app.dependency_overrides[get_spatial_substrate_provider] = _landmine_substrate_provider


def enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def raw_client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------
# Faithful M2-T013 substrate dicts (the shape build_property_profile consumes;
# mirrors tests/api/test_rule_evaluation_api.py so both routes share fixtures).
# --------------------------------------------------------------------------


def _pair(label: str, pair_class: str, *, lot_area=10000.0, share=(1.0, 1.0, 1.0), minor=False):
    smin, spoint, smax = share
    return {
        "layer": "nyzd",
        "family": "base_zoning",
        "district_label": label,
        "pair_class": pair_class,
        "raw_intersection_sq_ft": lot_area * spoint,
        "firm_intersection_sq_ft": lot_area * spoint,
        "dilated_intersection_sq_ft": lot_area * smax,
        "distance_ft": 0.0,
        "lot_area_sq_ft": lot_area,
        "share_min": smin,
        "share_point": spoint,
        "share_max": smax,
        "minor_portion": minor,
    }


def _substrate(lot_overall_class: str, pairs: list, *, review: bool, review_reasons=None):
    return {
        "bbl": BBL,
        "lot_overall_class": lot_overall_class,
        "pairs": pairs,
        "coverage_audits": [{"family": "base_zoning", "status": "unknown"}],
        "crosscheck": None,
        "professional_review_required": review,
        "review_reasons": review_reasons or [],
        "unassigned_area": [],
        "overlap_area": [],
        "accuracy_records": [{"applies_to": "lot", "value_ft": 20.0, "basis": "documented"}],
        "policy": {"version": "policy-1"},
        "provenance": {
            "source_id": "nyc-dcp-mappluto-arcgis",
            "requested_bbl": BBL,
            "retrieved_at": "2026-07-16T12:00:00Z",
            "normalized_digest": "sha256:" + "e" * 64,
            "source_data_last_edited": "2026-07-15T00:00:00Z",
        },
        "coverage_note": "facts_with_uncertainty; not a Verified zoning determination",
        "notes": [],
    }


def confident_r5_substrate(area: float = 10000.0):
    return _substrate(
        "single_district_confident",
        [_pair("R5", "interior_confident", lot_area=area)],
        review=False,
    )


def split_lot_substrate():
    return _substrate(
        "split_lot_confident",
        [
            _pair("R5", "split_confident", share=(0.55, 0.60, 0.65)),
            _pair("R6", "split_confident", share=(0.35, 0.40, 0.45)),
        ],
        review=True,
        review_reasons=[SPLIT_LOT_REVIEW_REASON],
    )


def _constraints_by_key(doc: dict) -> dict:
    return {c["key"]: c for c in doc["constraints"]}


def _coverage_values(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                yield value
            yield from _coverage_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _coverage_values(item)


# ==========================================================================
# AS-1 - confident R5 cap: 200 preliminary scenario, cap surfaced VERBATIM.
# ==========================================================================


def test_as1_confident_r5_cap_surfaces_trace_value_verbatim(client, monkeypatch):
    # Enable BOTH internal routes so the SAME inputs can be read back through the
    # mirrored rule-evaluation route to prove the scenario cap is the trace value
    # verbatim (not a locally recomputed number).
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    doc = response.json()

    # Strict canonical-contract validity (the endpoint's own pre-send check).
    validate_scenario_document(doc)

    # A preliminary, conditional, never-Verified draft scenario.
    assert doc["scenario_kind"] == "preliminary"
    assert doc["coverage_status"] == "conditional"
    assert doc["needs_review"] is True
    assert "verified" not in set(_coverage_values(doc))
    assert doc["not_verified_disclaimer"]

    # The cap is the canonical trace value, VERBATIM. Read the trace value from
    # the mirrored rule-evaluation route over the identical inputs.
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    rule_eval = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    trace_cap = rule_eval["evaluations"][0]["outputs"]["max_residential_floor_area_sq_ft"]
    assert doc["draft_zoning_floor_area_cap_sq_ft"] == trace_cap == 15000.0
    assert doc["cap_label"]  # present, non-null

    # The cap constraint carries the draft label and its trace provenance.
    residential = _constraints_by_key(doc)["residential_far_cap"]
    assert residential["value"] == trace_cap
    assert residential["state"] == "draft"

    # The coverage matrix lists all 8 envelope families as MISSING, never inferred.
    missing = {
        row["constraint_family"]
        for row in doc["coverage_matrix"]
        if row["rule_status_today"] == "missing"
    }
    assert MISSING_ENVELOPE_FAMILIES <= missing
    for family in MISSING_ENVELOPE_FAMILIES:
        assert _constraints_by_key(doc)[family]["state"] == "missing"


# ==========================================================================
# AS-2 - split-lot: fail-closed no_scenario, share ranges preserved, no cap.
# ==========================================================================


def test_as2_split_lot_is_no_scenario_ranges_preserved(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200  # a fail-closed outcome is a normal document
    doc = response.json()
    validate_scenario_document(doc)

    assert doc["scenario_kind"] == "no_scenario"
    assert doc["coverage_status"] == "professional_review_required"
    assert doc["professional_review_required"] is True
    # No cap surfaced.
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None
    assert doc["cap_label"] is None

    # A VISIBLE review reason is surfaced, never silently dropped. Surface (a):
    # the top-level human-readable reasons list explains WHY this is a
    # professional-review no_scenario outcome.
    assert isinstance(doc["reasons"], list) and doc["reasons"]
    assert any(
        "professional" in reason.lower() and "review" in reason.lower()
        for reason in doc["reasons"]
    )

    # Share RANGES preserved verbatim, never collapsed to a single district.
    district = _constraints_by_key(doc)["zoning_district"]
    assert district["value"] is None  # never collapsed
    candidates = {
        c["district_label"]: c
        for c in district["provenance"]["base_district_candidates"]
    }
    assert candidates["R5"]["share_min"] == 0.55 and candidates["R5"]["share_max"] == 0.65
    assert candidates["R6"]["share_min"] == 0.35 and candidates["R6"]["share_max"] == 0.45

    # Surface (b): the district-constraint provenance carries the EXACT spatial
    # review reason from the substrate, propagated verbatim through
    # rule_evaluation.spatial_uncertainty.review_reasons - a machine-readable,
    # visible review reason (not merely a boolean flag).
    assert SPLIT_LOT_REVIEW_REASON in district["provenance"]["review_reasons"]


# ==========================================================================
# AS-3 - no-match BBL: documented 404 no_match, correlation id, no scenario.
# ==========================================================================


def test_as3_no_match_is_documented_404(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)

    response = client.get("/api/v1/properties/5999999999/scenario")
    assert response.status_code == 404
    assert response.headers["x-correlation-id"]
    body = response.json()
    assert body["state"] == "no_match"  # distinguishable from the disabled-flag 404
    assert body["source_id"] == SOURCE_ID
    assert body["correlation_id"]
    # No invented scenario body.
    assert "scenario_kind" not in body and "constraints" not in body


# ==========================================================================
# AS-4 - malformed BBL / upstream failure / internal defect -> typed errors.
# ==========================================================================


@pytest.mark.parametrize(
    ("bbl", "expected_code"),
    [("abc", "non_numeric"), ("100001010", "wrong_length"), ("0000010100", "invalid_borough")],
)
def test_as4_malformed_bbl_is_typed_422_no_connector_call(
    client, monkeypatch, bbl, expected_code
):
    enable_flag(monkeypatch)

    def must_not_call(b, c):
        raise AssertionError("connector must not be called for a malformed BBL")

    app.dependency_overrides[get_pluto_fetcher] = lambda: must_not_call
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{bbl}/scenario")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == expected_code
    assert body["correlation_id"]


def test_as4_upstream_timeout_maps_to_504_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportTimeout("timeout after 10.0s")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 504
    assert response.json()["state"] == "timeout"


def test_as4_upstream_unavailable_maps_to_503_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportFailure("network failure: OSError")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 503
    assert response.json()["state"] == "source_unavailable"


def test_as4_schema_drift_maps_to_502_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")])
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 502
    assert response.json()["state"] == "schema_drift"


def test_as4_internal_defect_is_generic_500_no_internals(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    def exploding_builder(result, **kwargs):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::injected")

    monkeypatch.setattr(scenario_module, "build_property_profile", exploding_builder)
    response = raw_client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 500
    assert response.headers.get("X-Correlation-ID")
    body = response.json()  # strict JSON (never Starlette's plain-text 500)
    assert body["state"] == "internal_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    # No invented/partial scenario and no internals leaked.
    assert "scenario_kind" not in body
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as4_contract_validation_failure_is_typed_500_no_partial_scenario(
    raw_client, monkeypatch
):
    # A built payload that fails its canonical-contract validation before send is
    # an internal defect (an invalid 200 is impossible), mapped to the documented
    # typed (500, internal_contract_error) pair - NEVER a partial/invalid scenario
    # and never a raw stack. Driven via the scenario-document validator, the last
    # of the three contract checks the route runs (rebuilt profile, rebuilt
    # rule_evaluation, assembled scenario all share this pair).
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    def failing_validator(doc):
        raise ScenarioContractError(
            "secret-internal-path C:\\hostile\r\n::injected", location="constraints/0"
        )

    monkeypatch.setattr(scenario_module, "validate_scenario_document", failing_validator)
    response = raw_client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    # No partial/invented scenario body and no internals (message, path, stack).
    assert "scenario_kind" not in body and "constraints" not in body
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


# ==========================================================================
# AS-5 - contract: every 200 validates; the emitted (status, state) matrix.
# ==========================================================================


def test_as5_status_state_matrix_is_the_documented_set():
    # The single source of truth mirrors the rule-evaluation route's matrix: a
    # 200 (no state), the 422 validation pair, the 404 no_match result pair, the
    # connector-failure pairs, and the two generic 500 pairs. The scenario
    # contract defect reuses (500, internal_contract_error) -> no new pair.
    assert STATUS_STATE_MATRIX == frozenset(
        {
            (200, None),
            (422, "validation_error"),
            (404, "no_match"),
            (502, "schema_drift"),
            (503, "rate_limited"),
            (503, "source_unavailable"),
            (504, "timeout"),
            (500, "internal_error"),
            (500, "internal_contract_error"),
        }
    )


def test_as5_matrix_is_the_existing_property_route_matrix_minus_version_pair():
    # Cross-check against an ACTUAL existing route's published matrix (the
    # accepted GET /properties/{bbl} route, app.api.v1.properties), not just this
    # module's own literal. The scenario route emits the SAME pairs except the
    # bounded (500, unsupported_contract_version) case: the property route
    # surfaces an unpublished contract_version distinctly, whereas the scenario
    # and rule-evaluation rebuild paths collapse that defect into the shared
    # (500, internal_contract_error) pair (see app/api/v1/scenario.py, which maps
    # both UnsupportedContractVersionError and ContractValidationError to
    # _internal_contract_error_500). So the scenario matrix introduces NO pair the
    # existing route does not already document.
    version_pair: tuple[int, str | None] = (500, "unsupported_contract_version")
    assert STATUS_STATE_MATRIX == PROPERTY_MATRIX - {version_pair}
    assert version_pair in PROPERTY_MATRIX  # the existing route DOES document it
    assert version_pair not in STATUS_STATE_MATRIX  # scenario collapses it away


def test_as5_matrix_equals_rule_evaluation_route_emitted_set(
    client, raw_client, monkeypatch
):
    # Confirm the scenario matrix against the SIBLING rule-evaluation ROUTE
    # ITSELF (app.api.v1.rule_evaluation), the route this task mirrors - not
    # merely the property route's published constant. rule_evaluation.py exposes
    # NO matrix constant, so we DRIVE its route over the identical offline
    # harness, collect every emitted (HTTP status, state) pair, and assert the
    # scenario route's single-source-of-truth matrix EQUALS the set the
    # rule-evaluation route actually emits. This is the direct evidence for the
    # report's claim that the scenario matrix equals the rule-evaluation route's
    # emitted set (the scenario-document contract defect reuses the shared
    # (500, internal_contract_error) pair, introducing none of its own).
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    emitted: set[tuple[int, str | None]] = set()
    url = f"/api/v1/properties/{BBL}/rule-evaluation"

    def record(response):
        state = None if response.status_code == 200 else response.json().get("state")
        emitted.add((response.status_code, state))

    # 200 (confident) + 200 (split-lot fail-safe: a NORMAL rule_evaluation
    # document, still 200 / no state - the rule-evaluation route never errors on
    # a professional-review outcome, exactly like the scenario route).
    for substrate in (confident_r5_substrate(), split_lot_substrate()):
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(substrate)
        resp = client.get(url)
        assert resp.status_code == 200
        record(resp)

    # 422 malformed BBL, with NO connector call.
    install_substrate(confident_r5_substrate())
    app.dependency_overrides[get_pluto_fetcher] = lambda: (
        lambda b, c: (_ for _ in ()).throw(AssertionError("no call"))
    )
    record(client.get("/api/v1/properties/abc/rule-evaluation"))

    # 404 no_match.
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    record(client.get("/api/v1/properties/5999999999/rule-evaluation"))

    # 504 timeout, 503 source_unavailable, 502 schema_drift, 503 rate_limited.
    for script, expected in (
        (lambda: [TransportTimeout("t")] * 3, 504),
        (lambda: [TransportFailure("f")] * 3, 503),
        (lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")], 502),
        (lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3, 503),
    ):
        install_fetcher(script)
        install_substrate(confident_r5_substrate())
        resp = client.get(url)
        assert resp.status_code == expected
        record(resp)

    # 500 internal_contract_error: force the rule-evaluation route's own document
    # validator to fail (its contract-defect branch, the sibling of the scenario
    # route's).
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        rule_evaluation_module,
        "validate_rule_evaluation_document",
        lambda doc: (_ for _ in ()).throw(
            RuleEvaluationContractError("forced contract defect", location="<root>")
        ),
    )
    record(raw_client.get(url))

    # 500 internal_error: any unexpected exception in the build stage (explodes
    # before the still-patched validator is reached).
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        rule_evaluation_module,
        "build_property_profile",
        lambda result, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    record(raw_client.get(url))

    # The rule-evaluation route emitted EXACTLY the scenario route's matrix.
    assert emitted == STATUS_STATE_MATRIX


def test_as5_every_emitted_pair_is_in_the_matrix(client, raw_client, monkeypatch):
    enable_flag(monkeypatch)
    emitted: set[tuple[int, str | None]] = set()

    def record(response):
        state = None if response.status_code == 200 else response.json().get("state")
        emitted.add((response.status_code, state))

    # 200 preliminary + 200 no_scenario (both must validate).
    for substrate in (confident_r5_substrate(), split_lot_substrate()):
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(substrate)
        resp = client.get(f"/api/v1/properties/{BBL}/scenario")
        assert resp.status_code == 200
        validate_scenario_document(resp.json())
        record(resp)

    # 422 malformed, 404 no_match, 504/503/502 connector failures.
    install_substrate(confident_r5_substrate())
    app.dependency_overrides[get_pluto_fetcher] = lambda: (
        lambda b, c: (_ for _ in ()).throw(AssertionError("no call"))
    )
    record(client.get("/api/v1/properties/abc/scenario"))

    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    record(client.get("/api/v1/properties/5999999999/scenario"))

    # 504 timeout, 503 source_unavailable, 502 schema_drift, AND 503 rate_limited
    # (the fourth connector pair: three 429s exhaust the bounded retry budget).
    for script, expected in (
        (lambda: [TransportTimeout("t")] * 3, 504),
        (lambda: [TransportFailure("f")] * 3, 503),
        (lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")], 502),
        (lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3, 503),
    ):
        install_fetcher(script)
        install_substrate(confident_r5_substrate())
        resp = client.get(f"/api/v1/properties/{BBL}/scenario")
        assert resp.status_code == expected
        record(resp)

    # 500 internal_contract_error: a built payload fails its canonical-contract
    # validation before send. Driven via the scenario-document validator (the last
    # of the three contract checks the route runs); the rebuilt-profile and
    # rebuilt-rule_evaluation contract branches emit the SAME pair.
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        scenario_module,
        "validate_scenario_document",
        lambda doc: (_ for _ in ()).throw(
            ScenarioContractError("forced scenario contract defect", location="<root>")
        ),
    )
    record(raw_client.get(f"/api/v1/properties/{BBL}/scenario"))

    # 500 internal_error: any unexpected exception -> the generic pair. (build
    # explodes before the still-patched validator is reached.)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        scenario_module,
        "build_property_profile",
        lambda result, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    record(raw_client.get(f"/api/v1/properties/{BBL}/scenario"))

    # Every documented pair was actually driven AND the route emitted nothing
    # undocumented: the emitted set EQUALS the single-source-of-truth matrix.
    assert emitted == STATUS_STATE_MATRIX


# ==========================================================================
# AS-6 - flag-off / unknown -> generic 404; never in the OpenAPI schema.
# ==========================================================================


@pytest.mark.parametrize("flag_value", [None, "", "0", "false", "off", "maybe", "2", "  "])
def test_as6_flag_off_or_unknown_is_generic_404(client, monkeypatch, flag_value):
    if flag_value is None:
        monkeypatch.delenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, flag_value)
    # Landmine seams: a disabled request must return 404 WITHOUT invoking the
    # fetcher or substrate callables (the only things that perform network /
    # spatial I/O and could fail). The providers resolve cleanly; the returned
    # callables raise if the handler ever reached them.
    install_landmine_seams()

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 404
    # Byte-indistinguishable from an unmounted path: only {"detail": "Not Found"}.
    assert response.json() == {"detail": "Not Found"}
    # No hint the feature exists and no correlation id disclosed.
    text = response.text.lower()
    assert "scenario" not in text and "flag" not in text
    assert "x-correlation-id" not in {k.lower() for k in response.headers}


def test_as6_disabled_request_performs_no_dependency_io(client, monkeypatch):
    # Explicit fail-safe guard for the disabled path: the flag check runs FIRST,
    # so neither injected seam's I/O-performing callable is invoked. Proven two
    # ways over the SAME disabled request.
    monkeypatch.delenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, raising=False)

    # (a) Landmine seams installed: the handler must not call them -> still 404.
    install_landmine_seams()
    landmined = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert landmined.status_code == 404
    assert landmined.json() == {"detail": "Not Found"}

    # (b) No override at all: the REAL providers resolve (they only return a
    # function reference; no network/Supabase/Geoclient touched at resolution)
    # and the disabled handler returns 404 before any fetch is attempted.
    app.dependency_overrides.clear()
    real = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert real.status_code == 404
    assert real.json() == {"detail": "Not Found"}


def test_as6_openapi_never_lists_the_internal_route(client, monkeypatch):
    # Even with the flag ON the route is include_in_schema=False -> never a hint.
    enable_flag(monkeypatch)
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/api/v1/properties/{bbl}/scenario" not in paths
    assert "/api/v1/properties/{bbl}" in paths  # the existing route is unaffected


# ==========================================================================
# AS-7 - offline / no credentials: the confident path runs purely on the
# injected seams over committed fixtures (all tests above share this harness).
# ==========================================================================


def test_as7_confident_path_is_fully_offline(client, monkeypatch):
    # No SOCRATA/Supabase/Geoclient credential is set or read; the ONLY data
    # sources are the committed PLUTO fixture and the injected substrate.
    monkeypatch.delenv("SOCRATA_APP_TOKEN", raising=False)
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    validate_scenario_document(response.json())


def test_as7_existing_property_route_still_works(client):
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    response = client.get(f"/api/v1/properties/{BBL}")
    assert response.status_code == 200
    assert response.json()["identity"]["bbl"] == BBL
```

## Appendix B — Dependency-provider definitions (READ-ONLY, forbidden paths)

The two injection seams the scenario route depends on, embedded verbatim so the
reviewer can confirm both are cheap function-reference providers (no I/O at
resolution time — the basis for the AS-6 landmine argument).

**`services/api/app/api/v1/properties.py` lines 74–81, 111–138** (PLUTO fetcher seam +
the shared connector error→status map the scenario route imports):

```python
# Connector error_type -> HTTP status (see module docstring table).
_ERROR_STATUS: dict[str, int] = {
    "rate_limited": 503,
    "source_unavailable": 503,
    "timeout": 504,
    "schema_drift": 502,
}
_DEFAULT_ERROR_STATUS = 503

# ... (STATUS_STATE_MATRIX, docstring) ...

# Fetcher contract: (canonical_bbl, correlation_id) -> PlutoFetchResult.
# Injected through FastAPI dependency_overrides so tests run offline on the
# fixture transport while production uses the live connector unchanged.
PlutoFetcher = Callable[[str, str], PlutoFetchResult]


@lru_cache(maxsize=1)
def _default_resilient_fetcher():
    """Process-wide resilient fetcher (task M1-T009): ... Lazily built so importing
    this module never reads resilience env vars at import time ..."""
    from app.resilience.fetcher import build_default_resilient_fetcher

    return build_default_resilient_fetcher()


def _default_fetcher(canonical_bbl: str, correlation_id: str) -> PlutoFetchResult:
    return _default_resilient_fetcher()(canonical_bbl, correlation_id)


def get_pluto_fetcher() -> PlutoFetcher:
    """Dependency returning the PLUTO fetcher (override point for tests)."""
    return _default_fetcher
```

**`services/api/app/api/v1/rule_evaluation.py` lines 91–104** (server-side spatial
substrate seam; the scenario route imports `get_spatial_substrate_provider` from here):

```python
# (canonical_bbl, correlation_id) -> the M2-T013 substrate (LotIntersectionRecord
# or its dict form) for that BBL, or None when no substrate is available.
SpatialSubstrateProvider = Callable[[str, str], object | None]


def _default_spatial_substrate(canonical_bbl: str, correlation_id: str) -> object | None:
    return default_live_substrate(canonical_bbl, correlation_id)


def get_spatial_substrate_provider() -> SpatialSubstrateProvider:
    """Dependency returning the server-side spatial-substrate provider (override
    point for tests). The default is the settings-gated live provider: flag off
    (the default) yields no substrate -> honest fail-safe."""
    return _default_spatial_substrate
```

Both providers return a bare function reference; the network / spatial I/O happens
only when that reference is CALLED. `get_pluto_fetcher` builds the resilient fetcher
lazily (still no network at resolution). This is why a disabled-flag request that
returns 404 before calling either seam performs no I/O (AS-6).

## Appendix C — Rule-evaluation route emission enumeration (matrix, READ-ONLY)

`rule_evaluation.py` exports NO `STATUS_STATE_MATRIX` constant (`__all__ =
["get_spatial_substrate_provider", "router"]`). Its emitted (status, state) pairs,
enumerated from the route body with `path:line` refs:

| Emission | `rule_evaluation.py` line(s) | (status, state) | In matrix? |
|---|---|---|---|
| Disabled flag → generic 404 | 149–150 → `_not_found()` 114–118 | (404, `{"detail":"Not Found"}`, no state) | NO (generic, excluded — same as scenario) |
| Malformed BBL (pre-fetch) | 164–173 | (422, `validation_error`) | yes |
| Connector failure → `properties._ERROR_STATUS` | 185–197 | (502, `schema_drift`), (503, `rate_limited`), (503, `source_unavailable`), (504, `timeout`) | yes |
| Fetch-stage unexpected exception | 198–202 → `_internal_error_500` | (500, `internal_error`) | yes |
| `no_match` result | 212–225 | (404, `no_match`) | yes |
| Rebuilt-profile contract error | 243–255 | (500, `internal_contract_error`) | yes |
| Rebuilt rule_evaluation contract error | 275–287 | (500, `internal_contract_error`) | yes |
| 200 document (validated) | 289 | (200, None) | yes |
| Build-stage unexpected exception | 290–295 → `_internal_error_500` | (500, `internal_error`) | yes |

Derived emitted set (excluding the generic disabled-flag 404, exactly as the scenario
route excludes its own):
`{(200,None),(422,validation_error),(404,no_match),(502,schema_drift),(503,rate_limited),(503,source_unavailable),(504,timeout),(500,internal_error),(500,internal_contract_error)}`
— identical to `scenario.STATUS_STATE_MATRIX` (Appendix D). The executable confirmation
is `test_as5_matrix_equals_rule_evaluation_route_emitted_set` (Appendix A, lines 551–633).

## Appendix D — Scenario route matrix + error mappers (`scenario.py`, allowed path)

**`services/api/app/api/v1/scenario.py` lines 96–157** (the single source of truth +
the two generic-500 mappers; the disabled-flag `_not_found` is the generic 404):

```python
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # scenario document (validated before send)
        (422, "validation_error"),  # malformed BBL, no connector call
        (404, "no_match"),  # valid BBL, no PLUTO record (a result)
        (502, "schema_drift"),  # dataset contract breakage
        (503, "rate_limited"),  # SODA throttling after retry budget
        (503, "source_unavailable"),  # SODA outage after retry budget
        (504, "timeout"),  # SODA timeout after retry budget
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # a built payload failed its contract
    }
)


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. ..."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. ..."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_contract_error_500(correlation_id: str) -> JSONResponse:
    """Documented typed 500 for a built payload ... that FAILED canonical-schema
    validation before send. ..."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "an internal document failed canonical-contract validation and "
                "was not sent; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )
```
