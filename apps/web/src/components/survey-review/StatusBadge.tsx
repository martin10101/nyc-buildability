import type { StatusDisplay } from "@/lib/surveyReview/labels";

/**
 * Status badge for the survey-review screens (task M2-T016).
 *
 * Renders the full quadruple: LABEL + non-color SYMBOL + tone class + a
 * screen-reader GLOSS. Color (the tone class) is never the sole signal
 * (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md §8; accessibility §14).
 */
export function StatusBadge({
  display,
  testId,
}: {
  display: StatusDisplay;
  testId?: string;
}) {
  return (
    <span
      className={`sr-badge sr-tone-${display.tone}`}
      title={display.gloss}
      data-testid={testId}
    >
      <span aria-hidden="true" className="sr-badge-symbol">
        {display.symbol}
      </span>
      <span className="sr-badge-label">{display.label}</span>
      <span className="visually-hidden"> — {display.gloss}</span>
    </span>
  );
}
