# M5-T032 producer report

- Task: M5-T032 — Address-search reliability under GeoSearch failure + ZoLa-first human-readable property links
- Branch: task/M5-T032-address-search-links
- Date: 2026-09-17
- Directive refs: D-064 (D-064-R005 ZoLa-first link, D-064-R007 focused testing)
- This unit: a report/checkpoint honesty revision. It re-ran ONLY the fast documented validator
  (`modularity_check.py --check`, foreground, output quoted below) and corrected the integration
  handoff and evidence framing. It did NOT re-run the >300s directive-registry validator this turn
  (a foreground-captured transcript is not obtainable within the 300s limit — see "Status honesty").
  It did NOT author or re-author the code/test patches described below — see "Attribution and
  provenance" and "ROUTED TO SUPERVISOR".

## Attribution and provenance (read first)

The working-tree implementation and test changes below are CLAIMED to originate from a separate
producer run (labelled `persistent-local-36-m5t032`, claude-opus-4-8). That claim is UNVERIFIED here:
this unit did not observe or reproduce that run, and no digest-bound transcript of it exists in the
ledger. The changes currently sit as loose, unattributed working-tree edits. Their authorship,
provenance, and per-file content must be supplied by the supervisor as a bounded packet before they
are committed (see "ROUTED TO SUPERVISOR").

Three events must be kept strictly distinct. None of them, alone or together, establishes directive
compliance (see "Directive compliance — UNVERIFIED"):

1. The CLAIMED separate producer run — an assertion that some prior run authored the code/test
   patches. Unverified; needs attribution.
2. The supervisor directive-compliance check that TIMED OUT — a distinct, separate outcome. A timeout
   is neither pass nor fail. It says nothing about event 1 and is not the same run as event 3.
3. A separate background run of `validate_directive_compliance.py --check` reported to have COMPLETED
   (exit 0, no INVALID output), from which registry/structural integrity was inferred. That
   completion and its registry-integrity conclusion are WORKER-REPORTED and independently UNVERIFIED:
   the run was moved to the background and its transcript was never captured. Treat it as unverified
   unless a completed, digest-bound transcript is supplied. It is a different event from the
   supervisor timeout (event 2) and must not be conflated with it.

## Status honesty — OBSERVED vs WORKER-REPORTED vs UNVERIFIED

Nothing in this producer unit demonstrates a passing or failing web build.

OBSERVED (run by this unit in the foreground this turn, output quoted — reproducible):
- `python tools/modularity_check.py --check` → `selected 438 files; failures 0; warnings 18`. All 18
  warnings are pre-existing, unrelated files (surveyReview/types.ts; several services/api connectors
  and scenario modules; tools/agent_supervisor modules; tools/context_benchmark.py); none of this
  task's 14 files is flagged. PASS.

WORKER-REPORTED (NOT independently verified — no captured transcript; do NOT treat as verified):
- The separate background run of `python tools/validate_directive_compliance.py --check` is REPORTED
  to have exceeded the 300s foreground limit, been moved to the background, and completed with exit
  code 0 and no INVALID output, and registry/structural integrity was inferred from it. Because that
  run was backgrounded and its transcript was never captured, both the completion and the
  registry-integrity conclusion are worker-reported and independently unverified. This unit did NOT
  re-run it this turn: a foreground-captured transcript is not obtainable within the 300s limit, and a
  background re-run would only reproduce the same uncaptured state. A completed, digest-bound
  transcript would be required to promote this to verified. Even verified, it would confirm ONLY
  registry structure — never D-064-R005/R007 satisfaction (see "Directive compliance — UNVERIFIED").

SEPARATE OUTCOME (preserved, not merged with the above):
- The supervisor's earlier directive-compliance check TIMED OUT. This is its own outcome — neither
  pass nor fail — and is a different event from the worker-reported background completion above. It is
  recorded here as a distinct fact, not as corroboration of registry integrity or of compliance.

NOT observed / PENDING (no evidence produced here — do NOT treat as verified):
- Web CI (vitest `web`) and browser CI (`web-e2e`) were NOT run. This is a thin client with no local
  npm/node_modules. No web CI pass and no web CI failure has been demonstrated by this unit.
- AS-1..AS-10 have deterministic tests AUTHORED (in the loose working-tree changes), but they are NOT
  verified complete — their executable authority is the web/web-e2e CI jobs on the pushed head, which
  have not run.
- AS-11 (dated live GeoSearch + ZoLa smoke check) is deferred to the orchestrator at the seam.
- The `provenance-disclosure.test.tsx` positional-assertion incompatibility below is a PREDICTION, not
  an observed CI failure, and its blast radius is REASONED, not measured. It is preserved as
  UNVERIFIED and routed to the orchestrator (see "ROUTED TO ORCHESTRATOR").

