---
name: zr-r1-r2-height-setback-source-facts
description: Official ZR (City of Yes, 2024-12-05) source facts + interpretation gap for R1/R2-series height & setback — why an "A1 numeric per-district" clone of the R5 pilot is not cleanly buildable for R1/R2
metadata:
  type: reference
---

Verified against zr.planning.nyc.gov (retrieved 2026-09-13) for the current effective (City of Yes for Housing Opportunity, Last Amended 2024-12-05) height & setback regime for R1/R2 residence districts.

**Governing sections (Article II, Chapter 3):**
- **§23-42** (parent): routes group labels "R1 R2 R3 R4 R5" to §23-421 (basic pitched-roof envelopes) and §23-422 (basic flat-roof envelopes); standard setback §23-423; increases on qualifying-residential-sites/large-sites §23-424/§23-425; additional provisions §23-426 and §23-44. Heights measured from the **base plane**.
- **§23-421** (pitched-roof envelope) applies to **"R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A"** for single-/two-family detached, semi-detached, or zero-lot-line buildings. **Uniform** numeric caps: perimeter walls max **25 ft above base plane**; ridge line **35 ft above base plane**. The setback is pure **sloping-plane geometry** (apex points, ridge lines, ≤80° pitch, paragraphs a–g) = **A2 territory** (D-045-R008), NOT the flat §23-423 10/15 ft rule. Also a lot-geometry-keyed provision: "In R1 and R2 Districts **without a letter suffix**", for lots ≥9,500 sf & ≥100 ft width OR ≥5% slope, the reference plane may sit up to 5 ft above the base plane — also A2.
- **§23-422** (flat-roof): "R3-2 R4 R4B R5 R5B R5D" — **R1/R2 NOT included**.
- **§23-424** (QRS alternative): text (per M4-T006 capture) **excludes** R1/R2 ("is not located within an R1 or R2 District").
- **§23-44 / §23-441 / §23-442**: govern R9/R10 towers etc.; do NOT carry R1/R2-series contextual-variant caps.

**Authoritative R1/R2 variant enumeration** (from the byte-verified in-corpus `zr-23-21` FAR snapshot, digest b52771e6…): R1 series = {R1-1, R1-2, R1-2A}; R2 series = {R2, R2A, R2X}. R2X sits in a **higher-density FAR row grouped with R4** (standard FAR 1.00, vs 0.75 for R1-1/R1-2/R1-2A/R2A/R2), so R2X is treated differently from R2/R2A for at least one bulk parameter.

**The unresolved legal-interpretation gap (why guessing is barred by principle #3):**
§23-421 names the R1/R2 series only with **bare group labels "R1" and "R2"** — it does NOT enumerate the mapped variant symbols (contrast R3A/R3X/R3-1/R3-2 and R4/R4-1/R4A, which ARE listed explicitly). R2A, R2X, R1-2A appear in NEITHER §23-421 nor §23-422 nor §23-44. So it cannot be established from captured official text alone (a) whether §23-421's "R1"/"R2" sweep in the lettered variants R1-2A/R2A/R2X, and (b) whether the higher-density R2X shares the 25/35 pitched envelope or has a distinct/taller one. That mapping is a qualified-human (G6) legal-nomenclature call.

**Consequence for A1-wave packets:** an "R1/R2 = clean numeric per-district, no sky-exposure-plane dependency" premise is only partly true. The two height CAPS (25/35) are flat numbers (encodable exactly like the accepted `r5a_height` rule — same §23-421), but the setback is A2 geometry and the per-variant scoping needs the group-label ruling. Building differentiated per-variant rules with cross-variant isolation (as a pilot-clone packet demands) is blocked until the enumeration mapping + R2X envelope are resolved by a qualified human, or the packet is narrowed. See [[stale-span-inspectability-resolution]] discipline for evidence handling.
