# M5-T041 — producer report (resubmission)

**Task:** Address-flow + validator polish cluster — DB-024 copy/a11y quartet (a–d) +
DB-025(e) web-validator wording correction.
**Producer:** frontend-engineer (loop worker).
**Scope discipline:** web-only copy / a11y / wording. No `services/api` path touched; no
contract schema or generated-TS change; `apps/web/src/lib/address-search.ts` deliberately
untouched (out of allowed_paths — retry/outcome semantics unchanged).
**Web validation status:** PENDING CI on the pushed head (AS-7). No local `npm/npx/node`
was run; no web test result is claimed here. The orchestrator captures the web / web-e2e
CI conclusions on the pushed head.

**Resubmission note (why this report changed):** the prior submission cited the changed
sections but did not embed their verbatim, line-anchored content. This resubmission embeds
each omitted bounded section verbatim — the validator implementation + wording diff, the
complete contract-versions test addition, the zoning-context-panel test changes, the complete
autocomplete accessibility test, and the `fullSearchActive` lifecycle — so a reviewer can
verify the code, not a paraphrase. Digest binding of every source file is orchestrator-stamped
at the committed, pushed revision (§5): sha256 computation is NOT one of this packet's
`documented_test_commands`, so under D-024-R294 it fail-closes to a human/broker hold and is
routed to the orchestrator rather than improvised locally.

---

## 1. What changed (all inside allowed_paths)

Production source (behavior + copy + a11y):

- `architect/AddressAutocomplete.tsx` — homes three shared exported constants next to the
  existing `FULL_ADDRESS_SEARCH_LABEL`:
  - `ABSENT_BBL_MAP_LINK_NOTE` — DB-024(b) single absent-BBL note.
  - `ZOLA_LOT_LINK_LABEL` (`"Open ZoLa"`) — DB-024(d) one ZoLa-link accessible name.
  - `FULL_SEARCH_ERROR_MESSAGES` — DB-024(a) non-circular recovery copy for when the
    **explicit** full-address search itself fails (selected by `fullSearchActive`); it
    never names the just-failed search, and points at manual entry / BBL. The typed-suggestion
    failure path keeps `ERROR_MESSAGES` (naming the full-address button is a real next step there).
  - address-hint `↗` wrapped in `<span aria-hidden="true">` — DB-024(c).
- `address/AddressConfirmCard.tsx` — ZoLa link text → `ZOLA_LOT_LINK_LABEL`; absent note →
  `ABSENT_BBL_MAP_LINK_NOTE` (imported from AddressAutocomplete).
- `architect/PropertyOverview.tsx` — site-context ZoLa link → `ZOLA_LOT_LINK_LABEL`; absent
  note → `ABSENT_BBL_MAP_LINK_NOTE`.
- `architect/ZoningContextPanel.tsx` — ZoLa link → `ZOLA_LOT_LINK_LABEL`; absent note →
  `ABSENT_BBL_MAP_LINK_NOTE` (was `"Open in ZoLa"`).
- `architect/ProfileViews.tsx` — the `Inspect calculation evidence →` arrow wrapped in
  `<span aria-hidden="true">` (DB-024(c), matches the accepted DB-019a pattern).
- `lib/rule-evaluation-contract.ts` — DB-025(e): wording corrected to describe the actual
  behavior — a **positive-shape, documented-key** check with **no** client-side
  `additionalProperties` rejection; the server stays authoritative on the closed schema.
  No behavior change (no fixture verdict changes).

Tests finished this unit (the remaining in-scope assertions):

- `address/__tests__/address-confirm.test.tsx` — new **S7** block: asserts the confirm
  card's ZoLa link resolves by the shared `ZOLA_LOT_LINK_LABEL` accessible name, and its
  absent note equals `ABSENT_BBL_MAP_LINK_NOTE` byte-for-byte.
- `architect/__tests__/zoning-context-panel.test.tsx` — AS-5 (both the panel and site links
  by `ZOLA_LOT_LINK_LABEL`), AS-6 (both the non-canonical and the literal-null BBL paths)
  now assert **both** the ZoningContextPanel and the PropertyOverview absent notes equal
  `ABSENT_BBL_MAP_LINK_NOTE` (was `toContain`); new DB-024(c) block asserts the ProfileViews
  arrow is `aria-hidden` and the link's accessible name is arrow-free
  (`"Inspect calculation evidence"`). Consumes the previously-unused `ZoningView` import.
