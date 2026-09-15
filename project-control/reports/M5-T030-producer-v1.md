# M5-T030 producer evidence

Producer: `frontend-engineer`. Independent acceptance, full CI, browser review, and delivery verification remain pending. No task acceptance or remote action was performed by the producer.

## Identity, scope, and diagnosis

- Worktree: `/workspace/scratch/cfa2464c5c7f/nycdf-source-links`.
- Product baseline supplied and verified by the orchestrator: `546dd09a9541097a5c5e39cd43683c4068ab368d`; task-packet commit subsequently reported as `61ef58fc`.
- The orchestrator subsequently froze the unchanged product/test/capture content at `fa3cea2d2e4ac906f57648566df87178197c7076`; its scope/protected-state record is `project-control/reports/M5-T030-scope.json`. Local command evidence below was collected on this content before that commit.
- The orchestrator recorded G0 PASS, claimed the task, and authorized implementation before producer edits began. The producer did not run git, gh, or the project-control CLI.
- Recent-change finding from the orchestrator: accepted M5-T029 introduced the architect surfaces using `datasetLandingUrl(record.dataset_id ?? profile.reproducibility.dataset_id)` and profile metadata in the inspector; the existing helper and legacy disclosure originated in M5-T025. No concurrent product changes were reported. The protected main reference was reported as `d8b3899f`; the remote candidate remained at the product baseline during production.
- Runtime: Linux `6.18.44-x86_64-with-glibc2.39`, Node `v24.19.0`, npm `11.9.0`, Vitest `4.1.11`. The orchestrator supplied an existing dependency symlink backed by a byte-identical package lock. No installation or dependency/configuration edit was performed.

Root-cause hypothesis before the fix: the source UI constructs only dataset-level URLs and therefore discards the available lot identity at the URL/presentation boundary; an unchanged component rendering a matching lot-specific URL would falsify this hypothesis. Four component examples instead failed with the lot link absent.

The bounded failure surface was the fact drawer, profile source inspector, report source appendix, and legacy disclosure. The same link-selection mechanism explains all four. Actual data already contained the canonical BBL, source ID, and dataset ID; no API, contract, calculation, or legal-rule change was needed. Per-record metadata fallback also needed to remain within the fact's source when resolving the new link.

Applied guidance: engineering-reliability §§1–3, 8–10; its defect-convergence inventory for the four related surfaces; code-modularity policy §§2–6 and 11. A new test-locator defect recurred during verification and was closed with the bounded deficit-convergence method described below.

## Changed files and behavior

| File | Change |
|---|---|
| `apps/web/src/lib/provenance-link.ts` | Keeps `datasetLandingUrl`, `isValidDatasetId`, and the existing landing prefix API. Adds `plutoRecordUrl` and `sourceFactLinks` in the owning pure helper. |
| `apps/web/src/components/architect/EvidenceRecord.tsx` | Current lot record first, dataset link second, exact original field visible, captured/current sentence; values, dates, version, units, conflicts, fact review, complete raw record, and review history retained. |
| `apps/web/src/components/architect/EvidenceInspector.tsx` | Profile source links use the selected profile BBL and proven source/dataset; retains captured release/date and exposes full captured retrieval metadata. |
| `apps/web/src/components/architect/ReportSources.tsx` | Adds current/about links and exact field names; source IDs, original/normalized values, units, dates, version, provenance IDs, conflicts and review entries remain. One current/captured sentence above the table. |
| `apps/web/src/components/property/ProvenanceDisclosure.tsx` | Compatible existing props; validates the captured BBL, uses source-matched metadata fallback, retains exact values/dates and dataset ID, and exposes fact review plus full captured records. |
| `apps/web/src/lib/__tests__/provenance-link.test.ts` | Guard examples for all boroughs, identity mismatch, source/dataset conflicts, absent/malformed values, LF/CRLF, Unicode digits, oversized input, and hostile request URLs. |
| `apps/web/src/components/architect/__tests__/source-links.test.tsx` | Observable links on all architect surfaces; negative source/lot cases, changed-profile state, captured metadata, and actual ESB captured fact. |
| `apps/web/src/components/architect/__tests__/workspace.test.tsx` | Strengthens preservation of conflict state and exact confirmation/override history without removing existing assertions. |
| `apps/web/src/components/property/__tests__/provenance-disclosure.test.tsx` | Legacy current/about links, invalid BBLs, mixed source/dataset handling, and full captured metadata. |
| `apps/web/e2e/architect-workspace.spec.ts` | Adds desktop/mobile drawer href checks and a report source-row screenshot/check in the existing recorded-official journey. Existing legal text assertions remain unchanged. |
| `project-control/reports/M5-T030-producer-report.md` | This producer evidence only. |

