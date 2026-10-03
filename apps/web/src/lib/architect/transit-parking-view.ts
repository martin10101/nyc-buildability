/**
 * Presentation view-model for the "Transit and parking zone" section of the parity
 * window (queue D-15 slice 2, plan §5a / §11b, queue item B-10, check C-8). Pure:
 * it reshapes an already-validated `TransitParking` document (the v1 wiring
 * contract, verified by the lane C adapter `transit-parking-api.ts`) into the rows
 * the section renders. It carries NO legal meaning and computes NOTHING: there is
 * deliberately no parking OUTCOME here (a number of spaces, a waiver or an
 * exemption is a rule-engine / legal determination made by Lane A and a qualified
 * reviewer at G6 — the contract has no slot for one, and this layer invents none).
 *
 * §5a rules this model serves:
 *  - item 5: the raw `status` / `source.kind` enum TOKENS never reach the face —
 *    `status` is mapped to the plain `status_label` vocabulary (`STATUS_HEADLINE`,
 *    one entry per schema enum value), and the structured provenance (dataset
 *    version, request url) is surfaced ONLY inside the "Source" disclosure (§5a
 *    item 4 "details");
 *  - item 3: a missing source is read as "Not available — <reason>", never a
 *    caution label dropped next to a number.
 *
 * The server authors two sentences that are shown VERBATIM on the face: `detail`
 * (the plan §5a "one line shown beside every option") and, when the zone is not
 * recorded, `missing_source`. Both are plain-English provenance text; neither is
 * re-worded here. Note that `detail` can cite the PLUTO dataset by name and id
 * ("PLUTO (64uk-42ks)") as part of that prose — that citation is the backend's,
 * shown verbatim, not a structured code this layer renders.
 */

import { boundedText } from "@/lib/bounded";
import type {
  TransitParking,
  TransitParkingSource,
  TransitParkingMissingSourceRef,
} from "@/lib/transit-parking-api";

export const TRANSIT_SECTION_TITLE = "Transit and parking zone";

/** The §5a wording for a zone the city source does not record yet (item 3):
 * "Not available — <reason>", in place of a value, never a caution next to one. */
export const NOT_AVAILABLE_PREFIX = "Not available — ";

/** The plain "not connected yet" copy for a 404 (the read route is unmounted / the
 * server flag is off), worded as a fact like the sibling parity empty state. */
export const TRANSIT_NOT_CONNECTED =
  "The transit and parking data service is not wired to this screen, so there is nothing to " +
  "show here. Nothing is guessed and no status is shown as confirmed.";

/**
 * Each schema `status` enum value mapped to the plain words shown as the headline.
 * This equals the contract's own `status_label` vocabulary (a test pins the
 * equality on both committed fixtures), so no value is invented. The exhaustive
 * `Record` means a new status enum member fails tsc here until it is mapped.
 */
export const STATUS_HEADLINE: Readonly<Record<TransitParking["status"], string>> = {
  recorded: "Recorded",
  check_needed: "Check needed",
};

/** The PLUTO provenance, shown only inside the "Source" disclosure (§5a item 4). */
export interface TransitSourceView {
  readonly dataset: string;
  readonly datasetVersion: string | null;
  readonly retrievedAt: string | null;
  readonly requestUrl: string | null;
}

/** One sub-dataset a single named "source to check" is composed of (contract
 * 1.1.0 missing_source_ref.components). Both fields are required in the contract. */
export interface TransitMissingSourceRefComponentView {
  readonly dataset: string;
  readonly datasetId: string;
}

/**
 * The structured reference for the source that still needs checking (contract
 * 1.1.0 `missing_source_ref`, request D-2 / D-090-R095). Shown ONLY inside the
 * "Source" disclosure: the face keeps the readable `missingSource` line, so the
 * §5a item-5 rule holds — the raw dataset id never reaches the face. Each
 * id/version/url is nulled when the source omits it, so the section states the
 * honest fact ("Not available …") rather than rendering an empty row.
 */
export interface TransitMissingSourceRefView {
  readonly dataset: string;
  readonly datasetId: string | null;
  readonly publisher: string | null;
  readonly datasetVersion: string | null;
  readonly url: string | null;
  readonly components: readonly TransitMissingSourceRefComponentView[];
}

