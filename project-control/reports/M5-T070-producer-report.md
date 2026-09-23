# M5-T070 producer report — Preliminary-development-limits panel (D-082-R003 + D-083)

Status at this checkpoint: **IN_PROGRESS** (increment 2 closes the named increment-1 gap; the
producer cannot self-accept — final proof is CI-green on the pushed head, thin client). Run
lineage: `persistent3-local-17-m5t070`. Increment-1 material is committed on-branch (51ffc5cb,
harvested); increment-2 edits are uncommitted working-tree state for the orchestrator to harvest.
See "Increment 2" below for the two files this unit changed.

Evidence-resubmit pass (2026-09-23): the prior transmission dropped the reviewer-named spans beyond
a diff cutoff. This pass is REPORT-ONLY — the ONLY file it edits is this report; it embeds those
spans verbatim as separately bounded, supervisor-collectable segments (see "Supervisor-collectable
evidence segments" below: S1 = `entry.test.tsx:311-374`; S2 = disclosure; S3 = response
serialization; S4 = F01 request inputs; S5 = `maxEnvelopeRequestForProfile`). No test was rewritten
to accommodate truncation and no production scope was expanded.

This pass vs. the cumulative working tree (`git diff --stat HEAD`, HEAD a9148091): this report-only
pass ran NO Edit/Write against either test file. The uncommitted working tree carries three files —
the two increment-2 test files, unchanged by this pass (`apps/web/e2e/proposal-editor.spec.ts` +196;
`apps/web/src/components/architect/__tests__/entry.test.tsx` +182), plus this report (+415/-16). The
producer does NOT self-assert the two test files' byte-identity to the prior submission by a
self-computed digest — thin client, the producer runs no hashing command (see the segment section
below); the supervisor computes the LF-normalized git-blob digest of each test file at harvest and
compares it against the prior submission's frozen manifest. Web outcomes stay UNKNOWN until
orchestrator-provided CI on the pushed head.

## Provenance note (read first)

On entry this worktree already carried a COMPLETE, uncommitted production implementation of all
five source files (the orientation packet's "fresh unit / no prior progress" did not match the
tree — a prior unit of this lineage left the production code uncommitted, tests unwritten). This
unit did **not** author the production source; it verified the source against the contract and
wrote the missing test suites. The orchestrator/DCV must confirm production-code provenance at
harvest and prove behavior in CI (thin client: no web tests run locally — CODING_RULES).

## Implementation surface (inherited production code, verified this unit)

- `apps/web/src/lib/architect/max-envelope-api.ts` — typed client for the UNMOUNTED
  `POST /api/v1/max-envelope`. Mirrors the exact (status,state) matrix (`DOCUMENTED_PAIRS`
  :194), bounds every reflected string, size-bounds before parse (:427), derives the
  D-083-R004 incomplete-aggregate predicate (`envelopeAggregateIsComplete` :538), the adoption
  gate (`candidateIsAdoptable` :545), answer-first request assembly (`maxEnvelopeRequestForProfile`
  :506, sends NO geometry). No client CRS math.
- `apps/web/src/components/architect/MaxEnvelopePanel.tsx` — answer-first panel; heading class
  "Preliminary development limits" (:223), verbatim disclosure (:130), per-dimension binding
  provenance + gap + surfaced-never-resolved advisory (`DimensionRow` :51), "Generated building
  option" as the ONLY building-shaped claim (:154), no unrestricted-green aggregate (:134),
  typed degradation card (:246), one-action adoption via the ONE draft model (:112).
- `apps/web/src/lib/architect/proposal-draft.ts` — `draftFromCandidate` (:393) seeds the ONE
  draft model from a candidate verbatim (no math/CRS), provenance labeled PROPOSED.
- `apps/web/src/components/architect/ArchitectEntry.tsx` — `ProposalSurface` (:44) composes the
  panel ADDITIVELY above the accepted `ProposalEditor`; adoption lifts to `adoptedDraft`.
- `apps/web/src/components/architect/ProposalEditor.tsx` — accepts `adoptedDraft` (:60); a new
  non-null draft replaces the working draft; manual entry unchanged (:87 effect).

## Tests authored this unit (acceptance-scenario coverage)