- `architect/__tests__/autocomplete.test.tsx` — DB-024(a) non-circular recovery (explicit
  full-search failure offers manual entry, never names the just-failed search; the typed
  path still names it) and DB-024(c) address-hint arrow `aria-hidden`.
- `lib/__tests__/contract-versions.test.ts` — DB-025(e): an otherwise-valid document with an
  unknown/extra top-level key still validates `ok === true` (positive-shape proof).

---

## 2. Acceptance-scenario evidence mapping (AS-1 … AS-7)

- **AS-1 (a) — non-circular failure recovery.** `FULL_SEARCH_ERROR_MESSAGES`
  (AddressAutocomplete.tsx) is selected only while `fullSearchActive` (searchResult.query ===
  text). Every entry omits `FULL_ADDRESS_SEARCH_LABEL` and names manual entry / BBL. Full
  lifecycle source in §4.5; test in §4.4. Test: autocomplete.test.tsx "DB-024(a)" — status
  `not.toHaveTextContent(FULL_ADDRESS_SEARCH_LABEL)`, `toHaveTextContent(/manual entry/i)`,
  and `use-manual-entry` present; the twin test proves the typed-suggestion path is
  deliberately unchanged (still names the button — that path is not circular).
- **AS-2 (b) — one shared absent-BBL note across all three surfaces.** Single export
  `ABSENT_BBL_MAP_LINK_NOTE` (§4.5 head); rendered by AddressConfirmCard, ZoningContextPanel,
  PropertyOverview. Asserted **through the imported constant**: address-confirm.test.tsx S7
  (`zola-link-absent` === constant); zoning-context-panel.test.tsx AS-6 ×2
  (`zoning-context-zola-absent` and `site-zola-absent` both === constant, §4.3).
- **AS-3 (c) — decorative glyphs.** address-hint `↗`, ProfileViews `→` each in
  `<span aria-hidden="true">`. Tests: autocomplete.test.tsx DB-024(c) (hint arrow hidden,
  link name `"NYC Planning address suggestions"`, §4.4); zoning-context-panel.test.tsx
  DB-024(c) (ProfileViews arrow hidden, link name `"Inspect calculation evidence"`, §4.3).
  The already-accepted DB-019a suite covers the two ZoLa `↗` glyphs.
- **AS-4 (d) — one consistent ZoLa accessible-name pattern.** `ZOLA_LOT_LINK_LABEL` = `"Open ZoLa"`
  on all three ZoLa link sites (§4.5 head). Accessible name is identical across sites (the
  ZoningContextPanel and PropertyOverview links carry a decorative `↗`; the confirm-card action
  omits the arrow — neither affects the accessible name). Tests: address-confirm.test.tsx S7
  (`getByRole("link", { name: ZOLA_LOT_LINK_LABEL })`); zoning-context-panel.test.tsx AS-5
  (panel + site links by `ZOLA_LOT_LINK_LABEL`, §4.3).
- **AS-5 (e) — validator wording matches behavior.** Wording corrected (no behavior change),
  so every recorded 1.0.0 / 1.1.0 fixture stays valid. Proof: contract-versions.test.ts
  DB-025(e) (unknown key still `ok`, §4.2); the existing contract-version admission suite is
  unchanged. Validator implementation + wording diff in §4.1.
- **AS-6 — no retry/outcome semantic change; modularity clean.** `address-search.ts` untouched
  (not in allowed_paths); `ERROR_MESSAGES`/`rejected`/DB-006 classification unchanged; DRAFT
  vocabulary unchanged. Modularity check: **0 failures** (see §7).
- **AS-7 — CI green on the pushed head.** PENDING — orchestrator captures. Not claimed here.

---

## 3. Module-boundary explanation

The three shared constants are homed in `AddressAutocomplete.tsx` beside the pre-existing
`FULL_ADDRESS_SEARCH_LABEL`, which is already the single-source-of-truth export the address
surfaces import for shared user-facing strings. This keeps the "one string, many render sites"
discipline in one owning module rather than creating a new util file (no dumping ground) and
preserves the existing import direction: the address components and the two architect panels
already depend on this module's exports. No new cross-module dependency or cycle is introduced —
AddressConfirmCard / PropertyOverview / ZoningContextPanel already import from the architect
address module. Presentation-only: the validated `zolaLotUrl` helper and the retry/outcome
classification are untouched. Files stayed within their responsibilities; no file was grown past
its boundary (modularity check reports 0 failures for the touched files).

