"""Acceptance pack for POST /api/v1/proposal-validation (task M5-T053, D-076 phase
B3-scaffold slice 1) and the DB-034(a)/(b) input gate it calls.

Fully OFFLINE and deterministic: the route takes only the request body (an editor-authored
``proposed_massing`` block) and reaches the accepted validator through the gate; no test
touches the network. The route is feature-flag gated OFF by default (reuses
``INTERNAL_RULE_EVAL_ENABLED``), mirroring the sibling internal routes.

Coverage (AS-1..AS-8):
- AS-1 global vertex budget: at-budget accepted, one-over refused typed, and a many-levels
  probe the per-outline B0 ceilings alone would admit, refused BEFORE any quadratic work.
- AS-2 string ceilings at the exact boundary per field + bounded-repr on an attacker-length
  wall id (never echoed unbounded).
- AS-3 route discipline: oversized body -> 413 by BOUNDED STREAMING (a chunked /
  no-Content-Length body is refused the instant the aggregate crosses the ceiling, before the
  tail is drained or JSON is parsed; a declared Content-Length is an early fast path only, not
  the sole enforcement); NaN/Infinity/malformed/empty/non-object body -> typed 422; no stack
  trace / path / internal string in any response.
- AS-4 acceptance echo: block digest + the literal kind 'proposed', NO derived value.
- AS-5 B0 fixture passthrough: the committed valid proposal blocks accepted; the
  semantically_invalid geometry fixtures refused at the SAME field the B0 tests pin.
- AS-6 monotone gate: the gate refuses whenever the accepted validator refuses (same field).
- AS-7 purity + disjointness: the gate imports the validator read-only, delegates a defect it
  does not own, and does not mutate the block.
- AS-8 the documented (status, state) matrix.
"""

from __future__ import annotations