The pure guard accepts exactly source `nyc-dcp-pluto-soda`, dataset `64uk-42ks`, and a ten-character BBL matching `^[1-5][0-9]{9}$`. Its current-record prefix is the constant `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=`. It never reads `request_url` to construct either href, trims nothing, and performs no fetch.

For fact surfaces with profile identity, `record.bbl` must equal `profile.identity.bbl`. Missing per-record dataset metadata is borrowed only from matching-source reproducibility. Explicit invalid/different per-record datasets are never overwritten by fallback. Conflicting datasets for the same source suppress the current-lot link, while an independently valid About link remains. An explicit proven record can stand on its own when profile retrieval metadata belongs to a different source.

The legacy component receives no profile identity in its existing API; it validates the captured record's own BBL. This limitation is explicit in its code comment and test. No guessed filtered-table URL was added. Source IDs remain visible. Legal `RuleEvaluationResult` citations keep their existing semantics and were not edited.

Module ownership remains pure link validation in the existing helper and presentation in the four existing components. Physical production-file line counts are 56 / 82 / 69 / 59 / 107 respectively, versus 46 / 76 / 63 / 58 / 102 before the change. No new production module, fetch layer, registry, dependency, or competing contract was introduced.

## Exact commands and observed output

All npm commands used cwd `/workspace/scratch/cfa2464c5c7f/nycdf-source-links/apps/web`. The modularity command used the repository root. Each npm invocation reported the existing `http-proxy` and `min-release-age` configuration warnings; neither configuration was changed.

**A — observable red before production edits**

```text
npm run test -- src/components/architect/__tests__/source-links.test.tsx src/components/property/__tests__/provenance-disclosure.test.tsx
```

Exit 1. Exact summary:

```text
Test Files  2 failed (2)
     Tests  4 failed (4)
Start at  20:44:17
AssertionError: expected null not to be null
```

All four failures were the absent `Current PLUTO record (JSON)` anchor: fact evidence, profile sources, report appendix, and legacy evidence. These tests imported existing components; failure was observable UI output, not a missing helper export.

**B — first green plus existing helper/legacy compatibility examples**

```text
npm run test -- src/lib/__tests__/provenance-link.test.ts src/components/architect/__tests__/source-links.test.tsx src/components/property/__tests__/provenance-disclosure.test.tsx src/components/property/__tests__/sections.test.tsx
```

Exit 0:

```text
Test Files  4 passed (4)
     Tests  22 passed (22)
Start at  20:48:06
```

**C — complete affected suite**

```text
npm run test -- src/lib/__tests__/provenance-link.test.ts src/components/architect/__tests__/source-links.test.tsx src/components/architect/__tests__/workspace.test.tsx src/components/property/__tests__/provenance-disclosure.test.tsx src/components/property/__tests__/sections.test.tsx
```

The first two C runs (20:51:49 and 20:52:32) each exited 1 with `1 failed | 107 passed (108)`. Both failed only the new report-source text locator. The report's text is `another-source`, followed by `<br />`, followed by `26v1`; Testing Library's immediate text matching combines these as `another-source26v1`. Exact text and a word-boundary pattern therefore both rejected valid visible content. The no-link assertions had passed. No product code was changed for this issue.

The correction uses a source-prefix text match plus `toBeVisible()`. The safety assertions are unchanged. The isolated closure command was:

```text
npm run test -- src/components/architect/__tests__/source-links.test.tsx -t 'does not borrow'
Test Files  1 passed (1)
     Tests  2 passed | 17 skipped (19)
Start at  20:53:14
```

The final C run after mutation restoration exited 0:

```text
Test Files  5 passed (5)
     Tests  108 passed (108)
Start at  20:54:17
Duration  1.64s
```

This includes the unchanged eight legacy `sections.test.tsx` examples. Coverage totals: 69 helper, 19 architect source, 4 workspace, 8 new legacy, and 8 existing section examples.

**D — wrong-lot mutation and restoration**

Temporary mutation in `sourceFactLinks`:

```text
const identityMatches = identity === undefined || record.bbl === identity.bbl;
→ const identityMatches = true;
```

The mutation was executed inside a Python `try/finally` that restored the original file and checked SHA-256 equality. The exact nested test command was:

```text
npm run test -- src/lib/__tests__/provenance-link.test.ts src/components/architect/__tests__/source-links.test.tsx -t 'wrong lot|wrong-lot'
```

