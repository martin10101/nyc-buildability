# M5-T038 — producer report (bounded-evidence resubmission)

Address-flow + context-panel polish cluster (DB-006 / DB-007 / DB-009 / DB-019a-c).
Scope: the six recorded discoveries only — all label-display / affordance / honesty fixes.
No new computation, no schema change, no new data source. DB-008's 6000 ms deadline is
untouched; typed input is preserved through every failure path. D-064 lean.

**This resubmission changes NO implementation.** It only re-packages the review evidence so the
sections the review named survive intact. The failure to fix: an earlier packet inlined every
file's full diff, overran the delivery cap, and the tail sections (the zoning-context-panel
tests, the unchanged supporting excerpts) were dropped; simply re-expanding diffs did not fix
that. The fix here is **collection, not duplication**:

- The four sections the review named are inline and self-contained below, each complete on its
  own — nothing depends on the report tail surviving, and none of them asks a reviewer to open a
  file. They are: (§A) the complete address-search implementation + test changes; (§B) the
  remaining zoning-context-panel tests, **verbatim**; (§C) the relevant unchanged focus /
  coverage / fixture excerpts; and this concise report itself.
- The other five changed files are **not** re-inlined (that is the aggregate patch that overran
  the cap). They are handed to the supervisor for collection as separate, digest-bound sections
  at the committed head (§D), so the reviewer reads them from the frozen commit the supervisor
  establishes — **not** from this worktree via a report anchor, and **not** from uncommitted
  local state.

Executed validation and source inspection are kept apart on purpose: reading source is NOT proof
a web test passes — only CI on the pushed head is (§F).

## Section map (each section is complete on its own)

| Required section (review-named) | Where |
|---|---|
| Complete `address-search.ts` change | §A.1 (inline, full diff) |
| Complete `address-search.test.ts` change | §A.2 (inline, full diff) |
| Remaining zoning-context-panel tests | §B (inline, **verbatim** appended block) |
| Unchanged excerpts — focus return | §C.1 (inline) |
| Unchanged excerpts — coverage badge + fixture | §C.2 (inline) |
| Concise producer report | this document |
| Other five changed files | §D (per-file summary + digest; supervisor collects the full diff at the committed head) |
| Controller task-file diff (attributed, not producer material) | §E (reconciliation requested) |
| Validation — executed vs inspection vs pending CI | §F |

## What changed, per item

- **DB-006 (`address-search.ts`)** — new `rejected` reason. `fetchGeoSearchOnce` classifies
  `429 → rate_limited`, `>= 500 → source_unavailable` (retried, bounded), any other non-2xx
  (4xx: 404/422/400) `→ rejected`. The retry loop retries ONLY `source_unavailable`, so a 4xx
  spends one attempt and never borrows the transient label. (§A.1, §A.2)
- **DB-007** — the two missing tests. (a) AS-2 (`autocomplete.test.tsx`): a `timeout` outcome
  still renders the enabled `full-address-search` button; fails if it disappears. (b) AS-3
  (`address-resolution.test.tsx`): architect "Not my property" returns focus to the autocomplete
  input via the existing `entryFocusNonce`/`useEffect` pattern (never a synchronous `.focus()` on
  the remounting entry UI). (§C.1, §D)
- **DB-009 (`AddressAutocomplete.tsx`)** — `FULL_ADDRESS_SEARCH_LABEL` is the single source of
  truth for the button label AND the failure copy that names it; AS-4 asserts both read the same
  constant, so a rename cannot break only one side. (§D)
- **DB-019a** — the two ZoLa `↗` glyphs (`PropertyOverview.tsx`, `ZoningContextPanel.tsx`) are
  wrapped in `<span aria-hidden="true">`; accessible names stay "Open ZoLa" / "Open in ZoLa". (§D)
- **DB-019b (`PropertyOverview.tsx`)** — on null / non-canonical BBL the Site-context card renders
  `data-testid="site-zola-absent"`, copy byte-matched to the panel's `zoning-context-zola-absent`
  note; link unchanged when a canonical BBL is present. Additive-only. (§D)
- **DB-019c (`ZoningContextPanel.tsx`)** — each present landmark/historic row renders the mapped
  feature's own `coverage_status` via the shared `CoverageBadge` (enum token + SR gloss, never
  colour alone); absent rows show no badge. Display-only. (§B, §C.2, §D)

