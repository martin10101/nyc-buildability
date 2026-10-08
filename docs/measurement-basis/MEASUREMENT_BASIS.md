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

### 1d. The amenity base, and the two exclusions with specific eligibility

**The amenity 5 percent names its base (R514).** ZR 23-231 states its base in its own words:

> "Floor space in a building allocated to residential amenities may be exempted from the
> definition of floor area, in an amount not to exceed five percent of the residential floor
> area of the building."

So the base is **the residential floor area of the building** - not a figure to be chosen.
The same section covers only eligible amenity space **actually provided and accessible to
residents** ("Amenities provided pursuant to this Section shall be accessible to the
residents of the building"), and it **excludes circulation** ("amenity space shall not
include floor space for circulation through the building, including, corridors or vertical
circulation spaces"). It is therefore **never** an automatic 5 percent added to apartment
space: it applies only to amenity floor space that is provided and is not circulation.
Source: capture `zr-23-231`, content digest
`81eb95e85b333eb86a0fc55413c78567d0b72d7ba9656041f77457f2263b49d6`. A remaining doubt about
the **order** of the calculation (the cap is a percentage of the residential floor area it
helps determine) is a **question of law** (section 8), not an owner's preference, and the
examples do not rely on it because in each the cap does not bind.

**The exterior-wall exclusion is not a deduction for a new building's ordinary walls
(R516).** ZR 12-10's "qualifying exterior wall thickness" is a defined term that applies to
wall thickness **added to a building existing on December 6, 2023**:

> "Qualifying exterior wall thickness" shall refer to the floor space occupied by exterior
> wall thickness added to a building existing on December 6, 2023, where: (1) for
> over-cladding projects: ...; or (2) for re-cladding projects: ...

Source: capture `zr-12-10-qualifying-exterior-wall-thickness`, content digest
`119324c8b82348cd82b354565a36468bb60e5f3680d19143f7bccfb4d16bc7bf`. It principally concerns
over-cladding and re-cladding of existing-building walls and grandfathered walls; it is
**not** a licence to subtract the ordinary exterior walls of a new building. Every worked
example therefore **counts** the full exterior wall thickness under zoning.

**The energy exclusion's eligibility is not captured yet (R516).** ZR 12-10 excludes:

> "floor space within a fully electrified building or an ultra low energy building, of an
> amount equivalent to five percent of the floor area"

(capture `zr-12-10-floor-area`, digest
`e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`). The two defined terms
this rests on - **"fully electrified building"** and **"ultra low energy building"** - are
**not captured yet** (M4-T034 captures them); their conditions (which route concerns
buildings existing on December 6, 2023, and which performance and professional-verification
requirements a new building must meet) are not read here. So the energy exclusion's
**eligibility is withheld and no example takes it**. A user's statement that a building
qualifies would support only a **conditional** result; it never establishes eligibility.
There is **no general "confirm it applies" switch** for the energy, wall or amenity
provisions anywhere in this record.

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

## 4. The estimate's formula, in words, and its ratio

**The formula (stated once, in words).** The estimated number of apartments is the
**proposed building's residential zoning floor area**, times an **assumed apartment-area
ratio**, divided by an **assumed apartment size measured as HPD measures it**:

> estimated apartments = (proposed building's residential zoning floor area x assumed
> apartment-area ratio) / assumed HPD-measured apartment size.

The estimate starts from the **proposed building's** residential zoning floor area - the
floor area a real layout or massing can accommodate once setbacks, yards and the building's
shape are taken into account - **never** from the "allowed" or maximum permitted floor area
(R435, R509). The **maximum permitted floor area is a separate figure**, a limit to check
the proposal against, and it is never the area the estimate starts from. Where a detailed
layout already measures the apartments themselves, that measured dwelling-unit area is used
**directly**, in place of floor area times the ratio. **No count is computed in this
record.**

**The ratio.** The apartment-area ratio the formula uses is, and is only:

> ratio = **total HPD-measured dwelling-unit area** / **residential zoning floor area**.

The denominator is the residential zoning floor area; the numerator is the HPD-measured
dwelling-unit area; nothing else enters the ratio (R396). This is **not** the usual ratio
of apartment area to the building's physical gross area, because zoning floor area already
excludes certain physical spaces. The ratios computed in the examples below belong to those
examples only (R436).

**The range is not established here (R512).** The worked examples establish **no** realistic
range. The three example ratios differ precisely because each depends on its own made-up
layout; three made-up examples cannot establish a typical figure. If the owner adopts a
0.60 to 0.75 band, it is a **chosen sensitivity range, labelled unvalidated** - a span to
show the user how sensitive a count is to the assumption, not a measured or expected value.
No sentence in this record calls 0.60 to 0.75 realistic, expected or validated, and no
sentence starts the estimate from the allowed or permitted floor area.

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

## 6. Mixed-use buildings, and shared floor area as a required step

For a mixed-use proposal, the estimate uses the **residential portion's** zoning floor
area, including any counted residential circulation and support space - not the whole
building's and not a shop floor's (R407, R437).

**Shared floor area is a required calculation, not a switch and not an optional allowance
(R513).** Where a building has floor area shared by more than one use, ZR 23-20 requires
that shared portion to be attributed to each use in proportion to each use's share of the
building's floor area. Quoted word for word from the capture:

> "Where floor area in a building is shared by multiple uses, the floor area for such shared
> portion shall be attributed to each use proportionately, based on the percentage each use
> occupies of the total floor area of the zoning lot, less any shared floor area."

Source: capture `zr-23-20`
(`docs/research/zr-snapshots/v1/zr-23-20.snapshot.json`), content digest
`0685a2e4e7002830a1c007dea23ac68c5c441f1a32eeb2e37b78000c5765d7cc`, official page
`https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20` (last amended
12/5/2024). In plain words: the shared floor area is split between the uses by each use's
percentage of the total floor area of the zoning lot, after the shared floor area is taken
out of that total. This attribution is **always** performed when floor area is shared; it is
never offered as a choice or a "confirm it applies" switch. It does **not** necessarily
increase the residential figure. Where the areas the attribution needs are missing, the
result that depends on it stays **"not known"** or explicitly conditional.

**What is not settled.** How a mixed building in a Commercial District then **combines** its
residential and commercial floor areas - the mixed-building floor-area rules the reviewer
names as ZR 35-31 - is **not captured yet** (another task of this wave, M4-T034, captures
it). That text is not read here, so how the attributed shared floor area feeds the
residential figure for a commercial-district mixed building is **withheld** until the text
is captured and read. (The ZR 12-10 definition of a "mixed building" **is** captured:
"A 'mixed building' is a building in a Commercial District used partly for residential use
and partly for community facility or commercial use" - capture `zr-12-10-mixed-building`,
digest `6eb9a38952df680333bf54add4cd40a9428e338c1177e1dfe7ee35f35c9727e0`.)

**Example C shows the step.** The mixed-use worked example marks every component as exclusive
to one use (residential or commercial) or **shared**, and carries the ZR 23-20 attribution as
a line of its reconciliation. It has one small shared component (a 120 sq ft utility room);
the attribution is applied exactly as the captured sentence words it, and its effect on the
residential figure is labelled **conditional** on the mixed-building text not yet read, so
the example's ratio uses the residential **exclusive** floor area only.

---

## 7. The worked examples - what they show and do not show

Three made-up, deliberately simple layouts (not real properties, not detailed or
permit-ready designs) are provided under `examples/`. Each states every dimension **and every
floor's outside outline**, gives one area schedule, works out both areas separately,
reconciles them line by line, and shows its legal cap as a separate figure. A stdlib test
recomputes every area and every reconciliation line with exact decimal arithmetic **and
proves, floor by floor, that every floor fits**: on each floor the components - the exterior
wall ring among them - add up to exactly that floor's stated outside outline.

| Example | Mixed use | Residential zoning floor area | Total HPD dwelling-unit area | Ratio (this example only) |
|---|---|---|---|---|
| `example-a-standard-residential` | no | 8,000 sq ft | 6,032 sq ft | 0.7540 |
| `example-b-allowances-conditions-shown` | no | 12,001 sq ft | 7,780 sq ft | 0.6483 |
| `example-c-mixed-use` | yes | 10,428 sq ft (residential exclusive) | 7,120 sq ft | 0.6828 |

**Examples B and C were rebuilt; two ratios were withdrawn (R510, R511).** The owner's
reviewer found that the earlier Example C described a building that did not fit - 1,743 sq ft
of components on an upper floor whose stated outline was 1,260 sq ft, the apartment rooms
alone filling the inside outline - while its arithmetic still reconciled, and that Example B
stated no floor outline at all. Both examples were rebuilt so that every floor has a stated
outside outline and the components on each floor add up to it exactly. The ratios change as a
consequence: **the earlier Example B ratio 0.6022 and the earlier Example C ratio 0.6676 are
withdrawn**; nothing is replaced silently (each example's change log names the withdrawn
figure and why). The new example ratios are 0.6483 (B) and 0.6828 (C).

**What the examples show.** Every floor fits; the two calculations reconcile and nothing is
deducted twice; conditional allowances are taken only when their condition is shown (and
counted when it is not); spaces already out of zoning (cellar, mechanical room) are not
deducted again; the mixed-use example uses the residential portion only and marks every
component exclusive or shared, carrying the ZR 23-20 attribution as a reconciliation line.

**What they do not show.** They do **not** establish a typical ratio. The three ratios
differ (0.7540, 0.6483, 0.6828) precisely because each depends on its own made-up layout.
Correct arithmetic is **not** support for an assumption: 700 sq ft, 25 percent, 10 ft and
15 ft remain unapproved assumptions, and these examples validate none of them. Example A's
ratio happening to land near 75 percent proves nothing about any 75 percent ratio.

---

## 8. Open points for the owner - the owner's choices, and the questions of law

Nothing below is decided. The open points are now kept in **two separate lists**. The first
holds only **design assumptions and what is displayed** - the owner's own choices. The second
holds **questions of law**, which are settled by capturing and reading the official text, not
by preference (R515): a question of what the law says is never put to the owner as a
preference.

### 8a. Choices for the owner (design assumptions and what is displayed)

Each of these is a design assumption or a display choice. The owner's reviewer gave a
recommendation on each on 2026-10-07; the recommendation is noted, but **nothing here is
decided until the owner says so**. No starting value is approved by this record.

1. **The apartment-area ratio.** One figure, or a low and a high carried as a **sensitivity
   range labelled unvalidated** - never a validated or expected range. *Recommended by the
   owner's reviewer on 2026-10-07 (permit 0.60 to 0.75 as an editable sensitivity assumption,
   not a validated expected range); NOT decided until the owner says so.* The ratio stays an
   editable assumption shown to the user, never a fixed 75 percent (R398, R436).

