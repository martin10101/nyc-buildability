# M5-T065 producer report — map-drawing input slice + 4326→2263 correspondence bridge (revised evidence handoff)

Task: D-082-R001/R003 map-drawing input slice — a keyboard-operable outline input over the accepted
read-only lot map, a flag-gated UNMOUNTED server bridge that converts EPSG:4326 vertices to
authoritative EPSG:2263 by affine CORRESPONDENCE (no reprojection math, no new dependency, residual
disclosed), and additive adoption into the accepted numeric draft (manual entry stays the option).

Regime refs: D-082-R001/R003, D-066-R001, D-076-R001/R002, D-077-R002/R003.
Base (contract/claim-seam) sha: `f98924e5c9dc726437e9114108a5b599256208de`.

**Honesty banner (read first).** This handoff distinguishes DEMONSTRATED behavior (§1–§2) from
OUTSTANDING evidence and a real scope gap (§3). One item is load-bearing: the input mechanism built
here is **keyboard/numeric vertex entry over a read-only reference map — NOT click-to-place ON the
map surface.** The packet objective's "click-to-place vertices … over the existing `LotOutlineMap`"
is **not** delivered and, as analyzed in §3.1, **cannot** be delivered inside this packet's allowed
paths. It is surfaced for an owner/orchestrator decision, not claimed as done. Web behavior is
unverified here (thin client); it proves ONLY in CI at the pushed head.

## Digest binding

Change surface vs the base sha above — exactly the 12 allowed paths, no forbidden path
(`git status --porcelain`, `git diff --numstat HEAD`):

| File | +add / −del | Role |
|---|---|---|
| `services/api/app/api/v1/outline_bridge.py` | 823 / 4 | bridge endpoint + correspondence math |
| `services/api/tests/api/test_outline_bridge.py` | 694 / 1 | endpoint + math tests |
| `apps/web/src/lib/outline-bridge-api.ts` | 558 / 3 | typed client decoder |
| `apps/web/src/lib/__tests__/outline-bridge-api.test.ts` | 256 / 6 | decode-matrix tests |
| `apps/web/src/components/architect/ProposalOutlineDraw.tsx` | 266 / 4 | input UI (keyboard/numeric) |
| `apps/web/src/components/architect/__tests__/proposal-outline-draw.test.tsx` | 157 / 8 | component tests |
| `apps/web/e2e/proposal-editor.spec.ts` | 133 / 0 | AS-4 + AS-5 journeys |
| `apps/web/src/components/architect/ProposalEditor.tsx` | 25 / 9 | adoption wiring |
| `apps/web/src/components/architect/__tests__/proposal-editor.test.tsx` | 60 / 0 | editor adoption tests |
| `apps/web/src/lib/architect/proposal-draft.ts` | 14 / 0 | `adoptOutlineVertices` |
| `apps/web/src/lib/architect/__tests__/proposal-draft.test.ts` | 21 / 0 | adoption unit test |
| `project-control/reports/M5-T065-producer-report.md` | this file | |

Behavior below is anchored to file + line ranges at this working tree. The MATERIAL content identity
is frozen by the orchestrator at submit (the supervisor re-collects and hashes at harvest); these
files are uncommitted at report time (`git hash-object` is not in the permitted command set here).

## §1 Demonstrated behavior (file + line anchors)

### 1a. Input/drawing UI — `ProposalOutlineDraw.tsx`
Honest description of what the component IS: an ordered, keyboard-operable **vertex list** with a
labeled longitude/latitude **number input** per point, composed alongside the accepted `LotOutlineMap`
(rendered read-only in `context` mode, ll.137–143) shown **for reference only** — nothing is measured
from it and there is no map-click handler.
- Add / edit / delete points: `addPoint` ll.91–93, `updatePoint` ll.95–97, `deletePoint` ll.99–107;
  each row has `aria-label`ed lng/lat inputs + a labeled Delete button (ll.156–195).
- Focus-on-delete (DB-043(a) from the start): the delete handler records an intended target as a
  nonce (`pendingFocus`, ll.99–107) and a `useEffect` moves focus AFTER the remove re-render
  (ll.78–89) — never a synchronous `.focus()` on a remounting node (CODING_RULES).
- Convert → adopt: `convert` (ll.112–123) POSTs the drawn 4326 points via the client and, on a
  `bridged` result, calls `onAdopt` with the server's 2263 vertices; refusals adopt nothing.
- Honesty framing (D-076-R002): "Proposed — your sketch, not a city record …" (ll.130–134); the
  success card discloses the residual + correspondence provenance (ll.219–242); refusal surfaces are
  DISTINCT and typed (ll.243–261), keyed by `data-outcome-kind`.