---

## 4. Bounded evidence (verbatim, line-anchored)

Every excerpt below is a verbatim copy of the named file at the stated line range. Digest
binding for each file is orchestrator-stamped at the committed, pushed revision — see §5.

### 4.1 Validator wording diff + relevant implementation — `apps/web/src/lib/rule-evaluation-contract.ts`

**DB-025(e) corrected module doc (verbatim, lines 14–22):**

```ts
 * It then provides a RUNTIME validator that mirrors src/lib/validate-profile.ts:
 * every HTTP-200 rule-evaluation body has each DOCUMENTED key checked for the
 * right shape and contract-locked enum value BEFORE anything renders. This is a
 * POSITIVE-SHAPE check, not a closed-schema one: an unknown or extra top-level
 * key is NOT rejected (there is no client-side additionalProperties
 * enforcement), so the server stays authoritative on the full closed schema.
 * FAILURE IS TOTAL — when a documented key is missing or malformed the caller
 * receives only a bounded problem list, never a partially-usable document — so
 * nothing can be drawn from an invalid payload.
```

**DB-025(e) corrected function doc (verbatim, lines 392–398):**

```ts
/**
 * Validate an HTTP-200 body against the generated rule_evaluation types.
 * Returns the typed document ONLY when every documented key passes its shape
 * and enum check. Unknown/extra top-level keys are not rejected (positive-shape
 * check; the server owns the closed schema). A `verified` top-level
 * coverage_status is rejected (draft is never Verified).
 */
```

**Relevant implementation — the whole validator (verbatim, lines 399–472):** proves the
wording is accurate. The function calls `checkEnum` / `problems.add` only on **named**
documented keys; it never iterates `Object.keys(body)` to reject an unmodeled key, and it
returns `ok: true` whenever `problems.list` is empty — so an extra top-level key cannot fail
validation. That is exactly a positive-shape check with the server authoritative on the closed
schema. No behavior changed (no recorded 1.0.0 / 1.1.0 fixture verdict changes).

```ts
export function validateRuleEvaluationDocument(
  body: unknown,
): RuleEvaluationValidationResult {
  const problems = new Problems();
  if (!isRecord(body)) {
    return { ok: false, problems: ["rule_evaluation: response body is not a JSON object"] };
  }

  checkEnum(
    problems,
    "contract_version",
    body.contract_version,
    RULE_EVALUATION_CONTRACT_VERSIONS,
  );
  checkEvaluatedInput(problems, body.evaluated_input);
  checkEnum(problems, "coverage_status", body.coverage_status, DRAFT_COVERAGE_STATUSES);
  checkEnum(problems, "coverage_source", body.coverage_source, COVERAGE_SOURCES);
  if (
    !(
      body.data_completeness === null ||
      (typeof body.data_completeness === "string" &&
        (DATA_COMPLETENESS_VALUES as readonly string[]).includes(body.data_completeness))
    )
  ) {
    problems.add("data_completeness", "must be a data-completeness enum value or null");
  }
  for (const key of [
    "needs_review",
    "professional_review_required",
    "fail_safe",
  ] as const) {
    if (typeof body[key] !== "boolean") {
      problems.add(key, "must be a boolean");
    }
  }
  if (
    !(
      body.fail_safe_reason === null ||
      (typeof body.fail_safe_reason === "string" &&
        (FAIL_SAFE_REASONS as readonly string[]).includes(body.fail_safe_reason))
    )
  ) {
    problems.add("fail_safe_reason", "must be a documented fail-safe reason or null");
  }
  checkStringArray(problems, "rule_lifecycle_statuses", body.rule_lifecycle_statuses);
  if (!isNonEmptyString(body.not_verified_disclaimer)) {
    problems.add("not_verified_disclaimer", "must be a non-empty string");
  }
  if (!(body.zoning_district === null || isNonEmptyString(body.zoning_district))) {
    problems.add("zoning_district", "must be a non-empty string or null");
  }
  if (!(body.lot_area_sq_ft === null || typeof body.lot_area_sq_ft === "number")) {
    problems.add("lot_area_sq_ft", "must be a number or null");
  }
  if (!(body.lot_area_source === null || isNonEmptyString(body.lot_area_source))) {
    problems.add("lot_area_source", "must be a non-empty string or null");
  }
  if (!(body.spatial_context === null || isRecord(body.spatial_context))) {
    problems.add("spatial_context", "must be an object or null");
  }
  checkSpatialUncertainty(problems, body.spatial_uncertainty);
  if (!Array.isArray(body.evaluations)) {
    problems.add("evaluations", "must be an array");
  }
  checkFamilyCoverage(problems, body.family_coverage);
  checkStringArray(problems, "reasons", body.reasons);
  checkRuleConflict(problems, body.rule_conflict);
  checkWideStreet(problems, body.wide_street);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, document: body as unknown as RuleEvaluation };
}
```

