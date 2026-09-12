<!-- Design-director return preserved VERBATIM by the orchestrator (report-preservation
rule; transport entity-decoding applied: &lt; -> <, &gt; -> >, &amp; -> &). Author: independent
product-design-director subagent, returned 2026-09-12. Implementation packets are contracted
from this spec; Packet 3 (real lot outline / MapLibre) is ON THE OWNER-REVIEW EXPANSION HOLD
(.claude/rules/expansion-agent-dispatch-hold.md) and is recorded here as deferred, not planned. -->

DESIGN SPEC: address entry + confirm screen

**Scope** — the entry flow that replaces ten-digit-BBL typing with a street address: address form → resolution outcomes → a Confirm ("is this the right lot?") screen → handoff by BBL into the existing property flow. Design only; the orchestrator contracts implementation. Ground truth read: `services/api/app/api/v1/address_resolution.py` (the transport contract), `apps/web/src/components/property/PropertyLookup.tsx` + `FailureState.tsx` (the proven state machine and failure idioms to reuse), `apps/web/src/components/confirm/ConfirmScreen.tsx` (the existing step-2 card and honesty copy), `apps/web/src/lib/bounded.ts` (the reflection-hardening primitives), `apps/web/src/components/compare/NoScenarioBlock.tsx` (absence/`stated()` idiom), `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`, `docs/MVP_AGENDA.md` (A2 rows 3–4, B item 3–4).

This design **replaces the disabled "Address (not yet available)" input** at `PropertyLookup.tsx:300-316` (B-004 is resolved; the key is provisioned). It does not fork a new state machine — it clones the one that is already gated, reviewed, and shipped.

---

## 1. Information architecture + flow

The address flow is a front door that sits *before* today's Property→Confirm→Compare→Evidence flow. Its only job is to produce a **validated BBL** and hand off. One dominant decision per view.

```
[Address entry] --resolve--> (outcome) --resolved--> [Address Confirm: is this the right lot?]
                                                            |                         |
                                            "Yes, continue" |                         | "Not my property"
                                                            v                         v
                              hand off by BBL -> /property/confirm?bbl=<canonical>   back to [Address entry]
```

The Address Confirm screen is deliberately **thin**: canonical address, BBL, ZoLa deep-link, lot-outline placeholder, two buttons. It does *not* duplicate the rich compact property card — that already exists at `ConfirmScreen.tsx` (step 2) and is reached by BBL after this gate. Rationale: MVP_AGENDA H warns the current screens "read like a compliance document"; the address gate must stay a single clean confirmation, and one dominant action ("Continue with this lot").

**State machine** (mirrors `PropertyLookup` exactly — same `AbortController` + monotonic `requestSeq` guard + `OutcomeAnnouncer` + `[data-outcome-heading]` focus move + `retryFocus`):

| State | Enter on | Renders | Exits to |
|---|---|---|---|
| `idle` | mount | address form only | `resolving` on submit |
| `resolving` | submit / retry / suggestion pick | `LoadingStages`-style card | one outcome |
| `resolved` \| `resolved_with_warnings` | 200, `status` in success class | Address Confirm card | handoff / `idle` |
| `ambiguous` | 200, `status="ambiguous"` | verbatim suggestion chooser | `resolving` (re-resolve on pick) |
| `not_found` | 200, `status="not_found"` | recovery card + both GRCs | `idle` / retry |
| `rejected` | 200, `status="rejected"` | recovery card + both GRCs | `idle` |
| `unrecognized_status` | 200, `status` unknown | honest "form we don't recognize" | `idle` / retry |
| `error.*` | non-200 (matrix) | matched error card | retry where safe |

Branching is on **`document.status` for the 200 family** (never on field presence — the docstring is explicit) and on **`error.error_type` for the non-200 family**. The two `document_kind` values (`address_resolution` vs `address_resolution_error`) are the top-level discriminator, exactly as `api.ts` discriminates today.

The last good result survives a subsequent client-side no-op submit (the `PropertyLookup` D5 behavior); a superseded request resolves silently (its `aborted` analogue renders nothing).

---

## 2. Every resolution outcome — screen treatment + honesty rules

