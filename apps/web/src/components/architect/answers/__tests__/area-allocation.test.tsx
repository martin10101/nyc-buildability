import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  AREA_ILLUSTRATION_CAPTION,
  AREA_MEASURE_WORDS,
  AREA_ZONE_APARTMENT,
  AREA_ZONE_OTHER,
  PHYSICAL_PLATE_NOT_CHECKED,
} from "@/lib/architect/area-allocation-tokens";
import { AREA_ALLOCATION_CONVERSION_STATEMENT } from "@/lib/results-contract-checks";
import { AreaAllocation } from "../AreaAllocation";

/**
 * M5-T187 + M5-T202 part B2a — the two-zone area illustration component.
 * S1 (fitted zones), S3 (unfitted bar), S4 (byte-equal wording and the measure), S5 (hatch not
 * colour; only the division line inside; no plan detail), plus the fail-closed line. The block
 * values are small inline literals except the benchmark fitted case, which reads the recorded
 * fixture and the kit-authored golden from disk. The wording is checked byte-for-byte against
 * docs/design/presentation-tokens.json.
 */

afterEach(cleanup);

const CONVERSION =
  "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked";

/** Repo root is two levels above the vitest cwd (apps/web). */
function repoFile(relative: string): string {
  return readFileSync(resolve(process.cwd(), "../..", relative), "utf8");
}

function barBlock(share: number, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  const total = 18500;
  const apartment = Math.round(share * total * 100) / 100;
  return {
    label: "Illustrative",
    share,
    measure: "residential_floor_area",
    conversion_statement: CONVERSION,
    apartment_area_sqft: apartment,
    other_area_sqft: total - apartment,
    total_sqft: total,
    fitted: false,
    ...overrides,
  };
}

/** The recorded benchmark's own fitted block and placed footprint (0.6; 100.76 x 66.66). */
function benchmark(): { allocation: unknown; placement: unknown } {
  const doc = JSON.parse(
    repoFile("packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json"),
  );
  const alt = doc.building_alternatives[0];
  return { allocation: alt.area_allocation, placement: alt.placement };
}

function golden(): { benchmark: { division_x: number; apartment_fraction: number } } {
  return JSON.parse(repoFile("apps/web/src/test-support/report-parity-area-zones.json"));
}

// ---- S1: the fitted two-zone drawing (benchmark) ----

describe("S1 — the fitted two-zone drawing splits the placed footprint at the share", () => {
  it("draws two zones, one footprint outline and exactly one division; fraction and x equal the kernel's", () => {
    const { allocation, placement } = benchmark();
    const g = golden().benchmark;
    const { container } = render(<AreaAllocation allocation={allocation} placement={placement} />);

    // one stated percentage, read from the block's share (60%).
    expect(screen.getByTestId("area-allocation-percentage").textContent).toBe("60% apartment area");

    const svg = screen.getByTestId("area-allocation-zones");
    expect(Math.abs(Number(svg.getAttribute("data-apartment-fraction")) - g.apartment_fraction)).toBeLessThanOrEqual(1e-6);
    expect(Math.abs(Number(svg.getAttribute("data-apartment-fraction")) - 0.6)).toBeLessThanOrEqual(1e-6);
    expect(Math.abs(Number(svg.getAttribute("data-division-x")) - g.division_x)).toBeLessThanOrEqual(1e-6);

    // two zones, one footprint edge, and exactly one proportional division line.
    expect(container.querySelectorAll('[data-role="area_zone_apartment"]')).toHaveLength(1);
    expect(container.querySelectorAll('[data-role="area_zone_other"]')).toHaveLength(1);
    expect(container.querySelectorAll('[data-role="area_footprint"]')).toHaveLength(1);
    expect(container.querySelectorAll('[data-role="area_division"]')).toHaveLength(1);

    // the fitted state draws no proportional bar.
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
  });
});

// ---- S3: the unfitted proportional bar is unchanged ----