Mutated result, exit 1:

```text
Test Files  2 failed (2)
     Tests  4 failed | 84 skipped (88)
Start at  20:53:48
```

The helper returned the ESB URL for a different expected lot. The fact drawer and report rendered BBL `3021720001` as the selected property's link. The changed-profile example retained the previous lot's link. All four expected refusals detected the mutation.

Restored file SHA-256: `5c62219754122bfee6d635058139d8cc3d3f52692ee55c89fb85f93fb4f419fe`. Rerunning the identical D command after restoration exited 0:

```text
Test Files  2 passed (2)
     Tests  4 passed | 84 skipped (88)
Start at  20:54:16
```

The skipped counts come solely from this explicit test-name filter; the final C run executes all 108 examples with none skipped.

**E — static checks**

| Exact command | Observed output / exit |
|---|---|
| `npm run typecheck` | `tsc --noEmit`; exit 0. |
| `npm run lint` | `1077 problems (0 errors, 1077 warnings)`; exit 0. Warnings were in the existing vendored MapLibre modules; no warning waiver/configuration edit. |
| `python tools/modularity_check.py --check` | `selected 435 files; failures 0; warnings 18`; exit 0. Existing warnings identify unrelated modules; none of the changed production modules were listed. |

Severity and closure: the missing lot-specific destination was a must-fix provenance/workflow defect addressed by the four original regressions and subsequent guarded implementation. The repeated locator error was an Important test-harness defect: its affected surface was one new shared test across two renderers, its cause was the source/version text combination, and the targeted plus final affected runs establish `VERIFIED_CLOSED` for that harness issue. This is not an independent product acceptance verdict. No unresolved producer-observed code defect remains; the required external verification steps below remain open.

## Acceptance and directive evidence

| Scenario / requirement | Producer evidence | Remaining independent work |
|---|---|---|
| S1 / D-062-R001, R002 | A→B observable regressions on four surfaces; final C; exact field/value/date/version/unit checks; full raw ESB and profile metadata equality; conflict and review-history preservation; current link before About link. | Execute the updated Playwright journey and inspect desktop/mobile/report screenshots. |
| S2 / D-062-R001, R004 | 69 helper examples plus negative component cases; five-borough shape cases; wrong identity, malformed values, source/dataset conflicts, source-matched fallback, hostile URLs; D mutation FAIL→restore PASS. | Independent G5 review at the frozen code identity. |
| S3 / D-062-R003 | Actual captured ESB record is used by a component test; expected current URL matches the separately verified official endpoint. Sources and observed values below. | Verify the changed deployed UI's actual DOM href and the live official response after delivery. |
| S4 / D-062-R004 | Only the ten named product/test paths and this producer report were edited by the producer. C, typecheck, lint, and modularity pass. No backend/contracts/dependencies/calculation/legal changes. | Root diff/protected-reference verification; frozen-SHA full CI/build/e2e; remaining independent gates. |
| S5 / D-062-R005 | Architect-value draft below names supported use, the manual alternative, and professional-review limits; no benchmark/time-saving claim. | Independent review and final owner-facing return. |

## Real-building evidence and limits

The independent source report `project-control/reports/M5-T030-source-verification.md` reports HTTP 200 and exactly one official row for both:

- [Empire State Building BBL 1008350041](https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1008350041): retrieved September 15, 2026 at 00:29:14 UTC; PLUTO representative address `338 5 AVENUE`, version `26v2`.
- [Brooklyn BBL 3021720001](https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3021720001): retrieved at 00:28:17 UTC; `83 TAYLOR STREET`, `lotarea=116000`, `bldgarea=341300`, version `26v2`.