### 4.2 Complete contract-versions test addition — `apps/web/src/lib/__tests__/contract-versions.test.ts`

New DB-025(e) block (verbatim, lines 169–182). The existing contract-version admission suite
(1.0.0 + additive 1.1.0) is unchanged; this block is additive. The baseline assertion proves
the fixture is valid before the extra key is added and after — no fixture is mutated
destructively.

```ts
describe("DB-025(e) — positive-shape validator: unknown keys are not rejected", () => {
  // Backs the corrected module wording: the client checks DOCUMENTED keys
  // positively and does NOT enforce additionalProperties — the server owns the
  // closed schema. An unknown/extra top-level key must NOT fail total validation
  // (a forward-compatible server field the client does not yet model still
  // renders), and every recorded fixture stays valid.
  it("accepts an otherwise-valid document carrying an unknown/extra top-level key", () => {
    const doc = draftApplicableDoc();
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true); // baseline stays valid
    (doc as unknown as Record<string, unknown>).server_only_future_field =
      "ignored-by-the-client";
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });
});
```

### 4.3 Zoning-context-panel test changes — `apps/web/src/components/architect/__tests__/zoning-context-panel.test.tsx`

Import of the shared constants (verbatim, lines 6–11) — AS-5/AS-6/DB-024(c) assert through
these imports, never through independent literals:

```ts
import { ZoningView } from "../ProfileViews";
import { ReportView } from "../ReportView";
import {
  ABSENT_BBL_MAP_LINK_NOTE,
  ZOLA_LOT_LINK_LABEL,
} from "../AddressAutocomplete";
```

AS-5 — both ZoLa links resolve by the shared `ZOLA_LOT_LINK_LABEL` accessible name while the
`↗` glyph is decorative (verbatim, lines 229–253):

```tsx
describe("AS-5 (DB-019a) — both ZoLa link glyphs are decorative (aria-hidden), names unchanged", () => {
  it("hides the ↗ glyph on the panel's ZoLa link while keeping its accessible name", () => {
    const panel = renderPanel();
    const link = within(panel).getByTestId("zoning-context-zola-link");
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
    // The decorative arrow is out of the accessible name — the link still
    // resolves by its human name (DB-024(d): the shared ZoLa link label).
    expect(within(panel).getByRole("link", { name: ZOLA_LOT_LINK_LABEL })).toBe(link);
  });

  it("hides the ↗ glyph on the overview Site-context ZoLa link while keeping its name", () => {
    renderOverview();
    const link = screen.getByTestId("site-zola-link");
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
    // The overview nests ZoningContextPanel, whose ZoLa link now shares the SAME
    // accessible name (DB-024(d)); scope to the map card so this asserts the
    // site-context link specifically.
    const mapCard = document.querySelector<HTMLElement>(".architect-map-card")!;
    expect(within(mapCard).getByRole("link", { name: ZOLA_LOT_LINK_LABEL })).toBe(link);
  });
});
```

AS-6 — both absent notes are byte-identical to `ABSENT_BBL_MAP_LINK_NOTE` on the non-canonical
AND the literal-null BBL paths (verbatim, lines 255–297):