import asyncio
import copy
import json
import math
from pathlib import Path

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.api.v1.proposal_validation import (
    MAX_BODY_BYTES,
    PROPOSAL_VALIDATION_STATUS_STATE_MATRIX,
    _declared_content_length,
    _read_body_within_ceiling,
    post_proposal_validation,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.main import app
from app.scenario.proposal import ProposedMassingError, validate_proposed_massing
from app.scenario.proposal_input_gate import (
    MAX_STRING_LEN,
    MAX_TOTAL_VERTICES,
    ProposedMassingInputError,
    validate_proposed_massing_input,
)

_URL = "/api/v1/proposal-validation"
_JSON_HEADERS = {"content-type": "application/json"}

# A base X/Y comfortably inside the NYC EPSG:2263 unit-sanity bounds (mirrors the B0 pack).
_X0 = 1000000.0
_Y0 = 200000.0


# ---------------------------------------------------------------------------
# Block builders (mirror the accepted B0 unit pack so the shapes stay in step).
# ---------------------------------------------------------------------------
def _valid_block() -> dict:
    """A minimal, fully-valid proposed_massing block (fresh copy each call)."""
    return {
        "outline": {
            "srid": 2263,
            "vertices": [
                [_X0, _Y0],
                [_X0 + 100.0, _Y0],
                [_X0 + 100.0, _Y0 + 80.0],
                [_X0, _Y0 + 80.0],
                [_X0, _Y0],
            ],
        },
        "levels": [
            {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0},
            {"level_index": 1, "floor_count": 3, "floor_to_floor_ft": 10.5},
        ],
        "exterior_walls": [
            {"id": "south", "start_vertex_index": 0, "end_vertex_index": 1},
            {"id": "east", "start_vertex_index": 1, "end_vertex_index": 2},
        ],
        "provenance": {
            "author": "architect@example.com",
            "kind": "proposed",
            "editor_version": "proposal-editor/0.1.0",
            "parent_scenario_id": None,
        },
    }


def _convex_ring(n_distinct: int) -> list[list[float]]:
    """An explicitly-closed convex (hence simple) ring of ``n_distinct`` distinct vertices on
    a small circle inside the NYC bounds, plus the repeated closing vertex."""
    cx, cy, r = _X0, _Y0, 50.0
    pts = [
        [cx + r * math.cos(2.0 * math.pi * k / n_distinct),
         cy + r * math.sin(2.0 * math.pi * k / n_distinct)]
        for k in range(n_distinct)
    ]
    pts.append([pts[0][0], pts[0][1]])
    return pts


def _outline(n_positions: int) -> dict:
    """A valid closed EPSG:2263 outline with exactly ``n_positions`` positions
    (``n_positions - 1`` distinct vertices plus the closing duplicate)."""
    return {"srid": 2263, "vertices": _convex_ring(n_positions - 1)}


def _leveled_block(level_outline_positions: list[int]) -> dict:
    """A valid block whose geometry cost is spread over many SMALL per-level outlines, so the
    summed vertex budget can be exercised without an expensive single outline. The base is a
    small square (5 positions); one level per entry carries a per-level outline of that many
    positions. Walls are empty (accepted by the validator)."""
    block = _valid_block()
    block["outline"] = {
        "srid": 2263,
        "vertices": [
            [_X0, _Y0],
            [_X0 + 40.0, _Y0],
            [_X0 + 40.0, _Y0 + 40.0],
            [_X0, _Y0 + 40.0],
            [_X0, _Y0],
        ],
    }
    block["exterior_walls"] = []
    block["levels"] = [
        {
            "level_index": i,
            "floor_count": 1,
            "floor_to_floor_ft": 10.0,
            "outline": _outline(positions),
        }
        for i, positions in enumerate(level_outline_positions)
    ]
    return block


def _summed_positions(block: dict) -> int:
    """The gate's global count, reproduced for the boundary assertions: base outline + every
    present per-level outline."""
    total = len(block["outline"]["vertices"])
    for level in block["levels"]:
        outline = level.get("outline")
        if outline:
            total += len(outline["vertices"])
    return total


# ---------------------------------------------------------------------------
# Committed B0 fixtures (AS-5). Found by walking upward so the suite is depth-robust.
# ---------------------------------------------------------------------------
def _find_fixtures_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "packages" / "contracts" / "fixtures"
        if candidate.is_dir():
            return candidate
    raise RuntimeError("contracts fixtures directory not found")


_FIXTURES = _find_fixtures_root()
_VALID_FIXTURES = [
    "valid/scenario/proposed_massing_preliminary.json",
    "valid/scenario/proposed_massing_multilevel.json",
]
_SEMANTIC_INVALID_FIXTURES = [
    "semantically_invalid/scenario/proposed_massing_open_ring.json",
    "semantically_invalid/scenario/proposed_massing_self_intersecting.json",
]


def _load_proposed_massing(rel: str) -> dict:
    document = json.loads((_FIXTURES / rel).read_text(encoding="utf-8"))
    return document["proposed_massing"]


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------
def _enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Flag gate / posture (AS-3 posture)
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404_no_leak(client):
    resp = client.post(_URL, json=_valid_block())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_route_absent_from_openapi(client):
    schema = app.openapi()
    assert _URL not in schema.get("paths", {})


# ---------------------------------------------------------------------------
# AS-4: acceptance echo (block digest + literal kind, NO derived value)
# ---------------------------------------------------------------------------
def test_valid_block_accepted_echo(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_valid_block())
    assert resp.status_code == 200
    assert resp.headers["X-Correlation-ID"]
    body = resp.json()
    assert set(body) == {"result", "kind", "block_digest", "correlation_id"}
    assert body["result"] == "accepted"
    assert body["kind"] == "proposed"
    assert body["block_digest"].startswith("sha256:")
    assert len(body["block_digest"]) == len("sha256:") + 64


def test_acceptance_echo_carries_no_derived_value(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_valid_block())
    blob = json.dumps(resp.json()).lower()
    for vocab in (
        "far", "area", "coverage", "height", "allowance", "floor_area",
        "envelope", "buildable", "sq_ft",
    ):
        assert vocab not in blob


def test_digest_is_stable_for_the_same_block(client, monkeypatch):
    _enable_flag(monkeypatch)
    first = client.post(_URL, json=_valid_block()).json()["block_digest"]
    second = client.post(_URL, json=_valid_block()).json()["block_digest"]
    assert first == second


# ---------------------------------------------------------------------------
# AS-1: global vertex budget (the G5-A1 closure)
# ---------------------------------------------------------------------------
def test_global_budget_at_budget_accepted(client, monkeypatch):
    _enable_flag(monkeypatch)
    block = _leveled_block([45] * 111)  # 5 + 111*45 = 5000 positions
    assert _summed_positions(block) == MAX_TOTAL_VERTICES
    resp = client.post(_URL, json=block)
    assert resp.status_code == 200, resp.json()
    assert resp.json()["result"] == "accepted"


def test_global_budget_one_over_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    block = _leveled_block([45] * 110 + [46])  # 5 + 110*45 + 46 = 5001 positions
    assert _summed_positions(block) == MAX_TOTAL_VERTICES + 1
    resp = client.post(_URL, json=block)
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "validation_error"
    assert body["field"] == "proposed_massing"
    assert "MAX_TOTAL_VERTICES" in body["message"]


def test_many_levels_probe_refused_before_quadratic_work_gate_level():
    # 500 per-level outlines of 50 positions each: every outline < MAX_OUTLINE_VERTICES and
    # 500 == MAX_LEVELS, so the B0 per-outline / per-level ceilings ALONE would admit this;
    # the SUM (25005) blows the global budget. The gate raises its OWN input-gate type,
    # proving it refused BEFORE delegating to the quadratic simplicity test.
    block = _leveled_block([50] * 500)
    assert _summed_positions(block) > MAX_TOTAL_VERTICES
    with pytest.raises(ProposedMassingInputError) as exc:
        validate_proposed_massing_input(block)
    assert exc.value.field == "proposed_massing"


def test_many_levels_probe_refused_via_route(client, monkeypatch):
    _enable_flag(monkeypatch)
    block = _leveled_block([50] * 120)  # 6005 positions; under the body byte cap
    assert _summed_positions(block) > MAX_TOTAL_VERTICES
    resp = client.post(_URL, json=block)
    assert resp.status_code == 422
    assert resp.json()["field"] == "proposed_massing"


# ---------------------------------------------------------------------------
# AS-2: string ceilings at the exact boundary + bounded-repr (the G5-A2 closure)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("mutate", "field"),
    [
        (
            lambda b, v: b["provenance"].__setitem__("author", v),
            "proposed_massing.provenance.author",
        ),
        (
            lambda b, v: b["provenance"].__setitem__("editor_version", v),
            "proposed_massing.provenance.editor_version",
        ),
        (
            lambda b, v: b["provenance"].__setitem__("parent_scenario_id", v),
            "proposed_massing.provenance.parent_scenario_id",
        ),
        (
            lambda b, v: b["exterior_walls"][0].__setitem__("id", v),
            "proposed_massing.exterior_walls[0].id",
        ),
    ],
)
def test_string_ceiling_exact_boundary(client, monkeypatch, mutate, field):
    _enable_flag(monkeypatch)
    at_boundary = _valid_block()
    mutate(at_boundary, "x" * MAX_STRING_LEN)
    assert client.post(_URL, json=at_boundary).status_code == 200

    over = _valid_block()
    mutate(over, "x" * (MAX_STRING_LEN + 1))
    resp = client.post(_URL, json=over)
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "validation_error"
    assert body["field"] == field
    assert "MAX_STRING_LEN" in body["message"]