2. **The average apartment size (700 sq ft).** Carried as an explicitly chosen starting
   assumption, editable, measured on the HPD basis and labelled "not an HPD-measured,
   R6B-specific average". *Recommended by the owner's reviewer on 2026-10-07 (reasonable as a
   chosen starting assumption, explicitly measured on the HPD basis); NOT decided until the
   owner says so.* The RentCafe figures are one dataset's benchmarks with an unspecified
   measuring convention (R399, R419).

3. **The floor heights (10 ft residential, 15 ft ground).** Carried as editable starting
   assumptions, subject to the actual building envelope. *Recommended by the owner's reviewer
   on 2026-10-07 (reasonable editable starting assumptions, subject to the actual building
   envelope); NOT decided until the owner says so.* These remain unapproved assumptions.

4. **What stays "not known", and what the result is called.** Without a proposed shape and
   floors, report the physical apartment count as **not known** (the ratio and average size
   have no layout to act on); show only the legal cap, labelled as a ceiling. Once an option
   has a shape and floors, call the result a **preliminary capacity estimate**. *Recommended
   by the owner's reviewer on 2026-10-07 (yes - and call it a preliminary capacity estimate
   even then); NOT decided until the owner says so.* The measured physical space must come
   from a layout (R435); a missing fact stays not known.

