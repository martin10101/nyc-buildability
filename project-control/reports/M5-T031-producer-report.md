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
