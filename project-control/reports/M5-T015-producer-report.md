# M5-T015 producer report — address entry + resolution outcomes + error matrix (Packet 1)

- Task: M5-T015 (frontend-engineer, orchestrator-executed producer; ADR-005)
- Spec: `docs/design/address-entry-confirm-design-spec.md` sections 1–3, 5, 6-Packet-1
- Endpoint contract: `services/api/app/api/v1/address_resolution.py` (M2-T022, read-only)
- Packet: `project-control/tasks/M5-T015.json` (exact-file allowed_paths; deps [M2-T022])

## 1. What was built (all inside allowed_paths)

| File | Role |
|---|---|
| `apps/web/src/lib/address-api.ts` (new) | Typed client mirroring `api.ts` discipline: documented (HTTP,state) pair matrix verbatim from `STATUS_STATE_MATRIX`; 200 requires `document_kind:"address_resolution"`; bounded view (`boundedText`/`boundedToken`) built BEFORE render; discriminated outcomes incl. `aborted`/`client_timeout`/`network_error`/`unexpected_response`; merged abort+timeout controller. |
| `apps/web/src/components/address/AddressForm.tsx` (new) | Controlled inputs: house number, street, native five-borough `<select>` (no reflected text), optional ZIP. Zero validation — the connector is the sole authority; the ONLY inert condition is both house number and street blank (UX nicety, spec §5). Deliberately NOT disabled in flight (supersession is a supported flow, PropertyLookup precedent). |
| `apps/web/src/components/address/SuggestionChooser.tsx` (new) | `caller_selects` literally: source slot order, NO default selection, "Use this address" disabled until an active choice, labeled radio-group (native keyboard), index keys. Pick hands back `rawStreetName` (see §3.2). |
| `apps/web/src/components/address/AddressResolutionScreen.tsx` (new) | The PropertyLookup-clone state machine (AbortController + monotonic `requestSeq` + `[data-outcome-heading]` focus + `retryFocus` + D5 last-good-result + own `OutcomeAnnouncer` via `testId="address-outcome-announcer"`, the M4-T005 coexistence pattern) plus EVERY outcome/error card from the spec §2 tables. `resolved` renders an explicit Packet-2 STUB (disabled Continue + copy saying the confirm step ships next increment). |
| `apps/web/src/lib/announce.ts` (extended) | ADDITIVE: one import line + appended `announcementForAddressOutcome` block; every pre-existing line byte-unchanged (packet path note). |
| `apps/web/src/components/property/PropertyLookup.tsx` (edited) | Mount only: flag ON renders `<AddressResolutionScreen/>` above the BBL card and suppresses the disabled placeholder; flag OFF renders today's DOM byte-equivalently (the placeholder block is inside `{ruleEvalEnabled ? null : (…unchanged bytes…)}`). BBL state machine untouched. |
| `apps/web/src/components/address/__tests__/address-resolution.test.tsx` (new) | The S1–S8 pack, 20 tests — mapping in §4. |

## 2. Contract verification performed before writing code

Field names were re-verified against the endpoint source, not recalled: `_success_document` keys
(incl. `canonical.latitude/longitude`, `grc_reason`/`grc2_reason`, optional
`source_facts_not_emitted_reason`), the error body (`state`, `error.error_type/message/retry_after`),
and the connector's `_extract_suggestions` guarantee that every emitted slot carries a nonempty
`street_name` (empty slots are skipped connector-side; `street_code` optional). Borough is a free
string (≤32 chars) validated by the connector — the five-name native select emits values the
connector transports verbatim.

## 3. Design decisions a reviewer should challenge

1. **Failure primitives replicated, not imported.** `FailureTitle`/`Meta`/`RetryButton` are
   module-PRIVATE in `FailureState.tsx`, and that file is forbidden to this packet. The three
   primitives are cloned exactly (same classes, same `data-testid="correlation-id"`, same
   no-aria-live rule) in `AddressResolutionScreen.tsx` with a comment saying so. Exporting them
   would have widened scope for ~30 lines; the shared contract is the DOM shape, which S-tests pin.
2. **`rawStreetName` on `SuggestionView`.** The re-query contract is the suggestion's
   `street_name` VERBATIM, but the view's display string is bounded — so the view carries both:
   `streetName` (bounded, the only member that may reach the DOM) and `rawStreetName` (verbatim,
   goes ONLY to the fetch seam, URL-encoded by `URLSearchParams`). S6 asserts the hostile raw name
   reaches the seam verbatim and never materializes as markup.
3. **`request_budget_exceeded` stays typed.** Documented unreachable-by-construction from this
   endpoint (it passes no budget); the client types the pair anyway so an arrival renders as its
   own honest card instead of an undocumented surprise. Its S5 test states this posture.