- `__tests__/max-envelope-api.test.ts` (NEW full suite) — AS-1 (disclosure verbatim, binding
  provenance, gap by reason, advisory both ids), AS-5 (documented (status,state) matrix; malformed
  200 → validation_failure; size-bound-before-parse; exact request assembly; null on no lot area),
  AS-4 (candidate bounding + adoptability gate; malformed candidate dropped), **AS-3
  mutation-sensitive** (gap→binding flips aggregate; advisory alone keeps incomplete).
- `components/architect/__tests__/max-envelope-panel.test.tsx` (NEW full suite) — AS-1/AS-2 render,
  AS-2 source-grep proving ABSENCE of "maximum allowed building"/"demonstrated maximum",
  **AS-3 mutation** on `data-complete`, AS-4 adoption (`onAdopt` seeded draft), AS-6 degradation
  (no-context / retryable failure / feature-off no-retry).
- `lib/architect/__tests__/proposal-draft.test.ts` (APPENDED) — `draftFromCandidate` verbatim
  pass-through, D-083 claim-class label + PROPOSED provenance, runnable-after-seed (AS-4).
- `components/architect/__tests__/proposal-editor.test.tsx` (APPENDED) — adoption replaces the
  working draft, seeds the numeric authority, announces PROPOSED, manual entry stays available (AS-4).

## Self-checks

- `python tools/modularity_check.py --check` → `failures 0; warnings 22` (all 22 pre-existing,
  none in this packet's files). Exit 0.
- Web suites NOT run locally (thin client). Web behavior proves ONLY in CI on the pushed head.

## Increment 2 (this unit, revised) — the increment-1 gap is closed, then the two specs HARDENED

Two files changed; both test-only (no production source touched this increment):

- `apps/web/e2e/proposal-editor.spec.ts` (AS-5 e2e, max-envelope journey). The route stub now
  asserts the **COMPLETE POST body** with a deep+strict `toEqual` — BBL 1000010100 is served
  through the REAL profile builder over the committed official F01 fixture
  (`services/api/tests/fixtures/pluto/F01_single_lot_normal.json`: `lotarea` "23121" → 23121;
  single `zonedist1` "R3-2") — so it pins the EXACT fixture-derived `lot.area_sq_ft` 23121,
  `area_provenance` `{source_id:"architect_surface_lot_context"}`, `lot_rule_facts`
  `{zoning_district:"R3-2"}`, `label` "BBL 1000010100 preliminary development limits", and
  `lot_line_segments`/`street_lines` both `[]` (no geometry, no client CRS math); being strict,
  `toEqual` also proves the ABSENCE of any unexpected field at the top level and inside `lot`.
  The stubbed response body is now faithful to the authoritative `MaxEnvelope.as_dict()`
  serialization: the disclosure is the EXACT `ENVELOPE_DISCLOSURE` text
  (`services/api/app/scenario/max_envelope.py` :100-108), asserted verbatim; the FITTED
  `candidate_placement` carries ALL five fields, including real
  `lot_rectangle`/`footprint` `{anchor_x,anchor_y,width_ft,depth_ft,area_sq_ft}` records (no
  longer `{}`). An explicit **panel-before-editor ORDERING** assertion
  (`compareDocumentPosition`) proves the limits panel precedes the editor in the DOM. The
  journey still asserts the verbatim disclosure + heading class, binding/gap rows,
  `data-complete="false"` (no green, D-083-R004), the additive editor seed (5 verts, vertex0 X
  1000000), then one-action adoption reseeding the numeric authority (4 verts, vertex0 X
  1000200) + PROPOSED announcement + manual entry still present.
- `apps/web/src/components/architect/__tests__/entry.test.tsx` (AS-6, revised describe). The
  scoped `vi.stubGlobal("fetch", …)` fixture is now faithful to `as_dict()` (the real
  disclosure text; a FITTED contained candidate with the full five-field `candidate_placement`
  incl. `lot_rectangle`/`footprint`; one binding + one gap dimension). Three tests: (1) explicit
  **panel-BEFORE-editor** DOM ordering (`compareDocumentPosition`) with both present (additive);
  (2) adoption THROUGH the panel's one action reseeds the numeric authority (5→4 vertices,
  vertex0 X 1000000→1000200) with the PROPOSED announcement, then **manual editing AFTER
  adoption** mutates draft state (retype vertex 0 X → "1000999"; Add vertex → 5); (3) a thrown
  fetch degrades to the typed `envelope-failure` card (no disclosure), and **manual editing
  AFTER the failure** mutates draft state (retype → "1000123"; Add vertex → 6). `baseProfile`
  carries `lot_facts.lotarea.value` 7577714, so the panel fetches in every case; `afterEach`
  unstubs the global.

