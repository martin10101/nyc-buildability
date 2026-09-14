# M5-T025 G0 contract-readiness record (administrative; orchestrator)

Date: 2026-09-14 (UTC). D-056 owner work order (live-walkthrough findings), executed per
D-056-R005 as ONE hand-conducted packet parallel to the D-053 loop's M4-T020 — allowed_paths
fully disjoint (apps/web vs services/api + report files; D-046 ceiling 2/3 writers).

- **Requirement identifiers**: D-056:R001 (safe outbound source links, both provenance
  surfaces, constant-prefix + validated dataset-id, reflected strings never become hrefs),
  R002 (lot-outline visibility root-cause/fix + clear initial framing), R003 (zoom
  controls); D-046:R001/R002 (parallel discipline); D-040:R001 (lot-outline increment —
  the map edits sit inside the scoped release; MapLibre per the 3d-ui technical rules).
  `evaluate_task_refs` ok=true — applicable == cited across all three directives
  (missing/invalid/unresolved empty). Registry appends with same-commit digest resyncs
  (c14): D-046 4536a16c→5b564d34, D-040 d672035d→dbc2c294; D-056 bound M5-T025 at capture.
- **Design boundaries pinned**: link construction ONLY constant `https://data.cityofnewyork.us/d/`
  + strictly validated dataset-id token (ZoLa-link precedent, G5 F-1); honest absence
  preserved on invalid/absent id; `request_url` never an href. Lot-outline fix must name a
  concrete root cause with evidence (root-cause theater is a named risk — a framing-only
  change does not explain a fully invisible outline); display-only discipline unchanged
  (geometry verbatim, zero measurement); all six typed non-map fallback branches
  behavior-identical. Zoom via already-admitted maplibre-gl NavigationControl — zero new
  dependencies (§G; package.json/lockfiles forbidden paths).
- **Scope**: 9 allowed files (3 components, 1 new lib + its new test, 3 existing test
  files, producer report). New files + report seeded this commit (content-identity rule).
  Transport/client contract modules, app shell, packages, services/api all forbidden.
- **Scenarios**: S1–S4 (links both surfaces + negative reflected-string test; root-caused
  visible outline + framing; zoom controls with fallbacks unchanged; scope + regression
  with CI as executable authority — thin client).
- **Gates**: G0/G3/G4; reviewers code-reviewer (G3: root-cause coherence + link-safety) +
  qa-engineer (G4: test adequacy incl. negatives), both ≠ producer frontend-engineer.
- **Producer model (D-047-R001 deviation recorded)**: claude-sonnet-5 via dispatch model
  override (frontend-engineer agent-file flip remains an owner settings item).
- **Deploy note (D-056-R006)**: auto-deploy OFF on the owner's hand-created web service —
  after acceptance + push, the OWNER clicks Manual Deploy and refreshes; returned at seam.

Verdict: **PASS** — packet claimable.
