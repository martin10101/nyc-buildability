---
name: starlette-json-allow-nan-render-trap
description: A non-finite float in a JSONResponse body raises inside the handler (render happens in the constructor, allow_nan=False) -> untyped 500; guard with a pre-render json.dumps(allow_nan=False)
metadata:
  type: feedback
---

Any FastAPI/Starlette route that echoes caller-derived floats can emit a non-finite value
(a huge-but-finite input like `1e300` overflows a shoelace/area/bbox computation to `inf`).
Starlette's `JSONResponse` renders with `allow_nan=False` and — critically — render runs
in the `Response.__init__` CONSTRUCTOR, so the `ValueError("Out of range float values...")`
is raised INSIDE the handler at the `JSONResponse(...)` call, not in middleware. If that call
is the handler's `return` with no try/except, the client gets a bare untyped 500 with no
correlation id.

**Why:** M5-T108 (DXF import) G5 MEDIUM 1 — `1e300` coords passed the reader (each finite) but
overflowed measured dimensions to `inf`; POST /candidates returned a bare Starlette 500.

**How to apply:** Two layers. (1) Value-guard at the source: after computing, check
`math.isfinite` on every numeric field and return a typed refusal (e.g. `coordinate_out_of_range`
-> 422). (2) Defense-in-depth PRE-RENDER guard before every 200 return: trial
`json.dumps(body, ensure_ascii=False, allow_nan=False)` in a try/except; on `ValueError` return
the typed `(500, internal_error)` WITH a correlation id. This is the accepted pattern already in
`services/api/app/api/v1/proposal_validation.py`. Test both: mutate the source guard off (real
overflow reaches the body) to prove the pre-render guard yields a TYPED 500 with a correlation id;
mutate the pre-render guard to no-op to prove a BARE 500 with no correlation id (that flip is the
reddening proof). Use `TestClient(app, raise_server_exceptions=False)` so the bare-500 path is
observable instead of re-raised.

Related: to make a "which item was selected" behavior mutation-testable, extract the selection
into a tiny named seam (e.g. `_select_ring(rings, index)`) so a test can monkeypatch it to
always-index-0 / largest and prove the real code honors the user's assignment. See also
[[socrata-pluto-gotchas]] for other numeric-serialization gotchas in this repo.