The [official LPC designation report](https://s-media.nyc.gov/agencies/lpc/lp/2000.pdf) identifies the Empire State Building at 350 Fifth Avenue, Manhattan block 835, lot 41. The independent verification derived BBL `1008350041` from those components and the official PLUTO BBL definition. The address-only query for `350 5 AVENUE` returned no row; the source report explains PLUTO's representative/lowest-address convention. This change joins by the verified BBL, not by an address guess.

The orchestrator separately captured the actual live existing UI and current official response in `project-control/reports/M5-T030-real-building-baseline.json`, and the full escaped SourceFact in `project-control/reports/M5-T030-esb-captured-fact.json`. The new test imports only that latter JSON into test code and confirms:

| Captured fact | Preserved result |
|---|---|
| BBL / field | `1008350041` / `lotarea` |
| Original / normalized | String `91351` / number `91351` (displayed `91,351`) |
| Units | `square feet` |
| Version / captured time | `26v2` / `2026-09-15T00:38:20Z` |
| Current href | `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1008350041` |
| Full record | Deep equality with the captured JSON, including source IDs, observation ID, request URL as escaped text, and value/response digests. |

The independent current row also contains `bldgarea=2812739` and `numfloors=102.0000000`; the producer's real-data component test concerns the captured `lotarea` record. These are source observations, not evaluated development permissions.

This is component evidence against a real captured record, plus separately attributed official HTTP/source verification. The producer did not test the changed deployed UI. Top-level JSON rendering is blocked by the cloud browser according to the source/baseline workflow; DOM href inspection and an independent official HTTP response check are the verification route. The current public endpoint may change after capture and does not recover the immutable captured snapshot. No stable official filtered-table deeplink was established.

## Architect-value draft

An architect can use this MVP to keep captured property facts, the supported draft checks, calculation traces, and review states together for a lot. The new link opens that lot's current City PLUTO record beside the captured field, value, date, and version, so the architect can check the inputs and identify differences. The workspace can also assemble a traceable draft property brief for the checks it supports.

An architect can already gather these public records, inspect zoning sources, and perform the checks manually. The software organizes that work and its supporting evidence. Professional judgment is still needed to resolve conflicting data, verify site and survey conditions, interpret zoning and legal questions, and decide whether a project is feasible. This MVP does not establish complete feasibility, and no measured time-saving claim is made.

## Verification contexts and frozen-content handoff

- Cloud Linux worktree and focused integration with the existing React components and canonical fixtures were exercised. The final affected suite passes after restoration.
- Strict malformed/adversarial inputs and stale selected-property identity were exercised. There is no new async operation, shared mutable state, cache, job, retry, or external I/O; concurrency/retry verification is inapplicable to this pure URL/presentation change.
- A fresh frozen checkout, full regression/build, CI Chromium execution, independent responsive/keyboard screenshot review, and post-deployment live DOM/HTTP checks remain pending. Windows execution was not performed; no platform-dependent production API or shell behavior was added.
- Existing legal citation components are outside the changed files. Their full regression remains part of CI; this report does not substitute local source inspection for those gates.
- The producer supplies content hashes below; the orchestrator reports that content frozen at `fa3cea2d2e4ac906f57648566df87178197c7076` and will bind independent evidence to the reviewed SHA. A later product/test edit invalidates these content-specific observations.

Sorted code/test manifest (SHA-256, two spaces, relative path, newline per entry):

```text
de8dea8d6055f0238dae4bf98904de29e998763298186c31d62884c4dcf52eb7  apps/web/e2e/architect-workspace.spec.ts
3370ed2f4a72cc082e422efa4a370525153de8fffb0fae6c65d5d0aec665099a  apps/web/src/components/architect/EvidenceInspector.tsx
85a5e2992981ea9692e68cda31c40155597fc13cb5eb78ea9c5499198a5d28fc  apps/web/src/components/architect/EvidenceRecord.tsx
02959d1bbbdf6c7223d55b46877bf9e8dc9bad8093eae142e5c206f4371f3d79  apps/web/src/components/architect/ReportSources.tsx
77c01ef4016c07f4583da5b791e61b6ef0d8673ddffe02fa44d8905c0c649bf2  apps/web/src/components/architect/__tests__/source-links.test.tsx
48a19ef905b56f7d6f4ae627753919a974f6f06f86083530d49789f87c529019  apps/web/src/components/architect/__tests__/workspace.test.tsx
0213e6c717d25643acbbd6a6649e0865d3f32549131ce9192d0897cad22572bf  apps/web/src/components/property/ProvenanceDisclosure.tsx
99178ff3254e3f20a550c3fd01ab11f19b5b0e7848da3b681997f100d3ec9e95  apps/web/src/components/property/__tests__/provenance-disclosure.test.tsx
1de6ec9cb72d83f370647d11671e0dcd4817bb35c551ef247a7ca8e850ab5bdb  apps/web/src/lib/__tests__/provenance-link.test.ts
5c62219754122bfee6d635058139d8cc3d3f52692ee55c89fb85f93fb4f419fe  apps/web/src/lib/provenance-link.ts
```

Manifest SHA-256: `446534176f962bed0b3abfda887d524fcb34e6c8de78d6a3059c8a588799b562`.

Imported actual ESB capture SHA-256: `ccaaf621f409c4d732d269ae31ef817e30c64ff296ab461ea6ca662ead1a7507`.
