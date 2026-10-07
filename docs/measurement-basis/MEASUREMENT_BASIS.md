# Measurement basis for the realistic apartment estimate

A written record with worked examples, put to the owner before any apartment estimator is
built. No estimator is built by this record and no program code is changed.

**Standing of this record.** This is a draft reading of the law and of a guideline by an
AI. It is **not professionally reviewed** and is not a legal or professional
determination. Every legal statement quotes its source and links to it; where the sources
do not settle a point, the record says "not sure" and lists it as an open point for the
owner (ADR-007). Nothing here reads as "complies" or "legally correct".

**What this record does.** It says exactly what each area includes and excludes; gives one
area-schedule form; sets out a method that works the residential **zoning floor area** and
the total **HPD dwelling-unit area** out separately from one schedule and reconciles them
so nothing is deducted twice; defines the estimate's ratio; keeps the legal unit cap
separate; and, through three made-up worked examples, checks that the method reconciles.

**What this record does not do.** It builds no estimator, approves no default, and
validates no percentage. The starting values discussed elsewhere - 700 sq ft per
apartment, a 25 percent allowance, 10 ft residential floors and a 15 ft ground floor -
remain **unapproved assumptions**; this record validates none of them. Two or three
examples cannot establish a typical figure.

---

## 1. The two areas, each defined by its source

The definitions come first, before any formula.

### 1a. Residential zoning floor area (captured law)

"Floor area" is defined by the New York City Zoning Resolution, ZR 12-10. The captured
definition opens:

> "Floor area" is the sum of the gross areas of the several floors of a building or
> buildings, measured from the exterior faces of exterior walls or from the center lines
> of walls separating two buildings.

