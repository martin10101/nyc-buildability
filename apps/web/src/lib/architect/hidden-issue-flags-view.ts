/**
 * Presentation view-model for the §8a hidden-issue flags (queue D-12, plan M2-06 /
 * L-11, §8a). Pure: it reshapes an already-validated `HiddenIssueFlagsDocument`
 * (the W0 contract, verified by hidden-issue-flags-contract-checks) into the rows
 * the "Hidden issues" panel renders. It carries NO legal meaning and computes
 * nothing about the law — the §8a layer only reports what the sourced data shows,
 * or says the source is not available. What any rule requires is the rule engine's
 * and a qualified reviewer's, never the web's.
 *
 * §5a rules this model serves:
 *  - item 1/6: one status strip of at most three short items (`flagStripSummary`);
 *  - item 5: no internal codes on the face — the item_id, group id token, raw
 *    `<bbl>:<field>` fact_ref and the source `kind`/query tokens never become
 *    visible text here (item_id/group are keys only; a fact_ref is shown as plain
 *    words via `humanFactName`); the evidence `source` dataset ids and timestamps
 *    are surfaced only as the "Source" disclosure content (§5a item 4 "details").
 *
 * "No flag" honesty (B-09 reviews N1/N6): `not_flagged` is read as the SPECIFIC
 * check's result ("This check found nothing to flag."), never an overall clean
 * bill for the property — `NOT_A_CLEAN_BILL_NOTE` states this on the panel, and
 * the strip never asserts "no issues".
 */

import {
  HIDDEN_ISSUE_FLAG_GROUP_IDS,
  type HiddenIssueFlag,
  type HiddenIssueFlagEvidence,
  type HiddenIssueFlagGroup,
  type HiddenIssueFlagsDocument,
} from "@/lib/hidden-issue-flags-contract-checks";

/** §5a items 1 and 6: at most three items on the strip / notices on screen. */
export const FLAG_STRIP_LIMIT = 3;

/** What each status means for ONE check, in plain words. `not_flagged` reads as a
 * specific result, never an all-clear for the property (B-09 N1/N6). */
export const STATUS_MEANINGS: Readonly<Record<string, string>> = {
  flag: "This check found something to look at.",
  opportunity: "This check found a possible gain.",
  check_needed: "This check could not be answered from the data on file.",
  not_flagged: "This check found nothing to flag.",
};

/** Panel note that keeps "No flag" honest: each line is one specific check. */
export const NOT_A_CLEAN_BILL_NOTE =
  "Each line below is one specific check. “No flag” means that check found nothing — " +
  "it is not an all-clear for the property, and the list is not exhaustive.";

/** Panel note for "beside the affected results": placement waits on the numbers. */
export const BESIDE_RESULTS_NOTE =
  "When the development numbers are shown, each flag tied to a result will appear beside that " +
  "result. Until then every flag is shown here, in its group.";

/** Panel note: these checks run on every property; more depend on connected data. */
export const EVERY_PROPERTY_NOTE =
  "These checks run on every property. Which ones can be answered depends on the connected data " +
  "and rules; the rest stay “Check needed”.";

/** One evidence input as the "Source" disclosure shows it (§5a item 4 details). */
export interface EvidenceView {
  readonly label: string;
  /** Plain source lines; empty when the input carries no dataset. */
  readonly sourceLines: string[];
  readonly hasSource: boolean;
}

/** One §8a item as the panel renders it. */
export interface FlagView {
  /** Stable key for React / data-testid only — NEVER shown (it is an internal code). */
  readonly key: string;
  readonly title: string;
  readonly status: string;
  readonly statusLabel: string;
  readonly statusMeaning: string;
  readonly detail: string;
  readonly typicalSource: string;
  /** "Relates to: <plain fact names>." for a flag with a fact_ref, else null. */
  readonly relation: string | null;
  /** A results exception to read a future number by (e.g. "Out of date"), or null. */
  readonly exceptionLabel: string | null;
  readonly evidence: EvidenceView[];
}

/** One §8a group as the panel renders it. */
export interface GroupView {
  /** Group id — key only, never shown. */
  readonly key: string;
  readonly title: string;
  readonly flags: FlagView[];
}

