import { type CSSProperties, useId } from "react";
import {
  AREA_ILLUSTRATION_CAPTION,
  AREA_MEASURE_WORDS,
  AREA_ZONE_APARTMENT,
  AREA_ZONE_OTHER,
  PHYSICAL_PLATE_NOT_CHECKED,
} from "@/lib/architect/area-allocation-tokens";
import { type AreaPoint, type AreaZonesView, areaAllocationView } from "@/lib/architect/area-allocation";

/**
 * The two-zone area illustration (M5-T187; fitted branch M5-T202 part B2a; owner
 * H1, D-094 R087-R098, G-14).
 *
 * It renders what the selector (area-allocation.ts) returns for ONE 1.5.0
 * `area_allocation` block — never a figure of its own:
 *
 *   • NOT fitted -> a single proportional bar split by the apartment share, one
 *     stated percentage beside it, the two fixed-wording zone labels, the one
 *     caption, and the conversion statement in expandable detail (R094/R095);
 *   • FITTED (placed on the lot with a drawable outline) -> the two zones inside
 *     that footprint, split by one vertical division at the share ratio — the
 *     geometry the PDF kernel computes, so the website and the PDF split the
 *     footprint identically (R088/R091/R096); the two zones share one neutral fill
 *     and are told apart by a hatch, not by colour; the only line inside the
 *     footprint is the single proportional division;
 *   • a garbled / inconsistent / out-of-range block, or a placed outline the
 *     kernel cannot draw truthfully -> an explicit unavailable line with the
 *     selector's plain reason (no default stands for a fact).
 *
 * It shows no rooms, unit walls, apartment counts, stairs or elevators (R093).
 * This component is NOT mounted on any default route in this part; a later part
 * mounts it per worked building in lockstep with the PDF illustration.
 */

const INK = "var(--pt-color-ink)";
const OUTLINE = "var(--pt-color-supporting)";
const ZONE_FILL = "var(--pt-color-selected)";
const LABEL_SIZE = "var(--pt-type-drawing-label-size, 14px)";

/** The kernel's placed scale: the footprint's longer side fills this many user units. */
const FP_SPAN = 196;
/** Hatch geometry at that scale — identical to the kernel (_HATCH_SPACING / _HATCH_WEIGHT). */
const HATCH_SPACING = 5;
const HATCH_WEIGHT = 0.5;

/** A neutral fill overlaid with parallel hatch lines at `angle` degrees — the kernel's hatch idea in
 * CSS, so the two zones differ by pattern and never by colour alone (bar branch). */
function hatchStyle(angle: number): CSSProperties {
  return {
    backgroundColor: ZONE_FILL,
    backgroundImage: `repeating-linear-gradient(${angle}deg, ${INK}, ${INK} 0.75px, transparent 0.75px, transparent 5px)`,
  };
}

/** Drop binary-float noise from an SVG coordinate (0.1 * 3 is 0.30000000000000004). */
function fmt(value: number): string {
  return Number(value.toFixed(3)).toString();
}

/** The legend, caption and expandable methodology, shared by the bar and the zones (kernel `_footer`). */
function IllustrationFooter({ conversionStatement }: { conversionStatement: string }) {
  return (
    <>
      <ul
        className="aa-legend"
        data-testid="area-allocation-legend"
        style={{ listStyle: "none", padding: 0 }}
      >
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
        <p data-testid="area-allocation-conversion">{conversionStatement}</p>
        <p className="aa-not-checked">
          {"Not checked: "}
          <span data-testid="area-allocation-not-checked">{PHYSICAL_PLATE_NOT_CHECKED}</span>
        </p>
      </details>
    </>
  );
}

