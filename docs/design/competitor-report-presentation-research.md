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

---
---

<!-- PASS 2 preserved VERBATIM by the orchestrator (report-preservation rule; transport
entity-decoding applied: &amp; -> &). Author: independent general-purpose research subagent
(web research pass 2 of 2: practitioner sentiment — Reddit archives, forums, reviews,
practitioner blogs), returned 2026-09-12 (UTC). -->

# PRACTITIONER VOICE RESEARCH: ZONING-ANALYSIS TOOLS & REPORTS
**Retrieval date for all sources: 2026-09-12.** Method note: reddit.com blocks Anthropic's crawler, so Reddit quotes were pulled from the Arctic Shift public Reddit archive (arctic-shift.photon-reddit.com) — quotes are verbatim from archived comment/post bodies; permalinks given are the canonical reddit.com URLs. Archinect and G2 return HTTP 403 to this crawler, so those items rely on search-result summaries and are marked **[paraphrase]**. One review source (archigenai.com) has unverifiable authorship and is flagged.

---

## 1. THE FIRST QUESTION: "What can I build / how many units / how many sq ft"

The evidence is unusually consistent — the first question is always yield, phrased as "what can I build here," and practitioners state it explicitly:

- **"before anyone submits anything, they should be able to enter an address and get a clear answer to 'what can I probably do here, what approvals will I need, and what could kill this project?'"** — u/MeaningHealthy7167, r/RealEstateDevelopment, 2026-06-08, https://www.reddit.com/r/RealEstateDevelopment/comments/1tsi01q/
- **"you can ask stuff like 'what can I build at [address]?' and get a pretty solid summary with the code references it used"** — u/ctaldigital describing the AI zoning tool they actually use, r/Architects, 2026-07-24, https://www.reddit.com/r/Architects/comments/1mxsrwb/
- Thread title, verbatim: **"How many dwellings can I fit on this land?"** — u/randomladanon, r/Architects, 2024-12-31, https://www.reddit.com/r/Architects/comments/1hq79yr/
- **"it takes days just to tell a client 'yes, this lot works'"** — u/EndAccomplished7709, an architect-founder describing why he built a zoning tool, r/RealEstateDevelopment, 2025-12-31, https://www.reddit.com/r/RealEstateDevelopment/comments/1q0rs8v/
- WC Studio (Tacoma architecture firm) structures its cheapest feasibility tier around exactly one question: Level 1 **"addresses the foundational question: 'What can I build on this property?'"** [close paraphrase of firm's own framing] — https://wc-studio.com/journal/2020/5/22/feasibility-study-for-multifamily-development-projects
- Fontan Architecture (NYC) structures its zoning explainers to land on the same two numbers: **"Zoning Floor Area = 20,000 sq ft"** then heading **"How many apartments can we build on our R8B lot?"** — https://fontanarchitecture.com/r8b-zoning-nyc/ (read via NYC CB12 PDF mirror, cbmanhattan.cityofnewyork.us)
- The second question is money: TestFit's flagship customer vets sites by **"cost of yield, number of units, square footage, and more"** — Ware Malcomb story, https://www.testfit.io/customer-stories/ware-malcomb
- An NYC architect specifies the pro wants max yield, not just the base numbers: **"your tool should be smart to search for the zoning loop holes, search for the hidden zoning deductions that might maximize your design"** — u/Afraid-Muscle-4099, r/Architects, 2025-01-20, https://www.reddit.com/r/Architects/comments/1i4dnsw/
- One sophisticated user wants it as a dialogue, not a dump: **"I might ask… 'How high can the building be?' Since that depends on a lot of factors, the LLM could spit back 'how wide is the street? Is it on a corner lot? Will it follow Quality Housing regulations?'"** — u/patricktherat, same thread, 2025-01-20.

**Verdict: strong, multi-source.** Units + buildable SF first, dollars second, rules only as backup for the numbers.

## 2. TRUST COMPLAINTS: wrong, stale, missing overlays — and what earns trust

This is the loudest theme in the corpus, and liability is its engine:

- Top-voted comment (score 14) on an NYC AI-zoning-tool pitch: **"If this tool is built and I use it…. Would you be held liable if I was given an inaccurate response that then used?"** — u/Whenthebae, r/Architects, 2025-01-19, https://www.reddit.com/r/Architects/comments/1i4dnsw/
- Highest-scored comment (13) in the AI-for-zoning thread: **"I've tested ChatGPT with code questions at each new version, all of them have hallucinations within 5-10 fairly simple compliance questions. For that reason it just can't be trusted so why would I waste my time using it only to have to double check everything that I carry all the liability for"** — u/baerStil, r/Architects, 2025-08-23, https://www.reddit.com/r/Architects/comments/1mxsrwb/
- Staleness specifically (score 7): **"The issue is all old codes are still in circulation… I've had it find preliminary city code changes, that weren't approved, as if accurate and cited them by correct code section numbers."** — u/Slow-Distance7847, same thread, 2025-08-23. (Citations can be *correct-looking and still wrong* — a critical design warning.)
- Silent omissions: **"it impressively missed both the firefighter command center requirement as well as everything related to smoke control… it missed a setback requirement for buildings over four stories. I don't trust it now, but maybe one day."** — u/MasonHere, same thread, 2025-08-23.
- The professional-verification norm: **"Anyone sane isn't going to trust a random intern telling them it's a 10' setback, they're going to look at the regs themselves."** — u/metisdesigns, r/Architects, 2025-01-20, thread 1i4dnsw.
- What earns partial trust — *citations at parcel level, from the actual municipal source*: **"It does parcel specific zoning analysis with ordinance citations instead of just giving a generic response."** — u/Good-Indication-9489, r/Architects, 2026-07-25, thread 1mxsrwb; and **"Been using ChatGPT and Claude for this, responses were too generic… [this tool] pulls directly from the municipal source, conditions, overlays, anything you can think of"** — u/tatyanaaaaaa, r/RealEstateDevelopment, 2026-04-28, https://www.reddit.com/r/RealEstateDevelopment/comments/1sztq22/
- The accepted mental model for AI output: **"I find it a very useful librarian, you still need to read the book. It just tells you where to look."** — u/LayWhere, thread 1mxsrwb, 2025-08-23; echoed by u/kjsmith4ub88: **"Anything it summarizes can't be trusted."**
- TestFit's zoning data itself draws the same complaint: **"The zoning import was about 80% accurate, it caught the base FAR and height limit but missed a transit-overlay bonus."** — archigenai.com TestFit Review 2026 (https://archigenai.com/testfit-feasibility-generative-design-review-2026.html). **Caution: single review site of unverifiable authorship; treat as weak evidence, but it matches the pattern above.**
- Even the official NYC source disclaims itself — ZoLa FAQ, verbatim: **"the Department and the City make no representation as to the accuracy of the information, its timeliness, or its suitability for any purpose… All users should independently verify the accuracy of the data for their purposes"**, and for "What uses are allowed on my property?" DCP's answer is to contact the Zoning Information Desk where **"The staff will research and advise you."** — https://www.nyc.gov/assets/planning/download/pdf/data-maps/maps-geography/zola/zola-faq.pdf
- The upstream reality no tool can fully fix: **"even the best 'pre-app' research cannot be fully relied upon… you will be $250K+ into the project before you are certain that you can build it."** — u/BassManJam99 (commercial developer), r/RealEstateDevelopment, 2026-06-18, thread 1tsi01q; and **"You can do everything right and still get a correction notice because one reviewer interprets a code differently than another."** — u/NTXLandGal (20 yrs DFW land development), 2026-06-10, same thread.

**Verdict: strong.** Trust = per-fact citation to the current official text + explicit coverage statement + honest "what we can't know" — not a generic disclaimer.

## 3. OVERLOAD COMPLAINTS: PDF-dumps and fragmentation vs. "clean"

- The pain is expressed as *fragmented pieces*, not too few pages: **"The annoying part is trying to connect all the pieces: zoning district, allowed uses, overlays, setbacks, parking, special permits, variances, site plan review, and whatever random PDF the town buried on page 4 of their website."** — u/MeaningHealthy7167, thread 1tsi01q, 2026-06-08. What the same user praises: **"a plain-English zoning/due diligence report so you can see the likely red flags before paying for plans… a really useful first-pass filter."**
- **"Digging through zoning PDFs, calculating setbacks, FAR… it takes days"** — u/EndAccomplished7709 (architect), thread 1q0rs8v, 2025-12-31.
- **"zoning data is incredibly fragmented — every municipality does it differently, overlays vary, and what's 'allowed' on paper often has 10 conditions attached to it"** — u/KnownRide6195, thread 1sztq22, 2026-04-28.
- **"Fee schedules are buried, submission checklists are outdated… There's no centralized place to understand what a specific city actually requires"** — u/NTXLandGal, thread 1tsi01q, 2026-06-10.
- NYC scale of the dump: **"In NYC, there are over 3,000 pages of zoning regulations that must be reviewed."** — u/Consistent-Nerve-874 (NYC tool builder), thread 1i4dnsw, 2025-01-20.
- What gets praised as clean in actual reviews: **"TestFit allows us to evaluate numerous options in real-time with our clients"** (Thomas R., Architecture & Planning, 5★, June 2021) and **"Easy to get unit count and category ratio"** (Wien T., 3★) — while the usability complaint on the same product is **"Hard to use on Manual mode"** for precise measurements — SoftwareAdvice/Capterra-network TestFit reviews, https://www.softwareadvice.com/construction/testfit-profile/
- **"One downloaded report from UrbanForm replicates what would have taken me half a day to prepare."** — Lead City Planner, Yamhill County (vendor-published testimonial), https://urbanform.us/
- UX literature converges: NN/g progressive disclosure — **"Initially, show users only a few of the most important options"**, defer the rest, and keep it to **two levels max** because deeper **"designs… typically have low usability because users often get lost"** — https://www.nngroup.com/articles/progressive-disclosure/. Fintech-compliance UX writing names the same trap a "compliance paradox": dense legal disclosure erodes rather than builds user trust [paraphrase] — https://markswebb.com/insights/ux-for-ai-compliance-regulatory-ux/, https://think.design/blog/balancing-ux-with-regulatory-compliance-in-fintech-design/

**Verdict: moderate-to-strong.** Nobody asks for fewer facts — they ask for *assembly*: one screen that connects district + overlays + conditions, red flags surfaced, full text one click below.

## 4. WORKFLOW REALITY: how a feasibility check actually runs

- Many firms still refuse automation outright. Top answer (score 7) to "How did you automate your Space Analysis, Zoning, Laws and Regulations?": **"We don't. Given the constantly shifting regulatory landscape, along with the specificities of each project and site it is more prudent to go through each issue manually."** — u/Hrmbee, r/Architects, 2025-02-11, https://www.reddit.com/r/Architects/comments/1in1r9r/ — plus **"on top of phone calls and preapp meetings and everything else to make sure everything is being interpreted correctly"** (u/Exotic-Ad5004, same thread).
- Time scale, NYC: **"This takes weeks and weeks of work and NYC zoning is not always that straight forward in fact it's extremely complex"** (u/Afraid-Muscle-4099) and **"it takes their company around 4-6 weeks to fully finish the zoning process"** (u/Consistent-Nerve-874) — thread 1i4dnsw, 2025-01-20.
- Time scale, small projects: WC Studio prices Level 1 at **"2-4 hours to complete (about $400-$800)"**, Level 2 **"10-15 hours (about $1,800-$2,500)"**, Level 3 **"flat fee of $5,000"** for 20-30 hours — wc-studio.com (2020).
- Method (multifamily): Marilyn Moedinger's published sequence — prerequisites (survey, geotech) → **zoning deep dive** (dimensional tables, non-conformances, overlays, parking) → envelope → **egress/fire code** → prototype units to validate the proforma; tools are Excel + survey underlay; **"we often start with laying out egress stairs and elevators"** because floorplate-vs-egress decides **"whether a site is worth a dang"**; and the report's purpose is **"to document what you did so that the zoning officer can clearly see it during their review."** — https://mwmoedinger.substack.com/p/multifamily-feasibility-studies-5 and /how-to-do-a-zoning-analysis-part-0fb
- Where a tool fits: pre-design/deal-screening only. Ware Malcomb: site plan **"3 days to half a day"**, **"saving over $200k in labor hours"** on unpaid pursuit work — testfit.io/customer-stories/ware-malcomb. Archinect consensus **[paraphrase, forum blocked]**: TestFit is "limited to early schematic… mostly a feasibility study to see if your project fits on your site and if the developer's proforma might work"; "useful tool but not really a game changer" — https://archinect.com/forum/thread/150252043/automated-architecture
- Where they insist on humans: interpretation and the jurisdiction gap — **"The codified rules are honestly the easy part… The expensive part is the gap between what's technically by-right and what the reviewers will actually sign off on."** — u/jason-noetic, thread 1tsi01q, 2026-06-01. Also **"I can have AI give me the zoning in 30 seconds"** — what's missing is **"more actual analysis by consultants"** (u/OrangeArch, same thread). Checking dynamics: **"Checking the output of a model would take as much time as actually just doing it yourself."** — u/NBW99, thread 1i4dnsw, 2025-01-19.

**Verdict: strong.** The tool's ceiling is "instant first pass + documentation"; the floor practitioners defend is interpretation, pre-app calls, and sealed sign-off.

## 5. PRICE SENSITIVITY

- Incumbent tool prices: TestFit **"$195/month"** (Parking Solver) but the real product is **"Starting at $15,000/year"** (Site Solver) / **"$20,000/year"** (Portfolio) — https://www.testfit.io/pricing. Deepblocks **"starts at $2,000 per month"** — https://slashdot.org/software/p/Deepblocks/ (which also shows **"No User Reviews"** — telling for a 2017 company). Buildability sells reports at **"$99 per property"** / **"$289/month"** against a claimed manual baseline of **"$3,500+"** and **"2–3 weeks"** — https://buildability.us/
- The affordability complaint: **"The seat cost has crept up. For a sole practitioner doing one feasibility a quarter, it's hard to justify."** — archigenai.com TestFit review (weak-provenance source, flagged above).
- What the manual alternative costs (the price ceiling a tool competes against): an NYC homeowner was quoted **"$750 for feasibility study"** for a garage/studio job — and architects in the thread called the overall package **"Seems incredibly cheap"** (u/lukekvas, score 9), **"Suspiciously good deal"** (u/frenchiebuilder), with one saying **"I charge $19500 for feasibility"** (u/Not-a-Kitten) — r/Architects, 2026-07-17, https://www.reddit.com/r/Architects/comments/1uz46l2/. WC Studio's $400–$5,000 ladder sits between those poles.
- The developer's framing of cost: fees are noise, carry is the cost — **"permit delays on a construction loan cost the owner $8,000-$15,000 a month in interest… The direct fees are almost never the expensive part. The time is."** — u/NTXLandGal, thread 1tsi01q, 2026-06-10; **"Costs us 1-2 years and $1-2m per project"** — u/Free_Elevator_63360, same thread.

**Verdict: moderate.** Two viable anchors exist in the market: per-report ($99–$800, competing with the architect's Level-1 study) and enterprise seats ($15k+/yr, competing with unpaid pursuit hours). Sole practitioners are explicitly priced out of the latter.

## 6. NYC-SPECIFIC

- Complexity in practitioners' own words: **"NYC zoning is not always that straight forward in fact it's extremely complex. Are you thinking about incorporating bonuses or air rights? Quality housing?… search for the hidden zoning deductions"** — u/Afraid-Muscle-4099 (NYC/JC mixed-use firm), thread 1i4dnsw, 2025-01-20; **"over 3,000 pages of zoning regulations"** (same thread).
- A working NYC architect (Jorge Fontan, 224 blog posts on NYC zoning alone) hedges even his own explainer: **"Be aware that zoning is complicated and I am only addressing the basics here. I assure you there are many additional issues and variations to consider beyond this example."** and **"As an architect I study Zoning Codes closely, but these are complicated and quite involved issues."** His R8B piece must touch Quality Housing, community facility rules, commercial overlays, Inclusionary Housing ("Always check if your property is subject to…"), the Sliver Law, and density factor 680 — for *one* district — https://fontanarchitecture.com/r8b-zoning-nyc/ (CB12 PDF mirror).
- ZoLa's limits, per its own FAQ: monthly update cadence with **"a lag between when an action occurs and when the information is entered into the system"**; no representation of accuracy; "what can I build" questions routed to human staff — nyc.gov ZoLa FAQ PDF.
- Lay users misread ZoLa in predictable ways: a Queens owner saw "max 2 units" in R4A yet found bigger nearby buildings; answers hinged on invisible context — **"this specific lot could be within 100 feet of a wide street, and thus more FAR"** (u/13141314Dankeee) and prior non-conforming buildings / **"swiss cheese"** rezonings (u/damndudeny) — r/AskNYC-adjacent thread, 2024-07-24, https://www.reddit.com/r/asknyc/comments/1eb59q4/ [subreddit per archive record; id 1eb59q4].
- NYC process costs from Archinect **[paraphrase, forum blocked]**: clients weighing a zoning change via ULURP/BSA were told to expect **~$100,000 and 1–2 years** — https://archinect.com/forum/thread/150046018/zoning-architect-fees-do-i-need-engineer-on-board
- NYC filing reality: **"In NYC, you pretty much need permits and license to do anything"** and DOB approval usually needs only **"a schematic or permit set"** for small projects, but **"the amount of permits and bureaucracy… ADUs are a very new thing here"** — u/jae343 (NYC architect), thread 1uz46l2, 2026-07-17.
- Note: nothing found from practitioners praising any tool's NYC coverage; TestFit's US coverage discussion ("at least ConUS") never demonstrates NYC-specific rules like Quality Housing or sliver — and the r/Architects thread explicitly asks "Does TestFit offer NYC? I think these guys are specifically targeting NYC." **The NYC-correct zoning engine is perceived as an open gap.**

---

# WHAT THIS MEANS FOR OUR UI

1. **First screen = the verdict, three numbers deep.** Max residential floor area (ZFA), max units, max height/envelope — with the client-facing question answered in a sentence ("what can I probably do here, what approvals will I need, and what could kill this project" — the practitioner's own triad). Everything else is layer two. (Evidence: Section 1, strong.)

2. **Every number carries a citation to the governing ZR section, and citations must be *live and versioned*, not decorative.** Practitioners' worst story is a correct-looking citation to a superseded or unadopted text (u/Slow-Distance7847). Show the ZR section, its effective date, and the dataset vintage next to the value — this is exactly our platform's provenance principle, and it is the single strongest trust differentiator in the evidence. (Section 2, strong.)

3. **Position the product as the librarian, never the lawyer.** The accepted mental model is "it tells you where to look; you still read the book." UI language should say "computed from…, verify before filing," route interpretation to humans, and never render an unqualified "COMPLIANT." A visible "reviewed by a qualified human" state would convert the liability objection (top-voted comment in Section 2) into a feature. (Sections 2 & 4, strong.)

4. **Overlays, special districts, and "hidden" modifiers are the credibility test, so surface them affirmatively — including their absence.** The canonical failure is "caught base FAR, missed the transit-overlay bonus." Show an explicit checklist: commercial overlay ✓/✗, special district ✓/✗, IH designated area, landmark, sliver rule, split-lot condition — each marked found/not-found/unknown, never silently omitted. "Unknown" must be a first-class display state. (Sections 2, 3, 6; strong for NYC.)

5. **Progressive disclosure, two levels, red-flags-first.** Level 1: verdict + numbers + red flags in plain English. Level 2: per-parameter table (required/existing/proposed — the exact spreadsheet architects already keep, per Moedinger) with rule text and citation. Don't bury the dump — replace it with an assembled, connected view; NN/g warns against going deeper than two levels. (Section 3, moderate-strong.)

6. **Export must feed the practitioner's own deliverable, not replace it.** Architects monetize the zoning analysis as a $400–$19,500 document whose purpose is "to document what you did so the zoning officer can clearly see it." Ship a clean printable report + the parameter table as data (CSV/Excel), so our output becomes their appendix and evidence trail rather than their competitor. (Sections 4 & 5, moderate.)

7. **Show scenario yield in developer vocabulary immediately after the verdict** — units, sellable/rentable SF, and (later) yield-on-cost — because the second question is always financial, and the tools practitioners tolerate (TestFit) won adoption by pairing massing with a live pro-forma. (Sections 1 & 4, moderate.)

8. **State coverage honestly and per-lot.** The recurring failure mode of generic tools is unstated coverage ("Code compliant where?" — HN HomeCat thread, https://news.ycombinator.com/item?id=49601328). For NYC we can invert this: per-lot data-vintage banner ("Zoning layers as of DCP release YYYY-MM; ZoLa itself lags month-end") beats ZoLa's own blanket disclaimer and directly answers the staleness distrust. (Sections 2 & 6, moderate.)

**Honesty notes on evidence weight:** Sections 1, 2, 4 rest on many independent practitioners across Reddit (2022–2026), review platforms, and practitioner blogs — robust. The TestFit 80%-accuracy quote and seat-cost complaint come from one unverifiable review site (archigenai.com) and should not be cited alone, though both match stronger independent evidence. Archinect material is paraphrase-only (site blocks crawlers). "What they praise as clean" rests mostly on vendor-published testimonials plus a handful of Capterra-network reviews from 2021 — the thinnest cell in the grid. No practitioner quote was found praising or damning any tool's NYC-specific accuracy — that silence is itself a finding: nobody currently owns NYC-correct in the practitioner conversation.