export interface FlagStripSummary {
  /** At most three short items for the one status strip line. */
  readonly items: string[];
  readonly counts: {
    flag: number;
    opportunity: number;
    check_needed: number;
    not_flagged: number;
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.trim() !== "" ? value : null;
}

/** A fact_ref is the internal token "<bbl>:<field>"; show only the field, as plain
 * words, so no internal code reaches the face (§5a item 5). */
export function humanFactName(ref: string): string {
  const field = ref.includes(":") ? ref.slice(ref.indexOf(":") + 1) : ref;
  return field.replace(/_/g, " ").trim();
}

export function factRelationText(flag: HiddenIssueFlag): string | null {
  if (flag.fact_refs.length === 0) return null;
  const names = flag.fact_refs.map(humanFactName).filter((name) => name !== "");
  if (names.length === 0) return null;
  return `Relates to: ${names.join(", ")}.`;
}

/** Plain lines for one evidence input's provenance, shown only in the "Source"
 * disclosure. Known plain fields only — the raw `kind`, `query_ref` and
 * `document_ref` tokens are never surfaced (they are internal codes). */
export function evidenceView(evidence: HiddenIssueFlagEvidence): EvidenceView {
  const label = evidence.label;
  const source = evidence.source;
  if (!isRecord(source)) {
    return { label, sourceLines: ["No dataset is connected for this input."], hasSource: false };
  }
  const lines: string[] = [];
  const statement = asString(source.statement);
  const dataset = asString(source.dataset);
  const datasetVersion = asString(source.dataset_version);
  const retrievedAt = asString(source.retrieved_at);
  if (statement) lines.push(`Note: ${statement}`);
  if (dataset) lines.push(datasetVersion ? `Dataset: ${dataset} (${datasetVersion})` : `Dataset: ${dataset}`);
  if (retrievedAt) lines.push(`Recorded: ${retrievedAt}`);
  if (lines.length === 0) lines.push("Source on file.");
  return { label, sourceLines: lines, hasSource: true };
}

export function flagView(flag: HiddenIssueFlag): FlagView {
  return {
    key: flag.item_id,
    title: flag.title,
    status: flag.status,
    statusLabel: flag.status_label,
    statusMeaning: STATUS_MEANINGS[flag.status] ?? "",
    detail: flag.detail,
    typicalSource: flag.typical_source,
    relation: factRelationText(flag),
    exceptionLabel: flag.exception_label,
    evidence: flag.evidence.map(evidenceView),
  };
}

type GroupId = (typeof HIDDEN_ISSUE_FLAG_GROUP_IDS)[number];

function groupOrder(id: string): number {
  const index = HIDDEN_ISSUE_FLAG_GROUP_IDS.indexOf(id as GroupId);
  return index === -1 ? HIDDEN_ISSUE_FLAG_GROUP_IDS.length : index;
}

/** The document's groups in the canonical §8a order; a document may carry a subset. */
export function orderedGroups(doc: HiddenIssueFlagsDocument): HiddenIssueFlagGroup[] {
  return [...doc.groups].sort((a, b) => groupOrder(a.group_id) - groupOrder(b.group_id));
}

export function groupViews(doc: HiddenIssueFlagsDocument): GroupView[] {
  return orderedGroups(doc).map((group) => ({
    key: group.group_id,
    title: group.title,
    flags: group.flags.map(flagView),
  }));
}

/** The one §5a status strip: at most three short items. Only the categories that
 * are actually present show, so it never asserts "no issues"; when every check is
 * `not_flagged` it states that each check carries its own result. */
export function flagStripSummary(doc: HiddenIssueFlagsDocument): FlagStripSummary {
  const counts = { flag: 0, opportunity: 0, check_needed: 0, not_flagged: 0 };
  for (const group of doc.groups) {
    for (const flag of group.flags) {
      switch (flag.status) {
        case "flag":
          counts.flag += 1;
          break;
        case "opportunity":
          counts.opportunity += 1;
          break;
        case "check_needed":
          counts.check_needed += 1;
          break;
        case "not_flagged":
          counts.not_flagged += 1;
          break;
      }
    }
  }
  const items: string[] = [];
  if (counts.flag) items.push(`${counts.flag} ${counts.flag === 1 ? "flag" : "flags"}`);
  if (counts.opportunity) {
    items.push(`${counts.opportunity} ${counts.opportunity === 1 ? "opportunity" : "opportunities"}`);
  }
  if (counts.check_needed) items.push(`${counts.check_needed} to check`);
  if (items.length === 0) items.push("Each check below shows its own result");
  return { items: items.slice(0, FLAG_STRIP_LIMIT), counts };
}
