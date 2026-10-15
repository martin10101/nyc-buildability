# Options 2 & 3 — qualifying affordable housing (incl. the Universal Affordability Preference) and qualifying senior housing

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Legal readings here are drafts tied to the cited source
text. Where the producer is not sure, it says "not sure". Nothing here is labelled Verified;
nothing here calls a result compliant, buildable, feasible, optimal or preferred. Eligibility
for an affordable-housing or senior-housing programme is a legal determination the program does
not make. No floor area, height, unit count or parking count is computed for the benchmark lot
(a rule table value cited to its section is not such a computation). Benchmark: R6B with a C2-2
overlay, 215-16 Northern Boulevard, Queens (BBL 4073340070).

Second pass of the first-pass list in `../options-sections.md` §2 and §3; built from read-only
research helper HA (saved outside git) plus the producer's own checks of the snapshots and two
official pages (see `research-log.md`).

## Sections

Capture state is read from a listing of `docs/research/zr-snapshots/v1/`; handled state from
`services/api/app/rules/rulesets/`. `[C]` = captured snapshot · `[NC]` = not captured.

| id | title | official URL | last amended (page) | capture | handled |
|---|---|---|---|---|---|
| 12-10 | Definitions — "qualifying affordable housing" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-qualifying-affordable-housing.snapshot.json | NOT HANDLED (eligibility, not computed) |
| 12-10 | Definitions — "qualifying senior housing" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-qualifying-senior-housing.snapshot.json | NOT HANDLED |
| 12-10 | Definitions — "affordable independent residence for seniors" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-affordable-independent-residence-for-seniors.snapshot.json | NOT HANDLED |
| 12-10 | Definitions — "long-term care facility" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-long-term-care-facility.snapshot.json | NOT HANDLED |
| 23-22 | Floor Area Regulations for R6 Through R12 Districts | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22 | 12/5/2024 | zr-23-22.snapshot.json | r6_r12_residential_far.rule.json (1st col 2.00) + r6b_qualifying_housing_far.rule.json (2nd col 2.40) |
| 23-432 | Height and setback requirements | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432 | 12/5/2024 | zr-23-432.snapshot.json | r6b_height.rule.json |
| 23-433 | Setbacks (above the maximum base height) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433 | 12/5/2024 | zr-23-433.snapshot.json | NOT HANDLED |
| 23-52 | Maximum Number of Dwelling Units | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52 | 12/5/2024 | zr-23-52.snapshot.json | r6b_dwelling_units.rule.json |
| 11-25 | Suffix inheritance (reaches R6B from R6) | https://zoningresolution.planning.nyc.gov/article-i/chapter-1/11-25 | per rule | zr-11-25.snapshot.json | cited by r6b_dwelling_units.rule.json |
| 23-154 | (title not readable) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-154 | UNKNOWN — access blocked (HTTP 403) | NOT CAPTURED | NOT HANDLED |
| 27-111 | General definitions (UAP / MIH / regulatory agreement) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-111 | 12/5/2024 | zr-27-111.snapshot.json | NOT HANDLED |
| 27-131 | Mandatory Inclusionary Housing (shares / income bands) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-131 | 12/5/2024 | zr-27-131.snapshot.json | NOT HANDLED |
| 27-133 | Mandatory Inclusionary Housing areas | https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-133 | 12/5/2024 | zr-27-133.snapshot.json | NOT HANDLED |
| 27-14 | Methods of Providing Affordable Housing | https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-14 | 12/5/2024 | zr-27-14.snapshot.json | NOT HANDLED |
| 27-151 | Additional requirements for MIH and UAP developments | https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-151 | 12/5/2024 | zr-27-151.snapshot.json | NOT HANDLED |

