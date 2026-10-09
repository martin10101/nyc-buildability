# M5-T016 producer report — Address Confirm card + ZoLa deep-link + handoff (Packet 2)

- Task: M5-T016 (frontend-engineer, orchestrator-executed producer; ADR-005)
- Spec: `docs/design/address-entry-confirm-design-spec.md` sections 1, 2-resolved, 3, 4, 6-Packet-2
- ZoLa URL authority: `docs/design/zola-deeplink-url-confirmation.md` (preserved researcher return, 2026-09-12)
- Packet: `project-control/tasks/M5-T016.json` (exact-file allowed_paths; deps [M5-T015 — ACCEPTED 184th])

## 1. What was built (all inside allowed_paths)

| File | Role |
|---|---|
| `AddressConfirmCard.tsx` (new) | The thin confirm card: question heading (focus target), canonical address large, BBL+BIN, ZoLa link, lot-outline honesty placeholder, collapsed "Where this came from" disclosure, not-verified posture, Continue handoff, "Not my property". |
| `AddressOutcomeCards.tsx` (new) | BYTE-PRESERVING extraction of every Packet-1 outcome/error card + the failure-primitive clones (G3 F4 concurrence). Only module boundaries moved; markup/copy/testids identical. `Meta` is exported for the confirm card. |
| `AddressResolutionScreen.tsx` (slimmed) | Keeps ONLY the state machine + loading card; `resolved`/`resolved_with_warnings` now route to the confirm card; new `notMyProperty` (clear result, RETAIN form values, focus street input). 282 raw lines — back under every modularity threshold. |
| `address-api.ts` (additive) | View extension for the disclosure: `provenance.endpointHost` (HOST only — the full endpoint URL, which carries request params, is never surfaced as a URL), bounded `requestParams` pairs, bounded `sourceFacts` display rows. `confidence` deliberately NOT mapped (spec §4: never a badge). Existing discrimination/bounding untouched. |
| `__tests__/address-confirm.test.tsx` (new) | The Packet-2 pack (11 tests): S1 routing/shape + warnings-above-Continue DOM order; S2 ZoLa discipline (exact `/bbl/` href, invalid → honest absence, HOSTILE BBL → no links + sweep); S3 handoff href purity; S4 not-my-property; S5 disclosure + not-verified + withheld-facts; S6 hostile-resolved fixture (discharges M5-T015 G5 F-2). |
| `__tests__/address-resolution.test.tsx` (updated) | Stub tests replaced with confirm-card routing assertions (the stub testids are asserted GONE); every other Packet-1 test byte-unchanged except the `address-resolved`→`address-confirm-card` testid retarget; source scan extended to the two new files + `next/link` allowlisted; S5 matrix gains a DISTINCTIVE body-copy phrase per state (M5-T015 G4 finding-3 carried item). |

## 2. The two URL contexts (the packet's core risk)