/** The two zones inside the placed footprint, as an SVG (the kernel's `_draw_zones` in the browser). */
function ZonesDrawing({ view }: { view: AreaZonesView }) {
  const raw = useId();
  const uid = raw.replace(/[^a-zA-Z0-9_-]/g, "");
  const apartmentPattern = `aa-hatch-apartment-${uid}`;
  const otherPattern = `aa-hatch-other-${uid}`;

  const { minX, maxX, minY, maxY } = view.bounds;
  const spanX = maxX - minX;
  const spanY = maxY - minY;
  const span = Math.max(spanX, spanY);
  const k = span > 0 ? FP_SPAN / span : 1;
  // Place a footprint point: scale to the kernel's span and flip y (SVG y points down).
  const place = (p: AreaPoint): [number, number] => [(p[0] - minX) * k, (maxY - p[1]) * k];
  const polyPath = (poly: readonly AreaPoint[]): string =>
    `${poly
      .map((p, i) => {
        const [x, y] = place(p);
        return `${i === 0 ? "M" : "L"}${fmt(x)} ${fmt(y)}`;
      })
      .join(" ")} Z`;

  const apartmentD = polyPath(view.apartmentPolygon);
  const otherD = polyPath(view.otherPolygon);
  const ringD = polyPath(view.ring);
  const [dx1, dy1] = place([view.divisionX, view.divisionYLo]);
  const [dx2, dy2] = place([view.divisionX, view.divisionYHi]);

  const vbW = spanX * k;
  const vbH = spanY * k;

  return (
    <svg
      className="aa-zones"
      role="img"
      data-testid="area-allocation-zones"
      data-apartment-fraction={view.apartmentFraction}
      data-division-x={view.divisionX}
      viewBox={`0 0 ${fmt(vbW)} ${fmt(vbH)}`}
      style={{ display: "block", width: "100%", maxWidth: "320px", height: "auto", overflow: "visible" }}
      aria-label={`Two zones inside the placed footprint: ${view.percent}% ${AREA_ZONE_APARTMENT}; the remainder is ${AREA_ZONE_OTHER}`}
    >
      <defs>
        <pattern
          id={apartmentPattern}
          patternUnits="userSpaceOnUse"
          width={HATCH_SPACING}
          height={HATCH_SPACING}
          patternTransform="rotate(-45)"
        >
          <line
            x1={0}
            y1={HATCH_SPACING / 2}
            x2={HATCH_SPACING}
            y2={HATCH_SPACING / 2}
            stroke={INK}
            strokeWidth={HATCH_WEIGHT}
          />
        </pattern>
        <pattern
          id={otherPattern}
          patternUnits="userSpaceOnUse"
          width={HATCH_SPACING}
          height={HATCH_SPACING}
          patternTransform="rotate(-135)"
        >
          <line
            x1={0}
            y1={HATCH_SPACING / 2}
            x2={HATCH_SPACING}
            y2={HATCH_SPACING / 2}
            stroke={INK}
            strokeWidth={HATCH_WEIGHT}
          />
        </pattern>
      </defs>
      {/* Both zones carry ONE neutral fill; the hatch overlay tells them apart, not colour. */}
      <path data-role="area_zone_apartment" d={apartmentD} fill={ZONE_FILL} fillRule="evenodd" stroke={OUTLINE} strokeWidth={0.75} />
      <path d={apartmentD} fill={`url(#${apartmentPattern})`} fillRule="evenodd" stroke="none" />
      <path data-role="area_zone_other" d={otherD} fill={ZONE_FILL} fillRule="evenodd" stroke={OUTLINE} strokeWidth={0.75} />
      <path d={otherD} fill={`url(#${otherPattern})`} fillRule="evenodd" stroke="none" />
      {/* One clean footprint edge, no detail inside. */}
      <path data-role="area_footprint" d={ringD} fill="none" stroke={INK} strokeWidth={1} />
      {/* The single proportional division — the only line inside the footprint. */}
      <path data-role="area_division" d={`M${fmt(dx1)} ${fmt(dy1)} L${fmt(dx2)} ${fmt(dy2)}`} fill="none" stroke={INK} strokeWidth={1} />
    </svg>
  );
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

  if (view.kind === "fitted_zones") {
    return (
      <section
        className="aa-illustration"
        data-testid="area-allocation"
        aria-label="Area allocation illustration"
      >
        <p className="aa-percentage" data-testid="area-allocation-percentage">
          {`${view.percent}% apartment area`}
        </p>
        <ZonesDrawing view={view} />
        <IllustrationFooter conversionStatement={view.conversionStatement} />
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
      <IllustrationFooter conversionStatement={view.conversionStatement} />
    </section>
  );
}
