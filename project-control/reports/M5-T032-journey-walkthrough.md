# M5-T032 human-journey walkthrough (verbatim reviewer return; human-journey-reviewer, read-only, pinned c2437717)

Saved verbatim by the orchestrator. (The reviewer titled this "G3" in its own numbering; in
this packet's gate mapping the numbered G3 record belongs to code-reviewer — this report is
the roster's journey-walkthrough evidence supporting the wave, referenced by the G4 record.)

---

# G3 Human-Journey Gate Report — M5-T032

**Task:** Address-search reliability under GeoSearch failure + ZoLa-first human-readable property links
**Reviewed SHA:** c2437717af33601d61ef467e39fe162e8b797361 (pin confirmed)
**Executed-journey authority:** CI at 2b440f41 (Playwright 113/113 green, per prompt)
**Method:** Read-only static walkthrough of changed source + vitest specs + Playwright e2e. No local run (thin client). AS-11 live smoke is orchestrator-owned at the seam.

## Verdict: PASS

All five failure journeys produce distinct, non-collapsing, actionable copy; recovery (explicit /search, prefilled manual/Geoclient, BBL) is always reachable; no dead ends; focus/announcer accessibility is sound; and lot-identity links show honest absence when identity is invalid/conflicting. Findings are advisory only.

## Journey-by-journey

- **(a) Healthy** — Debounced autocomplete → suggestions → ArrowDown+Enter picks; onPick → resolveAddress → Confirm card. Never auto-accepts. Covered by autocomplete.test + e2e "one-box keyboard selection". PASS.
- **(b) Rate-limited (429)** — Classified `rate_limited`, NOT retried (calls=1), distinct copy "Address suggestions are rate-limited right now…". Manual + full-search offered. e2e mocks a 429 and asserts the exact copy. PASS.
- **(c) Down (repeated 503)** — Bounded 3 attempts (backoff 400ms) then distinct `source_unavailable` "…temporarily unavailable…"; not folded into transport `unavailable`. Manual fallback prefilled. address-search.test AS-1/AS-2. PASS.
- **(d) Slow past deadline** — 6000ms per-attempt timeout is a distinct terminal outcome ("taking too long to suggest"), never retried, deadline never re-armed/stacked; explicit full-address search + manual offered. address-search.test AS-3. PASS. (See Finding 1.)
- **(e) Garbage (malformed)** — Bad content-type / unparseable body / non-PAD payload → `malformed`; no partial/invented suggestion rendered; copy "…response we can't read safely." PASS. (See Finding 2.)
- **Paste complete address, no pick** — "Search this full address" button and Enter-with-no-highlight both run the explicit `/search` (same upstream, own seq+AbortController guard); candidate still requires an explicit pick — first approximate match is never accepted as the lot. autocomplete.test AS-4 + A→B→A stale-guard. PASS.
- **"Not my property" → entry** — Clears result, RETAINS form values, silences announcer, fires no fetch, returns focus via `entryFocusNonce` effect (fixes the null-ref-on-remount drop to <body>). Non-architect path tested (address-confirm S4, values BROADWAY/120 retained, street focused). PASS. (See Finding 3.)
- **Manual/Geoclient fallback** — Typed one-box text preserved and VISIBLE in the street field; stale house/borough/ZIP deliberately cleared (never silently combined); disclosure opened and focused. address-resolution S8 + e2e "manual and BBL recovery remain reachable". PASS.
- **Evidence surfaces (ZoLa-first)** — `zolaLotUrl` (constant prefix + `/^[1-5][0-9]{9}$/`) is PRIMARY "View this lot on ZoLa"; PLUTO JSON demoted to secondary `section-note`; "About this dataset" retained. ZoLa gated by the SAME identity/conflict guard as the raw record (`zolaUrl = currentRecordUrl!==null ? …`), so every M5-T030 wrong-lot / wrong-source / dataset-conflict negative renders neither link — honest absence. Verified across EvidenceRecord, EvidenceInspector, ReportSources, ProvenanceDisclosure (source-links.test, provenance-disclosure.test, provenance-link.test incl. hostile/reflected BBL rejection). AddressConfirmCard's own ZoLa/handoff gating (validateBblInput) is unchanged. PASS.

## Accessibility
- Autocomplete: `role=combobox` + `aria-autocomplete=list` + `aria-expanded` (bound to open && count>0) + `aria-activedescendant`/`aria-controls` matching option ids; listbox `aria-label`. Status line is `role=status` (polite live region) carrying searching/loading/incomplete/error/no-match/count messages.
- Resolution screen: single persistent `OutcomeAnnouncer` live region; focus moves to `[data-outcome-heading]` on arrival, to the resolving card on retry/pick, and back to entry on Not-my-property/Edit via the nonce effect. Announcer cleared while in flight so an identical retry outcome re-announces.

## Findings (all ADVISORY — none blocks PASS)

1. **6000ms deadline below observed healthy latency (hidden assumption).** Handoff §6 recorded ~6.8s successful GeoSearch timings; the deadline is intentionally NOT raised. Under a consistently-slow-but-healthy service, both autocomplete AND the explicit `/search` time out and the analyst is routed to manual entry every time. Recovery is honest and always reachable, and holding the deadline is an explicit task decision ("no indefinitely raised deadline"), so this is a conscious trade-off, not a defect — but worth surfacing to the owner as a product-usability watch item.

2. **`malformed` copy omits the still-present full-search button (minor copy/affordance mismatch).** The malformed message says "Use manual entry or BBL below" and does not mention searching the full address, yet the "Search this full address" button is still rendered (gated only by `trimmedLength>=3 && !selected`). Offering the extra path does no harm and is defensible (same upstream may still be junk), but the copy and the visible affordance are slightly inconsistent.

3. **Architect-mode "Not my property" focus target is unit-untested.** The `entryFocusNonce` effect focuses `autocompleteRef` in architect mode; only the non-architect `streetInputRef` path is asserted (address-confirm S4), and the e2e architect journey never clicks "Not my property". The logic is symmetric and the nonce mechanism is proven for `manualFocusNonce`/`streetInputRef`, so risk is low, but the architect focus-return is not directly verified.

## Notes for the orchestrator
- AS-11 (dated live GeoSearch autocomplete + `/search` + one ZoLa lot URL smoke) is PENDING in the producer report and deferred to you at the integration seam — capture and record it as live evidence separate from the deterministic tests before acceptance. [Orchestrator note: captured 2026-09-17T07:14:30Z in M5-T032-orchestrator-seam-evidence.md, before this review.]
- The prompt names CI 2b440f41 as executed authority while the review pin is c2437717; confirm 2b440f41 carries the byte-identical reviewed apps/web surfaces (or is the seam head over this content) when recording the gate. [Orchestrator note: DCV verified `git diff --stat 2b440f41 c2437717 -- apps/web/` is empty.]

**Reviewed files (all absolute):**
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\address-search.ts
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\architect\use-address-suggestions.ts
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\architect\AddressAutocomplete.tsx
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\address\AddressResolutionScreen.tsx
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\address\AddressConfirmCard.tsx
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\provenance-link.ts
- C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\architect\{EvidenceRecord,EvidenceInspector,ReportSources}.tsx, components\property\ProvenanceDisclosure.tsx, components\rule-evaluation\RuleEvaluationResult.tsx
- Specs: apps\web\src\lib\__tests__\{address-search,provenance-link}.test.ts; components\architect\__tests__\{autocomplete,source-links}.test.tsx; components\address\__tests__\{address-resolution,address-confirm}.test.tsx; components\property\__tests__\provenance-disclosure.test.tsx; apps\web\e2e\architect-workspace.spec.ts

Memory updated: .claude/agent-memory/human-journey-reviewer/m5t032-address-reliability-zola-first.md (+ MEMORY.md index).
