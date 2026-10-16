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
 * Unmounted here by design — M5-T174 mounts it in the Results flow.
 */
import type { ReactElement } from "react";

import { sectionUrl } from "@/lib/architect/zr-section-urls";

export interface ZrSectionLinksProps {
  /** Cited section labels, e.g. ["ZR 23-362", "ZR 11-25"]. Blank/missing entries are skipped. */
  citations?: readonly string[];
}

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
        if (href) {
          return (
            <a
              key={key}
              data-testid="zr-section-link"
              href={href}
              target="_blank"
              rel="noopener noreferrer"
            >
              {label}
            </a>
          );
        }
        return (
          <span key={key} data-testid="zr-section-plain">
            {label}
          </span>
        );
      })}
    </span>
  );
}