So zoning floor area is a **gross** measure, taken to the outside face of the exterior
walls. The definition then lists what it **includes** (among them basement space used for
dwelling, elevator shafts and stairwells at each floor, and "any other floor space used
for dwelling purposes") and what it **shall not include**. The exclusions that matter for
a residential building include:

- cellar space, "except where such space is used for dwelling purposes";
- "floor space used for accessory mechanical equipment" (plus the minimum access to it);
- accessory off-street parking within stated limits (for example, group parking "located
  not more than 23 feet above curb level");
- exterior balconies/terraces where "not more than 67 percent of the perimeter ... is
  enclosed";
- "qualifying exterior wall thickness" (see below);
- an energy exclusion - "floor space within a fully electrified building or an ultra low
  energy building, of an amount equivalent to five percent of the floor area"; and
- the ZR 23-23 allowances - "floor space in buildings containing multiple dwelling
  residences allocated to building amenities, corridors, refuse storage or disposal, or
  access to elevated ground floor dwelling units that is provided in accordance with the
  provisions of Section 23-23, inclusive".

Source: capture `zr-12-10-floor-area`
(`docs/research/zr-snapshots/v1/zr-12-10-floor-area.snapshot.json`), content digest
`e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`, official page
`https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10` (the floor-area term
was last amended 12/5/2024). Two cautions on this capture, both from the independent
review of the law-capture work (`docs/DISCOVERY_BACKLOG.md`, row DB-167): (i) the whole-page
print/PDF channel for ZR 12-10 returned HTTP 504, so the capture is from the canonical
HTML with a documented fallback and the Resolution's own list-marker glyphs were not
confirmed - where this record gives an item's label (for example "the ZR 12-10 exclusion
for the 23-23 allowances"), the label is the **capture's markup position**, not a
confirmed printed label, and the item **text** is what is quoted; (ii) the capture is
source text only and is not itself a zoning determination.

**"Qualifying exterior wall thickness".** This is itself a ZR 12-10 defined term:

> "Qualifying exterior wall thickness" shall refer to the floor space occupied by exterior
> wall thickness added to a building existing on December 6, 2023, where: (1) for
> over-cladding projects: such wall thickness is added to a wall ... up to a maximum of 12
> inches ...; or (2) for re-cladding projects ...

Source: capture `zr-12-10-qualifying-exterior-wall-thickness`, content digest
`119324c8b82348cd82b354565a36468bb60e5f3680d19143f7bccfb4d16bc7bf`, same official page
(this term last amended 12/6/2023). It is an exclusion with its own conditions; it is not
a licence to subtract all exterior wall thickness.

**The ZR 23-23 allowances (captured law).** ZR 23-23 makes the amenity / corridor / refuse
/ elevated-ground-floor-access floor space exemptible:

> In the districts indicated, for buildings containing multiple dwelling residences, floor
> space allocated to building amenities, corridors, refuse storage or disposal, or access
> to elevated ground floor dwelling units may be exempted from the definition of floor
> area pursuant to Section 12-10, provided that the provisions of this Section, inclusive,
> are met.

The four operative provisions, each quoted from its own capture, are **conditional
allowances, not automatic deductions**:

| Allowance | What the law allows | Source capture (digest) |
|---|---|---|
| Amenities (incl. qualifying laundry) | "may be exempted ... in an amount not to exceed five percent of the residential floor area of the building"; "amenity space shall not include floor space for circulation through the building, including, corridors or vertical circulation spaces" | `zr-23-231` (`81eb95e8...63b49d6`) |
| Corridors | "Fifty percent of the floor space of a corridor may be exempted" under the termination/daylighting/outdoor-access criteria; another 50% "where the length of the corridor ... does not exceed 100 linear feet"; "may be applied individually or in combination" | `zr-23-232` (`0a79cda6...1fc13ad2`) |
| Refuse storage/disposal | "may be exempted ... in an amount not to exceed a maximum of three square feet per dwelling unit in the building" | `zr-23-233` (`36b8c7da...994a7710`) |
| Access to elevated ground-floor units | "up to 100 square feet of such entryways may be exempted ... for each foot of difference" in level, "no more than a maximum of 500 square feet ... for each building" | `zr-23-234` (`ca3481a9...36affdcc6`) |

Each allowance is taken **only** when the building is shown to meet its condition. ZR 23-23
also records that exempted floor space "shall be considered floor area for the purposes of
satisfying other ground floor level use regulations", which this record does not model.

**The short inclusion/exclusion list is not complete (owner directive R403).** ZR 12-10
also carries the qualifying-exterior-wall and energy-related exclusions above; these should
be checked when relevant rather than treating the list as closed.

### 1b. HPD dwelling-unit area (a guideline, not law)

HPD's measurement convention is stated in the **HPD Design Guidelines for New Construction,
2026 edition**, subsection **UNIT AREA CALCULATION**, read on 2026-10-07 at the official
HPD page
`https://www.nyc.gov/assets/hpd/downloads/pdfs/services/hpd-design-guidelines-for-new-construction-2026.pdf`
(PDF last modified 2026-09-23; sha256
`309d1863649bb7ff75d38931ed610de66c8b2ff3986b0de86299212e2cddb890`; the subsection is on
PDF page 28). Quoted verbatim:

> Dwelling unit area is measured within the perimeter walls, from the finished face of all
> exterior walls and demising partitions.
>
> Structural members that are integral components of exterior walls or demising partitions,
> as well as all mechanical and plumbing chases, are excluded from unit area calculations.
> All other structural members - including freestanding columns and columns attached to
> interior partitions - are included in unit area calculations.
>
> PTACs, PTHPs, or similar through-wall equipment protruding less than 16" into the space
> under a window are not deducted from area calculations.

So HPD dwelling-unit area is a **net interior** measure of the apartments. It **excludes**
exterior/demising wall thickness and **mechanical and plumbing chases** (the precise term),
but it **keeps** the apartment's own internal partitions and free-standing structure. The
model must therefore **not** subtract all apartment walls (owner directive R413).

**To whom it applies.** This is a guideline, not law. The 2026 edition's APPLICABILITY
section states it applies to projects developed under HPD loan programs whose initial
design-consultation submission is received on or after October 1, 2026; "Projects
participating in Housing incentive programs (either MIH or UAP) that are not subsidized
through any HPD Loan Programs shall not be subject to the Guidelines". The 2026 unit-type
target net areas (studio/0BR 350-400, 1BR 500-550, 2BR 650-725, 3BR 850-950 sq ft) are
targets for a design mix, not a prescribed or observed average.

### 1c. These bases are different and are never mixed

Zoning floor area (gross, with its own exclusions) and HPD dwelling-unit area (net interior
of the apartments) measure different things. A third convention - HCR's common-space
percentage (residential common area divided by dwelling-unit area plus common area, on an
interior-gross basis) - is a **different** basis again and is **not** used here. The record
never mixes bases, and a missing fact stays "not known" rather than becoming zero.

---

## 2. The area-schedule form (one row per component, two treatments)

One schedule lists every component once, with its measured area, how it was measured, and
its treatment under **each** system together with the provision that governs it and the
condition that must be shown before an allowance is taken. The treatment words are:
**counts**, **excluded**, or **excluded only if a stated condition is shown**. Nothing that
zoning already leaves out is deducted again.

| Component | Under residential zoning floor area | Under HPD dwelling-unit area |
|---|---|---|
| Apartment net interior (rooms) | Counts (ZR 12-10, dwelling floor space) | Counts (within the perimeter walls) |
| Interior partitions within an apartment | Counts (gross) | Counts (internal partitions included) |
| Free-standing columns inside a unit | Counts (gross) | Counts (included per HPD) |
| Demising / party-wall thickness | Counts (gross, to centre line/face) | Excluded (integral to demising partitions) |
| Exterior wall thickness | Counts (to exterior face) | Excluded (integral to exterior walls) |
| Qualifying exterior wall thickness | Excluded **only if** the over-cladding/energy conditions are shown (ZR 12-10) | Excluded (wall thickness) |
| Mechanical and plumbing chases | Counts (gross; small chases are not the accessory-mechanical room) | Excluded (HPD: "mechanical and plumbing chases") |
| Corridors | Counts, with up to 50% + 50% **excluded only if** the ZR 23-232 conditions are shown | Excluded (circulation) |
| Stairs / stairwells | Counts (ZR 12-10; tall-building exclusions do not apply to low buildings) | Excluded (circulation) |
| Elevators / lift shafts | Counts (ZR 12-10) | Excluded (circulation) |
| Lobby / entry | Counts (circulation is not an amenity under ZR 23-231) | Excluded (circulation) |
| Access to elevated ground-floor units | Excluded **only if** the ZR 23-234 condition is shown (<=100 sq ft/ft, cap 500) | Excluded |
| Refuse storage / disposal room | Counts, with up to 3 sq ft/DU **excluded only if** the ZR 23-233 condition is shown | Excluded |
| Amenity and laundry room | Counts, with up to 5% of residential floor area **excluded only if** the ZR 23-231 condition is shown | Excluded |
| Building mechanical room | Excluded **only if** it is accessory mechanical-equipment space (ZR 12-10) | Excluded |
| Cellar (not used for dwelling) | Excluded **only if** not used for dwelling purposes (ZR 12-10) | Excluded |
| Accessory parking | Excluded **only if** within the ZR 12-10 parking limits; otherwise counts | Excluded |
| Balconies (private) | Excluded **only if** <=67% of the perimeter is enclosed (ZR 12-10); otherwise counts | Excluded |
| Energy exclusion (5% of floor area) | Excluded **only if** a fully-electrified / ultra-low-energy building (ZR 12-10); not limited to non-apartment space | Not applicable (not a physical component) |

An example that does **not** show a condition **counts** the space. Because each component
appears once and each total is built by **inclusion**, a space zoning has already excluded
is never subtracted again.

---

## 3. The method: two separate calculations from one schedule, then reconcile

Following the owner's correction (R430-R432): do **not** reach apartment area by subtracting
walls and shafts from zoning floor area (that risks deducting, a second time, space zoning
already excluded - R431). Instead, from the one schedule:

1. **Residential zoning floor area** = the measured physical residential space **minus the
   applicable zoning exclusions** (each taken only when its condition is shown).
2. **Total HPD dwelling-unit area** = the **same** measured physical space **minus
   everything excluded under HPD's measurement rules** (walls, chases, all non-unit space).
3. **Reconcile**: account for every square foot of the difference, component by component.
   A component counts for one total, the other, both, or neither; the reconciliation lists
   exactly the components whose two treatments differ, so **nothing is deducted twice**.

No generic gross-to-net loss percentage is applied to zoning floor area (R388, R397). The
measured physical space comes from a proposed building **layout**, never from the maximum
floor area the law allows (R435).

---

## 4. The estimate's ratio

The ratio the apartment estimate would use is, and is only:

> ratio = **total HPD-measured dwelling-unit area** / **residential zoning floor area**.

The denominator is the residential zoning floor area; the numerator is the HPD-measured
dwelling-unit area; nothing else enters the ratio (R396). This is **not** the usual ratio
of apartment area to the building's physical gross area, because zoning floor area already
excludes certain physical spaces. The ratios computed in the examples below belong to those
examples only (R436).

---

## 5. The legal unit cap stays separate

The legal maximum number of dwelling units is a **separate** figure. Under ZR 23-52 it is
the maximum residential floor area divided by the dwelling-unit factor (680, where it
applies), with a fraction of three-quarters or more counting as one unit. This is a density
**ceiling**, not proof that that many apartments physically fit, and it is not derived from
the physical estimate (and the physical estimate is not derived from it) - R392, R404. The
cap's worked values live in the R6B reference cases (`docs/reference-cases/R6B/`). Each
example below shows its legal cap as a distinct number from its measured
areas.

---

## 6. Mixed-use buildings

For a mixed-use proposal, the estimate uses the **residential portion's** zoning floor
area, including any counted residential circulation and support space - not the whole
building's and not a shop floor's (R407, R437). A shop floor is not added to a residential
allowance without checking the combined-FAR and shared-space rules; how shared stairs and
lifts are allocated between the portions is itself an open point.

---

## 7. The worked examples - what they show and do not show

Three made-up, deliberately simple layouts (not real properties, not detailed or
permit-ready designs) are provided under `examples/`. Each states every dimension, gives one
area schedule, works out both areas separately, reconciles them line by line, and shows its
legal cap as a separate figure. A stdlib test recomputes every area and every reconciliation
line with exact decimal arithmetic.

| Example | Mixed use | Residential zoning floor area | Total HPD dwelling-unit area | Ratio (this example only) |
|---|---|---|---|---|
| `example-a-standard-residential` | no | 8,000 sq ft | 6,032 sq ft | 0.7540 |
| `example-b-allowances-conditions-shown` | no | 11,291 sq ft | 6,800 sq ft | 0.6022 |
| `example-c-mixed-use` | yes | 6,920 sq ft | 4,620 sq ft | 0.6676 |

**What the examples show.** The two calculations reconcile and nothing is deducted twice;
conditional allowances are taken only when their condition is shown (and counted when it is
not); spaces already out of zoning (cellar, mechanical room) are not deducted again; and the
mixed-use example uses the residential portion only.

**What they do not show.** They do **not** establish a typical ratio. The three ratios
differ (0.7540, 0.6022, 0.6676) precisely because each depends on its own made-up layout.
Correct arithmetic is **not** support for an assumption: 700 sq ft, 25 percent, 10 ft and
15 ft remain unapproved assumptions, and these examples validate none of them. Example A's
ratio happening to land near 75 percent proves nothing about any 75 percent ratio.

---

## 8. Open points for the owner (plain words; each with a recommendation and its basis)

Nothing below is decided. Each point names what is not settled, a recommendation, and its
basis.

1. **The apartment-area ratio is unvalidated.** *Recommendation:* carry the ratio as an
   editable assumption shown to the user, not a fixed 75 percent. *Basis:* neither the HPD
   material nor the HCR ceiling establishes a ratio (R398); the examples' ratios are
   example-specific (R436).

2. **The average apartment size is unvalidated.** *Recommendation:* carry 700 sq ft as an
   explicitly chosen historical reference, editable, clearly labelled "not an HPD-measured,
   R6B-specific average". *Basis:* the RentCafe figures are one dataset's benchmarks with an
   unspecified measuring convention (R399, R419).

3. **What a user must see and be able to change.** *Recommendation:* expose the ratio, the
   average unit size, the unit mix, the ground-floor height and the residential floor
   height as visible, editable assumptions, each with its basis and uncertainty.
   *Basis:* the owner requires design assumptions to be visible and editable, and no default
   approved (R359, R361).

4. **What stays "not known" without a layout.** *Recommendation:* without a proposed
   layout, report the physical apartment count as **not known** (the ratio and average size
   have no layout to act on); show only the legal cap, labelled as a ceiling. *Basis:* the
   measured physical space must come from a layout (R435); a missing fact stays not known.

5. **The exact base for the amenity 5 percent.** *Recommendation:* treat "five percent of
   the residential floor area" as needing a defined base before it is relied on; in the
   examples the cap did not bind, so no base was assumed. *Basis:* "not sure" which figure
   the statute's "residential floor area" denotes here; it is a legal-interpretation point.

6. **Shared-space allocation in mixed-use.** *Recommendation:* decide how shared stairs,
   lifts and lobby are split between the residential and commercial portions before a
   mixed-use estimate is relied on. *Basis:* ZR 23-23 exempts residential circulation under
   conditions; the split affects the residential zoning floor area (R407).

7. **Which ZR 12-10 exclusions to model.** *Recommendation:* decide whether the energy
   (5 percent) and qualifying-exterior-wall exclusions are modelled or left as conditions a
   user confirms. *Basis:* these are real exclusions, "not limited to non-apartment space",
   that would raise the ratio if taken (R403, R431).

8. **What the estimator would need before it is built.** *Recommendation:* build the
   estimator only after the owner settles points 1-7; it would need a layout (or an
   explicit layout assumption), the editable ratio and average size, and it must keep the
   physical estimate separate from the legal cap. *Basis:* resolve the measurement basis
   before implementing the estimator (R387, R428).

**How changing an assumption would change an estimated count (direction only, no number
computed here).** A larger assumed average apartment size would lower an estimated count; a
higher assumed ratio would raise the HPD-measured dwelling-unit area and so raise an
estimated count; a taller ground floor or taller residential floors would, at a fixed
height limit, reduce the number of floors and so the floor area a layout could hold. These
are directions, not an estimate; no count is computed in this record.

---

## 9. Sources

- ZR law captures under `docs/research/zr-snapshots/v1/`, each pinned by its content
  digest: `zr-12-10-floor-area`, `zr-12-10-qualifying-exterior-wall-thickness`,
  `zr-23-23`, `zr-23-231`, `zr-23-232`, `zr-23-233`, `zr-23-234`, `zr-23-52`.
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION and
  APPLICABILITY, read 2026-10-07 at the official HPD site (URL, sha256 and date above).
- The legal cap's worked values: `docs/reference-cases/R6B/`.
- Where the program holds its editable starting values today (read only, not changed by
  this record): `services/api/app/scenario/three_answers/`.
- Leads only, not sources of record: `docs/RESEARCH_REQUESTS.md` (RQ-006 to RQ-008) and
  `docs/research/helper-research/`.

Owner directives behind this record: D-090 R357-R359, R387-R389, R392, R396, R397, R407,
R413, R428, R430-R437.
