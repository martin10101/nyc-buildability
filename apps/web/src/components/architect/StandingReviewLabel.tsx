"use client";
import { useId } from "react";
import {
  STANDING_REVIEW_BODY,
  STANDING_REVIEW_HEADING,
} from "@/lib/disclaimer";

/**
 * The one standing "not reviewed" label (owner decision D-090-R164/R165, source-027;
 * ADR-007). Rendered ONCE at the top of every architect surface that shows numbers
 * (dashboard, property screen, report preview and print view), never per card.
 *
 * It is a plain-text note: a short heading plus two sentences stating that the numbers are
 * computed from official sources, are not reviewed by a licensed professional, and must be
 * verified by one before reliance. Status is carried by the TEXT (the heading), not colour.
 * It is a `role="note"` with an accessible name, visible without a tap (not behind a
 * disclosure), readable at >= 14 px (see architect.css), and present in the print stylesheet.
 *
 * It is NOT dismissible and stores nothing: "one time" means one label, shown always, not
 * one viewing. The wording lives in `@/lib/disclaimer` so every surface shares one source.
 *
 * `className` lets a surface add a hook class (e.g. the dashboard screen banner, which the
 * dashboard print stylesheet hides so the printed brief shows only ReportView's copy).
 */
export function StandingReviewLabel({ className }: { className?: string }) {
  const headingId = useId();
  return (
    <section
      className={className ? `standing-review-label ${className}` : "standing-review-label"}
      role="note"
      aria-labelledby={headingId}
      data-testid="standing-review-label"
    >
      <strong id={headingId} className="standing-review-label__heading">
        {STANDING_REVIEW_HEADING}
      </strong>
      <p className="standing-review-label__body">{STANDING_REVIEW_BODY}</p>
    </section>
  );
}
