# M5-T046 producer report (bounded resubmission) — address-to-lot identity honesty (DB-026)

Producer: frontend-engineer. This revision closes ONE collection gap and expands NO
implementation scope: the prior submission's primary source evidence was lost behind a truncated
bundled patch, so the reviewer could not inspect the equality gate, the corpus tests, the
registry comparison-shape, or the production call-sites. The fix is NOT re-embedding long
verbatim excerpts in this report (the packet's REPORT DISCIPLINE forbids that) — it is to have
the supervisor assemble the packet so each changed FILE, the corpus, and the committed `ztldb.json`
are visible as **per-file, digest-bound source sections** (§1), never one bundled diff that
truncates. This report references source by `path:line`; it does not re-transcribe it.

The assertions below are producer claims to be verified against those collected source sections and
against CI — they are not independent source verification and must not be read as self-certified.
Web behavior proves ONLY in CI on the pushed head plus the AS-8 human-journey walkthrough on that
head (thin client): treat every web test result as `unknown` until the orchestrator captures web CI
AND AS-8 on a revision containing these working-tree changes. The sole local command is the
documented modularity check (§9).

## 0. Deliverable status (honest split — LIVE objective UNRESOLVED, routed to orchestrator)

| # | Deliverable | State |
|---|---|---|
| 1 | Equality-gate library in `address-search.ts` (`resolveLotFromGeoSearch` / `normalizeStreetForMatch`) | authored; unit tests authored (CI `unknown`) |
| 2 | Confirm-arc entered-vs-matched display + raw-typed-input preservation | authored (LIVE, in-scope); tests authored (CI `unknown`) |
| 3 | Case-1 offline corpus regression (`address-search.test.ts`) | authored (CI `unknown`) |
| 4 | GeoSearch source-registry draft (`geosearch.json`) mirroring the committed shape | authored |
| — | **LIVE GeoSearch→lot protection wired into a real promotion** | **UNRESOLVED — substantiated scope conflict; NO in-scope live promotion point exists (§5/§8); orchestrator adjudication required** |

The headline packet objective ("close the DB-026 identity gap in the LIVE address arc") is **not**
claimed complete and is **not** silently narrowed by this unit. Deliverables 1–4 are a correct,
tested library primitive, an offline regression, an in-scope live confirm-arc display with
typed-input preservation, and a registry draft. The one thing the allowed paths cannot do without
breaching a binding preservation is wiring the gate as a LIVE lot authority — §8 states the exact
conflict and routes it. This producer neither self-accepts a reduced objective nor invents a new
authority path (a client-side degraded-mode promotion).

## 1. COLLECTION COORDINATION (the fix for the truncated-patch gap) — READ FIRST

Ask (ADR-005 — the orchestrator/supervisor captures evidence and computes digests; this producer
runs no hashing command and commits nothing):

1. Capture **each file below as its own source section with its own sha256**, computed over
   **LF-normalized** bytes (the Windows checkout is CRLF-smudged; a raw digest will differ —
   PROGRAM_KNOWLEDGE "LF-normalize before hashing checkout files").
2. Do **not** rely on a single unified diff that can truncate and drop the equality gate.
3. Include the two read-only comparison/corpus sources so the gate and the registry are checkable
   against their basis; they are outside this task's `allowed_paths` and are unchanged by this unit.

| Source section | Role | In allowed_paths? |
|---|---|---|
| `apps/web/src/lib/address-search.ts` | equality gate + normalization (DB-026 section) — §2 | yes (changed) |
| `apps/web/src/lib/__tests__/address-search.test.ts` | byte-faithful corpus regression — §3 | yes (changed) |
| `docs/research/source-registry-drafts/geosearch.json` | source-registry draft — §4 | yes (changed) |
| `apps/web/src/components/architect/AddressAutocomplete.tsx` | raw-typed-text capture on pick — §6 | yes (changed) |
| `apps/web/src/components/architect/__tests__/autocomplete.test.tsx` | onPick raw-text test — §6 | yes (changed) |
| `apps/web/src/components/address/AddressResolutionScreen.tsx` | threads `typedInput` — §6 | yes (changed) |
| `apps/web/src/components/address/AddressConfirmCard.tsx` | entered-vs-matched display — §6 | yes (changed) |
| `apps/web/src/components/address/__tests__/address-confirm.test.tsx` | confirm-arc journey tests — §6 | yes (changed) |
| `docs/research/db026-address-to-lot-fixture-capture.md` | the 8-capture corpus (fixture provenance) — §3 | no (read-only basis) |
| `docs/research/source-registry-drafts/ztldb.json` | committed shape the draft mirrors — §4 | no (read-only basis) |
| `project-control/reports/M5-T046-producer-report.md` | this report | yes (evidence carrier) |

`apps/web/src/lib/architect/use-address-suggestions.ts` is an **unchanged** consumer named in the
call-path (§5); include it only as a read anchor if a reviewer wants it.

## 2. Equality-gate implementation (`apps/web/src/lib/address-search.ts`) — by reference

DB-026 section appended below the preserved M5-T032 suggestion exports (the suggestions path is
untouched). Verify in the collected §2 source section:
- `normalizeStreetForMatch` (`:257`, regex `ORDINAL_SUFFIX` `:249`): upper-case, whitespace-collapse,
  fold a digit-run's ST/ND/RD/TH ordinal — deliberately narrow, fails unclear cases closed.
- `resolveLotFromGeoSearch` (`:299`): the equality gate at `:320`–`:321` (exact housenumber; normalized
  street) and the `pad.bbl` identity bind at `:322`–`:325` (canonical 10-digit or honest no-match).
- `match_type`/`confidence` are READ onto the result (`:336`–`:337`) but NEVER compared.
- `readParsedInput` (`:264`) defaults the reference parse to the body's own
  `geocoding.query.parsed_text`; `readPad` (`:277`) tolerates absent pad/bin/version so
  `/autocomplete` bodies (no `confidence`/`match_type`) still parse and gate.
- A gate failure returns the existing `{ kind: "no_match" }` outcome — never a silently wrong lot.

## 3. Corpus regression + fixture provenance (`address-search.test.ts`) — by reference

`describe("DB-026 …")` at `:218`. Fixture constants at `:220`–`:230`
(`SEARCH_1279_37_STREET_SIZE3`, `SEARCH_1279_37TH_STREET`, `SEARCH_3622_13_AVENUE`,
`SEARCH_NONEXISTENT_STREET`, `SEARCH_OUT_OF_RANGE_HOUSE`, `AUTOCOMPLETE_1279_37_ST`) are the
**verbatim minified server bodies** captured 2026-09-19 UTC (keyless GET, 8/8 HTTP 200, no auth)
and saved by the orchestrator to `docs/research/db026-address-to-lot-fixture-capture.md`
(§1/§2/§3/§4a/§4b/§5). The load-bearing hazard the corpus proves: the true hit (`bbl 3052960043`),
the nonexistent street (`zzqqxx` → `1279 53 STREET`, `bbl 3056627501`), and the out-of-range house
(`99999` → `207 37 STREET`) all return HTTP 200 at the **identical** `confidence:0.8 /
match_type:"fallback"` — so only field equality can refuse the two wrong lots. Assertions map to
scenarios: AS-1 `:233`, AS-2 `:249`, AS-3 `:256`, AS-4 `:275`, AS-4 never-consult `:284`, AS-5
`:298`. Confirm-arc journeys live in `address-confirm.test.tsx` and the onPick raw-text test in
`autocomplete.test.tsx` (§6).

## 4. Registry draft comparison-shape (`geosearch.json` vs committed `ztldb.json`) — by reference

`docs/research/source-registry-drafts/geosearch.json` is a top-level JSON array of one object
mirroring the committed `ztldb.json` key set. Producer-authored comparison map (verify against the
two collected §4 source sections):

| Committed `ztldb.json` key | `geosearch.json` key | Note |
|---|---|---|
| `source_id`, `agency`, `name`, `official_url`, `source_type`, `api_dataset_identifier` | same | present |
| `authentication`, `rate_limits`, `update_frequency`, `geographic_coverage` | same | present |
| `fields_available.columns[]` | `fields_available.properties[]` | per-column vs per-feature parallel |
| `fields_available.assignment_rules_verbatim_basis` | `fields_available.match_discipline_verbatim_basis` | verbatim-basis parallel (the equality gate is the documented match discipline) |
| `fields_available.null_semantics` | `fields_available.null_semantics` | both present (key-absence ≠ value; `:36`) |
| `last_successful_ingestion`, `latest_source_version`, `health_status` | same | present |
| `known_limitations[]` (`:43`), `fallback_source`, `open_questions[]` (`:55`) | same | present |
| — | `connector_implementation` | additive (permissive-suggestion vs gated-promotion split; no new field type invented) |

Freshness discipline: the ONLY currency signal is the body-only `addendum.pad.version = "26c"`;
there is **no Last-Modified and no dataset-version HTTP header** (fixture §8), recorded in
`update_frequency`/`latest_source_version`. The record-address gap is in `known_limitations` +
`open_questions` OQ-5 (§7). AS-9 satisfied.

## 5. Production call-sites + absence-of-live-promotion evidence (bounded; verify in source)

Each path below is grep-/read-verified in source at HEAD — a producer claim to check against the
collected sections, not a self-certified fact:
1. Type-ahead: `AddressAutocomplete.tsx` → `useAddressSuggestions` (`use-address-suggestions.ts:16`)
   → `fetchAddressSuggestions` → GeoSearch `/autocomplete` → `parseAddressSuggestions`
   (`address-search.ts:58`), whose pushed suggestion `query` (`:73`) carries
   housenumber/street/borough/zip only — `addendum.pad.bbl` is **discarded** → permissive list.
2. Explicit full-address search: `AddressAutocomplete.runFullSearch` (`:126` → `fetchAddressSearch`
   `:136`) → GeoSearch `/search` → the SAME `parseAddressSuggestions` (bbl discarded) → permissive
   candidates; a candidate still requires an explicit user pick (`choose` `:110`).
3. Pick / manual submit → lot authority: `AddressResolutionScreen.runResolve` (`:146` →
   `resolveAddress` `:152`) → the **server** endpoint (`address-api.ts`,
   `/api/v1/address-resolution`). The canonical BBL comes from the server Geoclient path
   (M2-T021, OUT of scope); the GeoSearch feature's `pad.bbl` is never consulted as the lot
   authority on this path.
4. `resolveLotFromGeoSearch` importers: **none in production.** Repo-wide grep for the symbol
   returns exactly four files — its definition (`address-search.ts`), its test
   (`address-search.test.ts`), this report, and `geosearch.json`; no `.tsx`/production-`.ts`
   importer. The gate protects no live promotion today.

## 6. Confirm-arc display + typed-input preservation (LIVE; in-scope) — by reference

- `AddressAutocomplete.tsx` `choose` (`:110`) captures the RAW one-box `text` BEFORE `setText`
  (`:117`) rewrites the field, passing it as the second `onPick` arg (`:116`); `onPick` typed
  `(query, typedText)` at `:68`.
- `AddressResolutionScreen.tsx` threads it as `ResolutionResult.typedInput` (`:66`) through
  `runResolve(query, typedInput?)` (`:146`, set at `:159`) and hands it to `AddressConfirmCard`
  (`:251`).
- `AddressConfirmCard.tsx` `enteredInput` (`:96`) prefers `typedInput`, else falls back to
  `view.inputEcho` on the manual/BBL paths; trimming decides ONLY blank-vs-not, the ORIGINAL string
  renders through an escaped React text node (`:132`, no URL built from it). The in-place comment at
  `:80`–`:95` documents that this is a RECORD (no computed value implied) and that the PLUTO
  address-of-record gap is a reported discovery, not a built-around field. Closes scope 2/2(g).

## 7. Record-address channel gap (discovery, D-069 — not built around)

The lot's PLUTO/PTS address-of-record (`3622 13 AVENUE` for `bbl 3052960043`) is not carried by any
channel the confirm arc currently reads (the Geoclient channel does not carry it, and no existing
channel does). Per scope 2/2(g) AS-6 else-branch, this unit ships the entered-vs-matched increment
and reports the gap as a discovery — it does NOT add a server endpoint or contract field. Recorded
in `AddressConfirmCard.tsx:80`–`86`, `geosearch.json` `known_limitations` (record-address line), and
`geosearch.json` `open_questions` OQ-5.

## 8. Scope adjudication — substantiated conflict, routed to orchestrator (no self-accept)

**Determination (from the §5 verified facts, not inference):** an allowed-path integration CANNOT
satisfy the LIVE objective — "wire the equality gate so a user typing a nonexistent address is never
silently landed on a real but wrong lot" — while preserving BOTH the permissive suggestions AND the
Geoclient boundary, because the allowed-path surface contains **no live GeoSearch→lot promotion
point**:
- The two GeoSearch surfaces reachable from the allowed paths (`/autocomplete`, `/search`) both flow
  through `parseAddressSuggestions`, which structurally discards `pad.bbl` and produces a PERMISSIVE
  candidate list requiring an explicit pick (§5.1/§5.2) — and the preservation binding keeps
  suggestions permissive.
- The only node that resolves a pick/submit to THE lot is `resolveAddress` → the server Geoclient
  endpoint (§5.3), which is OUT of scope (M2-T021) and in a forbidden path (`services/api/`).
- `resolveLotFromGeoSearch` has no production importer (§5.4).

So the packet objective (1)'s premise — "the web GeoSearch client currently trusts the top /search
feature" and promotes it to a lot — does not hold at HEAD; the web client never promotes a GeoSearch
feature to a lot. Making the gate a LIVE authority would require either (A) a NEW client-side
GeoSearch lot-promotion that bypasses the server Geoclient — breaching the Geoclient boundary, the
permissive-suggestions preservation, and "never silently apply a default that materially changes a
scenario"; or (B) a client→server transform / contract-shape change — breaching "NO contract change
/ NO services/api change." Both are binding-preservation breaches, so neither is in-scope, and this
unit wires **no** new authority path.

Routed to the orchestrator (this unit does NEITHER unilaterally, invents no degraded-mode path):
- (A) Accept deliverables 1–4 as the contracted library + display + registry + input preservation,
  recording that server-Geoclient-mediated resolution is the interim live authority and that no
  unsafe live GeoSearch promotion exists to protect; OR
- (B) Authorize a NEW dependent task that revisits the OUT-of-scope constraints to introduce a
  client-side GeoSearch cross-check/degraded-mode promotion and wire the gate there (new
  user-facing design → product-design-director + a G3 human-journey walkthrough).

The LIVE objective stays **unresolved** until the orchestrator rules; a reduced objective is **not**
treated as accepted by this producer.

## 9. Local verification, preservation, discovery

- Local (documented, broker-approved): `python tools/modularity_check.py --check` → `selected 445
  files; failures 0; warnings 21`; none of the 21 warnings are in this packet's touched files. No
  npm/node run locally (thin client); web + AS-8 results are `unknown` until the orchestrator
  captures web CI + the HJ walkthrough on the pushed head containing these working-tree changes.
- Preservation: touched only `allowed_paths`. NO `services/api` change; NO contract-shape change
  (Geoclient server path untouched); no `packages/contracts`; no PropertyOverview /
  AnalysisIdentityNotice / ReportView or their tests (M5-T045-owned); the `onPick` type change is
  contained to `AddressAutocomplete.tsx` + its two in-scope callers. No new dependency; no
  package.json change. M5-T032 reliability outcomes and permissive autocomplete UX unchanged.
- Discovery (D-069): the BBL→PLUTO.address record-address lookup (§7) is a new server channel,
  deliberately NOT added; recorded as `geosearch.json` OQ-5 + its `known_limitations` line.