describe("S3 — the unfitted proportional bar (unchanged)", () => {
  it("shows one bar split by the share, one stated percentage, and no footprint/zones", () => {
    const { container } = render(<AreaAllocation allocation={barBlock(0.65)} />);

    expect(screen.getByTestId("area-allocation-percentage").textContent).toBe("65% apartment area");

    const bar = screen.getByTestId("area-allocation-bar");
    const fraction = Number(bar.getAttribute("data-apartment-fraction"));
    expect(Math.abs(fraction - 0.65)).toBeLessThanOrEqual(0.005);

    const apartment = container.querySelector<HTMLElement>('[data-role="area_bar_apartment"]');
    const other = container.querySelector<HTMLElement>('[data-role="area_bar_other"]');
    expect(apartment?.style.width).toBe("65%");
    expect(other?.style.width).toBe("35%");

    // a single proportional bar, NOT zones-in-footprint.
    expect(container.querySelectorAll('[data-role="area_footprint"]')).toHaveLength(0);
    expect(container.querySelectorAll('[data-role="area_zone_apartment"]')).toHaveLength(0);
    expect(container.querySelectorAll('[data-role="area_division"]')).toHaveLength(0);
    expect(screen.queryByTestId("area-allocation-zones")).toBeNull();
  });

  it("table: fitted:false -> bar; fitted:true (placed) -> zones", () => {
    const { allocation, placement } = benchmark();
    const { rerender } = render(<AreaAllocation allocation={barBlock(0.65)} />);
    expect(screen.getByTestId("area-allocation-bar")).toBeInTheDocument();
    expect(screen.queryByTestId("area-allocation-zones")).toBeNull();
    rerender(<AreaAllocation allocation={allocation} placement={placement} />);
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
    expect(screen.getByTestId("area-allocation-zones")).toBeInTheDocument();
  });
});

// ---- S4: wording byte-equal to the tokens; the measure in plain words ----

describe("S4 — the zone labels, caption and measure are byte-equal to presentation-tokens.json", () => {
  it("the component literals equal the JSON wording tokens (mutating the JSON reddens this)", () => {
    const { wording } = JSON.parse(repoFile("docs/design/presentation-tokens.json"));
    expect(AREA_ZONE_APARTMENT).toBe(wording.area_zone_apartment);
    expect(AREA_ZONE_OTHER).toBe(wording.area_zone_other);
    expect(AREA_ILLUSTRATION_CAPTION).toBe(wording.area_illustration_caption);
  });

  it("the rendered labels, caption and measure are exactly those words (no trailing full stop)", () => {
    const { wording } = JSON.parse(repoFile("docs/design/presentation-tokens.json"));
    const { allocation, placement } = benchmark();
    render(<AreaAllocation allocation={allocation} placement={placement} />);
    expect(screen.getByTestId("area-allocation-label-apartment").textContent).toBe(
      wording.area_zone_apartment,
    );
    expect(screen.getByTestId("area-allocation-label-other").textContent).toBe(
      wording.area_zone_other,
    );
    expect(screen.getByTestId("area-allocation-caption").textContent).toBe(
      wording.area_illustration_caption,
    );
    expect(screen.getByTestId("area-allocation-caption").textContent).not.toMatch(/\.$/);
    // the measure words are the kernel's bare "Residential floor area" (M5-T173 sheet not yet accepted).
    expect(AREA_MEASURE_WORDS).toBe("Residential floor area");
    expect(screen.getByTestId("area-allocation-measure").textContent).toBe(
      `Measure: ${AREA_MEASURE_WORDS}`,
    );
  });
});

// ---- S5: hatch not colour; only the division inside; no plan detail ----