4. **Loading card is local.** `LoadingStages` is BBL-lookup copy (and takes a `bbl` prop);
   the address flow gets a minimal `ResolvingCard` with the same focus contract (retry focus lands
   on it, never `<body>`). No new CSS tokens — `card`/`section-title`/`section-note` reuse only.
5. **Recovery affordances.** "Edit the address" refocuses the street input; "Look up by BBL
   instead" is a constant-fragment anchor `href="#bbl-input"` to the BBL form on the same page —
   the ONE anchor in the flow, never built from reflected text (the ZoLa link is Packet 2).
6. **Submit stays enabled in flight** (see AddressForm above) — superseding submits are part of
   the cloned state machine's contract; S7 exercises exactly that path.
7. **Two live regions coexist** on the flag-on property page (BBL announcer + address announcer)
   — the M4-T005 `testId` mechanism exists for precisely this; each announces only its own
   machine's arrivals, exactly once.

## 4. Scenario → test mapping (each with its named mutant)

| Scenario | Tests (describe/it in `address-resolution.test.tsx`) | Named mutant it kills |
|---|---|---|
| S1 flag posture | S1 both tests | removing the `ruleEvalEnabled ? null :` guard (placeholder + surface both render), or mounting the surface flag-off (fetch spy + testid asserts fail) |
| S2 resolved stub | S2 test 1 | rendering a live Continue (stub must be disabled + Packet-2 copy present); BBL not fixture-derived |
| S2 warnings | S2 test 2 | hiding warnings (role=status block + both fixture messages) or letting warnings gate the stub |
| S3 no-preselection | S3 test 1 | any default-checked radio, enabled Use button, reordered slots, invented `slot`/code fields |
| S3 re-resolve | S3 test 2 | re-querying anything but the verbatim `street_name` with the ORIGINAL house/borough (asserted at the fetch seam URL) |
| S4 honest non-success | S4 all three | dropping either GRC line; coercing an unknown status into not_found; dead-end cards (recovery affordances asserted) |
| S5 matrix complete | `it.each` over all 8 emitted pairs + 4 followups | wrong card per state; retry offered on invalid_input/key_missing; missing correlation id; blaming the user on key states; dropping retry_after; trusting an undocumented pair or a drifted 200 |
| S6 render safety | S6 tests 1–2 + source scan | any reflected string reaching an element/attribute (querySelector sweep + single-anchor assert + window sentinel); `dangerouslySetInnerHTML` anywhere; suggestion string keys; a new import specifier outside `react`/`@/`/`./` |
| S7 machine integrity | S7 all four | seq-guard removal (late first response overwrites), D5 removal (blank resubmit clears result or fires fetch), focus not moving (arrival + retry), announcer not clearing in flight (identical retry outcome silent) |
| S8 no new deps/tokens | S6 source-scan (module half) + CI (`web` lint/typecheck/build, `web-e2e` full suite) + git diff (package.json/lockfile untouched — forbidden paths) | — |

## 5. Verification posture (CI-only; thin client)

Per the packet's documented_test_commands there is NO local vitest (no `apps/web/node_modules`,
`docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`). The CI `web` (lint + typecheck + build) and
`web-e2e` (vitest + Playwright) jobs on the pushed head are the executable authority. The RED half
follows the M5-T014 posture: assertion-first commits are impractical at CI-cycle cost, so every
scenario names its mutant above and reviewers verify mutant-killing statically.

Local checks that CAN run were run: `python tools/modularity_check.py --check` → failures 0, no
address-file warnings (`AddressResolutionScreen.tsx` is 687 raw lines, under thresholds after
comment/blank stripping; single responsibility: the outcome-rendering table of one endpoint);
`git status` confirms the working set is exactly the packet's allowed_paths.

## 6. Self-review findings already fixed (disclosed for the wave)

- The submit button was initially disabled while a request was in flight — that would have made
  S7's superseding submit impossible and diverged from the cloned machine. Removed; comment added.
- Test fixtures originally inferred `null`-typed properties (TS would reject the warnings
  variant); fixture fields are now explicitly `string | null`.
- Suggestion views originally bounded the street name only — the verbatim re-query member
  (`rawStreetName`) was added before any test was run (see §3.2).

## 7. Out of scope / deferred honestly

Packet 2: AddressConfirmCard, ZoLa deep-link (exact URL shape to confirm), `/property/confirm`
handoff, provenance disclosure. Packet 3 (real lot outline / MapLibre): ON THE OWNER-REVIEW
EXPANSION HOLD — not planned, not started. `source_facts`/`provenance` render nowhere in Packet 1
(the client maps counts/ids for Packet 2's disclosure).