**resolved / resolved_with_warnings.** Route to the Address Confirm card (§ below). For `resolved_with_warnings`, the warning text renders **beside the result, above the Continue button**, never buried: a `completeness-banner`-style block, `role="status"`, plain-language lead + the source's `grc_message`/`grc2_message` verbatim (escaped, bounded). Warnings never gate Continue but are never hidden to make the screen look clean.

**ambiguous.** The dominant decision becomes "which of these?" Render `selection_policy: "caller_selects"` **literally**: the source's `suggestions[]` in **source slot order, verbatim (escaped, bounded)**, as an unstyled radio-group / listbox with **no default selection, no visual pre-highlight, no "recommended" chip**. The platform picks nothing. A "Use this address" button is disabled until the user actively selects. On selection the flow returns to `resolving` and **re-resolves** using the chosen suggestion (the exact re-query input is a connector-contract detail the implementation packet must confirm from the `AddressResolution` suggestion shape — flag it). Copy: "The city's address service returned more than one possible match. Choose the correct one — the platform will not guess for you."

**not_found.** A 200 result, not an error: "The city's address service has no record matching what you entered. This is an answer from the official source, not a system failure." Show **both** `grc`/`grc_message` and `grc2`/`grc2_message` (escaped) under a `failure-meta` line. Never a dead end: primary affordance "Edit the address," secondary "Look up by BBL instead" (the existing BBL form remains reachable).

**rejected.** Same structure as not_found but framed as "the city's address service rejected this address as unresolvable," both GRC codes + messages visible (escaped). Recovery affordances identical.

**unrecognized_status.** Honest treatment per `UnexpectedResponseState`: "The city's address service answered in a form this platform does not recognize. The response was not trusted or interpreted." Show the raw `status` token via `boundedToken` (a plain copyable token), correlation id, Retry. Never coerce an unknown status into "not found."

**Error matrix** (`document_kind:"address_resolution_error"`, branch on `error.error_type`) — user language, what-to-do-next, correlation id surfaced, retry only where retrying can help, **never blame the user for server-side key problems**:

| state (HTTP) | Title | Body posture | Retry? |
|---|---|---|---|
| `invalid_input` (422) | "That address can't be read yet" | The connector is the validation authority; render `error.message` (escaped) as the specific reason. Points at the field. | No — edit and resubmit |
| `key_missing` (503) | "Address lookup isn't configured on our side" | Explicitly a server configuration gap — "Nothing is wrong with your input." | No |
| `auth_failed` (502) | "Our access to the city's address service was refused" | Server-side credential problem, not the user. | Retry (may be transient) |
| `rate_limited` (503) | "The city's address service is throttling us" | "Nothing is wrong with your input." If a bounded `retry_after` is present, show it ("try again in N…"); it is already re-bounded server-side and dropped if unsafe. | Retry (respect `retry_after`) |
| `source_unavailable` (503) | "The city's address service is unavailable" | Outage after retries; retry safe. | Retry |
| `timeout` (504) | "The city's address service timed out" | Retry safe. | Retry |
| `malformed_response` (502) | "The city's address service sent an unreadable response" | Needs platform attention; retry likely same. | Retry (low value) |
| `internal_error` (500) | "Something went wrong on our side" | "Your input was fine." | Retry |

Every error card ends with the `Meta` line — `Reference id for support and server logs: <correlation-id>` (`boundedToken`, `data-testid="correlation-id"`) — reusing `FailureState.tsx`'s exact component. The flag-off generic 404 (feature disabled) is **outside** this matrix: it is byte-indistinguishable from an unmounted route, so the UI must **not** render any "address lookup failed" card for it — it must never have mounted the address surface at all (§6 flag posture).

---

## 3. Render-safety contract (the render-time checklist)

The endpoint transports caller-typed text verbatim and names its own unsanitized surfaces in `unsanitized_reflected_input.fields`. React JSX text nodes HTML-escape by default; that is **sufficient for every text-node render** and is the primary defense. Each named field, and how it is contained:

| Reflected field | Render context | Treatment |
|---|---|---|
| `input_echo.{house_number,street,borough,zip}` | JSX text | text node (auto-escaped) + `boundedText()` for length/control-char caps |
| `grc_message`, `grc2_message` | JSX text | text node + `boundedText()` |
| `suggestions[]` | JSX text in `<li>` | text node + `boundedText()` each; the React `key` uses the **array index**, never the suggestion string; never placed in `href`/`value` used as a URL |
| `canonical.street_name_normalized`, `canonical.borough_name` | JSX text | text node + `boundedText()` |
| `provenance.request_params` | JSX text inside provenance disclosure | rendered as escaped key/value text only, never executed, `boundedText()` per value |
| `source_facts[].original_value` / `normalized_value` (street/borough) | JSX text in provenance table | text node + `boundedText()` |