## Directive compliance — UNVERIFIED (pending a completed, digest-bound transcript)

Directive compliance for D-064-R005 (ZoLa-first link) and D-064-R007 (focused testing) is UNVERIFIED.

- `validate_directive_compliance.py --check` is a registry/structural integrity check. Even a clean,
  transcript-backed run of it would confirm only that the directive registry is well-formed. It does
  NOT verify that D-064-R005/R007 are actually satisfied by the code at the frozen head.
- The background run of that validator (event 3 above) is worker-reported and independently
  unverified. It is not evidence that D-064-R005/R007 are met, and it is not the supervisor timeout.
- The only acceptable evidence of directive compliance is an independent directive-compliance-verifier
  producing a completed, digest-bound `verification.json`/transcript pinned to the reviewed content
  identity at the frozen head. No such transcript exists yet: the supervisor check timed out, the
  background registry run was never captured, and the claimed separate producer run is itself
  unverified.

Therefore directive compliance is PENDING. Do not record it as PASS. Acceptance stays blocked on it.

## Summary (describes the loose working-tree changes; authorship claimed, not verified here)

Two changes, both intended to stay inside the M5-T030 identity/conflict discipline.

1. Address-search reliability (handoff §6). GeoSearch failures no longer collapse into one
   "unavailable" message. Distinct reasons, bounded recovery, an explicit full-address `/search`
   action, preserved typed text, and a prefilled manual/Geoclient fallback.
2. ZoLa-first source links (D-064-R005). The human-readable ZoLa lot page is the primary link on every
   evidence/provenance surface. The raw PLUTO JSON record is demoted to a secondary link. The dataset
   landing link is retained. Both record links stay gated by the same valid, conflict-free lot
   identity, so wrong-lot / wrong-source / dataset-conflict cases render neither.

## Bounded per-file change inventory (in allowed_paths; supplied FOR supervisor attribution)

This is the inventory of the loose working-tree changes: 14 in-scope implementation/test files (8
production + 6 tests). It is complete — it matches the working-tree change set file-for-file with no
material omissions. The supervisor must return the SAME set as bounded, attributed, per-file patches
(one patch per file, no material omissions) before anything is committed.

Production (8):
- `apps/web/src/lib/address-search.ts` — new `GEOSEARCH_SEARCH` endpoint; `AddressSearchErrorReason`
  (`unavailable | source_unavailable | rate_limited | malformed | timeout`); `AddressSearchOptions`
  (maxAttempts, backoffMs); split into `fetchGeoSearchOnce` + `fetchGeoSearchWithRetry`; bounded retry
  ONLY on a transient 5xx (`source_unavailable`), at most `ADDRESS_SEARCH_MAX_ATTEMPTS` (3), short
  backoff, abort-aware; `fetchAddressSuggestions` (autocomplete) and `fetchAddressSearch` (/search)
  share the same recovery, deadline, and strict PAD parsing. A 429 is `rate_limited` (never retried); a
  slow reply past the deadline is a terminal `timeout` (deadline never re-armed).
- `apps/web/src/components/architect/AddressAutocomplete.tsx` — per-reason copy (no collapsing);
  incomplete (<3 char) vs genuine no-match are distinct and not framed as service failures; an explicit
  "Search this full address" action and a prefilled "Use manual entry with this address" affordance;
  Enter with no highlighted suggestion runs `/search` (never a silent first-match accept); the explicit
  search carries the same request-generation + abort discipline as the suggestion hook.
- `apps/web/src/components/address/AddressResolutionScreen.tsx` — `onFallback` opens the existing
  Geoclient manual resolver, seeds ONLY the street field with the typed one-box text (clears stale
  house/borough/ZIP), opens the disclosure, and moves focus to the resolver.
- `apps/web/src/lib/provenance-link.ts` — `ZOLA_LOT_PREFIX` constant + `zolaLotUrl(bbl)` (constant
  prefix + canonical 10-digit BBL only; honest null otherwise); `sourceFactLinks` exposes `zolaUrl`
  under the same guard as `currentRecordUrl`.
- `apps/web/src/components/architect/EvidenceInspector.tsx`, `EvidenceRecord.tsx`, `ReportSources.tsx`,
  `apps/web/src/components/property/ProvenanceDisclosure.tsx` — ZoLa link rendered first (primary);
  PLUTO JSON demoted to a `section-note` secondary link; dataset link kept.

