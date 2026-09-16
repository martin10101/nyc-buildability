# M5-T031 producer evidence

Producer: frontend-engineer (isolated agent). Worktree: `m5t031-ui`, task branch `task/M5-T031-ui`, inherited task-control HEAD `dd22b95`; product base `780dccf1e95a6ede2051b334ed99e0340ebce914`. Submitted for independent review, not accepted by the producer.

## Result and limits

Overview, Zoning and Report now share a development-first summary. It separates **Residential FAR · city record** (PLUTO reference), **Evaluated residential FAR** (an applicable canonical rule trace), and the **Draft zoning floor-area cap** (canonical scenario square feet). No FAR arithmetic, zoning lookup table, API contract, backend rule, configuration or dependency changed.

Height, setbacks/yards and lot coverage/open space have visible rows. Missing results say **Not calculated**. A supplied numeric bulk result is promoted only with an exact linked applicable rule trace, matching output value and citations; malformed, empty or unlinked provenance cannot substantiate a limit. A value link opens the full calculation evidence. No bulk calculation has been added by this task.

Existing building information, including Built FAR, is collapsed below the overview and retained completely. Property facts, source inspector, open issues, report source appendix and print expansion remain available. The shared comparison heading now says **Floor-area record comparison**, preserving the backend's original label, scope note, signed result, review state and typed uncomputable reason.

The observed 1279 37 Street case had correctly recorded built FAR 2.61 and residential reference FAR 3.00 before this work. The reproduced defect is presentation hierarchy, not an arithmetic or swapped-field defect. The live `spatial_intersection_absent` failure remains outside this frontend task. A PLUTO reference is not a verified determination of project capacity. No 7,200 sq ft cap or unused zoning area is fabricated from this source record.

## Failure surface and change boundary

Baseline reproduction and causal clustering: `project-control/reports/M5-T031-baseline.md`. The production boundary is a pure presentation selector (`src/lib/architect/development-limits.ts`, 111 physical lines) and one shared React component (`DevelopmentLimits.tsx`, 73 lines). Existing pages compose the summary. `PropertyOverview.tsx` preserves the `DraftHeadline` export through a compatibility re-export for its existing scenario consumer.

The adapter rejects ambiguous/duplicate reference records and duplicate provenance IDs, conflicting source facts, wrong property identities, malformed numeric values, unsupported or duplicate evaluated outputs, missing citations and mismatched analysis fingerprints. Zero remains a value; absent data never becomes zero. Existing failure states, raw records, legal sources and report contents are retained.

Applied engineering-reliability sections: §1 reproduction and one owning-boundary hypothesis; §2 shared presentation boundary with stable public contracts; §3 observed red/green and provenance mutation proof; §7 concise status with complete evidence preserved; §8 malformed, identity, stale-snapshot, integration and browser-context distinctions; §9 no missing calculation reported as a closed defect. No speed, money, legal approval or universal correctness claim is made.

## Acceptance examples

| Packet scenario | Executable coverage and observed result |
|---|---|
| S1 | Three overview/zoning/report entry tests; real 1279 numeric regression (synthetic surrounding profile), 3.00 source distinct from 2.61 existing and no invented cap. PASS. |
| S2 | Supplied 1.50 evaluated FAR and 15,000 sq ft cap remain independent of source 3.00. Zero supported outputs preserved. PASS. |
| S3 | R1–R12 family representatives, numbered/lettered variants, split/mixed contexts and unknown label; all five borough BBL prefixes. Synthetic rendering cases only, not legal applicability assertions. PASS. |
| S4 | Null/string/boolean/object/negative/nonfinite source values; conflicting/duplicate/unlinked evidence; wrong BBL; unsupported, inapplicable, expired, invalid, citationless and duplicate traces; conflicting scenarios and stale fingerprints. PASS. |
| S5 | Every existing fact retained in an expandable disclosure; exact source inspector and Escape focus; original report print/restore checks preserved. Component PASS; new real-browser journeys committed, execution pending CI/reviewer. |
| S6 | Observed baseline 3 failing tests; implemented 3 passing tests; wrong source-field and old comparison-heading mutations fail, restoration passes. Independent source audit is separately owned by M4-T022. |

