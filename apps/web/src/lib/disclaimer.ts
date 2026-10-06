/**
 * Required disclaimer (PRD section 29). Must be displayed prominently in the
 * application and in reports.
 */
export const REQUIRED_DISCLAIMER =
  "This platform provides preliminary development and zoning feasibility " +
  "information based on available public records, user-provided assumptions, " +
  "and the platform’s current rule coverage. It is not a legal opinion, " +
  "architectural or engineering certification, DOB determination, permit " +
  "approval, or guarantee that a proposed development will be approved. " +
  "Results must be reviewed by qualified New York professionals before " +
  "reliance, acquisition, design, filing, financing, or construction.";

/**
 * Standing "not reviewed" label (owner decision D-090-R164/R165, source-027; ADR-007).
 *
 * One plain-language label, shown once and always at the top of every surface that
 * shows numbers (dashboard, property screen, report preview and print). It carries the
 * three facts the owner settled: the results are computed from official sources, they are
 * not reviewed by a licensed professional, and they must be verified by one before any
 * reliance. It is NOT dismissible and holds no state.
 *
 * This is distinct from REQUIRED_DISCLAIMER (PRD section 29): that stays the formal legal
 * disclaimer in the global footer and is unchanged. The owner asked for plain human
 * language here, so this label uses plain wording and deliberately avoids "complies",
 * "approved" and "guaranteed" (and the section-29 jargon) rather than reusing section 29
 * verbatim, which carries those exact words. No legal logic lives here: the text is fixed.
 */
export const STANDING_REVIEW_HEADING = "Not reviewed by a licensed professional";
export const STANDING_REVIEW_SENTENCE_1 =
  "These results are computed from official city data and the Zoning Resolution text " +
  "linked beside each value.";
export const STANDING_REVIEW_SENTENCE_2 =
  "They are not reviewed by a licensed architect, engineer or attorney, so verify with " +
  "one before you rely on them or file plans.";
/** The two sentences as one body string, in order. */
export const STANDING_REVIEW_BODY = `${STANDING_REVIEW_SENTENCE_1} ${STANDING_REVIEW_SENTENCE_2}`;
