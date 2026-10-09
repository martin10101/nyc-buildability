# M5-T032 G4 QA review (verbatim reviewer return; qa-engineer, read-only, pinned c2437717)

Saved verbatim by the orchestrator per the report-preservation rule.

---

## G4 QA GATE — M5-T032 — VERDICT: PASS

**Reviewed at pinned SHA** `c2437717af33601d61ef467e39fe162e8b797361` (worktree HEAD was `d8b3899f`; all content read via `git show c2437717:<path>`). Executable authority: CI on task head `2b440f41` — `apps/web` is byte-identical between `2b440f41` and `c2437717` (`git diff --quiet 2b440f41 c2437717 -- apps/web` → IDENTICAL), so vitest 971/971 + Playwright 113/113 apply to the reviewed surface.

### AS-by-AS coverage

| AS | Deterministic test(s) | Status |
|----|----|----|
| AS-1 transient 503 recovery, typed text kept | `address-search.test.ts` "AS-1 recovers a transient 503…" (calls==2); UI-preservation in `autocomplete.test.tsx` "reads each failure reason… never clears the typed text" | COVERED |
| AS-2 repeated 503 → distinct `source_unavailable`, bounded, prefilled fallback | `address-search.test.ts` "AS-2 stops at the retry bound…" (calls==MAX_ATTEMPTS); `autocomplete.test.tsx` "routes a source failure to the prefilled manual/Geoclient fallback"; `address-resolution.test.tsx` S8 prefilled resolver; e2e "manual and BBL recovery remain reachable" | COVERED |
| AS-3 valid-after-deadline = distinct timeout, no stacked deadline | `address-search.test.ts` "AS-3 a VALID reply arriving AFTER the deadline…" (reason timeout, calls==1); timeout copy `/taking too long/` in `autocomplete.test.tsx` | COVERED (see F1) |
| AS-4 pasted full address → explicit /search, never auto-accept first | `address-search.test.ts` "AS-4 fetchAddressSearch targets /search…"; `autocomplete.test.tsx` "runs the explicit full-address /search and never auto-accepts…" + "Enter with no highlighted suggestion triggers /search"; e2e "one-box keyboard selection resolves the authoritative BBL" | COVERED |
| AS-5 no-match vs incomplete, distinct, not a failure | `autocomplete.test.tsx` "distinguishes an incomplete address from a genuine no-match" (`/at least 3 characters/` vs `/no matching address found/`) | COVERED |
| AS-6 429 = rate_limit, distinct from 503, bounded | `address-search.test.ts` "AS-6 never retries a 429…" (calls==1); `address-resolution.test.tsx` S5 matrix; e2e 429 → rate-limited copy | COVERED |
| AS-7 malformed/non-PAD → validation failure, no invented suggestion | `address-search.test.ts` malformed→`malformed`, 129KB size cap→`malformed`, `parseAddressSuggestions` rejects empty/malformed parts (returns `[]`/`null`); `autocomplete.test.tsx` malformed copy `/read safely/` | COVERED |
| AS-8 Queens hyphenated + one per borough, deterministic fixtures | `address-search.test.ts` "AS-8 deterministic per-borough address-flow fixtures" (5 boroughs through `fetchAddressSuggestions`) + Queens `120-55` through `fetchAddressSearch` | COVERED |
| AS-9 edit cancels superseded in-flight; stale never overwrites | `autocomplete.test.tsx` "ignores a stale suggestion response…", cancellation suite (abort on edit/pick/unmount, A→B→A sequence-guard, superseded reply dropped); `address-search.test.ts` abort tests; `address-resolution.test.tsx` S7 superseded | COVERED |
| AS-10 ZoLa primary, PLUTO demoted, dataset retained, honest absence, M5-T030 green | `provenance-link.test.ts` `zolaLotUrl` valid/hostile/invalid + `sourceFactLinks` conflict/wrong-lot; `provenance-disclosure.test.tsx` "ZoLa PRIMARY / raw PLUTO demoted", conflict/non-PLUTO/invalid-BBL absence; `sections.test.tsx` `expectLotLinks` (ZoLa first) + wrong-lot/wrong-source/conflict guards; `source-links.test.tsx` `expectLotLinks` + M5-T030 wrong-lot/different-source/conflict + real ESB capture | COVERED |
| AS-11 dated live smoke, orchestrator-captured | By design NOT deterministic; recorded in `M5-T032-orchestrator-seam-evidence.md` + producer report | N/A (correct) |

### Negative-path checklist (all present)
Repeated 503s ✓ · malformed payload + 129KB size cap ✓ · cancellation (abort on edit/pick/unmount + A→B→A sequence guard) ✓ · Queens hyphenated `120-55` (both endpoints) ✓ · five boroughs (`it.each` in two suites) ✓ · rate-limit vs source-failure distinction ✓ · candidate BBL never consumed (`not.toHaveProperty("bbl")`) ✓.

### M5-T030 guard suite
Still exists and runs: `source-links.test.tsx` (imports `M5-T030-esb-captured-fact.json`); wrong-lot, wrong-source (borrowed-metadata), same-source dataset-conflict, and re-render wrong-lot guards preserved and **extended** to also assert `zola-lot-link` absence alongside `Current PLUTO record (JSON)` absence. No M5-T030 negative case was deleted or loosened.

### [ORCH-CORRECTED] audit — all assert the NEW contract, none weaken
- `provenance-disclosure.test.tsx:8` — legacy PLUTO-first test rewritten to the D-064-R005 **ZoLa-first** contract: asserts `getAllByRole("link")[0] === zola` (primary) AND `current` PLUTO link still present (demoted). Strengthened.
- `sections.test.tsx:260` — mechanical `querySelectorAll<HTMLElement>` typing so `indexOf` compiles; the primary-first assertion `indexOf(zola) < indexOf(raw)` is preserved.
- `provenance-link.test.ts:184` — double-cast on a deliberate invalid-shape probe; the fail-closed `zolaUrl).toBeNull()` assertion is preserved.
- `architect-workspace.spec.ts:220` (e2e) — replaced the single generic "busy" expectation with the distinct rate-limited copy for a mocked 429. Strengthened.
- `AddressResolutionScreen.tsx:118` is a source-side remount-nonce comment, not a test change.

### Findings
- **F1 (advisory, non-blocking):** AS-3 says a valid-after-deadline timeout should *offer an explicit full-address search action*. The unit layer proves the timeout classification is terminal with no stacked deadline, and the timeout copy is asserted; the `full-address-search` affordance is directly asserted only on the no-match/empty path, not specifically on the timeout status. Coverage of AS-3's core invariants is strong; consider one assertion that the `/search` button is offered on the timeout status. Not a gate blocker.

No FAIL-class defects. Test-to-scenario mapping is complete and deterministic, negative paths are thorough, the M5-T030 guards are intact and extended, and every `[ORCH-CORRECTED]` edit tightens rather than loosens the contract.

**VERDICT: PASS** (advisory F1 for a future increment).
