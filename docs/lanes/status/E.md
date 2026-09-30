# Lane E — Outputs and parity: status

Updated by lane E only, after every task (lane prompts, shared rules).

| | |
|---|---|
| **State** | E-01 (M1-27 drawing kit v0) built on `lane-e/E-01-drawing-kit`, handed to the integrator for review |
| **Done** | E-01: `services/api/app/drawings/kit/` — results loader (shared C-03 `validate_results_document`, then fail-closed geometry and drawn-vs-printed checks), drawing style table, site plan SVG, axonometric massing SVG, approved snapshots and property tests; behind `LANE_E_ENABLED` (off). Review corrections 1–4 applied |
| **Next** | E-02 (PDF converter trial), then E-03 (DXF from the same geometry and style table) |
| **Blocked by** | E-01b (section drawing): owner question Q8. E-01 CI: request E-2 (Lane C guard test `test_contract_serializers.py` treats any `app.contracts` import as a serializer use) |
| **Open owner questions** | Q8 — whether the section view falls under the expansion hold |