Accepted tests and frozen paths preserved: the M5-T060/T065/T066 e2e journeys above the AS-5
test, the accepted `entry.test.tsx` describes, and the harvested increment-1 unit suites
(`max-envelope-api.test.ts`, `max-envelope-panel.test.tsx`, `proposal-draft.test.ts`,
`proposal-editor.test.tsx`) are untouched; no production source and no forbidden path changed.

## Authored coverage vs. executed proof (read before recording a gate)

This unit **AUTHORED** the test code above; it did **not EXECUTE** the web suites. The owner PC
is a thin client and CODING_RULES forbids running npm/npx/node locally, so web behavior proves
ONLY in CI on the pushed head — no web outcome is claimed as verified from local reasoning.

- AUTHORED (this unit, verifiable by reading the diff): the strengthened e2e POST-body
  `toEqual`, the faithful `as_dict()` response fixtures (real disclosure + full five-field
  `candidate_placement`), the panel-before-editor ordering assertions, and the
  manual-editing-after-adoption / after-failure state-change assertions.
- EXECUTED PROOF (NOT producer-owned — the orchestrator/DCV collects it at harvest): web-unit
  green incl. the revised `entry.test.tsx` AS-6 cases, and web-e2e green incl. the hardened
  `proposal-editor.spec.ts` AS-5 journey, on the pushed head, alongside the unchanged accepted
  T060/T065/T066 specs.