5. **What a user must see and be able to change.** Expose the ratio, the average unit size,
   the unit mix and the floor heights as visible, editable assumptions, each with its basis
   and uncertainty. *Recommended by the owner's reviewer on 2026-10-07 (consistent with the
   choices above); NOT decided until the owner says so.* The owner requires design
   assumptions to be visible and editable, and no default approved (R359, R361).

### 8b. Questions of law (settled by capturing and reading the text, never by preference)

Each names what is captured, what is not, and says "not sure" where the captured text leaves
doubt. None is put to the owner as a preference (R515).

1. **The order of the amenity 5 percent calculation.** The **base** is settled: ZR 23-231
   names it "the residential floor area of the building" (section 1d; capture `zr-23-231`).
   What is **not sure** is the order when the cap actually binds (the cap is a percentage of
   the residential floor area it helps determine). The examples do not rely on it (the cap
   does not bind in any of them). Settled by reading ZR 23-231 and the related floor-area
   provisions, not by preference.

2. **How a mixed building combines its residential and commercial floor areas.** The
   proportional attribution of **shared** floor area is settled and required (ZR 23-20,
   section 6; capture `zr-23-20`). What is **not captured yet** is the mixed-building
   floor-area rule for a Commercial District (the reviewer names ZR 35-31), captured by
   M4-T034. Until it is captured and read, how the attributed shared floor area feeds the
   residential figure is **withheld**; the dependent result stays conditional or not known.

