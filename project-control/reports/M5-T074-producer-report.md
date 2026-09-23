# M5-T074 producer report — DB-045(c) outline-bridge (500, internal_error) server-branch proof

**Task:** M5-T074 (test-only; producer qa-engineer; G4 → backend-engineer).
**Directive:** D-084-R003 (lane-3 re-feed). **Closes:** DB-045 item (c) (M5-T065 wave G4-gap2).
**Scope (two paths, additions only):** `services/api/tests/api/test_outline_bridge.py` (test-only)
and this report. **Zero production edits.** **Claim-seam / starting sha:** `419c967a`.

This re-feed shortens the prior prose and instead inlines the COMPLETE test addition plus the
bounded source excerpts a reviewer needs to corroborate reachability, so the whole submission fits
one supervisor packet. Every pre-existing assertion in the test file is byte-unchanged; the two-path
scope is unchanged.

## The complete test addition (verbatim, `test_outline_bridge.py` :709-806)

Appended after the offline-adapter block (section header :697-708). It adds the generic-500
constants, one shared oracle, and four live-500 tests — nothing else in the file is touched.

```python
_GENERIC_500_MESSAGE = "unexpected internal error; see server logs by correlation id"
# The COMPLETE permitted generic-500 body is EXACTLY these three keys (the documented
# _internal_error_500 helper, outline_bridge.py :605-614). Extra detail/type/traceback leaks.
_GENERIC_500_KEYS = frozenset({"state", "message", "correlation_id"})


def _assert_bounded_internal_error(resp) -> dict:
    """AS-1 + AS-3: a documented (500, internal_error) carrying the FIXED generic body and an
    X-Correlation-ID header equal to the body's correlation_id, emitting NO coordinates. Returns
    the parsed body so each caller can add its own AS-2 leak-absence asserts."""
    assert resp.status_code == 500
    assert (500, "internal_error") in OUTLINE_BRIDGE_STATUS_STATE_MATRIX
    body = resp.json()
    assert body["state"] == "internal_error"
    assert body["message"] == _GENERIC_500_MESSAGE
    # The body is EXACTLY the fixed shape: any unexpected detail/type/traceback field is a leak
    # and fails here, hence in all four callers.
    assert set(body) == _GENERIC_500_KEYS
    assert "vertices" not in body  # a 500 never emits bridged coordinates
    assert resp.headers.get("X-Correlation-ID")
    assert body["correlation_id"] == resp.headers["X-Correlation-ID"]
    return body


def test_500_fetch_stage_internal_defect_is_bounded_generic(client):
    # :709-713 - a ring seam raising a NON-RingUnavailable exception is an unexpected internal
    # defect: caught generically, logged by correlation id, mapped to (500, internal_error).
    secret = "fetch-stage-leak-sentinel"  # secretscan:allow leak-absence probe
    resp = client(display=RuntimeError(secret)).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN}
    )
    _assert_bounded_internal_error(resp)
    assert secret not in resp.text  # AS-2: the exception message never leaks
    assert "RuntimeError" not in resp.text  # AS-2: no exception type leaks
    assert "Traceback" not in resp.text  # AS-2: no traceback marker leaks


def test_500_ring_crs_mismatch_display_side_is_bounded_generic(client):
    # :715-717 - the display seam returned a ring in the WRONG crs (an internal contract breach,
    # not a caller error): logged then mapped to the generic 500, emitting no ring detail. No
    # exception is raised on this branch, so the leak-absence probe rides the ring's provenance
    # detail (which the 200 path echoes as source_display_ring) - it must not appear on a 500.
    secret = "display-crs-leak-sentinel"  # secretscan:allow leak-absence probe
    bad_display = ParcelRing(
        points=_DISPLAY_PTS,
        crs="EPSG:2263",  # not the required display CRS EPSG:4326
        source_id="internal-only-src",
        source_detail={"leak_sentinel": secret},
    )
    resp = client(display=bad_display).post(_URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN})
    _assert_bounded_internal_error(resp)
    assert secret not in resp.text  # AS-2: internal ring detail never leaks on a 500
    assert "internal-only-src" not in resp.text  # AS-2: the internal source id never leaks
    assert "Traceback" not in resp.text


def test_500_ring_crs_mismatch_authoritative_side_is_bounded_generic(client):
    # :715-717 - the OTHER half of the same guard: a valid 4326 display ring but an authoritative
    # ring NOT in EPSG:2263 trips the identical internal-error branch.
    secret = "auth-crs-leak-sentinel"  # secretscan:allow leak-absence probe
    bad_auth = ParcelRing(
        points=_AUTH_PTS,
        crs="EPSG:4326",  # not the required authoritative CRS EPSG:2263
        source_id="internal-only-src",
        source_detail={"leak_sentinel": secret},
    )
    resp = client(auth=bad_auth).post(_URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN})
    _assert_bounded_internal_error(resp)
    assert secret not in resp.text
    assert "internal-only-src" not in resp.text
    assert "Traceback" not in resp.text


def test_500_serialization_unsafe_tail_guard_is_bounded_generic(client):
    # :820-824 - the render-parity tail guard. The correspondence fit SUCCEEDS (same geometry as
    # the happy path) but a non-finite value in the source ring's provenance detail makes the
    # assembled document fail strict-JSON (json.dumps allow_nan=False). It fails closed to the
    # typed generic 500, NOT an untyped ASGI 500, and leaks neither the value nor the json type.
    secret = "tail-guard-leak-sentinel"  # secretscan:allow leak-absence probe
    unsafe_display = ParcelRing(
        points=_DISPLAY_PTS,
        crs="EPSG:4326",  # correct CRS -> passes the crs guard and reaches document assembly
        source_id="nyc-dcp-mappluto-lot-outline",
        source_detail={
            "representation": "lot_outline_display",
            "leak_sentinel": secret,
            "nonfinite": float("nan"),  # spread into source_display_ring -> strict-JSON failure
        },
    )
    resp = client(display=unsafe_display).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN}
    )
    _assert_bounded_internal_error(resp)
    assert secret not in resp.text  # AS-2: provenance detail a 200 would echo never leaks
    assert "nan" not in resp.text.lower()  # the non-finite value never reaches the client
    assert "ValueError" not in resp.text  # AS-2: no json exception type leaks
    assert "Traceback" not in resp.text
```

