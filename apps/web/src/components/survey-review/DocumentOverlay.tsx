"use client";

import { useMemo, useState } from "react";
import { confirmationDisplay } from "@/lib/surveyReview/labels";
import { factResolution, renderValue } from "@/lib/surveyReview/model";
import type { BoundingBox, ReviewFact } from "@/lib/surveyReview/types";

/**
 * Original document page + overlay of extracted geometry (task M2-T016;
 * workflow §10.2). The overlay is a DOCUMENT ANNOTATION, never a georeferenced
 * map — page space is never presented as survey/world coordinates. Each
 * detection is anchored to its evidence `location.bounding_box` in its declared
 * `coordinate_space` (never guessed). Uncertain / conflicting detections are
 * marked distinctly AND labeled in text (never color alone).
 *
 * B-001 honesty: production storage is unprovisioned, so a page image may be
 * absent (`image_ref === null`). The overlay then renders a neutral page
 * schematic (clearly labeled) with the annotations still anchored — it never
 * fabricates a document image.
 */

const PAGE_FALLBACK_WIDTH = 800;
const PAGE_FALLBACK_HEIGHT = 1035;

function toSvgRect(
  box: BoundingBox,
  pageHeight: number,
): { x: number; y: number; width: number; height: number } {
  const width = Math.abs(box.x_max - box.x_min);
  const height = Math.abs(box.y_max - box.y_min);
  const x = Math.min(box.x_min, box.x_max);
  // raster_pixels: origin top-left, y down → SVG maps directly.
  // pdf_user_space_points: origin lower-left, y up → flip into SVG (y down).
  const yTop =
    box.coordinate_space === "raster_pixels"
      ? Math.min(box.y_min, box.y_max)
      : pageHeight - Math.max(box.y_min, box.y_max);
  return { x, y: yTop, width, height };
}

function toneForResolution(fact: ReviewFact): string {
  const resolution = factResolution(fact);
  if (resolution === "conflict") return "conflict";
  if (resolution === "unresolved") return "caution";
  if (resolution === "rejected") return "conflict";
  if (resolution === "confirmed") return "positive";
  return "info";
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
  facts: ReviewFact[];
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
    () => facts.filter((f) => f.fact.page_number === pageNumber),
    [facts, pageNumber],
  );
  const boxedFacts = useMemo(
    () =>
      pageFacts.filter(
        (f) => f.fact.location.kind === "bounding_box" && f.fact.location.bounding_box,
      ),
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
          {/* Neutral page schematic when no rendered image is available. */}
          {imageRef ? (
            <image href={imageRef} x={0} y={0} width={width} height={height} />
          ) : (
            <rect x={0} y={0} width={width} height={height} className="sr-overlay-page" />
          )}
          {visibleFacts.map((f) => {
            const box = f.fact.location.bounding_box as BoundingBox;
            const rect = toSvgRect(box, height);
            const selected = f.fact.evidence_id === selectedEvidenceId;
            return (
              <rect
                key={f.fact.evidence_id}
                x={rect.x}
                y={rect.y}
                width={rect.width}
                height={rect.height}
                className={`sr-overlay-mark sr-tone-${toneForResolution(f)}${selected ? " sr-overlay-mark-selected" : ""}`}
                tabIndex={0}
                role="button"
                aria-pressed={selected}
                aria-label={`${f.display_label}: ${renderValue(f.fact.normalized_value)}${f.fact.units ? ` ${f.fact.units}` : ""}. ${confirmationDisplay(f.fact.professional_confirmation.state).label}. Select to focus.`}
                data-testid={`overlay-mark-${f.fact.evidence_id}`}
                onClick={() => onSelect(f.fact.evidence_id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelect(f.fact.evidence_id);
                  }
                }}
              />
            );
          })}
        </svg>
      </div>

      {/* Non-visual equivalent of the overlay (accessibility §10.9). */}
      <details className="sr-overlay-altsummary" data-testid="overlay-alt-summary">
        <summary>Text summary of the overlay findings</summary>
        <ul className="sr-alt-list">
          {pageFacts.map((f) => {
            const confirmation = confirmationDisplay(f.fact.professional_confirmation.state);
            const resolution = factResolution(f);
            return (
              <li key={f.fact.evidence_id}>
                <strong>{f.display_label}</strong>: {renderValue(f.fact.normalized_value)}
                {f.fact.units ? ` ${f.fact.units}` : ""} — {confirmation.label}
                {resolution === "conflict" ? " — has a data conflict" : ""}
                {resolution === "unresolved" ? " — has an unresolved check" : ""}
                {f.fact.location.kind === "vector_object"
                  ? " (located by vector object reference)"
                  : ""}
              </li>
            );
          })}
          {pageFacts.length === 0 ? <li>No extracted facts on this page.</li> : null}
        </ul>
      </details>
    </section>
  );
}