Hard rules (all already house policy, `bounded.ts:5`): **never `dangerouslySetInnerHTML`; never place any reflected field into an `href`, `src`, `style`, `srcset`, or any attribute/URL context; never into a log line** (transport already keeps them out of headers/logs — the client must not re-introduce them).

**ZoLa deep-link** is the one attribute/URL context and it is built **only from the validated canonical BBL, never from reflected text.** Client re-validates `canonical.bbl` with the existing `validateBblInput` (belt-and-suspenders over the server's `normalize_bbl`), splits the 10 digits into borough/block/lot, `encodeURIComponent`s each, and only then constructs the ZoLa URL (`https://zola.planning.nyc.gov/l/lot/<boro>/<block>/<lot>` — confirm exact path shape in the implementation packet). **If the BBL fails client re-validation, no link is rendered** — an honest absence ("the city's map link needs a valid BBL, which this result did not provide"), never a link built from anything the source echoed. This makes a hostile reflected-text-in-a-BBL-field fixture provably unable to reach an anchor's `href`.

---

## 4. Progressive disclosure + provenance

`source_facts[]` and `provenance` surface only behind a collapsed **"Where this came from"** affordance on the Address Confirm card, reusing `ProvenanceDisclosure` / `provenance-details` / `provenance-body` (same `<details>`/`<summary>` idiom the property screens use). Collapsed by default — analysts never see connector internals up front (`PRODUCT_FLOW` UI rule; `frontend-web.md`). Inside: source id, endpoint host, retrieval timestamp, both GRCs, the connector's own correlation id (distinct from the HTTP one — label both honestly), and the response digest.

**Not-verified posture.** Nothing on the address gate is "Verified." A single quiet line consistent with platform vocabulary: "This is an official address match from the city's Geoclient service, transported exactly as received. It has not been through the platform's rule review." `source_facts[].confidence` is 1.0 (deterministic retrieval) and must **never** be mapped to a coverage label or a "verified" badge — it means "we retrieved this," not "we vouch for it." If `source_facts_not_emitted_reason` is present (BBL failed canonical validation), show it verbatim (escaped): the facts were **withheld and said so**, never faked.

---

## 5. Component inventory + design tokens

**Reused as-is** (no new CSS tokens): `card`, `section-title`, `section-note`, `primary-button`, `secondary-button`, `text-input`, `field-group`, `field-label`, `field-hint`, `inline-error`, `failure-state`, `failure-title`, `failure-meta`, `completeness-banner`, `missing-list`, `provenance-details`/`provenance-body`, `confirm-grid`/`confirm-row`, `next-action`. Reused components: `LoadingStages`, `OutcomeAnnouncer`, `ProvenanceDisclosure`, `InternalBanner`, and the `FailureTitle`/`Meta`/`RetryButton` primitives from `FailureState.tsx`. Reused libs: `bounded.ts` (`boundedText`, `boundedToken`), `announce.ts` (extend `announcementForOutcome` for the new statuses).

**Genuinely new** (small): `AddressForm` (three inputs: house number, street, and a borough select **or** zip — one row, borough as a native `<select>` of the five boroughs so it needs no reflected text; zip as an optional text input); `AddressResolutionScreen` (the state-machine host, a near-clone of `PropertyLookup`); `SuggestionChooser` (no-default radio-group honoring `caller_selects`); `AddressConfirmCard` (canonical address large, BBL, ZoLa link, lot-outline placeholder); `address-api.ts` (fetch + discriminated-outcome mapping, mirroring `api.ts`'s pair-matrix discipline and bounded reflection). One new token pair may be justified: a `.suggestion-option` layout class — reuse `missing-list` spacing rather than invent if possible.

**Accessibility (G3 acceptance evidence, not extras):** on every outcome change, focus moves to `[data-outcome-heading]` (the shared idiom); a single persistent `OutcomeAnnouncer` (`aria-live`) announces each arrival exactly once (cleared while resolving so a repeated identical outcome re-announces). The suggestion chooser is a labeled radio-group, fully keyboard-selectable, no default checked, "Use this address" disabled until a choice is made. Loading state uses the existing `LoadingStages` card; on retry, focus moves to the loading card (never dropping to `<body>`). Every input has a `<label>` + `field-hint`; errors are wired via `aria-describedby`.

**Empty-input handling.** The **connector is the sole validation authority.** The form submits plain strings; an empty/insufficient submit returns `invalid_input` (422) and renders as the `invalid_input` card with the connector's own message. The client does **not** replicate server address rules (there is no reliable client mirror for free-form addresses, unlike the 10-digit BBL). The only client guard is a trivial "enter a street to continue" that keeps the submit button inert when both house number and street are blank — a UX nicety, explicitly **not** a validation authority, and it never suppresses a 422 the server would have returned.

---

## 6. Packetization recommendation

Three packets; the orchestrator writes exact scenarios. All ship **behind `INTERNAL_RULE_EVAL_ENABLED`**, the same flag the endpoint is gated by. The UI must receive the flag from a Server Component prop (the `PropertyLookup` `ruleEvalEnabled` precedent) and, when off, render today's BBL-only form unchanged — it must never mount the address surface or fire the fetch (so the flag-off generic 404 is never even reachable, matching the endpoint's "indistinguishable from unmounted" contract).

**Packet 1 — Address entry + resolution outcomes + error matrix.** The form, `address-api.ts`, the state machine, and every outcome/error screen except the Confirm card (resolved routes to a stub handoff). Acceptance-scenario **themes**: every `STATUS_STATE_MATRIX` pair renders its documented treatment (one scenario per pair, incl. the unreachable-by-construction `request_budget_exceeded` as a not-emitted assertion); ambiguous shows suggestions verbatim in slot order with **no preselection** and re-resolves on pick; render-safety proven with a hostile-reflected-input fixture (script/markup in `street`, `grc_message`, and a suggestion — nothing executes, everything escapes, nothing reaches an attribute); correlation id surfaced on every error; retry present only where safe (respecting bounded `retry_after`); server-side key failures never blame the user; a11y focus-move + single announcement + keyboard suggestion selection.

**Packet 2 — Address Confirm card + ZoLa deep-link + handoff.** The confirm card (canonical address large, BBL, ZoLa link, lot-outline **placeholder**), the "Continue with this lot" handoff to `/property/confirm?bbl=<canonical>`, and the "Not my property" path back to entry. Acceptance **themes**: ZoLa `href` built **only** from a client-re-validated BBL (adversarial fixture: reflected text can never appear in the anchor; an invalid BBL yields no link + honest absence copy); provenance disclosure collapsed-by-default with connector internals; not-verified posture present; `resolved_with_warnings` shows warning text beside the result before Continue; handoff carries only the canonical BBL.

**Packet 3 (later increment, explicitly deferred) — real lot outline.** The lot outline is a **placeholder** in Packets 1–2: MapPLUTO geometry integration is not in scope here (the existing Confirm card already declares geometry "not yet retrieved," `ConfirmScreen.tsx:213-219`). Until then the honest stand-in is the ZoLa link (which shows the real, key-free outline) plus copy: "A parcel outline is not drawn here yet — a pin would mislead on corner and large lots (MVP_AGENDA B4). Open the city's ZoLa map above for the authoritative outline." Packet 3 renders the DCP/MapPLUTO geometry with MapLibre GL JS per `.claude/rules/3d-ui-expansion.md` when that connector lands; **it is on the owner-review expansion hold and must not be planned or started here.**

**Constraints honored:** no new npm dependencies; Next.js app-router idioms already in use (Server Component flag prop + `Suspense` + `useSearchParams`, as `confirm/page.tsx` does); nothing AI-generated enters any displayed value — every source string is transported verbatim and escaped; deterministic backend owns resolution, the UI only transports and renders.

**Assumptions / limitations flagged for the packets:** (a) exact ZoLa URL path shape must be confirmed before Packet 2; (b) the re-resolution input for a chosen ambiguous suggestion depends on the `AddressResolution` suggestion field shape — confirm from the connector contract; (c) `announce.ts` must be extended for the new statuses; (d) MVP_AGENDA F/H open decision (primary user = developer/architect/broker) does not affect this gate but will affect the downstream property card. I did not run any tooling (design-only, read-only scope); no files were written.