3. **The eligibility of the energy and exterior-wall exclusions.** The exterior-wall
   exclusion applies to thickness added to a building existing on December 6, 2023, not to a
   new building's ordinary walls (section 1d; capture
   `zr-12-10-qualifying-exterior-wall-thickness`), so no example takes it. The energy
   exclusion rests on two defined terms - "fully electrified building" and "ultra low energy
   building" - that are **not captured yet** (M4-T034); its eligibility is **withheld** and no
   example takes it. A user's statement supports only a conditional result; it never
   establishes eligibility. There is no general "confirm it applies" choice.

### 8c. How an assumption changes the count, and why floors are not equal (R519)

**Direction only, no number computed here.** A larger assumed average apartment size would
lower an estimated count; a higher assumed ratio would raise the HPD-measured dwelling-unit
area and so raise an estimated count; a taller ground floor or taller residential floors
would, at a fixed height limit, reduce the number of floors and so the floor area a layout
could hold. These are directions, not an estimate; no count is computed in this record.

**Floors above the maximum base height are set back, so they are smaller.** A count of floors
times one floorplate is therefore an **assumption**, and is labelled as one. For R6B the
captured height table (ZR 23-432, capture `zr-23-432`, digest
`9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`, structured `table` field,
R6B row) gives a **minimum base height of 30 ft, a maximum base height of 45 ft, and a maximum
building height of 55 ft** for standard residences (45 ft base and 65 ft building for
qualifying affordable or qualifying senior housing). ZR 23-432's operative text requires a
setback above the base height:

> "For portions of a building street wall that exceed the maximum base height, a setback shall
> be provided at a height not lower than the minimum base height or higher than the maximum
> base height in accordance with Section 23-433."

The setback depth is given by ZR 23-433 (capture `zr-23-433`, digest
`4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`):

> "a setback with a depth of at least 10 feet shall be provided from any street wall fronting
> on a wide street, and a setback with a depth of at least 15 feet shall be provided from any
> street wall fronting on a narrow street."

**The program does not work out the setback yet**, so the worked examples draw their floors as
equal floorplates for simplicity and say so; a real building would set back the floors above
the maximum base height, making the upper floors smaller than the floors below.

### 8d. What the estimator would need before it is built

Build the estimator only after the owner settles the choices in 8a and the questions of law in
8b are resolved by capture and reading. It would need a layout (or an explicit layout
assumption), the editable ratio and average size, and it must keep the physical estimate
separate from the legal cap (R387, R428).

---

## 9. Sources

- ZR law captures under `docs/research/zr-snapshots/v1/`, each pinned by its content
  digest: `zr-12-10-floor-area`, `zr-12-10-qualifying-exterior-wall-thickness`,
  `zr-12-10-mixed-building`, `zr-23-20`, `zr-23-23`, `zr-23-231`, `zr-23-232`, `zr-23-233`,
  `zr-23-234`, `zr-23-432`, `zr-23-433`, `zr-23-52`. Not captured yet (captured by M4-T034,
  not read here): the mixed-building floor-area combination rule the reviewer names as ZR
  35-31, and the ZR 12-10 definitions of "fully electrified building" and "ultra low energy
  building".
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION and
  APPLICABILITY, read 2026-10-07 at the official HPD site (URL, sha256 and date above).
- The legal cap's worked values: `docs/reference-cases/R6B/`.
- Where the program holds its editable starting values today (read only, not changed by
  this record): `services/api/app/scenario/three_answers/`.
- Leads only, not sources of record: `docs/RESEARCH_REQUESTS.md` (RQ-006 to RQ-008) and
  `docs/research/helper-research/`.

Owner directives behind this record: D-090 R357-R359, R387-R389, R392, R396, R397, R407,
R413, R428, R430-R437.
