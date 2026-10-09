# M5-T060 producer report — proposal editor UI (phase B3 slice 2, D-076) — REVISED evidence submission (rev 3)

Frontend increment: the first working **edit → run-check → read → save-variation** loop over the
accepted T057 route (`POST /api/v1/proposal-checks`). Authority is a numeric **EPSG:2263**
vertex/levels/walls draft; the recorded lot-outline map is composed **read-only** for context. No
map drawing, no client CRS transform, no scenario emission (the three deferred D-076-R003
owner-checkpoint questions). Production scope (the editor/report/variations/mount) is unchanged
from rev 1; rev 3 makes ONE additive change within the allowed test paths — a **separate AS-1
arithmetic coverage** in `proposal-check-report.test.tsx` (§2.1c) — and otherwise re-presents the
evidence per rev 2's bounded-slice form.

> **What rev 3 changes (one additive test; no production broadening).**
> Per the supervisor's requested action, rev 3 adds a **separate arithmetic coverage** that the
> rev-2 surfaces lacked: the earlier AS-1 test/fixture/decoder/renderer spans all *echo* the
> transcribed rectangle constants (0.625 / 0.5 / 0.125, 30 / 60) through decode+render, but none
> **independently pinned the arithmetic relation** or proved the plan phrasing composes for other
> values. §2.1c now does both — (a) the shortfall phrasing is composed for a NON-fixture minimum
> check (18 ft / 20 ft / 2 ft short), and (b) the rectangle fixture's numbers are asserted
> arithmetically self-consistent (shortfall IS provided − required, 0.625 − 0.5 = 0.125; height is a
> true PASS inequality 30 ≤ 60). This is the only implementation-touching change in rev 3; it is
> additive test-only, inside `apps/web/src/components/architect/__tests__/proposal-check-report.test.tsx`,
> and disturbs no production or forbidden path.
>
> **What rev 2 changed (evidence form only — no implementation broadening), still in force.**
> Rev 1 embedded the load-bearing surfaces as long inline dumps in one section; combined they
> exceeded the aggregate diff limit and did not survive supervisor collection intact. Rev 2 instead
> **identifies the four AS-1 load-bearing surfaces (test, fixture, decoder, renderer) as four
> separately bounded, digest-bound collection excerpts** (§2) — each is a small, exact line span
> with its own digest binding, so the supervisor collects each individually and each survives the
> aggregate diff limit. A short crux excerpt is kept inline per surface so the report is inspectable
> now and is not a bare routing map (the loop's inspectability precedent), while the full bounded
> span is what gets collected. Production and mount evidence for the remaining claims is in §3.
>
> Two honesty limits stand, unchanged and explicit:
> - **The producer hashes nothing.** The only local command is `python tools/modularity_check.py
>   --check`; the broker refuses `sha256sum` / `git hash-object` / `Get-FileHash`, and no git-write
>   verb is documented. Every per-surface and per-file digest below is therefore
>   **supervisor/orchestrator-bound at the frozen SHA** (checkout CRLF would smudge a raw digest);
>   the inline crux lets a reviewer inspect content now, the digest binds identity at collection.
> - **Web behaviour is UNVERIFIED and CI-pending (§8).** Lint, typecheck, Vitest, and Playwright
>   prove **only in CI on the pushed implementation head** — never from local reasoning (thin
>   client). **Preservation is UNVERIFIED (§7)** unless a supervisor-bound prior-unit comparison
>   exists to diff against.
>
> This report records **no gate as passed and no acceptance**, and asks to be routed to substantive
> independent review. Commit/push, digest binding, CI collection, and every ledger mutation are
> **orchestrator-only**.

---

## 1. Change set — 18 allowed paths (`N` new · `M` additive edit to existing)

Line anchors are entry points; the authoritative content is the working-tree file at the frozen
SHA (§7). The four AS-1 load-bearing surfaces are bounded for collection in §2; production/mount
evidence in §3.

| # | File | Kind | What it is |
|---|------|------|-----------|
| 1 | `apps/web/src/lib/architect/proposal-draft.ts` | N | Draft model, mirror-not-authority validation, request assembly (srid **2263**), rectangle seed |
| 2 | `apps/web/src/lib/proposal-checks-api.ts` | N | Typed POST client (scenario-api discipline): status/state matrix, size-bound-before-parse, bounded strings, 422 `field` decode |
| 3 | `apps/web/src/components/architect/ProposalEditor.tsx` | N | Container: numeric vertex table = PRIMARY input; run-check; read-only map compose; honesty banner |
| 4 | `apps/web/src/components/architect/ProposalCheckReport.tsx` | N | Grouped PASS/FAIL/COULD_NOT_CHECK; icon+text never colour-only; plan-phrased shortfall; CNC disclosure |
| 5 | `apps/web/src/components/architect/ProposalVariations.tsx` | N | Client-local, ephemeral save/select/compare-two + honesty copy |
| 6 | `apps/web/src/test-support/proposal-check-fixtures.ts` | N | Hand-transcribed rectangle fixtures (separate from the T058-held `rule-evaluation-fixtures.ts`) |
| 7 | `apps/web/src/lib/architect/__tests__/proposal-draft.test.ts` | N | Mirror-drift (one per cap, naming the route constant) + request-assembly + helper immutability |
| 8 | `apps/web/src/lib/__tests__/proposal-checks-api.test.ts` | N | Matrix decode + the AS-1 unchanged-rectangle transport pair (§2.1b) |
| 9 | `apps/web/e2e/proposal-editor.spec.ts` | N | Keyboard-only edited-draft journey; request contract asserted in-stub before fulfil |
| 10 | `apps/web/src/components/architect/__tests__/proposal-editor.test.tsx` | N | Keyboard edit→check→save; add/edit/delete; bad-charset block; no-`dangerouslySetInnerHTML` grep |
| 11 | `apps/web/src/components/architect/__tests__/proposal-check-report.test.tsx` | N | **AS-1 UI render** (§2.1a): shortfall phrasing + height PASS + both CNC first-class + markup-as-text; **plus the rev-3 separate AS-1 arithmetic coverage** (§2.1c, L147–188) |
| 12 | `apps/web/src/lib/architect/navigation.ts` | M | Additive `"proposal"` view id + label (§3.4) — no behaviour change to existing views |
| 13 | `apps/web/src/components/architect/ArchitectShell.tsx` | M | Additive `"proposal"` in the `PRIMARY` nav list (§3.4) |
| 14 | `apps/web/src/components/architect/ArchitectEntry.tsx` | M | Additive import + inspector-exclusion + gated `case "proposal"` (§3.4); no new flag |
| 15 | `apps/web/src/app/property/architect.css` | M | Additive `proposal-*` classes only; `.architect-map-status` untouched (DB-038(e)) |
| 16 | `apps/web/src/components/architect/__tests__/entry.test.tsx` | M | One additive test for the `"proposal"` view (this suite enumerates views) L183–187 |
| 17 | `apps/web/src/components/architect/__tests__/workspace.test.tsx` | M | One additive test for the `"proposal"` view routing (enumerates views) L15–17 |
| 18 | `project-control/reports/M5-T060-producer-report.md` | M | This report |

**Preservation & the "two-file-only" claim (PRODUCER-OBSERVED; UNVERIFIED — §7).** By producer
observation no forbidden path was edited, existing-view rendered behaviour is unchanged, and the
additive view disturbs **only the two enumerating test suites** (`entry.test.tsx`,
`workspace.test.tsx`) among existing tests. This "two-file-only" (minimal-disturbance) statement is
**producer-observed, not a cryptographic fact**. Per the requested action it is **retained as
UNVERIFIED**: substantiating it requires a **supervisor-bound prior-unit digest comparison** that
only the orchestrator can produce (§7). If no comparable prior snapshot exists to diff against, it
stays UNVERIFIED — not proven.

## 2. AS-1 load-bearing surfaces — four separately bounded, digest-bound collection excerpts

Each surface below is a self-contained collection target: **exact file · exact line span · a digest
bound at the frozen head (`«orch-bound»` = LF-normalized sha256, producer hashes nothing) · what it
proves · a short inline crux**. Collect each span independently — none depends on another surviving
the aggregate diff.

### 2.1 AS-1 test — the arithmetic-pinned proof (three bounded spans)

**(a) UI render** — `apps/web/src/components/architect/__tests__/proposal-check-report.test.tsx`
**L20–64** · digest `«orch-bound»`.
Proves: the unedited rectangle, decoded through the real client, renders the AS-1 arithmetic in the
plan's phrasing (coverage FAIL `0.625 / 0.5 / 0.125`; height PASS `30 ≤ 60`) and **both**
COULD_NOT_CHECK reasons first-class, each behind its own **closed** `semantic_gap` disclosure, with
the summary pinned to `2 could not be checked`. (Markup-as-text at L66–72 supports AS-3.)

```ts
const REQUEST = toProposalCheckRequest(rectangleSampleDraft());               // L20 unedited rectangle
// L31-33 plan phrasing:
expect(screen.getByTestId("shortfall-lot_coverage_ratio")).toHaveTextContent(
  "0.625 ratio provided; 0.5 ratio required; 0.125 ratio short");
// L45 both CNC counted; L51-53 / L60-63 each gap disclosure is CLOSED (open === false)
```

**(b) Transport pairing** — `apps/web/src/lib/__tests__/proposal-checks-api.test.ts` **L186–221** ·
digest `«orch-bound»`.
Proves: a request-capturing stub asserts the serialized POST body of the **unedited**
`rectangleSampleDraft()` (srid 2263; 5 vertices, first `[1000000,200000]`; 1 level; 4 walls; area
8000; facts `{zoning_district:"R5", street_width_class:"wide"}`) **before** the matching response
decodes to `{pass:1, fail:1, couldNotCheck:2, total:4}` with coverage `0.625/0.5/0.125` and height
PASS `30/60`. This pins the request↔response pairing to the canonical contract; the edited-draft
e2e journey (§3.2) is complementary interaction coverage, not this pairing.

```ts
expect(captured.body).toEqual(request);                       // L199 exact serialized body
expect(request.proposed_massing.outline.vertices).toHaveLength(5);  // L202 (edited journey: 6)
expect(outcome.report.summary).toEqual({ pass: 1, fail: 1, couldNotCheck: 2, total: 4 }); // L213
```

**(c) Separate arithmetic coverage** (rev 3) —
`apps/web/src/components/architect/__tests__/proposal-check-report.test.tsx` **L147–188** · digest
`«orch-bound»`.
Proves the arithmetic **relation** the (a)/(b) pass-through spans do not: **(a-span L148–165)** the
plan's shortfall phrasing is COMPOSED for a NON-fixture minimum check (`18 ft provided; 20 ft
required; 2 ft short`), so `shortfallPhrase` is proven to generate the plan phrasing rather than echo
one fixture; **(b-span L167–187)** the rectangle fixture's numbers are asserted arithmetically
self-consistent — the coverage shortfall IS `provided − required` (`0.625 − 0.5 = 0.125`, exact
eighths, no epsilon), and the height PASS is a true inequality (`30 ≤ 60`, 30 ft of headroom). This
is the AS-1 arithmetic *pin*; §2.1a/§2.1b/§2.2 remain the render + transport + fixture pass-through.

```ts
expect(screen.getByTestId("shortfall-synthetic_min_setback"))                       // L162 composed, non-fixture
  .toHaveTextContent("18 ft provided; 20 ft required; 2 ft short");
expect(cov!.providedValue! - cov!.requiredValue!).toBe(cov!.shortfall!);            // L178 relation, not a constant
expect(height!.requiredValue! - height!.providedValue!).toBe(30);                    // L186 true PASS headroom
```

### 2.2 Fixture — the hand-transcribed rectangle response

`apps/web/src/test-support/proposal-check-fixtures.ts` — collect **`attestedReportBody` L99–131**,
**`checkResponse` L177–185**, **`markupEchoReportBody` L165–173**, **`stubFetch` L188–190** · digest
`«orch-bound»`.
Proves: the fixture numbers are transcribed by hand from the accepted M5-T054 rectangle case
(never produced by running the client — it exists to prove the client decode + render), and
`checkResponse` sets an explicit `Content-Length` so the client's fail-closed bound-before-parse
branch is exercised deterministically.

```ts
provided_value: 0.625, required_value: 0.5, shortfall: 0.125,   // coverageFail() L57-58
summary: { pass: 1, fail: 1, could_not_check: 2, total: 4 },     // attestedReportBody L124
"Content-Length": String(new TextEncoder().encode(text).length),// checkResponse L181
```

### 2.3 Decoder — the typed client decode ladder

`apps/web/src/lib/proposal-checks-api.ts` — collect **`fetchProposalCheck` L319–437** (with these
load-bearing sub-spans called out for review): **size-bound-before-parse L363–372**,
**documented-pair gate L388–395** (backed by `DOCUMENTED_PAIRS` **L195–201**), **200 `boundReport`
L232–312**, **422 `field` decode L418–425**, **recoverable gating L178–186** · digest `«orch-bound»`.
Proves: the full `(status,state)` matrix incl. `(422, validation_error)` with a decoded `field`; a
plain-digit `Content-Length` within `MAX_RESPONSE_BYTES` is enforced **before** parse (else
`unexpected_response`); every reflected string passes `boundedText`/`boundedToken` (DB-039(k)); no
raw-HTML sink; results carry no recomputed legal value (the server refusal is the truth surface).

```ts
if (!Number.isFinite(declaredLength) || declaredLength > MAX_RESPONSE_BYTES)   // L370 bound-before-parse
  return { kind: "unexpected_response", ... };
if (!isDocumentedProposalPair(response.status, state)) return { kind: "unexpected_response", ... }; // L388
field: typeof record?.field === "string" ? boundedText(record.field, "unknown field") : null,      // L421
```

### 2.4 Renderer — the grouped report component

`apps/web/src/components/architect/ProposalCheckReport.tsx` — collect **`shortfallPhrase` L44–48**,
**`OUTCOME_META` L50–54**, **`ResultRow` CNC + `semantic_gap` disclosure L95–114**, **report branch
L187–211** (honesty banner L194–196; summary L197–200; groups L201–203; unmapped-lot-facts text
L204–208), **validation-field surface L218–222** · digest `«orch-bound»`.
Proves: FAIL renders the plan's exact `"<provided> u provided; <required> u required; <shortfall> u
short"`; status is icon **+ text** (never colour alone); COULD_NOT_CHECK reasons are first-class
with the non-commensurability prose behind a `<details>`; every echoed value renders as
React-escaped text.

```ts
return `${num(r.providedValue)} ${u} provided; ${num(r.requiredValue)} ${u} required; ${num(r.shortfall)} ${u} short`; // shortfallPhrase L47
fail: { icon: "✕", text: "Fail", className: "proposal-result-fail" },  // OUTCOME_META L51 icon+TEXT
{r.semanticGap ? (<details className="proposal-result-gap"><summary>Why this cannot be compared</summary><p>{r.semanticGap}</p></details>) : null} // L107-112
```

## 3. Production + mount evidence — for the remaining claims (AS-2..AS-7)

Bounded specs (file · lines · one-line · digest `«orch-bound»`); crux inline where load-bearing.

### 3.1 Request-assembly authority — `apps/web/src/lib/architect/proposal-draft.ts`
- **`toProposalCheckRequest` L203–244** — the exact route request; the outline `srid` is fixed
  **2263** at L209 (numeric authority; no client CRS transform exists — a deferred D-076-R003
  question). `provenance.kind: "proposed"` L220.
- **Mirror constants L83–95** + **`validateDraft` L145–191** — a MIRROR of the route caps/charset,
  each naming its route source; fast client feedback only, the server refusal remains the truth.
- **`rectangleSampleDraft` L308–333** — the canonical AS-1 draft (§2.1 sends exactly this).
- **`draftIsRunnable` L196–198** — UX gate (no mirror problems + ≥3 vertices), not a legal judgment.

```ts
outline: { srid: 2263, vertices: draft.vertices.map((v) => [v.x, v.y]) },   // L209 numeric authority
```

### 3.2 Editor container — `apps/web/src/components/architect/ProposalEditor.tsx`
- **`runCheck` L62–82** — mirror-gate (`validateDraft`) → POST → grouped render; a blocked draft is
  never sent (each problem names its route constant).
- **Vertex table L191–229** — PRIMARY keyboard-first input; `aria-label="Vertex i X/Y coordinate"`
  L208/L216. Levels L234–286, walls L288–339, run-check button L342–344, draft-problems L347–359.
- **Honesty banner `editor-honesty` L118–121**; `OutcomeAnnouncer` L115 (AS-2/AS-5).
- **Read-only map compose L362–371** — "display only" copy L365–368; `<LotOutlineMap bbl context />`
  L369 (composed, never edited; DB-038(e)). Save/select-variation L84–111.

```tsx
<LotOutlineMap bbl={bbl} context />   // L369 composed READ-ONLY beside the form
```

### 3.3 Variations — `apps/web/src/components/architect/ProposalVariations.tsx`
- **Honesty `variations-honesty` L62–64** + **ephemerality `variations-ephemeral` L65–67** ("Kept in
  this browser session only — not saved"); save L68–76; compare-two L96–132. Client-local only — no
  network write, no scenario document, no `contract_version` token (AS-4).

### 3.4 Mount — additive only (AS-6)
- `navigation.ts` **L2** (`WORKSPACE_VIEWS` gains `"proposal"`), **L6** (`VIEW_LABELS.proposal =
  "Proposal editor"`).
- `ArchitectShell.tsx` **L6** (`PRIMARY` gains `"proposal"`).
- `ArchitectEntry.tsx` **L30** import, **L87** inspector-exclusion (full-width workspace), **L142–143**
  the gated `case "proposal"` arm — reachable only inside the existing `ruleEvaluationSurfaceEnabled`
  tree (no new flag; producer-observed, confirmed at CI).
- Enumerating suites updated: `entry.test.tsx` **L183–187**, `workspace.test.tsx` **L15–17**.

## 4. Acceptance-scenario coverage (web proof UNVERIFIED — CI-pending, §8)

- **AS-1** — established by §2.1a (UI render arithmetic + both CNC), §2.1b (transport pairing on the
  unedited rectangle), and §2.1c (the **separate arithmetic coverage**: phrasing composed for a
  non-fixture value + fixture numbers proven arithmetically self-consistent), with §2.2 (fixture),
  §2.3 (decoder), §2.4 (renderer).
- **AS-2** (honesty) — `editor-honesty`/`report-honesty`/`variations-honesty`+`variations-ephemeral`
  (§3.2/§2.4/§3.3); outcomes by icon+text, never colour alone (`OUTCOME_META` §2.4).
- **AS-3** (typed refusals + bounded echoes) — full matrix incl. 422 `field` (§2.3); mirror blocks
  over-cap/bad-charset drafts naming the route constant (§3.1); markup id renders as text
  (proposal-check-report.test.tsx L66–72); no `dangerouslySetInnerHTML` (grep test in #10).
- **AS-4** (variations) — client-local save/select/compare-two; re-run updates the stored report; no
  network write / scenario doc / `contract_version` (§3.3).
- **AS-5** (a11y/keyboard) — e2e walks the journey keyboard-only; coordinate edit via real Tab nav
  with a focus assertion before typing (proposal-editor.spec.ts). This spec is a **mocked
  transport/rendering journey**: the proposal-checks route is `page.route`-intercepted (the stub
  asserts the serialized POST body of the EDITED draft — vertex 0 X retyped to 1000005; 6 vertices /
  2 levels / 5 walls — then fulfils the canned rectangle arithmetic), so it proves the
  edit→check→read→save interaction + rendering, NOT the live server contract (which §2.1b transport
  pairing and §2.3 decoder pin on the UNCHANGED rectangle). Edited-draft journey vs unchanged-draft
  pairing are deliberately distinct surfaces.
- **AS-6** (mount + gating) — §3.4; `LotOutlineMap` read-only; `ScenarioWorkspace` untouched.
- **AS-7** (proof) — **UNVERIFIED — CI-pending (§8).** Local `modularity_check --check` = 0 failures
  is the only local signal, not a substitute for the four CI web checks.

## 5. Directive requirement mapping

- **D-066-R001** — code-graph consumed the read-only seams named in the packet; graph regenerated at
  the contract seam before authoring; no forbidden/held file edited (compatibility in §6).
- **D-076-R001** — a flat numeric editor over the existing check engine; no 3D/massing/visual work.
- **D-076-R002** — every editor/report/variation number labeled proposed-derived, never a record or
  allowance; variations ephemeral; no scenario-document construction, no `contract_version` anywhere.
- **D-076-R003** — map drawing, the 4326→2263 transform, and scenario emission deliberately absent (§9).
- **D-077-R002 / R003** — reflected-string bounding (DB-039(k)) in the client (§2.3 `boundReport`) and
  the renderer (§2.4); the typed refusal decode is the truth surface.

## 6. Client ↔ route compatibility (mirror-not-authority)

Client mirrors compared against the read-only route `services/api/app/api/v1/proposal_checks_api.py`
(FORBIDDEN — never edited). Verified at this head:

| route pair | client `DOCUMENTED_PAIRS` (§2.3, L195–201) | match |
|---|---|---|
| `(200, None)` | `[200, null]` | ✓ |
| `(404, None)` | `[404, null]` (generic Not Found / flag-off → feature_unavailable) | ✓ |
| `(413, "payload_too_large")` | `[413, "payload_too_large"]` | ✓ |
| `(422, "validation_error")` | `[422, "validation_error"]` (+ `field` decode) | ✓ |
| `(500, "internal_error")` | `[500, "internal_error"]` | ✓ |

| route constant | value | client mirror (§3.1, L83–95) | value | match |
|---|---|---|---|---|
| `MAX_LABEL_LEN` | 200 | `MIRROR_MAX_LABEL_LEN` | 200 | ✓ |
| `_LABEL_CHARSET` | `[A-Za-z0-9 ._:\-]+` fullmatch | `MIRROR_LABEL_CHARSET` `/^[A-Za-z0-9 ._:-]+$/` | — | ✓ |
| `ROUTE_MAX_EXTERIOR_WALLS` | 500 | `MIRROR_ROUTE_MAX_EXTERIOR_WALLS` | 500 | ✓ |
| `ROUTE_MAX_LOT_LINE_SEGMENTS` | 800 | `MIRROR_ROUTE_MAX_LOT_LINE_SEGMENTS` | 800 | ✓ |
| `ROUTE_MAX_STREET_LINES` | 400 | `MIRROR_ROUTE_MAX_STREET_LINES` | 400 | ✓ |
| `ROUTE_MAX_TOTAL_OUTLINE_POSITIONS` | 1200 | `MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS` | 1200 | ✓ |

The drift tests in `proposal-draft.test.ts` fail if any client constant diverges from its named route
source — the mirror can never silently become an authority. Other read-only seams consumed (all
FORBIDDEN): `scenario-api.ts` (discipline copied), `surveyReview/api.ts` (POST/refusal-decode
precedent), `rule-evaluation.ts` (`ruleEvaluationSurfaceEnabled`, inherited — no new flag),
`LotOutlineMap.tsx` (composed read-only), `test_proposal_checks_api.py` + rectangle fixture (the AS-1
numbers).

## 7. Digest binding + preservation (orchestrator-bound; the producer hashes nothing)

The producer cannot hash (broker refuses `sha256sum`/`git hash-object`/`Get-FileHash`; no git-write
verb is documented). The orchestrator/supervisor fills the LF-normalized `sha256` for each surface
(§2/§3) and each file below at the frozen SHA. "Prior" = the previous submission head; "Current" =
this frozen head. The report's own digest is content-addressed by the harvest commit (a report
cannot self-embed its digest — M5-T013 precedent).

| # | File | prior sha256 (LF-norm) | current sha256 (LF-norm) | Δ |
|---|------|----|----|----|
| 1 | `apps/web/src/lib/architect/proposal-draft.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 2 | `apps/web/src/lib/proposal-checks-api.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 3 | `apps/web/src/components/architect/ProposalEditor.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 4 | `apps/web/src/components/architect/ProposalCheckReport.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 5 | `apps/web/src/components/architect/ProposalVariations.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 6 | `apps/web/src/test-support/proposal-check-fixtures.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 7 | `apps/web/src/lib/architect/__tests__/proposal-draft.test.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 8 | `apps/web/src/lib/__tests__/proposal-checks-api.test.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 9 | `apps/web/e2e/proposal-editor.spec.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 10 | `apps/web/src/components/architect/__tests__/proposal-editor.test.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 11 | `apps/web/src/components/architect/__tests__/proposal-check-report.test.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 12 | `apps/web/src/lib/architect/navigation.ts` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 13 | `apps/web/src/components/architect/ArchitectShell.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 14 | `apps/web/src/components/architect/ArchitectEntry.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 15 | `apps/web/src/app/property/architect.css` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 16 | `apps/web/src/components/architect/__tests__/entry.test.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 17 | `apps/web/src/components/architect/__tests__/workspace.test.tsx` | `«orch-bound»` | `«orch-bound»` | `«orch-bound»` |
| 18 | `project-control/reports/M5-T060-producer-report.md` | `«orch-bound»` | `«orch-bound»` | changed (this file) |

**Preservation & the "two-file-only" claim are UNVERIFIED.** The §1 statement — no forbidden path
touched, existing-view behaviour byte-stable, and the additive view disturbing **only the two
enumerating suites** (`entry.test.tsx`, `workspace.test.tsx`) among existing tests — is
**producer-observed**, not a cryptographic fact. It is substantiated **only** when the orchestrator
produces a **supervisor-bound prior-unit comparison**: fill the prior/current columns above at the
frozen head and confirm every file except #12–#18 (the additive mount/CSS/test/report set) is
byte-identical to its prior-unit content, and that #12–#15 differ only by the additive lines named
in §3.4. **Absent that comparison the claim is retained as UNVERIFIED — not proven.**

## 8. Verification status — web behaviour and preservation UNVERIFIED

- **Local (thin client):** `python tools/modularity_check.py --check` — re-run this unit:
  `selected 466 files; failures 0; warnings 20`; **none of the 18 packet files appear in the 20
  pre-existing warnings**. This is the only command run locally and is a self-check, not a substitute
  for CI.
- **Web behaviour is UNVERIFIED and CI-pending.** No web command is run or documented locally. The
  four web checks — **lint, typecheck, Vitest, Playwright e2e** — prove **only in CI on the pushed
  implementation head**. Acceptance of the AS-1..AS-7 web proof is **held** until those four CI
  results exist **bound to the pushed implementation SHA**; a reviewer must not accept any web claim
  on this report alone. **Nothing here records a gate as passed or the task as accepted.**

## 9. D-076-R003 deferrals + post-B3 owner-checkpoint input (plain English)

Three things this increment deliberately does NOT do — each is an owner question for the post-B3
checkpoint, not a gap to fix here:

1. **Map drawing.** You edit the building by typing numbers into the vertex table, not by drawing on
   the map. The map only shows the recorded lot for reference. Drawing is a later decision.
2. **Map-to-feet conversion (4326→2263).** The editor's numbers are already in survey feet (the units
   the checks use). Turning map clicks into those feet needs a new library and a measurement-accuracy
   decision, so it is deliberately left out.
3. **Saving a proposal as a scenario.** Variations live in the browser tab only and vanish when it
   closes. Making a proposal into a saved, shareable scenario document is a separate future step.

What works now: type a proposal, run it against the real check route, read an honest grouped result
(what passed, what failed with the exact shortfall, what could not be checked and why), and keep a
few variations side by side for the current session.

## 10. Requested next steps (orchestrator-controlled) + discovery routing

The producer performs none of these (authority-restricted — thin-client + orchestrator-only mutation):

1. Snapshot → commit → push the 18 allowed-path files to the task branch to yield an **implementation SHA**.
2. Collect the §2 bounded excerpts — the four load-bearing surfaces (test incl. the three §2.1a/b/c
   spans, fixture, decoder, renderer), each surviving independently — and fill the §2/§3/§7 digests at
   the frozen head; produce the **supervisor-bound prior-unit comparison** for the §7 preservation /
   "two-file-only" claim, or leave it recorded as **UNVERIFIED**.
3. Attach the four CI results (lint, typecheck, Vitest, Playwright e2e), green, **bound to that SHA**.
4. Route to **substantive independent review** before any completion or acceptance.

**Discovery routing (D-069):** no out-of-scope defects surfaced. The three §9 items are planned
D-076-R003 deferrals, not discoveries.