describe("S5 — hatch not colour; only the division line inside; no room/wall/unit/stair/elevator", () => {
  const FORBIDDEN = [/\broom\b/i, /unit wall/i, /\bstair/i, /\belevator/i, /\bapartments\b/i, /\bunits\b/i];

  it("the two zones share one fill and differ only by hatch angle", () => {
    const { allocation, placement } = benchmark();
    const { container } = render(<AreaAllocation allocation={allocation} placement={placement} />);

    const apartmentFill = container.querySelector('[data-role="area_zone_apartment"]')?.getAttribute("fill");
    const otherFill = container.querySelector('[data-role="area_zone_other"]')?.getAttribute("fill");
    expect(apartmentFill).toBe("var(--pt-color-selected)");
    expect(otherFill).toBe(apartmentFill); // same colour: colour cannot tell them apart.

    // the zones SVG carries exactly its two hatch patterns (the legend swatches are their own SVGs).
    const zonesSvg = screen.getByTestId("area-allocation-zones");
    const patterns = Array.from(zonesSvg.querySelectorAll("pattern"));
    expect(patterns).toHaveLength(2);
    const transforms = patterns.map((p) => p.getAttribute("patternTransform"));
    expect(new Set(transforms).size).toBe(2); // the hatch angle differs.
  });

  it("the only line inside the footprint is the single division; the drawing carries no text", () => {
    const { allocation, placement } = benchmark();
    const { container } = render(<AreaAllocation allocation={allocation} placement={placement} />);
    const svg = screen.getByTestId("area-allocation-zones");
    // no room/unit labels drawn inside the footprint.
    expect(svg.querySelectorAll("text")).toHaveLength(0);
    // exactly one division line and one footprint edge; nothing else stroked inside.
    expect(container.querySelectorAll('[data-role="area_division"]')).toHaveLength(1);
    expect(container.querySelectorAll('[data-role="area_footprint"]')).toHaveLength(1);
  });

  it("no forbidden mark for any state (bar and zones)", () => {
    const { allocation, placement } = benchmark();
    for (const node of [
      <AreaAllocation key="bar" allocation={barBlock(0.6)} />,
      <AreaAllocation key="zones" allocation={allocation} placement={placement} />,
    ]) {
      cleanup();
      render(node);
      const text = screen.getByTestId("area-allocation").textContent ?? "";
      for (const pattern of FORBIDDEN) expect(text).not.toMatch(pattern);
      expect(screen.queryAllByTestId("area-allocation-caption")).toHaveLength(1);
    }
  });
});

// ---- the legend key shows each zone's own hatch (not its mirror) ----

/**
 * The chromium-verified mirror between the two hatch render mechanisms (M5-T202 G3 visual review of
 * r1 + the round-2 producer-report screenshot): an SVG horizontal line under patternTransform
 * rotate(-45) renders rising "/", rotate(-135) renders falling "\"; a CSS repeating-linear-gradient
 * at 135deg renders rising "/", at 45deg renders falling "\". These constants are this test's OWN
 * record of that fact — independent of the component's mapping — so a component that pairs the
 * mechanisms wrongly (the r1 inverted legend) reddens here.
 */
type Diagonal = "rising" | "falling";

function svgRotateToDiagonal(transform: string | null | undefined): Diagonal {
  const m = /rotate\(\s*(-?\d+(?:\.\d+)?)\s*\)/.exec(transform ?? "");
  const deg = m ? Number(m[1]) : Number.NaN;
  if (deg === -45) return "rising";
  if (deg === -135) return "falling";
  throw new Error(`unexpected SVG hatch rotate: ${transform ?? "(none)"}`);
}

function cssAngleToDiagonal(backgroundImage: string | undefined): Diagonal {
  const m = /(-?\d+(?:\.\d+)?)deg/.exec(backgroundImage ?? "");
  const deg = m ? Number(m[1]) : Number.NaN;
  if (deg === 135) return "rising";
  if (deg === 45) return "falling";
  throw new Error(`unexpected CSS hatch angle: ${backgroundImage ?? "(none)"}`);
}

/** The diagonal a legend swatch (its own SVG pattern) renders for `role`. */
function swatchDiagonal(container: HTMLElement, role: string): Diagonal {
  const swatch = container.querySelector(`[data-role="${role}"]`);
  return svgRotateToDiagonal(swatch?.querySelector("pattern")?.getAttribute("patternTransform"));
}

/** The diagonal the fitted zone whose hatch pattern id contains `which` renders. */
function zoneDiagonal(which: "apartment" | "other"): Diagonal {
  const svg = screen.getByTestId("area-allocation-zones");
  const pattern = Array.from(svg.querySelectorAll("pattern")).find((p) =>
    (p.getAttribute("id") ?? "").includes(which),
  );
  return svgRotateToDiagonal(pattern?.getAttribute("patternTransform"));
}