Both hrefs are built EXCLUSIVELY from `validateBblInput(view.canonical.bbl).canonical` — the client
re-validation (belt-and-suspenders over the server's `normalize_bbl`), applied to a value that
already passed `boundedToken`. ZoLa uses the CONFIRMED `/bbl/<canonical>` convenience route (module
constant `ZOLA_BBL_URL_PREFIX`; verified from the labs-zola router source + live checks — see the
research doc; ZoLa's SPA answers 200 for ANY path, so this client gate is the only guard). The
handoff is `/property/confirm?bbl=<canonical>` (the existing step-2 contract; `ConfirmEntry` reads
the param on hydration — verified in `app/property/confirm/page.tsx`). A failing/hostile BBL renders
NO link + honest absence copy; S2/S3/S6 drive exact-equality and hostile fixtures through both.

## 3. Design decisions a reviewer should challenge

1. **Confirm card keeps testids `resolved-bbl`/`address-warnings`/`facts-withheld`** from the
   Packet-1 resolved card (continuity for consumers) but the card root is `address-confirm-card`;
   the Packet-1 stub testids are asserted ABSENT.
2. **Extraction scope**: `ResolvingCard` stayed in the screen (loading state, not an outcome);
   `ResolvedCard` was not moved but SUPERSEDED by the confirm card (its warnings block and BBL
   line live on in the confirm card, byte-similar).
3. **Packet-1 test changes are exactly two kinds** — the resolved-path tests updated to the new
   routing (S1 of this packet legitimately replaces the stub behavior), and the mechanical
   `address-resolved` → `address-confirm-card` retarget (5 occurrences). NO assertion was weakened;
   the S5 matrix and source scan were STRENGTHENED. Reviewers should diff the test module to
   confirm.
4. **Disclosure shows endpoint HOST only** (`hostOrNull` via `new URL().host`), never the full URL:
   the full endpoint string plus params would be a URL-ish display of caller-typed text (packet
   risk 3). Params render as bounded key/value TEXT rows.
5. **"Not my property" retains form values** — "back to [Address entry]" (spec flow) means back to
   an editable entry, not a wipe; S4 pins retention + focus + announcer silence + no fetch.
6. **OWNER NOTE (report-only, M5-T015 G5 F-1)**: the frontend flag env var (`INTERNAL_RULE_EVAL_UI`
   + `?ruleeval=on`) differs from the backend's `INTERNAL_RULE_EVAL_ENABLED`; spec §6 wanted one
   flag. Renaming is deploy-affecting — an owner decision, deliberately NOT changed in this packet.

## 4. Scenario → test mapping (named mutants)

| Scenario | Test(s) | Named mutant it kills |
|---|---|---|
| S1 confirm routing | confirm S1 test 1 + resolution S2 test 1 | stub survives; heading not focused; BBL not fixture-derived |
| S1 warnings order | confirm S1 test 2 | warnings hidden, below Continue, or gating (compareDocumentPosition + presence) |
| S2 ZoLa | confirm S2 tests 1–3 | href from unvalidated/reflected data (exact-equality + hostile-BBL absence + href sweep); wrong route shape; missing noopener |
| S3 handoff | confirm S3 | extra document data in the query string; handoff without validation |
| S4 return to entry | confirm S4 | value wipe; focus drop; phantom announcement; spurious refetch |
| S5 disclosure | confirm S5 tests 1–3 | open-by-default; full endpoint URL leaked; ids conflated; params/facts unrendered; a "Verified" badge; withheld reason hidden; retrieved-at clause dropped; disclosure GRC line dropped (both added by the G4 C1 correction) |
| S6 hostile resolved | confirm S6 | escape via normalized street/borough/params/fact values; any unexpected anchor |
| S7 extraction neutrality | resolution module (all non-resolved tests byte-unchanged) + CI | extraction changing card markup/copy/behavior |
| S8 deps/tokens | extended source scan (+`next/link` only) + git diff + CI | new package import; new CSS token |
| body-copy matrix | resolution S5 `it.each` 4th column | copy transposition among same-HTTP states |

## 5. Verification posture (CI-only; thin client)

CI `web` + `web-e2e` on the pushed head are the executable authority (packet
documented_test_commands). Local checks run: `python tools/modularity_check.py --check`
(AddressResolutionScreen.tsx back under thresholds after extraction; failures 0) and the staged-set
== allowed_paths scope check. The named-mutant table above is the reviewers' static red-half
(M5-T014/M5-T015 posture).

## 6. Rework addendum (G4 C1 correction)

The four-gate wave returned G1/G3/G5 PASS and G4 PASS with required correction C1: the S5
disclosure test asserted neither the retrieval timestamp nor the in-disclosure Geosupport
return-code line. Corrected in one bounded test-only commit: the S5 test now asserts the
bounded rendering of the fixture `retrieved_at` (boundedToken drops ":"/"+" — the assertion
derives the bounded form from the fixture, so it stays fixture-bound) and the full
"Geosupport return codes: <grc> / <grc2>" line. Report-hygiene advisories fixed in the same
commit: test count 10→11 (G1 A1 / G3 adv-4 / G4 F4), screen line count 306→282, S5 mutant
row extended with the two C1 mutants. No production source changed in the rework.