def test_attacker_length_wall_id_uses_bounded_repr(client, monkeypatch):
    _enable_flag(monkeypatch)
    attacker = "z" * 2000
    block = _valid_block()
    block["exterior_walls"][0]["id"] = attacker
    resp = client.post(_URL, json=block)
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing.exterior_walls[0].id"
    message = body["message"]
    # The full attacker value is NEVER echoed; only a bounded-repr with a truncation marker.
    assert attacker not in message
    assert "z" * 100 not in message
    assert "truncated" in message
    assert len(message) <= 512


# ---------------------------------------------------------------------------
# AS-3: route discipline
# ---------------------------------------------------------------------------
def test_oversized_body_is_413_before_parse(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(
        _URL, content=b" " * (MAX_BODY_BYTES + 1), headers=_JSON_HEADERS
    )
    assert resp.status_code == 413
    assert resp.json()["state"] == "payload_too_large"
    assert resp.headers["X-Correlation-ID"]


# ---------------------------------------------------------------------------
# AS-3 (bounded streaming): the size ceiling is enforced by chunk-by-chunk accumulation, NOT
# by the Content-Length header alone. Driven through the REAL route function with a genuine
# Starlette Request over an ASGI receive callable that counts how many chunks it is asked for,
# so "refused before the remaining stream is consumed or JSON is parsed" is a proven fact, not
# a claim. No network, no pytest-asyncio (asyncio.run drives the coroutine).
# ---------------------------------------------------------------------------
def _asgi_receive(chunks: list[bytes], counter: dict[str, int]):
    """An ASGI ``receive`` yielding ``chunks`` one per call (counting each pull) then a
    terminal empty body, so a real ``Request`` can drive the route's bounded streaming."""
    queue = list(chunks)

    async def receive() -> dict:
        counter["pulls"] += 1
        if queue:
            body = queue.pop(0)
            return {"type": "http.request", "body": body, "more_body": bool(queue)}
        return {"type": "http.request", "body": b"", "more_body": False}

    return receive


def _streaming_request(
    chunks: list[bytes], counter: dict[str, int], *, headers: dict[str, str] | None = None
) -> Request:
    header_pairs = [(b"content-type", b"application/json")]
    for name, value in (headers or {}).items():
        header_pairs.append((name.encode("latin-1"), value.encode("latin-1")))
    scope = {
        "type": "http",
        "method": "POST",
        "path": _URL,
        "headers": header_pairs,
        "query_string": b"",
    }
    return Request(scope, _asgi_receive(chunks, counter))


def test_streamed_body_over_ceiling_refused_before_draining_or_parsing(monkeypatch):
    # A chunked / NO-Content-Length oversized body. The header is absent, so ONLY the bounded
    # stream accumulation can refuse it. 16 KiB chunks of 'x' are not valid JSON, so a 413
    # (never a 422) proves the parser was never reached; a pull count below the body's chunk
    # count proves the tail was never drained and the whole body was never buffered.
    _enable_flag(monkeypatch)
    chunk = b"x" * 16384
    total_chunks = (MAX_BODY_BYTES // len(chunk)) + 6  # comfortably over the ceiling
    counter = {"pulls": 0}
    request = _streaming_request([chunk] * total_chunks, counter)  # no content-length header

    resp = asyncio.run(post_proposal_validation(request))

    assert resp.status_code == 413
    assert json.loads(bytes(resp.body))["state"] == "payload_too_large"
    assert resp.headers["X-Correlation-ID"]
    assert 0 < counter["pulls"] < total_chunks


def test_declared_content_length_over_ceiling_is_413_without_touching_stream(monkeypatch):
    # The Content-Length fast path: an over-ceiling declared length is refused immediately,
    # WITHOUT reading the body stream (the receive callable is never pulled).
    _enable_flag(monkeypatch)
    counter = {"pulls": 0}
    request = _streaming_request(
        [b"x" * 16384],
        counter,
        headers={"content-length": str(MAX_BODY_BYTES + 1)},
    )
    resp = asyncio.run(post_proposal_validation(request))
    assert resp.status_code == 413
    assert json.loads(bytes(resp.body))["state"] == "payload_too_large"
    assert counter["pulls"] == 0


@pytest.mark.parametrize(
    ("total", "expect_too_large"),
    [(MAX_BODY_BYTES, False), (MAX_BODY_BYTES + 1, True)],
)
def test_read_body_within_ceiling_boundary(total, expect_too_large):
    # The accumulator accepts a body of EXACTLY MAX_BODY_BYTES and refuses one byte over,
    # spread across two chunks so the running-total check (not a single-chunk check) decides.
    head = total - 1

    async def _stream():
        yield b"a" * head
        yield b"b"
        yield b""  # terminal empty chunk, skipped

    raw, too_large = asyncio.run(_read_body_within_ceiling(_stream(), MAX_BODY_BYTES))
    assert too_large is expect_too_large
    if too_large:
        assert raw == b""  # empty on refusal: nothing to hand to the parser
    else:
        assert len(raw) == total


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (None, None),          # absent -> stream is the only enforcement
        ("0", 0),
        (str(MAX_BODY_BYTES + 1), MAX_BODY_BYTES + 1),
        ("not-a-number", None),  # malformed -> ignored, stream decides
        ("-5", None),            # negative -> ignored, stream decides
    ],
)
def test_declared_content_length_parsing(header, expected):
    counter = {"pulls": 0}
    headers = {} if header is None else {"content-length": header}
    request = _streaming_request([b""], counter, headers=headers)
    assert _declared_content_length(request) == expected