```tsx
describe("AS-6 (DB-019b) — PropertyOverview honest absent note on a non-canonical or null BBL", () => {
  it("renders NO Site-context link and a panel-matched absent note when the BBL is not canonical", () => {
    const profile = baseProfile();
    profile.identity.bbl = "12345"; // wrong length — zolaLotUrl returns null
    renderOverview(profile);
    expect(screen.queryByTestId("site-zola-link")).toBeNull();
    const siteAbsent = screen.getByTestId("site-zola-absent");
    // PropertyOverview nests ZoningContextPanel, so its own absent note renders
    // in the same tree — assert BOTH honest notes are byte-identical to the
    // shared ABSENT_BBL_MAP_LINK_NOTE constant (single source of truth, DB-024(b)),
    // never independently drifting literals.
    const panelAbsent = screen.getByTestId("zoning-context-zola-absent");
    expect(siteAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
    expect(panelAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
  });

  it("renders the honest absent note (no link, no crash) when the BBL is literally null", () => {
    // Explicit null-BBL regression for AS-6 / DB-019b. The generated contract
    // types identity.bbl as a non-null string, but a connector miss can leave
    // it absent; a literal null must take the SAME honest-absence path as a
    // malformed string — never throw (zolaLotUrl's typeof guard and
    // propertyHref's `?? ""` both tolerate it) and never emit a guessed link.
    // Deliberate invalid-shape probe per CODING_RULES: `as unknown as`.
    const profile = baseProfile();
    profile.identity.bbl = null as unknown as string;
    renderOverview(profile);
    expect(screen.queryByTestId("site-zola-link")).toBeNull();
    const siteAbsent = screen.getByTestId("site-zola-absent");
    // Same shared constant on the null-BBL path too: both honest notes are
    // byte-identical to ABSENT_BBL_MAP_LINK_NOTE (DB-024(b)), never drifting.
    const panelAbsent = screen.getByTestId("zoning-context-zola-absent");
    expect(siteAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
    expect(panelAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
  });

  it("with a canonical BBL the Site-context link renders and no absent note appears (prior rendering preserved)", () => {
    renderOverview();
    expect(screen.getByTestId("site-zola-link").getAttribute("href")).toBe(
      `${ZOLA_PREFIX}1000010010`,
    );
    expect(screen.queryByTestId("site-zola-absent")).toBeNull();
  });
});
```

DB-024(c) — the ProfileViews "Inspect calculation evidence" arrow is decorative (verbatim,
lines 324–343):

```tsx
describe("DB-024(c) — the ProfileViews 'Inspect calculation evidence' arrow is decorative", () => {
  it("hides the → glyph (aria-hidden) and keeps the link's accessible name arrow-free", () => {
    // ZoningView carries the primary "Inspect calculation evidence" action; its
    // trailing → must be decorative (out of the accessible name), matching the
    // accepted DB-019a arrow pattern used on the ZoLa links above.
    render(
      <ZoningView
        profile={baseProfile()}
        evaluation={null}
        scenario={null}
        onInspect={vi.fn()}
      />,
    );
    // The link resolves by its arrow-free accessible name — the glyph is excluded.
    const link = screen.getByRole("link", { name: "Inspect calculation evidence" });
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("→");
  });
});
```

### 4.4 Complete autocomplete accessibility test — `apps/web/src/components/architect/__tests__/autocomplete.test.tsx`

DB-024(a) — the non-circular full-search failure recovery, plus the twin test proving the
typed-suggestion path is deliberately unchanged (verbatim, lines 271–302):

```tsx
describe("DB-024(a) — a failed EXPLICIT full-address search never points back at itself", () => {
  it("offers a genuinely different next step (manual entry / BBL), never the just-failed search", async () => {
    vi.useFakeTimers();
    // Typed suggestions come back empty (no typed-path error); the EXPLICIT
    // full-address search itself then fails. The recovery copy must NOT send the
    // user back to the search they just watched fail (the old circular copy).
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    fullSearch.mockResolvedValue({ kind: "error", reason: "source_unavailable" });
    const onFallback = vi.fn();
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} onFallback={onFallback} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway, New York" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); });
    const status = screen.getByRole("status");
    // Non-circular: the copy never names the full-address search button again…
    expect(status).not.toHaveTextContent(FULL_ADDRESS_SEARCH_LABEL);
    // …and it names a genuinely different affordance that is actually present.
    expect(status).toHaveTextContent(/manual entry/i);
    expect(screen.getByTestId("use-manual-entry")).toBeInTheDocument();
  });

  it("keeps the TYPED-suggestion failure copy pointing at the full-address search (that path is not circular)", async () => {
    vi.useFakeTimers();
    // A typed-suggestion failure is different: the user has NOT tried the explicit
    // full-address search, so naming it is a real next step — unchanged behavior.
    search.mockResolvedValue({ kind: "error", reason: "source_unavailable" });
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    expect(screen.getByRole("status")).toHaveTextContent(FULL_ADDRESS_SEARCH_LABEL);
  });
});
```