Local self-check this increment (the ONLY permitted local command; documented_test_commands):
`python tools/modularity_check.py --check` → `failures 0; warnings 22` (all 22 pre-existing,
none in this packet's files; test-only edits, no production growth). Exit 0. Web suites NOT run
locally (thin client).

## Supervisor-collectable evidence segments (bounded verbatim, for digest-bound collection)

Reviewer directive (2026-09-23 resubmit): line references alone are insufficient, and the prior
transmission dropped `entry.test.tsx:311-374`, the complete increment-2 report changes, and the
authoritative excerpts beyond a diff cutoff. So the required content is embedded here VERBATIM as
separately bounded segments, each delimited by explicit `--- BEGIN <id> ---` / `--- END <id> ---`
markers and anchored to an exact source path + line span, so the supervisor can collect each as its
OWN segment (below any single-diff cutoff) and digest-bind it. This deliberately overrides the
general "never embed long verbatim" report discipline for exactly these reviewer-named spans.

Digest-binding responsibility: the producer supplies each segment verbatim and byte-anchored (path +
line span + line count); the supervisor computes the LF-normalized sha256 / git-blob digest for each
collected segment at harvest (thin client: the only local command this packet documents is
`python tools/modularity_check.py --check`, so the producer runs no hashing command — strip `\r` /
LF-normalize before hashing per CODING_RULES). Every segment is byte-verifiable by opening its named
source at its named lines. No test was rewritten and no production scope expanded to produce this
section — it is report-only.

### Segment S1 — AS-6 test bodies (entry.test.tsx:311-374, 64 lines, this unit's increment-2 change)

Source: `apps/web/src/components/architect/__tests__/entry.test.tsx`, lines 311-374. This is the
reviewer-named span: the two vertex-input helpers plus the three AS-6 tests (panel-before-editor
ordering, adoption + manual-edit-after-adoption, degradation + manual-edit-after-failure) and the
two `afterEach` teardowns. The surrounding `describe` header (:201-214), `ENVELOPE_DISCLOSURE`
constant (:206-214), `OPTION_2263` (:219-224) and `envelopeResponse()` (:235-309) are unchanged
context above this span in the same file.

--- BEGIN S1 (entry.test.tsx:311-374) ---
```tsx
  const vertexXInputs = () => screen.getAllByLabelText(/^Vertex \d+ X coordinate$/) as HTMLInputElement[];
  const vertexX0 = () => screen.getByLabelText("Vertex 0 X coordinate") as HTMLInputElement;

  it("renders the limits panel BEFORE the accepted editor in document order (answer-first, additive)", async () => {
    state.params.set("view", "proposal");
    vi.stubGlobal("fetch", vi.fn(async () => envelopeResponse()));
    render(<ArchitectEntry />);
    // The panel leads with the server disclosure rendered VERBATIM...
    expect(await screen.findByTestId("envelope-disclosure")).toHaveTextContent(ENVELOPE_DISCLOSURE);
    expect(screen.getByRole("heading", { name: "Preliminary development limits" })).toBeInTheDocument();
    // ...and the accepted editor still renders, fully available.
    const panel = screen.getByTestId("max-envelope-panel");
    const editor = screen.getByTestId("proposal-editor");
    expect(screen.getByTestId("editor-honesty")).toHaveTextContent("not a city record");
    expect(screen.getByRole("button", { name: "Add vertex" })).toBeInTheDocument();
    // Explicit ORDERING (not merely both present): the panel PRECEDES the editor in
    // the DOM — the computed limits lead the surface, the editor follows.
    expect(panel.compareDocumentPosition(editor) & Node.DOCUMENT_POSITION_FOLLOWING).not.toBe(0);
  });

  it("adopts the Generated building option through the panel; manual editing AFTER adoption still mutates the draft", async () => {
    state.params.set("view", "proposal");
    vi.stubGlobal("fetch", vi.fn(async () => envelopeResponse()));
    render(<ArchitectEntry />);
    await screen.findByTestId("envelope-disclosure");
    // The editor starts on the MANUAL rectangle seed (5 vertices, vertex 0 X 1000000).
    expect(vertexXInputs()).toHaveLength(5);
    expect(vertexX0().value).toBe("1000000");

    // ONE action adopts the option: the numeric AUTHORITY is reseeded from the
    // candidate (4 vertices, vertex 0 X 1000200) and announced as PROPOSED.
    fireEvent.click(screen.getByTestId("adopt-candidate"));
    expect(vertexXInputs()).toHaveLength(4);
    expect(vertexX0().value).toBe("1000200");
    expect(screen.getByTestId("proposal-check-announcer")).toHaveTextContent("Adopted the Generated building option");

    // Manual editing AFTER adoption still changes draft state (never a dead or
    // read-only surface): retype a coordinate, then add a vertex.
    fireEvent.change(vertexX0(), { target: { value: "1000999" } });
    expect(vertexX0().value).toBe("1000999");
    fireEvent.click(screen.getByRole("button", { name: "Add vertex" }));
    expect(vertexXInputs()).toHaveLength(5);
  });

  it("degrades the panel to a typed failure card; manual editing AFTER the fetch failure still mutates the draft", async () => {
    state.params.set("view", "proposal");
    vi.stubGlobal("fetch", vi.fn(async () => { throw new Error("network down"); }));
    render(<ArchitectEntry />);
    // A typed failure card (never a dead surface, never a fabricated limit)...
    const failure = await screen.findByTestId("envelope-failure");
    expect(failure).toHaveTextContent("could not be reached");
    expect(screen.queryByTestId("envelope-disclosure")).not.toBeInTheDocument();
    // ...and the accepted editor below stays fully usable: manual editing changes state.
    expect(screen.getByTestId("proposal-editor")).toBeInTheDocument();
    expect(vertexXInputs()).toHaveLength(5);
    fireEvent.change(vertexX0(), { target: { value: "1000123" } });
    expect(vertexX0().value).toBe("1000123");
    fireEvent.click(screen.getByRole("button", { name: "Add vertex" }));
    expect(vertexXInputs()).toHaveLength(6);
  });
});

afterEach(() => vi.unstubAllGlobals());
afterEach(cleanup);
```
--- END S1 ---

### Segment S2 — Server disclosure asserted verbatim (max_envelope.py:100-109)

Source: `services/api/app/scenario/max_envelope.py`, lines 100-109 (`ENVELOPE_DISCLOSURE`). The
panel renders this string char-for-char; S1's ordering test and the e2e journey both assert it
verbatim (a paraphrase or truncation fails). The `ENVELOPE_DISCLOSURE` constant duplicated in
`entry.test.tsx:206-214` is byte-identical to this authoritative source.

--- BEGIN S2 (max_envelope.py:100-109) ---
```python
ENVELOPE_DISCLOSURE = (
    "This maximum-buildable envelope is a DETERMINISTIC, rules-derived ESTIMATE for the "
    "rectangle-prism massing class - NOT a city record, a permit, an approval, or a legal "
    "determination. Each dimension is the tightest applicable draft rule's allowance for this "
    "lot (the looser rules are automatically satisfied and recorded as out-competed); where "
    "more than one rule bounds a dimension, which rule governs is a legal determination "
    "requiring professional review, surfaced here as an advisory rather than resolved. "
    "Non-commensurable dimensions (residential FAR, rear yard) are disclosed as honest gaps. "
    "Qualified professional review is required before any reliance."
)
```
--- END S2 ---

### Segment S3 — Response serialization (as_dict trio + FITTED footprint)

Source: `services/api/app/scenario/max_envelope.py`. The stubbed unit/e2e response bodies mirror
this byte-shape exactly (never a guessed field). Four spans: `CandidatePlacement.as_dict` (:340-347),
`MaxEnvelope.as_dict` (:368-386), `_LotRect.as_dict` (:617-621), and the FITTED-placement footprint
construction (:882-896).

--- BEGIN S3a (max_envelope.py:340-347, CandidatePlacement.as_dict) ---
```python
    def as_dict(self) -> dict:
        return {
            "status": self.status.value,
            "detail": self.detail,
            "lot_rectangle": self.lot_rectangle,
            "footprint": self.footprint,
            "contained": self.contained,
        }
```
--- END S3a ---

--- BEGIN S3b (max_envelope.py:368-386, MaxEnvelope.as_dict) ---
```python
    def as_dict(self) -> dict:
        return {
            "massing_class": self.massing_class,
            "label": self.label,
            "disclosure": self.disclosure,
            "dimensions": [d.as_dict() for d in self.dimensions],
            "candidate": self.candidate,
            "candidate_notes": list(self.candidate_notes),
            "candidate_placement": self.candidate_placement.as_dict(),
            "candidate_consistency": self.candidate_consistency,
            "summary": {
                "binding": self.binding_count,
                "gap": self.gap_count,
                "saturating_binding": self.saturating_binding_count,
                "total": len(self.dimensions),
            },
            "rule_input_bindings": dict(self.rule_input_bindings),
            "unmapped_lot_facts": list(self.unmapped_lot_facts),
        }
```
--- END S3b ---

--- BEGIN S3c (max_envelope.py:617-621, _LotRect.as_dict) ---
```python
    def as_dict(self) -> dict:
        return {
            "anchor_x": self.min_x, "anchor_y": self.min_y,
            "width_ft": self.width, "depth_ft": self.depth, "area_sq_ft": self.area,
        }
```
--- END S3c ---

--- BEGIN S3d (max_envelope.py:882-896, FITTED placement footprint) ---
```python
    placement = CandidatePlacement(
        status=CandidatePlacementStatus.FITTED,
        detail=(
            f"rectangle-prism footprint {width} x {depth} ft anchored at the lot's SW corner "
            f"({rect.min_x}, {rect.min_y}), scaled to the lot's proportions, saturating the "
            "coverage ratio and PROVEN contained within the lot; the height is saturated by the "
            "level records. A rules-derived estimate placement, not a surveyed siting."
        ),
        lot_rectangle=rect.as_dict(),
        footprint={
            "anchor_x": rect.min_x, "anchor_y": rect.min_y,
            "width_ft": width, "depth_ft": depth, "area_sq_ft": width * depth,
        },
        contained=True,
    )
```
--- END S3d ---

### Segment S4 — F01 request inputs (fixture raw → builder → derived request)

The e2e journey (`proposal-editor.spec.ts`, AS-5) drives BBL 1000010100 through the REAL profile
builder over the committed official F01 fixture and pins the EXACT fixture-derived request. This
segment carries the full derivation chain so the reviewer can byte-verify each hop.

Raw fixture fields (`services/api/tests/fixtures/pluto/F01_single_lot_normal.json`, inside
`response_body_raw`): `"lotarea":"23121"`, `"zonedist1":"R3-2"` (single district; `zonedist2..4`
absent). These are the ONLY two fields the request depends on.

--- BEGIN S4a (builder.py:117-118, ZONING_DISTRICT_COLUMNS) ---
```python
ZONING_DISTRICT_COLUMNS: tuple[str, ...] = (
    "zonedist1", "zonedist2", "zonedist3", "zonedist4",
)
```
--- END S4a ---

--- BEGIN S4b (builder.py:312-323, _fact_value → lot_facts.<col>.value) ---
```python
def _fact_value(fact: dict, drift_columns: set[str]) -> dict:
    """property_profile fact_value: value + provenance_ref (+units), plus the
    additive coverage_status key (schema-permitted additional property)."""
    value = {
        "value": fact["normalized_value"],
        "provenance_ref": fact["provenance_id"],
        "coverage_status": _coverage_status(fact, drift_columns),
    }
    if fact.get("units") is not None:
        # fact_value.units is typed string in the contract; omit when unitless.
        value["units"] = fact["units"]
    return value
```
--- END S4b ---

--- BEGIN S4c (builder.py:395-400, _zoning → districts) ---
```python
    return {
        "districts": collect(ZONING_DISTRICT_COLUMNS),
        "commercial_overlays": collect(OVERLAY_COLUMNS),
        "special_districts": collect(SPECIAL_DISTRICT_COLUMNS),
        "mapped_features": mapped_features,
    }
```
--- END S4c ---

--- BEGIN S4d (bounded.ts:90-99, boundedZoningDistrict) ---
```ts
export function boundedZoningDistrict(
  value: unknown,
  max: number = MAX_ZONING_DISTRICT_LENGTH,
): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const cleaned = value.replace(NON_ZONING_DISTRICT_CHARS, "").slice(0, max);
  return cleaned === "" ? null : cleaned;
}
```
--- END S4d ---

Derivation (each hop byte-verifiable above): raw `lotarea` `"23121"` normalizes upstream (connector)
to the number `23121`, which `_fact_value` (S4b) passes through as `lot_facts.lotarea.value`;
`_zoning.collect(ZONING_DISTRICT_COLUMNS)` (S4a/S4c) collects only the present `zonedist1` →
`zoning.districts == ["R3-2"]` (length 1); `boundedZoningDistrict("R3-2")` (S4d) keeps `"R3-2"`
unchanged. `maxEnvelopeRequestForProfile` (S5) then assembles the request that the e2e stub asserts
with a deep+strict `toEqual`:

```json
{
  "lot": {
    "area_sq_ft": 23121,
    "area_provenance": { "source_id": "architect_surface_lot_context" },
    "lot_line_segments": [],
    "street_lines": []
  },
  "lot_rule_facts": { "zoning_district": "R3-2" },
  "label": "BBL 1000010100 preliminary development limits"
}
```

### Segment S5 — Answer-first request assembly, maxEnvelopeRequestForProfile (max-envelope-api.ts:527-548)

Source: `apps/web/src/lib/architect/max-envelope-api.ts`, lines 527-548. Builds the request from the
profile's lot context ALONE (recorded area + a single recorded district); sends NO geometry
(`lot_line_segments: []`, `street_lines: []` — the profile's geometry is display 4326, never
measured); returns `null` when the lot area is not a usable finite positive number (the panel then
degrades to a typed "cannot compute" card). No client-side CRS math.

--- BEGIN S5 (max-envelope-api.ts:527-548) ---
```ts
export function maxEnvelopeRequestForProfile(profile: PropertyProfile): MaxEnvelopeRequest | null {
  const area = profile.lot_facts?.lotarea?.value;
  if (typeof area !== "number" || !Number.isFinite(area) || area <= 0) {
    return null;
  }
  const districts = Array.isArray(profile.zoning?.districts) ? profile.zoning.districts : [];
  const lot_rule_facts: Record<string, string> = {};
  if (districts.length === 1) {
    const district = boundedZoningDistrict(districts[0]);
    if (district) lot_rule_facts.zoning_district = district;
  }
  return {
    lot: {
      area_sq_ft: area,
      area_provenance: { source_id: "architect_surface_lot_context" },
      lot_line_segments: [],
      street_lines: [],
    },
    lot_rule_facts,
    label: `BBL ${profile.identity.bbl} preliminary development limits`,
  };
}
```
--- END S5 ---

### Complete increment-2 report changes (collection pointer)

The complete increment-2 producer-report change set = the "Increment 2" section above (the prose
describing both changed test files) TOGETHER WITH Segment S1 (the verbatim AS-6 test bodies). The
second increment-2 file, `apps/web/e2e/proposal-editor.spec.ts` (AS-5 e2e), is described in the
Increment 2 section; its request-contract assertion corroborates against Segments S4 and S5, and its
response body against Segments S2 and S3. All are collectable here as bounded segments so none falls
beyond a diff cutoff.

## Remaining before acceptance (not producer-owned)

1. CI green on the pushed head across web-unit (incl. the new `entry.test.tsx` AS-6 cases) +
   web-e2e (the new `proposal-editor.spec.ts` AS-5 journey) + the unchanged accepted
   T060/T065/T066 specs (AS-6 display-surface safety).
2. Orchestrator harvest of both increments + independent G3/G4 review; the producer does not
   self-accept (control policy).