def test_malformed_json_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, content=b"{ not json", headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_empty_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, content=b"", headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_non_object_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=[1, 2, 3])
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_nan_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    raw = b'{"outline": {"srid": 2263, "vertices": [[NaN, 200000.0]]}}'
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_infinity_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    raw = b'{"outline": {"srid": 2263, "vertices": [[Infinity, 200000.0]]}}'
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_refusal_leaks_no_server_internals(client, monkeypatch):
    _enable_flag(monkeypatch)
    block = _valid_block()
    block["outline"]["srid"] = 4326  # a typed semantic refusal from the validator
    resp = client.post(_URL, json=block)
    assert resp.status_code == 422
    body = resp.json()
    assert set(body) <= {"state", "message", "correlation_id", "field"}
    assert body["field"] == "proposed_massing.outline.srid"
    blob = json.dumps(body).lower()
    for bad in ("traceback", 'file "', "site-packages", "/services/api", "\\services\\api"):
        assert bad not in blob


# ---------------------------------------------------------------------------
# AS-5: B0 fixture passthrough
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rel", _VALID_FIXTURES)
def test_b0_valid_fixture_accepted(client, monkeypatch, rel):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_load_proposed_massing(rel))
    assert resp.status_code == 200, resp.json()
    assert resp.json()["result"] == "accepted"