Tests (6; deterministic; no live network):
- `apps/web/src/lib/__tests__/address-search.test.ts` — AS-1 transient 503 recovery, AS-2 repeated 503
  → distinct `source_unavailable` at the bound, AS-3 slow-reply terminal timeout, AS-4 `/search`
  endpoint, AS-6 429 not retried, abort-mid-backoff, AS-8 per-borough + Queens hyphenated through both
  autocomplete and `/search`.
- `apps/web/src/lib/__tests__/provenance-link.test.ts` — `zolaLotUrl` valid across five boroughs,
  hostile/malformed BBL → null, same-guard-as-raw-record, wrong-lot / conflict → null.
- `apps/web/src/components/architect/__tests__/autocomplete.test.tsx` — per-reason copy + text
  preserved, incomplete vs no-match, prefilled fallback, explicit `/search` never auto-accepts,
  Enter-without-highlight, and full cancellation/request-generation suite (edit, A→B→A late reply,
  pick, unmount).
- `apps/web/src/components/architect/__tests__/source-links.test.tsx`,
  `apps/web/src/components/property/__tests__/sections.test.tsx` — ZoLa primary + PLUTO secondary,
  ordering, honest absence on wrong-lot / conflict / non-PLUTO / invalid BBL.
- `apps/web/src/components/address/__tests__/address-resolution.test.tsx` — manual/Geoclient fallback
  opens, focuses, preserves only the typed text.

## Acceptance-scenario mapping (implementation coverage — NOT a verification claim)

Each row names the code and the deterministic test intended to cover the scenario. Authoring a test is
not observing it pass: none of these tests were executed here (thin client, no local npm). Their
pass/fail authority is the web/web-e2e CI jobs on the pushed head, which have not run. Do not read this
section as "AS-1..AS-10 verified complete."

- AS-1..AS-9 → address-search.ts + AddressAutocomplete + resolution fallback, with the deterministic
  tests listed above. Coverage authored; execution PENDING at the CI seam.
- AS-10 → provenance-link.ts + the four provenance surfaces + source-links/sections tests. Coverage
  authored; execution PENDING at the CI seam.
- AS-11 → PENDING: deferred to the orchestrator (dated live GeoSearch + ZoLa smoke check at the seam).

## Verification run by this unit (documented commands only)

- `python tools/modularity_check.py --check` → OBSERVED this turn, foreground, output quoted:
  `selected 438 files; failures 0; warnings 18` (pre-existing warnings only; none of this task's 14
  files). PASS.