- Convert is gated to ≥3 points client-side (`MIN_DRAWN_VERTICES`, ll.40, 110); the route stays the
  authority.

### 1b. Correspondence algorithm + refusals — `outline_bridge.py`
Three non-overlapping sections (module boundary noted ll.318–332):
- **Connector I/O adapters** (ll.220–315): `_default_display_ring` reads the accepted 4326
  `mappluto_lot_outline` (ll.220–257, single_lot only, else `RingUnavailable`);
  `_default_authoritative_ring` reads the accepted 2263 `mappluto_geometry_arcgis` canonical geometry
  (ll.260–305). Both are injected seams (`Depends`, ll.308–315) so the suite runs offline.
- **Pure affine math** (ll.333–482, no I/O, no FastAPI): `_solve_affine` (ll.378–426) is a centered
  least-squares 6-parameter 2D affine; the centering rationale (4326 ~1e0 vs 2263 ~1e6
  ill-conditioning) is documented ll.383–391 and it returns `None` on (near-)collinear control points
  (ll.410–411). `fit_correspondence` (ll.429–482) searches **both windings and all cyclic offsets**
  (ll.466–473) because the two official layers need not start at the same vertex/wind the same way,
  and returns the best fit + the runner-up's residual as ambiguity evidence.
- **Refusals are typed and DISTINCT** (single source `OUTLINE_BRIDGE_STATUS_STATE_MATRIX`, ll.128–141):
  `invalid_request`(+reason: `not_json`/`not_object`/`non_finite`/`srid_unsupported`/`bbl_invalid`/
  `too_few_vertices`/`over_cap`/`vertex_non_finite`) — parse ll.516–549, endpoint ll.649–696;
  `out_of_neighborhood` (a drawn vertex outside the display bbox expanded by the diagonal margin,
  ll.494–504 / gate ll.719–727); `correspondence_unavailable`(+reason: `too_few_control_points`
  (<4, ll.446–451), `too_many_control_points` (>64), `vertex_count_mismatch`,
  `degenerate_control_points`, **`ambiguous_correspondence`** — the uniqueness gate ll.756–771);
  `residual_too_high` (RMS over the 2.0 ft bound, ll.739–754); `source_unavailable` (connector fault,
  ll.700–708); `payload_too_large` (raw body over ceiling, before parse, ll.641–647);
  `internal_error` (ring-CRS mismatch ll.715–717 / unsafe serialization ll.820–824).
- The trust rule is NECESSARY-NOT-SUFFICIENT and enforced in code: a fit is emitted only with ≥4
  control points AND RMS ≤ 2.0 ft AND a ≥2.0 ft margin over the runner-up alignment; otherwise
  refused, never guessed (ll.729–771). Success maps the drawn vertices through the affine (ll.773–775)
  and returns them with method/alignment/residual/margin/both source-ring identities + disclosure
  (ll.789–819). No CRS library import, no hand-rolled Lambert/CRS math anywhere.

### 1c. Client decoder — `outline-bridge-api.ts`
- Exact (HTTP status, state) matrix mirroring the route verbatim (`DOCUMENTED_PAIRS` ll.228–238;
  `isDocumentedBridgePair` ll.244–246; an undocumented pair → `unexpected_response`, ll.417–424).
- Size-bound-BEFORE-parse: Content-Length must be a plain-digit string within `MAX_RESPONSE_BYTES`,
  else fail-closed `unexpected_response` (ll.394–401).
- 200 bodies are shape-verified and bounded before render; a 200 **missing the correspondence block**
  is a distinct `validation_failure`, never bare coordinates (`boundReport` ll.283–341, esp. 294–296,
  308–310).
- Every reflected string is `boundedText`/`boundedToken`; numbers (the load-bearing residual) pass
  through verbatim (ll.317–338). Distinct refusal decodes ll.439–506; deterministic AT copy
  `announcementForOutlineBridge` ll.520–558; `outlineBridgeOutcomeIsRecoverable` ll.210–219 (refusals
  are results, not retryable faults).

### 1d. Adoption wiring — `proposal-draft.ts`, `ProposalEditor.tsx`
- `adoptOutlineVertices` (proposal-draft.ts ll.266–279): pure/immutable; replaces ONLY the outline
  vertices, leaves levels/walls/lot inputs intact.
- `adoptDrawnOutline` (ProposalEditor.tsx ll.102–114): adopted vertices land in the numeric table as
  if typed, the table stays the authority, and the stale check outcome is cleared so a fresh check
  runs on the adopted shape. Manual entry unchanged.

