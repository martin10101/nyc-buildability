/**
 * Display formatting only (task M2-T001). NO legal or numeric computation
 * happens in the frontend — values are rendered exactly as delivered by the
 * canonical profile, with locale digit grouping for readability
 * (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md section 7: clear units, no
 * unnecessary decimal noise, no truncation of real precision).
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

/** Human label for a PLUTO-style field key: "lotarea" stays visible raw. */
export const FIELD_LABELS: Record<string, string> = {
  lotarea: "Lot area",
  lotfront: "Lot frontage",
  lotdepth: "Lot depth",
  lottype: "Lot type code",
  irrlotcode: "Irregular lot",
  easements: "Easements",
  landuse: "Land use code",
  ownertype: "Owner type code",
  ownername: "Owner name",
  assessland: "Assessed land value",
  assesstot: "Assessed total value",
  exempttot: "Exempt total value",
  bbl: "BBL",
  borocode: "Borough code",
  borough: "Borough (source code)",
  block: "Tax block",
  lot: "Tax lot",
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
  bldgclass: "Building class",
  ext: "Extension code",
  proxcode: "Proximity code",
  bsmtcode: "Basement code",
  yearbuilt: "Year built",
  yearalter1: "Year altered (1)",
  yearalter2: "Year altered (2)",
  builtfar: "Built FAR",
  splitzone: "Split zoning lot",
  landmark: "Landmark",
  histdist: "Historic district",
  firm07_flag: "2007 FIRM flood flag",
  pfirm15_flag: "2015 preliminary FIRM flood flag",
  transitzone: "Transit zone",
  zonemap: "Zoning map",
  zmcode: "Zoning map change code",
};

export function fieldLabel(field: string): string {
  return FIELD_LABELS[field] ?? field;
}