## Commands and actual results

All npm commands below ran in `apps/web` in the isolated cloud worktree. Node 24.19.0 / npm 11.9.0 were preinstalled; CI pins npm 11.18.0, so exact CI-toolchain evidence remains an independent gate. No manifest or lockfile changed.

| Command | Observed result |
|---|---|
| `npm ci` | Exit 0; 469 packages installed from the committed lock. |
| `npm test -- --run src/components/architect/__tests__/development-limits.test.tsx` before production changes | Exit 1; 3 tests failed: no accessible `Development limits` region in Overview, Zoning or Report. |
| Same command after the initial implementation | Exit 0; 3 passed. |
| Same command on final test pack | Exit 0; 66 passed. |
| `npm test -- --run src/components/architect/__tests__/development-limits.test.tsx src/components/architect/__tests__/entry.test.tsx src/components/architect/__tests__/workspace.test.tsx src/components/compare/__tests__/unused-floor-area.test.tsx` | Exit 0; intermediate focused regression 89 passed. |
| `npm test` on the final restored production candidate | Exit 0; 40 files, 769 tests passed. Existing jsdom canvas warnings were emitted; this is not visual map evidence. |
| `npm run typecheck` | Exit 0. |
| `npm run lint` | Exit 0; 0 errors, 1,077 warnings in existing vendored MapLibre assets. |
| `npm run build` on the final restored production candidate | Exit 0; compilation, type checking, static generation and build traces completed. |
| `npm audit --json` | Exit 0; info/low/moderate/high/critical/total all 0. |
| `npm run depage` | Exit 0; all 563 committed registry packages at least seven days old and integrity verified. |
| `python tools/modularity_check.py --check` | Exit 0; selected 435 tracked files, 0 failures, 18 existing warnings. New files were not yet tracked; rerun after orchestrator integration for their official census. |

Critical provenance mutation: in `residentialReference`, temporarily changed `original_field_name === "residfar"` to `"builtfar"`; ran `npm test -- --run src/components/architect/__tests__/development-limits.test.tsx -t 'captured 1279'`. It failed, exit 1, with expected **3.00**, received **2.61**. Restored the exact original bytes in a `finally` block; the same test passed, exit 0. Targeted selection excluded other tests only for mutation isolation; the final full suite had no skipped cases.

Comparison-heading revert proof: temporarily restored **Unused draft zoning floor area**, then ran `npm test -- --run src/components/compare/__tests__/unused-floor-area.test.tsx -t 'shows the document label verbatim'`. Exit 1. Restoring **Floor-area record comparison** produced exit 0 while retaining the document label and scope assertions.

Local transient raw output: `/tmp/m5t031-red.log`, `/tmp/m5t031-focused.log`, `/tmp/m5t031-full-tests.log`, `/tmp/m5t031-build.log`, `/tmp/m5t031-audit.json`, `/tmp/m5t031-mutation-red.log`, `/tmp/m5t031-mutation-green.log`, `/tmp/m5t031-label-mutation-red.log`, `/tmp/m5t031-label-mutation-green.log`. Exact frozen-SHA gate records and CI evidence belong to the orchestrator.

## Independent review and remaining verification

Added six browser journeys in `e2e/development-limits.spec.ts`, using the existing real API over recorded official PLUTO fixtures. The harness's R5 spatial substrate is explicitly synthetic; it tests connected rendering rather than asserting that its real fixture parcel is legally R5. The existing architect mobile metric check now asserts one visible new reference figure, preventing an empty-list false pass. Existing map pixel assertions, report printing and remaining architect journeys were preserved.