### 1e. Endpoint boundary justification
- **UNMOUNTED by design** (ll.39–45, decorator `include_in_schema=False` ll.625): the router is NOT
  added to `app.main` in this slice — `services/api/app/main.py` is a forbidden path and is held by
  the live sibling M5-T062 lane. Tests mount it via `TestClient`; production mount rides a later seam.
- **Flag-gated OFF by default**: reuses `INTERNAL_RULE_EVAL_ENABLED` (the sibling internal-route flag);
  when off it returns a generic 404 byte-indistinguishable from an unmounted path (ll.636–637,
  `_not_found` ll.561–564) — no body hint the feature exists.
- Lives under `app/api/v1/` beside the accepted internal `proposal_checks_api` and reuses its vetted
  body-ceiling helpers (`_read_body_within_ceiling`, `MAX_BODY_BYTES`, `_bounded_message`,
  ll.68–74) rather than forking a new parsing path. The vertex cap is imported from the downstream
  route (`ROUTE_MAX_TOTAL_OUTLINE_POSITIONS`, l.104) so a bridged shape can never exceed what the
  check route will accept.

### 1f. Tests (what each proves)
- `test_outline_bridge.py` — 38 tests: correspondence math incl. the ambiguity/symmetry proof, each
  typed refusal, the flag-off 404 sentinel, the UNMOUNTED assertion (absent from `app.main`), and the
  offline production-adapter paths.
- `proposal-outline-draw.test.tsx` — 5 tests: proposed-label + convert-gating (ll.77–86); keyboard
  vertex entry + adoption of exact 2263 vertices + residual disclosure (ll.88–117); **focus-on-delete**
  (ll.119–132); `residual_too_high` refuses distinctly and adopts nothing (ll.134–147);
  `out_of_neighborhood` distinct from a residual refusal (ll.149–158).
- `outline-bridge-api.test.ts` — the full decode matrix (mutation-sensitive).
- `proposal-editor.test.tsx` + `proposal-draft.test.ts` — adoption into the numeric authority.
- `e2e/proposal-editor.spec.ts` AS-4 (ll.282–348) — drives the drawn→bridge→adopt→check loop with
  stubbed bridge responses. **Caveat (see §3.1):** it adds points via the "Add drawn point" button and
  fills lng/lat by `.fill()` (ll.320–330); it exercises **numeric/keyboard vertex ENTRY, not
  click-to-place on the map**.

## §2 Command evidence — EXPLICIT working directories + supervisor exit-code reconciliation

These are MY in-run outcomes; the supervisor re-collects at harvest. The supervisor's reported
**pytest exit 4** and **ruff exit 1** are both **wrong-cwd artifacts of the documented commands**, not
defects in this packet. The two `services/api` commands must run from the `services/api` cwd:

| Documented command | cwd | Result |
|---|---|---|
| `python -m pytest tests/api/test_outline_bridge.py -q` | `services/api` | **38 passed** (exit 0) |
| `python -m pytest tests/api/test_outline_bridge.py -q` | worktree root | **exit 4** — `file or directory not found: tests/api/test_outline_bridge.py` (the path only resolves from `services/api`; this reproduces the supervisor's exit 4) |
| `python -m ruff check .` | `services/api` | **All checks passed!** (exit 0) |
| `python -m ruff check .` | worktree root | **exit 1** — 45 pre-existing findings, ALL under `tools/**` and `project-control/reports/**` (e.g. `tools/project_control.py`, `tools/agent_supervisor/*`, `tools/modularity_check.py`, `project-control/reports/M0-T054-.../doctor_proof.py`); **ZERO in my two `services/api` files**. This reproduces the supervisor's exit 1 and is out of scope — per the rework instruction I did NOT fix unrelated repository lint findings. |
| `python tools/modularity_check.py --check` | worktree root | **failures 0**, 21 warnings; `outline_bridge.py` is a `review_signal` warning (above the warn threshold, under the 1000-SLOC hard cap — one cohesive module, three explicit sections), not a failure. |

Recollection recipe for a reviewer: for the two `services/api` commands, set cwd to `services/api`
first (a bare `cd services/api`, since the broker accepts only the exact documented command string);
run modularity from the worktree root.

## §3 Outstanding evidence and the scope gap

### 3.1 Map click-to-place is NOT implemented and cannot be added in this packet's scope (owner/orchestrator decision)
The packet objective says the architect "draws the building outline directly on the existing
`LotOutlineMap` (click-to-place vertices …)". What is built is keyboard/numeric vertex ENTRY over a
read-only reference map. **No executable journey that places/adjusts vertices ON the map exists, and
none can be added here**, because:
- `LotOutlineMap.tsx` is a **forbidden read-only path** (compose-only). Its public props are only
  `{ bbl, fetchImpl, context }` — it exposes **no** map-click / `onVertexPlace` callback and **no**
  `unproject` accessor, and its map instance (`mapRef`) is private. Drawn map-pixel coordinates
  therefore cannot be captured without editing it.
- Capturing clicks in `ProposalOutlineDraw` without the map's `unproject` would require hand-rolled
  screen-pixel→lng/lat math — barred by the packet's no-client-transform / no-hand-rolled-CRS
  doctrine — and standing up a second interactive map is barred by `.claude/rules/3d-ui-expansion.md`
  (compose the accepted display component; do not build a rendering engine from scratch).

This is a genuine conflict between the objective's "click-to-place" and the forbidden-path constraint
on the only map. It needs an owner/orchestrator decision among:
- (a) scope-release `LotOutlineMap` (or a new sibling) to expose a keyboard-accessible draw seam
  (`onVertexPlace` + `unproject`) and contract the map-interaction work as a dependent task; or
- (b) accept THIS slice as keyboard/numeric vertex entry over a reference map, and correct the
  objective/UI wording to drop "click-to-place"; or
- (c) split map click-to-place into a dependent follow-up task with `LotOutlineMap` in scope.

I did not edit any forbidden path and did not fabricate a map-interaction journey.

### 3.2 Web verification is pending CI
The web specs (component, client, editor, `proposal-draft`, e2e AS-4/AS-5) are authored but NOT run
locally (thin client, CODING_RULES). Web behavior — including the a11y/keyboard journeys — proves ONLY
in CI on the pushed head. No web result is claimed here.

## §4 Preservation / disjointness
Only the 12 allowed paths changed (`git status --porcelain`); no forbidden path touched:
`LotOutlineMap.tsx` (composed, not edited), the held M5-T063 surface, the live M5-T062 surface
(`main.py`, `site_definition/`), `app/connectors/**`, `app/rules/**`, `app/scenario/**`,
`packages/contracts/**` all untouched. The route is UNMOUNTED (test asserts absence from `app.main`).
The accepted numeric editor flow is byte-compatible (drawing is additive).

## §5 Acceptance-scenario coverage (honest)
- **AS-1 (drawing/keyboard/focus/label)** — **PARTIAL.** Keyboard-operable vertex entry, focus-on-delete,
  and proposed-input labeling are demonstrated (`proposal-outline-draw.test.tsx`). The "vertices placed
  by MOUSE … on the map" element is **NOT** met (§3.1).
- **AS-2 (bridge honesty)** — met: typed distinct refusals, flag-off 404, UNMOUNTED, correspondence
  provenance (`test_outline_bridge.py`), pending CI/gate confirmation.
- **AS-3 (no-reprojection doctrine)** — met: zero new dependencies; only the two accepted connector
  rings (read-only); no general CRS math (route imports carry no pyproj/shapely-CRS).
- **AS-4 (adoption + manual)** — met for the ENTRY→bridge→adopt→check loop (unit + AS-4 e2e, stubbed
  bridge), pending CI; note the AS-4 caveat in §1f/§3.1 (numeric entry, not map clicks).
- **AS-5 (decode matrix)** — met: residual vs neighborhood refusals decoded distinctly
  (`outline-bridge-api.test.ts`), pending CI.
- **AS-6 (preservation)** — met: allowed paths only; api ruff + pytest + modularity green from the
  correct cwds (§2); web proof = CI.

## §6 Discovery routing (D-069)
No out-of-scope code changes. Findings for the backlog/reviewer:
1. The `LotOutlineMap` public interface has no map-interaction seam; "click-to-place" needs (a)/(c) in
   §3.1 before it is buildable. (Route to `docs/DISCOVERY_BACKLOG.md`.)
2. A 4-vertex control ring is the minimum where residual carries signal; 4-point quads with affine
   self-symmetry (kites/parallelograms) stay inherently ambiguous — the route correctly refuses them;
   fixture authors must use irregular quads for the happy path.
3. The whole-repo `ruff` scan surfaces 45 pre-existing findings under `tools/**` and
   `project-control/reports/**` (out of this packet's scope) — noted, not touched.

## §7 Next action (orchestrator/owner)
1. Owner/orchestrator decision on §3.1 (a/b/c) — this determines whether the packet is re-scoped,
   split, or unblocked with `LotOutlineMap` released.
2. On the demonstrated slice: harvest the working tree, run gates G0/G2/G3/G4, and push to obtain CI
   proof of the web specs at the pushed head. Not a producer action (ADR-005).