- `python tools/validate_directive_compliance.py --check` → NOT re-run this turn. The prior background
  run is worker-reported and independently unverified (see "Status honesty" and "Attribution and
  provenance", event 3): it was backgrounded past the 300s foreground limit and its transcript was
  never captured, so its exit-0/no-INVALID completion and the registry-integrity conclusion drawn from
  it cannot be treated as verified here. Even if promoted to verified with a completed transcript, it
  would confirm registry structure ONLY — not D-064-R005/R007 satisfaction, which needs a completed,
  digest-bound directive-compliance transcript from an independent verifier.

Web tests (`npm run typecheck | test | lint | build | test:e2e`) are NOT run: thin client, no
npm/node_modules. Per the packet, CI web + web-e2e on the pushed head is the executable authority and
the orchestrator captures that evidence at the seam. No web CI result — pass or fail — is claimed here.

## ROUTED TO ORCHESTRATOR — predicted incompatibility outside this packet's allowed_paths (UNVERIFIED)

This is a PREDICTION for the orchestrator to verify at the CI seam, NOT an observed CI failure. No web
CI was run here, so neither the failure nor its blast radius has been demonstrated.

Predicted incompatibility (unverified): the ZoLa-first reordering renders the ZoLa link as the first
`<a>` on the provenance surfaces. An existing unit test, OUTSIDE this packet's allowed_paths, asserts
the first link positionally:

- `apps/web/src/components/property/__tests__/provenance-disclosure.test.tsx:19`
  `expect(screen.getAllByRole("link")[0]).toBe(current)` — `current` is the "Current PLUTO record
  (JSON)" link. If ZoLa now renders first, this assertion would fail under vitest. PREDICTED, not
  observed.

This mirrors the pattern already updated IN scope in `source-links.test.tsx` (expects the ZoLa link
first). This unit did NOT edit `provenance-disclosure.test.tsx`: it is outside allowed_paths (the
excluded test), and the packet routes it to the orchestrator rather than the producer editing out of
scope.

Requested orchestrator handling (verify first, then decide):
1. Run web CI on the pushed head to confirm whether `provenance-disclosure.test.tsx:19` actually fails
   and to measure the true blast radius — do not assume the prediction.
2. If confirmed, expand allowed_paths to include that test and either have a producer update line 19 to
   expect the ZoLa lot link first (asserting the PLUTO record present as the secondary link, mirroring
   `source-links.test.tsx`) or apply the correction as an orchestrator-tagged edit. No production change
   is expected for this.

Reasoned (NOT measured) blast-radius note, for the orchestrator to check, not to rely on: the two e2e
specs that reference "Current PLUTO record (JSON)" (`architect-workspace.spec.ts`,
`development-limits.spec.ts`) appear to use name-based locators rather than positional/first-link
locators, and the in-scope `source-links.test.tsx` / `sections.test.tsx` already assert the new
ordering. Whether `provenance-disclosure.test.tsx:19` is the ONLY break is a hypothesis for CI to
confirm, not a verified fact.

## ROUTED TO SUPERVISOR — evidence-repair packet (bounded, attributed, no material omissions)

The loose working-tree changes were not authored by this unit and must not be re-authored by it. Route
the evidence repair to the supervisor. The repair packet the supervisor supplies is exactly three
parts:

1. Bounded, per-file patches for EVERY changed implementation/test file — all 14 in the "Bounded
   per-file change inventory" above (8 production + 6 tests), one patch per file, with NO material
   omissions, and with attribution stating which run/identity authored each patch and its provenance.
   The patches must match the inventory file-for-file so nothing is committed as an unattributed loose
   edit.
2. The complete report (this file, `project-control/reports/M5-T032-producer-report.md`), carried
   whole — no material omissions.
3. The task-file patch WITH attribution: `project-control/tasks/M5-T032.json` shows modified in the
   working tree (task-contract / loop-ready packet metadata). This is a control-plane file. This unit
   did NOT and will NOT edit, revert, or commit it. The supervisor supplies who changed it and why so
   the orchestrator can account for it separately at the seam.

Constraints this unit held to (do not resolve the evidence gap by breaking them):
- This unit did NOT re-author the unattributed code/test edits.
- This unit did NOT modify any control-plane file (`project-control/tasks/M5-T032.json`, state, etc.).
- This unit did NOT touch the excluded, out-of-scope test
  `apps/web/src/components/property/__tests__/provenance-disclosure.test.tsx` — it stays routed to the
  orchestrator for CI verification and any allowed_paths expansion BEFORE any edit.
- The only file this unit wrote is this report, which is inside allowed_paths.

## INTEGRATION HANDOFF (corrected)

The current HEAD does NOT contain these working-tree changes — the in-scope implementation, tests, and
this report exist only as uncommitted working-tree edits. The prior handoff wording that assumed HEAD
already carried them was wrong. Correct sequence:

1. The authorized commit step must FIRST use the supervisor's bounded, attributed per-file patches
   (from "ROUTED TO SUPERVISOR") to capture the 14 in-scope implementation/test files PLUS this report
   (`project-control/reports/M5-T032-producer-report.md`) with proper authorship — never loose,
   unattributed edits.
2. Do NOT include in that producer commit: `project-control/tasks/M5-T032.json` (control-plane;
   orchestrator/supervisor account for it separately) or
   `apps/web/src/components/property/__tests__/provenance-disclosure.test.tsx` (the excluded,
   out-of-scope test; verify via CI first).
3. After attribution and source review, the orchestrator captures the authorized commit, then pushes
   and collects: web + web-e2e CI results on the pushed head (the executable authority for
   AS-1..AS-10), the dated AS-11 live smoke evidence (GeoSearch autocomplete + `/search` + one ZoLa lot
   URL, recorded alongside this report and separate from the deterministic tests), and an independent
   directive-compliance verification tied to the reviewed content identity at the frozen head.
4. Acceptance stays PENDING until: attribution and source review are done, the attributed commit lands,
   web/web-e2e CI is green on the pushed head, AS-11 live evidence is captured, the
   `provenance-disclosure.test.tsx` prediction is resolved, and directive compliance is independently
   verified via a completed, digest-bound transcript tied to the reviewed content. This unit ran no
   local npm and claims no completion.

## Scope notes

- `use-address-suggestions.ts`, `AddressConfirmCard.tsx`, `RuleEvaluationResult.tsx`, `entry.test.tsx`,
  `workspace.test.tsx`, `address-confirm.test.tsx`, `rule-evaluation.test.tsx` are in allowed_paths but
  show no working-tree change (RuleEvaluationResult renders no PLUTO/ZoLa link; the address hook and
  confirm card are reused as-is).
- This unit edited exactly one file: this report. It did not touch `project-control/tasks/M5-T032.json`,
  the excluded `provenance-disclosure.test.tsx`, or any production/test source.
