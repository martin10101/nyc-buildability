/**
 * ZrSectionLinks (M5-T206; D-094 R027/R246) — presentational exact-section law links.
 *
 * Given a list of cited Zoning Resolution section labels, each label that resolves to a
 * captured section (via sectionUrl) renders as an anchor to that EXACT official section
 * (opening in a new tab); each label with no captured section renders as plain text (no
 * link, never the host homepage) — the same split the PDF shows. A blank or missing
 * citation renders nothing. This component computes no law: it only resolves labels through
 * the shared zr-section-urls resolver and shows the label verbatim.
 *
 * Grouped citations read like the PDF: the items are joined with the PDF's "; " separator
 * (nothing before the first or after the last), so adjacent links no longer run together
 * ("ZR 23-344(b)ZR 23-344(c)(3)" -> "ZR 23-344(b); ZR 23-344(c)(3)").
 *
 * Unmounted here by design — M5-T174 mounts it in the Results flow.
 */
import { Fragment, type ReactElement } from "react";

import { sectionUrl } from "@/lib/architect/zr-section-urls";

export interface ZrSectionLinksProps {
  /** Cited section labels, e.g. ["ZR 23-362", "ZR 11-25"]. Blank/missing entries are skipped. */
  citations?: readonly string[];
}

/** The PDF's citation separator, interleaved between rendered items. */
const CITATION_SEPARATOR = "; ";

/** A cited label is shown only when it carries visible section text. */
function visibleCitations(citations: readonly string[]): string[] {
  return citations.filter((label) => typeof label === "string" && label.trim() !== "");
}

export function ZrSectionLinks({ citations = [] }: ZrSectionLinksProps): ReactElement | null {
  const labels = visibleCitations(citations);
  if (labels.length === 0) {
    return null;
  }
  return (
    <span data-testid="zr-section-links">
      {labels.map((label, index) => {
        const href = sectionUrl(label);
        const key = `${label}-${index}`;
        const item = href ? (
          <a
            data-testid="zr-section-link"
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${label} (opens in a new tab)`}
          >
            {label}
          </a>
        ) : (
          <span data-testid="zr-section-plain">{label}</span>
        );
        // Interleave the PDF's "; " between items — skipped blanks never reach here, so
        // there is never a double separator, and none precedes the first or follows the last.
        return (
          <Fragment key={key}>
            {index > 0 && (
              <span data-testid="zr-section-separator" aria-hidden="true">
                {CITATION_SEPARATOR}
              </span>
            )}
            {item}
          </Fragment>
        );
      })}
    </span>
  );
}
