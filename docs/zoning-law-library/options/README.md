# Zoning-law library — options (second pass, documents only)

**Unreviewed draft: discovery aid; each item links its source; nothing here is professionally
reviewed (ADR-007).** Legal readings in these files are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility
(affordable, senior, shared housing) is decided. No floor area, height, unit count or parking
count is computed for the benchmark lot (a rule's own table value cited to its section is not such
a computation).

## What this folder is

The second pass of the zoning-law library (M3-T007). The first pass (`../`) catalogued the
Zoning Resolution (ZR) sections that bear on the benchmark lot **215-16 Northern Boulevard**
(Queens; R6B with a C2-2 overlay) and listed what each of the eleven development options still
lacked. This folder turns that list into a **reading** for each remaining option family — one file
per family — so a later rules task can be contracted from it. Each file gives, per ZR section: id,
title, official URL, the last-amended date the official page shows, a **capture state** (the
snapshot file in `docs/research/zr-snapshots/v1/`, or NOT CAPTURED) and a **handled state** (the
rule file in `services/api/app/rules/rulesets/`, or NOT HANDLED); then a reading (applicable rule,
definitions, exceptions, overlay/special-district effects, measurement basis, zoning-lot scope,
the lot facts a rule would need with a possible source for each); then what is not sure, each with
its next step.

It was built from ten read-only research-helper returns (saved outside git; cited in
`research-log.md`) **plus the producer's own checks** against the snapshots, a few official pages
read this pass, and the settled R6B reference cases (`docs/reference-cases/R6B/cases/`, read by two
independent readers). The helper summaries were checked, not copied; the snapshot folder decides
capture state; the rulesets folder decides handled state.

## Limits

- **Captured ≠ handled ≠ verified.** A captured section has its verbatim text in the snapshot set;
  a handled section additionally has a rule file; neither is a professional verification. Most
  sections the remaining options need are captured but not handled, and the Article II Chapter 4
  community-facility sections and the Article II Chapter 7 affordable-housing sections are not
  captured at all.
- **Documents only.** This pass builds no code, no rule, no capture. A later rules task works its
  own independent example before any result, rule or label changes (D-093).
- **Unresolved stays unresolved.** The zoning lot is unconfirmed (NB-01); the recorded-vs-tax-map
  lot area disagrees (NB-04); the actual mapped C2-2 overlay line at the lot was not read;
  §23-154 is access-blocked. Every dependent output keeps these open.
- Public repository: pointers and at most one short quote per cited item; the owner's sample is
  cited by page number only.

## The option families

| File | Option(s) | Still-open questions (short) |
|---|---|---|
| `option-02-03-affordable-and-senior-housing.md` | 2 qualifying affordable (incl. UAP), 3 qualifying senior | §23-154 access-blocked (needed only for the UAP Offsite Option); the Article II Chapter 7 chapter (27-111/27-131/27-133/27-14/27-151) + Appendix F are NOT CAPTURED; which FAR is the dividend in option 2's unit count; the UAP income-index band |
| `option-05-shops-with-residences.md` | 5 ground-floor shops with residences | the actual mapped overlay line at the lot (76-131 default 150 ft; not read); whether C2-2 is a "select commercial overlay" (32-421); the single mixed-building rear-yard rule; 32-421/33-26/33-27/33-28/33-30/33-301 NOT CAPTURED |
| `option-06-07-community-facility.md` | 6 residences + community facility, 7 community facility alone | 24-11/24-111/24-161/24-163 and the Chapter-4 height/yard sections NOT CAPTURED; whether 24-161 or 35-31 is the operative combination citation for option 6; Use Group III use-permission detail |
| `option-08-split-lot.md` | 8 split lot with two buildings | which reading option 8 intends (two zoning lots / two buildings on one lot / a district-boundary split); whether a C2-2 overlay edge is a Chapter-7 district boundary (not settled by the text); 77-xx and the distance/court sections NOT CAPTURED |
| `option-09-shared-housing.md` | 9 shared housing (rooming units) | the shared-housing use/density sections (22-122, 23-51, 54-311) NOT CAPTURED; the modern shared-housing-suite framework is pending 2027 legislation; lawful occupancy is set outside the ZR (MDL/HMC/Building Code) |
| `option-10-parking-and-transit-zone.md` | 10 parking + transit zones, plus a parking/loading/bicycle line per option | rooming-unit vs dwelling-unit classification (gates the parking line); "Transit Zone, Inner" and 25-24/25-241 and community-facility parking 25-30+ NOT CAPTURED; whether an overlay triggers the same commercial parking as a stand-alone district |
| `option-11-combinations.md` | 11 all programs combined | whether a development may hold both affordable and senior; the full 35-31 carve-out sweep; option 11 currently reduces to the single best qualifying-housing program; inherits every open item of options 2-10 |

The benchmark lot's transit-zone membership is a recorded value: **Outer Transit Zone**
(`docs/reference-cases/R6B/cases/step-p5-worked.json#transit-zone-value`; DCP dataset `6ztr-wgff`
updated 2025-12-16 agrees) — labelled unreviewed.

## Questions for the owner (plain sentences; the orchestrator moves these into the questionnaire)

1. For option 5, should ground-floor commercial be modelled as consuming the residential FAR
   envelope (the owner's sample does this), or as a separate commercial-overlay FAR added under a
   combined cap (the program library's reading)?
2. For options 5 and 8, should the program assume the C2-2 overlay covers the whole lot (its
   default 150-ft depth exceeds the lot's 100-ft depth), or must it read the actual overlay line
   from the zoning map and handle a partial-coverage (split-lot) case?
3. For option 6, does "residences with a community facility" mean one mixed building, or separate
   residential and community-facility buildings on one zoning lot?
4. For option 8, should "split lot" mean subdividing into two independent zoning lots (the sample's
   approach), two buildings on one shared-budget zoning lot, or a zoning lot crossed by a district
   boundary — or should the program offer more than one as separate scenarios?
5. For options 9 and 10, is the sample's single-room-occupancy reading (rooms about 150 sq ft,
   shared kitchen/bath, counted as units) the intended meaning of "shared housing"; should the
   program show the zoning envelope only and mark buildability/occupancy as conditional on the
   Multiple Dwelling Law / Housing Maintenance Code / Building Code and the pending 2027
   legislation rather than report a room count; and does option 10 differ from option 9 only in
   showing the parking requirement eliminated, or in the housing programme itself?
6. For option 11, should "all programs combined" genuinely stack multiple compatible programs
   toward a stated objective (most residential floor area, most units, …), or follow the sample's
   narrower treatment (UAP alone)?
