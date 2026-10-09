# M5-T032 G1 source review (verbatim reviewer return; data-contract-verifier, read-only, pinned c2437717)

Saved verbatim by the orchestrator per the report-preservation rule.

---

# G1 GATE REPORT — M5-T032 (official-source / data-contract)

**Reviewer:** data-contract-verifier (read-only)
**Reviewed SHA (pinned):** c2437717af33601d61ef467e39fe162e8b797361 (verified via `git rev-parse HEAD`)
**Verdict: PASS** (two minor/advisory findings, non-blocking)

## Scope verified
Official GeoSearch v2 contract fidelity, HTTP-outcome honesty, ZoLa link discipline, AS-11 live-smoke separateness, and consumers just outside the packet boundary. Thin-client: vitest/e2e are CI authority; I verified source against the official contract directly and cross-checked the stored CI/AS-11 evidence.

## Official-source confirmation
- GeoSearch v2 docs (`geosearch.planninglabs.nyc/docs/`) confirm both `.../v2/autocomplete` and `.../v2/search` under one Pelias-backed base; constants at `address-search.ts:4,8` match exactly. Autocomplete and `/search` are correctly modeled as the SAME service / distinct user action, never independent failover (comment `address-search.ts:5-8`; risk noted in packet).
- PAD `addendum.pad.bbl` is present in real payloads but **never consumed**: `parseAddressSuggestions` (`address-search.ts:53-73`) emits only `houseNumber/street/borough/zip`; grep for `addendum|pad.bbl` across production `src` returned **no matches**. Suggestions cannot supply the authoritative BBL for legal identity. Confirmed by test `not.toHaveProperty("bbl")` (`address-search.test.ts:13,153`).
- AS-11 live smoke (`M5-T032-orchestrator-seam-evidence.md:10-30`) is dated 2026-09-17T07:14:30Z, orchestrator-captured, three live curls (autocomplete 200/2 features w/ PAD BBLs; `/search` 200/10; ZoLa `bbl/3052960043` 200, no redirect). BBL `3052960043` is canonical (`^[1-5]\d{9}$`). Kept explicitly separate from deterministic tests. Plausible and honest.

## Item-by-item
1. **GeoSearch usage** — PASS. Constant URLs; same-service framing; PAD-BBL never used for identity; suggestions carry no BBL.
2. **Outcome classification** — PASS with F1. 429→`rate_limited` (checked first, never retried), 5xx→`source_unavailable` (bounded retry, max 3, abortable backoff), timeout terminal & never re-armed, malformed for non-JSON content-type / body-parse fail / null-parse / oversize (128 KB). Retry gate keyed strictly to `source_unavailable` (`address-search.ts:162`); deadline never raised (AS-3 `address-search.test.ts:84-98`). No invented suggestions on malformed payloads: null → `malformed`; non-PAD features filtered, structurally-broken feature rejects whole collection (`address-search.ts:60-72`).
3. **ZoLa discipline** — PASS. `zolaLotUrl` = constant `ZOLA_LOT_PREFIX` + strict `^[1-5]\d{9}$` only, honest null otherwise (`provenance-link.ts:53-56`); never server-echoed. `sourceFactLinks.zolaUrl` gated by `currentRecordUrl !== null` (identity match AND no dataset conflict AND PLUTO source), so wrong-lot / wrong-source / conflict close the ZoLa link too (`provenance-link.ts:70-81`). Same gating rendered consistently across ProvenanceDisclosure (ZoLa primary line 47, PLUTO demoted `section-note` line 48), EvidenceRecord (30-31), ReportSources (32-33), EvidenceInspector (28,42-43). M5-T030 negative cases preserved (`source-links.test.tsx:77-133`, `provenance-disclosure.test.tsx:41-63`).
4. **AS-11** — PASS (see above).

## Consumer sweep (standing licence)
- Only exhaustive consumer of the changed `AddressSearchErrorReason` enum is `AddressAutocomplete.tsx:15-21` (`Record<AddressSearchErrorReason,string>` — TS-forced complete, all 5 reasons present). `use-address-suggestions.ts` switches on `outcome.kind` only. `announce.ts` consumes the unrelated `AddressErrorState`/`UpstreamFailureOutcome` enums, **not** this one — no missed/broken consumer.
- **F2 (advisory, pre-existing, out of scope):** `PropertyOverview.tsx:52` builds `https://zola.planning.nyc.gov/bbl/${bbl}` (the "Open ZoLa" site-context affordance) by raw interpolation of `profile.identity.bbl` **without** routing through `zolaLotUrl()` — no strict token validation, no honest-absence path. Uses the authoritative profile identity (not server-echoed, not a suggestion BBL) and is a constant host/path, so low risk; not changed by M5-T032. Recommend a follow-up to route it through `zolaLotUrl` for uniform discipline.

## Findings
- **F1 (minor, `address-search.ts:125-126,162`):** `if (!response.ok) return source_unavailable` classifies **any** non-ok, non-429 status — including 4xx client errors — as `source_unavailable`, which the retry loop then retries up to 3×. Packet/comment state "bounded retry only for transient 5xx." Practical impact ~nil (GeoSearch returns 200+empty for no-match, verified constant URL rules out 404, min-3-char client guard rules out the 400 missing-text case; retry stays bounded, no deadline stacking). Honest-classification tightening: gate retry/label on `status >= 500`. Non-blocking.
- **F2:** see consumer sweep above. Non-blocking.

## Notes / limits
- Deterministic vitest/e2e not executed locally (thin client). Stored CI evidence (`M5-T032-orchestrator-seam-evidence.md:52-58`, all 18 jobs green incl. web/web-e2e 971/971 + 113/113) is at task-branch head 2b440f41; reviewed content at HEAD c2437717 is byte-consistent with the files verified here. G1 verdict rests on direct source-vs-official-contract inspection, not on rerunning the suite.
- Schema-drift behavior is fail-safe: unknown top-level shape → `malformed`; renamed/removed PAD fields → features filtered → empty suggestions (no-match), never a crash or invented data.

**Verdict: PASS.** F1 and F2 are minor/advisory; recommend logging F1 as a hardening follow-up and F2 as a separate uniformity task. No blocking data-contract or official-source defect.

## Files reviewed (absolute)
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\address-search.ts
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\provenance-link.ts
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\property\ProvenanceDisclosure.tsx
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\architect\{EvidenceInspector,EvidenceRecord,ReportSources,AddressAutocomplete,PropertyOverview}.tsx
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\architect\use-address-suggestions.ts
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\announce.ts
- Tests: address-search.test.ts, provenance-link.test.ts, provenance-disclosure.test.tsx, source-links.test.tsx
- project-control\tasks\M5-T032.json; reports\M5-T032-producer-report.md; reports\M5-T032-orchestrator-seam-evidence.md

Sources:
- [NYC GeoSearch v2 docs](https://geosearch.planninglabs.nyc/docs/)
