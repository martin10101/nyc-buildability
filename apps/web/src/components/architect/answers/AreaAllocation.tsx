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
/** The legend swatch's side, matching the bar/zone hatch scale (px). */
const SWATCH_SIZE = 12;

/**
 * Hatch direction — the ONE fact that keeps every surface (the zone fills, the
 * legend swatches and the proportional bar) telling the two zones apart the SAME
 * way, and the same way the PDF kernel does.
 *
 * The kernel draws the apartment hatch rising ("/") and the other hatch falling
 * ("\") — kit/area_allocation.py `_defs`: apartment `patternTransform` rotate(-45),
 * other rotate(-135); its legend swatches and its bar reuse those same patterns.
 *
 * This component renders the hatch two ways, and in chromium the two mechanisms
 * MIRROR each other, so each diagonal is defined once here and every surface
 * derives its own mechanism's angle from it:
 *   • SVG pattern (the zones AND the legend swatches, exactly as the kernel): a
 *     horizontal line under `patternTransform` rotate(θ); rotate(-45) renders "/",
 *     rotate(-135) renders "\".
 *   • CSS `repeating-linear-gradient(θdeg)` (the proportional bar): 135deg renders
 *     "/", 45deg renders "\" — the MIRROR of the SVG rotation (M5-T202 G3 visual
 *     review r1, chromium-verified; see the producer-report screenshot).
 * Mixing the two mechanisms with un-paired angles inverted the legend key in r1;
 * deriving every angle from this one model is what stops that recurring.
 */
type HatchDiagonal = "rising" | "falling";
/** The kernel's apartment zone hatch: rising "/". */
const APARTMENT_DIAGONAL: HatchDiagonal = "rising";
/** The kernel's other zone hatch: falling "\". */
const OTHER_DIAGONAL: HatchDiagonal = "falling";

/** The SVG `patternTransform` rotation that renders `diagonal` (the kernel's convention). */
function hatchSvgRotate(diagonal: HatchDiagonal): number {
  return diagonal === "rising" ? -45 : -135;
}
/** The CSS `repeating-linear-gradient` angle that renders `diagonal` in chromium
 * (the mirror of the SVG rotation above). */
function hatchCssAngle(diagonal: HatchDiagonal): number {
  return diagonal === "rising" ? 135 : 45;
}

/** A neutral fill overlaid with parallel hatch lines running in `diagonal` — the kernel's hatch idea
 * in CSS, so the two zones differ by pattern and never by colour alone (the proportional bar). */
function hatchStyle(diagonal: HatchDiagonal): CSSProperties {
  return {
    backgroundColor: ZONE_FILL,
    backgroundImage: `repeating-linear-gradient(${hatchCssAngle(diagonal)}deg, ${INK}, ${INK} 0.75px, transparent 0.75px, transparent 5px)`,
  };
}

/** One `<pattern>` of parallel hatch lines running in `diagonal` — the kernel's `_hatch_pattern`
 * in the browser, used by both the zones and the legend swatches so they can never drift. */
function HatchPattern({ id, diagonal }: { id: string; diagonal: HatchDiagonal }) {
  return (
    <pattern
      id={id}
      patternUnits="userSpaceOnUse"
      width={HATCH_SPACING}
      height={HATCH_SPACING}
      patternTransform={`rotate(${hatchSvgRotate(diagonal)})`}
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
  );
}

/** A legend swatch drawn with the SAME SVG pattern as its zone (the kernel's `_footer` swatch), so
 * the key for each zone shows exactly the hatch that zone is drawn with — never a mirror of it. */
function HatchSwatch({ diagonal, role }: { diagonal: HatchDiagonal; role: string }) {
  const raw = useId();
  const uid = raw.replace(/[^a-zA-Z0-9_-]/g, "");
  const patternId = `aa-swatch-${role}-${uid}`;
  return (
    <svg
      className="aa-swatch"
      data-role={role}
      aria-hidden="true"
      width={SWATCH_SIZE}
      height={SWATCH_SIZE}
      viewBox={`0 0 ${SWATCH_SIZE} ${SWATCH_SIZE}`}
      style={{ flex: "0 0 auto", border: `1px solid ${OUTLINE}` }}
    >
      <defs>
        <HatchPattern id={patternId} diagonal={diagonal} />
      </defs>
      {/* One neutral fill overlaid with the zone's own hatch — colour never tells the zones apart. */}
      <rect x={0} y={0} width={SWATCH_SIZE} height={SWATCH_SIZE} fill={ZONE_FILL} />
      <rect x={0} y={0} width={SWATCH_SIZE} height={SWATCH_SIZE} fill={`url(#${patternId})`} stroke="none" />
    </svg>
  );
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
          <HatchSwatch diagonal={APARTMENT_DIAGONAL} role="area_swatch_apartment" />
          <span data-testid="area-allocation-label-apartment" style={{ fontSize: LABEL_SIZE }}>
            {AREA_ZONE_APARTMENT}
          </span>
        </li>
        <li className="aa-legend-item" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <HatchSwatch diagonal={OTHER_DIAGONAL} role="area_swatch_other" />
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
        <HatchPattern id={apartmentPattern} diagonal={APARTMENT_DIAGONAL} />
        <HatchPattern id={otherPattern} diagonal={OTHER_DIAGONAL} />
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
          style={{ width: apartmentWidth, ...hatchStyle(APARTMENT_DIAGONAL) }}
        />
        <span
          className="aa-bar-other"
          data-role="area_bar_other"
          style={{
            width: otherWidth,
            borderLeft: `1px solid ${OUTLINE}`,
            ...hatchStyle(OTHER_DIAGONAL),
          }}
        />
      </div>
      <IllustrationFooter conversionStatement={view.conversionStatement} />
    </section>
  );
}
