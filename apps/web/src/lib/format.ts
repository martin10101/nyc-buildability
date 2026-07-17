/**
 * Display formatting only (tasks M2-T001/M2-T002). NO legal or numeric
 * computation happens in the frontend — values are rendered exactly as
 * delivered by the canonical profile, with locale digit grouping for
 * readability (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md section 7: clear
 * units, no unnecessary decimal noise, no truncation of real precision).
 */

export function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "number") {
    // Group digits; keep every significant decimal the source provided.
    return value.toLocaleString("en-US", { maximumFractionDigits: 20 });
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  if (typeof value === "string") {
    return value;
  }
  return JSON.stringify(value);
}

/** Host of a URL for compact display (never shows query strings/secrets). */
export function urlHost(url: string): string {
  try {
    return new URL(url).host;
  } catch {
    return "unavailable";
  }
}

/**
 * REVIEWED human-label mapping for every PLUTO SODA column (M2-T001 G3
 * defect D1 resolution; scenario S5: no raw column name reaches the user).
 *
 * PROVENANCE OF THIS MAPPING (see the producer report section for the full
 * per-group basis):
 *
 * - COLUMN INVENTORY: the official 108-column SODA inventory of dataset
 *   64uk-42ks (/api/views metadata, retrieved 2026-07-16; committed as
 *   fixture F08_api_views_columns_snapshot.json and mirrored in
 *   services/api/app/connectors/pluto_soda.py PLUTO_COLUMN_TYPES, which CI
 *   cross-checks against the fixture). Every key below is from that
 *   inventory — no invented columns.
 * - MEANINGS: the official "PLUTO DATA DICTIONARY May 2026 (26v1)"
 *   (https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/
 *   bytes/pluto_datadictionary.pdf, G1-verified direct read) and the PLUTO
 *   README 26v1, as documented with page citations in
 *   docs/research/pluto-mappluto-2026-07-16.md (sections 3.2, 3.4, 4.1-4.3)
 *   and in services/api/app/profile/builder.py (M2-T004 documented
 *   19-column completeness basis with per-column dictionary citations).
 * - LABELS ARE NAMES, NOT INTERPRETATIONS: each label expands the official
 *   field name (e.g. ZoneDist1 -> "Zoning district 1"); no label attaches
 *   legal meaning, and code-list VALUES (BldgClass, LandUse, SPDist,
 *   LtdHeight appendices B-D) are deliberately NOT translated — the
 *   research doc records appendix extraction as an open connector-build
 *   item (OQ-5 residual).
 * - DISCLOSED LIMITS (flagged for the G3 reviewer to spot-check against
 *   the dictionary PDF): the expansions "community facility" (facilfar),
 *   "apportionment" (appbbl/appdate) and "E-designation" (edesignum)
 *   follow the official dictionary field names; the committed research doc
 *   cites the pages (residfar/commfar/facilfar p.36-37, condono p.39) but
 *   does not quote those name expansions verbatim. The acronyms DCAS, MAS,
 *   and RPAD in the input-vintage labels are passed through UNEXPANDED
 *   because no committed research defines them — passing an acronym
 *   through is not an interpretation; inventing an expansion would be.
 */
