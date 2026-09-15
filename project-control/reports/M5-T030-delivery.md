# M5-T030 — Verified source-link delivery

The reviewed frontend is live at https://nyc-buildability.onrender.com. The candidate branch advanced without force from `546dd09a9541097a5c5e39cd43683c4068ab368d` to `2cee838cf49cbb0bb7cf0c796d81141182909502`. Render deployment `dep-daka3nnqj5pc73add88g` on existing frontend service `srv-dajnsctg1s2s73bg2do0` reports that exact commit live, finished `2026-09-15T01:41:08.938481Z`. No service configuration or backend deployment changed.

All required functional gates G0–G5 passed. CI run [34917249174](https://github.com/martin10101/nyc-buildability/actions/runs/34917249174) passed all 18 jobs, 703 unit/component tests and 100 browser journeys. Reviewed task content identity remains `003f07771e693873864325d7fd69a712d78939faccab09bef0c92292ca229bf8`.

| Real property | Actual live source href | City response and comparison |
|---|---|---|
| Empire State Building, BBL 1008350041 | https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1008350041 | HTTP 200; one matching lot; lotarea original 91351, normalized 91351, displayed 91,351; version 26v2. |
| Brooklyn searched 125 Taylor Street, BBL 3021720001 | https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3021720001 | HTTP 200; one matching lot; lotarea original 116000, normalized 116000, displayed 116,000; version 26v2. |

The new deployed Source drawers were opened in the browser, and their actual hrefs and full captured source records were read from the DOM. Official HTTP requests were independently checked at approximately 01:42:32 UTC. The live ESB report's source appendix was also opened; its address and lotarea rows retain original/normalized values, exact fields, date/version/review state, current-record links and secondary About links.

PLUTO uses representative address `338 5 AVENUE` for the ESB lot identified by the official LPC report as 350 Fifth Avenue, block 835 lot 41. Brooklyn's representative address is `83 TAYLOR STREET`; the live page retains the searched address and explains this distinction. Identity was checked using BBL.

Limits: the cloud browser previously blocked top-level raw JSON viewing; this evidence verifies the actual live UI href and the successful official HTTP response, not a visually opened JSON document. Both real-property pages still show `No supported cap` and `Buildable envelope not assessed`. This source-link test does not establish full development feasibility. Current records and dated captured evidence remain distinct. Architect time savings have not been measured.

Protected references were checked after publication: main remains `d8b3899f61efa6620e18a26541ced96020f5bef9`; PR 241 remains open and unmerged at head `4174a3b2a547ae7d5df5d35cefb63767cbf84721`. Application scope evidence contains no backend, contract, dependency, configuration or calculation change.

Exact evidence:

- `project-control/reports/M5-T030-delivery.json`
- `project-control/reports/M5-T030-live-esb-ui.json`
- `project-control/reports/M5-T030-live-brooklyn-ui.json`
- `project-control/reports/M5-T030-live-official-records.json`
- `project-control/reports/M5-T030-live-report-ui.json`
- `project-control/reports/M5-T030-ci-v2.json`
- `project-control/reports/M5-T030-source-verification.md`

R006 candidate publication and R007 existing Render delivery are observed complete. Final directive verification and task acceptance are recorded separately by their authorized roles.