@pytest.mark.parametrize("rel", _SEMANTIC_INVALID_FIXTURES)
def test_b0_semantically_invalid_fixture_refused_same_field(client, monkeypatch, rel):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_load_proposed_massing(rel))
    assert resp.status_code == 422
    # Both B0 geometry fixtures are pinned at the outline by the B0 unit pack.
    assert resp.json()["field"] == "proposed_massing.outline"


# ---------------------------------------------------------------------------
# AS-6: monotone gate (refuses whenever the accepted validator refuses; same field)
# ---------------------------------------------------------------------------
def _b0_refusal_cases() -> dict[str, tuple[dict, str]]:
    cases: dict[str, tuple[dict, str]] = {}

    wrong_srid = _valid_block()
    wrong_srid["outline"]["srid"] = 4326
    cases["wrong_srid"] = (wrong_srid, "proposed_massing.outline.srid")

    open_ring = _valid_block()
    open_ring["outline"]["vertices"] = open_ring["outline"]["vertices"][:-1]
    cases["open_ring"] = (open_ring, "proposed_massing.outline")

    bad_kind = _valid_block()
    bad_kind["provenance"]["kind"] = "record"
    cases["bad_kind"] = (bad_kind, "proposed_massing.provenance.kind")

    dup_wall = _valid_block()
    dup_wall["exterior_walls"][1]["id"] = "south"
    cases["dup_wall"] = (dup_wall, "proposed_massing.exterior_walls[1].id")

    neg_height = _valid_block()
    neg_height["levels"][0]["floor_to_floor_ft"] = -1.0
    cases["neg_height"] = (neg_height, "proposed_massing.levels[0].floor_to_floor_ft")

    return cases


@pytest.mark.parametrize("name", list(_b0_refusal_cases()))
def test_gate_refuses_whenever_validator_refuses(name):
    block, expected_field = _b0_refusal_cases()[name]
    with pytest.raises(ProposedMassingError) as validator_exc:
        validate_proposed_massing(copy.deepcopy(block))
    with pytest.raises(ProposedMassingError) as gate_exc:
        validate_proposed_massing_input(copy.deepcopy(block))
    assert gate_exc.value.field == validator_exc.value.field == expected_field


# ---------------------------------------------------------------------------
# AS-7: purity + disjointness (the gate wraps the validator read-only)
# ---------------------------------------------------------------------------
def test_gate_accepts_valid_block_without_mutation():
    block = _valid_block()
    snapshot = copy.deepcopy(block)
    assert validate_proposed_massing_input(block) is None
    assert block == snapshot


def test_gate_delegates_a_defect_it_does_not_own():
    # The gate has no geometry check, so a bowtie must reach the accepted validator and earn
    # its typed field error verbatim.
    block = _valid_block()
    block["outline"]["vertices"] = [
        [_X0, _Y0],
        [_X0 + 10.0, _Y0 + 10.0],
        [_X0 + 10.0, _Y0],
        [_X0, _Y0 + 10.0],
        [_X0, _Y0],
    ]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing_input(block)
    assert exc.value.field == "proposed_massing.outline"
    assert "self-intersecting" in str(exc.value)