## Changed files (nine; all within allowed_paths) — git blob anchors

The blob anchors below were recorded in a prior round; the working-tree **content** of every file
was re-read natively this round and matches the diffs/summaries shown. This unit's broker admits
only enumerated read-only git plus the documented `python tools/modularity_check.py --check`;
`git hash-object` / `sha256sum` are refused, so a raw LF-normalized sha256 was NOT recomputed this
round. The supervisor confirms the authoritative git blob digests and the frozen head at commit
(git derives the blob SHA-1 from LF-normalized content, so each anchor is CRLF-stable).

| # | File | git blob old..new | Delivery |
|---|------|-------------------|----------|
| 1 | apps/web/src/lib/address-search.ts | 852c4030..d6895276 | §A.1 inline |
| 2 | apps/web/src/lib/__tests__/address-search.test.ts | d3d0aa96..4f8f6b64 | §A.2 inline |
| 3 | apps/web/src/components/architect/__tests__/zoning-context-panel.test.tsx | e5f45185..823b7b81 | §B inline (verbatim) |
| 4 | apps/web/src/components/architect/AddressAutocomplete.tsx | 16a03885..74c2fa2c | §D — supervisor-collected |
| 5 | apps/web/src/components/architect/__tests__/autocomplete.test.tsx | d32f820a..378caf89 | §D — supervisor-collected |
| 6 | apps/web/src/components/architect/PropertyOverview.tsx | ce7c148b..0eb5ffb9 | §D — supervisor-collected |
| 7 | apps/web/src/components/architect/ZoningContextPanel.tsx | 98a129e6..caf78654 | §D — supervisor-collected |
| 8 | apps/web/src/components/address/__tests__/address-resolution.test.tsx | 5e0d3782..50092878 | §D — supervisor-collected |
| 9 | project-control/reports/M5-T038-producer-report.md | (this report; digest at commit) | — |

`AddressConfirmCard.tsx`, `AddressResolutionScreen.tsx`, and `workspace.test.tsx` are in
allowed_paths but were NOT modified (read only, as unchanged supporting wiring — §C.1).

---

## §A — Complete diffs the review named (inline, self-contained)

### A.1 apps/web/src/lib/address-search.ts (full)
```diff
diff --git a/apps/web/src/lib/address-search.ts b/apps/web/src/lib/address-search.ts
index 852c4030..d6895276 100644
--- a/apps/web/src/lib/address-search.ts
+++ b/apps/web/src/lib/address-search.ts
@@ -20,12 +20,17 @@ export interface AddressSuggestion {
     query: AddressQuery;
 }
 /** Distinct, non-collapsing failure reasons (handoff §6): a transient source
- * failure (5xx) is `source_unavailable` (retried, bounded); a transport/offline
- * failure is `unavailable`; a rate limit, malformed body, and deadline are their
- * own reasons. The UI must never fold these into one "unavailable" message. */
+ * failure (>= 500) is `source_unavailable` (retried, bounded); a client-side
+ * refusal (any other 4xx/non-2xx, e.g. 404/422) is `rejected` (NEVER retried —
+ * retrying cannot change a request the service will not accept); a transport/
+ * offline failure is `unavailable`; a rate limit (429), malformed body, and
+ * deadline are their own reasons. The UI must never fold these into one
+ * "unavailable" message. DB-006: `rejected` is the honest 4xx outcome that is
+ * distinct from — and never labelled — `source_unavailable`. */
 export type AddressSearchErrorReason =
     | "unavailable"
     | "source_unavailable"
+    | "rejected"
     | "rate_limited"
     | "malformed"
     | "timeout";
@@ -122,8 +127,16 @@ async function fetchGeoSearchOnce(endpoint: string, text: string, options: Addre
             const response = await (options.fetchImpl ?? fetch)(`${endpoint}?text=${encodeURIComponent(text.trim())}`, { signal: controller.signal, credentials: "omit", referrerPolicy: "no-referrer", headers: { Accept: "application/json" } });
             if (response.status === 429)
                 return { kind: "error", reason: "rate_limited" };
-            if (!response.ok)
+            // DB-006: only a transient server-side failure (>= 500) is a
+            // retryable `source_unavailable`; every other non-2xx (a 4xx the
+            // service will not accept — 404/422/400 — or any other non-ok
+            // status) is a distinct, non-retried `rejected`. Retrying a 4xx
+            // cannot change the answer, so it must not spend the retry bound
+            // nor borrow the transient-failure label.
+            if (response.status >= 500)
                 return { kind: "error", reason: "source_unavailable" };
+            if (!response.ok)
+                return { kind: "error", reason: "rejected" };
             if (!response.headers.get("content-type")?.includes("json"))
                 return { kind: "error", reason: "malformed" };
             let body: unknown;
```

