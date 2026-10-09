/**
 * Runtime contract checks for the §8a hidden-issue-flags document (lane C packet
 * W2).
 *
 * Contract: packages/contracts/schemas/v1/hidden_issue_flags.schema.json and its
 * runtime guard services/api/app/contracts/study_contracts.py
 * (validate_hidden_issue_flags_document). The server already refuses to ship a
 * body that fails that guard (500 internal_contract_error); this is the CLIENT's
 * independent check, so a 200 body is never trusted until its shape is verified
 * (the condo-records / study-setup posture). Kept in its own module so the
 * transport adapter (hidden-issue-flags-api.ts) stays thin.
 *
 * NO legal meaning and NO zoning math live here: this only verifies the SHAPE of
 * the four §8a flag groups. A flag's `source` provenance is an open union
 * (a site_fact source, an engine-result provenance, or null) carried verbatim and
 * never read by the web, so it is checked for being an object-or-null only.
 */

import {
  Problems,
  checkBoundedArray,
  checkEnum,
  checkNonEmptyString,
  isRecord,
} from "./scenario-contract-checks";
import {
  checkBbl,
  checkNoFixtureAnnotation,
  checkNullableNonEmptyString,
  checkObject,
} from "./study/study-checks";

/** The only published hidden_issue_flags contract version (schema enum). */
export const HIDDEN_ISSUE_FLAGS_CONTRACT_VERSION = "1.0.0";

/** The four §8a group ids (schema `group_id` / `group` enums). */
export const HIDDEN_ISSUE_FLAG_GROUP_IDS = [
  "existing_building",
  "zoning_lot_history",
  "map_based_rules",
  "site_shape_and_street",
] as const;

/** The flag statuses (model.py STATUSES / schema `status` enum). */
export const HIDDEN_ISSUE_FLAG_STATUSES = [
  "flag",
  "opportunity",
  "check_needed",
  "not_flagged",
] as const;

/** The display label tied one-to-one to each status (model.py LABELS). */
export const HIDDEN_ISSUE_FLAG_STATUS_LABELS: Readonly<Record<string, string>> = {
  flag: "Flag",
  opportunity: "Opportunity",
  check_needed: "Check needed",
  not_flagged: "No flag",
};

const HIDDEN_ISSUE_FLAG_STATUS_LABEL_VALUES = ["Flag", "Opportunity", "Check needed", "No flag"];

/** The zoning-lot-history group is a reminder only (plan P-2): flag or check_needed. */
export const ZONING_LOT_HISTORY_GROUP_ID = "zoning_lot_history";
const ZONING_LOT_HISTORY_STATUSES = ["flag", "check_needed"];

export interface HiddenIssueFlagEvidence {
  readonly label: string;
  /** Open provenance union, carried verbatim and never read by the web. */
  readonly source: unknown;
}

export interface HiddenIssueFlag {
  readonly item_id: string;
  readonly group: string;
  readonly title: string;
  readonly status: string;
  readonly status_label: string;
  readonly detail: string;
  readonly typical_source: string;
  readonly evidence: HiddenIssueFlagEvidence[];
  readonly fact_refs: string[];
  readonly exception_label: string | null;
  readonly phase: string;
}

export interface HiddenIssueFlagGroup {
  readonly group_id: string;
  readonly title: string;
  readonly lot_bbl: string;
  readonly flags: HiddenIssueFlag[];
}

export interface HiddenIssueFlagsDocument {
  readonly contract_version: string;
  readonly groups: HiddenIssueFlagGroup[];
}

export type HiddenIssueFlagsValidation =
  | { ok: true; document: HiddenIssueFlagsDocument }
  | { ok: false; problems: string[] };

function checkEvidence(problems: Problems, path: string, value: unknown): void {
  const item = checkObject(problems, path, value);
  if (!item) return;
  checkNonEmptyString(problems, `${path}.label`, item.label);
  // `source` is anyOf[site_fact source, engine provenance, null]: an open object
  // or null, carried verbatim. A scalar is never a valid source.
  if (!(item.source === null || isRecord(item.source))) {
    problems.add(`${path}.source`, "must be a provenance object or null");
  }
}

