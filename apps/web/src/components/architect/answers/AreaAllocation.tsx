import type { CSSProperties } from "react";
import {
  AREA_ILLUSTRATION_CAPTION,
  AREA_MEASURE_WORDS,
  AREA_ZONE_APARTMENT,
  AREA_ZONE_OTHER,
  PHYSICAL_PLATE_NOT_CHECKED,
} from "@/lib/architect/area-allocation-tokens";
import { areaAllocationView } from "@/lib/architect/area-allocation";

/**
 * The two-zone area illustration (M5-T187; owner H1, D-094 R087-R098, G-14).
 *
 * It renders what the selector (area-allocation.ts) returns for ONE 1.5.0
 * `area_allocation` block — never a figure of its own:
 *
 *   • NOT fitted -> a single proportional bar split by the apartment share, one
 *     stated percentage beside it, the two fixed-wording zone labels, the one
 *     caption, and the conversion statement in expandable detail (R094/R095);
 *   • FITTED -> a marked placeholder; the zones-in-footprint drawing lands with
 *     the PDF scenario sheet (Part B / M5-T173), so the website never shows an
 *     illustration the PDF lacks (R096);
 *   • a garbled / inconsistent / out-of-range block -> an explicit unavailable
 *     line with the selector's plain reason (no default stands for a fact).
 *
 * It shows no rooms, unit walls, apartment counts, stairs or elevators (R093).
 * The two zones share one neutral fill and are told apart by a hatch, not by
 * colour (presentation contract). This component is NOT mounted on any default
 * route in this part; Part B mounts it in lockstep with the PDF illustration.
 */

/** The marked placeholder shown while the fitted zones-in-footprint drawing is deferred (R094/R096). */
const FITTED_DEFERRED_LINE =
  "The two-zone illustration inside the fitted footprint is not shown here yet.";

const INK = "var(--pt-color-ink)";
const OUTLINE = "var(--pt-color-supporting)";
const ZONE_FILL = "var(--pt-color-selected)";
const LABEL_SIZE = "var(--pt-type-drawing-label-size, 14px)";

/** A neutral fill overlaid with parallel hatch lines at `angle` degrees — the kernel's hatch idea in
 * CSS, so the two zones differ by pattern and never by colour alone. */
function hatchStyle(angle: number): CSSProperties {
  return {
    backgroundColor: ZONE_FILL,
    backgroundImage: `repeating-linear-gradient(${angle}deg, ${INK}, ${INK} 0.75px, transparent 0.75px, transparent 5px)`,
  };
}

export function AreaAllocation({
  allocation,
  placement,
}: {
  allocation: unknown;
  placement?: unknown;
}) {
  const view = areaAllocationView(allocation, placement);

  if (view.kind === "unavailable") {
    return (
      <section
        className="aa-illustration"
        data-testid="area-allocation"
        aria-label="Area allocation illustration"
      >
        <p className="aa-unavailable" data-testid="area-allocation-unavailable">
          {view.reason}
        </p>
      </section>
    );
  }

  if (view.kind === "fitted_deferred") {
    return (
      <section
        className="aa-illustration"
        data-testid="area-allocation"
        aria-label="Area allocation illustration"
      >
        <p className="aa-deferred" data-testid="area-allocation-fitted-deferred">
          {FITTED_DEFERRED_LINE}
        </p>
      </section>
    );
  }

  // Width strings formatted to drop binary-float noise (0.65 * 100 is 65.00000000000001).
  const widthPercent = (fraction: number): string => `${Number((fraction * 100).toFixed(4))}%`;
  const apartmentWidth = widthPercent(view.apartmentFraction);
  const otherWidth = widthPercent(1 - view.apartmentFraction);
  return (
    <section
      className="aa-illustration"
      data-testid="area-allocation"
      aria-label="Area allocation illustration"
    >
      <p className="aa-percentage" data-testid="area-allocation-percentage">
        {`${view.percent}% apartment area`}
      </p>
      <div
        className="aa-bar"
        role="img"
        data-testid="area-allocation-bar"
        data-apartment-fraction={view.apartmentFraction}
        aria-label={`Proportional bar: ${view.percent}% ${AREA_ZONE_APARTMENT}; the remainder is ${AREA_ZONE_OTHER}`}
        style={{
          display: "flex",
          width: "100%",
          maxWidth: "320px",
          height: "44px",
          border: `1px solid ${OUTLINE}`,
          overflow: "hidden",
        }}
      >
        <span
          className="aa-bar-apartment"
          data-role="area_bar_apartment"
          style={{ width: apartmentWidth, ...hatchStyle(45) }}
        />
        <span
          className="aa-bar-other"
          data-role="area_bar_other"
          style={{
            width: otherWidth,
            borderLeft: `1px solid ${OUTLINE}`,
            ...hatchStyle(135),
          }}
        />
      </div>
      <ul className="aa-legend" data-testid="area-allocation-legend" style={{ listStyle: "none", padding: 0 }}>
        <li className="aa-legend-item" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span
            className="aa-swatch"
            data-role="area_swatch_apartment"
            aria-hidden="true"
            style={{ width: "12px", height: "12px", border: `1px solid ${OUTLINE}`, ...hatchStyle(45) }}
          />
          <span data-testid="area-allocation-label-apartment" style={{ fontSize: LABEL_SIZE }}>
            {AREA_ZONE_APARTMENT}
          </span>
        </li>
        <li className="aa-legend-item" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span
            className="aa-swatch"
            data-role="area_swatch_other"
            aria-hidden="true"
            style={{ width: "12px", height: "12px", border: `1px solid ${OUTLINE}`, ...hatchStyle(135) }}
          />
          <span data-testid="area-allocation-label-other" style={{ fontSize: LABEL_SIZE }}>
            {AREA_ZONE_OTHER}
          </span>
        </li>
      </ul>
      <p className="aa-caption" data-testid="area-allocation-caption" style={{ fontSize: LABEL_SIZE }}>
        {AREA_ILLUSTRATION_CAPTION}
      </p>
      <details className="aa-methodology" data-testid="area-allocation-methodology">
        <summary data-testid="area-allocation-methodology-summary">How this illustration is worked out</summary>
        <p data-testid="area-allocation-measure">{`Measure: ${AREA_MEASURE_WORDS}`}</p>
        <p data-testid="area-allocation-conversion">{view.conversionStatement}</p>
        <p className="aa-not-checked">
          {"Not checked: "}
          <span data-testid="area-allocation-not-checked">{PHYSICAL_PLATE_NOT_CHECKED}</span>
        </p>
      </details>
    </section>
  );
}
