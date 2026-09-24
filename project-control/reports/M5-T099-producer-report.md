# M5-T099 producer report — D-087 PLAN-1 (export + 3D-viewer wiring plan)

- Task: M5-T099 (docs only). Producer: cloud-architect (orchestrator-dispatched subagent).
- Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t099`, branch `task/M5-T099-export-viewer-plan`.
- Base / claim seam: `2957e40d` (verified `--show-toplevel` = the wt-m5t099 path; `reset --hard 2957e40d`).
- Deliverables (exactly the two allowed paths): `docs/design/d087-export-and-3d-viewer-plan.md`,
  `project-control/reports/M5-T099-producer-report.md`. No code / test / route / dependency / web change.
- Directives: D-087 (R001,R002,R003,R004,R006,R009), D-083 (R001,R002), D-066 (R001).

## Commands run (explicit cwd + result)

1. `git -C C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t099 rev-parse --show-toplevel`
   → `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t099` [OBSERVED] (correct worktree; not the primary checkout).
2. `git -C .../wt-m5t099 reset --hard 2957e40d` → `HEAD is now at 2957e40d ...` [OBSERVED].
3. `python tools/modularity_check.py --check` (cwd `.../wt-m5t099`) → `selected 488 files; failures 0;
   warnings 26` `EXIT=0` [OBSERVED]. This task adds only two docs files, so no code modularity impact; the
   26 warnings are pre-existing review signals (incl. `sheet_reader.py`, `massing_model.py`,
   `building_footprints_arcgis.py` near ceilings — reflected in the plan as split-before-growth points).
4. `python tools/code_graph/query.py --no-regen impact <path>` for all seven blocks (cwd `.../wt-m5t099`)
   → every one returned `STALE (stale fingerprint): refusing to serve the cached graph` [BLOCKED]. The
   cached graph fingerprint does not match the reset worktree head; `--no-regen` refuses to serve it, and I
   did not regenerate (regen is out of this docs-only scope and would write a cache artifact). Consumers
   were instead verified directly in source (command 5), which is authoritative (graph is advisory,
   D-066-R001).
5. Consumer grep across `services/api` for each block's importers (cwd `.../wt-m5t099`) → the ONLY
   production import of any block is `app/cad/pdf_sheet_writer.py:54  from app.cad.dxf_writer import
   CLAIM_CLASS_WORDS` [OBSERVED]; the other six blocks have zero production importers. Test coverage
   confirmed present for all seven (`tests/cad/`, `tests/drawings/`, `tests/scenario/`,
   `tests/connectors/`). This matches the packet's stated graph fact.
6. Field-name / source_registry verification (cwd `.../wt-m5t099`): the connector uses full FeatureServer
   names (`HEIGHT_ROOF`, `GROUND_ELEVATION`, `CONSTRUCTION_YEAR`, `BASE_BBL`, `MAPPLUTO_BBL`; `:117-121`)
   and rejects the shapefile-truncated names (`:13`) [OBSERVED] — so DB-053 (e) is addressed by the
   accepted M5-T089 connector; no `source_registry` record exists for the connector yet [OBSERVED] —
   confirms DB-058 (g) is deferred to the wiring packet (PKT-C).

## Sources read (read-only)

Packet `M5-T099.json`; D-087 `requirements.json` (R001-R012) + `source-001.md` + `source-002-amendment.md`;
D-083 requirements/source-001 (claim-class vocabulary); `.claude/rules/expansion-agent-dispatch-hold.md`
§2.3; `docs/DISCOVERY_BACKLOG.md` DB-053..DB-062 + the seam-sweep lines 204-222; research notes
`dxf-format-reference-2026-09.md`, `building-footprints-source-2026-09.md`,
`architect-corpus-reader-trial-2026-09.md`, `architect-drawing-corpus-2026-09.md`; the seven accepted
modules + their entry-point docstrings (file:line quoted in the plan); `services/api/app/main.py`
router-mounting block; `app/api/v1/max_envelope_api.py` (unmounted preconditions);
`.claude/rules/backend-api.md`, `frontend-web.md`, `3d-ui-expansion.md`; the six in-flight packets
`M5-T094..M5-T098`, `M5-T100`.

## Per-AS evidence

- **AS-1 (inventory truth) [OBSERVED].** Plan §1 quotes every block's public API, limits and consumers
  with file:line at head `2957e40d` (commands 3-6). §6 maps every open DB-053..DB-062 sub-item to exactly
  one future step, an in-flight packet, a discharge, or `by note`.
- **AS-2 (contracts) [OBSERVED].** Plan §2 (export) and §2.1 (scene) name the flag (reused
  `INTERNAL_RULE_EVAL_ENABLED` + generic-404 sentinel; dedicated default-off flag for the write/import
  path), request bounds, response types + `Content-Disposition` + `X-Correlation-ID`, typed refusals
  (writer codes reconciled), provenance, and the D-083 honesty labels. Security points — size caps, time
  budgets, escaping, server-generated correlation ids, no upstream text in logs — are explicit.
- **AS-3 (viewer) [OBSERVED].** Plan §3 specifies the data path, coordinate frames (2263 ft → local metres
  via the GLB writer's `AXIS_MAPPING` + `1200/3937`), performance limits, a non-visual text alternative,
  print behaviour, and CI-only web testing. §3.1 lays out the `@types/three` decision with BOTH options and
  their trade-offs and explicitly chooses neither (owner's call).
- **AS-4 (packet breakdown) [OBSERVED].** Plan §5 gives an ordered, dependency-correct breakdown; each
  batch's `allowed_paths` are pairwise disjoint at file level; every packet lists its gates and the riders
  it closes; §0.1 accounts for the six in-flight packets and every future packet sequences after the
  in-flight packet that locks its file. Route modules ship UNMOUNTED; `main.py` mounts are isolated and
  serialized.
- **AS-5 (honesty + scope) [OBSERVED].** Plan states the architect-sheet reader reads 0/6 real drawings,
  nothing is wired to a route, and the max-envelope route stays unmounted with its preconditions listed
  (§7), not relaxed. D-083 claim classes are used ("Preliminary development limits" / "Generated building
  option"; never "approved"/"maximum allowed building"/"demonstrated maximum"). Exactly the two allowed
  files are written; no capability that does not exist is claimed.

## DISCOVERIES (D-069 — routed to the orchestrator, not fixed here)

- D1. The code-graph cached fingerprint is STALE against a worktree reset to a prior commit; `query.py
  --no-regen impact` fails closed on every path. When a producer's worktree is reset behind the
  contract-seam graph regen, `--no-regen` graph queries are unusable and consumers must be verified by
  grep. Suggest the dispatch note this for reset-based worktrees (advisory; not a defect in the plan).
- D2. `sheet_interpreter.py` / `sheet_objects.py` / `test_dxf_roundtrip.py` are 1-line placeholder seeds at
  `2957e40d`; `sheet_reader.py` is still 1096 SLOC monolithic and `dxf_writer.py` has no STYLE/VPORT yet —
  i.e. M5-T094/T096/T097 are genuinely in flight (not yet landed). The plan treats them as in-flight, not
  accepted state.
- D3. `app/main.py` route registration is a single hot file that every mount packet serializes on; the
  accepted pattern (max-envelope, M5-T059) is to ship route modules UNMOUNTED and isolate the
  `include_router` edit in a small mount packet. The plan adopts this as the disjointness discipline for
  the export/scene/import routes.
- D4. No `source_registry` record exists for the accepted OTI footprint connector (DB-058 (g)); the
  backend-api rule requires one for every connector, so PKT-C must add it as part of wiring, not defer it
  further.

END-OF-REPORT