**Correction carried from the first pass (checked by the producer).** `options-sections.md` §2
and the master list treat **23-154** as "the UAP section". That is not how the current text
reads. The producer opened §27-111 officially (WebFetch, HTTP 200, last amended 12/5/2024): it
defines "UAP development", "MIH development" and "affordable housing regulatory agreement" and
references 23-154 only for the UAP **Offsite Option** floor-area rate, while a UAP development on
its own (generating) site "utilizes the floor area regulations of Section 23-22 … or the height
and setback regulations of Section 23-432 … applicable to qualifying affordable housing." So the
substantive affordable/senior rules now live in **Article II, Chapter 7** (now captured by
M3-T008, not handled), and 23-154 is not load-bearing for the benchmark lot. 23-154 itself stayed HTTP 403 on
both WebFetch and the documented browser-UA GET fallback (see `research-log.md`); its text is not
read. The first-pass file `../options-sections.md` is editable by this pass and its §2 note is
updated; the non-editable `benchmark-r6b-sections.json` is addressed under "Findings outside my
files" in the producer report.

## Reading (unreviewed draft)

**Applicable rule.** Relative to standard residences (option 1), options 2 and 3 change only two
R6B figures, both captured and handled:
- **Floor area (23-22).** The R6B row carries a standard column and a separate column for
  "zoning lots containing qualifying affordable housing or qualifying senior housing". The
  snapshot's R6B row is standard **2.00**, qualifying **2.40**, with **no footnote** on the R6B
  row — so 2.40 is flat and does not depend on street width (the footnote-driven within-100-ft
  rows are higher-density districts, not R6B). Checked by the producer against
  `zr-23-22.snapshot.json`.
- **Height/setback (23-432).** R6B row (checked against `zr-23-432.snapshot.json`): minimum base
  30 ft; standard max base 45 ft / max building 55 ft; **qualifying** max base **45 ft** / max
  building **65 ft**; no footnote on the R6B row. A setback above the max base height follows
  23-433 (captured, not handled).

**Dwelling units (23-52).** Option 2 (affordable): the 680 dwelling-unit factor still applies
(affordable housing is not among the 23-52(a) no-factor branches); whether the dividend is the
standard 2.00 or qualifying 2.40 floor area is a reviewer question the handled rule flags, not a
lookup — **not sure**, kept open. Option 3 (senior): 23-52(a)(2) gives qualifying senior housing
**no** applicable dwelling-unit factor, so the 680 cap does not bind it (checked against
`zr-23-52.snapshot.json`, which lists "(2) #qualifying senior housing#" under the no-factor
branch). Eligibility for either programme is not decided here.

**Definitions relied on (12-10).** "qualifying affordable housing" (captured) = MIH developments
in MIH areas; UAP developments; or buildings under an affordable housing regulatory agreement —
its sub-terms are defined in §27-111 (captured). "qualifying senior housing" (captured) =
"affordable independent residence for seniors" or "long-term care facility" — both sub-terms are
§12-10 general definitions (captured). Also: "floor area", "floor area ratio", "zoning lot",
"dwelling unit".

**Exceptions / carve-outs.** UAP is by definition **outside** a Mandatory Inclusionary Housing
area, so inside an MIH area the MIH options of §27-131 apply (mandatory shares/income bands) and
UAP is not the route; outside an MIH area UAP is available. Senior housing (affordable
independent residences for seniors) needs an affordable housing regulatory agreement; a long-term
care facility additionally needs NYS Department of Health licensure. These are conditions, not a
decision.

**Overlay and special-district effects.** The C2-2 overlay does **not** raise the residential
FAR (2.00/2.40) or the 45/65-ft R6B heights — those are the underlying R6B figures; the overlay
adds commercial floor area only for commercial/community-facility use (options 5/6). Whether a
mixed building under the overlay changes the R6B height/setback numbers via 35-632 is not handled
(see option 5; evidence record NB-06). Special density areas (12-10) are only the Manhattan Core
and the Special Downtown Brooklyn District; the Queens benchmark is in neither (evidence record
NB-05), so the 23-52(a)(1) no-factor branch does not apply here.