### A.2 apps/web/src/lib/__tests__/address-search.test.ts (full)
```diff
diff --git a/apps/web/src/lib/__tests__/address-search.test.ts b/apps/web/src/lib/__tests__/address-search.test.ts
index d3d0aa96..4f8f6b64 100644
--- a/apps/web/src/lib/__tests__/address-search.test.ts
+++ b/apps/web/src/lib/__tests__/address-search.test.ts
@@ -107,6 +107,47 @@ describe("bounded recovery and the explicit full-address action (M5-T032)", () =
   });
 });
 
+/**
+ * DB-006: the retry/label gate. Only a transient server failure (>= 500) is the
+ * retried `source_unavailable`. A 4xx the service will not accept (404/422/400)
+ * is a DISTINCT `rejected` — never retried (retrying cannot change it) and never
+ * folded into the transient-failure label.
+ */
+describe("DB-006: 4xx is a distinct, non-retried `rejected`; only >= 500 is the retried `source_unavailable`", () => {
+  it("AS-1: a 404 is NOT retried and is NOT labelled source_unavailable (autocomplete)", async () => {
+    let calls = 0;
+    const fetchImpl: typeof fetch = async () => { calls += 1; return response({ error: "not found" }, 404); };
+    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
+    expect(result).toEqual({ kind: "error", reason: "rejected" });
+    expect(result).not.toEqual({ kind: "error", reason: "source_unavailable" });
+    expect(calls).toBe(1);
+  });
+
+  it("AS-1: a 422 on the explicit full-address /search is likewise a single-attempt `rejected`", async () => {
+    let calls = 0;
+    const fetchImpl: typeof fetch = async () => { calls += 1; return response({ error: "unprocessable" }, 422); };
+    const result = await fetchAddressSearch("120 Broadway, New York", { fetchImpl, backoffMs: 0 });
+    expect(result).toEqual({ kind: "error", reason: "rejected" });
+    expect(calls).toBe(1);
+  });
+
+  it("AS-1: a 400 is a single-attempt `rejected` (the retry bound is untouched)", async () => {
+    let calls = 0;
+    const fetchImpl: typeof fetch = async () => { calls += 1; return response({ error: "bad request" }, 400); };
+    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
+    expect(result).toEqual({ kind: "error", reason: "rejected" });
+    expect(calls).toBe(1);
+  });
+
+  it("AS-1: a 500 IS the retried source_unavailable — it spends the full retry bound, unlike a 4xx", async () => {
+    let calls = 0;
+    const fetchImpl: typeof fetch = async () => { calls += 1; return response({}, 500); };
+    const result = await fetchAddressSuggestions("120 Broadway", { fetchImpl, backoffMs: 0 });
+    expect(result).toEqual({ kind: "error", reason: "source_unavailable" });
+    expect(calls).toBe(ADDRESS_SEARCH_MAX_ATTEMPTS);
+  });
+});
+
 /**
  * AS-8: one real-shape NYC address per borough — Manhattan, Brooklyn, Queens,
  * the Bronx, and Staten Island — resolves END-TO-END through the repaired fetch
```

---

## §B — Remaining zoning-context-panel tests (verbatim appended block)

`apps/web/src/components/architect/__tests__/zoning-context-panel.test.tsx`. This block is a pure
**append**: the file previously ended at the AS-4 describe (prior last line was `});` closing that
describe), and the lines below (current source lines 213–312) are all additions — so this verbatim
block IS the diff. The header (source lines 1–39, unchanged) already imports `within`,
`PropertyOverview`, `baseProfile` and defines `ZOLA_PREFIX` / `renderPanel`, so the `renderOverview`
helper and the three describe blocks resolve. Reproduced byte-for-byte from the working tree:

```tsx
function renderOverview(profile = baseProfile()) {
  return render(
    <PropertyOverview
      profile={profile}
      scenario={null}
      evaluation={null}
      onInspect={vi.fn()}
    />,
  );
}

describe("AS-5 (DB-019a) — both ZoLa link glyphs are decorative (aria-hidden), names unchanged", () => {
  it("hides the ↗ glyph on the panel's ZoLa link while keeping its accessible name", () => {
    const panel = renderPanel();
    const link = within(panel).getByTestId("zoning-context-zola-link");
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
    // The decorative arrow is out of the accessible name — the link still
    // resolves by its human name.
    expect(within(panel).getByRole("link", { name: "Open in ZoLa" })).toBe(link);
  });

  it("hides the ↗ glyph on the overview Site-context ZoLa link while keeping its name", () => {
    renderOverview();
    const link = screen.getByTestId("site-zola-link");
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
    expect(screen.getByRole("link", { name: "Open ZoLa" })).toBe(link);
  });
});

describe("AS-6 (DB-019b) — PropertyOverview honest absent note on a non-canonical or null BBL", () => {
  it("renders NO Site-context link and a panel-matched absent note when the BBL is not canonical", () => {
    const profile = baseProfile();
    profile.identity.bbl = "12345"; // wrong length — zolaLotUrl returns null
    renderOverview(profile);
    expect(screen.queryByTestId("site-zola-link")).toBeNull();
    const siteAbsent = screen.getByTestId("site-zola-absent");
    // PropertyOverview nests ZoningContextPanel, so its own absent note renders
    // in the same tree — assert the two honest notes are the SAME copy (matched,
    // not independently drifting literals).
    const panelAbsent = screen.getByTestId("zoning-context-zola-absent");
    expect(siteAbsent.textContent).toBe(panelAbsent.textContent);
    expect(siteAbsent.textContent).toContain("needs a valid BBL");
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
    // Same copy the nested panel shows for its own null-derived absence — the
    // two honest notes stay matched, not independently drifting literals.
    const panelAbsent = screen.getByTestId("zoning-context-zola-absent");
    expect(siteAbsent.textContent).toBe(panelAbsent.textContent);
    expect(siteAbsent.textContent).toContain("needs a valid BBL");
  });

  it("with a canonical BBL the Site-context link renders and no absent note appears (prior rendering preserved)", () => {
    renderOverview();
    expect(screen.getByTestId("site-zola-link").getAttribute("href")).toBe(
      `${ZOLA_PREFIX}1000010010`,
    );
    expect(screen.queryByTestId("site-zola-absent")).toBeNull();
  });
});

describe("AS-7 (DB-019c) — landmark/historic rows surface the mapped-feature coverage_status", () => {
  it("shows each present designation's coverage status inline, display-only (base fixture: conditional)", () => {
    const panel = renderPanel();
    const designations = within(panel).getByTestId("zoning-context-designations");
    // One badge per PRESENT designation (landmark + historic), read straight
    // from the fixture's coverage_status — nothing computed. Not colour-only:
    // CoverageBadge carries the enum token + a screen-reader gloss.
    const badges = designations.querySelectorAll<HTMLElement>(".status-badge");
    expect(badges).toHaveLength(2);
    for (const badge of Array.from(badges)) {
      expect(badge.className).toContain("status-conditional");
    }
  });

  it("adds NO coverage badge on an Unknown row — nothing is invented when the feature is absent", () => {
    const profile = baseProfile();
    profile.zoning.mapped_features = [];
    const panel = renderPanel(profile);
    const designations = within(panel).getByTestId("zoning-context-designations");
    expect(designations.querySelectorAll(".status-badge")).toHaveLength(0);
    // The honest Unknown rows are still both present.
    expect(within(panel).getAllByText("Unknown — not supplied")).toHaveLength(2);
  });
});
```

---

## §C — Unchanged supporting source (inline; read, NOT executed — corroboration only)

These excerpts confirm each new test asserts against real, existing wiring. Reading them is
corroboration, NOT a pass claim.

### C.1 Focus-return wiring (AS-3 / DB-007b) — `apps/web/src/components/address/AddressResolutionScreen.tsx` (UNCHANGED)
The nonce and its effect already exist; the new AS-3 test drives exactly this path (the architect
branch focuses `autocompleteRef`, whose input is labelled "Street address"). Verbatim at the cited
lines:
```tsx
// L123-127
const [entryFocusNonce, setEntryFocusNonce] = useState(0);
useEffect(() => {
  if (entryFocusNonce > 0)
    (architect ? autocompleteRef : streetInputRef).current?.focus();
}, [entryFocusNonce, architect]);

// L209-212 — "Not my property" clears the result and bumps the nonce (async focus
// after the entry UI remounts); form values are deliberately retained.
const notMyProperty = useCallback(() => {
  setResult(null);
  setEntryFocusNonce((nonce) => nonce + 1);
}, []);
```
The `not-my-property` affordance the AS-3 test clicks is rendered by `AddressConfirmCard.tsx`; the
architect entry UI is `AddressAutocomplete` (labelled input "Street address",
`AddressAutocomplete.tsx:132`).