DB-024(c) — the address-hint arrow glyph is decorative (verbatim, lines 304–312):

```tsx
describe("DB-024(c) — the address-hint arrow glyph is decorative (aria-hidden)", () => {
  it("hides the ↗ on the NYC Planning hint link and keeps its accessible name arrow-free", () => {
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    const link = screen.getByRole("link", { name: "NYC Planning address suggestions" });
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
  });
});
```

### 4.5 `fullSearchActive` lifecycle — `apps/web/src/components/architect/AddressAutocomplete.tsx`

This is the implementation AS-1 (DB-024(a)) rests on: the non-circular copy is selected ONLY
while the explicit full-address search's result is the live outcome, and editing exits that
state so the typed-path copy returns.

Shared constants + the two copy tables (verbatim, lines 16–60). `FULL_SEARCH_ERROR_MESSAGES`
never names `FULL_ADDRESS_SEARCH_LABEL`; `ERROR_MESSAGES` (typed path) still does:

```ts
export const FULL_ADDRESS_SEARCH_LABEL = "Search this full address";

/** DB-024(b): the single shared "no canonical BBL, so no city-map link" note.
 * AddressConfirmCard, PropertyOverview, and ZoningContextPanel render it
 * BYTE-IDENTICALLY from here so the three honest-absence notes cannot drift into
 * three near-duplicate literals (the same single-source-of-truth discipline as
 * FULL_ADDRESS_SEARCH_LABEL; asserted via this import in the tests). */
export const ABSENT_BBL_MAP_LINK_NOTE =
    "The city map link needs a valid BBL, which this lot did not provide.";

/** DB-024(d): one accessible name for every ZoLa lot-map link — the
 * AddressConfirmCard action, the PropertyOverview site-context link, and the
 * ZoningContextPanel link. Reading identically to assistive tech instead of
 * drifting between "Open ZoLa", "Open in ZoLa", and a longer sentence. The
 * validated zolaLotUrl helper is untouched; this is presentation only. */
export const ZOLA_LOT_LINK_LABEL = "Open ZoLa";

/** Distinct, non-collapsing copy per failure reason (handoff §6): the old UI
 * folded timeout, source failure, and transport error into one "unavailable"
 * line. Each reason now reads differently and points at a real next step.
 * DB-006: `rejected` (a 4xx the service will not accept) is its own honest,
 * non-retry line. DB-009: the reasons that still render the full-address button
 * name it by its exact label via FULL_ADDRESS_SEARCH_LABEL. */
const ERROR_MESSAGES: Record<AddressSearchErrorReason, string> = {
    rate_limited: `Address suggestions are rate-limited right now. Wait a moment, then use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    timeout: `The city’s address service is taking too long to suggest. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    source_unavailable: `The city’s address service is temporarily unavailable. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    rejected: `The city’s address service didn’t accept that search. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    unavailable: `Couldn’t reach the city’s address service. Check your connection, then use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    malformed: `The city’s address service returned a response we can’t read safely. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
};

/** DB-024(a): copy for when the EXPLICIT full-address search ITSELF fails. The
 * ERROR_MESSAGES above point back at the “${FULL_ADDRESS_SEARCH_LABEL}” button —
 * which is CIRCULAR here, because the user just watched that exact search fail.
 * These never name the just-failed search; they point at genuinely different
 * next steps (the prefilled manual-entry recovery below, or the BBL lookup). */
const FULL_SEARCH_ERROR_MESSAGES: Record<AddressSearchErrorReason, string> = {
    rate_limited: `The full-address search is rate-limited right now. Use manual entry with this address below, or the BBL lookup.`,
    timeout: `The full-address search is taking too long. Use manual entry with this address below, or the BBL lookup.`,
    source_unavailable: `The city’s address service is temporarily unavailable. Use manual entry with this address below, or the BBL lookup.`,
    rejected: `The city’s address service didn’t accept that search. Use manual entry with this address below, or the BBL lookup.`,
    unavailable: `Couldn’t reach the city’s address service. Check your connection, then use manual entry with this address below, or the BBL lookup.`,
    malformed: `The full-address search returned a response we can’t read safely. Use manual entry with this address below, or the BBL lookup.`,
};
```