**Measurement basis.** FAR = zoning-lot area (sq ft) × ratio (dimensionless); R6B qualifying FAR
2.40. Heights in feet from the base plane / curb level. Dwelling units = maximum residential
floor area on the zoning lot / 680 (affordable); no factor (senior). Affordable floor area for a
UAP site is measured from DOB-approved plans "by methods specified in the [HPD] guidelines"
(§27-14, captured).

**Zoning-lot scope.** FAR and the dwelling-unit limit are per **zoning lot**; heights are per
building; "qualifying affordable housing / senior housing", "UAP development" and "MIH
development" are properties of the development/building. A tax lot is not a zoning lot; the
benchmark zoning lot is unconfirmed (NB-01), which keeps every FAR / floor-area / unit figure
conditional.

**Lot and applicant facts the program would need (each with a possible official source).**
- Zoning district R6B — DCP zoning map / MapPLUTO ZoneDist1 (have: R6B).
- Zoning-lot area — recorded lot area (deed / tax map) plus a zoning-lot determination; MapPLUTO
  LotArea is a benchmark only (NB-01, NB-04).
- Mandatory Inclusionary Housing-area membership (gates UAP vs MIH) — ZR Appendix F + §27-133 +
  DCP Zoning Map / ZoLa. MapPLUTO does **not** flag MIH-area membership.
- Special density area / special purpose district — MapPLUTO SPDist1 (null here) + ZR maps
  (NB-05: not a special density area).
- Which qualifying pathway, the affordable share and income band, rental vs homeownership
  (§27-161/§27-162), the executed regulatory agreement, the HPD permit notice to DOB — HPD; for a
  long-term care facility, NYS Department of Health. These are applicant facts; eligibility is not
  decided here.

## What the owner's sample shows (pointer only)

Sample scenario 1 "UAP max-development" (option 2, pp.16-22): a max-development residential
building driven by the Universal Affordability Preference FAR bonus with a City-of-Yes height
bonus, a share of floor area set aside as affordable. Sample scenario 2 "AIRS senior" (option 3,
pp.23-29): an entirely-affordable independent-residences-for-seniors building on the senior bonus
FAR, presented as mutually exclusive with any market-rate program. The sample cites no UAP section
number (only ZR 12-10 and 23-232 boilerplate, plus 23-22/23-432 on the senior sheet). Its premises
(UAP eligibility, a fixed affordable share/AMI, senior AIRS eligibility) are inputs / legal
determinations the program does not make.

## What is not sure (each with its next step)

1. **Text and current title of §23-154** — access blocked (HTTP 403 on WebFetch and on the
   documented browser-UA GET fallback, 2026-10-14; the first pass hit the same block). Next step:
   try the print/PDF node channel, else keep a durable "access blocked" note. Needed only for the
   UAP Offsite Option, not for the benchmark lot.
2. **Dividend for option 2's unit count** — standard 2.00 or qualifying 2.40 floor area in the
   23-52 calculation. The handled rule flags this for review. Next step: a reviewer/legal reading,
   not a lookup; keep unresolved.
3. **The Article II Chapter 7 chapter (27-111, 27-131, 27-133, 27-14, 27-151) and Appendix F** are
   now CAPTURED (M3-T008; `zr-27-111/131/133/14/151`, `zr-appendix-f`) but NOT HANDLED. Next step: a
   rule may now cite §27-131 (MIH shares / income) and §27-133 + Appendix F (MIH-area membership)
   before stating option 2's share or gate.
4. **Exact UAP income-index band** — not co-located with "UAP development"; set in §27-14 /
   §27-161 / §27-162 plus HPD guidelines. Next step: read those pages in full.
5. **Whether §35-632 changes the R6B envelope numbers for a mixed building under the overlay** —
   not sure (NB-06; see option 5). Next step: read §35-632 officially (its R6B effect).
