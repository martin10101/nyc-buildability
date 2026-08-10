"use client";

import { useMemo, useState } from "react";
import { confirmationDisplay } from "@/lib/surveyReview/labels";
import { factResolution, renderValue } from "@/lib/surveyReview/model";
import type { BoundingBox, FactView } from "@/lib/surveyReview/types";

/**
 * Original document page + overlay of extracted geometry (task M2-T016;
 * workflow §10.2). The overlay is a DOCUMENT ANNOTATION, never a georeferenced
 * map. Each detection is anchored to its `location.bounding_box` in its declared
 * `coordinate_space` (never guessed).
 *
 * F4: uncertain/conflicting marks carry a NON-COLOR cue (dashed stroke for a
 * conflict, dotted for an unresolved check) AND a small status glyph, in
 * addition to the tone color — status on the overlay is never by color alone.
 * Each mark also exposes its label/value/status as text (aria-label) and there
 * is a full text alt-summary below.
 */

const PAGE_FALLBACK_WIDTH = 612;
const PAGE_FALLBACK_HEIGHT = 792;

function toSvgRect(box: BoundingBox, pageHeight: number) {
  const width = Math.abs(box.x_max - box.x_min);
  const height = Math.abs(box.y_max - box.y_min);
  const x = Math.min(box.x_min, box.x_max);
  const yTop =
    box.coordinate_space === "raster_pixels"
      ? Math.min(box.y_min, box.y_max)
      : pageHeight - Math.max(box.y_min, box.y_max);
  return { x, y: yTop, width, height };
}

interface MarkStyle {
  tone: string;
  dash: string | undefined;
  glyph: string;
}

function markStyle(fact: FactView): MarkStyle {
  switch (factResolution(fact)) {
    case "conflict":
      return { tone: "conflict", dash: "6 3", glyph: "≠" };
    case "unresolved":
      return { tone: "caution", dash: "2 3", glyph: "?" };
    case "rejected":
      return { tone: "conflict", dash: "6 3", glyph: "✕" };
    case "confirmed":
      return { tone: "positive", dash: undefined, glyph: "✓" };
    default:
      return { tone: "info", dash: undefined, glyph: "◐" };
  }
}

export function DocumentOverlay({
  facts,
  pageNumber,
  imageRef,
  pageWidth,
  pageHeight,
  extractionAvailable,
  selectedEvidenceId,
  onSelect,
}: {
  facts: FactView[];
  pageNumber: number;
  imageRef: string | null;
  pageWidth: number | null;
  pageHeight: number | null;
  extractionAvailable: boolean;
  selectedEvidenceId: string | null;
  onSelect: (evidenceId: string) => void;
}) {
  const [showOnlyOpen, setShowOnlyOpen] = useState(false);

  const width = pageWidth ?? PAGE_FALLBACK_WIDTH;
  const height = pageHeight ?? PAGE_FALLBACK_HEIGHT;

  const pageFacts = useMemo(
    () => facts.filter((f) => (f.page_number ?? 1) === pageNumber),
    [facts, pageNumber],
  );
  const boxedFacts = useMemo(
    () => pageFacts.filter((f) => f.location?.kind === "bounding_box" && f.location.bounding_box),
    [pageFacts],
  );
  const visibleFacts = showOnlyOpen
    ? boxedFacts.filter((f) => {
        const r = factResolution(f);
        return r === "conflict" || r === "unresolved" || r === "unconfirmed";
      })
    : boxedFacts;

  if (!extractionAvailable) {
    return (
      <section className="sr-overlay" aria-label="Original document" data-testid="overlay-unavailable">
        <div className="sr-overlay-canvas sr-overlay-empty">
          <p className="section-note">
            Extraction is temporarily unavailable, so this document is stored
            safely and unprocessed. No overlay or extracted facts are shown —
            nothing is fabricated. The document rests in its uploaded state.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="sr-overlay" aria-label={`Original document, page ${pageNumber}, with extracted-geometry overlay`}>
      <div className="sr-overlay-toolbar">
        <span className="section-note" data-testid="overlay-page-label">
          Page {pageNumber} — extracted-geometry annotation (not a georeferenced map)
        </span>
        <label className="sr-overlay-toggle">
          <input
            type="checkbox"
            checked={showOnlyOpen}
            onChange={(e) => setShowOnlyOpen(e.target.checked)}
            data-testid="overlay-toggle-open"
          />{" "}
          Show only open items
        </label>
      </div>

      <div className="sr-overlay-canvas" data-testid="overlay-canvas">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="sr-overlay-svg"
          role="group"
          aria-label={`Extracted-geometry overlay for page ${pageNumber}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {imageRef ? (
            <image href={imageRef} x={0} y={0} width={width} height={height} />
          ) : (
            <rect x={0} y={0} width={width} height={height} className="sr-overlay-page" />
          )}
          {visibleFacts.map((f) => {
            const box = f.location!.bounding_box as BoundingBox;
            const rect = toSvgRect(box, height);
            const selected = f.evidence_id === selectedEvidenceId;
            const style = markStyle(f);
            return (
              <g key={f.evidence_id}>
                <rect
                  x={rect.x}
                  y={rect.y}
                  width={rect.width}
                  height={rect.height}
                  strokeDasharray={style.dash}
                  className={`sr-overlay-mark sr-tone-${style.tone}${selected ? " sr-overlay-mark-selected" : ""}`}
                  tabIndex={0}
                  role="button"
                  aria-pressed={selected}
                  aria-label={`${f.display_label}: ${renderValue(f.normalized_value)}${f.units ? ` ${f.units}` : ""}. ${confirmationDisplay(f.confirmation_state).label}. Select to focus.`}
                  data-testid={`overlay-mark-${f.evidence_id}`}
                  onClick={() => onSelect(f.evidence_id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onSelect(f.evidence_id);
                    }
                  }}
                />
                <text
                  x={rect.x + 2}
                  y={rect.y + 12}
                  className={`sr-overlay-glyph sr-tone-${style.tone}`}
                  aria-hidden="true"
                  data-testid={`overlay-glyph-${f.evidence_id}`}
                >
                  {style.glyph}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <details className="sr-overlay-altsummary" data-testid="overlay-alt-summary">
        <summary>Text summary of the overlay findings</summary>
        <ul className="sr-alt-list">
          {pageFacts.map((f) => {
            const confirmation = confirmationDisplay(f.confirmation_state);
            const resolution = factResolution(f);
            return (
              <li key={f.evidence_id}>
                <strong>{f.display_label}</strong>: {renderValue(f.normalized_value)}
                {f.units ? ` ${f.units}` : ""} — {confirmation.label}
                {resolution === "conflict" ? " — has a data conflict" : ""}
                {resolution === "unresolved" ? " — has an unresolved check" : ""}
                {f.location?.kind === "vector_object" ? " (located by vector object reference)" : ""}
              </li>
            );
          })}
          {pageFacts.length === 0 ? <li>No extracted facts on this page.</li> : null}
        </ul>
      </details>
    </section>
  );
}
