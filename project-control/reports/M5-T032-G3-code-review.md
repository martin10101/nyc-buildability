# M5-T032 G3 code review (verbatim reviewer return; code-reviewer, read-only, pinned c2437717)

Saved verbatim by the orchestrator per the report-preservation rule (reviewer's memory write
was blocked by the read-only guard; return channel preserved here).

---

# G3 Gate Report — M5-T032 (Address-search reliability + ZoLa-first links)

**Reviewer:** code-reviewer (read-only, senior review)
**Reviewed SHA:** c2437717af33601d61ef467e39fe162e8b797361 (verified `git rev-parse HEAD` matches)
**Material commits:** cbc10397 (producer), 71d4abb3 + 2b440f41 ([ORCH-CORRECTED])
**Diff basis:** `git diff 15701458..2b440f41 -- apps/web` (810+/36-, 16 files)
**Verdict: PASS** — 3 LOW/INFO findings, none gate-blocking.

## What I verified

**Core logic — `address-search.ts` (race/cancellation/bounded-retry):**
- Per-attempt deadline is a fixed `AbortController` + `timedOut/stop` + `Promise.race`; on timer fire `stop()` aborts the transport and resolves `timeout` synchronously before any late body/fetch settle, so a valid-reply-after-deadline is deterministically `timeout` (AS-3). Confirmed no misclassification of a slow body read.
- Retry (`fetchGeoSearchWithRetry`) is bounded to `ADDRESS_SEARCH_MAX_ATTEMPTS` (3) and fires **only** on `source_unavailable` (5xx). `timeout`/`rate_limited`/`malformed`/`unavailable`/success all return immediately → no unbounded retry, no raised/stacked deadline. `backoff()` resolves early to `aborted` on signal (AS-9).
- `fetchGeoSearchOnce` classification is exhaustive and non-collapsing: 429→`rate_limited`, non-ok→`source_unavailable`, non-JSON/parse/oversized→`malformed`, transport→`unavailable`, deadline→`timeout`, external abort→`aborted`. Matches handoff §6.

**UI — `AddressAutocomplete.tsx` / `use-address-suggestions.ts`:**
- Explicit `/search` carries the same guard as the typed hook: monotonic `fullSearchSeq` + `fullSearchAbort`, aborted+seq-retired on edit (`onChange`), pick (`choose`), and unmount; result applied only if `seq===current && kind!=="aborted"`. `searchResult` displays only while `query===text` → stale full-search never renders. Enter with no active option routes to `/search`, never auto-accepts first candidate (AS-4). `searching` state cannot get stuck (button `disabled` + Enter guard prevent overlap; every supersede path clears it).
- Distinct per-reason copy in `ERROR_MESSAGES`; typed text preserved across every failure (onChange is the only text reset).

**ORCH corrections are behavior-faithful to packet intent:**
- `entryFocusNonce` (71d4abb3): correct fix for the sync `.focus()`-hits-null-ref-on-remount class — same effect-after-commit pattern as the existing `manualFocusNonce`; focuses the always-mounted entry input (autocomplete/street). No behavior change beyond restoring intended focus.
- Two strict-TS casts (`as unknown as Identity`, `querySelectorAll<HTMLElement>`) are inert. Legacy `provenance-disclosure.test.tsx` and `architect-workspace.spec.ts` 429 copy updated to the intended ZoLa-first / typed-outcome contracts — correct, not weakened.

**ZoLa-first (`provenance-link.ts` + 4 consumers):**
- `zolaLotUrl` = constant `ZOLA_LOT_PREFIX` + `BBL_PATTERN`-validated 10-digit BBL; null otherwise (no reflected/guessed link). In `sourceFactLinks`, `zolaUrl` is gated behind `currentRecordUrl !== null`, so every M5-T030 wrong-lot / wrong-source / dataset-conflict guard also closes the ZoLa link. All 4 render surfaces (EvidenceInspector, EvidenceRecord, ReportSources, ProvenanceDisclosure) show ZoLa primary + PLUTO record demoted (`section-note`) + dataset landing retained. No production consumer of the record link was missed.

**Test adequacy — all AS covered by deterministic tests:**
AS-1 recovery(calls=2); AS-2 repeated-503→`source_unavailable` at bound + prefilled fallback; AS-3 slow-valid→terminal `timeout`(calls=1); AS-4 `/search` + never-auto-accept (button + Enter paths); AS-5 incomplete vs no-match distinct copy; AS-6 429 not retried(calls=1); AS-7 malformed (content-type/parse/oversized) → `malformed`; AS-8 per-borough + Queens hyphenated through both flows, BBL never consumed; AS-9 edit-aborts/immediate-new-search, delayed-superseded-drop, A→B→A seq-guard, select/unmount abort; AS-10 ZoLa primary+secondary ordering, conflict/non-PLUTO/invalid-BBL → honest absence, M5-T030 negatives now also assert `zola-lot-link` null. Modularity: all touched files well under thresholds. CI authority: seam commit records 18/18 green at 2b440f41 (thin-client, CI is executable authority per packet; I could not re-run web/web-e2e locally).

## Findings (all non-blocking)

1. **LOW / follow-up — `apps/web/src/components/architect/PropertyOverview.tsx:52`** (outside allowed_paths). A "view property" surface builds `https://zola.planning.nyc.gov/bbl/${bbl}` **inline** from `profile.identity.bbl` **without** the `zolaLotUrl()` BBL validation this task establishes. Pre-existing (not a regression; producer could not touch it). Recommend a follow-up task routing PropertyOverview (and `AddressConfirmCard`, which at least validates `canonicalBbl` + `encodeURIComponent`) through the shared validated `zolaLotUrl` helper for one link-safety path.

2. **LOW — `address-search.ts:12-13,152-155` comment.** "only a fast source-failure is retried" overstates: a *slow-but-under-deadline* 5xx is also retried, so repeated near-deadline 5xx can reach ~3×deadline cumulative latency. Still bounded (≤3 attempts, each fixed deadline, none raised) so it satisfies "no deadline stacking"; only the comment is slightly aspirational. Optional: bound retries to fast failures or tighten the comment.

3. **INFO — `AddressResolutionScreen.tsx:219` `openManualFallback`.** Seeds the entire one-box string into `street` with empty `houseNumber`. This is the documented packet intent (full one-box string, cleared stale parts) and user-editable, but the combined string may not split cleanly for the Geoclient manual resolver. Acceptable as designed; noted for UX awareness.

## Reproduction / evidence
- HEAD verified: `git rev-parse HEAD` → c2437717…
- Consumer sweep: `git grep -n "currentRecordUrl|plutoRecordUrl|sourceFactLinks|zolaLotUrl" c2437717 -- apps/web/src/**/*.tsx` → exactly 4 consumers, all updated; plus PropertyOverview inline link (finding 1).
- Diffs read: address-search.ts, provenance-link.ts, AddressAutocomplete.tsx, use-address-suggestions.ts, AddressResolutionScreen.tsx, 4 link consumers, and all test files listed above.

**Recommendation to orchestrator:** record **G3 = PASS**. Findings 1–3 are non-blocking; suggest opening a small follow-up task for finding 1 (unify inline ZoLa links through `zolaLotUrl`). AS-11 (dated live smoke) remains the orchestrator's seam capture, outside this code review.