function checkFlag(
  problems: Problems,
  path: string,
  value: unknown,
  enclosingGroupId: unknown,
): void {
  const flag = checkObject(problems, path, value);
  if (!flag) return;

  checkNonEmptyString(problems, `${path}.item_id`, flag.item_id);
  checkEnum(problems, `${path}.group`, flag.group, HIDDEN_ISSUE_FLAG_GROUP_IDS);
  // The item's group must equal its enclosing group (one group per flag).
  if (
    typeof flag.group === "string" &&
    typeof enclosingGroupId === "string" &&
    flag.group !== enclosingGroupId
  ) {
    problems.add(`${path}.group`, "must equal the enclosing group_id");
  }
  checkNonEmptyString(problems, `${path}.title`, flag.title);
  checkEnum(problems, `${path}.status`, flag.status, HIDDEN_ISSUE_FLAG_STATUSES);
  checkEnum(problems, `${path}.status_label`, flag.status_label, HIDDEN_ISSUE_FLAG_STATUS_LABEL_VALUES);
  // The label is tied one-to-one to the status (model.py LABELS).
  if (typeof flag.status === "string" && flag.status in HIDDEN_ISSUE_FLAG_STATUS_LABELS) {
    const expected = HIDDEN_ISSUE_FLAG_STATUS_LABELS[flag.status];
    if (flag.status_label !== expected) {
      problems.add(`${path}.status_label`, `must be "${expected}" for status "${flag.status}"`);
    }
  }
  // Plan P-2: the zoning-lot-history group is a reminder only, so its items are a
  // flag or 'Check needed', never opportunity or not_flagged - it never claims a
  // verified or combined zoning lot.
  if (
    enclosingGroupId === ZONING_LOT_HISTORY_GROUP_ID &&
    typeof flag.status === "string" &&
    !ZONING_LOT_HISTORY_STATUSES.includes(flag.status)
  ) {
    problems.add(
      `${path}.status`,
      "the zoning-lot-history group admits only 'flag' or 'check_needed' (plan P-2)",
    );
  }
  checkNonEmptyString(problems, `${path}.detail`, flag.detail);
  checkNonEmptyString(problems, `${path}.typical_source`, flag.typical_source);

  const evidence = checkBoundedArray(problems, `${path}.evidence`, flag.evidence);
  evidence?.forEach((item, index) => checkEvidence(problems, `${path}.evidence[${index}]`, item));

  const factRefs = checkBoundedArray(problems, `${path}.fact_refs`, flag.fact_refs);
  factRefs?.forEach((ref, index) =>
    checkNonEmptyString(problems, `${path}.fact_refs[${index}]`, ref),
  );

  checkNullableNonEmptyString(problems, `${path}.exception_label`, flag.exception_label);
  checkNonEmptyString(problems, `${path}.phase`, flag.phase);
}

function checkFlagGroup(problems: Problems, path: string, value: unknown): void {
  const group = checkObject(problems, path, value);
  if (!group) return;
  checkEnum(problems, `${path}.group_id`, group.group_id, HIDDEN_ISSUE_FLAG_GROUP_IDS);
  checkNonEmptyString(problems, `${path}.title`, group.title);
  checkBbl(problems, `${path}.lot_bbl`, group.lot_bbl);
  const flags = checkBoundedArray(problems, `${path}.flags`, group.flags);
  flags?.forEach((flag, index) =>
    checkFlag(problems, `${path}.flags[${index}]`, flag, group.group_id),
  );
}

/**
 * Validate a §8a hidden-issue-flags document against the W0 contract shape. On
 * success returns the typed envelope; otherwise a bounded list of problems. This
 * checks SHAPE only - no legal meaning is read.
 */
export function validateHiddenIssueFlagsDocument(body: unknown): HiddenIssueFlagsValidation {
  const problems = new Problems();
  const doc = checkObject(problems, "hidden_issue_flags", body);
  if (!doc) return { ok: false, problems: problems.list };
  checkNoFixtureAnnotation(problems, "hidden_issue_flags", doc);

  checkEnum(problems, "contract_version", doc.contract_version, [
    HIDDEN_ISSUE_FLAGS_CONTRACT_VERSION,
  ]);

  const groups = checkBoundedArray(problems, "groups", doc.groups);
  groups?.forEach((group, index) => checkFlagGroup(problems, `groups[${index}]`, group));

  if (problems.list.length > 0) return { ok: false, problems: problems.list };
  return { ok: true, document: doc as unknown as HiddenIssueFlagsDocument };
}