### C.2 Coverage-badge wiring (AS-7 / DB-019c)
`mappedFeatureView` derives `coverageStatus` from the fixture's `coverage_status` behind a guard
(null when absent → absent rows render no badge) — `apps/web/src/lib/contract.ts` (UNCHANGED):
```ts
// L254 field; L265-267 derivation
coverageStatus: CoverageStatus | null;
...
coverageStatus: isCoverageStatus(record.coverage_status)
  ? record.coverage_status
  : null,
```
`CoverageBadge` renders `status-badge status-${status}` (the class AS-7 queries) plus a
screen-reader gloss, so status is never colour-only — `apps/web/src/components/property/CoverageBadge.tsx:9-18` (UNCHANGED):
```tsx
export function CoverageBadge({ status }: { status: CoverageStatus }) {
  const display = coverageDisplay(status);
  return (
    <span className={`status-badge status-${status}`} title={display.gloss}>
      <span aria-hidden="true">{display.symbol}</span>
      {display.value}
      <span className="visually-hidden"> — {display.gloss}</span>
    </span>
  );
}
```
Panel designation wiring — `ZoningContextPanel.tsx` (CHANGED by DB-019c; the badge is the new
per-row addition). `DESIGNATION_FLAGS` is landmark + historic only (`splitzone` excluded), and each
present row draws its badge from the per-feature `view`:
```tsx
const DESIGNATION_FLAGS: ReadonlyArray<readonly [string, string]> = [
  ["landmark", "Landmark"],
  ["histdist", "Historic district"],
];
const features = (profile.zoning.mapped_features ?? []).map(mappedFeatureView);
```
**Fixture (AS-7)** — `baseProfile()` clones
`packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json`. Its
`zoning.mapped_features` array carries **eight** entries — `splitzone`, `landmark`, `histdist`,
`firm07_flag`, `pfirm15_flag`, `transitzone`, `zonemap`, `zmcode` — each with
`coverage_status: "conditional"` (re-verified this round at fixture lines 258–306). Of those, only
`landmark` and `histdist` map to the two `DESIGNATION_FLAGS` rows, so AS-7's "two
`status-conditional` badges" holds exactly:
```json
{ "feature": "landmark", "value": "INDIVIDUAL LANDMARK",
  "provenance_ref": "…-landmark", "coverage_status": "conditional" },
{ "feature": "histdist", "value": "Governors Island Historic District",
  "provenance_ref": "…-histdist", "coverage_status": "conditional" }
```

---

## §D — Other five changed files (supervisor-collected; NOT reviewer working-tree reads)

Each is a small, single-purpose change. To avoid re-inlining the aggregate patch that overran the
cap, the full diffs are **not** reproduced here; instead the supervisor collects each as a separate
digest-bound section (`git diff -- <file>` at the committed head, table blob anchors above) and
delivers it to the reviewers, who read it from the frozen commit — not from this worktree. The
per-file summary below is the producer's account of what each diff does; the working-tree content
was re-read natively this round and matches.

- **`AddressAutocomplete.tsx`** (16a03885..74c2fa2c) — DB-009 + DB-006 copy.
  - `:12-16` export `FULL_ADDRESS_SEARCH_LABEL = "Search this full address"` (single source of truth).
  - `:24-31` `ERROR_MESSAGES` — every reason that still renders the button names it via the constant; adds the `rejected` line ("didn't accept that search").
  - `:172-175` the button renders `{FULL_ADDRESS_SEARCH_LABEL}` (was a bare string literal).
- **`autocomplete.test.tsx`** (d32f820a..378caf89) — DB-006/007/009 tests.
  - `:4` imports `FULL_ADDRESS_SEARCH_LABEL`.
  - `:53` adds `["rejected", /didn.t accept that search/i]` to the reason→copy table.
  - `:68-81` AS-2: timeout still offers the enabled `full-address-search` button.
  - `:83-94` AS-4: the status copy and the button both read `FULL_ADDRESS_SEARCH_LABEL` (no drift).
