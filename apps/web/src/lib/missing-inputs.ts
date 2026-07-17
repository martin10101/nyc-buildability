/**
 * Missing-inputs display policy (task M2-T001; M1-T005 G3 defect D3).
 *
 * PROBLEM: the builder explicitly reports EVERY absent PLUTO column (42
 * boilerplate entries on typical lots), which is honest but is UI noise.
 *
 * DOCUMENTED FRONTEND FILTER POLICY (this is the policy record required by
 * the task packet — a display grouping, never a data filter):
 *
 * 1. NOTHING IS DROPPED. Every missing_inputs entry from the API is always
 *    reachable on screen; the section header always shows the TOTAL count.
 * 2. An entry is SURFACED (immediately visible) when either
 *    a. its criticality is "critical" (PRD section 12 — critical gaps are
 *       never collapsed), or
 *    b. its field is in FEASIBILITY_RELEVANT_FIELDS below — columns that
 *       feed zoning/feasibility reasoning (lot geometry, zoning districts
 *       and overlays, FAR family, floor area, units, landmark/height
 *       limits, inclusionary-housing options, environmental designations).
 * 3. All remaining entries are GROUPED behind an explicit, labeled
 *    count toggle ("Show N more missing fields…") — collapsed by default,
 *    one keyboard-accessible action to reveal, count always visible.
 * 4. The grouping is presentation-only: it never alters data_completeness,
 *    coverage labels, or the underlying profile document.
 *
 * Grounding for the relevant-field list: PLUTO columns already surfaced as
 * facts by the accepted M1-T005 builder (lot_facts / existing_building_facts
 * / zoning buckets) plus the zoning-family columns named by the D5 fallback
 * join. Administrative/service columns (firecomp, sanborn, policeprct,
 * healtharea, taxmap, date-stamp columns, …) are grouped, not surfaced.
 */

import type { MissingInput } from "./property-profile";

export const FEASIBILITY_RELEVANT_FIELDS: ReadonlySet<string> = new Set([
  // Lot geometry and character
  "lotarea",
  "lotfront",
  "lotdepth",
  "lottype",
  "irrlotcode",
  "easements",
  // Zoning districts, overlays, special districts, limited height
  "zonedist1",
  "zonedist2",
  "zonedist3",
  "zonedist4",
  "overlay1",
  "overlay2",
  "spdist1",
  "spdist2",
  "spdist3",
  "ltdheight",
  "splitzone",
  "zonemap",
  "zmcode",
  // FAR family
  "builtfar",
  "residfar",
  "commfar",
  "facilfar",
  "affresfar",
  "mnffar",
  // Existing building
  "bldgarea",
  "resarea",
  "comarea",
  "officearea",
  "retailarea",
  "garagearea",
  "strgearea",
  "factryarea",
  "otherarea",
  "numbldgs",
  "numfloors",
  "unitsres",
  "unitstotal",
  "bldgfront",
  "bldgdepth",
  "bldgclass",
  "yearbuilt",
  "yearalter1",
  "yearalter2",
  "ext",
  "proxcode",
  "bsmtcode",
  // Landmark / historic / flood / land use
  "landmark",
  "histdist",
  "landuse",
  "firm07_flag",
  "pfirm15_flag",
  // Inclusionary housing options and environmental designations
  "mih_opt1",
  "mih_opt2",
  "mih_opt3",
  "mih_opt4",
  "edesignum",
  // Development-history linkage
  "appbbl",
  "appdate",
  "condono",
]);

export interface GroupedMissingInputs {
  /** Immediately visible entries (critical or feasibility-relevant). */
  surfaced: MissingInput[];
  /** Entries behind the explicit count toggle. */
  grouped: MissingInput[];
  /** Always-displayed total (= surfaced.length + grouped.length). */
  total: number;
}

export function groupMissingInputs(entries: MissingInput[]): GroupedMissingInputs {
  const surfaced: MissingInput[] = [];
  const grouped: MissingInput[] = [];
  for (const entry of entries) {
    if (entry.criticality === "critical" || FEASIBILITY_RELEVANT_FIELDS.has(entry.field)) {
      surfaced.push(entry);
    } else {
      grouped.push(entry);
    }
  }
  return { surfaced, grouped, total: entries.length };
}