Lifecycle state + supersede/compute + status-message selection (verbatim, lines 75–100 and
144–151). `fullSearchActive` is true only while the recorded explicit-search result still
matches the current text; the status message picks `FULL_SEARCH_ERROR_MESSAGES` in that state
and `ERROR_MESSAGES` otherwise:

```ts
    /** Result of an EXPLICIT full-address /search, valid only while its query
     * still equals the current text (a stale full search never displays). */
    const [searchResult, setSearchResult] = useState<{ query: string; outcome: AddressSearchOutcome } | null>(null);
```

```ts
    const cancelFullSearch = () => {
        fullSearchAbort.current?.abort();
        fullSearchAbort.current = null;
        fullSearchSeq.current += 1;
        setSearching(false);
    };

    const fullSearchActive = searchResult !== null && searchResult.query === text;
    const outcome: AddressSearchOutcome | null = fullSearchActive ? searchResult!.outcome : typedOutcome;
```

```ts
    const statusMessage = searching
        ? "Searching the city’s full address service…"
        : loading
            ? "Searching official NYC addresses…"
            : incomplete
                ? "Keep typing the full address (at least 3 characters)."
                : outcome?.kind === "error"
                    ? (fullSearchActive ? FULL_SEARCH_ERROR_MESSAGES : ERROR_MESSAGES)[outcome.reason]
```

Editing the input clears the recorded full-search result and cancels any in-flight search, so
`fullSearchActive` becomes false and the typed-path copy (`ERROR_MESSAGES`) returns (verbatim
excerpt of the `onChange` handler, line 162):

```ts
onChange={event => { setText(event.target.value); setSelected(false); setActive(-1); setOpen(true); setSearchResult(null); cancelFullSearch(); onEdit(); }}
```

### 4.6 Confirm-card S7 test — `apps/web/src/components/address/__tests__/address-confirm.test.tsx`

The confirm-card S7 block (ZoLa link by `ZOLA_LOT_LINK_LABEL`, absent note ===
`ABSENT_BBL_MAP_LINK_NOTE`) is present in that file and modified in this packet. It is included
in the digest-bound set (§5); its verbatim excerpt was carried in the prior submission and is
unchanged in this resubmission. The orchestrator's digest stamp for
`address-confirm.test.tsx` binds it at the committed head.

---

## 5. Digest binding (orchestrator-stamped at the committed, pushed revision)

Each bounded excerpt above is verbatim from the working tree at the stated line range. Binding
each excerpt to an immutable file identity requires the LF-normalized sha256 of every source
file. **sha256 computation is NOT one of this packet's `documented_test_commands`** (the only
documented command is `python tools/modularity_check.py --check`), so under the native-tool
preference (D-024-R294) an ad-hoc `sha256sum`/`git hash-object`/`python -c hashlib` invocation
fail-closes to a broker/human hold and is deliberately **not** run here. Per the ADR-005
evidence-capture division of labor, the orchestrator computes and stamps the digests into this
report at the committed head (LF-normalized, per CODING_RULES — CRLF smudge changes digests).

Files to digest-bind (all in allowed_paths, all carrying material changes this unit):