- **`PropertyOverview.tsx`** (ce7c148b..0eb5ffb9) — DB-019a + DB-019b.
  - `:58-65` Site-context heading: canonical BBL → `site-zola-link` with `<span aria-hidden="true">↗</span>`; else `site-zola-absent` note, copy byte-matched to the panel.
- **`ZoningContextPanel.tsx`** (98a129e6..caf78654) — DB-019a + DB-019c.
  - `:3` import `CoverageBadge`.
  - `:58` `Open in ZoLa <span aria-hidden="true">↗</span>`.
  - `:115-121` per present designation row, render `<CoverageBadge status={view.coverageStatus} />` (guarded; absent → nothing).
- **`address-resolution.test.tsx`** (5e0d3782..50092878) — DB-007b (AS-3).
  - appended `describe("DB-007b …")` block (source lines 1005–1026): architect
    `<AddressResolutionScreen architect />`, resolve via `fillAndSubmit()`, click `not-my-property`,
    then `await waitFor(() => document.activeElement === getByLabelText("Street address"))`; asserts
    the confirm card is gone. Helpers `stubFetchOnce`, `fillAndSubmit`, `resolvedDoc`, `jsonResponse`
    are defined earlier in the file.

---

## §E — Controller task-file patch (attributed; NOT producer material; reconciliation requested)

`project-control/tasks/M5-T038.json` shows modified in the worktree. It is controller /
orchestrator authority (ADR-005); **I did not edit or revert it, and I will not.** The working-tree
copy carries control-plane bookkeeping only, no producer content:
- `inputs[0]` carries the CHECKPOINT ENVELOPE guidance (omit branch/worktree/starting_sha/
  current_sha; the controller fills authoritative values).
- `worktree` is the full path `C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\wt-m5t038` (normalized from
  the short `wt-m5t038`).

**Request to the controller:** independently reconcile this task-file diff, attribute it to the
control-plane edits above, and provide its own diff. It stays OUT of the producer change set (the
nine files in the table above). The producer takes no action on it.

---

## §F — Validation: executed vs source inspection vs pending CI

**Executed this round (real command through the broker):**
- `python tools/modularity_check.py --check` → `selected 442 files; failures 0; warnings 19`.
  None of the four touched source files (`address-search.ts`, `AddressAutocomplete.tsx`,
  `PropertyOverview.tsx`, `ZoningContextPanel.tsx`) nor any touched test file is among the 19
  warnings — all 19 are pre-existing api / tools / surveyReview modules. Adding test cases
  introduces no production growth. This is the packet's only documented test command.

**Source inspection (read, NOT executed — corroboration only):** §A/§B/§C and the per-file re-read
in §D. Reading source shows each new test asserts against real wiring; it does NOT prove a test
passes or that TypeScript compiles clean.

**Pending CI (orchestrator captures on the pushed head; NOT proven here — thin-client rule, no
npm/npx/node locally):**
- vitest web suites: `address-search`, `autocomplete`, `zoning-context-panel`,
  `address-resolution`.
- `tsc` typecheck.
- Full CI green on the pushed implementation head (AS-8).

This report does NOT claim any web suite passes or that `tsc` is clean; those claims are withheld
until the corresponding CI evidence exists on the pushed head. `python tools/modularity_check.py
--check` (executed above) is separate from and never a substitute for that pending web CI.

## Handoff state

- Working-tree changes are uncommitted (git is orchestrator authority, ADR-005; commit/push are
  not this packet's documented commands). No implementation changed this round — only this report.
- The orchestrator/supervisor: collects the five §D files as separate digest-bound sections at the
  committed head; commits/pushes the nine producer files; confirms web CI + typecheck green on the
  pushed head; reconciles the §E task-file diff; then records G0/G2/G3/G4/G5 with the named
  reviewers (code-reviewer, qa-engineer, security-reviewer, human-journey-reviewer,
  directive-compliance-verifier). No merge or acceptance is authorized by this checkpoint.
- No out-of-scope edits: `development-limits.test.tsx` (M5-T037 lane) is not touched. Its
  `getByRole("link", { name: /Open ZoLa/ })` still matches the trimmed accessible name after the
  aria-hidden change, and the new absent note is a `<span>` (not a link), so its
  `queryByRole("link")` null assertion holds. No conflict to record.