## The existing `client` fixture the four tests reuse (verbatim, `test_outline_bridge.py` :121-151)

Pre-existing (not added by this task). Its `raise_server_exceptions=False` mount is what lets a live
500 be observed as a response, and `_build_app`'s seam raises any Exception instance it is handed —
the mechanism `test_500_fetch_stage_internal_defect_is_bounded_generic` uses to inject a `RuntimeError`.

```python
def _build_app(display, auth) -> FastAPI:
    """A local app with the router mounted and both ring seams overridden. A ParcelRing is
    returned; an Exception instance is raised by the seam (fault injection)."""
    app = FastAPI()
    app.include_router(router)

    def _seam(value):
        def provider(_bbl: str, _cid: str):
            if isinstance(value, Exception):
                raise value
            return value

        return lambda: provider

    app.dependency_overrides[get_display_ring_provider] = _seam(display)
    app.dependency_overrides[get_authoritative_ring_provider] = _seam(auth)
    return app


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")

    def _make(display=None, auth=None):
        app = _build_app(
            display if display is not None else _display_ring(),
            auth if auth is not None else _auth_ring(),
        )
        return TestClient(app, raise_server_exceptions=False)

    return _make
```

## Corroborating production branches (bounded read-only excerpts; no production edit)

Each excerpt is the exact production path the matching test reaches. Anchors are `app/api/v1/outline_bridge.py`.

**:605-614 — the ONE (500, internal_error) builder.** Confirms `_GENERIC_500_MESSAGE` and that
the body is EXACTLY `{state, message, correlation_id}`; adding any field breaks the oracle's `set(body)`.

```python
def _internal_error_500(correlation_id: str) -> JSONResponse:
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )
```

**:700-717 — fetch stage (branch 1) + crs guard (branches 2 & 3).** `RingUnavailable` is caught at
:703 (→ source_unavailable), so a NON-`RingUnavailable` raise falls to `except Exception` :709 → 500.
After a successful fetch, either ring in the wrong CRS short-circuits at :715 with NO exception raised.

```python
    try:
        display = display_ring(normalized.canonical, correlation_id)
        authoritative = authoritative_ring(normalized.canonical, correlation_id)
    except RingUnavailable as exc:
        logger.warning(
            "outline_bridge source_unavailable source_id=%s correlation_id=%s",
            exc.source_id, correlation_id,
        )
        return _source_unavailable(exc.message, exc.source_id, correlation_id)
    except Exception:
        logger.error(
            "outline_bridge unexpected_error stage=fetch correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    if display.crs != "EPSG:4326" or authoritative.crs != "EPSG:2263":
        logger.error("outline_bridge ring_crs_mismatch correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
```

**:783 + :617-622 + :820-824 — provenance spread then the render-parity tail guard (branch 4).** The
display ring's `source_detail` is spread into `source_display_ring`, so a planted `float("nan")`
reaches document assembly; `_assert_json_safe` then fails strict-JSON and is caught → typed 500.