| # | Source file | Bounded section(s) | sha256 (LF-normalized) |
|---|---|---|---|
| 1 | `apps/web/src/lib/rule-evaluation-contract.ts` | §4.1 | `<orchestrator-stamped @ committed head>` |
| 2 | `apps/web/src/lib/__tests__/contract-versions.test.ts` | §4.2 | `<orchestrator-stamped @ committed head>` |
| 3 | `apps/web/src/components/architect/__tests__/zoning-context-panel.test.tsx` | §4.3 | `<orchestrator-stamped @ committed head>` |
| 4 | `apps/web/src/components/architect/__tests__/autocomplete.test.tsx` | §4.4 | `<orchestrator-stamped @ committed head>` |
| 5 | `apps/web/src/components/architect/AddressAutocomplete.tsx` | §4.5, §1 | `<orchestrator-stamped @ committed head>` |
| 6 | `apps/web/src/components/address/__tests__/address-confirm.test.tsx` | §4.6 | `<orchestrator-stamped @ committed head>` |
| 7 | `apps/web/src/components/address/AddressConfirmCard.tsx` | §1 | `<orchestrator-stamped @ committed head>` |
| 8 | `apps/web/src/components/architect/PropertyOverview.tsx` | §1 | `<orchestrator-stamped @ committed head>` |
| 9 | `apps/web/src/components/architect/ZoningContextPanel.tsx` | §1 | `<orchestrator-stamped @ committed head>` |
| 10 | `apps/web/src/components/architect/ProfileViews.tsx` | §1 | `<orchestrator-stamped @ committed head>` |

---

## 6. Out-of-scope consumer inspection (routed to orchestrator, NOT edited)

Per the requested action I inspected `architect/__tests__/development-limits.test.tsx` (M5-T040
territory; NOT in this packet's allowed_paths and NOT edited).

**Finding: no defect — the queries remain singular; no routing action needed.** The two
`/Open ZoLa/` queries there are both scoped with `within(siteCard())`, where
`siteCard()` = `document.querySelector(".architect-map-card")`. In `PropertyOverview.tsx` the
`ZoningContextPanel` (whose ZoLa link now also reads `"Open ZoLa"`) renders as a **sibling of**
`.architect-overview-grid`, i.e. **outside** the `.architect-map-card` section that holds
`site-zola-link`. So the shared label does not add a second match inside the scoped card; the
`getByRole`/`queryByRole` singular queries still resolve exactly the site link.

General note recorded for the orchestrator: keeping the site link's name `"Open ZoLa"` does NOT by
itself preserve any **unscoped** singular `Open ZoLa` query that renders `PropertyOverview`, now
that the nested panel shares the name. A full repo grep (`apps/web/src`) found no such unscoped
consumer — every in-scope `"Open ZoLa"` query is either scoped (map card) or asserted via
`ZOLA_LOT_LINK_LABEL` with explicit scoping. No consumer asserts the old literals
(`"Open in ZoLa"`, the pre-change AddressConfirmCard absent/link text); those changed strings have
no remaining test consumer.

---

## 7. Self-checks (real commands + real results)

- **Modularity (documented test command):** `python tools/modularity_check.py --check` →
  `selected 442 files; failures 0; warnings 19`. **0 failures.** All 19 warnings are pre-existing
  review signals on unrelated modules (surveyReview/types.ts, several services/api connectors and
  tools/agent_supervisor files); none is a file this packet touched. (Re-run for this
  resubmission; result unchanged.)
- **Ruff (api CI job step 1) — AUTHORIZATION CONFLICT, routed to the orchestrator.** The packet
  input says "Run ruff from services/api cwd before every checkpoint," but `python -m ruff check`
  is NOT in this packet's `documented_test_commands` (only `modularity_check.py` is), so under
  D-024-R294 it fail-closes to a broker/human hold rather than executing. This is a genuine
  authorization conflict, NOT a waiver: this packet changes **zero** `services/api` / Python
  files, so the change set cannot affect the api ruff step, and ruff runs on the pushed head in
  CI regardless. The requirement is **routed to the orchestrator** to execute through the broker
  and capture its execution evidence; it is not treated as satisfied here and is not bypassed.
- **Web tests:** NOT run locally (thin-client rule). No web / web-e2e result is claimed. Web
  behavior proves only in CI on the pushed head — orchestrator captures (AS-7).

---

## 8. Preservation / non-goals (confirmed)

- `apps/web/src/lib/address-search.ts` not in allowed_paths and not touched — DB-006 `rejected`
  semantics and retry/outcome classification stand.
- No contract schema or generated-TS change; DRAFT/not-verified vocabulary unchanged.
- No `services/api` path; no legal-rule or determination logic touched.
- The existing scoped implementation is preserved unchanged in this resubmission — only the
  producer report gained the omitted bounded sections (§4) and the digest-binding + ruff-routing
  handoffs to the orchestrator (§5, §7).