describe("the legend key shows each zone's OWN hatch and matches the PDF kernel direction", () => {
  it("FITTED: each swatch's hatch runs the same diagonal as the zone it labels", () => {
    const { allocation, placement } = benchmark();
    const { container } = render(<AreaAllocation allocation={allocation} placement={placement} />);

    // the r1 defect was an inverted key: the apartment swatch showed the OTHER zone's hatch.
    expect(swatchDiagonal(container, "area_swatch_apartment")).toBe(zoneDiagonal("apartment"));
    expect(swatchDiagonal(container, "area_swatch_other")).toBe(zoneDiagonal("other"));
    // and the directions are the kernel's: apartment rising "/", other falling "\".
    expect(zoneDiagonal("apartment")).toBe("rising");
    expect(zoneDiagonal("other")).toBe("falling");
    // the two swatches differ, so the key is not one ambiguous hatch.
    expect(swatchDiagonal(container, "area_swatch_apartment")).not.toBe(
      swatchDiagonal(container, "area_swatch_other"),
    );
  });

  it("BAR: each bar segment runs the same diagonal as its swatch, and matches the kernel bar", () => {
    const { container } = render(<AreaAllocation allocation={barBlock(0.65)} />);
    const apartmentBar = container.querySelector<HTMLElement>('[data-role="area_bar_apartment"]');
    const otherBar = container.querySelector<HTMLElement>('[data-role="area_bar_other"]');

    // the bar segment and its legend swatch render the same diagonal (bar is CSS, swatch is SVG).
    expect(cssAngleToDiagonal(apartmentBar?.style.backgroundImage)).toBe(
      swatchDiagonal(container, "area_swatch_apartment"),
    );
    expect(cssAngleToDiagonal(otherBar?.style.backgroundImage)).toBe(
      swatchDiagonal(container, "area_swatch_other"),
    );
    // the kernel bar direction: apartment rising "/", other falling "\".
    expect(cssAngleToDiagonal(apartmentBar?.style.backgroundImage)).toBe("rising");
    expect(cssAngleToDiagonal(otherBar?.style.backgroundImage)).toBe("falling");
  });
});

// ---- the conversion statement lives in expandable detail, not the caption ----

describe("the G-14 conversion statement is in the expandable detail, not the caption", () => {
  it("the methodology carries the exact statement and the physical floor plate as not checked", () => {
    render(<AreaAllocation allocation={barBlock(0.65)} />);
    const conversion = screen.getByTestId("area-allocation-conversion").textContent ?? "";
    expect(conversion).toBe(CONVERSION);
    expect(conversion).toBe(AREA_ALLOCATION_CONVERSION_STATEMENT);
    expect(screen.getByTestId("area-allocation-not-checked").textContent).toBe(
      PHYSICAL_PLATE_NOT_CHECKED,
    );
    expect(screen.getByTestId("area-allocation-caption").textContent).not.toContain(CONVERSION);
  });
});

// ---- a garbled / un-drawable block fails closed to a plain reason ----

describe("a garbled or un-drawable block renders an explicit unavailable line, never a guessed drawing", () => {
  it("a block with the wrong fixed label shows the plain reason and no drawing", () => {
    render(<AreaAllocation allocation={barBlock(0.65, { label: "Verified" })} />);
    expect(screen.getByTestId("area-allocation-unavailable").textContent).toBe(
      "The area allocation is incomplete.",
    );
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
    expect(screen.queryByTestId("area-allocation-zones")).toBeNull();
  });

  it("a fitted block whose outline cannot be drawn shows the kernel's plain reason, nothing drawn", () => {
    const fitted = {
      label: "Illustrative",
      share: 0.7,
      measure: "residential_floor_area",
      conversion_statement: CONVERSION,
      apartment_area_sqft: 13300,
      other_area_sqft: 5700,
      total_sqft: 19000,
      fitted: true,
    };
    render(
      <AreaAllocation
        allocation={fitted}
        placement={{ status: "placed", outline: [[[0, 0], [40, 0], [80, 0], [0, 0]]] }}
      />,
    );
    expect(screen.getByTestId("area-allocation-unavailable").textContent).toBe(
      "The footprint has no area to show as two zones.",
    );
    expect(screen.queryByTestId("area-allocation-zones")).toBeNull();
  });
});