Browser tests have not been executed by this producer. The root's cloud browser rejected loopback access; changed-build visual acceptance, responsive screenshots and connected browser assertions remain pending the CI/reviewer workflow. No local screenshot or live deployment is claimed.

M4-T022 source matrix/real-parcel audit is the paired independent source evidence for D-063. This producer neither certifies those results nor treats reference matches or honest refusals as completed buildability. Backend spatial wiring and unsupported height/yards/coverage calculations remain separate gaps; engineering tests do not replace G6 legal approval. The architect was not asked for routine validation or a new benchmark sheet.

Frozen app-file content identity (19 existing files named by the task's allowed app paths, sorted path + NUL + bytes + NUL; excludes this report): SHA-256 `6a805688f01797e34604a34f32f36266ddade407edf5680ed22fcb37c9857ac4`. Orchestrator commits, runs final gates and decides disposition. No git mutation, control-state mutation, main/PR-241 change or production action was performed by the producer.

## Rework v2 — independent G3/G4 findings and bounded visual corrections

This section supersedes the v1 guard and bulk-promotion claims above. Independent review `M5-T031-G3-G4-v1.md` at `b4514d9a338a7ced8bd268b85afd55b12c729fd3` found five must-fix cases despite the earlier green tests. All five were reproduced together before editing: `npm test -- --run src/components/architect/__tests__/development-limits.test.tsx -t 'review cluster'` exited **1**, with **8 failed / 66 excluded by the name filter**. Four failures were the separate missing nested trace fields; the other four covered conflict, null association, wrong bulk meaning and duplicate-value filtering. Raw capture: `/tmp/m5t031-rework-red.log`.

| Finding | Complete bounded repair | Acceptance evidence |
|---|---|---|
| Missing/malformed trace fields can crash new selectors and existing detail consumers | Guard fields the readers actually dereference, including trace objects, validation records, effective-window flags, output objects, steps and citations. Guard the shared route composition; preserve the unchanged unusable document in an explicit captured-record disclosure. Zoning and Report also guard direct composition. | Original four cases pass; malformed primitive/array/object variants, citation entries and trace entries pass. All four missing-field cases exercised through Overview, Zoning, Scenarios, Evidence and Report. |
| Conflicting or fail-safe evaluation still promotes a cap | Cap promotion requires an eligible unique residential trace, matching identity/version/status and the canonical residential square-foot output. Associated conflict/fail-safe states suppress promotion. Scenario failures and integrity disagreement also suppress numerical summary claims. | Same-BBL/same-fingerprint rule-conflict reproduction, all three summary views with fail-safe, and contradictory scenario/validation cases pass. |
| Null/malformed fingerprint is treated as agreement | Both documents must carry meaningful matching SHA-256 fingerprints, matching BBL/profile version and matching evaluation-contract version. Missing evaluation cannot substantiate a scenario cap. | Null, empty, whitespace, incomplete and malformed fingerprints, absent evaluation and mismatched source identifiers pass. |
| Matching identifiers/numbers can turn FAR into height | Removed generic numeric bulk promotion. The current open-typed bulk provenance does not establish supported height/yard/coverage meanings. These rows remain **Not calculated**, with evidence links and all supplied raw constraints retained. | FAR-as-height negative passes. The prior synthetic-height positive was replaced by preservation-without-promotion assertions, including zero in the unchanged captured scenario. This follows the review's explicit instruction; no bulk rule was removed. |
| Filtering by the desired value conceals competing traces | Choose a single applicable residential trace, then require unique rule/version identity before any value agreement. Cap must equal the trace's existing square-foot output exactly; no arithmetic. | Same/different-value, invalid and inapplicable duplicate identities pass. Generic bulk trace matching no longer exists. |

`ScenarioWorkspace` now supplies evaluation and selected BBL to the same headline. Unassociated returned scenario figures remain behind an explicitly labelled disclosure; the complete original scenario record is still available. No fabricated or cleaned substitute document is created.

Independent visual review added two narrowly scoped corrections: the existing skip link is explicitly anchored at viewport `top:0; left:0`, keeping the existing keyboard-focus reveal; the new headline spells out **Professional review required** and other statuses, preserving the raw enum within source wording. The readable-status test was observed failing before the label edit (exit 1) and passing after (exit 0). Seven additional browser journeys cover all five malformed-response routes, missing fingerprint, and mobile skip-link scrolling/focus with screenshots. The new browser file now contains thirteen journeys; v2 execution remains for final frozen CI and independent visual review.

### Load-bearing mutation evidence

Each mutation used the actual adapter, restored its exact bytes in a `finally` block, then ran the same targeted command again:

| Mutation | Command suffix after `npm test -- --run src/components/architect/__tests__/development-limits.test.tsx` | Mutated → restored |
|---|---|---|
| Treat missing scenario fingerprint as agreement | `-t 'R3 does not treat'` | Exit 1 / 1 failed → exit 0 / 1 passed |
| Remove fail-safe rejection from trace selection | `-t 'withholds cap promotion across'` | Exit 1 / 3 failed → exit 0 / 3 passed |
| Remove duplicate identity check before filtering | `-t 'inapplicable twin'` | Exit 1 / 1 failed → exit 0 / 1 passed |

Raw pairs are `/tmp/m5t031-rework-{missing-fingerprint,fail-safe,identity-before-value}-{red,green}.log`. Other tests were name-filtered only during targeted proof; the final full run excludes none.

### Regression failure found and repaired

The first v2 full regression exited **1**, with **859 passed / 1 failed**. The unchanged existing map-error test fired its synthetic error as soon as the DOM container existed, before the asynchronous MapLibre import had necessarily attached its error listener (`lot-outline-map.test.tsx:525`). The failure surface and source path were inspected; no repeated run was used to hide the failure.

The orchestrator explicitly extended scope to that one test file. It now waits for the observable `data-parcel-state="rendered"` precondition and fires the same error inside `act`. Every fallback/attribution assertion remains; no timeout, production map, dependency or contract changed. This closes the test's event-readiness race. Original failure capture: `/tmp/m5t031-rework-full.log`.

### Final v2 producer checks and remaining gates

| Command | Actual result |
|---|---|
| Focused run of development limits, entry, workspace, source links, unused floor area and lot-outline map tests | Exit 0; **6 files / 226 tests passed**. |
| `npm test` after all repairs | Exit 0; **40 files / 861 tests passed**, no skipped tests; existing jsdom canvas warnings remain. |
| `npm run typecheck` | Exit 0. |
| `npm run lint` | Exit 0; **0 errors / 1,077 unchanged vendored warnings**. |
| `npm run build` | Exit 0; compilation, type checking, static generation and build traces completed. |
| `python tools/modularity_check.py --check` | Exit 0; **437 tracked files / 0 failures / 18 existing warnings**. |

Final captures: `/tmp/m5t031-rework-focused-final.log`, `/tmp/m5t031-rework-full-final.log`, `/tmp/m5t031-rework-lint-final.log`, `/tmp/m5t031-rework-build-final.log`. The adapter is 162 physical lines; the shared component is 90. No production backend, rule, schema, API, dependency or configuration change was made. No git/control mutation or production action was performed by this producer.

V2 app-file content digest, using the same sorted path/NUL/bytes/NUL method over the **20** allowed existing app files including the explicitly extended map-test path: SHA-256 `703ea0f8c745ec8e63a5a0426979f8edaa403679a48b92547dc0bec730ba2ed5`. The original v1 digest and observations remain above as history. Independent G3/G4/G5/DCV and v2 browser/visual verification must be rerun against the newly frozen candidate; v1 passes do not establish v2 acceptance. Legal approval and completed citywide bulk calculations remain outside this frontend result.