export interface TransitParkingView {
  /** The plain status headline (`STATUS_HEADLINE[status]`, = the contract label). */
  readonly headline: string;
  /** The verbatim PLUTO transit-zone text when recorded; null when check_needed. */
  readonly zone: string | null;
  /** The server's verbatim one-line detail (plan §5a), shown on the face. */
  readonly detail: string;
  /** "Not available — <reason>" when a zone is not recorded; null otherwise. */
  readonly missingSource: string | null;
  /** Structured provenance, behind the "Source" disclosure; null when absent. */
  readonly source: TransitSourceView | null;
  /** The structured source-to-check reference, also behind the "Source"
   * disclosure; null when the document carries none (an absent or null
   * `missing_source_ref`, e.g. every recorded status). */
  readonly missingSourceRef: TransitMissingSourceRefView | null;
}

function sourceView(source: TransitParkingSource | null): TransitSourceView | null {
  if (source === null) return null;
  const datasetVersion = boundedText(source.dataset_version, "");
  const retrievedAt = boundedText(source.retrieved_at, "");
  const requestUrl = boundedText(source.query_ref, "");
  return {
    dataset: boundedText(source.dataset, "Recorded city dataset"),
    datasetVersion: datasetVersion === "" ? null : datasetVersion,
    retrievedAt: retrievedAt === "" ? null : retrievedAt,
    requestUrl: requestUrl === "" ? null : requestUrl,
  };
}

/**
 * Accept a source link ONLY if it is a well-formed absolute http(s) URL with no
 * embedded credentials; everything else → null, so the Link row is omitted exactly
 * as it is for a missing url. `boundedText` already caps length and strips control
 * characters, but it does NOT validate the scheme, so a server-supplied
 * `javascript:` / `data:` string would otherwise reach an href. This mirrors the
 * spirit of source-links.ts `officialZoningTextUrl` (parse with `new URL`, demand a
 * safe protocol, reject `user:pass@` credentials): a scheme the browser must not
 * navigate to never becomes a link.
 */
function safeHttpUrl(value: string): string | null {
  try {
    const url = new URL(value);
    if (url.protocol !== "http:" && url.protocol !== "https:") return null;
    if (url.username || url.password) return null;
    return value;
  } catch {
    return null;
  }
}

/**
 * Reshape the contract's `missing_source_ref` (absent or null → null) into the
 * disclosure view. Built with the same `boundedText` helper the source view uses,
 * so each reflected id/url is length-capped and control-stripped; an empty result
 * is nulled to an honest "Not available" row rather than a blank one, and the url is
 * additionally held to the http(s) safelist above before it can become an href.
 */
function missingSourceRefView(
  ref: TransitParkingMissingSourceRef | null | undefined,
): TransitMissingSourceRefView | null {
  if (ref === null || ref === undefined) return null;
  const datasetId = boundedText(ref.dataset_id, "");
  const publisher = boundedText(ref.publisher, "");
  const datasetVersion = boundedText(ref.dataset_version, "");
  const components = (ref.components ?? []).map((component) => ({
    dataset: boundedText(component.dataset, "Unnamed dataset"),
    datasetId: boundedText(component.dataset_id, "Unknown id"),
  }));
  return {
    dataset: boundedText(ref.dataset, "Unnamed dataset"),
    datasetId: datasetId === "" ? null : datasetId,
    publisher: publisher === "" ? null : publisher,
    datasetVersion: datasetVersion === "" ? null : datasetVersion,
    url: safeHttpUrl(boundedText(ref.url, "")),
    components,
  };
}

/** Reshape one validated transit/parking document into the section's view model. */
export function transitParkingView(status: TransitParking): TransitParkingView {
  const zone = boundedText(status.transit_zone, "");
  const missing = boundedText(status.missing_source, "");
  return {
    headline: STATUS_HEADLINE[status.status],
    zone: zone === "" ? null : zone,
    detail: boundedText(status.detail, "The transit and parking zone status is unavailable."),
    missingSource: missing === "" ? null : `${NOT_AVAILABLE_PREFIX}${missing}`,
    source: sourceView(status.source),
    missingSourceRef: missingSourceRefView(status.missing_source_ref),
  };
}
