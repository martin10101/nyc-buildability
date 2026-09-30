---
name: cad-export-wiring-seam
description: D-087 CAD/3D export wiring (export_service/route, PKT-D..H) - the glb_writer unwired grep-test, no reusable in-route rate limiter, per-writer refusal shapes, and the single-prism GLB dedupe
metadata:
  type: project
---

Wiring the accepted D-087 writers (dxf_writer / glb_writer / pdf_sheet_writer) into a service or
route (PKT-D and the later PKT-E scene / PKT-F import / PKT-H mount packets).

**Why:** these facts are not derivable from the writers alone and each cost a debug round on M5-T109.

**How to apply:**
- `services/api/tests/cad/test_glb_writer.py::test_as5_not_wired_into_the_app` greps EVERY
  `app/**/*.py` for the SUBSTRING `glb_writer` and asserts none contains it. It goes RED the instant
  any app module names the writer (import style is irrelevant - it's a text grep). It is usually a
  FORBIDDEN path for the wiring producer, so you cannot satisfy it - route a one-line orchestrator
  update (allow the wiring module, or drop the assertion). dxf_writer / pdf_sheet_writer have NO
  equivalent grep test, so only the GLB one breaks.
- There is NO reusable in-route per-caller rate limiter in the repo. Every `rate_limited` state in
  lot_geometry.py / properties.py / connectors is UPSTREAM 429/503 (SODA/ArcGIS retry budgets), not a
  route limiter. DB-061 (i) still requires one at each wiring seam - build a stdlib in-process
  sliding-window limiter (per client-host key, monotonic clock, bounded key set); zero new deps.
- Writer refusal shapes differ and must be reconciled to ONE `{reject_code, detail}`: DXF RAISES
  `DxfWriterError` (`.code`), GLB RAISES `GlbWriterError` (`.code`), PDF RETURNS `SitePlanRefusal`
  (`.reject_code`). The GLB/DXF messages INTERPOLATE the caller name/coordinate (`{name!r}`,
  `{value!r}`) - DB-059 (h): discard `str(exc)` and build detail from the fixed code only. The code
  strings are always fixed enum tokens (safe); PDF SitePlanRefusal.detail is server-field-only (safe).
- Filename safety (plan section 2 MANDATORY, M5-T099 G5 F1): allowlist the token to `[A-Za-z0-9._-]`
  from validated bbl + deterministic generated_at, length-cap, emit BOTH ascii `filename` and RFC
  5987 `filename*=UTF-8''`; DB-065 (a) - when the token allowlists to nothing (or only `._-`) fall
  back to a caller-free default (route passes the correlation id).
- GLB from a stacked massing: build ONE base->roof extrusion (walls + fan-triangulated bottom/top
  caps), NOT per-floor prisms - that satisfies DB-054 (m) coincident-interface-cap dedupe BY
  CONSTRUCTION (assert a 1-floor and an N-floor stack with equal total height give byte-identical
  GLB). Localize positions to the footprint SW-min origin (GLB caps local coords at 100_000 ft;
  EPSG:2263 world eastings are ~1e6). A robust polygon triangulator lives in app/scenario/
  massing_model.py (owned by M5-T106/T107), so fan-triangulate + disclose the simple-polygon
  assumption here.
- DXF and GLB writers are byte-frozen and take NO generated_at/address/bbl; only the PDF writer
  embeds generated_at (title block). Deterministic-no-clock holds for all three regardless.