export const FIELD_LABELS: Record<string, string> = {
  // --- Identity (dictionary p.38; Geoclient User Guide v2.0.4 s2.2.1) ---
  bbl: "BBL",
  borocode: "Borough code",
  borough: "Borough (source code)",
  block: "Tax block",
  lot: "Tax lot",
  address: "Address",
  zipcode: "ZIP code",

  // --- Lot geometry and character (dictionary p.21/p.29; research s4.1) ---
  lotarea: "Lot area",
  lotfront: "Lot frontage",
  lotdepth: "Lot depth",
  lottype: "Lot type code",
  irrlotcode: "Irregular lot",
  easements: "Easements",
  splitzone: "Split zoning lot",

  // --- Zoning assignment columns (README 26v1 minor-release zoning
  //     attributes; research s3.2; builder ZONING_DISTRICT_COLUMNS /
  //     OVERLAY_COLUMNS / SPECIAL_DISTRICT_COLUMNS mapping) ---
  zonedist1: "Zoning district 1 (primary)",
  zonedist2: "Zoning district 2",
  zonedist3: "Zoning district 3",
  zonedist4: "Zoning district 4",
  overlay1: "Commercial overlay 1",
  overlay2: "Commercial overlay 2",
  spdist1: "Special purpose district 1",
  spdist2: "Special purpose district 2",
  spdist3: "Special purpose district 3",
  ltdheight: "Limited height district",
  zonemap: "Zoning map",
  // G3 correction C1 (2026-07-17): pure name expansion only — the prior label
  // "Zoning map change code" was an invented interpretation (ZMCode marks a lot
  // on the border of two or more zoning maps, not a map change).
  zmcode: "Zoning map code",

  // --- FAR reference columns (dictionary p.36-37: based on ZoneDist1,
  //     exclusive of bonuses — informational reference values, never rule
  //     outputs; affresfar/mnffar are new in 26v1 per README/research
  //     s3.4: "max affordable residential FAR" / "max manufacturing FAR",
  //     SODA column for ManuFAR is mnffar) ---
  builtfar: "Built FAR",
  residfar: "Maximum residential FAR",
  commfar: "Maximum commercial FAR",
  facilfar: "Maximum community facility FAR",
  affresfar: "Maximum affordable residential FAR",
  mnffar: "Maximum manufacturing FAR",

  // --- Inclusionary housing / environmental designations (README 26v1
  //     s3.4: MIHOption1-4 = Mandatory Inclusionary Housing option flags;
  //     SODA columns are mih_opt1-4 per research s4.2 G1 resolution;
  //     EDesigNum per research s3.2) ---
  mih_opt1: "Mandatory Inclusionary Housing option 1",
  mih_opt2: "Mandatory Inclusionary Housing option 2",
  mih_opt3: "Mandatory Inclusionary Housing option 3",
  mih_opt4: "Mandatory Inclusionary Housing option 4",
  edesignum: "E-designation number",
  transitzone: "Transit zone",

  // --- Landmark / historic / flood ---
  landmark: "Landmark",
  histdist: "Historic district",
  firm07_flag: "2007 FIRM flood flag",
  pfirm15_flag: "2015 preliminary FIRM flood flag",

  // --- Existing use and building (dictionary p.22/p.28/p.34-35) ---
  landuse: "Land use code",
  bldgclass: "Building class",
  bldgarea: "Building floor area",
  comarea: "Commercial floor area",
  resarea: "Residential floor area",
  officearea: "Office floor area",
  retailarea: "Retail floor area",
  garagearea: "Garage floor area",
  strgearea: "Storage floor area",
  factryarea: "Factory floor area",
  otherarea: "Other floor area",
  areasource: "Area source code",
  numbldgs: "Number of buildings",
  numfloors: "Number of floors",
  unitsres: "Residential units",
  unitstotal: "Total units",
  bldgfront: "Building frontage",
  bldgdepth: "Building depth",
  ext: "Extension code",
  proxcode: "Proximity code",
  bsmtcode: "Basement code",
  yearbuilt: "Year built",
  yearalter1: "Year altered (1)",
  yearalter2: "Year altered (2)",

  // --- Ownership and valuation (dictionary p.33-34) ---
  ownertype: "Owner type code",
  ownername: "Owner name",
  assessland: "Assessed land value",
  assesstot: "Assessed total value",
  exempttot: "Exempt total value",

  // --- Development-history linkage (dictionary p.38-39; research s4.4
  //     APPBBL/condo semantics) ---
  appbbl: "Apportionment BBL (originating tax lot)",
  appdate: "Apportionment date",
  condono: "Condominium number",

  // --- Administrative / service districts (official column inventory;
  //     political/admin district inputs per research s3.3) ---
  cd: "Community district",
  schooldist: "School district",
  council: "City Council district",
  firecomp: "Fire company",
  policeprct: "Police precinct",
  healtharea: "Health area",
  healthcenterdistrict: "Health center district",
  sanitboro: "Sanitation district borough",
  sanitdistrict: "Sanitation district",
  sanitsub: "Sanitation subsection",

  // --- Census geography (official column inventory) ---
  ct2010: "2010 census tract",
  cb2010: "2010 census block",
  tract2010: "2010 census tract (alternate format)",
  bct2020: "2020 census tract (borough-prefixed)",
  bctcb2020: "2020 census block (borough-prefixed)",

  // --- Coordinates and geometry (research s1: EPSG:2263 NAD83
  //     New York-Long Island ftUS state plane) ---
  xcoord: "X coordinate (NY state plane)",
  ycoord: "Y coordinate (NY state plane)",
  latitude: "Latitude",
  longitude: "Longitude",
  geom: "Geometry",

  // --- Dataset administration ---
  sanborn: "Sanborn map number",
  taxmap: "Tax map number",
  plutomapid: "PLUTO map id",
  version: "PLUTO release version",
  dcpedited: "DCP-edited flag",
  notes: "Notes",

  // --- Per-input vintage dates (research s4.2 G1 resolution: eight
  //     per-record input-vintage provenance columns; input sources per the
  //     README DATES OF DATA table, research s3.3) ---
  basempdate: "Input data vintage (base map)",
  dcasdate: "Input data vintage (DCAS)",
  edesigdate: "Input data vintage (E-designations)",
  landmkdate: "Input data vintage (landmarks)",
  masdate: "Input data vintage (MAS)",
  polidate: "Input data vintage (political districts)",
  rpaddate: "Input data vintage (RPAD)",
  zoningdate: "Input data vintage (zoning features)",
};

/**
 * Human label for a source field key. Unknown keys (e.g. a future dataset
 * column not yet reviewed into FIELD_LABELS) are shown WITH an explicit
 * unlabeled marker — honest, never silently raw (scenario S5; a unit test
 * asserts the mapping covers the full current 108-column inventory so this
 * fallback is unreachable today).
 */
export function fieldLabel(field: string): string {
  return FIELD_LABELS[field] ?? `${field} (source column — label pending review)`;
}