def test_input_error_is_a_validator_error_subclass():
    assert issubclass(ProposedMassingInputError, ProposedMassingError)


# ---------------------------------------------------------------------------
# AS-8: the documented (status, state) matrix
# ---------------------------------------------------------------------------
def test_status_state_matrix_is_the_documented_set():
    assert PROPOSAL_VALIDATION_STATUS_STATE_MATRIX == frozenset(
        {
            (200, None),
            (404, None),
            (413, "payload_too_large"),
            (422, "validation_error"),
            (500, "internal_error"),
        }
    )


# ---------------------------------------------------------------------------
# M5-T057 SCOPE 2 - T053 route residual closures (four recorded branches).
# ---------------------------------------------------------------------------
_CHECKS_URL = "/api/v1/proposal-checks"


def test_residual_a_400_char_message_cap_truncation_branch(client, monkeypatch):
    """(a) The 400-char refusal-message cap (`_bounded_message`) truncation branch. A 2-element
    vertex whose first element is a >400-char string is NOT a wall id / provenance string, so it
    passes the DB-034(b) gate ceilings and reaches the accepted B0 validator, which embeds an
    UNCAPPED repr of the bad vertex (>400 chars). The route's message cap must truncate it to the
    exact cap with an explicit marker - the uncapped repr can never reach a client."""
    _enable_flag(monkeypatch)
    attacker = "q" * 600
    block = _valid_block()
    block["outline"]["vertices"][0] = [attacker, _Y0]
    resp = client.post(_URL, json=block)
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing.outline.vertices[0]"
    message = body["message"]
    assert attacker not in message
    assert "q" * 450 not in message  # far more than the 400-char cap is never echoed
    assert "truncated" in message
    # Cap (400) + a short truncation marker naming the true length; comfortably under 500.
    assert 400 < len(message) < 500


def test_residual_b_forced_internal_error_is_bounded_500(client, monkeypatch):
    """(b) The generic 500 path. A forced internal defect inside the validate stage returns the
    typed bounded 500 with NO stack trace / value leak (only a correlation id)."""
    _enable_flag(monkeypatch)

    def _boom(_block):
        raise RuntimeError("boom-with-secret-/services/api/path")

    monkeypatch.setattr(
        "app.api.v1.proposal_validation.validate_proposed_massing_input", _boom
    )
    resp = client.post(_URL, json=_valid_block())
    assert resp.status_code == 500
    body = resp.json()
    assert set(body) == {"state", "message", "correlation_id"}
    assert body["state"] == "internal_error"
    assert body["correlation_id"]
    blob = json.dumps(body).lower()
    for leak in ("boom", "runtimeerror", "traceback", "/services/api", "\\services\\api"):
        assert leak not in blob


def test_residual_c_lone_surrogate_body_refused_typed(client, monkeypatch):
    """(c) The surrogate half of the strict-JSON guard. A body carrying a lone (unpaired)
    surrogate parses via json.loads but is refused by the renderer-parity guard BEFORE it can
    reach the digest or raise mid-response."""
    _enable_flag(monkeypatch)
    raw = b'{"provenance": {"author": "\\ud800"}}'  # a lone high surrogate escape
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "validation_error"
    assert "surrogate" in body["message"]


def test_residual_d_both_routes_share_one_flag_and_off_behaviour(client, monkeypatch):
    """(d) The deliberate shared-flag coupling. Both the validation and the checks routes gate on
    the SAME INTERNAL_RULE_EVAL_ENABLED flag, and their flag-off behaviour is identical: a generic
    404 with no correlation id. The coupling is intentional (the proposal editor is one internal
    flow); this test documents it rather than introducing a second flag."""
    # Flag OFF (fixture default): both routes are a byte-identical generic 404, no leak.
    for url in (_URL, _CHECKS_URL):
        off = client.post(url, json=_valid_block())
        assert off.status_code == 404
        assert off.json() == {"detail": "Not Found"}
        assert "X-Correlation-ID" not in off.headers

    # Flag ON: both routes become reachable (an empty body earns each route's typed 422, i.e.
    # NOT the disabled 404) - the single flag flips both together.
    _enable_flag(monkeypatch)
    for url in (_URL, _CHECKS_URL):
        on = client.post(url, content=b"", headers=_JSON_HEADERS)
        assert on.status_code == 422
        assert on.json()["state"] == "validation_error"