```python
    display_identity = {"crs": display.crs, "source_id": display.source_id, **display.source_detail}
    #   ... document assembled with "source_display_ring": display_identity ...
    try:
        _assert_json_safe(document)          # :617-622  json.dumps(document, allow_nan=False)
    except Exception:
        logger.error("outline_bridge serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
```

## Acceptance-scenario coverage (one line each)

- **AS-1 (live 500 rows):** all three documented branches driven live (fetch-stage internal raise;
  ring_crs_mismatch ×2 sides; tail guard) → status 500, state `internal_error`, fixed message, matrix
  membership, exact `{state,message,correlation_id}` shape. Reachability [OBSERVED] against the source
  excerpts above; the live pass/fail is [UNVERIFIED — routed to harvest].
- **AS-2 (leak absence):** the oracle's `set(body)` exact-shape check is the primary leak gate; each
  test additionally asserts its `# secretscan:allow` sentinel, and where an exception is raised
  (fetch stage) the type name (`RuntimeError`) and `Traceback` are absent. The crs branches raise no
  exception, so their sentinel rides ring provenance (`internal-only-src` / `leak_sentinel`); the tail
  guard also asserts `nan` and `ValueError` never reach the client.
- **AS-3 (correlation):** `X-Correlation-ID` present and equal to `body["correlation_id"]` on every
  injected 500 (asserted in the shared oracle). [UNVERIFIED — routed to harvest].
- **AS-4 (no scope creep):** [OBSERVED] `git status --porcelain` shows exactly the two allowed paths:
  ` M project-control/reports/M5-T074-producer-report.md` and
  ` M services/api/tests/api/test_outline_bridge.py`. Zero production edits; ruff-clean at repo-root
  scope and modularity PASS (both OBSERVED, below); the full scoped suite is [UNVERIFIED — routed to harvest].

## Evidence status (documented commands, re-run 2026-09-23 at head `419c967a`)

The AUTHORITATIVE validation is the orchestrator harvest with cwd `services/api`, IN THIS ORDER —
(1) `python -m ruff check .` then (2) `python -m pytest tests/api/test_outline_bridge.py -q` — with the
outcomes bound to the reviewed file contents. Those api-cwd rows stay **[UNVERIFIED]** and the task
stays **pending** until that harvest lands. The documented commands runnable at the broker's
worktree-root cwd were run EXACTLY as documented, with the OBSERVED outcomes below.

- **ruff (`python -m ruff check .`, repo-root scope)** — [OBSERVED] exit 1, `Found 45 errors`
  (`[*] 21 fixable`). Every finding is in `project-control/reports/.../doctor_proof.py` or `tools/**`;
  ruff sorts by path (`project-control` < `services` < `tools`) and the stream steps DIRECTLY from the
  `project-control/**` block into the `tools/**` block with NO `services/**` finding between them (the
  only output truncation falls entirely inside the `tools/**` tail — both truncation boundaries are
  `tools/**` files). So the `services/**` sort region is fully covered and empty: the edited
  `services/api/tests/api/test_outline_bridge.py` is ruff-clean at repo-root scope. The authoritative
  `services/api`-cwd ruff is routed to harvest, [PREDICTED] clean (added lines mirror the T068 style
  already ruff-clean in api CI; each `# secretscan:allow` sentinel stays under the 100-char limit).
- **modularity (`python tools/modularity_check.py --check`, repo root)** — [OBSERVED]
  `selected 475 files; failures 0; warnings 22` → PASS. The edited test file is NOT flagged;
  `outline_bridge.py`'s `review_signal` warning is the pre-existing production standing watch, untouched
  by this test-only change.
- **scoped pytest (`python -m pytest tests/api/test_outline_bridge.py -q`)** — NOT run here.
  The broker runs documented commands from the worktree root, where this relative path fails collection
  with `No module named 'app'` (the known root-cwd artifact recorded for T067/T069). Repeating that
  failure is not validation, and `cd services/api && …` is a broker workaround; both are declined.
  Deferred to the harvest at cwd `services/api`. **[UNVERIFIED].**
- **digest binding:** LF-normalized blob SHAs of the two revised files are computed by the orchestrator
  at the harvest/commit seam (a raw digest on this CRLF checkout would mislead; a hashing command is
  non-documented). Routed to harvest.

## For the gate

G4 reviewer (backend-engineer): run `python -m pytest tests/api/test_outline_bridge.py -q` from
`services/api` (the deferred harvest) to elevate the AS-1/AS-3 rows to [OBSERVED], and — per the
DB-046 precedent — confirm leak-absence with an independent body-widening mutant: adding any field to
`_internal_error_500` breaks `set(body) == {"state","message","correlation_id"}` in all four tests.
The task remains pending until the harvest and gates PASS.
