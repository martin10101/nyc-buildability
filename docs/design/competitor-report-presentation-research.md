<!-- Researcher return preserved VERBATIM by the orchestrator (report-preservation rule;
transport entity-decoding applied: &amp; -> &). Author: independent general-purpose research
subagent (web research pass 1 of 2: product/report presentation), returned 2026-09-12 (UTC).
Companion pass 2 (practitioner sentiment: Reddit/forums/reviews) is appended below when it
returns. Purpose: design input for the upcoming architect-facing UI/report phase (owner request
2026-09-12); pairs with docs/design/address-entry-confirm-design-spec.md and the owner's Codex
(Astra) research pass, to be captured separately when supplied. -->

# Competitor Presentation Research: Zoning/Feasibility Products
**All sources retrieved 2026-09-12.** Method note: I fetched product, pricing, docs, and tour pages directly; read two primary PDFs (an UrbanForm conference deck with real app screenshots; a CUNY CityTech NYC zoning-analysis teaching deck showing the official DOB ZD1 format); plus one archived copy of a Fontan Architecture article. Items I could NOT verify are flagged per product.

---

## 1. TestFit (testfit.io) — generative feasibility

**What the output looks like.** Hero = an editable, AI-generated site plan: homepage headline "Automate Site Plans. Accelerate Decisions," with an interactive 3D site-planning visual and demo video; the pitch is "an AI-generated plan you can edit down to the last parking stall" (https://www.testfit.io/, 2026-09-12). The working output is a fully resolved 2D/3D site plan with live counts — unit counts, parking count, FAR, coverage, NRSF/efficiency, yield-on-cost, cut/fill volumes (https://www.testfit.io/product/site-solver). It is a design canvas first, dashboard second: "Adjust any input and the model updates in real time… sit with a client or an elected official and explore options live" (illustrarch review, https://illustrarch.com/articles/design-softwares/74579-testfit-review.html).

**Hierarchy.** Real-time co-editing loop: parameters in (setbacks, parking ratios, FAR targets, unit mix, typology) → instant plan + metrics out; scheme comparison side-by-side ("Compare each scheme with real-time insights"); a "Deal Pipeline… all your deals on OneMap" portfolio layer above individual sites; unlimited min/max filters (site-solver page). No visible citation/source layer for zoning rules — zoning is an input the user sets, "zoning compliance validation (setbacks, FAR, density)" is claimed but not source-linked (search results, testfit.io pages).

**Visual language.** 2D & 3D site plans and massing, 2D/3D topography with flood/wetland overlays, parking layouts drawn stall-by-stall. Numbers ride on the geometry rather than living in a separate report.

**Report/export.** "Polished PDF feasibility reports with models and data always in sync"; annotate with "sticky notes, markers, text, and images"; custom branded report templates that "stay connected to live TestFit models, your reports automatically pull in up-to-date visuals and data" (https://www.testfit.io/blog/testfit-web-1-26-0-custom-report-templates-for-better-decisions). Previously an "out-of-the-box 3-page report template." Exports: DXF, SKP, glTF, CSV, PDF; Revit add-in. *Not verified: exact page-by-page report contents.*

**Pricing (2026-09-12, testfit.io/pricing).** Parking Solver $195/mo (+add-ons: Site Intelligence +$150/mo, Pro Forma +$170/mo, MCP +$100/mo); Site Solver "Starting at $15,000/year"; Site Solver Portfolio "Starting at $20,000/year" (SSO, volume). Notably "unlimited users" on the entry plan — priced per firm/deal, not per seat.

**Targets.** Developers first, architects second (developers/architects/contractors/brokers role pages). Shows in the presentation: yield-on-cost and deal language everywhere; the report exists to drive "go or no-go decisions."

---

## 2. UrbanForm (urbanform.us) — parcel zoning data/reports

**What the output looks like** (best evidence: their own conference deck with real screenshots — https://theoregonsummit.com/wp-content/uploads/B3_Truong-Copy-of-UrbanForm_Coos_250409-2.pdf, pages read directly). Split screen: left = Mapbox parcel map (toggles: "Satellite View", "MaxBuild 3D"); right = report panel under an address search box. The right rail is a fixed section index: **SUMMARY, IDENTIFIERS, EXISTING STRUCTURES, ZONING, LOT INFO, USES, FAR, HEIGHT, COVERAGE, SETBACKS, UNITS, MASSING, OTHER**, plus INFO/FILTER tabs and persistent **SOURCES / HELP / ACCOUNT** buttons and a yellow **"DOWNLOAD FULL REPORT"** button pinned bottom-right. The "MaxBuild 3D" toggle renders a citywide extruded max-envelope map colored by zone family (their deck's cover image is exactly this: Portland with green/pink/yellow/orange extrusions).

**Hierarchy — the standout pattern.** Every fact is an atomic 4-line record: **Regulation → Value → Comment → Source**. Screenshot example (Newberg, OR parcel): "Regulation: Quadplex or cottage cluster minimums / Value: 8 units / Comment: *This lot meets the minimum lot area of 7,000 SF… per the table in 15.405.010.A.1… This lot is 15585 square feet.* / Source: 15.405.010.A.1" — the source is a hyperlink to the code section, and the comment does the lot-specific reasoning in plain English with a "See less" collapse. Selected parcel is outlined cyan on a 2D lot view with lot-line dimensions. The architects page confirms: "zoning reports tied directly to their official code citations" (https://www.urbanform.us/architects).

**Visual language.** 2D parcel map + optional citywide 3D max-build extrusions; no per-scheme massing design. Color = zone family. Data-overload control = the fixed section rail + per-fact collapse.

**Report/export.** PDF "Full Report": "detailed site-specific zoning information in PDF format, zoning explanations with calculations and source links, static/vector maps, FAR/height/setback details" (pricing page). Deck testimonial: "One UrbanForm report instantly does what I used to spend half a day compiling for a meeting" — Staff Planner.

**Pricing (2026-09-12, urbanform.us/pricing).** Free tier ($0, all public zoning data in the interface); **Single Report $197 one-time** (PDF); Pro (contact; for architects/RE professionals; free for students/faculty); Enterprise (contact; unlimited PDFs, search/filter by FAR/height/lot size/build potential).

**Targets.** Architects explicitly ("start sketching within minutes"), plus developers and governments (several cities white-label it as their public zoning map — yam.urbanform.us, boardman.urbanform.us).

---

## 3. Deepblocks (deepblocks.com) — AI feasibility

**What the output looks like.** Draw a parcel/assemblage on a satellite map, pick uses, adjust market assumptions → "a 3D model and financial projection update in real-time… a visual of the project, a sense of the cost of construction and acquisition, and your expected returns" (search result citing deepblocks tutorial content). Homepage now leads with "AI STRATEGY"; Developer software shows 3D massing + financial tables (return metrics, pro forma, assumptions) + interactive dashboards recalculating on rent/cost/unit-mix changes (https://deepblocks.com/, 2026-09-12).

**Hierarchy.** Dashboard of studies → per-study 3D+financial view; the dashboard's comparison metric is **"return on cost across studies"** — a single financial number as the cross-study ranking key (https://deepblocks.com/blog/welcome-to-the-deepblocks-pro/). GIS layers (demographics, economics, crime, ownership) integrate into the same map.

**Visual language.** Satellite map + simple extruded 3D massing + financial tables. Finance-first, not geometry-first.

**Report/export.** "Export a PDF customized with your logo and brand colors or a CSV of all the financials, which can be plugged into a proforma spreadsheet" (search result on Deepblocks pages). *Not verified: PDF section order.*

**Pricing (2026-09-12, deepblocks.com/pricing).** Pivoted to deal-flow-as-a-service: AIM plans $499/mo (2 deals/mo) → $7,999/mo (32 deals/mo); Developer software "available as a stand-alone product," price on contact.

**Targets.** Developers/investors/brokers. Presentation is returns-led throughout; zoning is an invisible constraint engine, with no visible code citations.

---

## 4. Envelope / envelope.city — NYC-specific (DEFUNCT)

**Status.** envelope.city no longer serves the product — the domain's TLS cert now belongs to an unrelated German bank host (fetch attempt 2026-09-12: "Host: envelope.city… cert's altnames: DNS:client-auth.cleo.l-bank.de"). Wayback Machine could not be fetched from this environment (web.archive.org blocked for this tool) — *honest gap*. Evidence below is from a partner page, a designer's case study, and press.

**What the output looked like.** "Visualize zoning envelopes in 3D for any NYC parcel, instantly" with "full citations, footnotes, and stacking charts for comprehensive planning"; features: "3D Scenario Massing," "Assemblage Tools," "Feasibility Modeling," "Stacking Charts," site search filtering "by built %, available FAR, location analytics" (TitleVest partner page, https://www.titlevest.com/public/HTML/envelope.html). So: 3D as-of-right envelope + a stacking chart (floor-by-floor use breakdown) + cited legal basis — the closest historical analog to an NYC-accurate envelope product.

**Hierarchy/interaction.** "Intuitive search/select/test interaction paradigm"; a "flexible and extensible query builder" for spec search ("find a site that can accommodate at least 100 residential units plus ground floor retail… within 5 minutes of a subway… at least 10,000 ZFA of adjacent air rights"); loop of "build queries, contextual exploration, refine and repeat" (design case study, https://www.siqizhu.net/envelope-city/).

**Business lesson.** Pivoted "from a pure SaSS design software to a hybrid SaSS/consulting model" targeting "high-value real estate customers" (siqizhu.net) — i.e., pure self-serve NYC zoning SaaS didn't hold; by the end access was via contact form/email (TitleVest page). Pricing never publicly listed.

**Targets.** NYC developers/owners/brokers doing due diligence and site search; "legal-quality zoning analysis and architecture-quality visualization" (Medium listing via search).

---

## 5. Gridics / Zonar.City — municipal + real estate

**What the output looks like.** Map-first: "select a parcel or assemblage of parcels on a map and in seconds visualize in 3D the development allowance according to the regulations in the written code" (PR/press, prnewswire + gridics.com news pages). Current product suite (https://gridics.com/, 2026-09-12): government — CodeHUB ("integrate code text, maps, & self help tools"), MuniMap ("visualize the zoned development potential of the site in real-time 3D"), ZoneCheck ("virtualize your zoning front counter"); real estate — PropZone, Property Zoning Reports ("feasibility reports prepared by our zoning experts"), Zoning Data API ("hundreds of parcel-level zoning… data points": max buildable area, max footprint, allowable addition, height, density, setbacks).

**Hierarchy.** Parcel click → data panel of 30+ attributes (allowed uses, setbacks, overlays, density) with 3D massing of the allowance; code text linked to map in CodeHUB (cities "self-publish their zoning code changes in real-time"). PropZone adds "hundreds of filters" + proprietary "PropZone Scores" ranking redevelopment potential (https://gridics.com/propzone/).

**Report/export.** Human-expert-prepared zoning feasibility reports (contents/pricing demo-gated — *not verified*). API for data export.

**Pricing.** None public; demo/contact only (2026-09-12).

**Targets.** Municipalities (public transparency UI: plain map + click-a-parcel + 3D) and RE professionals (filters + scores). NYC relevance: ran a NYC Dept. of City Planning pilot of the 3D zoning platform (gridics.com/news).

---

## 6. Zoneomics — zoning data + report ladder

**What the output looks like.** "An Intuitive Dashboard" (search history, unlocked properties) + zoning map ("Enter an address or drop a pin"); parcel data organized into: zoning classification, Permitted Land Uses, building controls, parking, short-term-rental rules, overlays, parcel details (https://www.zoneomics.com/product/platform, 2026-09-12).

**Hierarchy — the report ladder is the product.** Four escalating deliverables (https://www.zoneomics.com/product/reports): **Zoning Brief** (automated: classification+guides, permitted uses, development controls; add-ons: use-compliance, dimensional-compliance, massing/zoning-envelope reviews) → **Summary Report** (analyst-prepared, 24h: + parking, comprehensive restrictions review, ALTA Table A/6a/6b items, applicable codes/ordinances) → **Full Report** ("golden standard," 15 working days: + compliance determination, land-use permits, Certificates of Occupancy) → **Certified Zoning Letter** from the jurisdiction. Machine speed at the bottom, human certainty at the top.

**Visual language.** Map + tables; no 3D. "ZoneCheck: Powerful Office Macros" pushes zoning data into MS Word (appraiser workflow).

**Pricing (2026-09-12, zoneomics.com/pricing + /pricing/reports).** Essentials $92/mo (1 user, 25 searches, 1 Brief, extra Briefs $65); Advanced $279/mo (150 searches, 5 Briefs, extras $55); Enterprise custom (25+ Briefs, extras $39, white-labeled reports). À-la-carte report prices not public.

**Targets.** Appraisers, lenders, title companies, law firms — shows in ALTA tables, certified letters, Word plugin. Not architects.

---

## 7. Giraffe (giraffe.build) — feasibility canvas

**What the output looks like.** Browser map canvas layering "GIS data, editable 3D massing, and spreadsheet-style feasibility"; sketch a 2D shape, "just add levels" → 3D building; "analytical feedback (area, cost, context metrics) updates in real time" (https://www.giraffe.build/architects/ + search results, 2026-09-12).

**Hierarchy.** Assumptions ("efficiency, or floor-to-floor height") + design geometry feed a calculation engine; users "define your own calculations… with an Excel-like syntax"; side-by-side scenario comparison "against your investment thesis using consistent metrics"; portfolio tracked "on a map or a kanban board" (giraffe.build pages/search). Zoning arrives as data layers — Giraffe does not adjudicate compliance and shows no code citations.

**Report/export.** "Board-ready outputs include exported structured reports, exhibits, and audit trails for capital partners"; geometry exports STL/OBJ/DXF/IFC.

**Pricing (2026-09-12).** Pricing page itself hides numbers (self-serve vs Enterprise; https://www.giraffe.build/pricing/); search results cite **US$45/user/mo Individual** and **US$1,500/user/yr Teams (up to 10)** — *secondary source (bimtoolshub/saasworthy via search), not verified on giraffe.build*.

**Targets.** Architects/urban designers and developer teams; the pitch to architects is workflow ("iterate rapidly and get metrics instantly"), the pitch to developers is investment screening.

---

## 8. ArcGIS Urban (Esri) — planning capacity

**What the output looks like.** 3D web scene of a plan area; **zoning envelopes** render as translucent volumes: "Envelopes display the maximum extent of potential buildings" from "height, setback, and skyplane restrictions on each parcel," toggled per-layer (All parcels vs planned developments), generated async with a spinner (https://doc.esri.com/en/arcgis-urban/latest/help/help-zoning-envelopes.html, 2026-09-12). Doc explicitly notes FAR/coverage mean real buildings won't fill the envelope — envelope ≠ buildable floor area.

**Hierarchy.** A **Dashboard side panel** (upper-right button) shows metric cards + charts; click a metric → "the metric chart, a description, and how the metric is calculated"; scenario switcher in header compares scenarios on identical metrics; "Explore section" breaks metrics down by space-use/buildings/parcels (https://doc.arcgis.com/en/urban/11.5/help/help-analyze-plan.htm). Metrics include GFA, dwelling units, footprint, coverage, FAR, custom compound metrics.

**Visual language.** 3D city model + envelope volumes + chart cards. Built for comparing scenarios across whole districts, not for one lot's legal analysis; no code citations.

**Report/export.** Dashboard/chart views; no property-report PDF concept found.

**Pricing (2026-09-12).** No standalone price: "included only with the Professional Plus user type" of ArcGIS Online; Creator/Professional tiers say "Not included" (https://www.esri.com/en-us/arcgis/products/arcgis-urban/buy). Effectively enterprise/municipal procurement.

**Targets.** City planning departments; presentation is aggregate (capacity, density across scenarios), not parcel-legal.

---

## 9. ZoLa — NYC's own zoning map (the free baseline)

**What the output looks like.** Full-screen web map; searching/clicking a lot opens a **left panel** with property info, "the Zoning District designation clearly listed near the top"; default layers: zoning districts, tax lots, commercial overlays, subways; toggleable: special purpose districts, IHDA, flood, historic districts, 3D buildings, zoning map amendments, aerials (ZoLa user guide via search, https://www.nyc.gov/assets/planning/download/pdf/data-maps/maps-geography/zola/zola-userguide.pdf; https://zola.planning.nyc.gov/). Deep-linkable: "Each tax lot, zoning district… lives at its own URL, and the currently selected map layers are included in the URL" (govfacts.org summary + NYCPlanning/labs-zola GitHub: `/bbl` and `/bbox` routes, autocomplete search API).

**What it does NOT do** — the gap every NYC startup fills: no FAR math, no envelope, no allowed-floor-area number, no report. It names the district and links out; the user must open the Zoning Resolution themselves.

**Pricing.** Free. **Targets.** Everyone (public); consequently zero interpretation.

---

## 10. Manual NYC zoning analysis documents (what architects produce today)

**a) Fontan Architecture articles** (archived copy read directly: https://cbmanhattan.cityofnewyork.us/cb12/wp-content/uploads/sites/2/2022/05/R8B-Zoning-NYC-.-Fontan-Architecture.pdf). Structure of the R8B explainer: district context ("high density… contextual… Quality Housing") → sibling-district list → programs (Quality Housing, community facility, commercial overlay, Inclusionary Housing) → **"R8B Zoning Regulations For Quality Housing" as a labeled value list**: "Minimum Lot width = 18 Feet… Minimum Lot Area = 1,700 Sq Ft… Corner Lot = 100% / Interior or Through Lot = 70%… FAR = 4… Density Factor 680… Base Height = 55 Minimum / 65 Maximum… Manhattan Core: = 75 feet… Interior Lot = 30 foot minimum rear yard" → **worked example on a hypothetical 50×100 lot**: footprint (rear yard → 50×70, 3,500 sf) → "Zoning Floor Area = Lot Area X FAR" → 20,000 sf → 29 units max, "6 stories tall… setback at least on the top floor" → heavy disclaimer ("zoning is complicated and I am only addressing the basics… many additional issues and variations"). Plain paragraphs + bold key:value lines; no tables, one zoning map image. Sequenced arithmetic + a concrete example is the explanatory backbone. Their definition elsewhere: "an architectural Zoning Analysis is a report on the applicable zoning codes for a given property resulting in a basic outline of what can be developed" (search snippet).

**b) The official NYC format — DOB ZD1 Zoning Diagram** (CityTech teaching deck read directly, https://openlab.citytech.cuny.edu/ar2330btech3spring14/files/2014/01/02-Zoning-Analysis-285-Jay-Street.pdf). Workflow: "Identify Block & Lot → Determine Zoning Map → Determine Size Dimension → Calculate Lot Area → Determine FAR → Calculate Total Allowable Sq Ft → Identify existing buildings & calculate their area → Subtract existing… to determine total available square footage," then consider "Zoning District, Use Group, Narrow/wide streets, Side/Front/Rear Yard requirements, Street Wall & Sky Exposure plane." Deliverable = **Zoning Sheet (Z-101): "Environs Map, Zoning Map, Site Plan, Isometric Massing, Sections, Dimensions, Scale, Calculations, legend" + Zoning Text Sheet (Z-102): "excerpts of all relevant zoning code."** The sample ZD1 sheets show the canonical quad layout: **Site Plan Diagram** (yards/setbacks dimensioned) + **Legend** + **Axonometric Diagram** (massing with "88' STREET WALL / 74' BUILDING HEIGHT") + **Section Diagram**, with *every* dimension annotated "AS PER ZR XX-XX" — a per-line citation to the Zoning Resolution section. This is the provenance standard NYC reviewers already expect.

**c) NYC official form fields** (BSA Zoning Analysis form, via search, https://www.nyc.gov/assets/bsa/downloads/pdf/forms_instructions/bsa_zoning_analysis.pdf): Site Data + Zoning Analysis with lot area/width, use groups, floor area by category (residential/CF/commercial), FAR per category, open space, lot coverage, dwelling units, heights, yards, setbacks, sky exposure plane, parking, loading — i.e., the finite canonical row-set of an NYC analysis table.

**d) Consultant tier** (Urban Cartographics, https://www.urbancartographics.com/advanced-zoning): three deliverable tiers — Massing Studies (3D + FAR/height figures), Development Rights Analyses (assemblage scenarios), Complete Zoning Analysis (site plans + schematics + 3D + calculations report); their thesis: "compelling illustrations take zoning analyses to the next level; from good to great." No public pricing.

---

# PATTERNS (recurring across the best products)

1. **Map/geometry first, numbers attached to it.** Every successful tool opens on the parcel (map or 3D), never on a table. The first interaction is always "search address / click parcel" (ZoLa, UrbanForm, Gridics, Deepblocks, TestFit, Giraffe).
2. **One hero number per audience.** Developers get a finance number (Deepblocks' "return on cost," TestFit's yield-on-cost); zoning-data tools get a capacity number (UrbanForm's "calculated maximum build areas," Gridics' "maximum buildable area"). For architects the natural hero is max buildable floor area + the envelope.
3. **Fixed, named section rail for parcel facts.** UrbanForm's SUMMARY→IDENTIFIERS→ZONING→LOT INFO→USES→FAR→HEIGHT→COVERAGE→SETBACKS→UNITS→MASSING rail; BSA form's canonical field list; Zoneomics' category tabs. A stable taxonomy beats free-form scroll — architects learn where a fact lives.
4. **Atomic fact = Value + plain-English reasoning + clickable code citation.** UrbanForm's Regulation/Value/Comment/Source rows and Envelope's "full citations, footnotes"; the manual-world equivalent is ZD1's "AS PER ZR XX-XX" on every dimension. This is the single strongest differentiator vs. black-box tools — and it matches this platform's provenance principle exactly.
5. **3D envelope as instant comprehension, table as verification.** Envelope.city, Gridics, ArcGIS Urban, UrbanForm MaxBuild 3D all pair a translucent/extruded max-volume with the numeric breakdown. Esri's docs carry the key honesty rule: envelope volume ≠ achievable floor area (FAR/coverage bind first) — say so on-screen.
6. **Live recompute + side-by-side scenarios.** TestFit ("compare each scheme with real-time insights"), ArcGIS Urban (scenario switcher, identical metric cards), Giraffe (consistent metrics across options), Deepblocks (compare across studies). Comparison is always on a fixed metric set, never free-form.
7. **The PDF report is the deliverable that gets paid for — and it mirrors the screen.** UrbanForm sells the report ($197) with "explanations with calculations and source links"; TestFit's reports "stay connected to live models"; Zoneomics' whole business is a report ladder. Report = same sections as the panel, frozen and citable.
8. **Ladder of certainty: automated → analyst-reviewed → certified.** Zoneomics' Brief→Summary→Full→Certified Letter; Gridics' data API vs expert-prepared reports; Envelope's drift into consulting. Buyers pay by confidence level, which maps cleanly onto this platform's human-approval gates.
9. **Progressive disclosure per fact, not per page.** UrbanForm's "See less/See more" on each comment; ArcGIS Urban's click-metric→"how the metric is calculated." Depth on demand, one fact at a time.
10. **Shareability as a feature.** ZoLa's URL-per-lot-and-layer-state; UrbanForm's "Share" link and shareable verified parameters; TestFit annotation loops. An analysis that can't be linked/sent doesn't exist for a project team.

# ANTI-PATTERNS (what makes these tools fail/overwhelm)

1. **Uncited authority.** TestFit/Deepblocks/Giraffe show zoning-derived numbers with no code linkage — fine for a developer's screen, fatal for an architect who must defend the number at DOB. Nothing in that class survives NYC filing scrutiny; the manual ZD1 world requires per-dimension ZR citations.
2. **Raw data dump instead of an answer.** ZoLa (and the old OASIS screens in the CityTech deck) show district labels and 30 links but never compute "so what can I build?" — the user is handed homework. Gridics' "30+ attributes" and "hundreds of filters" risk the same wall-of-attributes effect without a summary layer on top.
3. **Envelope shown as if it were buildable area.** The 3D max-volume over-promises; Esri documents the correction explicitly ("parcel coverage and floor area ratio" keep buildings from filling it). Presenting the envelope without the binding-constraint callout misleads architects and clients.
4. **Finance-first framing for a legal question.** Deepblocks leads with returns while zoning sits inside a black box; when the zoning input is wrong, every downstream pro-forma number is wrong with no visible trail. Architects need the legal chain exposed before economics.
5. **Hidden/enterprise-only pricing and demo-gated output.** Gridics, ArcGIS Urban, Giraffe (pricing page), Envelope late-stage: when the sample output can't be seen before a sales call, individual architects self-select out — and Envelope's fate (SaaS→consulting pivot, then domain death) shows pure self-serve NYC zoning SaaS needs either a report SKU (UrbanForm's $197) or a subscription with a visible free tier to survive.
6. **Precision-input pain in the design canvas.** TestFit's noted weakness: "Manual mode is genuinely difficult to use, particularly when trying to input precise measurements" — generative canvases frustrate architects the moment exactness matters.

**Unverified/gaps, for honesty:** Wayback Machine unreachable from this environment (envelope.city archive not directly viewed; reconstructed from TitleVest/siqizhu/press). Demo videos (TestFit, Deepblocks YouTube) not watchable here — described via pages citing them. Not obtained: TestFit report page-by-page contents, Gridics report sample/pricing, Zoneomics à-la-carte report prices, Giraffe prices on giraffe.build itself (secondary sources only), ArcGIS Urban dollar pricing (bundled in ArcGIS Online "Professional Plus").
